============================================================
NETWORK ATTACK SURFACE MAPPER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
This tool performs a fast, asynchronous scan of a target
host to identify open ports, grab service banners, and
produce a prioritized attack surface report.

It is designed for competition environments where speed,
clarity, and actionable information are critical.

The tool:
- Scans a user-defined port range
- Attempts to connect to each port
- Grabs banners when possible
- Identifies common services
- Assigns a simple risk score
- Outputs a sorted attack surface map


2. HOW TO RUN THE TOOL
-----------------------

Basic scan (default ports 1–1024):

    python3 attack_surface_mapper.py <target_ip>

Example:

    python3 attack_surface_mapper.py 10.0.0.5


Scan specific ports:

    python3 attack_surface_mapper.py 10.0.0.5 -p 22,80,443


Scan a range:

    python3 attack_surface_mapper.py 10.0.0.5 -p 1-65535


Scan mixed ranges:

    python3 attack_surface_mapper.py 10.0.0.5 -p 1-1024,3306,3389


3. OUTPUT FORMAT
----------------

The tool prints a report similar to:

    === Attack Surface Report ===
    Host: 10.0.0.5
    Scanned at (UTC): 2026-03-26T15:30:12

    PORT   SERVICE     RISK  BANNER
    ------------------------------------------------------------
    445    smb         5     SMBv1 Server (Workgroup: WORKGROUP)
    22     ssh         3     OpenSSH_7.4
    80     http        3     Apache/2.4.29 (Ubuntu)

Fields:
- PORT:    The open port number
- SERVICE: Best guess based on common ports
- RISK:    Simple scoring system (higher = more interesting)
- BANNER:  Any text returned by the service


4. RISK SCORING LOGIC
----------------------

The tool assigns a basic risk score based on:
- Known high-value ports (e.g., SMB, RDP, FTP)
- Service banners (e.g., Apache, OpenSSH, Samba)
- Potentially weak or legacy services

This is NOT a vulnerability scanner. It is a fast
triage tool to help prioritize manual analysis.


5. INTERNAL WORKFLOW
---------------------

A) Port Scanning
----------------
The tool uses asyncio to scan many ports concurrently.
If a TCP connection succeeds, the port is considered open.

B) Banner Grabbing
------------------
After connecting, the tool attempts to read up to 1024 bytes
from the service. If the service responds, the banner is
captured and displayed.

C) Service Identification
-------------------------
Common ports are mapped to likely services (e.g., 22 → ssh).

D) Report Generation
--------------------
All findings are sorted by risk score and printed in a
clean, readable table.


6. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Run a fast scan on the target:

    python3 attack_surface_mapper.py <target>

Step 2: Identify high-risk services:
- SMB (445)
- RDP (3389)
- FTP (21)
- HTTP/HTTPS (80/443)
- SSH (22)

Step 3: Use findings to guide deeper analysis:
- Version enumeration
- Vulnerability research
- Exploit development
- Service-specific testing

Step 4: Document findings in your team notes.


7. TROUBLESHOOTING
-------------------

Problem: "No open ports found"
Solution: Expand the port range using -p 1-65535.

Problem: "Connection refused" or "Timeout"
Solution: This is normal for closed ports; the tool continues.

Problem: Slow scan
Solution: The tool already uses high concurrency, but scanning
          1–65535 will always take longer than scanning 1–1024.


8. SUMMARY
-----------
This tool provides a fast, lightweight method for mapping a
target's exposed services and prioritizing attack vectors.
It is optimized for competition use where speed and clarity
are essential.

============================================================
END OF DOCUMENT
============================================================
