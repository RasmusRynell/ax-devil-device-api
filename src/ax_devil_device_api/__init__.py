__version__ = "0.6.5"

from .core.config import DeviceConfig
from .client import Client

__all__ = [
    'Client',
    'DeviceConfig',
] 