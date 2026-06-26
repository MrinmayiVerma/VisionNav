"""
Monocular distance estimation using the pinhole camera model.

For a camera with focal length f (in pixels), an object of real height H
(in metres) that appears with a pixel height h is at distance:

        distance = (H * f) / h

This is a well-established approximation that works well when the object
class has a roughly known physical size (a person, a car, a stop sign...).
It needs no second camera and no depth sensor, which is exactly what an
inexpensive, battery-powered wearable device requires.

A one-time focal-length calibration (scripts/calibrate_focal_length.py)
makes the estimate accurate to within a few tens of centimetres at typical
pedestrian ranges, which is sufficient for the proximity bands we use.
"""
from __future__ import annotations

from .config import DistanceConfig
from .types import Detection, Urgency


class DistanceEstimator:
    def __init__(self, config: DistanceConfig):
        self.config = config

    def estimate(self, detection: Detection) -> float:
        """Return estimated distance in metres for a detection."""
        pixel_height = detection.box.height
        if pixel_height <= 0:
            return float("inf")

        real_height = self.config.known_heights_m.get(
            detection.label, self.config.default_height_m
        )
        distance = (real_height * self.config.focal_length_px) / pixel_height
        return round(distance, 2)

    def urgency_for(self, distance_m: float) -> Urgency:
        """Convert a raw distance into a discrete urgency band."""
        if distance_m <= self.config.danger_distance_m:
            return Urgency.DANGER
        if distance_m <= self.config.warning_distance_m:
            return Urgency.WARNING
        if distance_m <= self.config.notice_distance_m:
            return Urgency.NOTICE
        return Urgency.INFO

    def annotate(self, detection: Detection) -> Detection:
        """Fill in distance_m and urgency on a detection (in place) and return it."""
        detection.distance_m = self.estimate(detection)
        detection.urgency = self.urgency_for(detection.distance_m)
        return detection
