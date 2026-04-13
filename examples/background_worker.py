from omniscript import Monitor, monitor
import time

@monitor("heartbeat")
def worker_heartbeat(event_type, data):
    print(f"worker alive: {data['readable']}")

@monitor("stop")
def worker_stopped(event_type, data):
    print("worker stopped")

monitor_instance = Monitor(crash_safe=True, heartbeat_interval=5)
monitor_instance.start()

try:
    while True:
        print("doing work")
        time.sleep(1)
except KeyboardInterrupt:
    monitor_instance.stop()
