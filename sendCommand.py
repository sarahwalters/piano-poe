import serial
import readMidi


''' handles opening/closing serial ports & calling method
	which gets midi contents and sends them to Arduino 
'''
def serialWrapper():
	# open all serial connections
	ser0 = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	# ser1 = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
	sers = [ser0]

	# define notes each serial connection handles
	noteSet0 = ['E3','G3','C4','D4','E4','G4'] # ser0 handles all notes in test midi
	# noteSet1 = []
	noteSets = [noteSet0]

	# map note nameAndOctave to serial connection
	serMap = {}
	numArduinos = len(sers)
	for i in range(numArduinos):
		noteSet = noteSets[i]
		ser = sers[i]
		for note in noteSet:
			serMap[note] = ser

	# write midi output to serial
	sendMidiOutput(serMap)

	# tell the Arduino to stop reading
	for ser in sers:
		ser.write('!') # end character - done sending midi output


	print '---'
	done = False;
	while (not done):
		s = ser.readline()
		if '@' in s:
			print s
			done = True;

	# close all serial connections
	for ser in sers:
		ser.close()


''' gets midi contents and sends them to Arduino according to
	serMap (key: note name, value: open serial connection)
'''
def sendMidiOutput(serMap):
	testMidiOutput = [[0, 'E4', 72],
					  [0, 'G3', 70],
					  [25, 'D4', 72],
					  [50, 'C4', 71],
					  [75, 'D4', 79],
					  [100, 'E4', 85],
					  [100, 'G3', 79],
					  [125, 'E4', 78],
					  [150, 'E4', 74]]

	# if python-midi isn't installed, use testMidiOutput as midiOutput
	#midiOutput = testMidiOutput
	midiOutput = readMidi.read('midis/mary.mid')
	midiOutput = midiOutput
	
	for item in midiOutput:
		start = item[0]
		nameAndOctave = item[1]
		out = str(start) + ',25,'+str(nameAndOctave) + '*'
		print out

		serMap[nameAndOctave].write(out)