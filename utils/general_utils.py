import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import plotly.express as px
import base64
from PIL import Image
from io import BytesIO
import json

def json_to_dict(data_store):
    if data_store:
        return json.loads(data_store)
    else:
        return {}

def proc_blur_image(contents):
    in_img = data_uri_to_cv2_img(contents)
    gray_img = gray(in_img)
    blurred_img = blur(gray_img,11,type="median")
    return blurred_img

def proc_image(contents,threshold):
    blurred_img = proc_blur_image(contents)
    circles_df = find_circles(
        image=blurred_img,
        method=cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=100,
        param1=20, 
        param2=30, 
        minRadius=25, 
        maxRadius=100
    )
    return circles_df

def draw_circles(contents,circles_df,threshold):
    blurred_img = proc_blur_image(contents)
    annotated_img = plot_circles(
        blurred_img,
        circles_df,
        threshold=threshold
    )
    return annotated_img

def data_url_to_array(data_url):
    """
    Converts a data URL containing an image to a NumPy array.

    This function assumes the data URL is in the format:
    data:image/png;base64,<base64_encoded_image_data>

    Parameters:
        data_url (str): The data URL containing the image.

    Returns:
        numpy.ndarray: The image data as a NumPy array.

    Raises:
        ValueError: If the data URL is not in the expected format.
    """
    if not data_url.startswith("data:image/"):
        raise ValueError("Invalid data URL format. Expected to start with 'data:image/'")
    
    # Split the data URL into parts
    header, encoded_data = data_url.split(",", 1)
    # Extract image format from header
    image_format = header.split("/")[1].split(";")[0]

    # Decode base64 data
    decoded_data = base64.b64decode(encoded_data)

    # Use PIL to convert to NumPy array
    with BytesIO(decoded_data) as buffer:
        img = Image.open(buffer)
        return np.array(img)


def data_uri_to_cv2_img(
        uri
):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def read_image(
        path
):
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

    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    circles = np.uint16(np.around(circles))
    data = []
    for i in circles[0, :]:
        x, y, r = i[0], i[1], i[2]
        
        mask = np.zeros_like(image, dtype="uint8")
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
        
        colour_vals = binary_image[mask == 255]
        
        data.append({
            "coordinate": (x, y),
            "radius": r,
            "colour_values": colour_vals.tolist()
        })
        try:
            test = mask + test
        except:
            test = mask
    df = pd.DataFrame(data)
    return df

def plot_circles(
        image,
        df,
        threshold
):
    a=0
    drawn = []
    for i, row in df.iterrows():
        font = cv2.FONT_HERSHEY_SIMPLEX
        x = 0
        for val in row.colour_values:
            x += val
        x = x/len(row.colour_values)
        if x < threshold:
            cv2.circle(image, row.coordinate, int(row.radius), (255, 0, 0), 2)
            label = f"{row.microm_radius}"
            cv2.putText(image, label, (row.coordinate[0] - int(row.radius/2), row.coordinate[1] + int(row.radius/2)), font, 1, (0,0,255), 2)
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

def get_radii_hist(
        df,
        file_name
):
    query_df = df.query("file_name == @file_name").copy()
    radii_list = query_df.radii.values[0].split(",")
    fig = px.histogram(radii_list)
    fig.show()