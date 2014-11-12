#include <Wire.h>
#include <Note.h>
#include <QueueList.h>
#include <avr/pgmspace.h>
#include <Servo.h>

// TUNABLE PARAMETERS //
int minQueueSize = 8;
int ticksPerSec = 18; // midi time -> second conversion


// NONTUNABLE INITIALIZATIONS //
int state = 0; 
QueueList<Note> qList;
String incomingString = "";
long startMillis = 0;
Servo sE4;
Servo sG4;
Servo servos[2] = {sE4, sG4};
int servoEnd[2] = {-1, -1};
int startPos = 0;
int stopPos = 20;


// FUNCTIONS //
void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  sE4.attach(7);
  sG4.attach(9);
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
        //Serial.println(nameAndOctave);
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
        servoEndPush(leader);

        // establish array of more notes to be played simultaneously
        int i = 1;
        String noteIds[10] = {getNameAndOctave(leader)}; // revisit?

        // add subsequent "follower" notes which start at the same time to the array
        int leaderStart = leader.getStart();
        if (qList.count() > 0) {
          Note follower = qList.peek();

          // while notes start at the same time...
          while (follower.getStart() == leaderStart) {
          	qList.pop(); // this is follower - already have; need to get out of queue
            noteIds[i] = getNameAndOctave(follower); // add to set to play
            servoEndPush(follower); // store end time
            i++;

            // look at next; if there is no next, break
            if (qList.count() > 0) {
              follower = qList.peek();
            } else {
              break;
            }
          }
        }

        while (ticks() < leaderStart) {
        	Serial.print(".");
        	for (int i=0; i < sizeof(servoEnd); i++) {
        		int endTime = servoEnd[i];
        		if (endTime < ticks() && endTime > 0) { // time to end note
        			// stop the appropriate servo
        			servos[i].write(stopPos);
        			Serial.println("END: " + String(servoEnd[i]) + "--" + String(ticks()));
        			servoEnd[i] = -1;
        		}
        	}
        	delay(10);
        }
        Serial.println(getNameAndOctave(leader));
        Serial.println("START: " + String(leader.getStart()) + "--" + String(ticks()));
        playNotes(noteIds);
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

long ticks() {
  long ms = millis() - startMillis;
  return ms*ticksPerSec/1000;
}

void servoEndPush(Note n) {
	String id = getNameAndOctave(n);
	if (id == "E4") {
		servoEnd[0] = n.getStart() + n.getDuration();
	} else if (id == "G4") {
		servoEnd[1] = n.getStart() + n.getDuration();
	}
	//Serial.println(String(servoEnd[0]) + ", " + String(servoEnd[1]));
}

void playNotes(String noteSet[10]) {
	// if first note played, then set start time of piece to ticks()
	if (startMillis == 0) {
		startMillis = millis();
	}
	for (int i=0; i < sizeof(noteSet); i++) {
		if (noteSet[i] == "E4") {
			sE4.write(startPos);
		} else if (noteSet[i] == "G4") {
			sG4.write(startPos);
		}
	}	
}