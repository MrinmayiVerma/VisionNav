"""
Spatial reasoning: map a detection's horizontal position to a human-friendly
direction (left / ahead / right).

Telling a user "person ahead" vs "person on your right" is far more useful
than a raw bounding box, and it is cheap to compute: we just look at where
the box centre falls along the width of the frame.
"""
from __future__ import annotations

from .config import SpatialConfig
from .types import Detection, Zone


class SpatialMapper:
    def __init__(self, config: SpatialConfig, frame_width: int):
        self.config = config
        self.frame_width = max(1, frame_width)

    def zone_for(self, detection: Detection) -> Zone:
        fraction = detection.box.center_x / self.frame_width
        if fraction < self.config.left_boundary:
            return Zone.LEFT
        if fraction > self.config.right_boundary:
            return Zone.RIGHT
        return Zone.CENTER

    def annotate(self, detection: Detection) -> Detection:
        detection.zone = self.zone_for(detection)
        return detection
