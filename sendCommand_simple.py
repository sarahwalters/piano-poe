import serial
import readMidi
from math import ceil

# http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package

''' handles opening/closing serial ports & calling method
	which gets midi contents and sends them to Arduino 
'''
def serialWrapper():
	# open all serial connections
	ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)

	# python -> arduino
	ser.write('@')

	testMidiOutput = [[0, 'E4', 72],
					  [0, 'G3', 70],
					  [25, 'D4', 72],
					  [50, 'C4', 71],
					  [75, 'D4', 79],
					  [100, 'E4', 85],
					  [100, 'G3', 79],
					  [125, 'E4', 78],
					  [150, 'E4', 74]]

	midiOutput = readMidi.read('midis/mary.mid')
	setSize = 5
	numSets = ceil(len(midiOutput)/float(setSize))
	setNum = 0

	print numSets
	# arduino -> python
	while (setNum <= numSets):
		# PYTHON READING BLOCK
		# print 'Trying to read'
		inc = ser.read(1000)
			# inc: everything Arduino printed to serial during the last loop()
			# 	   should always end with '%'
		# END OF PYTHON READING BLOCK

		if '%' in inc: 
			if setNum > 0:
				print 'arduino write msg: ' 
				print inc 
				print '---'
			if setNum < numSets:
				# PYTHON WRITING BLOCK
				for i in range(setSize):
					index = setNum*setSize + i
					if index < len(midiOutput):
						noteArray = midiOutput[setNum*setSize + i]
						print noteArray
						ser.write(str(noteArray[0]))
						ser.write(',25,')
						ser.write(noteArray[1])
						ser.write('*')
				ser.write('!')
				# END OF PYTHON WRITING BLOCK
			ser.write('@')
			setNum = setNum + 1

	ser.close()