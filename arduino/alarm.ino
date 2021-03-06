#include <Wire.h>

#define SLAVE_ADDRESS 0x12
// reveided data from RPI
int dataReceived =        0;
int returnedData =        0;
// returned data
int START_SIREN_ACK =     10;
int STOP_SIREN_ACK =      20;
int DELAY_SIREN_ACK =     30;
int CANCEL_DELAY_SIREN =  40;
int PONG =                50;
int SIREN_STATUS_LOW =     60;
int SIREN_STATUS_HIGH =    61;

// used to set the siren state
int sirenState = HIGH;
// used to know if a delayed start has been asked
boolean delayed_siren_asked = false;
// used to know id the use has canceled his request (when the code to disarme the alarm is ok)
boolean delayed_siren_canceled = false;
// delay to wait before switch on the siren
long delay_time = 20000;   // 20 seconde delay
// the pin number where the relay is plugged
int relay_pin_number = 7;


void setup() {
  // used to monitor and debug
  Serial.begin(9600);
  // start listening
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  // initialize digital pin  as an output. This pin must be plugged to the relay that close the siren circuit
  sirenState = HIGH;
  pinMode(relay_pin_number, OUTPUT);
  // by default the relay is off
  digitalWrite(relay_pin_number, sirenState);
}

void loop() {
  if (delayed_siren_asked){
    myDelay(delay_time);  // wait the delay
    Serial.print("Delay over. delayed_siren_canceled Bool is: ");
    Serial.println(delayed_siren_canceled);
    // check if the user has canceled before the end of the delay time
    if (delayed_siren_canceled == true){
      Serial.println("Delayed siren canceled by the user. Do not start the siren");
    }else{
      Serial.println("Delayed siren not canceled by the user. Alarm !!!");
      startSiren();
    }
    // reset state
    delayed_siren_asked = false;
    delayed_siren_canceled = false;
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
        Serial.println("Order: Start the siren");
        startSiren();
        break;
      case 2: // stop the siren
        Serial.println("Order: Stop the siren");
        stopSiren();
        break;
      case 3:   // delayed siren
        Serial.println("Order: Delayed siren");
        if (!delayed_siren_asked){
          delayed_siren_canceled = false;
          delayedSiren();
        }
        break;
      case 4: // cancel the delayed siren
        Serial.println("Order: Cancel the delayed siren");
        cancelDelayedSiren();
        break;
      case 5: // ping
        Serial.println("Order: Ping");
        pong();
      break;
      case 6: // get the current siren status
        Serial.println("Order: Get siren status");
        get_siren_status();
        break;
    }
  }
}

void sendData() {
  Wire.write(returnedData);
}

void startSiren(){
  Serial.println("Start the siren");
  digitalWrite(relay_pin_number, LOW);   // turn the RELAY on (HIGH is the voltage level)
  sirenState = LOW;  // save the state
  returnedData = START_SIREN_ACK;
}

void stopSiren(){
  Serial.println("Stop the siren");
  digitalWrite(relay_pin_number, HIGH);   // turn the RELAY off by making the voltage HIGH
  sirenState = HIGH;
  returnedData = STOP_SIREN_ACK;
}

void delayedSiren(){
  Serial.println("Siren will start in 20 sec");
  delayed_siren_asked = true;
  returnedData = DELAY_SIREN_ACK;
}

void cancelDelayedSiren(){
  Serial.println("Cancel delayed siren");
  delayed_siren_canceled = true;
  returnedData = CANCEL_DELAY_SIREN;
}

void pong(){
  Serial.println("Received ping, return pong");
  returnedData = PONG;
}

void get_siren_status(){
  if (sirenState == LOW){
    Serial.println("Siren status LOW");
    returnedData = SIREN_STATUS_LOW;
  }else{
    Serial.println("Siren status HIGH");
    returnedData = SIREN_STATUS_HIGH;
  }

}
