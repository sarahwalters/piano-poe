'''
This code works for images/quarter_note_run.png, using images/note2.png as a the note template
and images/treble.png as the treble template

Currently only works for a single bar, because it depends on y positions
'''

import cv2
import cv2.cv
import numpy as np
from matplotlib import pyplot as plt

'''
This method takes an image and a template image of a treble
clef and returns the top left corner of the treble clef within
the image

Note: this is imperfect because it won't scale the template, i.e.
it depends on image size.  Will error if template image size
is bigger in any dimensions that img size
'''
def find_treble_clef(img, treble):
	method = eval('cv2.TM_SQDIFF')
	res = cv2.matchTemplate(img,treble,method)

	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	return min_loc

'''
This function takes an image and finds the staff lines
as a list of y values only
'''
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

'''
This takes a list of y-values where lines live, and creates ranges of discrete buckets
for notes to fall into, and assigns ranges of buckets to their note letter

Returns a dictionary where each key is a letter and each value is a list (range), would
have liked it the other way around by python doesn't allow lists to be keys

Note F1 and E1, any other ways we could distinguish these?
'''
def find_slots(lines):
	assert(len(lines)==5)
	lines.sort() # starting at the top
	note_slots = {}
	line_notes = ['F5','D5','B4','G4','E4']
	space_notes = ['E5','C5','A4','F4']
	count = 0

	# find average space between each line 
	# this is assuming our line finding went well and they're pretty evenly spaced
	# could be improved by finding each space between lines individually
	space_between = int(np.mean([lines[1]-lines[0], lines[2]-lines[1], lines[3]-lines[2],lines[4]-lines[3]]))
	
	for y in lines:
		# within 1/4 of "space between" from a line means it's "on" the line
		r = range(y-(space_between/4), y+(space_between/4)) 
		note_slots[line_notes[count]] = r
		if count < 4:
			# in the 1/4 - 3/4 range of space between lines means it's a space note
			r2 = range(y+(space_between/4), y+(3*space_between/4))
			note_slots[space_notes[count]] = r2
		count+=1
	return note_slots

'''
Given a note's y position and a dictionary of slots,
finds the name of the note
'''
def name_note(slots, y):
	for name in slots:
		r = slots[name]
		if y in r:
			return name

'''
This function is the meat of the code
Takes 3 strings:
	im_name = name of image of music
	note_name = name of note template image
	treble_name = name of treble template image

Uses openCV template matching to find notes
Then identifies each note by name
Returns a list of note names in order
	We can fix this later, but it's currently assuming all notes are 
	one second apart (quarter notes) and therefore not saving their
	x position.

Note: If image doesn't contain a treble clef send in the treble name as empty string
'''
def read_quarter_notes(im_name, note_name, treble_name):
	img = cv2.imread(im_name,0)
	template = cv2.imread(note_name,0)
	w, h = template.shape[::-1]
	cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

	method = eval('cv2.TM_SQDIFF')

	iw, hw = img.shape[::-1]

	treble = None
	w2 = 0
	h2 = 0
	top_left = (0,0)

	if treble_name != "":
		treble = cv2.imread('images/treble_clef.png',0)
		w2, h2 = treble.shape[::-1]
		top_left = find_treble_clef(img,treble)

	# Apply template matching
	res = cv2.matchTemplate(img,template,method)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

	threshold = 27000000 # need a way to determine this not by hand through guess and check
	loc = np.where(res <= threshold)

	centers = []

	for pt in zip(*loc[::-1]):
		# each pt is an {x,y) of the location of a rectangle in the image that matches the template
	    center = (pt[0] + w/2, pt[1] + h/2)
	    too_close = False
	    th = 10 #pixels

	    # this part is somewhat flawed in that, if there's a group
	    # of points clustered together, it just takes the first one it
	    # sees and drops the rest instead of averaging them
	    for c in centers:
	    	if abs(c[0] - center[0]) <= th:
	    		too_close = True
	    	elif abs(c[1] - center[1]) <= th:
	    		too_close = True
	    if not too_close:
	        centers.append(center)

	notes = []

	# filter out points that matched the note template but are actually part of the treble clef
	for i in centers:
		is_treble = False
		if i[0] >= top_left[0] and i[0] <= top_left[0] + w2 and i[1] >= top_left[1] and i[1] <= top_left[1] + h2:
			is_treble = True
		if not is_treble:
			notes.append(i)

	y_lines = read_staff_lines(img)
	slots = find_slots(y_lines)

	# draw the note centers and lines.  For debugging's sake
	for j in notes:
		cv2.circle(cimg,(j[0],j[1]),2,(0,0,255),3)
	for y in y_lines:
		cv2.line(cimg,(0,y),(iw,y),(0,0,255),2)

	# sort notes by x order 
	notes.sort(key=lambda tup: tup[0])

	# store note names
	note_names_in_order = []
	for note in notes:
		note_names_in_order.append(name_note(slots, note[1]))

	# show test image
	cv2.imshow('test',cimg)
	cv2.waitKey(0)

	return note_names_in_order

'''
Run code
'''
if __name__ == '__main__':
	im_name = 'images/quarter_note_run.png'
	note_name = 'images/note2.png'
	treble_name = 'images/treble_clef.png'
	
	print read_quarter_notes(im_name, note_name, treble_name)