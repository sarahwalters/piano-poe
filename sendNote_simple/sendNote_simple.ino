#include <Wire.h>
#include <Note.h>
#include <QueueList.h>

int state = 0;
String incomingString = "";
QueueList<Note> qList;
int minQueueSize = 0;

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
}

void loop() {
  switch(state) {
    // Arduino reading mode
    case 0: {
      if (Serial.available() > 0) {
        
        int incoming = Serial.read();
        if (char(incoming)=='@') { // done with reading mode - DO NOT MODIFY
          state = 1; // switch to writing mode
        } else {
          incomingString = incomingString + char(incoming);
        }
      }
      break;
    }
    
    // Arduino processing mode (w/ writing capability)
    case 1: {
      // process incomingString
      while (incomingString.length() > 1) {
        // get single note from front (FIFO)
        int starIndex = incomingString.indexOf('*');
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
      //Serial.println(String(qList.count()));
      incomingString = ""; // clear before getting more notes
      state = 2; // switch to Arduino acting mode
      break;
    }
    
    // Arduino acting mode (w/ writing capability)
    case 2: {
      while (qList.count() > minQueueSize) {
        Note next = qList.pop();
        Serial.print(String(next.getName()) + String(next.getOctave()));
        Serial.print(',');
      }
      state = 3;
      break;
    }
      
    // This case exists solely to switch the Arduino back to reading mode when it's
    // ready to process more data. DO NOT MODIFY
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