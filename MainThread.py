import threading
import Queue
from Controllers import ScreenManager, KeypadManager
import time
from flask import Flask
from RestAPI import FlaskAPI


class MainThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(MainThread, self).__init__(group, target, name, args, kwargs, verbose)

        # prepare a queue to share data between this threads and the keyboard
        self.shared_queue_keyborad = Queue.Queue()

        # create an object to manager the screen
        self.screen_manager = ScreenManager()

        # run the keypad thread
        self.keypad_thread = KeypadManager(self.shared_queue_keyborad)
        self.keypad_thread.start()

        # create a shared queue for passing message between flask api and this thread
        shared_queue_message_from_api = Queue.Queue()

        # create the flask rest api
        app = Flask(__name__)
        flask_api = FlaskAPI(app, shared_queue_message_from_api)
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
                else:
                    # we add a star to the screen
                    self.screen_manager.add_star()
                    # add the value to the buffer
                    self.code_buffer += str(val)
                    # if we have 4 number we can test the code
                    if len(self.code_buffer) == 4:
                        self._test_pin_code()
                        self.code_buffer = ""
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
            self.screen_manager.switch_status()
        else:
            print "Code invalid"
            self.screen_manager.print_invalid_code()
