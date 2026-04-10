import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileSystemMonitor:
    def __init__(self):
        self.events = []
        self.observer = Observer()

    def start(self):
        handler = FSHandler(self.events)
        self.observer.schedule(handler, ".", recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class FSHandler(FileSystemEventHandler):
    def __init__(self, events):
        self.events = events

    def on_any_event(self, event):
        self.events.append(
            f"{time.time()}: {event.event_type} — {event.src_path}"
        )
