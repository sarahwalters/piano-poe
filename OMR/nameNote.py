import cv2
import cv2.cv as cv
import numpy as np 

def mean_shift(hypothesis, keypoints, threshold):
	"""
	Inputs:
		hypothesis -> Previous center point as a starting hypothesis
		keypoints -> List of keypoint (x,y) coordinates
		Threshold -> maximum acceptable difference in center between iterations (eg 10 pixels, 5 pixels)
		current -> np array representing the image (for visualization)
		show -> determines whether visualization is shown
		frame -> name of the window if the image is displayed

	Returns:
		New center of keypoints
		Radius
		If show is true -> displays the center, keypoints and a circle around the object
	"""

	n=0
	if len(keypoints) > 1:

		#assigns a value to the weighting constant -> based on 
		#experimental results on cropped cookie_00274
		c = 0.0001

		#arbitrarily set diff high to go through loop at least once
		diff = 1000

		while(diff > threshold):
			#sets up lists of weights and weights*position
			x_weights = []
			y_weights = []
			weighted_x = []
			weighted_y = []
			#Creats a list of weighted points, where points near the 
			#hypothesis have a larger weight
			last_guess = hypothesis
			for kp in keypoints:
				x_val = np.exp(-c * (kp[0] - last_guess[0])**2)
				x_weights.append(x_val)
				weighted_x.append(x_val*kp[0])
				y_val = np.exp(-c * (kp[1] - last_guess[1])**2)
				y_weights.append(y_val)
				weighted_y.append(y_val*kp[1])

			#finds 'center of mass' of the points to determine new center
			x = int(sum(weighted_x)/sum(x_weights))
			y = int(sum(weighted_y)/sum(y_weights))

			#update hypothesis
			hypothesis = (x,y)

			#difference between the current and last guess
			diff = np.sqrt((last_guess[0] - x)**2 + (last_guess[1] - y)**2)
		return hypothesis

def find_stems(image):
	"""
	Takes in an image and isolates the number and positions of the stems, then 
	breaks up the image as necessary and removes the stems 

	inputs:
		image -> a binary numpy array
	returns:
		stem_number -> the number of stems in the image
		new_images -> a list of images with stems removed
	"""

	#creating a list x values
	stems = []
	for x in range(len(image[0])):
		column = image[0:len(image), x]
		stem_length = len(column) - sum(column)/255
		# print stem_length
		if stem_length >= 25:
			stems.append(x)

	#removing stems and counting their number
	if len(stems) != 0:
		num_stems = 1
		current_stem = stems[0]
		divisions = [stems[0]]
		for row in stems:
			#color stems white to remove
			image[0:len(image), row] = 255
			if row != stems[0]:
				#count the number of stems
				if abs(current_stem - row) > 5:
					current_stem = row
					num_stems = num_stems + 1
					#add the stem to a list to divide images
					divisions.append(current_stem)
	else:
		num_stems = 0
		divisions = []
	
	# cv2.imshow('test', image)
	# cv2.waitKey(0)

	segment = None

	if len(divisions) > 0:
		images = []
		splitting = [0] + divisions + [len(image[0])]
		for index in range(len(splitting)-1):
			start = splitting[index]+5
			end = splitting[index+1]-2
			segment = image[0:len(image), start:end]
			if 0 in segment:
				if len(divisions) > 1:
					segment[0:len(segment)/3.5, 0:len(segment[0])] = 255
					segment[2.5*len(segment)/3.5: len(segment), 0:len(segment[0])] = 255
				images.append(segment)

			# cv2.imshow('test', segment)
			# cv2.waitKey(0)

	#else:
	#   segment = image[0:len(image), start:end]


	if len(divisions)==0:
		images = [image]


	#print len(images)
	return images, num_stems



def isolate_center(image):
	"""
	Takes in a binary numpy array and pulls out the coordinates of the black pixels
	Uses these pixels to estimate the center of the note using mean_shift

	inputs: 
		image -> numpy array for the binary image
	returns:
		center -> the center of mass of the note
	"""
	#finds the points which are black
	points = []
	for row in range(len(image)):
	  for col in range(len(image[row])):
		  if image[row,col] == 0:
			points.append((row,col))

	#finds the center of the image
	center_row = len(image)/2 
	center_col = len(image[0])/2
	center = (center_row, center_col)
	center = mean_shift((100, 46), points, 0.005)
	return center

def check_non_note(image):
	no_note = False
	try:
		loc = find_template(image, cv2.imread('../images/treble.png', 0))
		if np.shape(loc)[1] != 0:
			no_note = True
	except:
		print "no treble"
	try:
		loc = find_template(image, cv2.imread('../images/bass.png', 0))
		if np.shape(loc)[1] != 0:
			no_note = True
	except:
		print "no bass"
	try:
		loc = find_template(image, cv2.imread('../images/brace1.png', 0))
		print np.shape(loc)
		if np.shape(loc)[1] != 0:
			no_note = True
	except:
		print "no brace1"
	try:
		loc = find_template(image, cv2.imread('../images/brace2.png', 0))
		print np.shape(loc)
		if np.shape(loc)[1] != 0:
			no_note = True
	except:
		print "no brace2"
	try:
		loc = find_template(image, cv2.imread('../images/44.png', 0))
		if np.shape(loc)[1] != 0:
			no_note = True
	except:
		print "no 44"
	print "no note:", no_note
	return no_note
'''
'cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
			'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED'
'''
def find_template(img, template):
	method = eval('cv2.TM_SQDIFF_NORMED')
	res = cv2.matchTemplate(img,template,method)

	#min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	threshold = 1 # need a way to determine this not by hand through guess and check
	#print res
	loc = np.where(res == 0) #Area where a match to the template has been found
	return loc

def get_note_type(image):
	"""
		Takes in a note or set of quarter notes and outputs a name and a duration

		inputs:
			image -> numpy array of a binary image
		returns:
			name -> list of note names
			duration -> list of note durations
	"""
	images, num_stems = find_stems(image)
	raw_note = []
	duration = []
	centers = []
	for index in range(len(images)):
		center = isolate_center(images[index])
		if center == None:
			duration.append(0)
		else:
			centers.append(center)
			if num_stems == 0:
				if images[index][center] == 0:
					duration.append(0)
				else:    
					duration.append(4000)
			elif num_stems > 1:
				duration.append(500)
			elif images[index][center] == 0:
				duration.append(1000)
			else:
				duration.append(2000)
	if check_non_note(image) == True:
		duration = []
		centers = []
	return duration, centers



if __name__ == '__main__':
	im = cv2.imread('../images/notes/top0.png', 0)
	# image = find_stems(im)
	# show_im = cv2.imread('../images/note3.png')
	# center = isolate_center(im)
	duration, center = get_note_type(im)
	print("duration ", duration)
	print("center ", center)
	# cv2.circle(image, (center[1], center[0]), 4, (255, 255, 255))
	# cv2.imshow('test', image)
	# cv2.waitKey(0)

