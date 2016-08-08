# from Controllers import ScreenManager, KeypadManager, ArduinoManager, BuzzerManager, MessageReceiver
from MainThread import MainThread
import Queue

from flask import Flask

from RestAPI import FlaskAPI

# main
#import RPi.GPIO as gpio

if __name__ == '__main__':

    main_thread = MainThread()
    main_thread.start()



