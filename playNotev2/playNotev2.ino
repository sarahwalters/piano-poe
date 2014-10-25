/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->	http://www.adafruit.com/products/1438
*/

#include <Wire.h>
#include <Note.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_DCMotor *E4Motor = AFMS.getMotor(1);
Adafruit_DCMotor *G4Motor = AFMS.getMotor(3);

//Note test = Note(1, 2, 'E', 3);
//Note another = Note(10, 20, 'F', 5);
//Note notes[100];

String incomingString = "";
String state = "reading";

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  AFMS.begin(); // create with the default frequency 1.6KHz
}

void loop() {
  if (state == "reading" && Serial.available() > 0) {
    // append new info to incomingString
    int incoming = Serial.read();
    incomingString = incomingString + char(incoming);
    
    // received ! (end signal) yet?
    if (incoming == 33) {
      state = "processing"; // switch states
      Serial.println("Done");
    }
  } else if (state == "processing") {
    // split info into individual notes
    while (incomingString != "!") {
      // get single note from incomingString
      int starIndex = incomingString.indexOf("*");
      String noteStr = incomingString.substring(0, starIndex);
      incomingString = incomingString.substring(starIndex+1);
      Serial.println(noteStr);
      
      // parse single note
//      int commaIndex1 = noteStr.indexOf(",");
//      int commaIndex2 = noteStr.indexOf(",", commaIndex1 + 1);
//      String startTime = noteStr.substring(0,commaIndex1);
//      String duration = noteStr.substring (commaIndex1+1, commaIndex2);
//      String nameAndOctave = noteStr.substring (commaIndex2+1);
//      Serial.println(nameAndOctave);
    }
  }
}

void play(String note) {
  if (note=="E4") {
    runMotor(E4Motor);
  } else if (note == "G4") {
    runMotor(G4Motor);
  }
}

void runMotor(Adafruit_DCMotor *motor) {
  motor->run(FORWARD);
  motor->setSpeed(75);
  delay(500);
  motor->setSpeed(0);
}
