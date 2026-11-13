import os
import sys
import time
import threading
import http.server
import socketserver
from build import sync_all

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
    print("  • Drop an image in 'pages/02_vfx-works/projects/' -> auto-adds card to VFX Works!")
    print("  • Replace 'pages/01_home/background.jpg' -> auto-updates homepage background!")
    print("  • Drop photos in 'pages/04_photography/gallery/' -> auto-adds to gallery!")
    print("  • Edit 'pages/01_home/content.json' -> auto-updates name/designation/tagline!\n")
    
    last_state = get_dir_state()
    while True:
        time.sleep(1.2)
        current_state = get_dir_state()
        if current_state != last_state:
            # Detect what changed
            added = set(current_state.keys()) - set(last_state.keys())
            removed = set(last_state.keys()) - set(current_state.keys())
            modified = {k for k in current_state if k in last_state and current_state[k] != last_state[k]}

            for f in added:
                print(f"[Watcher] ➕ New file detected: {f}")
            for f in modified:
                print(f"[Watcher] ✏️ File modified: {f}")
            for f in removed:
                print(f"[Watcher] 🗑️ File removed: {f}")

            print("[Watcher] ⚡ Triggering automatic page rebuild...")
            try:
                sync_all()
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
    # First do a fresh sync
    sync_all()

    # Start watcher in background thread
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()

    # Start HTTP server
    start_server()
