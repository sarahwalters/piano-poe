import cv2
import cv2.cv
import numpy as np
from matplotlib import pyplot as plt

def get_lines(img):
	rows, cols = np.shape(img)
	print rows,cols
	prev_row = 0
	lines = []

	current_row = 0

	row = 0
	while row<rows-1:
		row+=1
		brightnesses = get_row_brightnesses(img,row,cols)
		current_row = row
		if 0 not in brightnesses:
			while current_row < rows and 0 not in get_row_brightnesses(img,current_row,cols):
				current_row+=1
				#print current_row

			if current_row - row > 30:
				line = np.zeros([current_row - prev_row, cols])
				for r in range(current_row - prev_row):
					for col in range(cols):
						line[r][col] = img[r+prev_row][col]
				lines.append(line)
				prev_row = current_row
		row = current_row
	# for line in lines:
	# 	cv2.imshow('test',line)
	# 	cv2.waitKey(0)
	#print lines
	return lines

def get_row_brightnesses(img,row,cols):
	brightnesses = []
	for col in range(cols):
		#print row,col
		brightnesses.append(img[row][col])
	return brightnesses

if __name__ == '__main__':
	im_name = 'images/jinglebells.png'

	img = cv2.imread(im_name,0)
	get_lines(img)