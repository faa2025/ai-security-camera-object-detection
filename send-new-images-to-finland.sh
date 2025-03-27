import os
import time
import subprocess

SOURCE_DIR = "this_directory"
DESTINATION = "polina@softala.haaga-helia.fi:~/images/"
SENT_FILES = set()
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def is_image_file(filename):
    return filename.lower().endswith(IMAGE_EXTENSIONS)

while True:
    for filename in os.listdir(SOURCE_DIR):
        if not is_image_file(filename):
            continue
        filepath = os.path.join(SOURCE_DIR, filename)
        if filepath not in SENT_FILES:
            try:
                subprocess.run(["scp", filepath, DESTINATION], check=True)
                SENT_FILES.add(filepath)
                print(f"Sent: {filename}")
            except subprocess.CalledProcessError:
                print(f"Failed to send: {filename}")
    time.sleep(10)
