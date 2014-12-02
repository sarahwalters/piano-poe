#include <EEPROM.h>
#include <QueueList.h>

int fsmState = 0;
String incomingString = "";
int address = 0;
QueueList<int> ticks;
int lastByteLength = 0;
int numBytes = 0; // how many bytes of EEPROM for 1 state


void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  for (int i=0; i < 1000; i++) {
    EEPROM.write(i, B0);
  }
}


void loop() {
  switch(fsmState) {
    // 0) Arduino reading mode
    case 0: {
      if (Serial.available() > 0) {
      	// get what Python sent
        int incoming = Serial.read();

        // was it end character?
        if (char(incoming)=='@') {
          fsmState = 1; // switch to writing mode - DO NOT MODIFY
        } else {
          incomingString = incomingString + char(incoming); // add to string of notes
        }
      }
      break;
    }
    
    // 1) Arduino processing mode (w/ writing capability)
    case 1: {
      Serial.println("In state 1");
      Serial.println(incomingString);
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
          byte toWrite;
          if (state.length() < 8) {
            toWrite = stringToByte(state);
            if (lastByteLength == 0) {
              lastByteLength = state.length();
            }
          } else {
            toWrite = stringToByte(state.substring(0,8));
            state = state.substring(8);
          }
          EEPROM.write(address, toWrite);
          address++;
        }
        ticks.push(tick);
      }
      if (incomingString == "&") {
        fsmState = 2; // switch to Arduino acting mode
      } else {
        fsmState = 3; // not done - skip acting mode
      }
      incomingString = ""; // clear before receiving more data
      break;
    }
    
    // 2) Arduino acting mode (w/ writing capability)
    case 2: {
      Serial.println("In state 2");
      int current = 0;
      int shift = millis();
      while (ticks.count() > 0) {
        int tick = ticks.pop();
        String state = getState(current);
        // wait until it's time to play the note
        while (millis()-shift < tick) {
          delay(5);
        }
        Serial.print(tick);
        Serial.print("/");
        Serial.print(millis()-shift);
        Serial.print("/");
        Serial.println(state);
        current++;
        play(state);
      }
      fsmState = 3;
      break;
    }
      
    // 3) DO NOT MODIFY - exists solely to switch the Arduino back to reading mode when it's ready to process more data
    case 3: {
      Serial.print("%");
      fsmState = 0;
      break;
    }
      
    // END
    default:
      break;
  }
}

byte stringToByte(String s) {
  int res = 0;
  int power = 1;
  int mult;
  for (int i=s.length(); i > 0; i--) {
    mult = s.substring(i-1, i).toInt(); // 1 or 0
    res = res + mult*power;
    power = power * 2;
  }
  return byte(res);
}

String byteToString(byte b) {
  int num = int(b);
  String res = "";
  int power = 128;
  for (int i=0; i<8; i++) {
    if (num >= power) {
      num = num - power;
      res = res + "1";
    } else {
      res = res + "0";
    }
    power = power/2;
  }
  return res;
}

String getState(int stateNum) {
  String res = "";
  int startAddress = stateNum * numBytes;
  int endAddress = startAddress + numBytes - 1;
  for (int i = startAddress; i < endAddress; i++) {
    res = res + byteToString(EEPROM.read(i));
  }
  String wholeLastByte = byteToString(EEPROM.read(endAddress));
  return res + wholeLastByte.substring(8-lastByteLength);
}

void play(String state) {
  Serial.print("");
}