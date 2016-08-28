from pi_switch import RCSwitchReceiver
import signal

continue_reading = True


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

receiver = RCSwitchReceiver()
receiver.enableReceive(2)

num = 0
print "Receiver started, now play with your sensors"
while continue_reading:
    if receiver.available():
        received_value = receiver.getReceivedValue()
        if received_value:
            num += 1
            print("Received[%s]:" % num)
            print(received_value)
            print("%s / %s bit" % (received_value, receiver.getReceivedBitlength()))
            print("Protocol: %s" % receiver.getReceivedProtocol())
            print("")

        receiver.resetAvailable()
