"""
Debug overlay rendering.

Draws bounding boxes, labels, distance, and urgency colour on the frame so a
sighted developer / evaluator can see what the system perceives. This is
purely for development and demonstration; on a real headless wearable the
window is disabled (config.show_window = False) and this module is never used.
"""
from __future__ import annotations

from typing import List

import cv2

from .types import Detection, Urgency

_URGENCY_COLORS = {
    Urgency.DANGER: (0, 0, 255),     # red   (BGR)
    Urgency.WARNING: (0, 165, 255),  # orange
    Urgency.NOTICE: (0, 255, 255),   # yellow
    Urgency.INFO: (0, 200, 0),       # green
}


def draw_detections(frame, detections: List[Detection]):
    for det in detections:
        color = _URGENCY_COLORS.get(det.urgency, (200, 200, 200))
        x1, y1, x2, y2 = (int(det.box.x1), int(det.box.y1),
                          int(det.box.x2), int(det.box.y2))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        parts = [det.label]
        if det.zone is not None:
            parts.append(det.zone.value)
        if det.distance_m is not None and det.distance_m != float("inf"):
            parts.append(f"{det.distance_m:.1f}m")
        label = " | ".join(parts)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return frame
