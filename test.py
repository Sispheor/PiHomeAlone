import Queue
from MainThread import MainThread
from Controllers import RFIDrc522Manager

# main
if __name__ == '__main__':

    # main_thread = MainThread()
    # main_thread.start()

    # prepare a queue to share data between this threads and the keyboard
    shared_queue_rfid_reader = Queue.Queue()

    rfid = RFIDrc522Manager(shared_queue_rfid_reader)

    rfid.start()


