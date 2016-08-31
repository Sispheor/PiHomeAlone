import Adafruit_CharLCD as LCD
import time

from Utils.TimerReset import TimerReset

RED = 1.0, 0.0, 0.0
GREEN = 0.0, 1.0, 0.0
BLUE = 0.0, 0.0, 1.0
YELLOW = 1.0, 1.0, 0.0
WHITE = 1.0, 1.0, 1.0

PIXEL_WAIT = [31, 17, 10, 4, 10, 17, 31, 0]
PIXEL_OK = [0, 1, 3, 22, 28, 8, 0, 0]
PIXEL_NOK = [0, 27, 14, 4, 14, 27, 0, 0]
PIXEL_BELL = [4, 14, 14, 14, 31, 0, 4, 0]
PIXEL_SMILEY_SAD = [0, 0, 10, 0, 14, 17, 0, 0]
PIXEL_SELECTOR = [0, 8, 12, 14, 12, 8, 0, 0]


class AdafruitScreenManager:
    def __init__(self):
        self.lcd = LCD.Adafruit_CharLCDPlate()
        # create some custom characters
        self.lcd.create_char(1, PIXEL_OK)
        self.lcd.create_char(2, PIXEL_NOK)
        self.lcd.create_char(3, PIXEL_WAIT)
        self.lcd.create_char(4, PIXEL_BELL)
        self.lcd.create_char(5, PIXEL_SMILEY_SAD)
        self.lcd.create_char(6, PIXEL_SELECTOR)

        self.light_status = "on"
        # thread to turn off the screen automaticaly
        self.timer = TimerReset(10, self.turn_light_off)

    def _check_timer_alive(function):
        """
        A decorator class to reset the timer that will turn off the screen automatically
        :return:
        """

        def wrapper_original_function(self, *args, **kwargs):
            print "check timer is alive"
            if self.timer.isAlive():
                print "timer still aline, reseting it"
                self.timer.reset(10)
            else:
                print "timer not anymore alive, recreating a new one"
                if function.__name__ != "switch_light":  # switch light function will handle this part
                    self.turn_light_on()
                self.timer = TimerReset(10, self.turn_light_off)
                self.timer.start()
            # call the initial function
            function(self, *args, **kwargs)
        return wrapper_original_function

    def reset(self):
        """
        Clean the lcd screen
        :return:
        """
        self.lcd.clear()
        self.lcd.show_cursor(False)
        self.lcd.set_color(*BLUE)

    @_check_timer_alive
    def set_disabled(self):
        """
        By default the screnn show that the service is Disabled
        """
        self.reset()
        self.lcd.message("\x02 Disabled\nEnter code:")
        self.lcd.show_cursor(True)
        self.lcd.blink(True)
        self.lcd.set_color(*WHITE)

    @_check_timer_alive
    def set_enabled(self):
        """
        By default the screnn show that the service is Enabled
        """
        self.reset()
        self.lcd.message("\x01 Enabled\nEnter code:")
        self.lcd.show_cursor(True)
        self.lcd.blink(True)
        self.lcd.set_color(*GREEN)

    @_check_timer_alive
    def print_invalid_code(self, status):
        """
        Print Invalid code on the screen and go back to the last status
        :return:
        """
        self.reset()
        self.lcd.message("\x01 Invalid code")
        time.sleep(2)
        # show back the last status
        if status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()

    @_check_timer_alive
    def print_invalid_card(self, status):
        """
        Print Invalid RFID card on the screen and go back to the last status
        :return:
        """
        self.reset()
        self.lcd.message("\x05 Invalid card")
        time.sleep(2)
        # show back the last status
        if status == "disabled":
            self.set_disabled()
        else:
            self.set_enabled()

    @_check_timer_alive
    def switch_light(self):
        if self.light_status == "on":
            # so we switch to off
            self.lcd.set_backlight(0)
            self.light_status = "off"
        else:
            # we switch on on
            self.lcd.set_backlight(1)
            self.light_status = "on"

    @_check_timer_alive
    def cancel_arming(self):
        """
        The user has canceled the arming of the system.
        Go back to Disabled status
        :return:
        """
        self.reset()
        self.lcd.message("Cancelled")
        time.sleep(2)
        self.set_disabled()

    @_check_timer_alive
    def set_intrustion_detected(self, location):
        """
        Show intrusion detected message
        :param location:
        :return:
        """
        self.reset()
        self.lcd.message("\x06 "+location+"\nEnter code:")
        self.lcd.show_cursor(True)
        self.lcd.blink(True)
        self.lcd.set_color(*YELLOW)

    @_check_timer_alive
    def add_star(self):
        """
        Add a "*" to the last char of the screen
        :return:
        """
        self.lcd.message("*")

    def set_arduino_connection_missing(self):
        """
        Print a message to notify that the arduino is not connected
        :return:
        """
        self.reset()
        self.lcd.set_color(*RED)
        self.lcd.message("Fail! No Arduino\nconnection")

    @_check_timer_alive
    def set_alarm(self):
        """
        Siren on, switch screen to red
        :return:
        """
        self.reset()
        self.lcd.set_color(*RED)
        self.lcd.message("Alarm!\nEnter code:")

    def turn_light_off(self):
        self.lcd.set_backlight(0)
        self.light_status = "off"

    def turn_light_on(self):
        self.lcd.set_backlight(1)
        self.light_status = "on"

