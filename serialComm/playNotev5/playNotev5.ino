#include <EEPROM.h>

int state = 0;
String incomingString = "";
int address = 0;
int noteLimit = 20;
String states[20];
int ticks[20];
int numBytes; // how many bytes of EEPROM for 1 state

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
}


void loop() {
  switch(state) {
    // 0) Arduino reading mode
    case 0: {
      if (Serial.available() > 0) {
      	// get what Python sent
        int incoming = Serial.read();

        // was it end character?
        if (char(incoming)=='@') {
          state = 1; // switch to writing mode - DO NOT MODIFY
        } else {
          incomingString = incomingString + char(incoming); // add to string of notes
        }
      }
      break;
    }
    
    // 1) Arduino processing mode (w/ writing capability)
    case 1: {
      while (incomingString.length() > 1) {        
        // parse single note
        // ...get delimiter indices
        int starIndex = incomingString.indexOf('*');
        int commaIndex = incomingString.indexOf(",");

        // ...perform split
        String state = incomingString.substring(0, commaIndex);
        int tick = incomingString.substring(commaIndex+1, starIndex).toInt();

        // ...update incomingString
        incomingString = incomingString.substring(starIndex+1);

        // define memory required (only first time through case)
        if (numBytes == 0) {
          numBytes = state.length()/8 + 1; // how many bytes of EEPROM for 1 state
        }

        // store state to EEPROM
        // ...split into bytes
        for (int i = 0; i < numBytes; i++) {
          word toWrite;
          if (state.length() < 8) {
            toWrite = state.toInt();
          } else {
            Serial.println(state.substring(0,8));
            toWrite = state.substring(0,8).toInt();
            state = state.substring(8);
            Serial.println(toWrite);
          }
        }
        if (address < noteLimit) {
          states[address] = state;
          ticks[address] = tick;
          address++;
        }
      }
      Serial.println(incomingString);
      incomingString = ""; // clear before receiving more data
      state = 2; // switch to Arduino acting mode
      break;
    }
    
    // 2) Arduino acting mode (w/ writing capability)
    case 2: {
      state = 3;
      break;
    }
      
    // 3) DO NOT MODIFY - exists solely to switch the Arduino back to reading mode when it's ready to process more data
    case 3: {
      Serial.print("%");
      state = 0;
      break;
    }
      
    // END
    default:
      break;
  }
}