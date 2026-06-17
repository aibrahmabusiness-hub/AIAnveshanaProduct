import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
ROOT = Path(__file__).resolve().parent

class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve static files from frontend directory
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path == '' or path == '/':
            path = '/index.html'
        elif path in ['/login', '/signup', '/project']:
            path = f'{path}.html'
        else:
            # fallback to .html for route paths without extension
            if not os.path.splitext(path)[1]:
                candidate = path + '.html'
                candidate_path = ROOT / candidate.lstrip('/')
                if candidate_path.exists():
                    path = candidate
        return str(ROOT / path.lstrip('/'))

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(ROOT)
    Handler = SPARequestHandler
    with socketserver.TCPServer(('0.0.0.0', PORT), Handler) as httpd:
        print(f'Serving frontend from {ROOT} at http://localhost:{PORT}')
        httpd.serve_forever()
