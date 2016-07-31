import bv4242 as b
import threading
import time


class ScreenManager(threading.Thread):

    def __init__(self, q):
        """
        Thread that handle the screen
        :param q:
        """
        super(ScreenManager, self).__init__()
        self.shared_queue = q
        self.ui = b.BV4242(0x3d, 1)
        self.number_of_star = 0
        self.status = "disabled"
        self.set_disabled()
        # Save a buffer where we put each typed number
        self.code_buffer = ""
        self.valid_key = "1234"

    def run(self):
        while True:
            if not self.shared_queue.empty():
                val = self.shared_queue.get()
                print "Key received from keypad: ", val
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
        By default the screnn show that the service is Disabled
        """
        self.status = "enabled"
        self.reset()
        self.ui.lcd_print("Enabled")
        self.ui.set_cursor(2, 2)
        self.ui.lcd_print("Enter code:")

    def add_star(self):
        self.number_of_star += 1
        self.ui.lcd_print("*")

    def turn_light_off(self):
        self.ui.bl(0)

    def turn_light_on(self):
        self.ui.bl(103)

    def test_pin_code(self):
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
            self.set_enabled()
            self.status = "enabled"
        else:
            self.set_disabled()
            self.status = "disabled"

    def print_invalid_code(self):
        self.reset()
        self.ui.lcd_print("Invalid code")
        time.sleep(2)
        # show back the last status
        if self.status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()


