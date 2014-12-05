import cv2
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

def isolate_center(image):
    """
    Takes in a binary numpy array and pulls out the coordinates of the black pixels
    Uses these pixels to estimate the center of the note using mean_shift

    inputs: 
        image -> file path for the binary image
    returns:
        center -> the center of mass of the note
    """
    #finds the points which are not black
    points = []
    for row in range(len(image)):
      for col in range(len(image[row])):
          if image[row,col] == 0:
            points.append((row,col))

    #finds the center of the image
    center_row = len(image)/2
    center_col = len(image[0])/2
    center = (center_row, center_col)
    center = mean_shift(center, points, 0.25)
    return center