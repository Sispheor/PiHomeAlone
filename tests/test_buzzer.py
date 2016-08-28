import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
buzzer_pin = 4  # set to GPIO pin 4
GPIO.setup(buzzer_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)

# by default the buzz does not buzz
GPIO.output(buzzer_pin, True)   # set pin to high

# play sound
print "Play sound for 3 secondes"
GPIO.output(buzzer_pin, False)   # set pin to high
# wait a litle and cut off the buzzer
time.sleep(2)
print "Stop buzzing"
GPIO.output(buzzer_pin, True)   # set pin to high

# Clean GPIO
GPIO.cleanup()
