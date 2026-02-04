#!/usr/bin/env python3
import time, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_FILES = {"USER.md", "IDENTITY.md", "CLAUDE.md", "MEMORY.md"}
SYNC_SCRIPT = "/root/clawd/scripts/cross-sync-memory.py"

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.last = 0
    def on_modified(self, event):
        if event.is_directory: return
        if event.src_path.split("/")[-1] in WATCH_FILES:
            if time.time() - self.last > 5:
                print(f"📝 {event.src_path} changed, syncing...")
                subprocess.run(["python3", SYNC_SCRIPT])
                self.last = time.time()

if __name__ == "__main__":
    print("👀 Watching docs...")
    o = Observer()
    o.schedule(Handler(), "/root/clawd", recursive=False)
    o.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: o.stop()
    o.join()
