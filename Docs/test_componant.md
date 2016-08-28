# Test componant

This part of the doc is used to test each componant of the system for puting it in production.

## Test 433 Mhz receiver

Run the test script. this must be runned as root with sudo.
```
sudo python tests/test433Receiver.py 
```

Then, play with your sensors to get some value. Use this script to get all IDs from your sensor and add each one to the **settings.yml** file.
```
Starting receiver 433
Receiver 433; Received id: 1234567
Receiver 433; Received id: 1234567
Receiver 433; Received id: 1234567
```

## Test the keypad
Run the test script
```
python tests/test_matrixKeypad.py 
```

Then press some key on your keypad
```
Press buttons on your keypad. Ctrl+C to exit.
8
9
D
#
```

## Test the adafruit screen
Run the script
```
python tests/test_adafruit_screen.py
```

You should see "test" on the screen