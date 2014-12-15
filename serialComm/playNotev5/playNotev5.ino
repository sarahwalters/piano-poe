#include <EEPROM.h>
#include <QueueList.h>
#include <Servo.h>

// INITIALIZATIONS & SETUP
// ...for fsm
int fsmState = 0;

// ...for serial comm & writing to EEPROM
int address = 0;
String incomingString = "";
int lastByteLength = 0; // (num. keys in state) % 8
int numBytes = 0; // how many bytes of EEPROM for 1 state

// ...for playing
QueueList<long> ticks;
float speedFactor = 3.75;

// ...servos
Servo sC4, sCsh4, sD4, sDsh4, sE4, sF4, sFsh4, sG4, sGsh4, sA4, sAsh4, sB4;
Servo servos[12] = {sC4, sCsh4, sD4, sDsh4, sE4, sF4, sFsh4, sG4, sGsh4, sA4, sAsh4, sB4}; // in pin order, starting at 2
int offPos[12] = {24, 0, 16, 0, 22, 11, 180, 169, 180, 163, 180, 130};
int onPos[12] = {4, 0, 5, 0, 10, 0, 180, 180, 180, 174, 180, 148};
// 160, 173
int numServos = 12;

// ...setup
void setup() {
  Serial.begin(9600); // set up serial at 9600 baud

  // attach all servos to pins and set to default positions
  for (int i=0; i<numServos; i++) {
    int pin = i+2;
    servos[i].attach(pin);
    servos[i].write(offPos[i]);
  }
}


// MAIN FSM METHOD
void loop() {
  switch(fsmState) {
    // CASE 0 = Arduino reading mode
    case 0: {
      if (Serial.available() > 0) {
      	// get one char from what Python sent
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
    
    // CASE 1 = Arduino processing mode (w/ writing capability)
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
        long tick = incomingString.substring(commaIndex+1, starIndex).toInt();

        // ...update incomingString
        incomingString = incomingString.substring(starIndex+1);

        // define memory required (only first time through case)
        if (numBytes == 0) {
          numBytes = state.length()/8 + 1; // how many bytes of EEPROM for 1 state
        }

        // store size of "remainder" last byte, to reconstruct state later
        if (lastByteLength == 0) {
          lastByteLength = state.length() % 8;
        }

        // store state to EEPROM, byte by byte
        for (int i = 0; i < numBytes; i++) {
          byte toWrite;
          // get one byte (or less)
          if (state.length() < 8) {
            toWrite = stringToByte(state); // less than a byte
          } else {
            toWrite = stringToByte(state.substring(0,8)); // get one byte
            state = state.substring(8); // & update state
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
    
    // CASE 2 = Arduino acting mode (w/ writing capability)
    case 2: {
      Serial.println("In state 2");
      int current = 0;
      long shift = millis();
      while (ticks.count() > 0) {
        long tick = ticks.pop();
        String state = getState(current);
        // wait until it's time to play the note
        while (millis()-shift < tick/speedFactor) {
          delay(5);
        }
        play(state);
        //Serial.print("/");
        Serial.print(tick);
        Serial.print("/");
        Serial.println(millis()-shift);
        
        current++;
        
      }
      fsmState = 3;
      break;
    }
      
    // CASE 3 = DO NOT MODIFY - exists solely to switch the Arduino back to reading mode 
    //          when it's ready to process more data
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


// BYTE/STRING CONVERSION
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


// PARSING EEPROM
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


// INTERFACING W/ SERVOS
void play(String state) {
  for (int i=0; i < state.length(); i++) {
    int val = state.substring(i,i+1).toInt();
    //Serial.print(val);
    int pos;
    if (val == 1) {
      pos = onPos[i];
    } else {
      pos = offPos[i];
    }
    servos[i].write(pos);
  }
}