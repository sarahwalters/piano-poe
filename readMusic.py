"""This will become the code to take in a MIDI file and output motor signals
<<<<<<< HEAD
Right now it's mainly just to test pushing"""
import cv2
test = cv2.imread('treblestaffsheetblank.jpg', 0)
test1 = cv2.Canny(test,100,200)
print type(test1)


cv2.imshow('test', test1)
cv2.waitKey(0)

