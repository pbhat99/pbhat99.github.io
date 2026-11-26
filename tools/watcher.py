import os
import sys

# Ensure working directory is project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.abspath(os.getcwd()) != PROJECT_ROOT:
    os.chdir(PROJECT_ROOT)

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import time
import threading
import http.server
import socketserver
import importlib
import build

WATCH_TARGETS = ("pages", os.path.join("tools", "build.py"), os.path.join("tools", "siteConfig.json"))
PORT = 8080

def get_dir_state():
    state = {}
    for target in WATCH_TARGETS:
        if os.path.isfile(target):
            try:
                state[target] = os.path.getmtime(target)
            except OSError:
                pass
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for f in files:
                    path = os.path.join(root, f)
                    try:
                        state[path] = os.path.getmtime(path)
                    except OSError:
                        pass
    return state

def watch_loop():
    print("\n[Watcher] Actively monitoring pages/ and tools/build.py...")
    last_state = get_dir_state()
    while True:
        time.sleep(1.2)
        current_state = get_dir_state()
        if current_state != last_state:
            print("[Watcher] Detected changes, rebuilding...")
            try:
                importlib.reload(build)
                build.sync_all(convert_webp=False)
                print("[Watcher] ✅ Site refreshed successfully!\n")
            except Exception as e:
                print(f"[Watcher] ❌ Error syncing: {e}")
            last_state = current_state

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Resolve clean extensionless URLs (e.g. /more -> /more.html)
        path_without_query = self.path.split('?')[0].rstrip('/')
        if path_without_query and not os.path.exists(self.translate_path(path_without_query)):
            cand_html = self.translate_path(path_without_query) + ".html"
            if os.path.exists(cand_html):
                query = ("?" + self.path.split('?', 1)[1]) if '?' in self.path else ""
                self.path = path_without_query + ".html" + query
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
        print(f"[Server] 🚀 Serving at http://localhost:{PORT}/ (no-cache enabled)")
        print("[Server] 💡 Press Ctrl+C or close this window to stop the server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] 🛑 Stopping server cleanly...")

if __name__ == "__main__":
    build.sync_all(convert_webp=False)
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()
    start_server()
