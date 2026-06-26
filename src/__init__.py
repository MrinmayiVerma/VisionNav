"""VisionNav: real-time assistive navigation for visually impaired users."""

from .config import AppConfig, default_config
from .types import (
    Announcement,
    BoundingBox,
    Detection,
    Urgency,
    Zone,
)

__version__ = "1.0.0"

__all__ = [
    "AppConfig",
    "default_config",
    "Announcement",
    "BoundingBox",
    "Detection",
    "Urgency",
    "Zone",
    "__version__",
]
