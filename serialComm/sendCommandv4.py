import sys
sys.path.insert(0, '../midiReading')

import serial
import glob
import readMidi

def findPort():
    ports = glob.glob("/dev/tty[A-Za-z]*")
    for port in ports:
        if 'ACM' in port:
            return port

def serialWrapper():
	# open all serial connections
	ser = serial.Serial(findPort(), 9600, timeout=1)

	'''testMidiOutput = ['000000000100000000000,0',
					  '000000000000000000000,480',
					  '000000000100000000000,960',
					  '000000000000000000000,1440',
					  '000000000010000000000,1920',
					  '000000000000000000000,2400',
					  '000000000000100000000,2880',
					  '000000000000000000000,3360',
					  '000000000000100000000,3840',
					  '000000000000000000000,4320',
					  '000000000010000000000,4800',
					  '000000000000000000000,5280',
					  '000000000100000000000,5760',
					  '000000000000000000000,6240',
					  '000000010000000000000,6720',
					  '000000000000000000000,7200']'''

	testMidiOutput = ['000000000001,0',
					  '000000000000,480',
					  '000000000001,960',
					  '000000000000,1440',
					  '000000000001,1920',
					  '000000000000,2400',
					  '000000000001,2880',
					  '000000000000,3360',]

	midiOutput = readMidi.readNew('../midiReading/midis/odeToJoy2.mid', 60, 71)
	#midiOutput = testMidiOutput
	# pre-sending setup
	ser.write('@') # give Arduino serial control
	sentIndex = 0 # runs to numNotes + 1
	numNotes = len(midiOutput)
	batchSize = 10

	# sending
	while sentIndex <= numNotes + 1:
		# PYTHON READING BLOCK
		# print 'Trying to read'
		inc = ser.read(100000)
		# inc: everything Arduino printed to serial during the last loop()
		# 	   should always end with '%'
		# END OF PYTHON READING BLOCK

		if '%' in inc: # give Python serial control
			print 'arduino write msg: ' 
			print inc
			print '---'

			# PYTHON WRITING BLOCK - send a batch of notes
			count = 0
			while count < batchSize and sentIndex < numNotes:
				ser.write(midiOutput[sentIndex])
				ser.write('*')
				sentIndex = sentIndex + 1
				count = count + 1
			# END OF PYTHON WRITING BLOCK
			if sentIndex < numNotes:
				ser.write('!')
			else:
				ser.write('&')
				sentIndex = sentIndex + 1 # trigger end of while loop

			# give Arduino serial control
			ser.write('@')

	ser.close()