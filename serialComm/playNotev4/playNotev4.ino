#include <Wire.h>
#include <Note.h>
#include <QueueList.h>
#include <avr/pgmspace.h>
#include <Servo.h>


// INITIALIZATIONS //
// ... timing
int minQueueSize = 16;
//int ticksPerSec = 25; // midi time -> second conversion MARY
int ticksPerSec = 40;

// ... for FSM
int state = 0;
String incomingString = "";
QueueList<Note> qList;

// ... for timing
long startMillis = 0;

// ... for pitch/note name/key index conversion
String noteNames[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
int lowestNote = 60; // starting at C4 for now

// ... servo stuff
Servo sC4, sCsh4, sD4, sDsh4, sE4, sF4, sFsh4, sG4, sGsh4, sA4, sAsh4, sB4;
Servo servos[12] = {sC4, sCsh4, sD4, sDsh4, sE4, sF4, sFsh4, sG4, sGsh4, sA4, sAsh4, sB4}; // in pin order, starting at 2
int servoEnd[12];
// FOR REAL THING
//int onPos[8] = {160, 0, 152, 0, 143, 0, 0, 37};
//int offPos[8] = {140, 0, 137, 0, 131, 0, 0, 49};

// FOR FOAM PROTOTYPE
//int onPos[8] = {7, 0, 171, 0, 180, 0, 0, 178};
//int offPos[8] = {18, 0, 163, 0, 168, 0, 0, 168};

// FOR TESTING
//int offPos[12] = {28, 0, 16, 0, 22, 11, 180, 169, 180, 163, 180, 156};
int offPos[12] = {28, 0, 16, 0, 22, 11, 180, 169, 180, 163, 180, 156};
//int offPos[12] = {90, 90, 90, 90, 90, 90, 180, 180, 180, 180, 180, 180};
int onPos[12] = {15, 0, 5, 0, 10, 0, 170, 180, 180, 174, 180, 169};
int numServos = 12;


// MAIN FUNCTIONS //
void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps

  // attach all servos to pins and set to default positions
  for (int i=0; i<numServos; i++) {
  	int pin = i+2;
  	servos[i].attach(pin);
  	servos[i].write(offPos[i]);
    servoEnd[i] = -1;
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
        
        // ...start time, duration, pitch
        int startTime = noteStr.substring(0,commaIndex1).toInt();
        int duration = noteStr.substring (commaIndex1+1, commaIndex2).toInt();
        int pitch = noteStr.substring (commaIndex2+1).toInt();
        
        // ...make an object
        Note current = Note(startTime, duration, pitch);
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
        int stopCounter = 1;
        Note currentNotes[10] = {leader}; // revisit?

        // add subsequent "follower" notes which start at the same time to the array
        int leaderStart = leader.getStart();
        if (qList.count() > 0) {
          Note follower = qList.peek();

          // while notes start at the same time...
          while (follower.getStart() == leaderStart) {
          	qList.pop(); // this is follower - already have; need to get out of queue
            currentNotes[stopCounter] = follower; // add to set to play
            stopCounter++;

            // look at next; if there is no next, break
            if (qList.count() > 0) {
              follower = qList.peek();
            } else {
              break;
            }
          }
        }

        // WHILE WAITING, IS IT TIME TO END ANY NOTE?
        while (ticks() < leaderStart) {
        	Serial.print(".");
        	for (int i=0; i < numServos; i++) {
        		int endTime = servoEnd[i];
        		if (endTime < ticks() && endTime > 0) { // time to end note
        			// stop the appropriate servo
        			servos[i].write(offPos[i]);
        			Serial.println("END: " + String(servoEnd[i]) + "--" + String(ticks()));
        			servoEnd[i] = -1;
        		}
        	}
        	delay(5);
        }
        
        // PLAY THE NOTES
        Serial.println(getNameAndOctave(leader));
        Serial.println("START: " + String(leader.getStart()) + "--" + String(ticks()));
        playNotes(currentNotes, stopCounter);
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
  int pitch = n.getPitch();
  String name = noteNames[pitch%12];
  int octave = int(pitch/12)-1;
  return name + String(octave);
}

int getKeyIndex(Note n) {
  return n.getPitch() - lowestNote; // C4 is 0th note -> pitch of 60
}

long ticks() {
  long ms = millis() - startMillis;
  return ms*ticksPerSec/1000;
}

void playNotes(Note noteSet[10], int stopIndex) {
	// if first note played, then set start time of piece to ticks()
	if (startMillis == 0) {
		startMillis = millis();
	}

  // go through note set
	for (int i=0; i < stopIndex; i++) {
    // get current note
    int keyIndex = getKeyIndex(noteSet[i]);

    // if it's in range, move servo and store the end time
    if (keyIndex >= 0 && keyIndex < numServos) {
      servos[keyIndex].write(onPos[keyIndex]); // move the servo
      servoEnd[keyIndex] = noteSet[i].getStart() + noteSet[i].getDuration(); // store the end time
	  }
  }	
}