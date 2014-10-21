/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->	http://www.adafruit.com/products/1438
*/

//#include <Wire.h>
//#include <Adafruit_MotorShield.h>
//#include "utility/Adafruit_PWMServoDriver.h"

//Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
//Adafruit_DCMotor *myMotor = AFMS.getMotor(1);

String incomingString = "";

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps

  //AFMS.begin();  // create with the default frequency 1.6KHz
 
  // Set the speed to start, from 0 (off) to 255 (max speed)
  //myMotor->setSpeed(150);
  //myMotor->run(FORWARD);
  // turn on motor
 // myMotor->run(RELEASE);
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
    
      incomingString = "";
    } else {
      incomingString = incomingString + char(incoming);
    }
  }
  
 
  
//  byte i;
//
//  myMotor->run(FORWARD);
//  for (i=0; i<255; i++) {
//    myMotor->setSpeed(i);  
//    delay(10);
//  }
//  for (i=255; i!=0; i--) {
//    myMotor->setSpeed(i);  
//    delay(10);
//  }
//  
//  Serial.print("tech");
//  myMotor->run(RELEASE);
//  delay(1000);
}
