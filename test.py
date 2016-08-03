from Controllers import ScreenManager, KeypadManager
import Queue
import bv4242 as b
import i2c
# main


if __name__ == '__main__':
    # # prepare a queue to share data betwen threads
    # shared_queue = Queue.Queue()
    #
    # # run the screen thread
    # screen_thread = ScreenManager(shared_queue)
    # screen_thread.start()
    #
    # # run the keypad thread
    # keypad_thread = KeypadManager(shared_queue)
    # keypad_thread.start()

    i2c_address = 0x12
    i2c_chan = 1
    bus = i2c.IIC(i2c_address, i2c_chan)

    # Message send to the arduino
    START_SIREN = 1  # ask the arduino to turn on the siren
    STOP_SIREN = 2  # ask the arduino to stop the siren
    DELAY_SIREN = 3  # ask the arduino to start the siren in 20 sec
    CANCEL_DELAY_SIREN = 4  # cancel delay siren

    # Response from arduino
    START_SIREN_ACK = 10
    STOP_SIREN_ACK = 20
    DELAY_SIREN_ACK = 30
    CANCEL_DELAY_SIREN_ACK = 40

    bus.i2c([DELAY_SIREN], 0)
    reponse = bus.read(1)
    print reponse

    print "wait 5 secondes"
    import time
    time.sleep(5)
    bus.i2c([CANCEL_DELAY_SIREN], 0)
    reponse = bus.read(1)
    print reponse

