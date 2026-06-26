"""
Threaded video capture.

Reading frames from a camera and running inference in the same loop wastes
time because the CPU blocks on I/O. This module runs frame grabbing on a
background thread and always hands the main loop the *latest* frame, which
keeps end-to-end latency low (important for a real-time safety system).
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import cv2
import numpy as np

from .config import CameraConfig

logger = logging.getLogger(__name__)


class VideoStream:
    """Background-threaded wrapper around cv2.VideoCapture."""

    def __init__(self, config: CameraConfig):
        self.config = config
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_count = 0

    def start(self) -> "VideoStream":
        self._cap = cv2.VideoCapture(self.config.source)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.config.source!r}")

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)

        self._running = True
        self._thread = threading.Thread(target=self._update, daemon=True)
        self._thread.start()
        logger.info("VideoStream started on source %s", self.config.source)
        return self

    def _update(self) -> None:
        min_interval = 1.0 / max(1, self.config.fps_limit)
        while self._running:
            t0 = time.time()
            ok, frame = self._cap.read()
            if not ok:
                logger.warning("Frame read failed; stopping stream.")
                self._running = False
                break
            if self.config.flip_horizontal:
                frame = cv2.flip(frame, 1)
            with self._lock:
                self._frame = frame
                self._frame_count += 1
            # throttle to the configured fps to avoid burning CPU
            elapsed = time.time() - t0
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

    def read(self) -> Optional[np.ndarray]:
        """Return the most recent frame, or None if not ready / stream ended."""
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    @property
    def resolution(self) -> tuple[int, int]:
        if self._cap is None:
            return (self.config.width, self.config.height)
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or self.config.width
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self.config.height
        return (w, h)

    @property
    def is_running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._cap is not None:
            self._cap.release()
        logger.info("VideoStream stopped after %d frames.", self._frame_count)

    def __enter__(self) -> "VideoStream":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()
