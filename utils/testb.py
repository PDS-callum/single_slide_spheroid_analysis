import cv2
import numpy as np

originalPicRead = cv2.imread('.test_images\StemFlex and StemScale\mTeSR plus Stemflex D2-1.jpg')
img_bgr = cv2.resize(originalPicRead, (0,0), fx=0.33, fy=0.33)
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

templateR = cv2.imread('.test_images\\template_test.png',0)

w,h = templateR.shape[::-1]

for magn in range(1,11):
    mult = magn*0.35
    w,h = int(mult*w),int(mult*h)
    template = cv2.resize(templateR, (0,0), fx=mult, fy = mult)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.4
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_bgr, pt, (pt[0]+w, pt[1]+h), (0,255,255), 2)

img_bgr = cv2.resize(img_bgr, (0,0), fx=3, fy=3)

cv2.imshow('test', originalPicRead)
cv2.imshow('Detected', img_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()