/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->	http://www.adafruit.com/products/1438
*/

#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_DCMotor *E5Motor = AFMS.getMotor(1);
//Adafruit_DCMotor *G4Motor = AFMS.getMotor(3);

String incomingString = "";

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps

  AFMS.begin();  // create with the default frequency 1.6KHz
}

void loop() {
  if (Serial.available() >0) {
  //recieve information from pyserial
    int incoming = Serial.read();
    if (incoming == 42) {
      Serial.println ("incomingString = " + incomingString);
      int commaIndex = incomingString.indexOf(",");
      int commaIndex2 = incomingString.indexOf(",", commaIndex+1);
    
      String startTime = incomingString.substring(0,commaIndex);
      String duration = incomingString.substring (commaIndex+1, commaIndex2);
      String note = incomingString.substring (commaIndex2+1);
      Serial.println ("startTime = " + startTime);
      Serial.println ("duration  = " + duration);
      Serial.println ("note = " + note);
      
      if (note == "E5"){
        G4Motor->setSpeed(0);
        runE5Motor();
        delay (duration);
        incomingString = "";
       
      }
//      else if (note == "G4"}{
//        E5Motor->setSpeed(0);
//        runG4Motor();
//        delay(duration);
//        incomingString = "";
//      }
     else{
      incomingString = "";
    }
    else {
      
      incomingString = incomingString + char(incoming);
    }
  }
}

  void runE5Motor()
    {  
    E5Motor->run(FORWARD);
    E5Motor->setSpeed(75);  
    delay(500); 
  }
  
//    void runG4Motor()
//    {  
//    G4Motor->run(FORWARD);
//    G4Motor->setSpeed(75);  
//    delay(500); 
//  }
