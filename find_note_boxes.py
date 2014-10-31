import cv2
import cv2.cv
import numpy as np
from matplotlib import pyplot as plt

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

def find_notes(im_name):
	img = cv2.imread(im_name,0)
	rows, cols = np.shape(img)
	print rows, cols

	lines = read_staff_lines(img)
	lines.sort()
	print lines

	space_between = int(np.mean([lines[1]-lines[0], lines[2]-lines[1], lines[3]-lines[2],lines[4]-lines[3]]))
	#space_between = 28

	descriptors = {}

	### HOW TO ACCOUNT FOR HALF NOTES???

	note_assembly = {}
	# key is col #
	# value is tuple (streak_start_row, streak_end_row)

	for col in range(bypass_clef,cols):
		brightnesses = []
		for row in range(rows):
			brightnesses.append(img[row,col])
			
		#threshold = 100 # brightness to be considered "dark" vs "white"
		#print brightnesses

		longest_streak = 0
		current_streak = 0
		streak_start_row = 0
		streak_end_row= 0
		current_start = 0
		current_end = 0
		prev = 0
		in_streak = False

		for i in range(len(brightnesses)):
			b = brightnesses[i]
			if b == prev and b == 0:
				if not in_streak:
					current_start = i
				current_streak += 1
				in_streak = True
			else:
				if in_streak:
					current_end = i
				in_streak = False
			if current_streak >= longest_streak:
				longest_streak = current_streak
				streak_end_row = current_end
				streak_start_row = current_start
				if not in_streak:
					current_streak = 0
			prev = b

		note_assembly[col] = (streak_start_row, streak_end_row)

		line_threshold = 7 # error in line being length of staff space

		if abs(longest_streak - space_between) <= line_threshold:
			descriptors[col] = FULL_NOTE
		elif longest_streak < space_between and longest_streak > 6: #8 is arbitrary
			descriptors[col] = PARTIAL_NOTE
		elif longest_streak >= space_between*2:
			descriptors[col] = STEM
		else:
			descriptors[col] = UNKNOWN

	# sort notes in x order
	sorted(descriptors, key=lambda key: descriptors[key])

	boxes = [] #tuples

	for col in range(bypass_clef,cols):
		current_desc = 0
		box_range = []
		if descriptors[col] == FULL_NOTE:
			box_range.append(col)
			i = 1
			while current_desc != UNKNOWN and (col-i>=bypass_clef):
				current_desc = descriptors[col-i]
				if current_desc != UNKNOWN:
					box_range.append(col-i)
				i+=1

			current_desc = 0
			j = 1
			while current_desc != UNKNOWN and (col+j<cols):
				current_desc = descriptors[col+j]
				if current_desc != UNKNOWN:
					box_range.append(col+j)
				j+=1
		box_tolerance = 2 #pixels to extend past last partial_note reading on either side
		if len(box_range) > 0:
			max_col = max(box_range) + box_tolerance
			min_col = min(box_range) - box_tolerance
			if min_col < bypass_clef:
				min_col += box_tolerance
			if max_col > cols:
				max_col -= box_tolerance

			boxes.append((min_col, max_col))
			cv2.circle(img,(min_col,10),2,(0,0,255),3)
			cv2.circle(img,(max_col,10),2,(0,0,255),3)

	no_dup_boxes = []
	for box in boxes:
		if box not in no_dup_boxes:
			no_dup_boxes.append(box)
	print no_dup_boxes

	for box in no_dup_boxes:
		note = np.ones([rows, box[1]-box[0]])
		np.multiply(note,255)
		for c in range(box[0],box[1]):
			start_row = note_assembly[c][0]
			end_row = note_assembly[c][1]
			loc_index = c - box[0]
			#print start_row, end_row
			for i in range(start_row,end_row):
			#START ROWS NOT CHANGING WHEN ASSIGNED LOL IT DONT WORK
				#print i,loc_index
				note[i,loc_index] = 0
		#print note

		cv2.imshow('test',note)
		cv2.waitKey(0)

	cv2.imshow('test',img)
	cv2.waitKey(0)

'''
Run code
'''
if __name__ == '__main__':
	im_name = 'images/eighth_notes.jpg'
	find_notes(im_name)
	#note_name = 'images/note2.png'
	#treble_name = 'images/treble_clef.png'
	
	#print read_quarter_notes(im_name, note_name, treble_name)