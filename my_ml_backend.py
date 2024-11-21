import cv2
import numpy as np
from label_studio_sdk import Client

def detect_blobs(image_path):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Threshold the image to binary
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create polygon annotations
    annotations = []
    for contour in contours:
        polygon = contour.reshape(-1, 2).tolist()
        annotations.append({
            "type": "polygon",
            "points": polygon
        })
    
    return annotations

def main():
    try:
        # Initialize Label Studio client
        client = Client(url='http://localhost:8080', api_key='YOUR_API_KEY')
        
        # Get tasks from Label Studio
        tasks = client.get_tasks()
        
        for task in tasks:
            image_url = task['data']['image']
            image_path = download_image(image_url)
            
            # Detect blobs and create annotations
            annotations = detect_blobs(image_path)
            
            # Send annotations back to Label Studio
            client.create_annotation(task_id=task['id'], annotations=annotations)
    except Exception as e:
        print(f"An error occurred: {e}")

def download_image(url):
    import requests
    from io import BytesIO
    from PIL import Image
    
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image_path = 'temp_image.png'
    image.save(image_path)
    
    return image_path

if __name__ == "__main__":
    main()