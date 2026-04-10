import argparse
import os
import platform
import subprocess
from datetime import datetime

import psutil


def detect_os():
    return platform.system().lower()  # 'windows', 'linux', 'darwin', etc.


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            errors="ignore"
        )
        if result.stdout:
            return result.stdout.strip().splitlines()
        if result.stderr:
            return [f"[stderr] {line}" for line in result.stderr.strip().splitlines()]
    except Exception as e:
        return [f"[!] Error running command {cmd}: {e}"]
    return []


def header(title):
    return f"{'=' * 10} {title} {'=' * 10}"



def scan_startup(os_name):
    lines = [header("Startup / Autoruns")]

    if os_name == "windows":
        # Registry Run keys
        try:
            import winreg
            run_keys = [
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
                r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
            ]
            for root, root_name in [(winreg.HKEY_CURRENT_USER, "HKCU"),
                                    (winreg.HKEY_LOCAL_MACHINE, "HKLM")]:
                for key_path in run_keys:
                    try:
                        key = winreg.OpenKey(root, key_path)
                    except OSError:
                        continue
                    lines.append(f"[{root_name}\\{key_path}]")
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            lines.append(f"  {name} = {value}")
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
        except ImportError:
            lines.append("[!] winreg not available, skipping registry Run keys")

        # Startup folders
        user = os.environ.get("USERNAME", "User")
        startup_paths = [
            fr"C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup",
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp",
        ]
        for path in startup_paths:
            if os.path.isdir(path):
                lines.append(f"[Startup folder] {path}")
                for entry in os.listdir(path):
                    lines.append(f"  {entry}")
    elif os_name == "linux":
        # Common persistence files
        candidates = [
            "/etc/rc.local",
            "/etc/profile",
            "/etc/bash.bashrc",
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.profile"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                lines.append(f"[File] {path}")
                try:
                    with open(path, "r", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                lines.append(f"  {line}")
                except Exception as e:
                    lines.append(f"  [!] Error reading {path}: {e}")
    else:
        lines.append("[!] Unsupported OS for startup scan")

    return lines



def scan_services(os_name):
    lines = [header("Services")]

    if os_name == "windows":
        cmd = "sc query type= service state= all"
        lines.extend(run_command(cmd))
    elif os_name == "linux":
        cmd = "systemctl list-unit-files --type=service --no-pager"
        lines.extend(run_command(cmd))
    else:
        lines.append("[!] Unsupported OS for services scan")

    return lines



def scan_tasks(os_name):
    lines = [header("Scheduled Tasks / Cron")]

    if os_name == "windows":
        cmd = "schtasks /query /fo LIST /v"
        lines.extend(run_command(cmd))
    elif os_name == "linux":
        lines.append("[User crontab]")
        lines.extend(run_command("crontab -l"))
        lines.append("")
        lines.append("[/etc/crontab]")
        if os.path.isfile("/etc/crontab"):
            try:
                with open("/etc/crontab", "r", errors="ignore") as f:
                    lines.extend([line.rstrip("\n") for line in f])
            except Exception as e:
                lines.append(f"[!] Error reading /etc/crontab: {e}")
        lines.append("")
        lines.append("[/etc/cron.*]")
        lines.extend(run_command("ls -R /etc/cron.*"))
    else:
        lines.append("[!] Unsupported OS for tasks scan")

    return lines



def scan_integrity(os_name):
    lines = [header("Integrity / Suspicious Files")]

    if os_name == "windows":
        suspicious_ext = (".ps1", ".vbs", ".js", ".bat", ".cmd")
        system_dirs = [
            r"C:\Windows\System32",
            r"C:\Windows",
        ]
        for base in system_dirs:
            if not os.path.isdir(base):
                continue
            lines.append(f"[Scan] {base} (suspicious script extensions)")
            try:
                for root, dirs, files in os.walk(base):
                    for f in files:
                        if f.lower().endswith(suspicious_ext):
                            full = os.path.join(root, f)
                            lines.append(f"  {full}")
            except Exception as e:
                lines.append(f"  [!] Error scanning {base}: {e}")
    elif os_name == "linux":
        # Look for world-writable files in /etc and /usr/bin
        targets = ["/etc", "/usr/bin"]
        for base in targets:
            if not os.path.isdir(base):
                continue
            lines.append(f"[World-writable files] {base}")
            try:
                for root, dirs, files in os.walk(base):
                    for f in files:
                        full = os.path.join(root, f)
                        try:
                            st = os.stat(full)
                            if st.st_mode & 0o002:
                                lines.append(f"  {full}")
                        except Exception:
                            continue
            except Exception as e:
                lines.append(f"  [!] Error scanning {base}: {e}")
    else:
        lines.append("[!] Unsupported OS for integrity scan")

    return lines



def scan_users(os_name):
    lines = [header("User Accounts / Privileged Groups")]

    if os_name == "windows":
        lines.append("[net user]")
        lines.extend(run_command("net user"))
        lines.append("")
        lines.append("[Administrators group]")
        lines.extend(run_command("net localgroup administrators"))
    elif os_name == "linux":
        lines.append("[/etc/passwd]")
        try:
            with open("/etc/passwd", "r", errors="ignore") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if line:
                        lines.append(line)
        except Exception as e:
            lines.append(f"[!] Error reading /etc/passwd: {e}")
        lines.append("")
        lines.append("[sudo / wheel groups]")
        lines.extend(run_command("getent group sudo"))
        lines.extend(run_command("getent group wheel"))
    else:
        lines.append("[!] Unsupported OS for users scan")

    return lines



def scan_network(os_name):
    lines = [header("Network Listeners")]

    try:
        conns = psutil.net_connections(kind="inet")
    except Exception as e:
        lines.append(f"[!] Error getting connections: {e}")
        return lines

    for c in conns:
        if c.status != psutil.CONN_LISTEN:
            continue
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "?:?"
        pid = c.pid or 0
        try:
            p = psutil.Process(pid) if pid else None
            name = p.name() if p else "unknown"
        except Exception:
            name = "unknown"
        lines.append(f"LISTEN {laddr} PID {pid} ({name})")

    return lines



def build_report(args):
    os_name = detect_os()
    sections = []

    # determine which scans to run
    selected = any([
        args.startup, args.services, args.tasks,
        args.integrity, args.users, args.network, args.all
    ])

    run_startup = args.startup or args.all or not selected
    run_services = args.services or args.all or not selected
    run_tasks = args.tasks or args.all or not selected
    run_integrity = args.integrity or args.all or not selected
    run_users = args.users or args.all or not selected
    run_network = args.network or args.all or not selected

    banner = [
        header("Persistence & Integrity Scanner"),
        f"OS detected: {os_name}",
        f"Timestamp: {datetime.now().isoformat()}Z",
        ""
    ]
    sections.extend(banner)

    if run_startup:
        sections.extend(scan_startup(os_name))
        sections.append("")
    if run_services:
        sections.extend(scan_services(os_name))
        sections.append("")
    if run_tasks:
        sections.extend(scan_tasks(os_name))
        sections.append("")
    if run_integrity:
        sections.extend(scan_integrity(os_name))
        sections.append("")
    if run_users:
        sections.extend(scan_users(os_name))
        sections.append("")
    if run_network:
        sections.extend(scan_network(os_name))
        sections.append("")

    return "\n".join(sections)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Persistence & Integrity Scanner (Cyber Combat – Tool C)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--startup",
        action="store_true",
        help="Scan startup / autorun locations",
    )
    parser.add_argument(
        "--services",
        action="store_true",
        help="Scan services",
    )
    parser.add_argument(
        "--tasks",
        action="store_true",
        help="Scan scheduled tasks / cron",
    )
    parser.add_argument(
        "--integrity",
        action="store_true",
        help="Run lightweight integrity checks",
    )
    parser.add_argument(
        "--users",
        action="store_true",
        help="List users and privileged groups",
    )
    parser.add_argument(
        "--network",
        action="store_true",
        help="List listening network ports and owning processes",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scans (default if no specific scan is selected)",
    )
    parser.add_argument(
        "-o",
        "--out",
        help="Also write full report to this file",
        default=None,
    )

    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)

    # always print to terminal
    print(report)

    # optionally write to file
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n[+] Report written to {args.out}")
        except Exception as e:
            print(f"\n[!] Failed to write report to {args.out}: {e}")


if __name__ == "__main__":
    main()
