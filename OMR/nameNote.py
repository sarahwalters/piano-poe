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
        if stem_length >= 45:
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
    
    # cv2.imshow('test', image)
    # cv2.waitKey(0)
    if len(divisions) > 1:
        images = []
        start = 0
        for x in divisions:
            end = x + 5
            segment = image[0:len(image[0]), start:x]
            images.append(segment)
            start = x
            #TODO: add in protection for dealing with stems on the left side of the note (probably if black switch to next line as divider)
            # cv2.imshow('test', segment)
            # cv2.waitKey(0)

    else:
        num_stems = 0
        images = len[image]


    print len(images)
    return image



def isolate_center(image):
    """
    Takes in a binary numpy array and pulls out the coordinates of the black pixels
    Uses these pixels to estimate the center of the note using mean_shift

    inputs: 
        image -> file path for the binary image
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
    center = mean_shift((100, 46), points, 0.25)
    return center

if __name__ == '__main__':
    im = cv2.imread('../images/lonely_quarters.png', 0)
    image = find_stems(im)
    # show_im = cv2.imread('../images/note3.png')
    center = isolate_center(im)

    # cv2.circle(image, (center[1], center[0]), 4, (255, 255, 255))
    # cv2.imshow('test', image)
    # cv2.waitKey(0)
