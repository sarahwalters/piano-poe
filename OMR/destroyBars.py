import cv2
import numpy as np

## TODO: code to figure out the right black threshold 


def eliminateBars(barred_img):
    """Takes in an image with notes and bars
       Returns an image with only the notes"""

    unbarred = np.zeros(np.shape(barred_img))
    print np.shape(unbarred)
    for row in range(5, len(barred_img)-5):
        for column in range(len(barred_img[row])):
            if barred_img[row + 4, column] or barred_img[row-4, column] == 255:
                unbarred[row,column] = 255
            else:
                unbarred[row, column] = barred_img[row, column]

    cv2.imwrite('./images/unbarred_jinglebells.png', unbarred)
    cv2.imshow('show', unbarred)
    cv2.waitKey(0)

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
        # from other linesho
        # would be better if used averaging between close lines instead of
        # just taking the first one we see and tossing the other

        # for y in staff_lines:
        #     if abs(y - y1) <= th:
        #         too_close = True
        # if not too_close:
        print y1,y2
        staff_lines.append((y1))

    return staff_lines

def destroy_non_note_cols(img):
    (rows,cols) = np.shape(img)
    print rows,cols
    for col in range(cols):
        total_black_in_col = 0
        for row in range(rows):
            # print row,col
            if img[row][col]==0:
                total_black_in_col += 1
        black_threshold = 30
        if total_black_in_col < black_threshold:
            for row in range(rows):
                img[row][col]=255
    return img


if __name__ == '__main__':
    img = cv2.imread('./images/quarter_note_run.png', 0)
    (rows,cols) = np.shape(img)


    # staff_lines = read_staff_lines(img)
    # i=0
    # print staff_lines

    # staff_lines.sort()
    # while i < len(staff_lines)-1:
    #     if staff_lines[i+1] - staff_lines[i] < 5:
    #         for row in range(staff_lines[i],staff_lines[i+1]+1):
    #             for col in range(cols):
    #                 img[row][col] = 255
    #         i+=2

    #     else:
    #         for row in range(staff_lines[i],staff_lines[i]+4):
    #             for col in range(cols):
    #                 img[row][col] = 255
    #         i+=1
    new_img = destroy_non_note_cols(img)

    cv2.imshow('test',new_img)
    cv2.waitKey(0)
    #cv2.imwrite('./images/unbarred_jinglebells2.png',img)
