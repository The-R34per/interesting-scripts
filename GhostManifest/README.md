# GhostManifest

GhostManifest is a lightweight Python-based system state collection and transfer tool designed for controlled. It gathers specified files or directories from a target system, packages them into a ZIP archive, and securely posts the archive to a designated server endpoint for analysis or scoring.

This tool was built for educational purposes only. The author is not responsable for any actions that a user may take using this code.

---

## Features

- Collects files or directories from a target system
- Automatically generates a ZIP archive of collected data
- Sends the archive to a remote server via HTTP POST
- Includes a minimal Python server for receiving and storing uploads
- Cross-platform compatibility (Windows, macOS, Linux)
- No external dependencies beyond Python standard libraries

---

## Usage


### Client (GhostManifest.py)

(OPTIONAL) Change values at the beginning of the file (values like max file size, max files to extract, etc.)

1. Configure the target directory or files inside the script.
2. Set the server URL where the ZIP archive will be uploaded.
3. Run the script

### Server (ManifestServer.py)
1. Start the server to listen for incoming uploads

### NOTE
1. The Client side (GhostManifest.py) is meant to be run on the victim's computer, while the Server side (ManifestServer.py) is meant to run on the attack's computer.
2. Run the server prior to running the client, this will allow you to change the URL of the server before trying to exfiltrate data.

---

## How to Run

How to run Client (GhostManifest.py)
```bash
python GhostManifest.py
```

How to run Server
```bash
python ManifestServer.py
```
