============================================================
FILE INTEGRITY CHECKER (HYBRID MODE)
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
This tool provides two modes of operation:

A) MENU MODE (default)
   - Activated when you run the script with NO arguments.
   - Allows checking a single file or an entire directory.
   - Uses your original ASCII-art interface.

B) ADVANCED CLI MODE
   - Activated when you run the script WITH arguments.
   - Enables full baseline creation, comparison, exporting,
     timestamp tracking, permission tracking, summary mode,
     and quiet mode.

This hybrid design keeps your original aesthetic while adding
professional-grade forensic capabilities.


2. WHAT THE TOOL CAN DO
------------------------

✔ Hash files using MD5, SHA1, SHA256, or SHA512  
✔ Recursively scan directories  
✔ Ignore common noise directories (node_modules, venv, etc.)  
✔ Create a FILE INTEGRITY BASELINE  
✔ Compare a directory against a baseline  
✔ Detect:
    • Modified files  
    • New files  
    • Deleted files  
    • Timestamp changes  
    • Permission changes  
✔ Export results to:
    • JSON  
    • CSV  
✔ Provide summary-only output  
✔ Quiet mode for automation  


3. MENU MODE (NO ARGUMENTS)
----------------------------

Run:
    python file_integrity_checker.py

You will see:
    • ASCII banner
    • Option to check a single file
    • Option to check an entire directory
    • Option to choose hashing algorithm

This mode behaves exactly like your original tool.


4. ADVANCED CLI MODE (WITH ARGUMENTS)
--------------------------------------

Run:
    python file_integrity_checker.py --help

You will see all available options:

------------------------------------------------------------
BASELINE / COMPARE OPTIONS
------------------------------------------------------------
--baseline DIR
    Create a baseline from the specified directory.

--compare BASELINE.json
    Compare a directory against an existing baseline file.

--dir DIR
    Directory to compare. If omitted, uses the baseline's
    original root directory.

------------------------------------------------------------
HASHING OPTIONS
------------------------------------------------------------
--algo {md5, sha1, sha256, sha512}
    Hashing algorithm to use (default: sha256)

------------------------------------------------------------
OUTPUT OPTIONS
------------------------------------------------------------
--out FILE
    Output path for baseline JSON when using --baseline.

--json-out FILE
    Write comparison results to a JSON file.

--csv-out FILE
    Write comparison results to a CSV file.

--summary
    Show only a summary of results.

--quiet
    Suppress detailed per-file output.

------------------------------------------------------------


5. BASELINE CREATION
---------------------

A baseline is a JSON file containing:
    • File hashes
    • File sizes
    • Modified time (mtime)
    • Created time (ctime)
    • Permissions (mode)
    • Owner/group (uid/gid)
    • Directory root
    • Hashing algorithm used

Create a baseline:
    python file_integrity_checker.py \
        --baseline /path/to/dir \
        --algo sha256 \
        --out baseline.json

If --out is omitted, baseline.json is used automatically.


6. COMPARING AGAINST A BASELINE
-------------------------------

Compare the current state of a directory to a baseline:

    python file_integrity_checker.py \
        --compare baseline.json

Compare a different directory:

    python file_integrity_checker.py \
        --compare baseline.json \
        --dir /new/path/to/check

The tool will detect:
    • unchanged files
    • modified files
    • deleted files
    • new files
    • metadata changes (timestamps, permissions, ownership)


7. OUTPUT MODES
----------------

A) FULL OUTPUT (default)
    Shows every file and its status.

B) SUMMARY MODE
    python file_integrity_checker.py --compare baseline.json --summary

    Example summary:
        unchanged: 120
        modified: 3
        deleted: 1
        new: 2
        meta_changed: 1

C) QUIET MODE
    python file_integrity_checker.py --compare baseline.json --quiet

    Only prints summary unless combined with --summary.

D) JSON EXPORT
    python file_integrity_checker.py \
        --compare baseline.json \
        --json-out results.json

E) CSV EXPORT
    python file_integrity_checker.py \
        --compare baseline.json \
        --csv-out results.csv


8. CSV EXPORT FORMAT
---------------------

Columns:
    path
    status
    old_hash
    new_hash
    old_mtime
    new_mtime
    old_ctime
    new_ctime
    old_mode
    new_mode
    old_uid
    new_uid
    old_gid
    new_gid


9. JSON EXPORT FORMAT
----------------------

[
  {
    "path": "relative/path/to/file",
    "status": "modified",
    "old": { ...metadata... },
    "new": { ...metadata... }
  }
]


10. TYPICAL WORKFLOW
---------------------

Step 1: Create a baseline
    python file_integrity_checker.py --baseline /dir --out baseline.json

Step 2: Later, compare the directory
    python file_integrity_checker.py --compare baseline.json

Step 3: Export results (optional)
    python file_integrity_checker.py \
        --compare baseline.json \
        --json-out results.json \
        --csv-out results.csv

Step 4: Use summary mode for quick triage
    python file_integrity_checker.py --compare baseline.json --summary


11. TROUBLESHOOTING
--------------------

Problem: "Directory does not exist"
Solution:
    Check your path and ensure it is correct.

Problem: "Baseline file not found"
Solution:
    Ensure the JSON file exists and is readable.

Problem: "Permission denied"
Solution:
    Run with appropriate permissions or exclude restricted folders.

Problem: "Ignored by pattern"
Solution:
    The file or folder matches IGNORE_PATTERNS.


12. SUMMARY
-----------
This hybrid File Integrity Checker provides both a user-friendly
menu interface and a powerful CLI mode for forensic-grade
baseline creation and comparison.

It supports hashing, timestamps, permissions, JSON/CSV export,
summary mode, quiet mode, and full automation.

============================================================
END OF DOCUMENT
============================================================
