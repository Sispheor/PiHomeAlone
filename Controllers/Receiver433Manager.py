import threading
from pi_switch import RCSwitchReceiver
import RPi.GPIO as GPIO  # import the GPIO library
import time  # import the time library


class Receiver433Manager(threading.Thread):

    def __init__(self, shared_queue):
        super(Receiver433Manager, self).__init__()
        # shared queue to send data (received UID)to the main thread
        self.shared_queue = shared_queue
        # init the lib
        self.receiver = RCSwitchReceiver()
        # WiringPi 2 = RPI pin 13 = GPIO 27
        self.receiver.enableReceive(2)
        # this is used to stop the arming thread
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            if self.receiver.available():
                received_value = self.receiver.getReceivedValue()
                if received_value:
                    # print received_value
                    # send the value to the main thread
                    self.shared_queue.put(received_value)
                    # wait before listen again
                    time.sleep(1)
            self.receiver.resetAvailable()
            # take a breath
            time.sleep(0.1)

    def stop(self):
        """
        Stop the thread
        :return:
        """
        self.stop_event.set()
