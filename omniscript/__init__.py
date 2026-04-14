"""
OmniScript: Background monitoring for Python.
"""

from .core import Monitor
from .decorator import monitor

__version__ = "0.0.2"
__all__ = ["Monitor", "monitor"]
