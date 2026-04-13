from omniscript import Monitor, monitor
import time

@monitor("start")
def on_start(event_type, data):
    print("CLI task started")

@monitor("heartbeat")
def heartbeat(event_type, data):
    print(f"Still running at {data['readable']}")

@monitor("uncaught-exception")
def crash_alert(event_type, data):
    print(f"Crash: {data['type']} - {data['exception']}")

monitor_instance = Monitor(crash_safe=False, heartbeat_interval=10)
monitor_instance.start()

for i in range(3):
    print(f"Step {i + 1}")
    time.sleep(2)

raise RuntimeError("demo failure")
