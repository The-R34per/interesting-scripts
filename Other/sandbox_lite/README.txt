============================================================
MALWARE SANDBOX LITE
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
Malware Sandbox Lite is a safe, competition-friendly tool
designed to observe and record the behavior of a program
inside a controlled environment.

It does NOT execute anything with elevated privileges and
does NOT allow harmful actions. It only monitors and logs:

- File system activity
- Process creation
- Network connection attempts
- Program runtime behavior

At the end of execution, the sandbox generates a complete
behavior report in a file named:

    sandbox_report.txt


2. DIRECTORY STRUCTURE
-----------------------

sandbox_lite/
    sandbox.py
    monitors/
        fs_monitor.py
        proc_monitor.py
        net_monitor.py
    reports/
        report_builder.py

Each component is modular and can be expanded or modified
without affecting the rest of the system.


3. HOW TO RUN THE SANDBOX
--------------------------

Basic usage:

    python3 sandbox.py <path_to_program>

Example:

    python3 sandbox.py suspicious.exe

Set a custom timeout (default = 10 seconds):

    python3 sandbox.py suspicious.exe --timeout 15

The sandbox will:
1. Start all monitors
2. Launch the target program
3. Observe behavior until:
   - the program exits, OR
   - the timeout is reached
4. Stop all monitors
5. Generate a behavior report


4. WHAT THE SANDBOX MONITORS
-----------------------------

A) File System Monitor
----------------------
Tracks:
- File creation
- File deletion
- File modification
- File movement

Logs look like:

    171147.23: modified — C:\Temp\abc.tmp


B) Process Monitor
------------------
Tracks:
- New processes starting
- Their PID
- Their executable name

Logs look like:

    171147.89: Process started — PID 5321, Name chrome.exe


C) Network Monitor
------------------
Tracks:
- Outbound connection attempts
- Local and remote addresses

Logs look like:

    171148.12: Network connection — 127.0.0.1:50000 -> 8.8.8.8:53


5. WHAT HAPPENS WHEN YOU RUN THE SANDBOX
-----------------------------------------

Step-by-step:

1. The sandbox starts all three monitors.
2. It launches the target program using subprocess.
3. The program runs normally (no elevated privileges).
4. Monitors record any observable behavior.
5. When the timeout expires or the program exits:
   - The sandbox terminates the process if needed.
   - All monitors stop.
   - A full report is generated.

The sandbox NEVER:
- Modifies your system
- Executes harmful actions
- Elevates privileges
- Emulates a full VM environment


6. THE REPORT FILE
-------------------

After execution, the sandbox creates:

    sandbox_report.txt

The report contains:

    === Malware Sandbox Lite Report ===
    Target: suspicious.exe
    Runtime: 9.82 seconds

    === File System Events ===
    <list of file events>

    === Process Events ===
    <list of process events>

    === Network Events ===
    <list of network events>

If no events were recorded in a category, it will show:

    (none)


7. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Run the sandbox on a suspicious binary:

    python3 sandbox.py sample.exe --timeout 10

Step 2: Open sandbox_report.txt

Step 3: Look for:
- Unexpected file writes
- New processes spawned
- Network connection attempts
- Indicators of malicious behavior

Step 4: Document findings in your team notes.

Step 5: Use the behavioral data to answer NCX malware
analysis questions quickly and accurately.


8. TROUBLESHOOTING
-------------------

Problem: "Failed to start process"
Solution: Ensure the target file exists and is executable.

Problem: No events recorded
Solution: The program may not have performed any observable
          actions during the timeout. Increase timeout.

Problem: Permission errors
Solution: Run the sandbox from a directory where you have
          full read/write permissions.


9. SUMMARY
-----------
Malware Sandbox Lite provides a safe, controlled way to
observe program behavior without executing harmful actions.

It is ideal for:
- Behavioral analysis
- Competition environments
- Quick triage of unknown binaries
- Generating clean, readable reports

============================================================
END OF DOCUMENT
============================================================
