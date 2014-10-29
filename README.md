piano-poe
=========

Sending midi file contents to Arduino:
* Upload playNotev2.ino to Arduino (see below); take note of the serial port to which the Arduino is connected
* In sendCommand.py -> serialWrapper(), replace the first argument in the instantiation of ser0 with the name of the serial port to which the Arduino is connected
* Ensure that you have python-midi installed (see below) OR set midiOutput to testMidiOutput instead of reading from midi in sendCommand.py -> sendMidiOutput
* Start a Python/ipython process (you may need sudo permissions to access the serial port) then run sendCommand.py -> serialWrapper()

Installing python-midi:
* git clone https://github.com/vishnubob/python-midi/ into your local piano-poe repo
* sudo apt-get install swig
* sudo apt-get install libasound2-dev
* cd to python-midi, then sudo python setup.py install
* sudo python setup.py install

Compiling playNotev2.ino:

-> Adafruit motor shield library:
* Download Adafruit Library from https://learn.adafruit.com/adafruit-motor-shield-v2-for-arduino/install-software
* Save files in arduino/libraries/Adafruit_Motorshield
* After restarting your Arduino environment, be sure you can #include <Adafruit_Motorshield.h> (in the IDE, check Sketch > Import Library)

-> QueueList library:
* Download Queuelist Library from http://playground.arduino.cc/Code/QueueList
* Save files in arduino/libraries/QueueList
* After restarting your Arduino environment, be sure you can #include <QueueList.h>

-> Note library:
* Pull the Note folder from this git repo
* Save files in the Note folder from this repo into arduino/libraries/Note
* After restarting your Arduino environment, be sure you can #include <Note.h>

Installing OpenCV:
* Follow the instructions on this link: https://help.ubuntu.com/community/OpenCV

