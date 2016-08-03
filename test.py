from Controllers import ScreenManager, KeypadManager, ArduinoManager
import Queue
import bv4242 as b
import i2c

# main
import RPi.GPIO as gpio

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

    # arduino = ArduinoManager()
    #
    # arduino.start_siren()
    import time
    # time.sleep(3)
    # arduino.stop_siren()
    # time.sleep(3)
    # arduino.delayed_siren()

    BUZZER_PIN = 4
    gpio.cleanup()
    gpio.setmode(gpio.BCM)
    gpio.setup(BUZZER_PIN, gpio.OUT)  # Relay enable
    # defini le port GPIO 4 comme etant une sortie output
    gpio.output(BUZZER_PIN, gpio.HIGH)
    time.sleep(2)

    gpio.output(BUZZER_PIN, gpio.LOW)

    time.sleep(2)

    gpio.output(BUZZER_PIN, gpio.HIGH)


