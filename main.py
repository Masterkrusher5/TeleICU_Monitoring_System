import base64
import cv2
import numpy as np
import os
import shutil
import streamlit as st
import tempfile
import subprocess
from io import BytesIO

# Function to run YOLO and return predicted folder
def run_yolo(image_data):
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    try:
        temp_image_path = os.path.join(temp_dir, 'temp.jpg')
        image_array = np.array(bytearray(image_data.read()), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        success = cv2.imwrite(temp_image_path, image)
        if not success:
            raise IOError(f"Failed to write image to {temp_image_path}")
        
        yolo_command = (
            f"yolo task=detect mode=predict model='./icu_best.pt' "
            f"conf=0.9 source='{temp_image_path}' save=True project='{temp_dir}'"
        )
        result = subprocess.run(yolo_command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        
        folders = [f for f in os.listdir(temp_dir) if f.startswith('predict')]
        if not folders:
            raise FileNotFoundError("No prediction folders found in temporary directory.")
        latest_folder = max(folders, key=lambda f: os.path.getctime(os.path.join(temp_dir, f)))
        return os.path.join(temp_dir, latest_folder)
    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        shutil.rmtree(temp_dir)  # Clean up the temporary directory

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
        # Use BytesIO to temporarily store the uploaded image in memory
        image_data = BytesIO(uploaded_file.getvalue())
        
        # Run YOLO on the in-memory image
        try:
            predict_folder = run_yolo(image_data)
            images = get_images_from_directory(predict_folder)

            for image in images:
                st.image(image, caption='Predicted Image', use_column_width=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
