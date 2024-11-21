import cv2 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
  
# Load the image 
img = cv2.imread('.test_images\mTeSR 3D\mTeSR plus-mTeSR3D_D1-1.jpg') 
  
# Convert the image to grayscale 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

ret,thresh2 = cv2.threshold(gray,100,255,cv2.THRESH_BINARY_INV)

kernel = np.ones((5, 5), np.uint8) 
img_erosion = cv2.erode(gray, kernel, iterations=1) 
ret,img_erosion2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
img_dilation = cv2.dilate(gray, kernel, iterations=1) 
ret,img_dilation2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)

kernel = np.ones((1, 1), np.uint8) 
thresh2_erosion = cv2.erode(thresh2, kernel, iterations=1) 

test = thresh2_erosion.copy()

# # Show the final image with the bounding boxes 
# # and areas of the objects overlaid on top 
# cv2.imshow('image', test) 
# cv2.waitKey(0) 
# cv2.destroyAllWindows() 
  
# # Show the final image with the bounding boxes 
# # and areas of the objects overlaid on top 
# cv2.imshow('image', thresh2) 
# cv2.waitKey(0) 
# cv2.destroyAllWindows() 
  
# Apply a threshold to the image to 
# separate the objects from the background 
ret, thresh = cv2.threshold( 
    gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) 
  
# Find the contours of the objects in the image 
contours, hierarchy = cv2.findContours( 
    test, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    # thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

df_vals = [[],[],[],[]]
# Loop through the contours and calculate the area of each object 
for cnt in contours: 
    area = cv2.contourArea(cnt) 
  
    # Draw a bounding box around each 
    # object and display the area on the image 
    x, y, w, h = cv2.boundingRect(cnt) 

    df_vals[0].append(x)
    df_vals[1].append(y)
    df_vals[2].append(w)
    df_vals[3].append(h)

    if w>25:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
        cv2.putText(img, str(area), (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) 

df = pd.DataFrame({
    "x":df_vals[0],
    "y":df_vals[1],
    "w":df_vals[2],
    "h":df_vals[3]
})

standard_deviation = df["w"].std()

print(standard_deviation)

plt.hist(df["w"],bins=500)
plt.xlabel("Values")
plt.ylabel("Frequency")
plt.title("Histogram of Data")
plt.show()
  
# Show the final image with the bounding boxes 
# and areas of the objects overlaid on top 
cv2.imshow('image', img) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 