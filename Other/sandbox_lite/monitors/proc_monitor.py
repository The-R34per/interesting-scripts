import psutil
import time
import threading


class ProcessMonitor:
    def __init__(self):
        self.events = []
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def monitor_loop(self):
        known = set()
        while self.running:
            for p in psutil.process_iter(["pid", "name"]):
                if p.pid not in known:
                    known.add(p.pid)
                    self.events.append(
                        f"{time.time()}: Process started — PID {p.pid}, Name {p.info['name']}"
                    )
            time.sleep(0.5)
