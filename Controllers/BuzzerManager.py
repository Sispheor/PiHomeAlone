import threading

import RPi.GPIO as GPIO  # import the GPIO library
import time  # import the time library


class BuzzerManager(threading.Thread):

    def __init__(self):
        super(BuzzerManager, self).__init__()
        GPIO.setmode(GPIO.BCM)
        self.buzzer_pin = 4  # set to GPIO pin 4
        GPIO.setup(self.buzzer_pin, GPIO.IN)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        # by default the buzz does not buzz
        GPIO.output(self.buzzer_pin, True)  # set pin to high
        # this is used to stop the arming thread
        self.stop_event = threading.Event()
        # Select a mode. This is a kind of song.
        # Mode = 1 Short double bip, when the system detect en entry
        # Mode = 2 Long bip each second. Used when we arm te system
        self.mode = 1
        print("Buzzer ready")

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        print "Playing Buzzer until stop event"
        while not self.stop_event.is_set():
            self.buzz(self.mode)

        # reset the GPIO ping to cut the sound
        GPIO.setup(self.buzzer_pin, GPIO.IN)

    def buzz(self, mode):

        if mode == 1:   # this is the mode used when a sensor detect something
            delay = 0.1
            for x in range(2):
                GPIO.output(self.buzzer_pin, False)  # set pin to low, the buzzer is buzzing
                time.sleep(delay)  # wait with pin low
                GPIO.output(self.buzzer_pin, True)  # set pin to high
                time.sleep(delay)  # wait with pin high
            time.sleep(1)

        if mode == 2:   # this mode is used to count seconds before the system is armed
            delay = 1
            GPIO.output(self.buzzer_pin, False)  # set pin to low, the buzzer is buzzing
            time.sleep(delay)  # wait with pin low
            GPIO.output(self.buzzer_pin, True)  # set pin to high
            time.sleep(delay)  # wait with pin high

        if mode == 3:     # this is used when we scan a card.
            delay = 0.1
            GPIO.output(self.buzzer_pin, False)  # set pin to low, the buzzer is buzzing
            time.sleep(delay)  # wait with pin low
            GPIO.output(self.buzzer_pin, True)  # set pin to high
            time.sleep(delay)  # wait with pin high

    def stop(self):
        print "Stopping Buzzer"
        self.stop_event.set()
