import numpy as np
import tensorflow as tf
import cv2
import yt_dlp
import matplotlib
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from PIL import Image
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util
from datetime import datetime
import time
import threading
import requests

SPRING_BOOT_URL = "http://127.0.0.1:8080/sendHumanDetectionEmail" # Replace with actual server URL if deployed
def notify_human_detection():     
    try:         
        response = requests.get(SPRING_BOOT_URL)
        print(f"Notification sent, response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")

# Load label map data (for visualization)
PATH_TO_LABELS = './models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

# Load TensorFlow human detection model (example)
model_path = "/home/jneval92/project_folder/object_detection/saved_model"  # Update with the correct path
model = tf.saved_model.load(model_path)
youtube_url = "https://www.youtube.com/watch?v=VR-x3HdhKLQ"  # Replace with actual livestream URL

# Initialize a counter for unique filenames
frame_counter = 0

def get_livestream_url(youtube_url):
    ydl_opts = {'quiet': True, 'format': 'bestvideo[height<=720]'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        print(f"FPS: {info_dict.get('fps', 'Unknown')}")
        return info_dict['url']  # Direct video stream URL

def detect_human(frame):
    input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)  # Convert to tensor with dtype uint8
    detections = model(input_tensor)  # Get predictions
    detection_boxes = detections['detection_boxes'][0].numpy()
    detection_classes = detections['detection_classes'][0].numpy().astype(np.int32)
    detection_scores = detections['detection_scores'][0].numpy()
    for i in range(len(detection_boxes)):
        if detection_classes[i] == 3 and detection_scores[i] > 0.7:  # Assuming class 1 is 'person'
            return True, detection_boxes, detection_classes, detection_scores
    return False, None, None, None

def process_frame(frame):
    global frame_counter
    detected, boxes, classes, scores = detect_human(frame)
    if detected:
        threading.Thread(target=notify_human_detection, daemon=True).start()
        # Visualize the detection results on the frame
        viz_utils.visualize_boxes_and_labels_on_image_array(
            frame,
            boxes,
            classes,
            scores,
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        
        # Timestamp for unique filenames
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Add counter to the frame
        cv2.putText(frame, f"Frame {timestamp}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Save detected frame as an image
        cv2.imwrite(f"saved_human_frame/human_detected_{timestamp}.jpg", frame)
        print(f"Human detected! Frame {timestamp} saved.")
        

        # Define the codec and create VideoWriter object for the 5-second clip
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(f'saved_human_frame/human_clip_{timestamp}.avi', fourcc, 30.0, (frame.shape[1], frame.shape[0]))
        
        # Write the initial frame to the video file
        video_writer.write(frame)
        
        # Capture video for 5 seconds
        fps = 30  # Define the expected FPS
        num_frames = fps * 10  # Total frames for 10 seconds
        #start_time = time.time()
        frame_count = 0
        while frame_count < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame = frame.astype(np.uint8)
            video_writer.write(frame)
            frame_count += 1
            del frame  # Explicitly release the frame
        # Release the video writer
        video_writer.release()
        video_writer = None # Reset the video writer
        print(f"10-second video clip {timestamp} saved.")

def capture_frames():
    global cap
    last_capture_time = time.time()
    last_detection_time = time.time()
    frame_skip = 10  # Process every 5th frame
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip this frame
        
        current_time = time.time()
        if current_time - last_capture_time >= 1:  # Capture frame every 1 second
            last_capture_time = current_time
            
            # Process frame (send to AI model)
            detected = process_frame(frame)
            if detected:
                last_detection_time = time.time()
            del frame  # Explicitly release the frame

        # Print "Nothing detected" every 10 seconds if no detection occurs
        if time.time() - last_detection_time >= 10:
            print("Nothing detected")
            last_detection_time = time.time()


stream_url = get_livestream_url(youtube_url)
# Capture frames in-memory with OpenCV
cap = cv2.VideoCapture(stream_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reduce OpenCV buffer size

# Start the frame capture thread
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

# Keep the main thread running to keep the video capture open
try:
    while capture_thread.is_alive():
        time.sleep(10)
except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()