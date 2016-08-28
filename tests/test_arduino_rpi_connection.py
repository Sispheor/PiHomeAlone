import sys
import os

CUR_FOLDER = os.path.dirname(os.path.abspath(__file__))
PARENT_FOLDER = os.path.dirname(CUR_FOLDER)
sys.path.append(PARENT_FOLDER)

from Utils import i2c

PING = 5    # ping byte code
PONG = 50   # pong byte code

if len(sys.argv) > 1:
    addr = int(sys.argv[1][2:], 16)
    i2c_address = addr
else:
    print "You must give your i2c addres."
    print "E.g: python tests/test_arduino_rpi_connection.py 0x12"
    sys.exit(1)

# edit this address. Use the following shell command to know you arduino i2c address
# sudo i2cdetect -y 1
i2c_chan = 1
bus = i2c.IIC(i2c_address, i2c_chan)

try:
    bus.i2c([PING], 0)
    response = bus.read(1)
    if response[0] == PONG:
        print "Response from aduino: Pong"
except IOError:
    print "No aduino connection. Check if the bus address %c is right with \'sudo i2cdetect -y 1\'" % i2c_address
