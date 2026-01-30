"""
File watcher service for real-time file updates
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.websocket_manager import ConnectionManager

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, workspace_root: str, exclude: list, ws_manager: ConnectionManager):
        self.workspace_root = workspace_root
        self.exclude = exclude
        self.ws_manager = ws_manager
        self.loop = None

    def should_exclude(self, path: str) -> bool:
        for exc in self.exclude:
            if exc in path:
                return True
        return False

    def get_rel_path(self, path: str) -> str:
        return os.path.relpath(path, self.workspace_root)

    def get_file_type(self, path: str) -> str:
        ext = Path(path).suffix.lower().lstrip(".")
        if ext in ["py", "js", "ts", "jsx", "tsx", "go", "rs", "java", "sh"]:
            return "code"
        elif ext in ["md", "txt", "rst", "pdf"]:
            return "doc"
        elif ext in ["png", "jpg", "jpeg", "gif", "svg", "webp"]:
            return "image"
        elif ext in ["json", "yaml", "yml", "toml", "ini", "env"]:
            return "config"
        return "other"

    def _broadcast(self, event_type: str, path: str):
        if self.should_exclude(path):
            return

        rel_path = self.get_rel_path(path)
        details = {
            "name": os.path.basename(path),
            "is_dir": os.path.isdir(path) if os.path.exists(path) else False,
            "type": self.get_file_type(path) if os.path.isfile(path) else "directory",
            "timestamp": datetime.utcnow().isoformat()
        }

        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.ws_manager.broadcast_file_event(event_type, rel_path, details),
                self.loop
            )

    def on_created(self, event):
        self._broadcast("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._broadcast("modified", event.src_path)

    def on_deleted(self, event):
        self._broadcast("deleted", event.src_path)

    def on_moved(self, event):
        self._broadcast("moved", event.dest_path)


class FileWatcher:
    def __init__(self, workspace_root: str, exclude: list, ws_manager: ConnectionManager):
        self.workspace_root = workspace_root
        self.exclude = exclude
        self.ws_manager = ws_manager
        self.observer = None
        self.handler = None

    async def start(self):
        """Start watching the workspace directory"""
        self.handler = FileEventHandler(
            self.workspace_root,
            self.exclude,
            self.ws_manager
        )
        self.handler.loop = asyncio.get_event_loop()

        self.observer = Observer()
        self.observer.schedule(
            self.handler,
            self.workspace_root,
            recursive=True
        )
        self.observer.start()
        print(f"📂 File watcher started: {self.workspace_root}")

    async def stop(self):
        """Stop the file watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("📂 File watcher stopped")
