============================================================
IOC AGGREGATOR & EXPORTER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The IOC Aggregator & Exporter is a centralized tool for
collecting, normalizing, deduplicating, and exporting
Indicators of Compromise (IOCs) from multiple sources.

It supports:
    • Free-form text extraction (regex-based)
    • JSON IOC files (list-of-objects format)
    • CSV IOC files (type,value,source)
    • Optional labeling for source tracking
    • Filtering by IOC type
    • Export to TEXT, CSV, and JSON

This tool is 100% read-only and competition-safe.


2. SUPPORTED IOC TYPES
-----------------------
The tool recognizes the following IOC categories:

    • hash
    • ip
    • domain
    • url
    • file
    • registry

All values are normalized and deduplicated automatically.


3. INPUT FORMATS
-----------------

A) TEXT FILES
--------------
Use:
    --from-text FILE

The tool extracts IOCs using regex patterns for:
    • IPs
    • Hashes (MD5/SHA1/SHA256)
    • Domains
    • URLs
    • File paths
    • Registry keys

Example:
    python ioc_aggregator.py --from-text scan_output.txt


B) JSON FILES (PRIMARY FORMAT)
-------------------------------
Use:
    --from-json FILE

Expected structure:
[
  { "type": "hash", "value": "..." },
  { "type": "ip", "value": "1.2.3.4" },
  { "type": "domain", "value": "malicious.com" }
]

Example:
    python ioc_aggregator.py --from-json malware_iocs.json


C) CSV FILES
-------------
Use:
    --from-csv FILE

Expected format:
    type,value,source

Example:
    python ioc_aggregator.py --from-csv manual_iocs.csv


4. LABELING INPUT SOURCES
--------------------------
Use:
    --label "Memory Analyzer"

This tag is added to all IOCs collected during this run.

Example:
    python ioc_aggregator.py --from-text log.txt --label "Round 2"


5. OPTIONAL FILTERS
--------------------

A) Filter by IOC type:
    --only hashes
    --only ips
    --only domains
    --only urls
    --only files
    --only registry

Example:
    python ioc_aggregator.py --from-json iocs.json --only hashes

B) Summary only:
    --summary-only

Example:
    python ioc_aggregator.py --from-text logs.txt --summary-only


6. OUTPUT OPTIONS
------------------

A) Export to TEXT:
    --out-text all_iocs.txt

B) Export to CSV:
    --out-csv all_iocs.csv

C) Export to JSON:
    --out-json all_iocs.json

You may use any combination of these.


7. FULL EXAMPLE COMMAND
------------------------

python ioc_aggregator.py \
    --from-text net_scan.txt \
    --from-json malware_output.json \
    --from-csv manual_iocs.csv \
    --label "Round 3" \
    --only hashes \
    --out-json final_hashes.json


8. OUTPUT STRUCTURE
--------------------

A) Console Summary:
    ========= IOC Summary =========
    Hashes: 12
    IPs: 5
    Domains: 3
    URLs: 4
    Files: 9
    Registry: 2

B) Detailed Listing (unless --summary-only):
    ========= Hashes =========
    <hash1>
    <hash2>
    ...

    ========= IPs =========
    1.2.3.4
    5.6.7.8
    ...

C) JSON Export:
[
  {
    "type": "hash",
    "value": "abcd1234...",
    "sources": ["Round 3:net_scan.txt"]
  }
]


9. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Run your tools (network, memory, malware, persistence).  
Step 2: Feed their outputs into the IOC Aggregator.  
Step 3: Apply filters if needed (e.g., only hashes).  
Step 4: Export to JSON/TXT/CSV.  
Step 5: Use the final IOC list for Cyber Combat answers.  


10. TROUBLESHOOTING
--------------------

Problem: "No input files provided"
Solution:
    Provide at least one:
        --from-text
        --from-json
        --from-csv

Problem: "JSON must be a list of IOC objects"
Solution:
    Ensure your JSON matches the required format.

Problem: Filters return nothing
Solution:
    Check spelling and ensure the IOC type exists.


11. SUMMARY
-----------
The IOC Aggregator & Exporter unifies all your indicators
into a single, clean, deduplicated dataset. It supports
multiple input formats, optional labeling, filtering, and
exporting to multiple formats.

This tool is designed to be the final IOC hub for your
Cyber Combat toolkit.

============================================================
END OF DOCUMENT
============================================================
