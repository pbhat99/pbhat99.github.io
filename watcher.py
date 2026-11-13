import os
import sys
import time
import threading
import http.server
import socketserver
import importlib
import build

PAGES_DIR = "pages"
PORT = 8080

def get_dir_state():
    state = {}
    if not os.path.exists(PAGES_DIR):
        return state
    for root, dirs, files in os.walk(PAGES_DIR):
        for f in files:
            path = os.path.join(root, f)
            try:
                state[path] = os.path.getmtime(path)
            except OSError:
                pass
    return state

def watch_loop():
    print(f"\n[Watcher] 👁️  Actively monitoring '{PAGES_DIR}/' folder...")
    last_state = get_dir_state()
    while True:
        time.sleep(1.2)
        current_state = get_dir_state()
        if current_state != last_state:
            print("[Watcher] ⚡ Detected changes in pages/ folder, rebuilding...")
            try:
                importlib.reload(build)
                build.sync_all()
                print("[Watcher] ✅ Site refreshed successfully!\n")
            except Exception as e:
                print(f"[Watcher] ❌ Error syncing: {e}")
            last_state = current_state

def start_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[Server] 🚀 Serving at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    build.sync_all()
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()
    start_server()
