#include <Wire.h>

int state = 0;
String incomingString = "";
int incoming;

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
}

void loop() {
  switch(state) {
    // PYTHON -> ARDUINO
    case 0:
      if (Serial.available() > 0) {
        incoming = Serial.read();
        if (char(incoming)=='@') { // SWITCH to Arduino writing mode
          Serial.println(incomingString);
          state = 1;
        } else {
          incomingString = incomingString + char(incoming);
        }
      }
      break;
      
    // ARDUINO -> PYTHON
    case 1:
      Serial.println("%"); // SWITCH to Python writing mode
      incomingString = ""; // clear before getting more notes
      state = 0;
      break;
      
    // END
    default:
      break;
  }
}
