import os
import base64
import cv2
import time
import shutil
import streamlit as st

# Function to run YOLO and return predicted folder
def run_yolo(image_path):
    yolo_command = (
        r"yolo task=detect mode=predict model='./icu_best.pt' "
        f"conf=0.9 source='{image_path}' save=True project='.'"
    )
    os.system(yolo_command)
    
    folders = [f for f in os.listdir('.') if f.startswith('predict')]
    latest_folder = max(folders, key=os.path.getctime)
    return latest_folder

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

# Function to delete files from a directory after a delay
def delete_files_after_delay(directory, delay):
    time.sleep(delay)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# Streamlit App
def main():
    st.title('TeleICU Monitoring System')

    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        temp_image = './temp.jpg'
        with open(temp_image, 'wb') as f:
            f.write(uploaded_file.getvalue())

        predict_folder = run_yolo(temp_image)
        images = get_images_from_directory(predict_folder)

        delete_files_after_delay(predict_folder, 60)

        for image in images:
            st.image(image, caption='Predicted Image', use_column_width=True)

if __name__ == "__main__":
    main()
