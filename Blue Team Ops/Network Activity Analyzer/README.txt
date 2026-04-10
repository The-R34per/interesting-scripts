============================================================
LIVE NETWORK ACTIVITY ANALYZER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Live Network Activity Analyzer is a competition-safe,
read-only tool designed to give you real-time visibility into
network activity on a system.

It can:
- Show active TCP/UDP connections
- Show listening ports
- Identify associated processes
- Detect suspicious patterns
- Run in snapshot mode (default)
- Run in live continuous mode (--live)
- Save results to a file (-o)

This tool is ideal for Cyber Combat exercises where you must
quickly identify unusual network behavior or potential
malicious communication.


2. INSTALLING DEPENDENCIES
---------------------------

This tool requires:

- Python 3
- psutil

Install psutil:

    pip install psutil


3. HOW TO RUN THE TOOL
-----------------------

A) Single snapshot (default):

    python network_analyzer.py

This prints:
- All active connections
- Listening ports
- Process names
- Suspicious indicators

Then exits.


B) Live continuous monitoring:

    python network_analyzer.py --live

This updates every 2 seconds by default, similar to "top".


C) Live mode with custom interval:

    python network_analyzer.py --live --interval 1

Updates every 1 second.


D) Save output to a file:

    python network_analyzer.py -o report.txt

Works in both snapshot and live mode.


4. COMMAND-LINE OPTIONS
------------------------

--live
    Run in continuous monitoring mode.

--interval <seconds>
    Set refresh interval for live mode (default: 2).

--tcp
    Show TCP connections only.

--udp
    Show UDP connections only.

--listening
    Show listening ports only.

--established
    Show established connections only.

--processes
    Include process names (default).

--no-processes
    Hide process names.

-o <filename>, --out <filename>
    Save output to a file in addition to printing it.

-h, --help
    Show help menu.


5. WHAT THE TOOL DISPLAYS
--------------------------

Each connection is shown in the format:

    Proto   Local Address        Remote Address       State        PID   Process

Example:

    TCP     192.168.1.10:51532   34.117.59.81:443     ESTABLISHED  1024  chrome.exe


6. SUSPICIOUS PATTERN DETECTION
-------------------------------

The tool automatically flags:

A) Beacon-like behavior
-----------------------
Repeated connections from the same process to the same IP.

Example alert:
    [Beacon?] PID 1234 has 15 connections to 8.8.8.8


B) High connection count
------------------------
Processes with unusually large numbers of connections.

Example:
    [High conn count] PID 5678 has 25 active connections


C) Suspicious ports
-------------------
Connections to:
- 4444
- 1337
- 2222
- High ephemeral ports (>50000)

Example:
    [Suspicious port] PID 4321 -> 10.0.0.5:4444 (ESTABLISHED)


7. LIVE MODE BEHAVIOR
----------------------

In live mode, the screen updates continuously and shows:

- Current connections
- New connections since last update
- Closed connections since last update
- Suspicious alerts

Example:

    [+] New connections: 3
    [-] Closed connections: 1


8. OUTPUT FORMAT
-----------------

Snapshot mode:

    ========= Network Connections Snapshot =========
    <connection table>

    ========= Alerts =========
    <alerts or "none">

Live mode:

    Continuously updating table
    Alerts section
    Change tracking section


9. TYPICAL WORKFLOW
-------------------------------

Step 1: Run a quick snapshot:

    python network_analyzer.py

Step 2: Look for:
- Unknown outbound connections
- High-risk ports
- Beacon-like patterns
- Unexpected processes opening ports

Step 3: If something looks suspicious, switch to live mode:

    python network_analyzer.py --live

Step 4: Save findings:

    python network_analyzer.py -o network_report.txt

Step 5: Use results to answer Cyber Combat questions.


10. TROUBLESHOOTING
--------------------

Problem: "ModuleNotFoundError: No module named 'psutil'"
Solution:
    pip install psutil

Problem: No connections appear
Solution:
    Filters may be too restrictive (e.g., --tcp + --udp).

Problem: Live mode screen flickers
Solution:
    Increase interval:
        --interval 3


11. SUMMARY
-----------
The Live Network Activity Analyzer provides fast, safe,
real-time visibility into system network activity. It supports
snapshot mode, live mode, filtering, process visibility, and
suspicious pattern detection.

============================================================
END OF DOCUMENT
============================================================
