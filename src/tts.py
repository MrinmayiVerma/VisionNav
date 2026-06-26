"""
Text-to-speech output.

Audio feedback is the system's only output channel, so it must never block
the vision loop. Speech runs on its own worker thread fed by a queue. For
safety, the queue is intelligently managed:

  * DANGER announcements jump to the front of the queue and clear pending
    lower-priority messages, so the user always hears the most urgent thing
    first.
  * The queue is bounded so a backlog of stale messages can never build up.

pyttsx3 is used because it works fully offline (no network, no API key),
which is essential for an assistive device that must work anywhere.
"""
from __future__ import annotations

import logging
import queue
import threading
from typing import Optional

from .config import TTSConfig
from .types import Announcement, Urgency

logger = logging.getLogger(__name__)


class SpeechEngine:
    def __init__(self, config: TTSConfig, max_queue: int = 4):
        self.config = config
        self._queue: "queue.PriorityQueue[tuple]" = queue.PriorityQueue(maxsize=max_queue)
        self._engine = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._seq = 0  # tie-breaker so PriorityQueue never compares Announcements
        self._lock = threading.Lock()

    def start(self) -> "SpeechEngine":
        import pyttsx3

        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", self.config.rate)
        self._engine.setProperty("volume", self.config.volume)
        if self.config.voice_id:
            self._engine.setProperty("voice", self.config.voice_id)

        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        logger.info("SpeechEngine started.")
        return self

    def _worker(self) -> None:
        while self._running:
            try:
                _, _, announcement = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if announcement is None:
                break
            try:
                self._engine.say(announcement.text)
                self._engine.runAndWait()
            except Exception as exc:  # pragma: no cover - hardware dependent
                logger.error("TTS failure: %s", exc)
            finally:
                self._queue.task_done()

    def speak(self, announcement: Announcement) -> None:
        """Enqueue an announcement. Higher urgency is spoken first."""
        with self._lock:
            # A DANGER message pre-empts everything already queued.
            if announcement.urgency == Urgency.DANGER:
                self._drain()
            self._seq += 1
            # PriorityQueue pops the smallest item, so negate urgency.
            item = (-int(announcement.urgency), self._seq, announcement)
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                # Drop the lowest-priority pending item to make room.
                self._drain_lowest()
                try:
                    self._queue.put_nowait(item)
                except queue.Full:
                    logger.debug("Speech queue full; dropping announcement.")

    def _drain(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

    def _drain_lowest(self) -> None:
        items = []
        while not self._queue.empty():
            try:
                items.append(self._queue.get_nowait())
                self._queue.task_done()
            except queue.Empty:
                break
        if items:
            items.sort()        # smallest priority value = most urgent
            items.pop()         # discard the least urgent
            for it in items:
                try:
                    self._queue.put_nowait(it)
                except queue.Full:
                    break

    def stop(self) -> None:
        self._running = False
        try:
            self._queue.put_nowait((999, self._seq + 1, None))
        except queue.Full:
            self._drain()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        logger.info("SpeechEngine stopped.")

    def __enter__(self) -> "SpeechEngine":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()
