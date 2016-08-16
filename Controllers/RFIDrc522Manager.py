import threading
from Utils.MFRC522 import MFRC522
import time


class RFIDrc522Manager(threading.Thread):

    def __init__(self, shared_queue):
        super(RFIDrc522Manager, self).__init__()

        # This queue is used to send message to the main thread
        self.shared_queue = shared_queue

        # this is used to stop the thread
        self.stop_event = threading.Event()

        # Create an object of the class MFRC522
        self.MIFAREReader = MFRC522()

        print "RFID reader ready"

    def run(self):
        while not self.stop_event.is_set():
            # Scan for cards
            (status, TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == self.MIFAREReader.MI_OK:
                print "Card detected"

            # Get the UID of the card
            (status, uid) = self.MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == self.MIFAREReader.MI_OK:
                # Print UID
                print "Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]) \
                      + "," + str(uid[4])

                # send the UID to the main thread
                self.shared_queue.put(uid)
                print "Freeze 3 secondes"
                time.sleep(3)
            time.sleep(0.1)
