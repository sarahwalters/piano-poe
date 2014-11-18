import sys
sys.path.insert(0, '../midiReading')

import glob
import serial
import readMidi
from math import ceil

# @ -> Python sends to Arduino to start Arduino writing mode
# % -> Arduino sends to Python to start Python writing mode
# * -> delimiter in note strings
# ! -> end of a set of note strings
# & -> done with all note strings

# http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package

''' TUNABLE PARAMETERS '''
setSize = 8 # how many notes Python sends upon a request from Arduino for more


''' FUNCTIONS '''
# finds which USB port the Arduino is connected to
def findPort():
    ports = glob.glob("/dev/tty[A-Za-z]*")
    for port in ports:
        if 'ACM' in port:
            return port

# handles opening/closing serial ports & calling method
# which gets midi contents and sends them to Arduino 
def serialWrapper():
	# open all serial connections
	ser = serial.Serial(findPort(), 9600, timeout=1)

	testMidiOutput = [[0, 64, 72],
					  [0, 60, 70],
					  [25, 62, 72],
					  [50, 60, 71],
					  [75, 62, 79],
					  [100, 64, 85],
					  [100, 60, 79], # making this last for longer later
					  [125, 64, 78],
					  [150, 64, 79]]

	midiOutput = readMidi.read('../midiReading/midis/mary.mid')
	#midiOutput = testMidiOutput
	numSets = ceil(len(midiOutput)/float(setSize))
	setNum = 0

	# python -> arduino
	ser.write('@')

	# arduino -> python
	while (setNum <= numSets+1):
		# PYTHON READING BLOCK
		# print 'Trying to read'
		#print setNum
		#print numSets + 1
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
						#if (str(noteArray[0])=="100" and str(noteArray[1])=="60"):
						#	ser.write(',70,')
						#else:
						ser.write(',15,')
						ser.write(str(noteArray[1]))
						ser.write('*')
				ser.write('!')
				# END OF PYTHON WRITING BLOCK
			else:
				ser.write('&')
			ser.write('@')
			setNum = setNum + 1

	ser.close()