import cv2
import cv2.cv
import numpy as np
from matplotlib import pyplot as plt
from get_lines import get_lines

np.set_printoptions(threshold=np.nan)

FULL_NOTE = 1
PARTIAL_NOTE = 2
STEM = 3
UNKNOWN = 4

bypass_clef = 120

def read_staff_lines(img):
	edges = cv2.Canny(img,150,700)

	lines = cv2.HoughLines(edges,1,np.pi/180,200)
	staff_lines = []
	for rho,theta in lines[0]:
	    a = np.cos(theta)
	    b = np.sin(theta)
	    x0 = a*rho
	    y0 = b*rho
	    x1 = int(x0 + 1000*(-b))
	    y1 = int(y0 + 1000*(a))
	    x2 = int(x0 - 1000*(-b))
	    y2 = int(y0 - 1000*(a))

	    th = 10 #pixels
	    too_close = False

	    # only appends lines if they're a reasonable distance
	    # from other lines
	    # would be better if used averaging between close lines instead of
	    # just taking the first one we see and tossing the other
	    for y in staff_lines:
	      	if abs(y - y1) <= th:
	    		too_close = True
	    if not too_close:
	    	staff_lines.append((y1))

	return staff_lines

def find_notes(img):
	rows, cols = np.shape(img)

	#lines = read_staff_lines(img)
	#lines.sort()

	#space_between = int(np.mean([lines[1]-lines[0], lines[2]-lines[1], lines[3]-lines[2],lines[4]-lines[3]]))
	space_between = 28

	boxes = []

	# key is col #
	# value is tuple (streak_start_row, streak_end_row)

	is_black = False

	start = 0
	for col in range(cols):
		brightnesses = []
		for row in range(rows):
			brightnesses.append(img[row][col])

		if 0 in brightnesses and is_black == False:
			start=col
			is_black=True
		if 0 not in brightnesses and is_black == True:
			if (col+1 - start-1) > 5:
				boxes.append((start-1,col+1))
			is_black = False

	print boxes


	for box in boxes:
		note = np.ones([rows, box[1]-box[0]])
		np.multiply(note,255)
		for c in range(box[0],box[1]):
			brightnesses = []
			for row in range(rows):
				brightnesses.append(img[row][c])

			loc_index = c - box[0]
			note[:,loc_index] = brightnesses
		#print note

		cv2.circle(img,(box[0],10),2,(0,0,255),3)
		cv2.circle(img,(box[1],10),2,(0,0,255),3)

		cv2.imshow('test',note)
		cv2.waitKey(0)

	cv2.imshow('test',img)
	cv2.waitKey(0)

'''
Run code
'''
if __name__ == '__main__':
	im_name = 'images/jinglebells.png'
	img = cv2.imread(im_name,0)
	lines = get_lines(img)
	for line in lines:
		find_notes(line)
	#note_name = 'images/note2.png'
	#treble_name = 'images/treble_clef.png'
	
	#print read_quarter_notes(im_name, note_name, treble_name)