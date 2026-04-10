============================================================
LATERAL MOVEMENT PATH VISUALIZER
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Lateral Movement Path Visualizer is a
read-only tool that models potential lateral movement paths
between hosts based on user accounts and shared resources.

It does NOT:
- Scan networks
- Probe hosts
- Access shares
- Perform authentication

Instead, it uses *provided input files* to infer:
- Shared user accounts across hosts
- Shares that could be reachable
- Host-to-host relationships
- Potential pivot paths

This tool is ideal for Cyber Combat scenarios where you must
analyze environment structure without touching the network.


2. REQUIRED INPUT FILES
------------------------

You may provide any combination of:
- Hosts list
- User mappings
- Share mappings

A) hosts.txt
------------
One host per line:
    HOSTA
    HOSTB
    10.0.0.5

B) users.txt
------------
Format:
    HOST,USER

Example:
    DC01,alice
    WEB01,alice
    DB01,bob

This allows the tool to detect:
- Shared users across hosts
- Potential credential reuse paths

C) shares.txt
-------------
Format:
    HOST,SHARE,ACCESS

Example:
    FILESRV,Public,read
    APP01,Admin$,admin-only

This allows the tool to detect:
- File-based pivot opportunities


3. HOW TO RUN THE TOOL
-----------------------

A) Basic usage:

    python lateral_path_visualizer.py --hosts hosts.txt --users users.txt --shares shares.txt

B) Summary-only mode:

    python lateral_path_visualizer.py --hosts hosts.txt --users users.txt --summary-only

C) Save full report to a file:

    python lateral_path_visualizer.py --hosts hosts.txt --users users.txt -o report.txt

D) Export edges for graph tools:

    python lateral_path_visualizer.py --hosts hosts.txt --users users.txt --edges edges.csv


4. WHAT THE TOOL DOES
----------------------

A) Shared User Analysis
-----------------------
If the same user appears on multiple hosts, the tool infers:

    HOSTA -> HOSTB via shared user 'alice'

This models potential credential reuse paths.

B) Share-Based Analysis
-----------------------
If a host exposes a share, the tool models:

    HOSTX -> SHARE_HOST via share 'Public (read)'

This represents a potential file-based pivot.

C) Graph Construction
---------------------
The tool builds:
- A list of edges (host-to-host relationships)
- An adjacency map (graph-centric view)
- A path list (path-centric view)

D) Output Sections
------------------
1. Summary
2. Path-Centric View
3. Graph-Centric View (Adjacency)
4. Optional CSV edge list


5. OUTPUT FORMAT
-----------------

A) Summary Example:
-------------------
    ========= Summary =========
    Total hosts: 5
    Total users (unique): 3
    Total shares: 4
    Total inferred lateral paths: 12

B) Path-Centric Example:
------------------------
    ========= Inferred Lateral Movement Paths =========
    DC01 -> WEB01 via shared user 'alice'
    WEB01 -> DC01 via shared user 'alice'
    APP01 -> FILESRV via share 'Public (read)'

C) Graph-Centric Example:
-------------------------
    ========= Host Adjacency =========
    DC01:
      -> WEB01 (shared user: alice)

    WEB01:
      -> DC01 (shared user: alice)

    APP01:
      -> FILESRV (share: Public (read))


6. TYPICAL COMPETITION WORKFLOW
-------------------------------

Step 1: Gather host, user, and share lists  
Step 2: Run the visualizer  
Step 3: Review shared-user paths  
Step 4: Review share-based paths  
Step 5: Export edges for graph tools if needed  
Step 6: Use results to answer Cyber Combat questions  


7. TROUBLESHOOTING
--------------------

Problem: "No input data provided"
Solution:
    Provide at least one of:
        --hosts
        --users
        --shares

Problem: Empty adjacency or path list
Solution:
    Ensure your input files contain overlapping users or shares.

Problem: CSV not writing
Solution:
    Ensure the directory is writable.


8. SUMMARY
-----------
The Lateral Movement Path Visualizer provides a safe,
read-only analysis of potential lateral movement paths based
on shared users and shared resources.

It produces:
- A summary
- A path-centric view
- A graph-centric adjacency view
- Optional CSV edge export

This tool is designed for Cyber Combat environments where
mapping potential pivot paths is essential.

============================================================
END OF DOCUMENT
============================================================
