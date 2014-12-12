piano-poe
=========

###Sending midi file contents to Arduino:
* Upload playNotev4.ino to Arduino (see below); take note of the serial port to which the Arduino is connected
* Ensure that you have python-midi installed (see below) OR set midiOutput to testMidiOutput instead of reading from midi in sendCommandv3.py -> sendMidiOutput
* Start a Python/ipython process (you may need sudo permissions to access the serial port) then run sendCommandv3.py -> serialWrapper()

###Installing python-midi:
* git clone https://github.com/vishnubob/python-midi/ into your local piano-poe repo
* sudo apt-get install swig
* sudo apt-get install libasound2-dev
* cd to python-midi
* sudo python setup.py install

###Compiling playNotev2.ino:

#### QueueList library:
* Download Queuelist Library from http://playground.arduino.cc/Code/QueueList
* Save files in arduino/libraries/QueueList  - that is, /usr/share/arduino/libraries
* After restarting your Arduino environment, be sure you can #include <QueueList.h>

#### Note library:
* Pull the Note folder from this git repo
* 
* Save files in the Note folder from this repo into arduino/libraries/Note (that is, /usr/share/arduino/libraries)
* After restarting your Arduino environment, be sure you can #include <Note.h>

###Installing OpenCV:
* Follow the instructions on this link: https://help.ubuntu.com/community/OpenCV

###Installing Wand (for pdfPng):
* sudo apt-get install python-wand
