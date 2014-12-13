import cv2
import cv2.cv as cv
import numpy as np

from nameNote import get_note_type

'''
Line class is some sub-image that contains staff lines
It is used to represent either full lines of music, or each
individual note
'''
class Line:
	def __init__(self, img, start_row, end_row):
		self.img = img
		self.start_row = start_row
		self.end_row = end_row
		self.rows,self.cols = np.shape(img)
		self.staff_lines = []

	'''
	Given "global" indices for staff lines, translate them to "local"
	indices relative to this sub-image
	'''
	def translate_lines(self, all_staff_lines):
		for sl in all_staff_lines:
			if (sl > self.start_row) and (sl < self.end_row): #staff line in line
				self.staff_lines.append(sl-self.start_row)
		self.staff_lines.sort()

	def calc_lines_below(self):
		sum_dists = 0
		for i in range(len(self.staff_lines)-1):
			sum_dists += self.staff_lines[i+1] - self.staff_lines[i]
		avg_dist = (sum_dists)/(len(self.staff_lines)-1)
		self.staff_lines.append(self.staff_lines[len(self.staff_lines)-1] + avg_dist)
		self.staff_lines.append(self.staff_lines[len(self.staff_lines)-1] + avg_dist)
		self.staff_lines.append(self.staff_lines[len(self.staff_lines)-1] + avg_dist)
		self.staff_lines.append(self.staff_lines[len(self.staff_lines)-1] + avg_dist)
		self.staff_lines.append(self.staff_lines[len(self.staff_lines)-1] + avg_dist)


	def make_slots(self):
		note_slots = {}
		line_notes = [29,26,23,19,16,12,9,5,2]
		space_notes = [28,24,21,17,14,11,7,4,0]
		#all_notes = ['F5','E5','D5','C5','B4','A4','G4','F4','E4','D4','C4','B3','A3']
		#count = 0

		for i in range(len(self.staff_lines)-1):
			# next_line = 0
			# try:
			#   next_line = self.staff_lines[i+1]
			# except:
			#   next_line = self.staff_lines[i] + avg_dist
			y = self.staff_lines[i]
			space_between = self.staff_lines[i+1] - self.staff_lines[i]
			r = range(y-(space_between/4), y+(space_between/4)+1)
			note_slots[line_notes[i]] = r

			r2 = range(y+(space_between/4), y+(3*space_between/4))
			note_slots[space_notes[i]] = r2
		self.note_slots = note_slots

	def get_note_name(self,center):
		if center == None:
			return "null"
		else:
			note_y = center[0]
			for name in self.note_slots:
				r = self.note_slots[name]
				if note_y in r:
					return name

