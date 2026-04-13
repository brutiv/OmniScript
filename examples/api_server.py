from omniscript import Monitor, monitor
from http.server import BaseHTTPRequestHandler, HTTPServer

@monitor("start")
def announce_start(event_type, data):
    print("API watchdog online")

@monitor("heartbeat")
def heartbeat(event_type, data):
    print(f"watchdog heartbeat {data['readable']}")

@monitor("error")
def report_error(event_type, data):
    print(f"watchdog error: {data['event_type']} -> {data['exception']}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

Monitor(crash_safe=True, heartbeat_interval=30).start()
server = HTTPServer(("127.0.0.1", 8000), Handler)
server.serve_forever()
