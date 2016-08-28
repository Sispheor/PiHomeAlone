from Controllers import AdafruitScreenManager
from Utils.TimerReset import TimerReset

screen = AdafruitScreenManager()


def turn_off_screen():
    screen.turn_light_off()


import time
timer = TimerReset(10, turn_off_screen)
timer.start()
time.sleep(5)

# reset the timer for 20 seconds
timer.reset(10)

time.sleep(12)

if timer.isAlive():
    print "timer still aline, reseting it"
    timer.reset(10)
else:
    print "timer not anymore aline, recreating a new one"
    screen.turn_light_on()
    timer = TimerReset(10, turn_off_screen)
    timer.start()

