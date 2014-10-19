import midi
import math

def read(midiFile):
	pattern = list(midi.read_midifile(midiFile))
	metadata = list(pattern[0])
	noteObjects = list(pattern[1])

	# http://jazzparser.granroth-wilding.co.uk/api/midi.TimeSignatureEvent-class.html
	timeSignature = metadata[0].data
	numerator = timeSignature[0]
	denominator = 2**timeSignature[1]

	# http://jazzparser.granroth-wilding.co.uk/api/midi.KeySignatureEvent-class.html
	keySignature = metadata[1].data

	time = 0
	notes = []
	for noteObj in noteObjects:
		if isinstance(noteObj, midi.events.NoteOnEvent):
			# http://jazzparser.granroth-wilding.co.uk/api/midi.NoteEvent-class.html#velocity
			noteName = toNoteName(noteObj.data[0])
			velocity = noteObj.data[1] # How hard the note is played or how quickly it's released (0-127)
			if (velocity > 0):
				time = time + noteObj.tick
				notes.append([time, noteName, velocity])

	return [metadata, notes]

def toNoteName(pitch):
# Pitch ranges from 0-127). C5 is pitch 60.
	names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
	name = names[pitch%12]
	octave = int(pitch/12)
	return name + str(octave)