from omniscript import Monitor

def on_build(event_type, data):
    print(f"build event: {data}")

def on_deploy(event_type, data):
    print(f"deploy event: {data}")

def main():
    monitor_instance = Monitor()
    monitor_instance.on_event("build", on_build)
    monitor_instance.on_event("deploy", on_deploy)
    monitor_instance.start()

    monitor_instance.dispatch_event("build", {"status": "success", "target": "wheel"})
    monitor_instance.dispatch_event("deploy", {"environment": "staging"})

if __name__ == "__main__":
    main()
