# OmniScript

![OmniScript Logo](https://i.ibb.co/7x9DYkCB/O-1.png)

Notice: OmniScript is still in v0.0.01, this isn't even close to the full version.

OmniScript is a lightweight event-monitoring library for Python scripts. It gives your program a simple way to register callbacks for lifecycle and runtime events like `start`, `heartbeat`, `error`, `stop`, and custom events you define yourself.

It is designed for developers who want a clean, familiar pattern for reacting to what their script is doing, similar in spirit to event-driven libraries like `discord.py`.

## What OmniScript does

OmniScript runs a background daemon thread that monitors your script without blocking the main thread. While your program keeps doing its own work, OmniScript can emit events on a schedule or when important runtime conditions happen.

It supports:

- A background heartbeat every 60 seconds by default.
- Event registration with `on_event(...)`.
- A decorator-based API with `@monitor("event_name")`.
- Safe callback execution so one failing handler does not break the monitor.
- Automatic `stop` handling on process exit.
- Optional uncaught exception handling.
- Custom events that you can trigger yourself.

## Installation

```bash
pip install omniscript
```

If you are developing locally:

```bash
pip install -e .
```

## Basic idea

You create a monitor, register event handlers, then start it.

```python
from omniscript import Monitor, monitor

monitor_instance = Monitor()

@monitor("start")
def on_start(event_type, data):
    print("Monitor started")

@monitor("heartbeat")
def on_heartbeat(event_type, data):
    print(f"Heartbeat at {data['readable']}")

monitor_instance.start()
```

The main script keeps running while OmniScript handles events in the background.

## Event types

OmniScript includes these built-in events:

- `start`  
  Fired when the monitor starts.

- `heartbeat`  
  Fired on the configured interval, defaulting to 60 seconds.

- `error`  
  Fired when a registered callback raises an exception.

- `stop`  
  Fired when the monitor stops or the process exits.

- `uncaught-exception`  
  Fired when the monitor is configured to observe uncaught exceptions.

- `shutdown-signal`  
  Fired when the process receives signals like `SIGINT` or `SIGTERM`.

You can also define your own custom event names.

## Clean decorator API

OmniScript supports a decorator style that keeps handlers close to the code they belong to.

```python
from omniscript import monitor

@monitor("heartbeat")
def send_status(event_type, data):
    print(data["readable"])
```

This registers the function as a handler for the `heartbeat` event.

## Manual registration

If you prefer explicit wiring, use `on_event(...)`.

```python
from omniscript import Monitor

monitor_instance = Monitor()

def handle_error(event_type, data):
    print(data["exception"])

monitor_instance.on_event("error", handle_error)
monitor_instance.start()
```

This is useful when you want to register handlers dynamically.

## Example: Discord webhook heartbeat

```python
from omniscript import Monitor, monitor
import time

@monitor("start")
def on_start(event_type, data):
    print(f"Started with pid {data['pid']}")

@monitor("heartbeat")
def heartbeat(event_type, data):
    print(f"Heartbeat at {data['readable']}")

@monitor("error")
def on_error(event_type, data):
    print(f"Error in {data['event_type']}: {data['exception']}")

monitor_instance = Monitor(crash_safe=True, heartbeat_interval=60)
monitor_instance.start()

while True:
    time.sleep(1)
```

## How it works

OmniScript uses a singleton-style monitor object, so repeated calls to `Monitor()` refer to the same underlying monitor instance. This makes it easy to register handlers from different parts of your program without passing a monitor object around everywhere.

When the monitor is started:

1. A daemon thread begins running in the background.
2. The thread checks whether it is time to emit a heartbeat.
3. Any registered handlers for that event are called.
4. If a handler fails, OmniScript logs the error and continues.
5. When the process ends, `stop` is triggered automatically.

## Crash-safe mode

OmniScript supports a `crash_safe` option.

```python
monitor_instance = Monitor(crash_safe=True)
monitor_instance.start()
```

When enabled, OmniScript uses its exception hook behavior to report uncaught exceptions through the monitor instead of letting them go through the default flow.

This is useful when you want alerting or logging behavior attached to crashes. It does not replace normal application error handling, and it does not change how Python itself works for exceptions that are not managed by your code.

## Custom events

You can define and trigger your own events.

```python
from omniscript import Monitor

monitor_instance = Monitor()

def on_build(event_type, data):
    print(f"Build status: {data['status']}")

monitor_instance.on_event("build", on_build)
monitor_instance.start()
monitor_instance._dispatch_event("build", {"status": "success"})
```

Custom events are useful for application-specific signals like:

- `build`
- `deploy`
- `sync`
- `backup`
- `task-finished`

## API reference

### `Monitor(heartbeat_interval=60.0, crash_safe=False)`

Creates or returns the monitor instance.

Parameters:

- `heartbeat_interval`: Number of seconds between heartbeat events.
- `crash_safe`: Enables safe exception-hook behavior.

### `Monitor.on_event(event_type, callback)`

Registers a callback for a named event.

The callback receives:

```python
callback(event_type, data)
```

### `Monitor.start()`

Starts the background thread and begins emitting events.

### `Monitor.stop()`

Stops the background thread and emits a final `stop` event.

### `@monitor("event_name")`

Decorator that registers a function as a handler for the given event.

## Expected callback signature

All handlers should accept two arguments:

```python
def handler(event_type, data):
    ...
```

Example:

```python
def on_heartbeat(event_type, data):
    print(event_type)
    print(data)
```

## Project structure

```bash
OmniScript/
├── omniscript/
│   ├── __init__.py
│   ├── core.py
│   └── decorator.py
├── examples/
│   ├── api_server_watchdog.py
│   ├── background_worker.py
│   ├── cli_task_runner.py
│   ├── custom_event_bus.py
│   └── discord_heartbeat.py
└── README.md
```

## Status

OmniScript is currently early-stage software. The core ideas are stable, but the API may evolve as the library grows.

---

OmniScript is built for developers who want a small, event-driven layer for scripts, services, bots, and background workers.
