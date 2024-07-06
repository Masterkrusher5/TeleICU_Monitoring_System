import os
import base64
import cv2
import time
import threading
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="TeleICU",
    description="YOLO",
    version="0.0.1",
)

origins = [
    "http://localhost:3000",  # Local development frontend URL
    "http://localhost:5173",  # Local development frontend URL
    "https://tele-icu-detection.vercel.app"  # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save and serve processed images
PROCESSED_DIRECTORY = "processed"
os.makedirs(PROCESSED_DIRECTORY, exist_ok=True)

# Serve processed images as static files
app.mount("/processed", StaticFiles(directory=PROCESSED_DIRECTORY), name="processed")

@app.post("/execute")
async def execute(file: UploadFile = File(...)):
    temp_image = './temp.jpg'
    with open(temp_image, 'wb') as f:
        f.write(await file.read())
    
    predict_folder = run_yolo(temp_image)
    images = get_images_from_directory(predict_folder)
    
    delete_files_after_delay(predict_folder, 60)

    return JSONResponse(content={"images": images})

def run_yolo(image_path):
    yolo_command = (
        r"yolo task=detect mode=predict model='./icu_best.pt' "
        f"conf=0.9 source='{image_path}' save=True project='.'"
    )
    os.system(yolo_command)
    
    folders = [f for f in os.listdir('.') if f.startswith('predict')]
    latest_folder = max(folders, key=os.path.getctime)
    return latest_folder

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

def delete_files_after_delay(directory, delay):
    def delete_files():
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
    
    threading.Thread(target=delete_files).start()

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
