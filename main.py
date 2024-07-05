import os
import base64
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import subprocess

# Function to run YOLO and return predictions
def run_yolo(image_path):
    yolo_command = (
        f"yolo task=detect mode=predict model='./icu_best.pt' "
        f"conf=0.9 source='{image_path}' save=False"
    )
    result = subprocess.run(yolo_command, shell=True, capture_output=True)
    return result

# Function to get base64 encoded image
def get_image_base64(image):
    _, encoded_image = cv2.imencode('.png', image)
    image_base64 = base64.b64encode(encoded_image).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# Streamlit App
def main():
    st.title('TeleICU Monitoring System')

    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        # Convert uploaded file to an image
        image = Image.open(uploaded_file)
        image = np.array(image)

        # Save the uploaded image temporarily
        temp_image_path = './temp_image.jpg'
        cv2.imwrite(temp_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Run YOLO on the uploaded image
        run_yolo(temp_image_path)

        # Get the processed image (assuming the model saves or modifies the image in place)
        processed_image = cv2.imread(temp_image_path)
        processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)

        # Get base64 encoded image for displaying in Streamlit
        image_base64 = get_image_base64(processed_image_rgb)

        st.image(image_base64, caption='Predicted Image', use_column_width=True)

        # Optionally, clean up the temporary image
        os.remove(temp_image_path)

if __name__ == "__main__":
    main()
