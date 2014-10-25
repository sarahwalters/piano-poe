import serial
import readMidi

def serialWrapper():
	ser1 = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	ser2 = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
	formatMidiOutput(ser)
	ser.close()

def formatMidiOutput(ser):

	test = 		[[0, 'E5', 72],
		 [0, 'G4', 70],
		 [25, 'D5', 72],
		 [50, 'C5', 71],
		 [75, 'D5', 79],
		 [100, 'E5', 85],
		 [100, 'G4', 79],
		 [125, 'E5', 78],
		 [150, 'E5', 74]]
	midiOutput = readMidi.read('midis/mary.mid')
	#midiOutput = test
	for item in midiOutput:
		if (item[1] == 'C4' or 'D4' or 'E4' or 'F4')
			out1 = str(item[0]) + ',' + '25,' + item[1]
			print out1
			ser1.write(out1)
			ser1.write('*')
		else
			out2 = str(item[0]) + ',' + '25,' + item[1]
			print out2
			ser2.write(out)
			ser2.write('*')