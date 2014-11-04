//http://arduino.cc/en/Hacking/LibraryTutorial

#ifndef Note_h
#define Note_h

#include "Arduino.h"

class Note
{
  public:
    Note();
    Note(int start, int duration, char name, int octave);
    int getStart();
    int getDuration();
    char getName();
    int getOctave();
    /*int getNext();
    void setNext(int next);*/
  private:
    int _start;
    int _duration;
    char _name;
    int _octave;
    int _next;
};

#endif