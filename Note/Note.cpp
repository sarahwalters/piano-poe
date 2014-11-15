#include "Arduino.h"
#include "Note.h"

Note::Note() { } // need this to initialize array of undefined notes

Note::Note(int start, int duration, int pitch)
{
  _start = start;
  _duration = duration;
  _pitch = pitch;
}

int Note::getStart()
{
	return _start;
}

int Note::getDuration()
{
	return _duration;
}

int Note::getPitch()
{
	return _pitch;
}