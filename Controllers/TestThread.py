import threading


class TestThread(threading.Thread):

    def __init__(self, shared_queue):

        super(TestThread, self).__init__()
        self.shared_queue = shared_queue

    def run(self):
        print "Run test thread"
        while True:
            if not self.shared_queue.empty():
                val = self.shared_queue.get()
                print val
