"""
Hardware-free demonstration of the VisionNav decision pipeline.

This simulates a sequence of detection frames (as if YOLO had produced them)
and prints exactly what the system would announce. It lets an evaluator see
the distance estimation, spatial mapping, prioritisation, and cooldown logic
working end-to-end WITHOUT a camera, GPU, or speakers.

Run:  python scripts/demo_offline.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.announcer import Announcer
from src.config import default_config
from src.distance import DistanceEstimator
from src.spatial import SpatialMapper
from src.types import BoundingBox, Detection


def make(label, x_center, pixel_height, frame_w=640):
    """Build a synthetic detection given a label, horizontal centre, and size."""
    half = 30
    return Detection(
        label=label,
        confidence=0.9,
        box=BoundingBox(x_center - half, 240 - pixel_height / 2,
                        x_center + half, 240 + pixel_height / 2),
    )


# A scripted scene: each list is one "frame" of detections.
SCENES = [
    [make("person", 320, 120)],                          # person far ahead
    [make("person", 320, 300)],                          # person now very close, centre
    [make("car", 80, 90), make("bicycle", 560, 70)],     # car left, bike right (both far)
    [make("car", 320, 400)],                             # car right in front -> DANGER
    [make("stop sign", 300, 110), make("person", 500, 80)],
    [make("dog", 320, 200)],
]


def main():
    cfg = default_config()
    cfg.announcer.min_speech_gap_seconds = 0.0  # speed up the demo
    distance = DistanceEstimator(cfg.distance)
    spatial = SpatialMapper(cfg.spatial, frame_width=cfg.camera.width)
    announcer = Announcer(cfg.announcer)

    print("=" * 64)
    print(" VisionNav — offline decision pipeline demo")
    print("=" * 64)

    for i, scene in enumerate(SCENES, 1):
        for det in scene:
            distance.annotate(det)
            spatial.annotate(det)

        summary = ", ".join(
            f"{d.label}({d.zone.value}, {d.distance_m:.1f}m, {d.urgency.name})"
            for d in scene
        )
        print(f"\nFrame {i}: {summary}")

        announcement = announcer.build(scene)
        if announcement:
            print(f"   >> SPEAK [{announcement.urgency.name}]: \"{announcement.text}\"")
        else:
            print("   >> (silent)")
        time.sleep(0.3)

    print("\nDone.")


if __name__ == "__main__":
    main()
