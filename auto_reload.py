import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"{event.src_path} changed. Restarting the app...")
            self.restart_app()

    def start_app(self):
        env = os.environ.copy()
        env['ENV'] = 'DEV'  # Set the environment variable for development mode
        self.process = subprocess.Popen(['briefcase', 'dev'], env=env)

    def restart_app(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.start_app()

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), 'src')
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()




'''import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print(f"{event.src_path} changed. Restarting the app...")
            self.restart_app()

    def start_app(self):
        self.process = subprocess.Popen(['briefcase', 'dev'])

    def restart_app(self):
        self.process.terminate()
        self.start_app()

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), 'src')  # Watch the 'src' folder for changes
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()'''
