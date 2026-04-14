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

@monitor("stop")
def announce_stop(event_type, data):
    print("API watchdog offline")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def main():
    monitor_instance = Monitor(crash_safe=True, heartbeat_interval=30)
    monitor_instance.start()
    server = HTTPServer(("127.0.0.1", 8000), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        monitor_instance.stop()

if __name__ == "__main__":
    main()
