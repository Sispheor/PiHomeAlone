from Controllers import ScreenManager, KeypadManager
import Queue
# main


if __name__ == '__main__':
    # prepare a queue to share data betwen threads
    shared_queue = Queue.Queue()

    # run the screen thread
    screen_thread = ScreenManager(shared_queue)
    screen_thread.start()

    # run the keypad thread
    keypad_thread = KeypadManager(shared_queue)
    keypad_thread.start()

