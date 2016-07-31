#!/usr/bin/env python
import i2c
from time import sleep

# commands
PAD_CLEARBUF   = 1
PAD_KEYSINBUF  = 2
PAD_GETKEY     = 3
PAD_ISINBUF    = 4
PAD_SCANCODE   = 5
PAD_GETAVG     = 10
PAD_GETDELTA   = 11
PAD_RESETEEPROM= 20
PAD_SLEEP      = 21
LCD_RESET      = 30
LCD_CMD        = 31
LCD_DATA       = 32
LCD_STRING     = 33
LCD_SIGNON     = 35
LCD_BL         = 36
LCD_CONTRAST   = 37
LCD_MODE       = 38


class BV4242:
    """
    BV4242 Keypad and LCD screen for the Arduino and Rpi, works
    on 3V3 to 5V
    """
    # i2c_address is the i2c address of the device, channel is the channel
    # number 0 for older rpi and 1 for newer
    def __init__(self, i2c_address, i2c_chan):
        self.bus = i2c.IIC(i2c_address, i2c_chan)
        self.adr = i2c_address

    # ***************************************************************************
    # K E Y   S E C T I O N
    # ***************************************************************************

    def clr_buf(self):
        """
        clears the key buffer
        :return:
        """
        self.bus.i2c([PAD_CLEARBUF], 0)

    def keys(self):
        """
        gets number of keys in buffer
        :return:
        """
        kib = self.bus.i2c([PAD_KEYSINBUF], 1)
        return kib[0]

    def key(self):
        """
        gets the key
        :return:
        """
        kib = self.bus.i2c([PAD_GETKEY], 1)
        return kib[0]

    def key_in_buf(self, key):
        """
        see if a particular key is in the buffer
        :param key: The key to look for into the buffer
        :return:
        """
        kib = self.bus.i2c([PAD_ISINBUF, key], 1)
        return kib[0]

    def scan(self):
        """
        gets the scancode
        :return:
        """
        kib = self.bus.i2c([PAD_SCANCODE], 1)
        return kib[0]

    def scan8_avg(self):
        """
        returns 8 average values as a list
        :return:
        """
        return self.bus.i2c([PAD_GETAVG], 8)

    def scan8_list(self):
        """
        returns 8 delta values as a list
        :return:
        """
        return self.bus.i2c([PAD_GETDELTA], 8)

    def ee_reset(self):
        """
        EEPROM default values reset
        :return:
        """
        self.bus.i2c([PAD_RESETEEPROM], 0)

    def sleep(self):
        """
        sleep
        :return:
        """
        self.bus.i2c([PAD_SLEEP], 0)

    # ***************************************************************************
    # L C D   S E C T I O N
    # ***************************************************************************

    def lcd_reset(self):
        """
        resets LCD display
        :return:
        """
        self.bus.i2c([LCD_RESET], 0)
        sleep(0.7)

    def mode(self, mode):
        """
        mode of the screen
        :param mode: 0 normal, 1 single line
        :return:
        """
        self.bus.i2c([LCD_MODE, mode], 0)

    def contrast(self, value):
        """
        contsast 0 to 63
        :param value:
        :return:
        """
        self.bus.i2c([LCD_CONTRAST, value], 0)

    def bl(self, value):
        """
        backlight control
        :param value: 0 to 103
        :return:
        """
        self.bus.i2c([LCD_BL, value], 0)

    def clear(self):
        """
        clear lcd screen
        :return:
        """
        self.bus.i2c([LCD_CMD, 1], 0)

    def lcd_home(self):
        """
        home cursor
        :return:
        """
        self.bus.i2c([LCD_CMD, 2], 0)

    def set_cursor(self, col, row):
        """
        set cursor position. lines 1 or 2, columns 1 to 16 (for 16x2)
        :param col: 1 or 2
        :param row: 1 to 16
        :return:
        """
        if row > 2:
            row = 2
        if col > 16:
            col = 16
        col -= 1
        if row == 1:
            adr = 0x80+col-1
        else:
            adr = 0xc0+col-1
        self.bus.i2c([LCD_CMD, adr], 0)

    def cursor(self):
        """
        turn cursor on
        :return:
        """
        self.bus.i2c([LCD_CMD, 0xe], 0)

    def no_cursor(self):
        """
        turn cursor off
        :return:
        """
        self.bus.i2c([LCD_CMD, 0xc], 0)

    def blink(self):
        """
        turn cursor blinking on
        :return:
        """
        self.bus.i2c([LCD_CMD, 0xd], 0)

    def no_blink(self):
        """
        turn cursor blinking off
        :return:
        """
        self.bus.i2c([LCD_CMD, 0xc], 0)

    def display(self):
        """
        turn dislay on
        :return:
        """
        self.bus.i2c([LCD_CMD, 0xc], 0)

    def no_display(self):
        """
        turn dislay off
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x8], 0)

    def scroll_display_left(self):
        """
        scroll left
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x18], 0)

    def scroll_display_right(self):
        """
        scroll right
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x1c], 0)

    def autoscroll(self):
        """
        autoscroll 1 line
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x7], 0)

    def no_autoscroll(self):
        """
        stop autoscroll 1 line
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x6], 0)

    def left_to_right(self):
        """
        left to right
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x6], 0)

    def right_to_left(self):
        """
        right to left
        :return:
        """
        self.bus.i2c([LCD_CMD, 0x4], 0)

    def create_char(self, location, map):
        """
        create custom char
        :param location:
        :param map:
        :return:
        """
        location &= 7  # 7 locations
        self.bus.i2c([LCD_CMD, 0x40 | location << 3], 0)
        sleep(0.01)
        for c in map:
            self.bus.i2c([LCD_DATA, c], 0)
            sleep(0.01)

    def lcd_print(self, s):
        """
        prints a string
        :param s:
        :return:
        """
        for c in s:
            self.bus.i2c([LCD_DATA, ord(c)], 0)
