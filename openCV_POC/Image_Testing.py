# import cv2
# import numpy as np

# img = cv2.imread(r'Images\Fishing_Pole.jpg',cv2.IMREAD_COLOR)
#
# cv2.imshow('image',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# px = img[55,55]
# img[55,55] = [255,255,255]
# px = img[55,55]
# print(px)
#
# px = img[100:150,100:150]
# print(px)
#
# img[100:150,100:150] = [255,255,255]
# img = cv2.imread(r'Images1\Fishing_Pole.jpg',cv2.IMREAD_COLOR)
# print(img.shape)
# print(img.size)
# print(img.dtype)
# temp_img = img[100:150,100:150]
# img[0:50,0:50] = temp_img
#
# cv2.imshow('image',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# import cv2
# import numpy as np
# img = cv2.imread(r'Images\Bookmark.jpg',cv2.IMREAD_COLOR)
#
# grayscaled = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
# cv2.imshow('original',img)
# cv2.imshow('Adaptive threshold',th)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # Template Matching
# import cv2
# import numpy as np
#
# img_rgb = cv2.imread('Images/Brian.jpg')
# img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
#
# template = cv2.imread('Images/Fishing_Pole.jpg',0)
# w, h = template.shape[::-1]
# res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
# threshold = 0.95
# loc = np.where(res >= threshold)
# for pt in zip(*loc[::-1]):
#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
#
# cv2.imshow('Detected',img_rgb)
# cv2.imwrite('Images/output.jpg', img_rgb)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import numpy as np
import cv2

im = cv2.imread('Images/Fishing_Pole.jpg')
hsv_img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
COLOR_MIN = np.array([100, 100, 100],np.uint8)
COLOR_MAX = np.array([255, 255, 255],np.uint8)
frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
imgray = frame_threshed
ret,thresh = cv2.threshold(frame_threshed,127,255,0)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# Find the index of the largest contour
areas = [cv2.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt=contours[max_index]

x,y,w,h = cv2.boundingRect(cnt)
cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
cv2.imshow("Show",im)
cv2.waitKey()
cv2.destroyAllWindows()