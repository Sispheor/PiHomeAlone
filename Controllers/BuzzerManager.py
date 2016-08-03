import RPi.GPIO as GPIO  # import the GPIO library
import time  # import the time library


class Buzzer(object):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.buzzer_pin = 4  # set to GPIO pin 4
        GPIO.setup(self.buzzer_pin, GPIO.IN)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        print("Buzzer ready")

    def buzz(self, pitch, duration):

        if pitch == 0:
            time.sleep(duration)
            return
        period = 1.0 / pitch  # in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
        delay = period / 2  # calcuate the time for half of the wave
        cycles = int(duration * pitch)  # the number of waves to produce is the duration times the frequency

        for i in range(cycles):  # start a loop from 0 to the variable "cycles" calculated above
            GPIO.output(self.buzzer_pin, True)  # set pin 18 to high
            time.sleep(delay)  # wait with pin 18 high
            GPIO.output(self.buzzer_pin, False)  # set pin 18 to low
            time.sleep(delay)  # wait with pin 18 low

    def play(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        x = 0

        pitches = [500, 1000, 5000]
        duration = [0.05, 0.05, 0.05]
        for p in pitches:
            self.buzz(p, duration[x])  # feed the pitch and duration to the func
            time.sleep(duration[x])
            x += 1

        GPIO.setup(self.buzzer_pin, GPIO.IN)
