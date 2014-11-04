import cv2
import numpy as np


def eliminateBars(img):
    """
    Removes bars from an image

    inputs:
        img - np array of the image to remove bars from

    returns:
        unbarred - image without the bars
    """

    # barred_img = cv2.imread(img, 0)
    unbarred = np.zeros(np.shape(barred_img))
    print np.shape(unbarred)
    for row in range(5, len(barred_img)-5):
        for column in range(len(barred_img[row])):
            if barred_img[row + 2, column] or barred_img[row-2, column] == 255:
                unbarred[row,column] = 255
            else:
                unbarred[row, column] = barred_img[row, column]

    # cv2.imwrite('./images/unbarred_quarter_note_run.png', unbarred)
    # cv2.imshow('show', unbarred)
    # cv2.waitKey(0)
    return unbarred

def findScale(image):
    """
    finds the scale of an image based on the staff; also removes the staff

    inputs:
        image - unprocesesed image file path 

    returns:
        unbarred - image without bars or cleff in it
        staff_lines - a list of pixel values for the rows containing bars
        scale - the scale based on the average distance between bars
    """

    img = cv2.imread(image)
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
    average_space = sum(staff_lines)/len(staff_lines)
    scale = average_space * scale_constant #TODO: find appropriate scale constant or just return average_space
    unbarred = eliminateBars(img)
    return [staff_lines, scale, unbarred]

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
        matches a music note to a template to determine the type of the note

        inputs: 
            scale - the scale of the image we are using   #TODO: use this to adjust our image template
            note - a numpy array representing a single muscal note 
    """
    img = cv2.imread('./images/matchTemplate.png')
    newx,newy = img.shape[1]/4,img.shape[0]/4 #new size (w,h)
    scaled_img = cv2.resize(img,(newx,newy))

    method = eval('cv2.TM_SQDIFF')
    res = cv2.matchTemplate(img,note,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    threshold = 27000000 # need a way to determine this not by hand through guess and check
    
    loc = np.where(res <= threshold) #Area where a match to the template has been found

    return loc
    

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