import threading
import Queue
from Controllers import ScreenManager, KeypadManager, BuzzerManager, ArduinoManager, RFIDrc522Manager, Receiver433Manager
import time
from flask import Flask
from RestAPI import FlaskAPI
from Utils.utils import *


class MainThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(MainThread, self).__init__(group, target, name, args, kwargs, verbose)
        # init a status
        self.status = "disabled"
        # self.status = "enabled"
        self.arming_in_pogress = False
        self.waiting_alarm_disarm = False

        # load settings file
        self.cfg = get_settings()

        # this is used to stop the arming thread
        self.pill2kill = None

        # keep a buzzer object
        self.buzzer = None

        # prepare a queue to share data between this threads and other thread
        self.shared_queue_keyborad = Queue.Queue()
        self.shared_queue_rfid_reader = Queue.Queue()
        self.shared_queue_433_receiver = Queue.Queue()
        self.shared_queue_message_from_api = Queue.Queue()

        # create an object to manager the screen
        self.screen_manager = ScreenManager()

        # create an object to manage the arduino
        self.arduino = ArduinoManager()
        # TODO remove this in prod
        self.arduino.stop_siren()

        # run the keypad thread
        self.keypad_thread = KeypadManager(self.shared_queue_keyborad)
        self.keypad_thread.start()

        # run the thread that handle RFID
        rfid = RFIDrc522Manager(self.shared_queue_rfid_reader)
        rfid.start()

        # create an object to store the reveicer433 thread
        # self.receiver443 = Receiver433Manager(self.shared_queue_433_receiver)
        # self.receiver443.start()
        self.receiver443 = None

        # create the flask rest api
        app = Flask(__name__)
        flask_api = FlaskAPI(app, self.shared_queue_message_from_api, self)
        flask_api.start()

        # Save a buffer where we put each typed number
        self.code_buffer = ""
        # The valid pin code
        self.valid_key = self.cfg["pin_code"]

    def run(self):
        print "Run main thread"
        while True:
            if not self.shared_queue_keyborad.empty():
                val = self.shared_queue_keyborad.get()
                print "Key received from keypad: ", val
                if val == "switch_light":
                    self.screen_manager.switch_light()
                elif val == "cancel" or val == "enter":
                    self.screen_manager.cancel_arming()
                    # stop the thread
                    self.pill2kill.set()
                    # stop buzzing
                    self.buzzer.stop()
                    time.sleep(2)
                    self.screen_manager.set_disabled()
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

    def _test_pin_code(self):
        """
        The user has entered 4 number. We test if typed code is the right one
        If the code is right, we switch the status of the system
        If the code is wrong we show a notification on the screen
        :return:
        """
        print "Valid code is %s" % self.valid_key
        if str(self.code_buffer) == str(self.valid_key):
            print "Code valid"
            self._switch_status()
        else:
            print "Code invalid"
            self.screen_manager.print_invalid_code(self.status)

    def _switch_status(self):
        """
        If we were disabled, switch to enabled, else switch to disabled
        :return:
        """
        if self.status == "disabled":
            # the system was disabled, arming during 20 secondes with thread
            self.delayed_enableling()
        else:
            # stop arduino counter
            self.arduino.cancel_delayed_siren()
            # stop siren 
            self.arduino.stop_siren()
            self.screen_manager.set_disabled()
            self.status = "disabled"
            if self.waiting_alarm_disarm:
                self.pill2kill.set()

    def delayed_enableling(self):
        """
        Arming the alarm. Count 20 second. During this time the action can be cancelled
        by the user
        :return:
        """
        def doit(stop_event, screen_manager):
            while not stop_event.is_set():
                for x in range(20, 0, -5):
                    if not stop_event.is_set():
                        screen_manager.ui.lcd_print("%s.." % str(x))
                        stop_event.wait(5)
                # counter over, if the user has not cancel, we active the alarm
                if not stop_event.is_set():
                    # switch status
                    screen_manager.set_enabled()
                    self.status = "enabled"
                    # stop buzzing
                    self.buzzer.stop()
                    # start the 433 receiver thread
                    self.start_receiver433()
                    # Stop this thread
                    self.pill2kill.set()

        self.arming_in_pogress = True
        self.arduino.stop_siren()
        self.screen_manager.reset()
        self.screen_manager.ui.lcd_print("Arming...")
        self.screen_manager.ui.set_cursor(2, 2)
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill, self.screen_manager))
        t.start()
        # we start the buzzer
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 2
        self.buzzer.start()

    def cancel_arming(self):
        print "Arming canceled"
        self.pill2kill.set()

    def update_status(self, new_alarm_status, new_siren_status):
        # first, switch the alamr status
        if new_alarm_status == "enabled":
            self.status = "enabled"
            self.screen_manager.set_enabled()
        else:
            self.screen_manager.set_disabled()
            self.status = "disabled"

        if new_siren_status == "on":
            print "Start the siren"
            self.arduino.start_siren()
        else:
            print "Stop the siren"
            self.arduino.stop_siren()

    def _test_rfid_uid(self, uid):
        # we bip to notify the user that we scanned the card
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 3
        self.buzzer.start()
        self.buzzer.stop()

        if uid in self.cfg['rfid']['valid_uid']:
            print "Valid UID"
            self._switch_status()
        else:
            print "Invalid UID"
            self.screen_manager.print_invalid_card(self.status)

    def start_receiver433(self):
        self.receiver443 = Receiver433Manager(self.shared_queue_433_receiver)
        self.receiver443.start()

    def _test_433_uid(self, uid):
        """
        Test the received uid against settings uid. Should be always a valid code
        :param uid: received ID from the 433MHZ receiver sent by a sensor
        :return:
        """
        for el in self.cfg['door_sensor']:
            if uid == el['id']:
                print "Valid sensor ID from %s" % el['location']
                # something has been detected
                self.delayed_alarm(el['location'])
                # not need to test other ID
                break
            else:
                print "Sensor ID not reconized"

    def delayed_alarm(self, location):
        """
        Send a notification to the arduino, this one will sounds the alarm if no code provided
        :param location: String location to show on screen
        :return:
        """
        def doit(stop_event):
            while not stop_event.is_set():
                # wait 20 secondes
                stop_event.wait(20)
            self.buzzer.stop()

        # stop the receiver, we do not need it anymore, intrusion already detected
        self.receiver443.stop()
        # send notification to the arduino
        self.arduino.delayed_siren()
        # show info on screen
        self.screen_manager.set_intrustion_detected(location)
        # set a boolean so next pressed key from the keypad will be used to disable the alarm
        self.waiting_alarm_disarm = True
        # wait 20 sec the code to disable the alarm
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill,))
        t.start()
        # we start the buzzer
        self.buzzer = BuzzerManager()
        self.buzzer.mode = 1
        self.buzzer.start()



