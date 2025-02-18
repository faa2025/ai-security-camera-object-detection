import numpy as np
import tensorflow as tf
import cv2
from collections import deque
import yt_dlp
import pathlib
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from PIL import Image
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util
from obj_detect import load_model  # Import model functions
from datetime import datetime
import time
import asyncio

# Load label map data (for visualization)
PATH_TO_LABELS = './models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

 
# Load TensorFlow human detection model (example)
model_path = "/home/jneval92/project_folder/object_detection/saved_model"  # Update with the correct path
model = tf.saved_model.load(model_path)

def get_livestream_url(youtube_url):

    ydl_opts = {'quiet': True, 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info_dict = ydl.extract_info(youtube_url, download=False)

        return info_dict['url']  # Direct video stream URL
 
youtube_url = "https://www.youtube.com/watch?v=mur-Ciu2zJM"  # Replace with actual livestream URL

stream_url = get_livestream_url(youtube_url)
def detect_human(frame):
    input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)  # Convert to tensor with dtype uint8
    detections = model(input_tensor)  # Get predictions
    detection_boxes = detections['detection_boxes'][0].numpy()
    detection_classes = detections['detection_classes'][0].numpy().astype(np.int32)
    detection_scores = detections['detection_scores'][0].numpy()
    for i in range(len(detection_boxes)):
        if detection_classes[i] == 18 and detection_scores[i] > 0.7:
            return True, detection_boxes, detection_classes, detection_scores
    return False, None, None, None
    
saved_frames = deque(maxlen=10)  # Store only recent frames
def process_frame(frame):
    detected, boxes, classes, scores = detect_human(frame)
    if detected:
        # Visualize the detection results on the frame
        viz_utils.visualize_boxes_and_labels_on_image_array(
            frame,
            boxes,
            classes,
            scores,
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        
        # Add timestamp to the frame
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        saved_frames.append(frame)  # Save detected frame
        cv2.imwrite(f"saved_human_frame/human_detected{timestamp}.jpg", frame)
        print("Human detected! Frame saved.")

        # Pause for 5 seconds
        #time.sleep(5)

# Capture frames in-memory with OpenCV
cap = cv2.VideoCapture(stream_url)
 
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    detect_human(frame)    
    # Process frame (send to AI model)
    process_frame(frame)
 
cap.release()
cv2.destroyAllWindows()



 

