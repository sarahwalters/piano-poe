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



t_im = cv2.imread('images/note4.png')
q_im = cv2.imread('images/singleOctaveTemplate.png')

method = 'SIFT'
#finding keypoints and descriptors in the training image
detector = cv2.FeatureDetector_create(method)
descriptor = cv2.DescriptorExtractor_create(method)     
t_k = detector.detect(t_im)
t_k, t_d = descriptor.compute(t_im, t_k)

#find all keypoints and descriptors in the query image
q_k = detector.detect(q_im)
q_k, q_d = descriptor.compute(q_im, q_k)


#saving keypoint coordinates in a list because keypoint objects can't be pickled
kps =[]
for point in t_k:
    kps.append((point.pt[0], point.pt[1]))
    cv2.circle(t_im, (int(point.pt[0]), int(point.pt[1])), 2, (0, 0, 255), 3)

matcher = cv2.BFMatcher() #(normType = cv2.NORM_HAMMING)

#match list of object keypoints to query image, not other way around
matches = matcher.knnMatch(t_d, q_d, k = 2)

#Nearest neighbor test to reduce false matches
good_matches = []
for m,n in matches:
    # if m.distance < 0.75*n.distance:
    # Get coordinate of the match
    m_x = int(q_k[m.trainIdx].pt[0])
    m_y = int(q_k[m.trainIdx].pt[1])
    good_matches.append((m_x, m_y))
    cv2.circle(q_im, (int(m_x), int(m_y)), 2, (0, 0, 255), 3)


h = mean_shift([300, 100], good_matches, 0.001)
cv2.circle(q_im, h, 2, (255, 0, 0), 3)
cv2.imshow('show', q_im)
cv2.waitKey(0)




