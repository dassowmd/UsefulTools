# import numpy as np
# import cv2
#
# cap = cv2.VideoCapture(0)
#
# while (True):
#     ret, frame = cap.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

# # Color Filtering
# import cv2
# import numpy as np
#
# cap = cv2.VideoCapture(0)
#
# while (1):
#     _, frame = cap.read()
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#
#     lower_red = np.array([50, 0, 0])
#     upper_red = np.array([255, 255, 255])
#
#     mask = cv2.inRange(hsv, lower_red, upper_red)
#     res = cv2.bitwise_and(frame, frame, mask=mask)
#
#     cv2.imshow('frame', frame)
#     cv2.imshow('mask', mask)
#     cv2.imshow('res', res)
#
#     k = cv2.waitKey(5) & 0xFF
#     if k == 27:
#         break
#
# cv2.destroyAllWindows()
# cap.release()

# Detect moving things
import numpy as np
import cv2
import imutils
import time

cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2()

while (1):
    ret, frame = cap.read()

    fgmask = fgbg.apply(frame)
    # cv2.imshow('fgmask', fgmask)

    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(fgmask,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 1)

    # cv2.imshow('Erosion',erosion)
    # cv2.imshow('Dilation',dilation)

    res = cv2.bitwise_and(frame,frame, mask= dilation)
    cv2.imshow('res',res)

    # find contours in the mask and initialize the current
    # (x, y) center of the moving object
    cnts = cv2.findContours(dilation.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
            # cv2.circle(frame, center, 10, (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            rect_mask = np.zeros(frame.shape[:2], np.uint8)
            rect_mask[y - (radius * 1.5):y + (radius * 1.5), x - (radius * 1.5):x + (radius * 1.5)] = 255
            res = cv2.bitwise_and(frame, frame, mask=rect_mask)
            # time.sleep(.5)
    cv2.imshow('frame', frame)
    cv2.imshow('res', res)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()