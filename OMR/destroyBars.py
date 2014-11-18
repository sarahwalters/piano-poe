import cv2
import numpy as np

def eliminateBars(img):
    """Takes in an image with notes and bars
       Returns an image with only the notes"""

    barred_img = cv2.imread(img, 0)
    unbarred = np.zeros(np.shape(barred_img))
    print np.shape(unbarred)
    for row in range(5, len(barred_img)-5):
        for column in range(len(barred_img[row])):
            if barred_img[row + 2, column] or barred_img[row-2, column] == 255:
                unbarred[row,column] = 255
            else:
                unbarred[row, column] = barred_img[row, column]

    cv2.imwrite('./images/unbarred_quarter_note_run.png', unbarred)
    cv2.imshow('show', unbarred)
    cv2.waitKey(0)

if __name__ == '__main__':
    eliminateBars('./images/quarter_note_run.png')