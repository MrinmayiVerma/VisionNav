"""
Central configuration for the VisionNav assistive navigation system.

All tunable parameters live here so that the rest of the codebase reads
cleanly and a single file can be edited to re-tune the system for a new
camera, environment, or user preference.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# --------------------------------------------------------------------------- #
#  Camera / capture configuration
# --------------------------------------------------------------------------- #
@dataclass
class CameraConfig:
    source: int | str = 0          # 0 = default webcam, or a path to a video file
    width: int = 640               # capture width  (px)
    height: int = 480              # capture height (px)
    fps_limit: int = 30            # cap processing rate to save CPU/battery
    flip_horizontal: bool = False  # mirror image (useful for front cameras)


# --------------------------------------------------------------------------- #
#  Detection model configuration
# --------------------------------------------------------------------------- #
@dataclass
class DetectorConfig:
    weights: str = "yolov8n.pt"    # nano model: best speed for edge devices
    conf_threshold: float = 0.40   # minimum detection confidence
    iou_threshold: float = 0.45    # NMS IoU threshold
    imgsz: int = 416               # inference resolution (smaller = faster)
    device: str = "cpu"            # "cpu", "cuda", or "mps"
    # COCO class ids that matter for a walking pedestrian. Restricting the
    # classes reduces noise and speeds up post-processing.
    classes_of_interest: List[int] = field(default_factory=lambda: [
        0,   # person
        1,   # bicycle
        2,   # car
        3,   # motorcycle
        5,   # bus
        7,   # truck
        9,   # traffic light
        10,  # fire hydrant
        11,  # stop sign
        13,  # bench
        15,  # cat
        16,  # dog
        56,  # chair
        57,  # couch
        59,  # potted plant
        60,  # dining table
    ])


# --------------------------------------------------------------------------- #
#  Distance estimation configuration (monocular pinhole model)
# --------------------------------------------------------------------------- #
@dataclass
class DistanceConfig:
    # Focal length in pixels. Obtain via one-time calibration
    # (see scripts/calibrate_focal_length.py). The default is a reasonable
    # value for a 640px-wide phone/webcam.
    focal_length_px: float = 600.0

    # Average real-world height (in metres) of each object class. Distance is
    # estimated from the apparent pixel height using the pinhole model.
    known_heights_m: Dict[str, float] = field(default_factory=lambda: {
        "person": 1.70,
        "bicycle": 1.10,
        "car": 1.50,
        "motorcycle": 1.20,
        "bus": 3.20,
        "truck": 3.50,
        "traffic light": 0.75,
        "fire hydrant": 0.75,
        "stop sign": 0.75,
        "bench": 0.90,
        "cat": 0.30,
        "dog": 0.55,
        "chair": 0.90,
        "couch": 0.85,
        "potted plant": 0.50,
        "dining table": 0.75,
    })
    default_height_m: float = 1.0  # fallback for unknown classes

    # Proximity bands (in metres) used to convert a raw distance into a
    # human-friendly urgency level.
    danger_distance_m: float = 1.5     # "stop" zone
    warning_distance_m: float = 3.0    # "caution" zone
    notice_distance_m: float = 6.0     # "be aware" zone


# --------------------------------------------------------------------------- #
#  Spatial reasoning configuration
# --------------------------------------------------------------------------- #
@dataclass
class SpatialConfig:
    # Fractions of frame width that define the left / centre / right zones.
    # e.g. left = [0, 0.38), centre = [0.38, 0.62), right = [0.62, 1.0]
    left_boundary: float = 0.38
    right_boundary: float = 0.62


# --------------------------------------------------------------------------- #
#  Announcement / prioritisation configuration
# --------------------------------------------------------------------------- #
@dataclass
class AnnouncerConfig:
    # Per-class base priority (higher = more important to announce).
    class_priority: Dict[str, int] = field(default_factory=lambda: {
        "stop sign": 100,
        "traffic light": 95,
        "car": 90,
        "bus": 90,
        "truck": 90,
        "motorcycle": 88,
        "bicycle": 80,
        "person": 70,
        "dog": 60,
        "cat": 50,
        "fire hydrant": 55,
        "bench": 45,
        "potted plant": 40,
        "chair": 40,
        "couch": 40,
        "dining table": 40,
    })
    default_priority: int = 30

    # Do not repeat the same (class, zone) announcement more often than this.
    cooldown_seconds: float = 4.0
    # Maximum number of objects announced in a single spoken sentence.
    max_objects_per_announcement: int = 2
    # Minimum gap between two consecutive spoken sentences.
    min_speech_gap_seconds: float = 1.5


# --------------------------------------------------------------------------- #
#  Text-to-speech configuration
# --------------------------------------------------------------------------- #
@dataclass
class TTSConfig:
    rate: int = 165          # words per minute
    volume: float = 1.0      # 0.0 - 1.0
    voice_id: str | None = None  # platform voice id; None = system default


# --------------------------------------------------------------------------- #
#  Top-level application configuration
# --------------------------------------------------------------------------- #
@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    distance: DistanceConfig = field(default_factory=DistanceConfig)
    spatial: SpatialConfig = field(default_factory=SpatialConfig)
    announcer: AnnouncerConfig = field(default_factory=AnnouncerConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)

    show_window: bool = True   # draw an annotated debug window (disable on headless devices)
    log_level: str = "INFO"


def default_config() -> AppConfig:
    """Return a fresh AppConfig populated with sensible defaults."""
    return AppConfig()
