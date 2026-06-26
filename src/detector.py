"""
Object detection using YOLOv8 (Ultralytics).

The detector is wrapped behind a small, stable interface (`detect(frame)
-> list[Detection]`) so the rest of the pipeline never depends on the
Ultralytics API directly. This makes it trivial to swap in a different
model (e.g. a custom-trained traffic-sign detector) later.
"""
from __future__ import annotations

import logging
from typing import List

import numpy as np

from .config import DetectorConfig
from .types import BoundingBox, Detection

logger = logging.getLogger(__name__)


class ObjectDetector:
    def __init__(self, config: DetectorConfig):
        self.config = config
        self._model = None
        self._names: dict[int, str] = {}

    def load(self) -> "ObjectDetector":
        # Imported lazily so unit tests that don't need the model stay light.
        from ultralytics import YOLO

        logger.info("Loading YOLO weights: %s", self.config.weights)
        self._model = YOLO(self.config.weights)
        self._names = self._model.names
        logger.info("Model loaded with %d classes.", len(self._names))
        return self

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Run inference on one BGR frame and return a list of Detections."""
        if self._model is None:
            raise RuntimeError("Detector not loaded. Call .load() first.")

        results = self._model.predict(
            source=frame,
            conf=self.config.conf_threshold,
            iou=self.config.iou_threshold,
            imgsz=self.config.imgsz,
            classes=self.config.classes_of_interest or None,
            device=self.config.device,
            verbose=False,
        )

        detections: List[Detection] = []
        if not results:
            return detections

        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            label = self._names.get(cls_id, str(cls_id))
            detections.append(
                Detection(
                    label=label,
                    confidence=conf,
                    box=BoundingBox(*xyxy),
                )
            )
        return detections
