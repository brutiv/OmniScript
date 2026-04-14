from omniscript import Monitor, monitor
import time

@monitor("start")
def worker_started(event_type, data):
    print(f"worker started with pid {data['pid']}")

@monitor("heartbeat")
def worker_heartbeat(event_type, data):
    print(f"worker alive: {data['readable']}")

@monitor("error")
def worker_error(event_type, data):
    print(f"worker error in {data['event_type']}: {data['exception']}")

@monitor("stop")
def worker_stopped(event_type, data):
    print("worker stopped")

def main():
    monitor_instance = Monitor(crash_safe=True, heartbeat_interval=5)
    monitor_instance.start()

    try:
        while True:
            print("doing work")
            time.sleep(1)
    except KeyboardInterrupt:
        monitor_instance.stop()

if __name__ == "__main__":
    main()
