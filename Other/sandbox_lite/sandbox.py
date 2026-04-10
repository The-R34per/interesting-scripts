#!/usr/bin/env python3
import argparse
import subprocess
import time
from pathlib import Path

from monitors.fs_monitor import FileSystemMonitor
from monitors.proc_monitor import ProcessMonitor
from monitors.net_monitor import NetworkMonitor
from reports.report_builder import ReportBuilder


def run_sandbox(target: str, timeout: int):
    print(f"[+] Starting sandbox for: {target}")
    start_time = time.time()

    fs = FileSystemMonitor()
    proc = ProcessMonitor()
    net = NetworkMonitor()

    fs.start()
    proc.start()
    net.start()

    try:
        p = subprocess.Popen([target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[+] Process started with PID {p.pid}")
    except Exception as e:
        print(f"[!] Failed to start process: {e}")
        return

    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("[!] Timeout reached — terminating process")
        p.terminate()

    fs.stop()
    proc.stop()
    net.stop()

    report = ReportBuilder(
        target=target,
        fs_events=fs.events,
        proc_events=proc.events,
        net_events=net.events,
        runtime=time.time() - start_time,
    )

    output_path = Path("sandbox_report.txt")
    output_path.write_text(report.build())
    print(f"[+] Report saved to: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Malware Sandbox Lite")
    parser.add_argument("target", help="Path to executable to analyze")
    parser.add_argument("--timeout", type=int, default=10, help="Max runtime in seconds")
    return parser.parse_args()


def main():
    args = parse_args()
    run_sandbox(args.target, args.timeout)


if __name__ == "__main__":
    main()
