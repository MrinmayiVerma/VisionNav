"""
Prioritisation and announcement building.

A busy street scene can contain a dozen objects per frame. Speaking all of
them would overwhelm the user and, worse, bury the one announcement that
actually matters (a car approaching from the front). This module:

  1. Scores every detection by combining class importance, proximity
     (urgency), and whether it is directly ahead.
  2. Selects the top-N highest-priority detections.
  3. Suppresses repeats using a per-(class, zone) cooldown so the user is
     not told "person ahead" thirty times a second.
  4. Composes a single, natural-language sentence.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

from .config import AnnouncerConfig
from .types import Announcement, Detection, Urgency, Zone


# Urgency contributes a large additive boost so that a very close low-priority
# object still outranks a far-away high-priority one.
_URGENCY_WEIGHT = 50.0


def compute_priority(detection: Detection, config: AnnouncerConfig) -> float:
    base = config.class_priority.get(detection.label, config.default_priority)
    urgency_boost = int(detection.urgency) * _URGENCY_WEIGHT
    # Objects directly ahead are most relevant to the walking path.
    center_boost = 25.0 if detection.zone == Zone.CENTER else 0.0
    return base + urgency_boost + center_boost


class Announcer:
    def __init__(self, config: AnnouncerConfig, clock=time.monotonic):
        self.config = config
        self._clock = clock
        # last time a given (label, zone) pair was spoken
        self._last_spoken: Dict[Tuple[str, Optional[Zone]], float] = {}
        self._last_speech_time: float = -1e9

    # ---- scoring ---------------------------------------------------------- #
    def rank(self, detections: List[Detection]) -> List[Detection]:
        for det in detections:
            det.priority = compute_priority(det, self.config)
        return sorted(detections, key=lambda d: d.priority, reverse=True)

    # ---- cooldown --------------------------------------------------------- #
    def _on_cooldown(self, det: Detection, now: float) -> bool:
        key = (det.label, det.zone)
        last = self._last_spoken.get(key)
        if last is None:
            return False
        # DANGER items bypass most of the cooldown so urgent repeats get through.
        cooldown = self.config.cooldown_seconds
        if det.urgency == Urgency.DANGER:
            cooldown = min(cooldown, 1.5)
        return (now - last) < cooldown

    # ---- phrasing --------------------------------------------------------- #
    @staticmethod
    def _phrase(det: Detection) -> str:
        zone_word = det.zone.value if det.zone else "ahead"
        article = "an" if det.label[0].lower() in "aeiou" else "a"

        if det.urgency == Urgency.DANGER:
            return f"Stop. {det.label.capitalize()} {zone_word}, very close"
        if det.distance_m is not None and det.distance_m != float("inf"):
            return f"{article.capitalize()} {det.label} {zone_word}, {det.distance_m:.0f} metres"
        return f"{article.capitalize()} {det.label} {zone_word}"

    # ---- main entry point ------------------------------------------------- #
    def build(self, detections: List[Detection]) -> Optional[Announcement]:
        """Return an Announcement to speak, or None if nothing should be said."""
        now = self._clock()

        # Global rate limit between sentences (a DANGER item can override it).
        ranked = self.rank(detections)
        has_danger = any(d.urgency == Urgency.DANGER for d in ranked)
        if (now - self._last_speech_time) < self.config.min_speech_gap_seconds and not has_danger:
            return None

        chosen: List[Detection] = []
        for det in ranked:
            if det.urgency == Urgency.INFO:
                continue  # never volunteer far-away, non-urgent clutter
            if self._on_cooldown(det, now):
                continue
            chosen.append(det)
            if len(chosen) >= self.config.max_objects_per_announcement:
                break

        if not chosen:
            return None

        # Record cooldown + global timing.
        for det in chosen:
            self._last_spoken[(det.label, det.zone)] = now
        self._last_speech_time = now

        text = ". ".join(self._phrase(d) for d in chosen)
        top_urgency = max(d.urgency for d in chosen)
        return Announcement(text=text, urgency=top_urgency)
