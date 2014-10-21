import midi

def read(midiFile):
	''' convert midi file to array of notes 
		INPUTS: midiFile (string, e.g. '____.mid')
		OUTPUTS: notes (array of note arrays, each with format [time, note name, velocity])
		e.g.
		[[0, 'E5', 72],
		 [0, 'G4', 70],
		 [25, 'D5', 72],
		 [50, 'C5', 71],
		 [75, 'D5', 79],
		 [100, 'E5', 85],
		 [100, 'G4', 79],
		 [125, 'E5', 78],
		 [150, 'E5', 74]]
	'''
	pattern = list(midi.read_midifile(midiFile))
	metadata = list(pattern[0])
	noteObjects = list(pattern[1])

	# PARSE METADATA
	tempoEvents = []
	timeSignatureEvents = []
	keySignatureEvents = []

	# http://jazzparser.granroth-wilding.co.uk/api/midi.TimeSignatureEvent-class.html
	# http://jazzparser.granroth-wilding.co.uk/api/midi.KeySignatureEvent-class.html
	# http://jazzparser.granroth-wilding.co.uk/api/midi.SetTempoEvent-class.html
	for item in metadata:
		if isinstance(item, midi.events.SetTempoEvent):
			tempoEvents.append(item)
		elif isinstance(item, midi.events.TimeSignatureEvent):
			timeSignatureEvents.append(item)
		elif isinstance(item, midi.events.KeySignatureEvent):
			keySignatureEvents.append(item)

	# PARSE NOTES
	time = 0
	notes = []
	for noteObj in noteObjects:
		if isinstance(noteObj, midi.events.NoteOnEvent):
			# http://jazzparser.granroth-wilding.co.uk/api/midi.NoteEvent-class.html#velocity
			noteName = toNoteName(noteObj.data[0])
			velocity = noteObj.data[1] # How hard the note is played or how quickly it's released (0-127)
			if (velocity > 0): # For some reason some midi files include extra notes w/ velocity 0
				time = time + noteObj.tick
				notes.append([time, noteName, velocity])

	return notes


def toNoteName(pitch):
	''' Convert from pitch number to note name
		INPUTS: pitch (integer, 0-127 -> C4, middle C, is 60)
		OUTPUTS: note name (eg C5, D#4, B7)
	'''
	names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
	name = names[pitch%12]
	octave = int(pitch/12)-1
	return name + str(octave)


def collect(notes):
	''' Collect notes played simultaneously - for readability.
		INPUTS: notes (produced by readMidi.read. Array of note arrays, each with format [time, note name, velocity])
		OUTPUTS: timedNotes (array of same-time arrays of note arrays)
			-> each same-time array collects all of the note arrays which happen at the same time
		e.g.
		[[[0, 'E5', 72], [0, 'G4', 70]],
 		 [[25, 'D5', 72]],
 		 [[50, 'C5', 71]],
		 [[75, 'D5', 79]],
 		 [[100, 'E5', 85], [100, 'G4', 79]],
 		 [[125, 'E5', 78]],
 		 [[150, 'E5', 74]]]
	'''
	threshold = 5
	timedNotes = []

	i = 0
	# outer loop through all notes
	while (i < len(notes)):
		compare = notes[i]
		noteSet = []

		# collect notes at same time
		while (i < len(notes)):
			note = notes[i]
			if (note[0] - compare[0] <= threshold):
				noteSet.append(note)
				i = i+1
			else:
				break
		timedNotes.append(noteSet)

	return timedNotes