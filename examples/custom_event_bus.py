from omniscript import Monitor

monitor_instance = Monitor()

def on_build(event_type, data):
    print(f"build event: {data}")

def on_deploy(event_type, data):
    print(f"deploy event: {data}")

monitor_instance.on_event("build", on_build)
monitor_instance.on_event("deploy", on_deploy)
monitor_instance.start()
monitor_instance._dispatch_event("build", {"status": "success", "target": "wheel"})
monitor_instance._dispatch_event("deploy", {"environment": "staging"})
