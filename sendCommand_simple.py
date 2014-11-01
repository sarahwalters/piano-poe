import serial
import time

# http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package

''' handles opening/closing serial ports & calling method
	which gets midi contents and sends them to Arduino 
'''
def serialWrapper():
	# open all serial connections
	ser = serial.Serial('/dev/ttyACM2', 9600, timeout=1)

	# python -> arduino
	ser.write('@')

	count = 1

	testMidiOutput = [[0, 'E4', 72],
					  [0, 'G3', 70],
					  [25, 'D4', 72],
					  [50, 'C4', 71],
					  [75, 'D4', 79],
					  [100, 'E4', 85],
					  [100, 'G3', 79],
					  [125, 'E4', 78],
					  [150, 'E4', 74]]

	# arduino -> python
	while (count <= 4):
		inc = ser.read(100)
		print inc
		if '%' in inc:
			ser.flushInput()
			print '--'
			# START OF WRITING MODE
			ser.write('eg')
			ser.write('f')
			ser.write('d')

			# END OF WRITING MODE
			ser.write('@')
			count = count + 1

	ser.close()