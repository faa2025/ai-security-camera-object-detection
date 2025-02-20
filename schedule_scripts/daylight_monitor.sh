#!/bin/bash

# This script triggers "run_person_inference.py" based on daylight status.
# Daylight status is fetched from the Spring Boot app.
# If car inference is wanted also, uncomment those sections in the code.

# API Endpoint of your Spring Boot application
API_URL="http://127.0.0.1:8080/api/daylight"  # Replace with actual backend URL if needed

# Paths to the Python scripts to run
SCRIPT_TO_RUN_1="$HOME/object_detection/run_person_inference.py"
# SCRIPT_TO_RUN_2="$HOME/object_detection/run_car_inference.py"  # Uncomment to enable car detection

# Check API response
response=$(curl -s "$API_URL")

if [[ "$response" == "true" ]]; then
    # If true, start person detection if not already running
    if ! pgrep -f "$SCRIPT_TO_RUN_1" > /dev/null; then
        echo "Starting person detection..."
        source venv/bin/activate && nohup python3 "$SCRIPT_TO_RUN_1" &>/dev/null &
    else
        echo "Person detection is already running."
    fi

    # # Uncomment below to enable car detection
    # if ! pgrep -f "$SCRIPT_TO_RUN_2" > /dev/null; then
    #     echo "Starting car detection..."
    #     source venv/bin/activate && nohup python3 "$SCRIPT_TO_RUN_2" &>/dev/null &
    # else
    #     echo "Car detection is already running."
    # fi
else
    # If false, stop person detection if running
    if pgrep -f "$SCRIPT_TO_RUN_1" > /dev/null; then
        echo "Stopping person detection..."
        pkill -f "$SCRIPT_TO_RUN_1"
    else
        echo "Person detection is not running."
    fi

    # # Uncomment below to enable stopping car detection
    # if pgrep -f "$SCRIPT_TO_RUN_2" > /dev/null; then
    #     echo "Stopping car detection..."
    #     pkill -f "$SCRIPT_TO_RUN_2"
    # else
    #     echo "Car detection is not running."
    # fi
fi


# Make this script executable:
    # chmod 755 daylight_monitor.sh

# Schedule this script with crontab to run once every hour:
# Open crontab editor:
    # crontab -e 
# Add the following line to the end of the file (either the first or the second one):
    # 0 * * * * bash $HOME/object_detection/schedule_scripts/daylight_monitor.sh
    # 0 * * * * bash $HOME/object_detection/schedule_scripts/daylight_monitor.sh >> $HOME/object_detection/schedule_scripts/daylight_monitor.log 2>&1
# Verify scheduled job:
    # crontab -l


