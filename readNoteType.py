import cv2
import numpy as np

def findScale(image):
    """
    finds the scale of an image based on the staff; also removes the staff

    inputs:
        image - unprocesesed image with scale 

    returns:
        unbarred - image without bars or cleff in it
        bar position - a list of pixel values for the rows containing bars
        scale - the scale based on the average distance between bars
    """

    pass

def isolateNotes(image):
    """
    Isolates each note in an image into a seperate numpy array and stores them in a list

    inputs:
        image - the image (with bars and cleff removed)

    returns:
        notes - a list of numpy arrays representing isolated notes 
    """
    pass

def templateMatch(scale, note):
    """
        Takes in a scale and a music note, matches it to a template to determine the type of the note
    """
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    threshold = 27000000 # need a way to determine this not by hand through guess and check
    loc = np.where(res <= threshold)

def meanShift(points, hypothesis, threshold):
    """
    returns: 
        The center of a group of inputted points

    inputs:
        points - list of [x,y] objects
        hypothesis - guess of where the center would be (center of image is good start)
        threshold - maximum acceptable difference in center guess between iterations
    """
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
        for pt in points:
            x_val = np.exp(-c * (pt[0] - last_guess[0])**2)
            x_weights.append(x_val)
            weighted_x.append(x_val*kp[0])
            y_val = np.exp(-c * (pt[1] - last_guess[1])**2)
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

def processNotes(notes):
    """
    Process notes to extract note name, note type, and start time (may also put into queues based on note name)

    inputs:
        notes - list of numpy arrays representing isolated notes in order of appearence

    returns:
        list of [note name, note type, start time]
    """
    pass