#include <Wire.h>
#include <Note.h>
#include <QueueList.h>
#include <avr/pgmspace.h>
#include <Servo.h>

// TUNABLE PARAMETERS //
int minQueueSize = 8;
int ticksPerSec = 18; // midi time -> second conversion


// NONTUNABLE INITIALIZATIONS //
// ... for FSM
int state = 0;
String incomingString = "";
QueueList<Note> qList;

// ... for timing
long startMillis = 0;

// ...servo stuff
Servo sC4;
Servo sD4;
Servo sE4;
Servo sG4;
Servo servos[4] = {sC4, sD4, sE4, sG4}; // in pin order, starting at 2
int servoEnd[4] = {-1, -1, -1, -1};
int numServos = 4;
int onPos = 0;
int offPos = 20;


// MAIN FUNCTIONS //
void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps

  // attach all servos to pins and set to default positions
  for (int i=0; i<numServos; i++) {
  	int pin = i+2;
  	servos[i].attach(pin);
  	servos[i].write(100);
  }
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
      // are there still notes in incomingString?
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
        char charBuf[2];
        nameAndOctave.toCharArray(charBuf, 2);
        char name = charBuf[0];
        int octave = nameAndOctave.substring(1).toInt();
        
        // ...make an object
        Note current = Note(startTime, duration, name, octave);
        qList.push(current);
      }

      // is remaining 1 character the end-of-piece character? (Python done sending notes) 
      if (incomingString == "&") {
        minQueueSize = 0; // use up all notes at the end
      }
      
      // Done processing this incomingString
      incomingString = ""; // clear before receiving more data
      state = 2; // switch to Arduino acting mode
      break;
    }
    
    // 2) Arduino acting mode (w/ writing capability)
    case 2: {
      while (qList.count() > minQueueSize) {
        // get first note in next set to be played
        Note leader = qList.pop();

        // establish array of more notes to be played simultaneously
        int i = 1;
        Note currentNotes[10] = {leader}; // revisit?

        // add subsequent "follower" notes which start at the same time to the array
        int leaderStart = leader.getStart();
        if (qList.count() > 0) {
          Note follower = qList.peek();

          // while notes start at the same time...
          while (follower.getStart() == leaderStart) {
          	qList.pop(); // this is follower - already have; need to get out of queue
            currentNotes[i] = follower; // add to set to play
            i++;

            // look at next; if there is no next, break
            if (qList.count() > 0) {
              follower = qList.peek();
            } else {
              break;
            }
          }
        }

        // WHILE WAITING, IS IT TIME TO END ANY NOTE?
        Serial.println("Next end times: " + String(servoEnd[0]) + ", " + String(servoEnd[1]));
        while (ticks() < leaderStart) {
        	Serial.print(".");
        	for (int i=0; i < numServos; i++) {
        		int endTime = servoEnd[i];
        		if (endTime < ticks() && endTime > 0) { // time to end note
        			// stop the appropriate servo
        			servos[i].write(offPos);
        			Serial.println("END: " + String(i) + ", " + String(servoEnd[i]) + "--" + String(ticks()));
        			servoEnd[i] = -1;
        		}
        	}
        	delay(20);
        }
        
        // PLAY THE NOTES
        Serial.println(getNameAndOctave(leader));
        Serial.println("START: " + String(leader.getStart()) + "--" + String(ticks()));
        playNotes(currentNotes);
      }
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


// HELPER FUNCTIONS //
String getNameAndOctave(Note n) {
  return String(n.getName()) + String(n.getOctave());
}

long ticks() {
  long ms = millis() - startMillis;
  return ms*ticksPerSec/1000;
}

void servoEndPush(Note n) {
	String id = getNameAndOctave(n);
	int index;
	if (id == "C4") {
		index = 0;
	} else if (id == "D4") {
		index = 1;
	} else if (id == "E4") {
		index = 2;
	} else if (id == "G4") {
		index = 3;
	}
	servoEnd[index] = n.getStart() + n.getDuration();
}

void playNotes(Note noteSet[10]) {
	// if first note played, then set start time of piece to ticks()
	if (startMillis == 0) {
		startMillis = millis();
	}
	for (int i=0; i < numServos; i++) {
		Servo s;
		String id = getNameAndOctave(noteSet[i]);
		if (id == "C4") {
			s = sC4;
		} else if (id == "D4") {
			s = sD4;
		} else if (id == "E4") {
			s = sE4;
		} else if (id == "G4") {
			s = sG4;
		}
		s.write(onPos);
		servoEndPush(noteSet[i]);
	}	
}