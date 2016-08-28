#!/usr/bin/python

from pad4pi import rpi_gpio
import time


def print_key(key):
    print(key)

try:
    KEYPAD = [
        [1, 2, 3, "A"],
        [4, 5, 6, "B"],
        [7, 8, 9, "C"],
        ["*", 0, "#", "D"]
    ]

    ROW_PINS = [5, 6, 13, 19]  # BCM numbering
    COL_PINS = [26, 12, 16, 20]  # BCM numbering

    factory = rpi_gpio.KeypadFactory()
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

    keypad.registerKeyPressHandler(print_key)

    print("Press buttons on your keypad. Ctrl+C to exit.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Goodbye")
finally:
    keypad.cleanup()
