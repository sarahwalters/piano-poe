/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->	http://www.adafruit.com/products/1438
*/

#include <Wire.h>
#include <Note.h>
#include <QueueList.h>
#include <Adafruit_MotorShield.h>
#include <MemoryFree.h>
#include "utility/Adafruit_PWMServoDriver.h"
#include <avr/pgmspace.h>

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_DCMotor *E4Motor = AFMS.getMotor(1);
Adafruit_DCMotor *G4Motor = AFMS.getMotor(3);

QueueList<Note> qList;

int state = 0;
String incomingString = "";

int bottomSwitchPin = 2;         // the number of the input pin

/*int state = HIGH;      // the current state of the output pin
int reading;           // the current reading from the input pin
int previous = LOW;    // the previous reading from the input pin*/

// the follow variables are long's because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
long time = 0;         // the last time the output pin was toggled
long debounce = 200;   // the debounce time, increase if the output flickers

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  AFMS.begin(); // create with the default frequency 1.6KHz
  pinMode(bottomSwitchPin, INPUT);
}

void loop() {
  runMotor(E4Motor);
  runMotor(G4Motor);
  /*
  int incoming;
  switch(state) {
    // PYTHON -> ARDUINO
    case 0:  // append new info to incomingString
      if (Serial.available() > 0) {
        incoming = Serial.read();        
        incomingString = incomingString + char(incoming);

        // received ! (end signal) yet?
        if (incoming == 33) {
          Serial.println(incomingString);
          state = 1;
        }
      }
      break;
      
    // WITHIN ARDUINO
    case 1:  // split info into individual notes
      while (incomingString != "!") {
        // get single note from incomingString
        int starIndex = incomingString.indexOf("*");
        String noteStr = incomingString.substring(0, starIndex);
        incomingString = incomingString.substring(starIndex+1);
      
        // parse single note
        // ...split by commas
        int commaIndex1 = noteStr.indexOf(",");
        int commaIndex2 = noteStr.indexOf(",", commaIndex1 + 1);
      
        // ...start time and duration
        int startTime = noteStr.substring(0,commaIndex1).toInt();
        int duration = noteStr.substring (commaIndex1+1, commaIndex2).toInt();
      
        // ...note name and octave
        String nameAndOctave = noteStr.substring (commaIndex2+1);
        int octave = nameAndOctave.substring(1).toInt();
        char charBuf[2];
        nameAndOctave.toCharArray(charBuf, 2);
        char name = charBuf[0];
      
        // ...make an object
        Note current = Note(startTime, duration, name, octave);
        qList.push(current);
      }
      Serial.println(qList.count());
      //Serial.println("Moving on to playing");
      state = 2;
      break;
      
    // ARDUINO -> MOTOR
    case 2:
      state = 3;
      /*Note top;
      Note currentSet[8];
      if (qList.count() != 0) {
        top = qList.pop();
        Serial.println(String(top.getName()) + String(top.getOctave()));
      }*/
      
      /*
      while (!qList.isEmpty()) {
        Serial.println(String(qList.pop().getName()));
        int topStart = top.getStart();
        /*boolean stillSame = true;
        Note currentSet[8] = {top};
        int index = 1;
      
        //Serial.println(qList.count());
      
        while (stillSame && !qList.isEmpty()) {
          Serial.println("In the while loop");
          Note next = qList.pop();
          Serial.println(String(next.getName()) + String(next.getOctave()));
//          if (next.getStart() == topStart) {
//            currentSet[index] = qList.pop(); // this is Note next
//            index = index + 1;
//          } else {
//            stillSame = false;
//            Serial.println("In the else!");
//          }
        }
      }
     
      break;
      
    // ARDUINO -> PYTHON
    case 3:
      Serial.println(qList.count());
      state = 0;b
      break;
  }
}*/

/*
void play(String note) {
  
  reading = digitalRead(bottomSwitchPin);
  
  if (note=="E4") {
    runMotor(E4Motor);
    if (reading == HIGH && previous == LOW && millis() - time > debounce) {
      E4motor->setSpeed(0);
      delay(duration);
      runMotor (E4Motor)
    }
    time = millis();
    previous = reading;
    
  } else if (note == "G4") {
    runMotor(G4Motor);
        if (reading == HIGH && previous == LOW && millis() - time > debounce) {
          E4motor->setSpeed(0);
          delay(duration);
          runMotor(G4Motor)
        }
    time = millis();
    previous = reading;
  }*/
}

void runMotor(Adafruit_DCMotor *motor) {
  motor->run(FORWARD);
  motor->setSpeed(0);
  /*delay(500);
  motor->setSpeed(0);*/
}
