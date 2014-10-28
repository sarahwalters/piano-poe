piano-poe
=========

Installing python-midi:
* git clone https://github.com/vishnubob/python-midi/ into your local piano-poe repo
* sudo apt-get install swig
* sudo apt-get install libasound2-dev
* cd to python-midi, then sudo python setup.py install
* sudo python setup.py install

Running playNotev2.ino:

-> Adafruit motor shield library:
* download Adafruit Library from https://learn.adafruit.com/adafruit-motor-shield-v2-for-arduino/install-software
* save files in arduino/libraries/Adafruit_Motorshield

-> Note library:
* Pull the Note folder from this git repo
* Add a Note directory to arduino/libraries
* Copy all of the files in the Note folder from this repo into arduino/libraries/Note
* Restart your Arduino environment
* Ensure that Note shows up in the Sketch > Import Library menu

Installing OpenCV:
* Follow the instructions on this link: https://help.ubuntu.com/community/OpenCV

