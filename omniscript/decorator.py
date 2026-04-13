from typing import Any, Callable
from .core import Monitor


class monitor:
    """Initialize a monitor with the given event type.

    This sets up the monitor to later register functions for the specified
    event when the instance is used as a decorator.

    Args:
        event_type: The name or identifier of the event to monitor.

    Usage:
        @monitor("heartbeat")
        async def my_callback(event_type, data):
            ...
    """

    def __init__(self, event_type: str):
        self.event_type = event_type

    def __call__(self, fn: Callable[[str, Any], None]) -> Callable[[str, Any], None]:
        Monitor().on_event(self.event_type, fn)
        return fn
