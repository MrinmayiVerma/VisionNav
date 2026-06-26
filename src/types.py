"""
Shared, dependency-free data types passed between pipeline stages.

Keeping these as plain dataclasses (no OpenCV / Torch imports) lets the
business-logic modules be unit-tested without any heavy dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class Zone(str, Enum):
    """Horizontal position of an object relative to the user."""
    LEFT = "left"
    CENTER = "ahead"
    RIGHT = "right"


class Urgency(int, Enum):
    """Proximity-based urgency level. Higher value = more urgent."""
    INFO = 0       # far away, informational only
    NOTICE = 1     # be aware
    WARNING = 2    # caution, getting close
    DANGER = 3     # stop / immediate


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned bounding box in pixel coordinates (x1,y1 = top-left)."""
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class Detection:
    """A single detected object with all derived spatial/semantic metadata."""
    label: str
    confidence: float
    box: BoundingBox
    distance_m: float | None = None
    zone: Zone | None = None
    urgency: Urgency = Urgency.INFO
    priority: float = 0.0


@dataclass
class Announcement:
    """A spoken message produced by the announcer."""
    text: str
    urgency: Urgency


# A frame is just a numpy array; we type it loosely to avoid importing numpy here.
Frame = "numpy.ndarray"
Resolution = Tuple[int, int]  # (width, height)
