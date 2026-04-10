import subprocess
import asyncio
import os
import psutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_PATHS = [
    os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
    "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
    "C:\\Windows\\System32\\drivers\\etc",
    "C:\\Windows\\System32\\tasks"
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
        # FIX: Use shell=True for complex commands like netsh and reg query
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except subprocess.CalledProcessError as e:
        # FIX: Return the error output for better debugging
        return f"Error: {e.output.strip() if e.output else str(e)}"
    except Exception:
        return "Unknown/Error"


def get_windows_security_status():
    status = {}

    av_check = get_command_output("powershell -Command \"(Get-MpComputerStatus).RealTimeProtectionEnabled\"")
    status["RealTimeProtection"] = "Enabled" if "True" in av_check else "Disabled"

    # FIX: Use a more reliable way to check firewall status
    fw_check = get_command_output("netsh advfirewall show allprofiles state | findstr State")
    status["Firewall"] = "Enabled" if "ON" in fw_check else "Disabled"

    cloud_check = get_command_output("powershell -Command \"(Get-MpComputerStatus).IsCloudProtectionEnabled\"")
    status["CloudProtection"] = "Enabled" if "True" in cloud_check else "Disabled"

    uac_check = get_command_output("reg query \"HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v ConsentPromptBehaviorAdmin")
    status["UAC_Strictness"] = "High" if "0x2" in uac_check or "0x1" in uac_check else "Low/Standard"

    return status

async def monitor_network():
    print("[*] Network Monitor Active...")
    try:
        initial_conns = {(c.laddr, c.raddr) for c in psutil.net_connections()}
    except psutil.AccessDenied:
        print("[X] Network Error: Access Denied. Run as Administrator.")
        return

    while True:
        await asyncio.sleep(2)
        try:
            current_conns = psutil.net_connections()
            for conn in current_conns:
                addr_pair = (conn.laddr, conn.raddr)
                if addr_pair not in initial_conns:
                    if conn.status == 'ESTABLISHED':
                        # FIX: Removed the erroneous proc.name() line
                        try:
                            proc = psutil.Process(conn.pid).name() if conn.pid else "Unknown"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            proc = "System/Protected"
                        print(f"[!] NEW CONNECTION: {proc} ({conn.laddr} -> {conn.raddr})")
                    initial_conns.add(addr_pair)
        except Exception:
            pass

async def monitor_win_security(interval=10):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Establishing Windows Security Baseline...")

    baseline = get_windows_security_status()
    for feature, state in baseline.items():
        print(f"- {feature}: {state}")

    while True:
        await asyncio.sleep(interval)
        current_state = get_windows_security_status()
        for feature, state in current_state.items():
            if state != baseline[feature]:
                print(f"[!] SECURITY CHANGE DETECTED! {feature}: {baseline[feature]} -> {state}")
                baseline[feature] = state

async def start_file_monitor():
    event_handler = RedTeamDetector()
    observer = Observer()
    for path in WATCH_PATHS:
        if os.path.exists(path):
            try:
                observer.schedule(event_handler, path, recursive=False)
                print(f"[*] Monitoring: {path}")
            except PermissionError:
                print(f"[!] Permission denied for path: {path}")
            except Exception as e:
                print(f"[!] Error monitoring {path}: {e}")

    observer.start()
    print("[*] File System Watchdog Active...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # FIX: Only catch KeyboardInterrupt here, not all exceptions
        print("\n[*] Stopping file monitor...")
        observer.stop()
    observer.join()

async def RealStartUp():
    await asyncio.gather(
        start_file_monitor(),
        monitor_network(),
        monitor_win_security(interval=10)
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
    print("--- WINDOWS DEFENDER INITIALIZED ---")
    try:
        asyncio.run(RealStartUp())
    except KeyboardInterrupt:
        print("\nExiting Defender...")