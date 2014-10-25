import serial
import readMidi
import time

def serialWrapper():
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	formatMidiOutput(ser)
	ser.close()

def formatMidiOutput(ser):
	midiOutput = readMidi.read('midis/mary.mid')
	for item in midiOutput:
		out = str(item[0]) + ',' + '25,' + item[1]
		print out
		ser.write(out)
		ser.write('*')
	ser.write('!')