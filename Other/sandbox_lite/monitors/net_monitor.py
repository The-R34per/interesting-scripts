import psutil
import time
import threading


class NetworkMonitor:
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
        while self.running:
            conns = psutil.net_connections()
            for c in conns:
                if c.raddr:
                    self.events.append(
                        f"{time.time()}: Network connection — {c.laddr} -> {c.raddr}"
                    )
            time.sleep(0.5)
