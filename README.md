# ai-security-camera-object-detection
A computer vision model for detecting persons and vehicles in real-time using TensorFlow/keras/CNN. Designed for surveillance, traffic monitoring and security applications.

# Creators
- [Henein Roda](https://github.com/hxrda) (henein.roda@gmail.com)
- [Jesse Nevalainen](https://github.com/Suppiluliumas) (nevalainen.jesse92@gmail.com)
- [Juslin Jukka](https://github.com/jusju) (jukka.juslin@haaga-helia.fi)


# Project structure

<img width="126" alt="File_tree" src="https://github.com/user-attachments/assets/31049624-ab0c-49af-b6c4-493fb9342df4" />

# Installation process

- On Windows, install Windows Subsystem for Linux (WSL). Instructions at https://learn.microsoft.com/en-us/windows/wsl/install
- Clone the project: https://github.com/faa2025/ai-security-camera-object-detection
- Install virtual environment in WSL `pip install virtualenv`
- Run the virtual environment `source venv/bin/activate`
- Install latest Python version inside the virtual environment (venv)
- Install Tensorflow 2 in the virtual environment. Instructions at https://www.tensorflow.org/install
- Install required libraries
  
  ## Libraries
  - Run `pip install requirements.txt` in the virtual environment.
  - Clone at the root level of the project: Pretrained models library (https://github.com/tensorflow/models) & install the Object Detection API accroding to the instructions at https://www.tensorflow.org/hub/tutorials/tf2_object_detection#visualization_tools
 
  ## Technical requirements:
  - NVIDIA GPU

# Developer guide
 - Run `create_obj_model.py` to create the model. The model can be chosen from a list of available models. The model will be saved under `saved_model` folder.
 - Schedule the shell script `daylight_monitor.sh` with crontab (instructions included in the script) to run person (and optionally car) inference scripts.
 - If the Spring Boot application is running on localhost:8080, configure network settings to allow WSL to communicate with the Windows host and port 8080.
   1.  In admin powershell run New-NetFirewallHyperVRule -Name "MyWebServer" -DisplayName "My Web Server" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 8080
   2.  In Windows firewall go to advanced settings, inbound rules, new rule, port, set specific local ports 8080, select allow connection then next, accept defaults then next, name like example "WSL" and finish.
   3.  Open WSL settings and network tab select network mirrored, enable localhost forwarding, enable host address loop.
   4.  Shutdown WSL in admin powershell using command 'wsl --shutdown'
   5.  Restart WSL


# Screenshots


