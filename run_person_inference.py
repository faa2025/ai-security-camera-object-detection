"""
This script performs object detection on a YouTube livestream to detect humans.
It uses a TensorFlow model to process frames from the livestream and sends a notification
when a human is detected. The detected frames and a 10-second video clip are saved locally.
The script is modularized into an ObjectDetection class with methods for each major functionality.
"""
import numpy as np
import tensorflow as tf
import cv2
import yt_dlp
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from PIL import Image
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util
from datetime import datetime
import time
import threading
import requests
import os


class ObjectDetection:
    def __init__(self, model_path, label_path, youtube_url, notification_url):
        """
        Initialize the ObjectDetection class with model path, label path, YouTube URL, and notification URL.
        Load the TensorFlow model and category index for object detection.
        """
        self.model = tf.saved_model.load(model_path)
        self.category_index = label_map_util.create_category_index_from_labelmap(label_path, use_display_name=True)
        self.youtube_url = youtube_url
        self.notification_url = notification_url
        self.frame_counter = 0
        self.cap = None

    def get_livestream_url(self):
        """
        Get the livestream URL from the YouTube URL using yt_dlp.
        """
        ydl_opts = {'quiet': True, 'format': 'bestvideo[height<=720]'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.youtube_url, download=False)
            # Print the frames per second (FPS) of the video stream
            print(f"FPS: {info_dict.get('fps', 'Unknown')}")
            return info_dict['url']

    def notify_human_detection(self):
        """
        Send a notification to the specified URL when a human is detected.
        """
        try:
            response = requests.get(self.notification_url)
            print(f"Notification sent, response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send notification: {e}")

    def detect_human(self, frame):
        """
        Detect humans in the given frame using the TensorFlow model.
        Returns a tuple indicating whether a human was detected and the detection details.
        """
        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)
        detections = self.model(input_tensor)
        detection_boxes = detections['detection_boxes'][0].numpy()
        detection_classes = detections['detection_classes'][0].numpy().astype(np.int32)
        detection_scores = detections['detection_scores'][0].numpy()
        for i in range(len(detection_boxes)):
            if detection_classes[i] == 1 and detection_scores[i] > 0.7: # 1 = person, check github readme for other classes.
                return True, detection_boxes, detection_classes, detection_scores
        return False, None, None, None

    def process_frame(self, frame):
        """
        Process a single frame to detect humans, send notifications, and save detected frames and video clips.
        """
        detected, boxes, classes, scores = self.detect_human(frame)
        if detected:
            threading.Thread(target=self.notify_human_detection, daemon=True).start()
            viz_utils.visualize_boxes_and_labels_on_image_array(
                frame,
                boxes,
                classes,
                scores,
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=8)
            
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # Ensure the directory exists
            os.makedirs('recorded_media/saved_human_frame', exist_ok=True)
            os.makedirs('recorded_media/saved_human_clip', exist_ok=True)
            cv2.putText(frame, f"Frame {timestamp}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imwrite(f"recorded_media/saved_human_frame/human_detected_{timestamp}.jpg", frame)
            print(f"Human detected! Frame {timestamp} saved.")

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(f'recorded_media/saved_human_clip/human_clip_{timestamp}.avi', fourcc, 30.0, (frame.shape[1], frame.shape[0]))
            video_writer.write(frame)

            # Frames per second from the video stream
            fps = 30
            # Number of frames to capture for the video clip so duration is 10 seconds
            num_frames = fps * 10 
            # Intialize frame count
            frame_count = 0
            # Capture frames until the required number of frames is reached
            while frame_count < num_frames:
                # Read frame from the video stream
                ret, frame = self.cap.read()
                if not ret:
                    break
                # Convert the frame to uint8 type
                frame = frame.astype(np.uint8)
                # Write the frame to the video clip
                video_writer.write(frame)
                frame_count += 1
                # Delete the frame
                del frame
            # Release the video writer
            video_writer.release()
            print(f"10-second video clip {timestamp} saved.")

    def capture_frames(self):
        """
        Capture frames from the livestream and process them at regular intervals.
        """
        # Record the time of the last frame capture
        last_capture_time = time.time()
        # Record the time of the last human detection
        last_detection_time = time.time()
        # Number of frames to skip before processing the next frame to save memory
        frame_skip = 10
        # Initialize frame counter
        frame_count = 0
        # Loop to capture frames as long as the video object is open
        while self.cap.isOpened():
            # Read a frame from the video capture object
            ret, frame = self.cap.read()
            # If frame reading fails, print an error message and break the loop
            if not ret:
                print("Failed to grab frame")
                break
            # Increment the frame counter
            frame_count += 1
            # Skip frames based on the frame_skip value
            if frame_count % frame_skip != 0:
                continue
            # Get current time
            current_time = time.time()
            # Process the frame if at least 1 second has passed since the last capture
            if current_time - last_capture_time >= 1:
                last_capture_time = current_time
                self.process_frame(frame)
                del frame
            # Print a message if no detection has been made for 10 seconds
            if time.time() - last_detection_time >= 10:
                print("Nothing detected")
                last_detection_time = time.time()

    def start(self):
        # Get the livestream URL using the get_livestream_url method
        stream_url = self.get_livestream_url()
        # Initialize the video capture object with the livestream URL
        self.cap = cv2.VideoCapture(stream_url)
        # Set the buffer size for the video capture object to 2 frames
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        # Create and start a new thread to capture frames using the capture_frames method
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.start()

        try:
            # Keep the main thread alive while the capture thread is running
            while capture_thread.is_alive():
                time.sleep(10)
        except KeyboardInterrupt:
            # Handle keyboard interrupt (Ctrl+C) to stop the process gracefully
            pass

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    user_name = os.environ["USER"] # Get the username from the environment variables
    model_path = f"/home/{user_name}/ai-security-camera-object-detection/saved_model" # Path to created model
    label_path = './models/research/object_detection/data/mscoco_label_map.pbtxt' # cloned https://github.com/tensorflow/models repo path
    youtube_url = "https://www.youtube.com/watch?v=80MaYh4ksQk" # Replace with your own YouTube URL
    notification_url = "http://127.0.0.1:8080/sendHumanDetectionEmail"
    # Create an instance of the ObjectDetection class
    detector = ObjectDetection(model_path, label_path, youtube_url, notification_url)
    # Start the object detection process
    detector.start()
