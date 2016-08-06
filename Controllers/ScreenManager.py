import bv4242 as b
import threading
import time
from BuzzerManager import BuzzerManager
from ArduinoManager import ArduinoManager


class ScreenManager(threading.Thread):

    def __init__(self, q):
        """
        Thread that handle the screen
        :param q:
        """
        super(ScreenManager, self).__init__()
        self.shared_queue = q
        self.ui = b.BV4242(0x3d, 1)
        self.status = "disabled"
        self.set_disabled()
        # Save a buffer where we put each typed number
        self.code_buffer = ""
        self.valid_key = "1234"
        self.light_status = "on"
        # this is used to stop the arming thread
        self.pill2kill = None
        # save if we are currently arming the system
        self.arming_in_pogress = False
        # init a buzzer
        self.buzzer = BuzzerManager()
        # init the connection with the arduino
        self.arduino = ArduinoManager()

    def run(self):
        while True:
            if not self.shared_queue.empty():
                val = self.shared_queue.get()
                print "Key received from keypad: ", val
                if val == "switch_light":
                    self.switch_light()
                elif val == "cancel" or val == "enter":
                    self.cancel_arming()
                else:
                    # we add a star to the screen
                    self.add_star()
                    # add the value to the buffer
                    self.code_buffer += str(val)
                    # if we have 4 number we can test the code
                    if len(self.code_buffer) == 4:
                        self.test_pin_code()
                        self.code_buffer = ""
            time.sleep(0.1)

    def reset(self):
        """
        Clean the lcd screen
        :return:
        """
        self.ui.lcd_reset()
        self.ui.clear()
        self.ui.lcd_home()
        self.ui.cursor()

    def set_disabled(self):
        """
        By default the screnn show that the service is Disabled
        """
        self.status = "disabled"
        self.reset()
        self.ui.lcd_print("Disabled")
        self.ui.set_cursor(2, 2)
        self.ui.lcd_print("Enter code:")

    def set_enabled(self):
        """
        By default the screnn show that the service is Enabled
        """
        self.status = "enabled"
        self.reset()
        self.ui.lcd_print("Enabled")
        self.ui.set_cursor(2, 2)
        self.ui.lcd_print("Enter code:")

    def add_star(self):
        """
        Add a "*" to the last char of the screen
        :return:
        """
        self.ui.lcd_print("*")

    def turn_light_off(self):
        """
        Turn the light of the screen off
        :return:
        """
        self.ui.bl(0)

    def turn_light_on(self):
        """
        Turn the light of the screen on
        :return:
        """
        self.ui.bl(103)

    def test_pin_code(self):
        """
        The user has entered 4 number. We test if typed code is the right one
        If the code is right, we switch the status of the system
        If the code is wrong we show a notification on the screen
        :return:
        """
        if self.code_buffer == self.valid_key:
            print "Code valid"
            self.switch_status()
        else:
            print "Code invalid"
            self.print_invalid_code()

    def switch_status(self):
        """
        If we were disabled, switch to enabled, else switch to disabled
        :return:
        """
        if self.status == "disabled":
            # the system was disabled, arming during 20 secondes with thread
            self.delayed_enableling()
        else:
            self.set_disabled()
            self.status = "disabled"

    def print_invalid_code(self):
        """
        Print Invalid code on the screen and go back to the last status
        :return:
        """
        self.reset()
        self.ui.lcd_print("Invalid code")
        time.sleep(2)
        # show back the last status
        if self.status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()

    def delayed_enableling(self):
        """
        Arming the alarm. Count 20 second. During this time the action can be cancelled
        by the user
        :return:
        """
        def doit(stop_event):
            while not stop_event.is_set():
                for x in range(20, 0, -5):
                    if not stop_event.is_set():
                        self.ui.lcd_print("%s.." % str(x))
                        stop_event.wait(5)
                # counter over, if the user has not cancel, we active the alarm
                if not stop_event.is_set():
                    # switch status
                    self.set_enabled()
                    self.status = "enabled"
                    # stop the thread
                    self.pill2kill.set()
                    # stop buzzing
                    self.buzzer.stop()

        self.arming_in_pogress = True
        self.reset()
        self.ui.lcd_print("Arming...")
        self.ui.set_cursor(2, 2)
        self.pill2kill = threading.Event()
        t = threading.Thread(target=doit, args=(self.pill2kill,))
        t.start()
        # we start the buzzer
        self.buzzer.mode = 2
        self.buzzer.start()

    def switch_light(self):
        if self.light_status == "on":
            # so we switch to off
            self.turn_light_off()
            self.light_status = "off"
        else:
            # we switch on on
            self.turn_light_on()
            self.light_status = "on"
        pass

    def cancel_arming(self):
        """
        The user has canceled the arming of the system.
        Go back to Disabled status
        :return:
        """
        if self.arming_in_pogress:
            self.pill2kill.set()
            self.reset()
            self.ui.lcd_print("Cancelled")
            # stop buzzing
            self.buzzer.stop()
            time.sleep(2)
            self.set_disabled()



