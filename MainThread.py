import threading
import Queue
from Controllers import ScreenManager, KeypadManager, BuzzerManager, ArduinoManager
import time
from flask import Flask
from RestAPI import FlaskAPI


class MainThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(MainThread, self).__init__(group, target, name, args, kwargs, verbose)
        # init a status
        self.status = "disabled"
        self.arming_in_pogress = False

        # this is used to stop the arming thread
        self.pill2kill = None

        # prepare a queue to share data between this threads and the keyboard
        self.shared_queue_keyborad = Queue.Queue()

        # create an object to manager the screen
        self.screen_manager = ScreenManager()

        # create an object to manage the arduino
        self.arduino = ArduinoManager()

        # run the keypad thread
        self.keypad_thread = KeypadManager(self.shared_queue_keyborad)
        self.keypad_thread.start()

        # Create a buzzer object
        self.buzzer = BuzzerManager()

        # create a shared queue for passing message between flask api and this thread
        self.shared_queue_message_from_api = Queue.Queue()

        # create the flask rest api
        app = Flask(__name__)
        flask_api = FlaskAPI(app, self.shared_queue_message_from_api, self)
        flask_api.start()

        # Save a buffer where we put each typed number
        # TODO Should be in config file
        self.code_buffer = ""
        self.valid_key = "1234"

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
            if not self.shared_queue_message_from_api.empty():
                val = self.shared_queue_keyborad.get()
                print "Received command from API ", val

            time.sleep(0.1)

    def _test_pin_code(self):
        """
        The user has entered 4 number. We test if typed code is the right one
        If the code is right, we switch the status of the system
        If the code is wrong we show a notification on the screen
        :return:
        """
        if self.code_buffer == self.valid_key:
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
            self.screen_manager.set_disabled()
            self.status = "disabled"

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
                    screen_manager.status = "enabled"
                    # stop buzzing
                    self.buzzer.stop()
                    # Stop this thread
                    self.pill2kill.set()

        self.arming_in_pogress = True
        self.screen_manager.reset()
        self.screen_manager.ui.lcd_print("Arming...")
        self.screen_manager.ui.set_cursor(2, 2)
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill, self.screen_manager))
        t.start()
        # we start the buzzer
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

