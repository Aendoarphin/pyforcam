import http.server
import socketserver
import os
import socket

PORT = 5000
FILE_PATH = os.path.join(os.path.dirname(__file__), "doc", "sample-files", "MA1assets[521].xml")

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/sample-files":
            try:
                with open(FILE_PATH, "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "application/xml")
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found.")
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving file at http://{ip_address}:{PORT}/sample-files")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

httpd.server_close()
print("Server stopped.")
