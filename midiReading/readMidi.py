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
	lastTick = 0

	count = 0
	for noteObj in noteObjects:
		if count < 15:
			print noteObj
			count = count + 1

		if isinstance(noteObj, midi.events.NoteOnEvent):
			# http://jazzparser.granroth-wilding.co.uk/api/midi.NoteEvent-class.html#velocity
			#noteName = toNoteName(noteObj.data[0])
			velocity = noteObj.data[1] # How hard the note is played or how quickly it's released (0-127)
			if (velocity > 0): # For some reason some midi files include extra notes w/ velocity 0
				# add current note
				time = time + noteObj.tick
				notes.append([time, noteObj.data[0], 15])

	return notes


# obsolete
def toNoteName(pitch):
	''' Convert from pitch number to note name
		INPUTS: pitch (integer, 0-127 -> C4, middle C, is 60)
		OUTPUTS: note name (eg C5, D#4, B7)
	'''
	names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
	name = names[pitch%12]
	octave = int(pitch/12)-1
	return name + str(octave)


def readNew(midiFile, startKey, stopKey):
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
	keyboardArray = [0]*(stopKey-startKey+1)
	noteOns = []
	noteOffs = []
	lastOnTick = -1
	lastOffTick = -1

	# make on and off states for every on/off change
	for i, noteObj in enumerate(noteObjects):
		updated = False

		# update state of keyboardArray?
		isNoteOn = isinstance(noteObj, midi.events.NoteOnEvent) and noteObj.data[1] > 0 #  check velocity - some midi files have extra notes?
		isNoteOff = isinstance(noteObj, midi.events.NoteOffEvent)

		if isNoteOn or isNoteOff:
			# if note is valid, update state...
			keyboardIndex = noteObj.data[0]-startKey
			if keyboardIndex in range(0, len(keyboardArray)):
				# ..add to keyboardArray
				if isNoteOn:
					keyboardArray[keyboardIndex] = 1
					time = time + noteObj.tick
					leftoverTick = 0
				else:
					keyboardArray[keyboardIndex] = 0
					durationProportion = 0.5
					time = time + noteObj.tick

				# ...make new state array
				newState = ''.join(map(str, keyboardArray))
				timeInt = int(time)
				

				if isNoteOn:
					if timeInt == lastOnTick:
						noteOns[-1] = (newState, timeInt)
					else:
						noteOns.append((newState, timeInt))
						lastOnTick = timeInt
				else:
					if timeInt == lastOffTick:
						noteOffs[-1] = (newState, timeInt)
					else:
						noteOffs.append((newState, timeInt))
						lastOffTick = timeInt

	# collect states into single array containing ons and offs
	iOn = 0
	iOff = 0
	nextOnTick = -1
	nextOffTick = -1
	states = []
	while iOn < len(noteOns) or iOff < len(noteOffs):
		#print str(iOn) + ' -> ' + str(len(noteOns))
		#print str(iOff) + ' -> ' + str(len(noteOffs))

		if iOn < len(noteOns):
			nextOnTick = noteOns[iOn][1]
		else:
			nextOnTick = None

		if iOff < len(noteOffs):
			nextOffTick = noteOffs[iOff][1]
		else:
			nextOffTick = None

		if (nextOnTick < nextOffTick and nextOnTick > -1) or (nextOffTick == None):
			# next on comes first
			states.append(noteOns[iOn][0] + ',' + str(noteOns[iOn][1]))
			iOn = iOn + 1

		elif (nextOffTick < nextOnTick and nextOffTick > -1) or (nextOnTick == None):
			# next off comes first
			states.append(noteOffs[iOff][0] + ',' + str(noteOffs[iOff][1]))
			iOff = iOff + 1

		elif nextOffTick == nextOnTick and nextOffTick > -1:
			# scheduled for the same time - space out for servos
			if iOn-1 > 0:
				diff = noteOns[iOn][1] - noteOns[iOn-1][1]
			else:
				diff = noteOns[iOn+1][1] - noteOns[iOn][1]
			states.append(noteOffs[iOff][0] + ',' + str(noteOffs[iOff][1]-diff/2))
			states.append(noteOns[iOn][0] + ',' + str(noteOns[iOn][1]))
			iOn = iOn + 1
			iOff = iOff + 1

	return states