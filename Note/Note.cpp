#include "Arduino.h"
#include "Note.h"

Note::Note() { } // need this to initialize array of undefined notes

Note::Note(int start, int duration, char name, int octave)
{
  _start = start;
  _duration = duration;
  _name = name;
  _octave = octave;
}

int Note::getStart()
{
	return _start;
}

int Note::getDuration()
{
	return _duration;
}

char Note::getName()
{
	return _name;
}

int Note::getOctave()
{
	return _octave;
}

/*
void Note::setNext(int next)
{
	_next = next;
}

int Note::getNext()
{
	return _next;
}
*/