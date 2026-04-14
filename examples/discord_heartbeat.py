from omniscript import Monitor, monitor
import time

@monitor("start")
def on_start(event_type, data):
    print(f"Started with pid {data['pid']}")

@monitor("heartbeat")
def send_heartbeat(event_type, data):
    print(f"Heartbeat at {data['readable']}")

@monitor("error")
def on_error(event_type, data):
    print(f"Error in {data['event_type']}: {data['exception']}")

@monitor("stop")
def on_stop(event_type, data):
    print("Stopped")

monitor = Monitor(crash_safe=True, heartbeat_interval=60)

try:
    monitor.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
