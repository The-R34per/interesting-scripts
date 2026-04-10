============================================================
PRIVILEGE ESCALATION SURFACE MAPPER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Privilege Escalation Surface Mapper is a competition-safe,
read-only tool designed to identify potential privilege
escalation vectors on Windows and Linux systems.

It does NOT exploit anything. It only enumerates and reports
possible weak points that could be relevant in Cyber Combat
scenarios.

The tool supports:
- OS auto-detection
- Multiple enumeration modules
- Output style modes (raw, explain, severity)
- Optional output-to-file
- Safe, read-only checks only


2. INSTALLING DEPENDENCIES
---------------------------

This tool requires:

- Python 3
- No external libraries

It runs immediately on any system with Python 3 installed.


3. HOW TO RUN THE TOOL
-----------------------

A) Default usage (recommended):

    python privesc_mapper.py

This automatically:
- Detects the OS
- Runs ALL modules
- Uses "explain" mode (findings + short notes)


B) Save output to a file:

    python privesc_mapper.py -o report.txt


C) Run specific modules only:

    python privesc_mapper.py --users --path

D) Run all modules explicitly:

    python privesc_mapper.py --all


4. OUTPUT STYLE MODES
----------------------

You can control how detailed the output is.

A) Raw mode (findings only):

    python privesc_mapper.py --raw

Example:
    Writable PATH entry: /usr/local/bin


B) Explain mode (default):

    python privesc_mapper.py --explain

Example:
    Writable PATH entry: /usr/local/bin
    Why this matters: Writable PATH entries can allow execution hijacking.


C) Severity mode (adds simple severity tags):

    python privesc_mapper.py --severity

Example:
    [MEDIUM] Writable PATH entry: /usr/local/bin
    Why this matters: Writable PATH entries can allow execution hijacking.


5. ENUMERATION MODULES
-----------------------

You can run modules individually or let the tool run all of
them by default.

--users
    Enumerates current user and group information.

--sudo
    Checks sudo/admin surface (read-only).

--services
    Lists service-related privilege escalation surfaces.

--suid
    Lists SUID/SGID binaries (Linux only).

--path
    Lists PATH entries and identifies writable directories.

--cron
    Lists cron jobs or scheduled tasks.

--containers
    Identifies container/virtualization indicators.

--all
    Runs all modules (default if none selected).


6. WHAT EACH MODULE DOES
-------------------------

A) User & Group Information
---------------------------
Shows:
- Current user
- Group memberships

Useful for identifying privilege boundaries.


B) Sudo / Admin Surface
------------------------
Shows:
- Sudo/admin configuration (read-only)
- Indicators of misconfiguration


C) Service Configuration Surface
--------------------------------
Shows:
- Service-related privilege escalation surfaces
- Weak or interesting service configurations (placeholder)


D) SUID / SGID (Linux Only)
---------------------------
Shows:
- SUID/SGID binaries
- Potential escalation surfaces


E) PATH & Writable Directories
------------------------------
Shows:
- PATH entries
- Writable directories in PATH
- Potential hijack points


F) Cron / Scheduled Tasks
-------------------------
Shows:
- Cron jobs (Linux)
- Scheduled tasks (Windows)
- Potential escalation surfaces


G) Container Indicators
-----------------------
Shows:
- Docker/LXC/container hints
- Potential breakout surfaces


7. OUTPUT FORMAT
-----------------

Each section is printed with a header:

    ========= PATH & Writable Directories =========
    <results>

If using explain or severity mode, each finding includes a
short note explaining why it matters.


8. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Run the mapper:

    python privesc_mapper.py

Step 2: Review:
- Writable PATH entries
- SUID/SGID binaries
- Service configuration surfaces
- Cron/scheduled tasks
- User/admin group membership

Step 3: Save findings:

    python privesc_mapper.py -o privesc_report.txt

Step 4: Use results to answer Cyber Combat questions.


9. TROUBLESHOOTING
--------------------

Problem: "Permission denied" on some checks
Solution:
    Some system files require elevated privileges to read.

Problem: SUID section empty on Linux
Solution:
    System may not have SUID binaries or placeholder logic
    needs to be expanded.

Problem: Windows shows "placeholder" values
Solution:
    Add your own enumeration logic in the placeholder functions.


10. SUMMARY
-----------
The Privilege Escalation Surface Mapper provides a safe,
read-only overview of potential privilege escalation vectors.
It supports multiple modules, output styles, and OS-aware
enumeration.

It is designed for Cyber Combat environments where rapid
privilege surface awareness is essential.

============================================================
END OF DOCUMENT
============================================================
