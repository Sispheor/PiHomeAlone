import threading
from pad4pi import rpi_gpio
import time

KEYPAD = [
            [1, 2, 3, "A"],
            [4, 5, 6, "B"],
            [7, 8, 9, "C"],
            ["*", 0, "#", "D"]
        ]

ROW_PINS = [5, 6, 13, 19]  # BCM numbering
COL_PINS = [26, 12, 16, 20]  # BCM numbering


class MatrixKeypadManager(threading.Thread):

    def __init__(self, shared_queue):
        super(MatrixKeypadManager, self).__init__()
        self.shared_queue = shared_queue

    def run(self):

        def send_key(key):
            print "Key pressed: %s" % key
            self.shared_queue.put(key)

        factory = rpi_gpio.KeypadFactory()
        keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
        keypad.registerKeyPressHandler(send_key)
        while True:
            time.sleep(1)


