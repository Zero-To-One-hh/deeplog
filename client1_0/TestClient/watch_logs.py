import time
import os
import json
import requests  # Import requests library for sending HTTP requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log_file = "../result/output_log.txt"  # Log file to monitor
log_file = os.path.abspath(log_file)  # Convert to absolute path

API_URL = "http://localhost:8000/deviceTrustLevelModel"  # The API endpoint to send requests to

# Custom event handler
class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position = 0  # Record the last read position

    def on_modified(self, event):
        # Debug info to confirm event is triggered
        print("File modified event triggered.")

        # Check if this is the file we are monitoring
        if not event.is_directory and os.path.abspath(event.src_path) == log_file:
            print("Observer is running...")

            # Open the file, move to the last read position
            with open(log_file, "r") as file:
                file.seek(self.last_position)  # Start from the last read position

                # Read new log entries
                new_entries = file.readlines()
                self.last_position = file.tell()  # Update offset

                # Process new log entries
                for entry in new_entries:
                    entry = entry.strip()
                    if not entry:
                        continue  # Skip empty lines
                    # Here, parse the log entry to extract required fields
                    try:
                        # Assuming each log entry is a JSON object
                        log_data = json.loads(entry)

                        data = {
                            "browserId": log_data.get("browserId", ""),
                            "logId": log_data.get("logId", ""),
                            "deviceMac": log_data.get("deviceMac", ""),
                            "deviceIp": log_data.get("deviceIp", ""),
                            "accessPort": log_data.get("accessPort", 0),
                            "serviceId": log_data.get("serviceId", ""),
                            "accessedIp": log_data.get("accessedIp", ""),
                            "rawLog": entry,  # Include the raw log entry
                            "timestamp": log_data.get("timestamp", ""),
                        }

                        # Send POST request to the API endpoint
                        response = requests.post(API_URL, json=data)

                        if response.status_code == 200:
                            print("Request successful.")
                        else:
                            print(f"Request failed with status code {response.status_code}: {response.text}")

                    except json.JSONDecodeError:
                        print(f"Failed to parse log entry as JSON: {entry}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

# Create observer and start
observer = Observer()
event_handler = LogHandler()

# Monitor the directory containing the log file
observer.schedule(event_handler, path=os.path.dirname(log_file), recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("The last position is:", event_handler.last_position)
    observer.stop()

observer.join()
