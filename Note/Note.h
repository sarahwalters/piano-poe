//http://arduino.cc/en/Hacking/LibraryTutorial

#ifndef Note_h
#define Note_h

#include "Arduino.h"

class Note
{
  public:
    Note();
    Note(int start, int duration, int pitch);
    int getStart();
    int getDuration();
    int getPitch();
  private:
    int _start;
    int _duration;
    int _pitch;
};

#endif