class MusicReader:

	'''
	A MusicReader has an image (filename passed as param) and whether
	it's two-handed music or not
	'''
	def __init__(self, im_name, twohanded):
		self.img = cv2.imread(im_name,0)
		self.rows, self.cols = np.shape(self.img)
		self.twohanded = twohanded
		self.staff_lines = []

	'''
	Main function that goes through the steps of reading and understanding the music
	1. split into lines
	2. chunk into notes, destroy all columns not containing a note
	3. go though chunked-up music and pull out specific notes as continuous units
	4. if it's twohanded, split each of these into top_row and bottom_row notes
	5. identify each note, both letter (E,G,etc) and type (quarter, half, etc)
	'''
	def read(self):
		i=0
		self.staff_lines, widths = self.read_staff_lines(self.img)
		#print "all staff lines", self.staff_lines
		lines = self.split_into_lines(self.img)
		top_notes = []
		bottom_notes = []
		for l in range(len(lines)):
			line_obj = lines[l]
			line = line_obj.img
			line_obj.translate_lines(self.staff_lines) # tells line object which lines belong to it

			#print "full line", line_obj.start_row, line_obj.end_row, line_obj.staff_lines

			unbarred_line = self.destroy_non_note_cols(line)
			cv2.imwrite('single_line.png',line)
			#cv2.waitKey(0)
			notes = self.find_notes(unbarred_line)
			if notes != None:
				for n in range(len(notes)):
					if self.twohanded:
						#hand_notes = self.split_into_lines(note)
						if len(line_obj.staff_lines) == 10:
							note = notes[n]
							cv2.imwrite('both_notes'+str(n)+'.png',note)
							top_line_bottom_row = line_obj.staff_lines[5]

							top_obj, bottom_obj = self.split_at_row(note, top_line_bottom_row-10)

							top_durations, top_names = self.prep_note(top_obj,line_obj.staff_lines,"top",i)
							bottom_durations, bottom_names = self.prep_note(bottom_obj,line_obj.staff_lines,"bottom",i)
							print top_durations
							print top_names
							print bottom_durations
							print bottom_names
							assert len(top_durations) == len(top_names)
							assert len(bottom_durations) == len(bottom_names)
							if ((n > 2 and l == 2) or (n > 1 and l > 2)):
								for j in range(len(top_durations)):
									top_notes.append((top_durations[j], top_names[j]))
								for k in range(len(bottom_durations)):
									bottom_notes.append((bottom_durations[k], bottom_names[k]))
							i+=1
		print top_notes
		print bottom_notes
		# tt=0
		# bt=0
		# for t in top_notes:
		# 	d = t[0]
		# 	if d=="whole note" or d=="whole rest":
		# 		tt+=1
		# 	elif d=="half note":
		# 		tt+=.5
		# 	elif d=="quarter note":
		# 		tt+=.25
		# 	elif d=="eighth note":
		# 		tt+=.125
		# for b in bottom_notes:
		# 	d = b[0]
		# 	if d=="whole note" or d=="whole rest":
		# 		bt+=1
		# 	elif d=="half note":
		# 		bt+=.5
		# 	elif d=="quarter note":
		# 		bt+=.25
		# 	elif d=="eighth note":
		# 		bt+=.125
		# print tt, bt
		self.translate_for_arduino(top_notes, bottom_notes)

	def translate_for_arduino(self,top,bottom):
		strings = []
		time = 0
		for note in top:
			arr = ['0']*36
			length = note[0]
			index = note[1]
			arr[index] = '1'
			string = ''.join(arr)
			string += ',' + str(time)
			arr2 = ['0']*36
			string2 = ''.join(arr2)
			string2 += ',' + str(time+length/2)
			strings.append(string)
			strings.append(string2)
			time += length
		print strings


	'''
	Given a Line object for a note, prepares it to be read, saves it, etc
	'''
	def prep_note(self, input_obj, staff_lines, desc,i):
		img = input_obj.img
		rows,cols = np.shape(img)
		input_obj.translate_lines(staff_lines)
		input_obj.calc_lines_below()
		input_obj.make_slots()
		print desc, input_obj.start_row, input_obj.end_row, input_obj.staff_lines
		
		durations, centers = get_note_type(input_obj.img)
		#cimg = cv2.cvtColor(input_obj.img, cv.CV_GRAY2RGB)
		names = []
		for i in range(len(centers)):
			print centers[i]
			if centers[i] != None:
				cv2.circle(input_obj.img,(centers[i][1],centers[i][0]),2,(0,0,255),3)
			name = input_obj.get_note_name(centers[i])
			print durations[i], name
			names.append(name)
		if len(names) == 0:
			names.append("null")
		if len(durations) == 0:
			durations.append("null")
		cv2.imwrite("../images/notes2/"+desc+str(i)+".png",img)
		cv2.imshow(desc, img)
		cv2.waitKey(0)
		return durations, names

	'''
	Function that takes an input_img with multiple rows and splits it by each row
	Returns an array containing each row as a separate element
	'''
	def split_into_lines(self, input_img):
		rows,cols = np.shape(input_img)
		prev_row = 0
		lines = []

		current_row = 0

		row = 0
		while row<rows-1:
			row+=1
			brightnesses = self.get_row_brightnesses(row, input_img)
			current_row = row
			if not self.gray_in_brightnesses(brightnesses):
				while current_row < rows and not self.gray_in_brightnesses(self.get_row_brightnesses(current_row, input_img)):
					current_row+=1

				if current_row - row > 30:
					line = np.zeros([current_row - prev_row, cols])
					for r in range(current_row - prev_row):
						for col in range(cols):
							if input_img[r+prev_row][col] < 100:
								line[r][col] = 0
							else:
								line[r][col] = 255
					line_obj = Line(line, prev_row, current_row)
					lines.append(line_obj)
					prev_row = current_row
			row = current_row
		return lines

	'''
	Given an input image and a row, splits the image into two at that row
	'''
	def split_at_row(self, input_img, row):
		rows,cols = np.shape(input_img)

		line1 = np.zeros([row, cols])
		line2 = np.zeros([rows-row, cols])
		for r1 in range(row):
			for c1 in range(cols):
				if input_img[r1][c1] < 100:
					line1[r1][c1] = 0
				else:
					line1[r1][c1] = 255
		line1_obj = Line(line1, 0, row)
		for r2 in range(row,rows):
			for c2 in range(cols):
				if input_img[r2][c2] == 0:
					line2[r2-row][c2] = 0
				else:
					line2[r2-row][c2] = 255
		line2_obj = Line(line2, row, rows)

		return line1_obj, line2_obj

	'''
	Takes an input image (line) and goes through each column
	If that column contains no notes, it shades it white (erases it)
	If a column doesn't contain a note, then it's only 5 staff lines
	This determins the staff_line threshold as a percentage of black pixels
	and erases all columns with a smaller percentage than calculated
	'''
	def destroy_non_note_cols(self, input_img):
		rows,cols = np.shape(input_img)
		black_threshold = self.get_black_staff_threshold(input_img)
		unbarred_img = input_img.copy()
		for col in range(cols):
			total_black_in_col = 0
			for row in range(rows):
				if input_img[row][col]==0:
					total_black_in_col += 1
			if float(total_black_in_col)/rows < black_threshold:
				for row in range(rows):
					unbarred_img[row][col]=255
		return unbarred_img

	'''
	Uses connectivity search to take an input image and split it into
	individual notes by considering everything that's connected to be a note
	'''
	def find_notes(self, input_img):
		rows, cols = np.shape(input_img)

		boxes = []
		notes = []

		is_black = False

		start = 0
		for col in range(cols):
			brightnesses = []
			for row in range(rows):
				brightnesses.append(input_img[row][col])

			if 0 in brightnesses and is_black == False:
				start=col
				is_black=True
			if 0 not in brightnesses and is_black == True:
				if (col+1 - start-1) > 5:
					boxes.append((start-1,col+1))
				is_black = False

		for box in boxes:
			note = np.ones([rows, box[1]-box[0]])
			np.multiply(note,255)
			for c in range(box[0],box[1]):
				brightnesses = []
				for row in range(rows):
					brightnesses.append(input_img[row][c])

				loc_index = c - box[0]
				note[:,loc_index] = brightnesses

			# cv2.circle(input_img,(box[0],10),2,(0,0,255),3)
			# cv2.circle(input_img,(box[1],10),2,(0,0,255),3)

			notes.append(note)
		return notes

	def read_note(self, input_img):
		# TODO: take an input image note and identify it
		# BOTH AS quarter note/half etc, as well as E,G,F,etc
		# 
		# run staff lines on it
		# find center of black pixels, maybe using meanShift? or HoughCircles?
		pass

	'''
	Helper function to split_into_lines
	Takes an input image and a specific row in that image
	Returns a list of the pixel brightnesses of every pixel in that row
	'''
	def get_row_brightnesses(self, row, input_img):
		rows, cols = np.shape(input_img)
		brightnesses = []
		for col in range(cols):
			brightnesses.append(input_img[row][col])
		return brightnesses

	'''
	Helper function to split_into_lines
	Takes a list of brightnesses and tells you if any of the values from 0-20 are in it
	Originally we only looked for 0's, but the images are imperfect and have some gray in them
	This prevents it from looking past dark pixels that aren't perfect black
	'''
	def gray_in_brightnesses(self,brightnesses):
		grays = range(20)
		contains_gray = False
		for g in grays:
			if g in brightnesses:
				contains_gray = True
				break
		return contains_gray

	'''
	Helper function to destroy_non_note_cols
	Gets staff lines and determines their total pixelage
	Right now assuming every line has width 2
	This could be fixed
	'''
	def get_black_staff_threshold(self, input_img):
		rows,cols = np.shape(input_img)
		staff_lines, widths = self.read_staff_lines(input_img)
		if staff_lines:
			avg_width = 2 # 
			if widths:
				avg_width = sum(widths)/len(widths)
			return (len(staff_lines)*avg_width + 1)/float(rows)

			#return float(sum(widths)/rows)
			# staff_lines.sort()
			# #assert len(staff_lines)%2==0
			# sum_widths = 0

			# i=0

			# while i<len(staff_lines)-1:
			#   if staff_lines[i+1] - staff_lines[i] > 10:
			#       i+=1
			#   else:
			#       sum_widths += staff_lines[i+1] - staff_lines[i]
			#       i+=2

			# sum_widths +=1

			# return float(sum_widths)/rows
		else:
			return 0

	'''
	Helper function to destroy_non_note_cols and get_black_staff_threshold
	Takes an input image and uses HoughLines to find staff lines
	Returns a list of lines with their y-values
	Only one line per actual staff line ***
	'''
	def read_staff_lines(self, input_img):

		rows,cols = np.shape(input_img)
		nump_arr = np.zeros([rows,cols])
		for r in range(rows):
			for c in range(cols):
				if input_img[r][c] < 200:
					nump_arr[r][c] = 0
				else:
					nump_arr[r][c] = 255

		copy = np.uint8(nump_arr)
		edges = cv2.Canny(copy,150,700)
		lines = cv2.HoughLines(edges,1,np.pi/180,300)
		staff_lines = []
		widths = []
		if lines != None:   
			for rho,theta in lines[0]:
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))

				th = 6 #pixels
				too_close = False
				for y in staff_lines:
					if abs(y - y1) <= th:
						too_close = True
						widths.append(abs(y - y1))
				if not too_close:
					staff_lines.append((y1))
		staff_lines.sort()
		for i in range(len(staff_lines)-1):
			staff_lines[i] = staff_lines[i] + 1
			cv2.line(nump_arr,(0,staff_lines[i]),(cols,staff_lines[i]),(0,0,255),2)
		cv2.imwrite('staff_lines.png',nump_arr)
		#cv2.waitKey(0)
		return staff_lines, widths

if __name__ == "__main__":
	mr = MusicReader("../images/ode_to_joy.png", True)
	mr.read()