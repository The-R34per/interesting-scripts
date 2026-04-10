============================================================
CREDENTIAL SPRAY AUTOMATOR (SAFE MODE)
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Credential Spray Automator is a competition-safe planning
tool that helps you design a credential spraying schedule
WITHOUT performing any authentication attempts.

This tool:
- Accepts usernames and passwords
- Models lockout policies
- Simulates spray rounds
- Generates a real-timestamp schedule
- Estimates lockout risk
- Outputs a human-readable plan or CSV file

It NEVER:
- Sends authentication attempts
- Contacts any network service
- Performs any login actions

This is a SAFE planning and timing tool only.


2. INSTALLING DEPENDENCIES
---------------------------

This tool requires:

- Python 3
- No external libraries

It runs immediately on any system with Python 3 installed.


3. HOW TO RUN THE TOOL
-----------------------

A) Basic usage:

    python cred_spray_planner.py --users users.txt --passwords pw.txt

This:
- Loads usernames and passwords
- Uses safe default policy values
- Generates a full spray plan with real timestamps


B) Inline usernames/passwords:

    python cred_spray_planner.py --user alice,bob --password Summer2024!

C) Save output to a text file:

    python cred_spray_planner.py --users u.txt --passwords p.txt -o plan.txt

D) Save output to CSV:

    python cred_spray_planner.py --users u.txt --passwords p.txt --csv plan.csv

E) Summary-only mode:

    python cred_spray_planner.py --users u.txt --passwords p.txt --summary-only


4. INPUT OPTIONS
-----------------

--users FILE
    Load usernames from a file (one per line)

--user u1,u2,u3
    Provide usernames inline

--passwords FILE
    Load passwords from a file (one per line)

--password p1,p2,p3
    Provide passwords inline


5. POLICY OPTIONS
------------------

--lockout-threshold N
    Maximum allowed attempts per user before lockout
    Default: 5

--lockout-window MIN
    Lockout window duration in minutes
    Default: 15

--cooldown MIN
    Time between spray rounds
    Default: 30


6. STRATEGY OPTIONS
--------------------

--per-round N
    Number of passwords used per spray round
    Default: 1

--max-attempts-per-user N
    Maximum attempts allowed per user in the entire plan
    Default: 3


7. OUTPUT OPTIONS
------------------

-o FILE, --out FILE
    Save the full text plan to a file

--csv FILE
    Save the plan as a CSV file

--summary-only
    Only print the summary (no per-attempt schedule)


8. HOW THE TOOL WORKS
----------------------

A) Load usernames and passwords
-------------------------------
The tool accepts input from files or inline arguments.
Duplicates are removed automatically.

B) Build spray rounds
----------------------
Passwords are grouped into rounds of size `--per-round`.

Example:
    passwords = [P1, P2, P3]
    per-round = 1

    Round 1: P1
    Round 2: P2
    Round 3: P3

C) Assign timestamps
---------------------
- Round 1 starts at the current system time
- Attempts inside a round are spaced evenly across the lockout window
- Each new round starts after:
      lockout_window + cooldown

Example:
    Lockout window: 15 minutes
    Cooldown: 30 minutes

    Round 1: starts now
    Round 2: starts now + 45 minutes
    Round 3: starts now + 90 minutes

D) Enforce max attempts per user
--------------------------------
No user will exceed:
    --max-attempts-per-user

E) Risk estimation
------------------
The tool compares:
    max_attempts_per_user  vs  lockout_threshold

Risk levels:
- NONE       (safe)
- ELEVATED   (equal to threshold)
- HIGH       (exceeds threshold)


9. OUTPUT FORMAT
-----------------

A) Full schedule example:

    ========= Credential Spray Plan (Simulated) =========
    Round  Timestamp           User                 Password
    ---------------------------------------------------------------
    1      2026-03-26 14:05    alice                Spring2026!
    1      2026-03-26 14:10    bob                  Spring2026!
    1      2026-03-26 14:15    carol                Spring2026!

B) Summary example:

    ========= Plan Summary =========
    Total attempts: 3
    Users involved: 3
    Lockout threshold: 5 attempts per 15 minutes
    Max attempts per user in this plan: 1
    Estimated lockout risk: NONE


10. TYPICAL COMPETITION WORKFLOW
---------------------------------

Step 1: Load usernames and passwords
Step 2: Run the planner with safe defaults
Step 3: Review timestamps and risk
Step 4: Export plan if needed
Step 5: Use the plan to answer Cyber Combat questions


11. TROUBLESHOOTING
--------------------

Problem: "No users provided"
Solution:
    Use --users FILE or --user u1,u2,...

Problem: "No passwords provided"
Solution:
    Use --passwords FILE or --password p1,p2,...

Problem: CSV not writing
Solution:
    Ensure the directory is writable


12. SUMMARY
-----------
The Credential Spray Automator is a safe, read-only planning
tool that generates a timestamped credential spray schedule
without performing any authentication attempts.

It is designed for Cyber Combat environments where timing,
policy modeling, and risk estimation are essential.

============================================================
END OF DOCUMENT
============================================================
