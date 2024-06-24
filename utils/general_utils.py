import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import plotly.express as px
import base64

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def read_image(path):
    return cv2.imread(path)

def gray(
        image
):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def blur(
        image,
        intensity,
        type="median"
):
    if type == "median":
        return cv2.medianBlur(image, intensity)
    
def find_circles(
        image,
        method,
        dp,
        minDist,
        param1,
        param2,
        minRadius,
        maxRadius
):
    circles = cv2.HoughCircles(
        image=image, 
        method=method, 
        dp=dp, 
        minDist=minDist,
        param1=param1, 
        param2=param2, 
        minRadius=minRadius, 
        maxRadius=maxRadius
    )
    
    # Convert image to grayscale (optional, depending on input format)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert grayscale image to black and white (binary)
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

    circles = np.uint16(np.around(circles))
    data = []
    for i in circles[0, :]:
        # Extract center coordinates and radius
        x, y, r = i[0], i[1], i[2]

        # Create a mask for the circle
        mask = np.zeros_like(image, dtype="uint8")
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1)

        # Get pixel values within the circle mask
        colour_vals = binary_image[mask == 255]

        # Add data to list
        data.append({
            "coordinate": (x, y),
            "radius": r,
            "colour_values": colour_vals.tolist()
        })
        try:
            test = mask + test
        except:
            test = mask
    # import matplotlib.pyplot as plt
    # import matplotlib.image as mpimg
    # imgplot = plt.imshow(test)
    # plt.show()
    df = pd.DataFrame(data)
    return df

    # coordinates = [(x[0],x[1]) for x in np.uint16(np.around(circles))[0, :]]
    # radii = [x[2] for x in np.uint16(np.around(circles))[0, :]]
    # return pd.DataFrame({
    #     "coordinate":coordinates,
    #     "radius":radii
    # })

def plot_circles(
        image,
        df
):
    a=0
    for i, row in df.iterrows():
        if a<10:
            cv2.circle(image, row.coordinate, row.radius, (255, 0, 0), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            # label = f"{str(row.coordinate)}"
            x = 0
            for val in row.colour_values:
                x += val
            print(x)
            print(len(row.colour_values))
            x = x/len(row.colour_values)
            print(x)
            print(" ")
            label = f"{x}"
            cv2.putText(image, label, (row.coordinate[0] - int(row.radius/2), row.coordinate[1] + int(row.radius/2)), font, 1, (0,0,255), 2)
            a+=1
    return image

def plot(
        image,
        size=(50,7),
        gray=False
):
    plt.figure(figsize = size)
    if gray:
        plt.imshow(image, interpolation='nearest', cmap="gray")
    else:
        plt.imshow(image, interpolation='nearest')
    plt.show()

def annotate_images(
        image_paths:list,
        save_dir:str=None,
        blur_intensity=15,
        blur_type="median"
):
    if type(image_paths) == str:
        image_paths = [image_paths]
    circles_data_df = pd.DataFrame()
    for path in image_paths:
        if type(path) == str:
            file_name = os.path.basename(path)
            image = read_image(path)
        elif type(path) == np.ndarray:
            image = path.copy()
        try:
            grayed = gray(image)
        except:
            grayed = image.copy()
        blurred = blur(grayed,blur_intensity,type=blur_type)
        circles_df = find_circles(
            image=blurred,
            method=cv2.HOUGH_GRADIENT, 
            dp=1, 
            minDist=100,
            param1=20, 
            param2=30, 
            minRadius=25, 
            maxRadius=100
        )
        annotated_image = plot_circles(
            image,
            circles_df
        )
        if save_dir:
            cv2.imwrite(f"{save_dir}/{file_name}", annotated_image)
            circles_df["filename"] = file_name
        circles_data_df = pd.concat([circles_data_df,circles_df])
    if save_dir:
        circles_data_df.to_csv(f"{save_dir}/1_size_analysis.csv",index=False)
    return circles_data_df

def get_radii_hist(df,file_name):
    query_df = df.query("file_name == @file_name").copy()
    radii_list = query_df.radii.values[0].split(",")
    fig = px.histogram(radii_list)
    fig.show()