#!/bin/bash

# Hardcoded boolean value for testing (change to "false" to stop the script)
TEST_MODE="false"

# Path to the Python scripts to trigger
SCRIPT_TO_RUN_1="$HOME/object_detection/run_person_inference.py"
# SCRIPT_TO_RUN_2="$HOME/object_detection/run_car_inference.py"  # Uncomment to enable car detection

if [[ "$TEST_MODE" == "true" ]]; then
    # If true and script is not running, start person detection
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
    # If false and script is running, stop person detection
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
    # chmod 755 test_trigger.sh

# Schedule this script with crontab to run once every hour:
# Open crontab editor:
    # crontab -e 
# Add the following line to the end of the file (either the first or the second one):
    # 0 * * * * bash $HOME/object_detection/schedule_scripts/test_trigger.sh
    # 0 * * * * bash $HOME/object_detection/schedule_scripts/test_trigger.sh >> $HOME/object_detection/schedule_scripts/daytest_trigger.sh.log 2>&1
# Verify scheduled job:
    # crontab -l
