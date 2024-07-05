import base64
import cv2
import numpy as np
import os
import shutil
import streamlit as st
import tempfile
import time
import subprocess

# Function to run YOLO and return predicted folder
def run_yolo(image_array):
    # Create a temporary directory to store the image and YOLO outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_image_path = os.path.join(temp_dir, 'temp.jpg')
        cv2.imwrite(temp_image_path, image_array)
        
        yolo_command = (
            r"yolo task=detect mode=predict model='./icu_best.pt' "
            f"conf=0.9 source='{temp_image_path}' save=True project='{temp_dir}'"
        )
        subprocess.run(yolo_command, shell=True, check=True)
        
        folders = [f for f in os.listdir(temp_dir) if f.startswith('predict')]
        if not folders:
            raise FileNotFoundError("No prediction folders found in temporary directory.")
        latest_folder = max(folders, key=lambda f: os.path.getctime(os.path.join(temp_dir, f)))
        return os.path.join(temp_dir, latest_folder)

# Function to get base64 encoded images from a directory
def get_images_from_directory(directory):
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    images_base64 = []

    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        _, encoded_image = cv2.imencode('.png', image_rgb)
        image_base64 = base64.b64encode(encoded_image).decode('utf-8')
        images_base64.append(f'data:image/png;base64,{image_base64}')
    
    return images_base64

# Streamlit App
def main():
    st.title('TeleICU Monitoring System')

    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image_array = cv2.imdecode(file_bytes, 1)
        
        # Run YOLO on the in-memory image
        try:
            predict_folder = run_yolo(image_array)
            images = get_images_from_directory(predict_folder)

            for image in images:
                st.image(image, caption='Predicted Image', use_column_width=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
