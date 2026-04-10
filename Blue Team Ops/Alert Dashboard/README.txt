============================================================
BLUE TEAM MONITORING DASHBOARD (TUI + OS AUTO-DETECT)
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Blue Team Monitoring Dashboard is a real-time,
terminal-based defensive console designed for competition
environments. It automatically detects the operating system
(Windows or Linux) and loads the correct monitoring modules.

The dashboard provides:
- Live log monitoring
- Process activity monitoring
- File integrity monitoring
- Real-time alerts
- A curses-based TUI (Text User Interface)

This tool is lightweight, fast, and requires no admin
privileges. It is designed for rapid situational awareness
during Cyber Combat exercises.


2. INSTALLING DEPENDENCIES
---------------------------

A) Python Requirements
----------------------
You must install:

- psutil
- curses (Linux/macOS)
- windows-curses (Windows only)

Install psutil:

    pip install psutil


B) Installing curses on Windows
-------------------------------
Windows does NOT include curses by default.
Install the Windows-compatible version:

    pip install windows-curses

After installation, Python can import curses normally.


C) Installing curses on Linux
-----------------------------
Most Linux distros already include curses.

If missing:

Debian/Ubuntu:
    sudo apt install python3-curses

Fedora/RHEL:
    sudo dnf install python3-curses

Arch:
    sudo pacman -S python-curses


3. HOW TO RUN THE DASHBOARD
----------------------------

Basic usage:

    python dashboard.py

Optional arguments:

    --log <path>       Monitor an additional log file
    --watch <dirs>     Comma-separated directories to watch

Example:

    python dashboard.py --log /var/log/auth.log --watch "/etc,/var/www"

Windows example:

    python dashboard.py --watch "C:\Users\YourName\Downloads,C:\Temp"


4. OS AUTO-DETECTION
---------------------

At startup, the dashboard detects the OS using:

    platform.system().lower()

This determines which monitoring modules to load:

Windows:
- Process monitor (psutil)
- File monitor (polling)
- Log monitor (only if a log file is provided)

Linux:
- Process monitor (psutil)
- File monitor (polling)
- Log monitor (auth.log, syslog, or custom)


5. WHAT THE DASHBOARD MONITORS
-------------------------------

A) Log Monitor
--------------
On Linux:
- /var/log/auth.log
- /var/log/syslog

On Windows:
- Only logs you explicitly provide with --log

The monitor highlights suspicious keywords:
- fail
- denied
- unauthorized
- invalid
- error
- login


B) Process Monitor
------------------
Tracks:
- New processes
- High CPU usage
- Unusual spikes in activity

Events look like:

    NEW PID 5321 - chrome.exe
    HIGH CPU 72.5% PID 884 - python.exe


C) File Integrity Monitor
-------------------------
Watches directories for:
- New files
- Modified files
- Deleted files

Example events:

    NEW FILE: /etc/passwd.bak
    MODIFIED: C:\Users\User\Downloads\config.ini
    DELETED: /var/www/html/index.php


6. THE TUI DASHBOARD
---------------------

The screen is divided into four panels:

1. Logs
2. Processes
3. File Changes
4. Alerts

Alerts are automatically generated from:
- Suspicious log entries
- High CPU processes
- File changes

Controls:
- Press 'q' to quit


7. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Start the dashboard:

    python dashboard.py

Step 2: Watch for:
- Unauthorized login attempts
- Unexpected processes
- File changes in critical directories

Step 3: Investigate suspicious activity:
- Check process names
- Check file paths
- Check log entries

Step 4: Document findings for scoring.

Step 5: Keep the dashboard running during active attacks.


8. TROUBLESHOOTING
-------------------

Problem: "ModuleNotFoundError: No module named 'curses'"
Solution (Windows):
    pip install windows-curses

Solution (Linux):
    sudo apt install python3-curses

Problem: No logs appear
Solution:
    Provide a log file manually:
        python dashboard.py --log /path/to/log

Problem: No file events appear
Solution:
    Add directories to watch:
        python dashboard.py --watch "/etc,/var/www"

Problem: Dashboard crashes on resize
Solution:
    Avoid resizing the terminal during curses rendering.


9. SUMMARY
-----------
The Blue Team Monitoring Dashboard provides a fast,
lightweight, real-time defensive console with:

- OS auto-detection
- Log monitoring
- Process monitoring
- File integrity monitoring
- Real-time alerts
- A clean curses-based UI

It is designed for Cyber Combat exercises where rapid
situational awareness is essential.
