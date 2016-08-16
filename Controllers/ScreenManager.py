import threading
import time

from ArduinoManager import ArduinoManager
from BuzzerManager import BuzzerManager
from Utils import bv4242 as b


class ScreenManager:

    def __init__(self):
        """
        Thread that handle the screen
        """
        self.ui = b.BV4242(0x3d, 1)
        self.set_disabled()
        self.light_status = "on"
        self.pill2kill = None

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
        self.reset()
        self.ui.lcd_print("Disabled")
        self.ui.set_cursor(2, 2)
        self.ui.lcd_print("Enter code:")

    def set_enabled(self):
        """
        By default the screnn show that the service is Enabled
        """
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

    def print_invalid_code(self, status):
        """
        Print Invalid code on the screen and go back to the last status
        :return:
        """
        self.reset()
        self.ui.lcd_print("Invalid code")
        time.sleep(2)
        # show back the last status
        if status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()

    def print_invalid_card(self, status):
        """
        Print Invalid RFID card on the screen and go back to the last status
        :return:
        """
        self.reset()
        self.ui.lcd_print("Invalid card")
        time.sleep(2)
        # show back the last status
        if status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()

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
        self.reset()
        self.ui.lcd_print("Cancelled")



