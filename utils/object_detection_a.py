import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
 
img_rgb = cv2.imread('.test_images\StemFlex and StemScale\mTeSR plus Stemflex D2-1.jpg')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

template = cv2.imread('.test_images\\template_test.png', 0)

w, h = template.shape[::-1]
 
res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)

threshold = 0.3
loc = np.where(res >= threshold)
boxes = [(pt[0],pt[1],pt[0]+w,pt[1]+h) for pt in zip(*loc[::-1])]
boxes = np.array(boxes)

indices = cv2.dnn.NMSBoxes(boxes, res.flatten(), threshold, 0.3)  # Adjust NMS threshold

for i in indices:
    x, y, w, h = boxes[i]
    cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 0, 255), 2)

# for pt in zip(*loc[::-1]):
#     print(pt[0])
#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)
#     os.system("pause")
 
# cv2.imwrite('res.png',img_rgb)

# Show the final image with the bounding boxes 
# and areas of the objects overlaid on top 
cv2.imshow('test', res) 
cv2.imshow('image', img_rgb) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 