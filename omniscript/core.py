import sys
import os
import signal
import asyncio
import inspect
import threading
import time
import atexit
import logging
from typing import List, Any, Callable
from datetime import datetime


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Monitor:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, heartbeat_interval: float = 60.0, crash_safe: bool = False):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._running = False
            self._thread = None
            self._event_registry = {
                "start": [],
                "heartbeat": [],
                "error": [],
                "stop": [],
            }
            self._loop = None
            self._async_mode = False
        self._heartbeat_interval = heartbeat_interval
        self.crash_safe = crash_safe

    def on_event(self, event_type: str, callback: Callable[[str, Any], None]) -> None:
        if event_type not in self._event_registry:
            self._event_registry[event_type] = []
        self._event_registry[event_type].append(callback)

    def start(self) -> None:
        if self._running:
            logger.warning("Monitor is already running.")
            return

        self._original_excepthook = sys.excepthook

        if self.crash_safe:
            sys.excepthook = self._safe_excepthook
        else:
            sys.excepthook = self._crashing_excepthook

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._dispatch_event("start", {"pid": os.getpid()})

    async def start_async(self) -> None:
        if self._running:
            logger.warning("Monitor is already running.")
            return

        self._running = True
        self._async_mode = True
        self._install_hooks()
        self._loop = asyncio.get_running_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        await self._dispatch_event_async("start", {"pid": os.getpid()})

    def stop(self) -> None:
        if not self._running:
            return
        if hasattr(self, "_original_excepthook"):
            sys.excepthook = self._original_excepthook
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self._dispatch_event("stop", None)

    async def stop_async(self) -> None:
        if not self._running:
            return
        self._running = False
        self._restore_hooks()
        await self._dispatch_event_async("stop", None)

    def _run(self) -> None:
        last_heartbeat = time.time()
        while self._running:
            now = time.time()
            if now - last_heartbeat >= self._heartbeat_interval:
                last_heartbeat = now
                readable_time = datetime.fromtimestamp(now).isoformat()
                payload = {
                    "timestamp": now,
                    "readable": readable_time
                }
                if self._async_mode and self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self._dispatch_event_async("heartbeat", payload),
                        self._loop,
                    )
                else:
                    self._dispatch_event("heartbeat", payload)
            time.sleep(0.1)

    def _safe_excepthook(self, exc_type, exc_value, exc_traceback):
        self._dispatch_event("uncaught-exception", {
            "exception": exc_value,
            "type": exc_type.__name__,
            "traceback": exc_traceback
        })
        logger.error("Swallowed %s: %s", exc_type.__name__, exc_value, exc_info=exc_traceback)

    def _crashing_excepthook(self, exc_type, exc_value, exc_traceback):
        self._dispatch_event("uncaught-exception", {
            "exception": exc_value,
            "type": exc_type.__name__,
            "traceback": exc_traceback,
        })
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)

    def _dispatch_event(self, event_type: str, data: Any) -> None:
        callbacks = self._event_registry.get(event_type, [])
        for cb in callbacks:
            try:
                result = cb(event_type, data)
                if inspect.isawaitable(result):
                    if self._loop and self._loop.is_running():
                        asyncio.run_coroutine_threadsafe(result, self._loop)
                    else:
                        asyncio.run(result)
            except Exception as exc:
                logger.error(
                    "Error in callback for event: '%s': %s: %s",
                    event_type,
                    type(exc).__name__,
                    exc,
                    exc_info=True,
                )
                try:
                    self._dispatch_event(
                        "error", {"event_type": event_type, "exception": exc}
                    )
                except Exception:
                    logger.error("Error in 'error' event handler.", exc_info=True)

    async def _dispatch_event_async(self, event_type: str, data: Any) -> None:
        callbacks = list(self._event_registry.get(event_type, []))
        for cb in callbacks:
            try:
                result = cb(event_type, data)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                logger.error(
                    "Error in callback for event: '%s': %s: %s",
                    event_type,
                    type(exc).__name__,
                    exc,
                    exc_info=True
                )
                try:
                    await self._dispatch_event_async(
                        "error", {"event_type": event_type, "exception": exc}
                    )
                except Exception:
                    logger.error("Error in 'error' event handler.", exc_info=True)

    def _signal_handler(self, signum, frame):
        if self._async_mode and self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._dispatch_event_async("shutdown-signal", {"signal": signum}),
                self._loop,
            )
            asyncio.run_coroutine_threadsafe(self.stop_async(), self._loop)
        else:
            self._dispatch_event("shutdown-signal", {"signal": signum})
            self.stop()


def _on_process_exit():
    try:
        Monitor().stop()
    except Exception as exc:
        logger.error("Error during atexit cleanup: %s", exc, exc_info=True)
