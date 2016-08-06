import bv4242 as b
import threading
import time


class KeypadManager(threading.Thread):

    def __init__(self, shared_queue):
        """
        Class that handle the keypad
        :param q:
        """
        super(KeypadManager, self).__init__()
        self.shared_queue = shared_queue
        # init the class to call with the keypad
        self.ui = b.BV4242(0x3d, 1)
        # clean the buffer for init
        self.ui.clr_buf()

    def run(self):
        while True:
            pressed_key = self.ui.key()
            if pressed_key is not 0:
                real_number_pressed = self.map_key(str(pressed_key))
                print "Key pressed: %s" % real_number_pressed
                # put the number in the queue so the screnn manager can show info
                self.shared_queue.put(real_number_pressed)
                self.ui.clr_buf()

            time.sleep(0.1)

    def map_key(self, pressed_key):
        """
        Get the number behind the pressed key. The number correspond to the front panel
        :return:
        """
        map_key = dict()
        map_key["1"] = "1"
        map_key["2"] = "2"
        map_key["3"] = "3"
        map_key["4"] = "4"
        map_key["5"] = "5"
        map_key["6"] = "cancel"
        map_key["7"] = "cancel"
        map_key["8"] = "switch_light"
        map_key["9"] = "6"
        map_key["10"] = "7"
        map_key["11"] = "8"
        map_key["12"] = "9"
        map_key["13"] = "0"
        map_key["14"] = "enter"
        map_key["15"] = "enter"
        map_key["16"] = "nothing"

        return map_key[pressed_key]
