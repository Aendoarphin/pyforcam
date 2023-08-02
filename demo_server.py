import http.server
import socketserver
import os

PORT = 8000
FILE_PATH = os.path.join(os.path.dirname(__file__), "doc", "sample-files", "index.xml")

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
    print(f"Serving file at http://192.168.1.249:{PORT}/sample-files")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

httpd.server_close()
print("Server stopped.")
