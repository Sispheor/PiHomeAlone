# Test componant

This part of the doc is used to test each componant of the system before running the main programm.

## Test 433 Mhz receiver
Run the test script. this must be runned as root with sudo.
```
sudo python tests/test433Receiver.py 
```

Then, play with your sensors to get some value. Use this script to get all IDs from your sensor and add each one to the **settings.yml** file.
```
Starting receiver 433
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
Pressed key 5
Pressed key 6
Pressed key D
Pressed key *
```

## Test the adafruit screen
Run the script
```
python tests/test_adafruit_screen.py
```

You should see "test" on the screen

## Test the RFID reader
Run the script
```
python tests/test_rfid_reader.py
```

Then test your card
```
Welcome to the MFRC522 data read example
Press Ctrl-C to stop.
Card detected
Card read UID: 12,102,125,412,70
```

## Test the buzzer
Run the script
```
python tests/test_buzzer.py 
```

The output should look like the following and you should have listened the buzzer during 3 secondes
```
Play sound for 3 secondes
Stop buzzing
```

## Test the connectivity Arduino / Raspberry Pi
Get your i2c bus address
```
sudo i2cdetect -y 1
```

This is an example output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- 12 -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- -- 
```

In this case, my arduino is listening on the base 16 bus address is 0x12

Run the script with the address as argument
```
python tests/test_arduino_rpi_connection.py 0x12
```

The correct output is:
```
Response from aduino: Pong
```
