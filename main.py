"""
VisionNav — main application entry point.

Usage:
    python main.py                 # use default webcam (source 0)
    python main.py --source vid.mp4
    python main.py --no-window     # headless (for a real wearable device)
    python main.py --device cuda   # run detection on GPU

Press 'q' in the debug window (or Ctrl-C in a terminal) to quit.
"""
from __future__ import annotations

import argparse
import logging
import time

import cv2

from src.announcer import Announcer
from src.camera import VideoStream
from src.config import default_config
from src.detector import ObjectDetector
from src.distance import DistanceEstimator
from src.overlay import draw_detections
from src.pipeline import NavigationPipeline
from src.spatial import SpatialMapper
from src.tts import SpeechEngine


def parse_args():
    p = argparse.ArgumentParser(description="VisionNav assistive navigation")
    p.add_argument("--source", default=None,
                   help="camera index (e.g. 0) or path to a video file")
    p.add_argument("--device", default=None, help="cpu | cuda | mps")
    p.add_argument("--weights", default=None, help="path to YOLO weights")
    p.add_argument("--no-window", action="store_true",
                   help="run headless without the debug window")
    p.add_argument("--no-audio", action="store_true",
                   help="disable text-to-speech (print announcements only)")
    return p.parse_args()


def build_config(args):
    cfg = default_config()
    if args.source is not None:
        cfg.camera.source = int(args.source) if args.source.isdigit() else args.source
    if args.device is not None:
        cfg.detector.device = args.device
    if args.weights is not None:
        cfg.detector.weights = args.weights
    if args.no_window:
        cfg.show_window = False
    return cfg


def main():
    args = parse_args()
    cfg = build_config(args)
    logging.basicConfig(
        level=getattr(logging, cfg.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("visionnav")

    detector = ObjectDetector(cfg.detector).load()
    distance = DistanceEstimator(cfg.distance)

    stream = VideoStream(cfg.camera).start()
    width, _ = stream.resolution
    spatial = SpatialMapper(cfg.spatial, frame_width=width)
    announcer = Announcer(cfg.announcer)

    speech = None
    if not args.no_audio:
        speech = SpeechEngine(cfg.tts).start()

    pipeline = NavigationPipeline(
        config=cfg, detector=detector, distance=distance,
        spatial=spatial, announcer=announcer, speech=speech,
    )

    log.info("VisionNav running. Press 'q' to quit.")
    frames, t_start = 0, time.time()
    try:
        while stream.is_running:
            frame = stream.read()
            if frame is None:
                time.sleep(0.005)
                continue

            result = pipeline.process(frame)
            frames += 1

            if result.announcement and args.no_audio:
                print(f"[SAY] {result.announcement.text}")

            if cfg.show_window:
                draw_detections(frame, result.detections)
                fps = frames / max(1e-6, time.time() - t_start)
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("VisionNav", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    finally:
        stream.stop()
        if speech is not None:
            speech.stop()
        if cfg.show_window:
            cv2.destroyAllWindows()
        log.info("Processed %d frames.", frames)


if __name__ == "__main__":
    main()
