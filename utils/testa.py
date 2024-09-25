import cv2 
import numpy as np 
  
# Read the main image 
img_rgb = cv2.imread('.test_images\StemFlex and StemScale\mTeSR plus Stemflex D2-1.jpg')
  
# Convert it to grayscale 
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
  
# Read the template 
template = cv2.imread(".test_images\\template_test.png", 0) 
  
# Store width and height of template in w and h 
w, h = template.shape[::-1] 
  
# Resize the image according to scale and 
# keeping track of ratio of resizing 
resize = imutils.resize(img_gray, width=int(shape[0]), height=int(img_gray.shape[1]*scale))
  
# If resize image is smaller than that of template 
# break the loop 
# Detect edges in the resized, grayscale image and apply template 
# Matching to find the template in image edged 
# If we have found a new maximum correlation value, update 
# the found variable if 
# found = null/maxVal > found][0] 
if resized.shape[0] < h or resized.shape[1] < w: 
          break
found=(maxVal, maxLoc, r) 
  
# Unpack the found variables and compute(x,y) coordinates 
# of the bounding box 
(__, maxLoc, r)=found 
(startX, startY)=(int(maxLoc[0]*r), int maxLoc[1]*r) 
(endX, endY)=(int((maxLoc[0]+tw)*r), int(maxLoc[1]+tH)*r) 
  
# Draw a bounding box around the detected result and display the image 
cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2) 
cv2.imshow("Image", image) 
cv2.waitKey(0)