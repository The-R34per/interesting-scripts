#!/usr/bin/env python3
import argparse
import curses
import os
import platform
import threading
import time
from collections import deque
from pathlib import Path

import psutil

def detect_os():
    return platform.system().lower()

class LogMonitor:
    def __init__(self, os_name, max_lines=200):
        self.os_name = os_name
        self.max_lines = max_lines
        self.lines = deque(maxlen=max_lines)
        self.running = False
        self.thread = None
        self.log_paths = self._default_logs()

    def _default_logs(self):
        if self.os_name == "linux":
            candidates = ["/var/log/auth.log", "/var/log/syslog"]
            return [Path(p) for p in candidates if Path(p).exists()]
        elif self.os_name == "windows":
            return []
        else:
            return []

    def start(self, extra_log=None):
        if extra_log:
            p = Path(extra_log)
            if p.exists():
                self.log_paths.append(p)
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _loop(self):
        positions = {p: 0 for p in self.log_paths}
        while self.running:
            for p in self.log_paths:
                try:
                    with p.open("r", errors="ignore") as f:
                        f.seek(positions.get(p, 0))
                        for line in f:
                            line = line.rstrip("\n")
                            if self._is_interesting(line):
                                self.lines.append(f"{p.name}: {line}")
                        positions[p] = f.tell()
                except Exception:
                    continue
            time.sleep(1)

    def _is_interesting(self, line):
        keywords = ["fail", "denied", "unauthorized", "error", "invalid", "login"]
        lower = line.lower()
        return any(k in lower for k in keywords)

class ProcessMonitor:
    def __init__(self, max_events=200):
        self.events = deque(maxlen=max_events)
        self.running = False
        self.thread = None
        self.known_pids = set()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _loop(self):
        while self.running:
            try:
                for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
                    if p.pid not in self.known_pids:
                        self.known_pids.add(p.pid)
                        self.events.append(
                            f"NEW PID {p.pid} - {p.info.get('name','?')}"
                        )
                    cpu = p.info.get("cpu_percent", 0.0)
                    if cpu and cpu > 50:
                        self.events.append(
                            f"HIGH CPU {cpu:.1f}% PID {p.pid} - {p.info.get('name','?')}"
                        )
            except Exception:
                pass
            time.sleep(2)


class FileMonitor:
    def __init__(self, paths, max_events=200):
        self.paths = [Path(p) for p in paths if Path(p).exists()]
        self.events = deque(maxlen=max_events)
        self.running = False
        self.thread = None
        self.snapshot = {}

    def start(self):
        self._take_snapshot()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _take_snapshot(self):
        snap = {}
        for base in self.paths:
            for root, dirs, files in os.walk(base):
                for f in files:
                    p = Path(root) / f
                    try:
                        snap[p] = p.stat().st_mtime
                    except Exception:
                        continue
        self.snapshot = snap

    def _loop(self):
        while self.running:
            new_snap = {}
            for base in self.paths:
                for root, dirs, files in os.walk(base):
                    for f in files:
                        p = Path(root) / f
                        try:
                            new_snap[p] = p.stat().st_mtime
                        except Exception:
                            continue

            for p, mtime in new_snap.items():
                if p not in self.snapshot:
                    self.events.append(f"NEW FILE: {p}")
                elif mtime != self.snapshot[p]:
                    self.events.append(f"MODIFIED: {p}")

            for p in self.snapshot:
                if p not in new_snap:
                    self.events.append(f"DELETED: {p}")

            self.snapshot = new_snap
            time.sleep(3)


class Dashboard:
    def __init__(self, stdscr, log_mon, proc_mon, file_mon):
        self.stdscr = stdscr
        self.log_mon = log_mon
        self.proc_mon = proc_mon
        self.file_mon = file_mon
        self.running = True

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        while self.running:
            self._draw()
            try:
                ch = self.stdscr.getch()
                if ch == ord('q'):
                    self.running = False
            except Exception:
                pass
            time.sleep(0.5)

    def _draw_box(self, y, x, h, w, title):
        win = self.stdscr.derwin(h, w, y, x)
        win.box()
        win.addstr(0, 2, f" {title} ")
        return win

    def _draw(self):
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()

        half_y = max_y // 2
        half_x = max_x // 2

        log_win = self._draw_box(0, 0, half_y, half_x, "Logs")
        proc_win = self._draw_box(0, half_x, half_y, max_x - half_x, "Processes")
        file_win = self._draw_box(half_y, 0, max_y - half_y, half_x, "File Changes")
        alert_win = self._draw_box(half_y, half_x, max_y - half_y, max_x - half_x, "Alerts")

        self._fill_window(log_win, list(self.log_mon.lines))
        self._fill_window(proc_win, list(self.proc_mon.events))
        self._fill_window(file_win, list(self.file_mon.events))

        alerts = []
        alerts.extend([l for l in self.log_mon.lines if "fail" in l.lower()])
        alerts.extend([e for e in self.proc_mon.events if "HIGH CPU" in e])
        alerts.extend(list(self.file_mon.events)[-10:])
        self._fill_window(alert_win, alerts[-(alert_win.getmaxyx()[0]-2):])

        self.stdscr.addstr(max_y - 1, 2, "Press 'Ctr + C' to quit")
        self.stdscr.refresh()

    def _fill_window(self, win, lines):
        h, w = win.getmaxyx()
        start = max(0, len(lines) - (h - 2))
        view = lines[start:]
        for idx, line in enumerate(view[: h - 2]):
            truncated = line[: w - 2]
            try:
                win.addstr(1 + idx, 1, truncated)
            except Exception:
                pass


def parse_args():
    parser = argparse.ArgumentParser(description="Blue Team Monitoring Dashboard (TUI)")
    parser.add_argument("--log", help="Extra log file to monitor", default=None)
    parser.add_argument(
        "--watch",
        help="Comma-separated directories to watch for file changes",
        default=None,
    )
    return parser.parse_args()


def main(stdscr, args):
    os_name = detect_os()

    log_mon = LogMonitor(os_name)
    log_mon.start(extra_log=args.log)

    watch_dirs = []
    if args.watch:
        watch_dirs = [p.strip() for p in args.watch.split(",") if p.strip()]
    else:
        if os_name == "linux":
            watch_dirs = ["/etc", "/var/www"]
        elif os_name == "windows":
            user = os.environ.get("USERNAME", "User")
            watch_dirs = [fr"C:\Users\{user}\Desktop", fr"C:\Users\{user}\Downloads"]

    file_mon = FileMonitor(watch_dirs)
    file_mon.start()

    proc_mon = ProcessMonitor()
    proc_mon.start()

    dash = Dashboard(stdscr, log_mon, proc_mon, file_mon)
    dash.run()

    log_mon.stop()
    proc_mon.stop()
    file_mon.stop()


if __name__ == "__main__":
    args = parse_args()
    curses.wrapper(main, args)
