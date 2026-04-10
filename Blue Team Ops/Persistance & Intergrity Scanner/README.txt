============================================================
PERSISTENCE & INTEGRITY SCANNER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Persistence & Integrity Scanner is a competition-safe,
OS‑auto‑detecting defensive tool designed to quickly identify:

- Startup persistence mechanisms
- Suspicious or auto-starting services
- Scheduled tasks / cron jobs
- Lightweight integrity issues
- Unauthorized or new user accounts
- Suspicious network listeners

The tool is designed for Cyber Combat exercises where rapid
triage and situational awareness are essential.

It NEVER executes files or makes system changes. It only reads
system information and prints a structured report.


2. INSTALLING DEPENDENCIES
---------------------------

This tool requires:

- Python 3
- psutil

Install psutil:

    pip install psutil

No other dependencies are required.


3. HOW TO RUN THE TOOL
-----------------------

Basic usage (auto-scan):

    python persistence_scanner.py

This performs ALL scans automatically and prints results to
the terminal.

To also save the results to a file:

    python persistence_scanner.py -o report.txt

To run specific scans only:

    python persistence_scanner.py --services --network

To run specific scans AND save to a file:

    python persistence_scanner.py --startup --users -o findings.txt


4. COMMAND-LINE OPTIONS
------------------------

-h, --help
    Show the help menu and exit.

--startup
    Scan startup entries and autorun locations.

--services
    Scan system services (Windows: sc query, Linux: systemd).

--tasks
    Scan scheduled tasks (Windows: schtasks, Linux: cron).

--integrity
    Run lightweight integrity checks:
    - Windows: suspicious script files in system directories
    - Linux: world-writable files in /etc and /usr/bin

--users
    List user accounts and privileged groups.

--network
    List listening network ports and owning processes.

--all
    Run all scans (same as default behavior).

-o <filename>, --out <filename>
    Save the full report to a file in addition to printing it.


5. OS AUTO-DETECTION
---------------------

The tool automatically detects the operating system:

    platform.system().lower()

Supported:
- Windows
- Linux

Each scan automatically switches to the correct backend for
the detected OS.


6. WHAT EACH SCAN DOES
-----------------------

A) Startup Scan
---------------
Windows:
- Registry Run keys
- Startup folders

Linux:
- rc.local
- profile scripts
- bashrc/profile modifications

B) Services Scan
----------------
Windows:
- sc query type= service state= all

Linux:
- systemctl list-unit-files --type=service

C) Scheduled Tasks / Cron Scan
------------------------------
Windows:
- schtasks /query /fo LIST /v

Linux:
- crontab -l
- /etc/crontab
- /etc/cron.*

D) Integrity Scan
-----------------
Windows:
- Suspicious script extensions in system directories

Linux:
- World-writable files in /etc and /usr/bin

E) User Accounts Scan
---------------------
Windows:
- net user
- net localgroup administrators

Linux:
- /etc/passwd
- sudo / wheel groups

F) Network Listener Scan
------------------------
Cross-platform:
- psutil.net_connections(kind="inet")
- Lists listening ports and owning processes


7. OUTPUT FORMAT
-----------------

The tool prints a structured report with section headers:

    ========= Startup / Autoruns =========
    <results>

    ========= Services =========
    <results>

    ========= Scheduled Tasks / Cron =========
    <results>

    ========= Integrity / Suspicious Files =========
    <results>

    ========= User Accounts / Privileged Groups =========
    <results>

    ========= Network Listeners =========
    <results>

If -o is used, the same report is written to the specified file.


8. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Run the scanner:

    python persistence_scanner.py

Step 2: Look for:
- Unknown startup entries
- Suspicious services
- Unexpected scheduled tasks
- World-writable system files
- New or unauthorized users
- Unknown processes listening on ports

Step 3: Save findings:

    python persistence_scanner.py -o report.txt

Step 4: Use results to answer Cyber Combat questions.

Step 5: Include findings in your team’s incident report.


9. TROUBLESHOOTING
-------------------

Problem: "ModuleNotFoundError: No module named 'psutil'"
Solution:
    pip install psutil

Problem: No output appears for a scan
Solution:
    The OS may not support that scan type.

Problem: Permission denied errors
Solution:
    Some system files require elevated privileges to read.


10. SUMMARY
-----------
The Persistence & Integrity Scanner provides fast, safe,
OS-aware defensive triage. It identifies persistence,
suspicious services, scheduled tasks, integrity issues,
user accounts, and network listeners.

It is designed for Cyber Combat environments where rapid
visibility is critical.

============================================================
END OF DOCUMENT
============================================================
