# ai-security-camera-object-detection
A computer vision model for detecting persons and vehicles in real-time using TensorFlow/keras/CNN. Designed for surveillance, traffic monitoring and security applications.

This project performs real-time **human detection** using a pre-trained TensorFlow object detection model. It captures frames from the stream, detects people in the scene, and saves both annotated images and short video clips when humans are detected. Optional notifications can be triggered for each detection event.

---

## 🚀 Features

- 🎯 Real-time object detection with TensorFlow
- 📹 Automatically processes a YouTube livestream
- 🔲 Draws bounding boxes around detected people
- 💾 Saves snapshot frames and 5-second video clips when a person is detected
- 🔔 Sends notifications to a specified URL on detection
- 📁 Organized storage of captured media

---

# Creators
- [Henein Roda](https://github.com/hxrda) (henein.roda@gmail.com)
- [Jesse Nevalainen](https://github.com/Suppiluliumas) (nevalainen.jesse92@gmail.com)
- [Juslin Jukka](https://github.com/jusju) (jukka.juslin@haaga-helia.fi)


# Project structure
![Tree](https://github.com/user-attachments/assets/a3a1585e-462b-4cc6-84b0-db7e7f88ac21)



# Installation process

- On Windows, install Windows Subsystem for Linux (WSL2). Instructions at https://learn.microsoft.com/en-us/windows/wsl/install
- Clone the project inside the user's home directory inside the subsystem (refer to the project structure above): https://github.com/faa2025/ai-security-camera-object-detection
- Install pip `sudo apt install python3-pip` or pipx `sudo apt install pipx` if you do not have them
- Install virtual environment in WSL to project folder `pip install virtualenv` if it doesnt work try `pipx install virtualenv` and try again
- Create a virtual environment `python -m venv venv`
- Run the virtual environment `source venv/bin/activate`
- Install latest Python version at least newer than 3.10 inside the virtual environment (venv)
- Install Tensorflow 2 in the virtual environment. Instructions at https://www.tensorflow.org/install
- Install required libraries
  
  ## Libraries
  - Clone at the root level of the project: Pretrained models library (https://github.com/tensorflow/models) & install the Object Detection API accroding to the instructions at https://www.tensorflow.org/hub/tutorials/tf2_object_detection#visualization_tools
  - Install yt_dlp `pip install yt-dlp` (https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation)
 
  ## Technical requirements and recommendations:
  - Windows 10 or higher
  - NVIDIA GPU
  - Latest Nvidia drivers https://www.nvidia.com/en-us/drivers/

# Developer guide
 - Run `pyhton create_obj_model.py` to create the model. The model can be chosen from a list of available models. The model will be saved under `saved_model` folder.
 - For Chrome install an extension Get cookies.txt LOCALLY
 - Navigate to your Youtube page and export cookies using the extension
 - Transfer the cookies.txt to the root folder of the project
 - Run `python run_person_inference.py`
   
 - Connect remote WSL to Visual Studio Code(VS-Code):
   1. open VS-Code and go to Extension view.
   3. Search and install Remote - WSL extension by microsoft.
   4. To open your WSL project in VS-Code: In your WSL terminal navigate to your project folder 
      "cd /object_detection/ai-security-camera-object-detection$". When you are inside the 
      project type "code" and enter. It will open the VS-Code and when you click "Open Folder" 
      option in side bar in VS-Code you can search and click your project folder.

 - Run the Spring Boot application, which can be found in the backend folder of the camera repository. If the Spring Boot application is running on localhost:8080, configure network settings to allow WSL to communicate with the Windows host and port 8080.
  1.  In admin powershell run `New-NetFirewallHyperVRule -Name "MyWebServer" -DisplayName "My Web Server" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 8080`
  2.  In Windows firewall go to advanced settings, inbound rules, new rule, port, set specific local ports 8080, select allow connection then next, accept defaults then next, name like example "WSL" and finish.
  3.  Open WSL settings and network tab select network mirrored, enable localhost forwarding, enable host address loop.
  4.  Shutdown WSL in admin powershell using command `wsl --shutdown`
  5.  Restart WSL
 - The list of class identification numbers used in object detection can be found at https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/  


# Example output

![human_detected_2025-02-20_15-28-15](https://github.com/user-attachments/assets/6009520e-faa7-476e-a455-916dbaffd204)

![car_detected_2025-02-20_15-37-36](https://github.com/user-attachments/assets/12d11f22-9c29-4d9d-b787-5ab672a025f2)

![DEMO](polina-ezgif.com-video-to-gif-converter.gif)

