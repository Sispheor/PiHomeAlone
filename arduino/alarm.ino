#include <Wire.h>

#define SLAVE_ADDRESS 0x12
// reveided data from RPI
int dataReceived =        0;
int returnedData =        0;
int START_SIREN_ACK =     10;
int STOP_SIREN_ACK =      20;
int DELAY_SIREN_ACK =     30;
int CANCEL_DELAY_SIREN =  40;

// used to set the siren state
int sirenState = LOW;
// used to know if a delayed start has been asked
boolean delayed_siren_asked = false;
// used to know id the use has canceled his request (when the code to disarme the alarm is ok)
boolean delayed_siren_canceled = false;
// delay to wait before switch on the siren
long delay_time = 20000;   // 20 seconde delay


void setup() {
  // used to monitor and debug
  Serial.begin(9600);
  // start listening
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
}

void loop() {
  if (delayed_siren_asked){
    myDelay(delay_time);  // wait the delay
    Serial.print("Delay over. ");
    // check if the user has canceled before the end of the delay time
    if (delayed_siren_canceled){
      Serial.println("Delayed siren canceled by the user. Do not start the siren");
      delayed_siren_asked = false;
      delayed_siren_canceled = false;
    }else{
      Serial.println("Delayed siren not canceled by the user. Alarm !!!");
      startSiren();
      delayed_siren_asked = false;
      delayed_siren_canceled = false;
    }

  }

  // take a breath
  delay(100);
}

/*
 * This is used to wait a delay without breaking the main loop
 */
void myDelay(unsigned long ms) {              // ms: duration
    unsigned long start = millis();           // start: timestamp
    for (;;) {
        unsigned long now = millis();         // now: timestamp
        unsigned long elapsed = now - start;  // elapsed: duration
        if (elapsed >= ms)                    // comparing durations: OK
            return;
    }
}

void receiveData(int byteCount) {
  while (Wire.available()) {
    dataReceived = Wire.read();
    Serial.print("Received order number : ");
    Serial.println(dataReceived);
    switch (dataReceived) {
      case 1:    // start the siren
        startSiren();
        break;
      case 2: // stop the siren
        stopSiren();
        break;
      case 3:   // delayed siren
        if (!delayed_siren_asked){
          delayedSiren();
        }
        break;
      case 4: // cancel the delayed siren
        cancelDelayedSiren();
        break;
    }
  }
}

void sendData() {
  Wire.write(returnedData);
}

void startSiren(){
  Serial.println("Start the siren");
  sirenState = HIGH;  // Turn it off
  returnedData = START_SIREN_ACK;
}

void stopSiren(){
  Serial.println("Start the siren");
  returnedData = START_SIREN_ACK;
}

void delayedSiren(){
  Serial.println("Siren will start in 20 sec");
  delayed_siren_asked = true;

}

void cancelDelayedSiren(){
  Serial.println("Cancel delayed siren");
  delayed_siren_canceled = true;
}



















