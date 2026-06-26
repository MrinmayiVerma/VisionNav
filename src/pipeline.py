"""
Pipeline orchestrator.

Wires the independent stages into a single per-frame processing function:

    frame -> detect -> distance -> spatial -> rank/announce -> speak

Each stage is injected, so the pipeline can be unit-tested with fakes and
each component can be swapped without touching the others (separation of
concerns / dependency inversion).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from .announcer import Announcer
from .config import AppConfig
from .detector import ObjectDetector
from .distance import DistanceEstimator
from .spatial import SpatialMapper
from .tts import SpeechEngine
from .types import Announcement, Detection

logger = logging.getLogger(__name__)


@dataclass
class FrameResult:
    detections: List[Detection]
    announcement: Optional[Announcement]


class NavigationPipeline:
    def __init__(
        self,
        config: AppConfig,
        detector: ObjectDetector,
        distance: DistanceEstimator,
        spatial: SpatialMapper,
        announcer: Announcer,
        speech: Optional[SpeechEngine] = None,
    ):
        self.config = config
        self.detector = detector
        self.distance = distance
        self.spatial = spatial
        self.announcer = announcer
        self.speech = speech

    def process(self, frame) -> FrameResult:
        # 1. Detect objects.
        detections = self.detector.detect(frame)

        # 2. Enrich each detection with distance + spatial zone.
        for det in detections:
            self.distance.annotate(det)
            self.spatial.annotate(det)

        # 3. Decide what (if anything) to announce.
        announcement = self.announcer.build(detections)

        # 4. Speak it.
        if announcement is not None and self.speech is not None:
            self.speech.speak(announcement)
            logger.info("SAY: %s", announcement.text)

        return FrameResult(detections=detections, announcement=announcement)
