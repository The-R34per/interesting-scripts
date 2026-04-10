============================================================
ARTIFACT PACKAGING & REPORT GENERATOR
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
This tool collects, organizes, summarizes, and packages all
artifacts produced by your Cyber Combat toolkit.

It automatically:
    • Scans a source directory for tool outputs
    • Categorizes files (Memory, Network, IOCs, Integrity, etc.)
    • Copies them into a clean folder structure
    • Generates a summary report (.txt or .md)
    • Optionally creates a ZIP archive

This is the final step in your workflow, producing a clean,
professional artifact bundle for submission, handoff, or storage.


2. FEATURES
-----------
✔ Automatic artifact categorization  
✔ Organized output directory  
✔ IOC counting (from JSON files)  
✔ Integrity status counting (modified/new/deleted/etc.)  
✔ Network indicator counting (IPs, domains, URLs)  
✔ TXT or Markdown report generation  
✔ Optional ZIP packaging  
✔ Optional analyst name + notes  
✔ Verbose mode for debugging  
✔ Clean mode to rebuild output folder  


3. BASIC USAGE
---------------

Required:
    --source DIR       Directory containing tool outputs

Optional:
    --dest DIR         Destination folder (default: ./Artifacts)
    --report FILE      Path for report (extension optional)
    --report-format    txt or md (default: txt)
    --zip FILE         Create a ZIP archive of the final output
    --analyst NAME     Add analyst name to report
    --notes FILE       Include notes from a text file
    --clean            Remove destination folder before rebuilding
    --verbose          Show detailed processing output


4. EXAMPLES
-----------

A) Basic run (default TXT report):
    python artifact_packager.py --source ./Outputs

B) Specify destination folder:
    python artifact_packager.py --source ./Outputs --dest ./FinalArtifacts

C) Generate Markdown report:
    python artifact_packager.py --source ./Outputs --report-format md

D) Custom report name:
    python artifact_packager.py --source ./Outputs --report final_report

E) Include analyst name + notes:
    python artifact_packager.py \
        --source ./Outputs \
        --analyst "The_R34PER" \
        --notes notes.txt

F) Create ZIP archive:
    python artifact_packager.py \
        --source ./Outputs \
        --zip artifacts.zip

G) Full example:
    python artifact_packager.py \
        --source ./Outputs \
        --dest ./Artifacts \
        --report artifact_summary \
        --report-format md \
        --zip final_artifacts.zip \
        --analyst "The_R34PER" \
        --notes notes.txt \
        --clean \
        --verbose


5. HOW FILES ARE CATEGORIZED
-----------------------------

The tool automatically sorts files into categories based on
filename patterns:

    Memory:
        memory*, *.dmp, *.raw, memdump*

    Network:
        network*, nmap*, scan*, *.pcap, *.pcapng

    IOCs:
        *ioc*, *iocs*, JSON files containing IOC objects

    Integrity:
        baseline.json, compare_*.json, integrity*

    Persistence:
        persist*, autoruns*, startup*, runkeys*

    Malware:
        malware*, sample*, payload*, *.exe, *.dll, *.scr, *.bin

    Reports:
        *.txt, *.md, *.log, *report*

    Other:
        Anything that does not match the above


6. REPORT GENERATION
---------------------

The tool generates a summary report in either:
    • TXT (default)
    • Markdown (optional)

Report includes:
    • Timestamp
    • Hostname
    • Analyst name (optional)
    • Artifact counts per category
    • Total IOCs found
    • Integrity status counts
    • Network indicator counts
    • Notes section


7. ZIP PACKAGING
-----------------

If --zip is provided, the tool compresses the entire organized
artifact directory into a ZIP file.

Example:
    python artifact_packager.py --source ./Outputs --zip final.zip


8. CLEAN MODE
--------------

Use --clean to delete the destination folder before rebuilding.

Example:
    python artifact_packager.py --source ./Outputs --clean


9. VERBOSE MODE
----------------

Use --verbose to show every file being processed.

Example:
    python artifact_packager.py --source ./Outputs --verbose


10. TYPICAL WORKFLOW
---------------------

Step 1: Run your tools and collect outputs into a folder.
Step 2: Run the Artifact Packager:
        python artifact_packager.py --source ./Outputs
Step 3: Review the generated report.
Step 4: Submit or archive the ZIP (optional).


11. TROUBLESHOOTING
--------------------

Problem: "Source directory does not exist"
Solution:
    Check the path and ensure it is correct.

Problem: "Report not generated"
Solution:
    Ensure you have write permissions to the destination folder.

Problem: "ZIP creation failed"
Solution:
    Ensure the ZIP path is valid and not locked by another program.

Problem: "Notes file not found"
Solution:
    Provide a valid path to a .txt file.


12. SUMMARY
-----------
The Artifact Packaging & Report Generator is the final step in
your Cyber Combat workflow. It organizes all outputs, generates
a clean report, and packages everything into a professional,
ready-to-submit bundle.

============================================================
END OF DOCUMENT
============================================================
