#!/usr/bin/env python3
import subprocess
import numpy as np
import tensorflow as tf
import cv2
import time
from collections import deque
from datetime import datetime
import yt_dlp
import threading
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util

# filepath: /home/jneval92/project_folder/object_detection/old_test_obj_2.py
# ...existing code...

# Example: Load TensorFlow model
PATH_TO_LABELS = "./models/research/object_detection/data/mscoco_label_map.pbtxt"
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
model_path = "/home/jneval92/project_folder/object_detection/saved_model"
model = tf.saved_model.load(model_path)

def get_livestream_url(youtube_url):
    """Use yt_dlp to get the direct video stream URL."""
    ydl_opts = {
        'quiet': True,
        'format': 'best'  # or 'bestvideo[height<=720]+bestaudio/best' for 720p
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict['url']

youtube_url = "https://www.youtube.com/watch?v=EvsLqQS_80E"
stream_url = get_livestream_url(youtube_url)

def detect_human(frame):
    """
    Run inference on the frame and return whether a human was detected,
    plus the bounding boxes, classes, and scores for visualization.
    """
    input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)
    detections = model(input_tensor)
    boxes = detections['detection_boxes'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(np.int32)
    scores = detections['detection_scores'][0].numpy()

    # Example: class 1 or 16 might be 'person' in your label map
    for i in range(len(boxes)):
        if (classes[i] in (1, 16)) and (scores[i] > 0.7):
            return True, boxes, classes, scores
    return False, None, None, None

saved_frames = deque(maxlen=10)  # Store recent frames if needed

def record_5s_clip(initial_frame, frame_width, frame_height):
    """
    Record a 5-second clip using FFmpeg by piping raw frames into a new process.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_path = f"saved_human_frame/human_clip_{timestamp}.mp4"

    # Start a new FFmpeg process for writing
    ffmpeg_cmd = [
        "ffmpeg", "-y",               # Overwrite output file
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{frame_width}x{frame_height}",
        "-r", "20",                   # Frames per second
        "-i", "-",                    # Read from stdin (raw frames)
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    # Write the initial frame
    ffmpeg_proc.stdin.write(initial_frame.tobytes())

    start_time = time.time()
    while time.time() - start_time < 5:
        raw_frame = pipe.stdout.read(frame_size)
        if len(raw_frame) < frame_size:
            break
        curr_frame = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))
        ffmpeg_proc.stdin.write(curr_frame.tobytes())

    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()
    print("5-second video clip saved.")

def process_frame(frame):
    # Make the frame array writable
    frame = np.ascontiguousarray(frame)

    detected, boxes, classes, scores = detect_human(frame)
    if detected:
        viz_utils.visualize_boxes_and_labels_on_image_array(
            frame, boxes, classes, scores, category_index,
            use_normalized_coordinates=True, line_thickness=8
        )

        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2, cv2.LINE_AA)

        # Save snapshot
        snapshot_path = f"saved_human_frame/human_detected_{timestamp}.jpg"
        cv2.imwrite(snapshot_path, frame)
        print("Human detected! Frame saved.")

        # Record 5-second clip
        record_5s_clip(frame, FRAME_WIDTH, FRAME_HEIGHT)

def capture_ffmpeg_stream():
    """
    Read raw frames from FFmpeg (the YouTube stream).
    For each frame read, run 'process_frame' if enough time has passed.
    """
    global pipe, frame_size
    last_capture_time = time.time()

    while True:
        # Read one frame from the FFmpeg stdout pipe
        raw_frame = pipe.stdout.read(frame_size)
        if len(raw_frame) < frame_size:
            print("No more frames or stream ended.")
            break

        # Convert to NumPy array (BGR format)
        frame = np.frombuffer(raw_frame, np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))

        current_time = time.time()
        # Example: process a frame every 1 second
        if current_time - last_capture_time >= 1:
            last_capture_time = current_time
            process_frame(frame)

# Set your desired resolution (e.g., 1280x720)
FRAME_WIDTH, FRAME_HEIGHT = 1280, 720

# Start FFmpeg process to read raw frames from the YouTube stream
ffmpeg_cmd = [
    "ffmpeg",
    "-i", stream_url,
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-r", "20",  # read at 20 FPS
    "-s", f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
    "-an",       # no audio
    "-"
]
pipe = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**8)

# Calculate size of one frame in bytes
frame_size = FRAME_WIDTH * FRAME_HEIGHT * 3

# Start a thread to continuously read from pipe and process frames
capture_thread = threading.Thread(target=capture_ffmpeg_stream)
capture_thread.start()

# Keep main thread alive until capture_thread finishes or user stops
try:
    while capture_thread.is_alive():
        time.sleep(1)
except KeyboardInterrupt:
    pass

# Cleanup
pipe.stdout.close()
capture_thread.join()
print("Exiting...")