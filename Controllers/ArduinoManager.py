from Utils import i2c

# Message send to the arduino
START_SIREN = 1         # ask the arduino to turn on the siren
STOP_SIREN = 2          # ask the arduino to stop the siren
DELAY_SIREN = 3         # ask the arduino to start the siren in 20 sec
CANCEL_DELAY_SIREN = 4  # cancel delay siren
PING = 5                # Ping the arduino
GET_SIREN_STATE = 6     # Get the cuirrent status of the siren

# Response from arduino
START_SIREN_ACK = 10
STOP_SIREN_ACK = 20
DELAY_SIREN_ACK = 30
CANCEL_DELAY_SIREN_ACK = 40
PONG = 50
SIREN_STATUS_LOW = 60
SIREN_STATUS_HIGH = 61


class ArduinoManager:
    """
    Class used to send message to the arduino
    """
    def __init__(self):
        i2c_address = 0x12
        i2c_chan = 1
        self.bus = i2c.IIC(i2c_address, i2c_chan)

    def start_siren(self):
        self.bus.i2c([START_SIREN], 0)
        response = self.bus.read(1)
        print response
        return response

    def stop_siren(self):
        self.bus.i2c([STOP_SIREN], 0)
        response = self.bus.read(1)
        print response
        return response

    def delayed_siren(self):
        self.bus.i2c([DELAY_SIREN], 0)
        response = self.bus.read(1)
        print response
        return response

    def cancel_delayed_siren(self):
        self.bus.i2c([CANCEL_DELAY_SIREN], 0)
        response = self.bus.read(1)
        print response

    def ping(self):
        self.bus.i2c([PING], 0)
        response = self.bus.read(1)
        print response

    def get_siren_status(self):
        self.bus.i2c([GET_SIREN_STATE], 0)
        response = self.bus.read(1)
        print response
        if response[0] == SIREN_STATUS_HIGH:
            print "siren is off"
            return "off"
        else:
            print "Siren is on"
            return "on"
