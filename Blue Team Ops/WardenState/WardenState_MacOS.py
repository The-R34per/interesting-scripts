import subprocess
import asyncio
import os
import psutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_PATHS = [
    "/Library/LaunchAgents",
    "/Library/LaunchDaemons",
    "~/Library/LaunchAgents",
    "/private/etc/pam.d",
    "/private/etc/sudoers.d"
]

class RedTeamDetector(FileSystemEventHandler):
    def on_modified(self, event):
        self.alert("MODIFIED", event.src_path)

    def on_created(self, event):
        self.alert("CREATED (Persistence?!)", event.src_path)

    def alert(self, action, path):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [!][!][!] {action}: {path}")
        print('\a')

def get_command_output(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except:
        return "Unknown/Error"

def get_mac_security_status():
    status = {}

    status["FileVault"] = "Enabled" if "FileVault is On" in get_command_output("fdesetup status") else "Disabled"

    fw_output = get_command_output("/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate")
    status["Firewall"] = "Enabled" if "enabled" in fw_output.lower() else "Disabled"

    status["Gatekeeper"] = "Enabled" if "assessments enabled" in get_command_output("spctl --status") else "Disabled"

    status["SIP"] = "Enabled" if "enabled" in get_command_output("csrutil status") else "Disabled"

    return status

async def monitor_network():
    print("[*] Network Monitor Active...")
    try:
        initial_conns = {(c.laddr, c.raddr) for c in psutil.net_connections()}
    except psutil.AccessDenied:
        print("[X] Network Error: Access Denied. Run with sudo.")
        return

    while True:
        await asyncio.sleep(2)
        try:
            current_conns = psutil.net_connections()
            for conn in current_conns:
                addr_pair = (conn.laddr, conn.raddr)
                if addr_pair not in initial_conns:
                    if conn.status == 'ESTABLISHED':
                        proc = psutil.Process(conn.pid).name() if conn.pid else "Unknown"
                        print(f"[!] NEW CONNECTION: {proc} ({conn.laddr} -> {conn.raddr})")
                    initial_conns.add(addr_pair)
        except Exception as e:
            pass

async def monitor_mac_security(interval=10):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Establishing macOS Security Baseline...")

    baseline = get_mac_security_status()
    for feature, state in baseline.items():
        print(f"- {feature}: {state}")

    while True:
        await asyncio.sleep(interval)
        current_state = get_mac_security_status()
        for feature, state in current_state.items():
            if state != baseline[feature]:
                print(f"[!] SECURITY CHANGE DETECTED! {feature}: {baseline[feature]} -> {state}")
                baseline[feature] = state

async def start_file_monitor():
    event_handler = RedTeamDetector()
    observer = Observer()
    for path in WATCH_PATHS:
        full_path = os.path.expanduser(path)
        if os.path.exists(full_path):
            observer.schedule(event_handler, full_path, recursive=False)

    observer.start()
    print("[*] File System Watchdog Active...")

    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        observer.stop()
    observer.join()


async def RealStartUp():
    await asyncio.gather(
        start_file_monitor(),
        monitor_network(),
        monitor_mac_security(interval=10)
    )

if __name__ == "__main__":

    print(r"""
        __        __              _            ____  _        _       
        \ \      / /_ _ _ __   __| | ___ _ __ / ___|| |_ __ _| |_ ___ 
         \ \ /\ / / _` | '__| / _` |/ _ \ '_ \\___ \| __/ _` | __/ _ \
          \ V  V / (_| | |   | (_| |  __/ | | |___) | || (_| | ||  __/
           \_/\_/ \__,_|_|    \__,_|\___|_| |_|____/ \__\__,_|\__\___|
        """)
    time.sleep(1.5)
    print("--- MAC DEFENDER INITIALIZED ---")
    try:
        asyncio.run(RealStartUp())
    except KeyboardInterrupt:
        print("\nExiting Defender...")
