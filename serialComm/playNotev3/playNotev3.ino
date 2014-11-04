#include <Wire.h>
#include <Note.h>
#include <QueueList.h>

// TUNABLE PARAMETERS //
int minQueueSize = 8;


// NONTUNABLE INITIALIZATIONS //
int state = 0; 
QueueList<Note> qList;
String incomingString = "";


// FUNCTIONS //
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
      // 1) are there notes to remove?
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

      // 2) is it the overall end character (Python done sending notes?)
      if (incomingString == "&") {
        minQueueSize = 0; // use up all notes at the end
      }
      
      // Done processing this incomingString
      incomingString = ""; // clear before receiving more data
      state = 2; // switch to Arduino acting mode
      break;
    }
    
    // Arduino acting mode (w/ writing capability)
    case 2: {
      while (qList.count() > minQueueSize) {
        // get first note in next set to be played
        Note leader = qList.pop();

        // establish array of more notes to be played simultaneously
        Note noteSet[8] = {leader};
        int i = 1;

        // add subsequent "follower" notes which start at the same time to the array
        int leaderStart = leader.getStart();
        if (qList.count() > 0) {
          Note follower = qList.peek();

          // while notes start at the same time...
          while (follower.getStart() == leaderStart) {
            noteSet[i] = qList.pop(); // add to array
            i++;

            // look at next; if there is no next, break
            if (qList.count() > 0) {
              follower = qList.peek();
            } else {
              break;
            }
          }
        }

        // play the notes
        Serial.print(noteSet[0].getStart());
        Serial.print(':');
        for (int j=0; j<i; j++) {
          Serial.print(getNameAndOctave(noteSet[j]));
          Serial.print('/');
        }
        Serial.println();
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

String getNameAndOctave(Note n) {
  return String(n.getName()) + String(n.getOctave());
}