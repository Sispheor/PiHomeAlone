import threading
import Queue
from Controllers import BuzzerManager, ArduinoManager, RFIDrc522Manager, Receiver433Manager, AdafruitScreenManager, \
    MatrixKeypadManager
import time
from flask import Flask
from RestAPI import FlaskAPI
from Utils.utils import *
from fysom import Fysom
import sys


class MainThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(MainThread, self).__init__(group, target, name, args, kwargs, verbose)
        # load settings file
        self.cfg = get_settings()
        # this is used to stop the arming thread
        self.pill2kill = None
        # keep a buzzer object to stop it from every function. same for the receiver433
        self.buzzer = None

        # prepare a queue to share data between this threads and other thread
        self.shared_queue_keyborad = Queue.Queue()
        self.shared_queue_rfid_reader = Queue.Queue()
        self.shared_queue_433_receiver = Queue.Queue()
        self.shared_queue_message_from_api = Queue.Queue()

        # create an object to manage the screen
        self.screen_manager = AdafruitScreenManager()

        # create an object to manage the arduino
        self.arduino = ArduinoManager()
        try:
            self.arduino.ping()
        except IOError:
            self.screen_manager.set_arduino_connection_missing()
            sys.exit(0)

        # run the keypad thread
        self.keypad_thread = MatrixKeypadManager(self.shared_queue_keyborad)
        self.keypad_thread.start()

        # run the thread that handle RFID
        rfid = RFIDrc522Manager(self.shared_queue_rfid_reader)
        rfid.start()

        # keep 433 receiver thread object in mind
        self.receiver443 = None

        # create the flask rest api
        app = Flask(__name__)
        flask_api = FlaskAPI(app, self.shared_queue_message_from_api, self)
        flask_api.start()

        # Save a buffer where we put each typed number
        self.code_buffer = ""
        self.last_state = "disabled"

        # create the state machine
        self.fsm = Fysom({'initial': self._get_initial_state(),
                          'events': [
                              {'name': 'arm', 'src': 'disabled', 'dst': 'arming'},
                              {'name': 'enable', 'src': 'arming', 'dst': 'enabled'},
                              {'name': 'intrusion', 'src': 'enabled', 'dst': 'waiting_code'},
                              {'name': 'alarm', 'src': 'waiting_code', 'dst': 'alarming'},
                              {'name': 'disable', 'src': ['arming', 'enabled', 'waiting_code', 'alarming'],
                               'dst': 'disabled'}],
                          'callbacks': {
                              'ondisabled': self.ondisabled,
                              'onarming': self.onarming,
                              'onenabled': self.onenabled,
                              'onwaiting_code': self.onwaiting_code,
                              'onalarming': self.onalarming}
                          })

    def run(self):
        print "Run main thread"
        while True:
            if not self.shared_queue_keyborad.empty():
                val = self.shared_queue_keyborad.get()
                print "Key received from keypad: ", val
                if val == "D":
                    self.screen_manager.switch_light()
                elif val == "C":
                    # cancel only if we were in arming status
                    if self.fsm.current == "arming":
                        self.fsm.disable()

                else:
                    # we add a star to the screen
                    self.screen_manager.add_star()
                    # add the value to the buffer
                    self.code_buffer += str(val)
                    # if we have 4 number we can test the code
                    if len(self.code_buffer) == 4:
                        self._test_pin_code()
                        self.code_buffer = ""
            if not self.shared_queue_rfid_reader.empty():
                val = self.shared_queue_rfid_reader.get()
                print "Received UID from RFID ", val
                self._test_rfid_uid(val)
            if not self.shared_queue_433_receiver.empty():
                val = self.shared_queue_433_receiver.get()
                print "Received UID from 433 receiver ", val
                self._test_433_uid(val)

            time.sleep(0.1)

    def ondisabled(self, e):
        """
        Disable the alarm system
        :return:
        """
        # stop buzzer
        if self.buzzer is not None:
            self.buzzer.stop()
        # stop arduino counter if it was counting
        self.arduino.cancel_delayed_siren()
        # stop siren if it was ringing
        self.arduino.stop_siren()
        # if the last status was waiting code
        if self.last_state == "waiting_code":
            # then we stop the counter thread
            self.pill2kill.set()
        if self.last_state == "arming":
            self.pill2kill.set()
            self.screen_manager.cancel_arming()
            time.sleep(2)   # wait 2 seconde with the cancel message before showing disabled status
        # show disabled on screen
        self.screen_manager.set_disabled()

        # we keep the last state in memory
        self.last_state = "disabled"

    def onarming(self, e):
        """
        Arming the alarm. Count 20 second. During this time the action can be cancelled
        by the user
        :return:
        """
        def doit(stop_event, screen_manager):
            max_time = 15
            if self.cfg["debug"]:
                max_time = 5
            while not stop_event.is_set():
                for x in range(max_time, 0, -5):
                    if not stop_event.is_set():
                        screen_manager.lcd.message("%s.." % str(x))
                        stop_event.wait(5)
                # counter over, if the user has not cancel, we active the alarm
                if not stop_event.is_set():
                    self.fsm.enable()

        self.screen_manager.reset()
        self.screen_manager.lcd.message("Arming...\n")
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill, self.screen_manager))
        t.start()
        # we start the buzzer
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 2
        self.buzzer.start()
        # we keep the last state in memory
        self.last_state = "arming"

    def onenabled(self, e):
        # switch status
        self.screen_manager.set_enabled()
        # stop buzzing
        self.buzzer.stop()
        # start the 433 receiver thread
        self.receiver443 = Receiver433Manager(self.shared_queue_433_receiver)
        self.receiver443.start()
        # Stop the counter thread
        self.pill2kill.set()
        # we keep the last state in memory
        self.last_state = "enabled"

    def onwaiting_code(self, e):
        """
        Send a notification to the arduino, this one will sounds the alarm if no code provided
        :return:
        """

        def doit(stop_event):
            while not stop_event.is_set():
                # wait 20 secondes
                stop_event.wait(20)
                stop_event.set()
            self.buzzer.stop()
            # if we are still waiting the code after 20 sec, then alarm
            print "End of the 20 second delay to disable the alarm"
            print "Alarm status is: %s" % self.fsm.current
            if self.fsm.current == "waiting_code":
                self.fsm.alarm()

        # stop the receiver, we do not need it anymore, intrusion already detected
        self.receiver443.stop()
        # send notification to the arduino
        self.arduino.delayed_siren()
        # show info on screen
        self.screen_manager.set_intrustion_detected(e.location)
        # wait 20 sec the code to disable the alarm
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill,))
        t.start()
        # we start the buzzer
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 1
        self.buzzer.start()
        # we keep the last state in memory
        self.last_state = "waiting_code"

    def onalarming(self, e):
        """
        Switch alarm
        """
        print "Alarm !!"
        if self.buzzer is not None:
            self.buzzer.stop()
        self.screen_manager.set_alarm()
        # we keep the last state in memory
        self.last_state = "alarming"

    def _test_pin_code(self):
        """
        The user has entered 4 number. We test if typed code is the right one
        If the code is right, we switch the status of the system
        If the code is wrong we show a notification on the screen
        :return:
        """
        print "Valid code is %s" % self.cfg["pin_code"]
        if str(self.code_buffer) == str(self.cfg["pin_code"]):
            print "Code valid"
            self._switch_status()
        else:
            print "Code invalid"
            self.screen_manager.print_invalid_code(self.last_state)

    def _switch_status(self):
        """
        If we were disabled, switch to enabled, else switch to disabled
        :return:
        """
        if self.fsm.current == "disabled":
            # the system was disabled, arming it
            self.fsm.arm()
        else:  # in all other case, we want to disable
            self.fsm.disable()

    def update_status(self, new_alarm_status, new_siren_status):
        # first, switch the alamr status
        if new_alarm_status == "enabled":
            self.fsm.enable()
        else:
            self.fsm.disable()

        if new_siren_status == "on":
            print "Start the siren"
            self.arduino.start_siren()
        else:
            print "Stop the siren"
            self.arduino.stop_siren()

    def _test_rfid_uid(self, uid):
        # one little bip to notify the user that we scanned the card
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 3
        self.buzzer.start()
        time.sleep(1)
        self.buzzer.stop()

        if uid in self.cfg['rfid']['valid_uid']:
            print "Valid UID"
            self._switch_status()
        else:
            print "Invalid UID"
            self.screen_manager.print_invalid_card(self.last_state)

    def _test_433_uid(self, uid):
        """
        Test the received uid against settings uid. Should be always a valid code
        :param uid: received ID from the 433MHZ receiver sent by a sensor
        :return:
        """
        for el in self.cfg['sensors']:
            if uid == el['id']:
                print "Valid sensor ID from %s" % el['location']
                # something has been detected
                self.fsm.intrusion(location=el['location'])
                # not need to test other ID
                break
            else:
                print "Sensor ID not reconized"

    def _get_initial_state(self):
        """
        Get the initial state of the system. can be "disabled" if the siren is off
        or "alarm" if the siren is on
        :return:
        """
        siren_status = self.arduino.get_siren_status()

        if siren_status == "off":
            return "disabled"
        else:
            return "alarming"



