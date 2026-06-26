# VisionNav — Real-Time Assistive Navigation for the Visually Impaired

A real-time computer-vision system that detects obstacles and important objects
(people, vehicles, traffic lights, stop signs, etc.), estimates how far away and
in which direction they are, and delivers concise spoken guidance — helping a
visually impaired user move safely and independently, indoors and outdoors.

It also includes an optional GPS-based turn-by-turn **route guidance** module.

---

## Key features

- **Object & obstacle detection** using YOLOv8 (80 COCO classes, filtered to the
  ones that matter for a pedestrian).
- **Monocular distance estimation** via the pinhole-camera model — no depth
  sensor or second camera required.
- **Spatial awareness** — every object is reported as *left*, *ahead*, or *right*.
- **Smart audio feedback** — priority + urgency scoring, repeat-suppression
  cooldowns, and danger pre-emption so the user hears the most important thing
  first and is never spammed.
- **Fully offline text-to-speech** (pyttsx3) — works with no internet connection.
- **Threaded architecture** — separate threads for capture, inference, and
  speech keep the system real-time.
- **Optional route guidance** — GPS waypoint following with great-circle
  distance and compass bearings.

---

## Project structure

```
visionnav/
├── main.py                     # application entry point
├── requirements.txt
├── src/
│   ├── config.py               # all tunable parameters
│   ├── types.py                # shared dataclasses (Detection, BoundingBox, ...)
│   ├── camera.py               # threaded video capture
│   ├── detector.py             # YOLOv8 wrapper
│   ├── distance.py             # monocular distance estimation
│   ├── spatial.py              # left/ahead/right zone mapping
│   ├── announcer.py            # prioritisation + sentence building + cooldowns
│   ├── tts.py                  # threaded, priority-queued speech engine
│   ├── navigator.py            # GPS route guidance
│   ├── overlay.py              # debug visualisation
│   └── pipeline.py             # orchestrates all stages
├── scripts/
│   ├── demo_offline.py         # run the decision logic with NO hardware
│   └── calibrate_focal_length.py
├── tests/
│   └── test_logic.py           # unit tests (no camera/model needed)
└── docs/
```

---

## Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The first run downloads the YOLOv8-nano weights (`yolov8n.pt`, ~6 MB) automatically.

---

## Usage

```bash
# default webcam, with debug window and audio
python main.py

# run on a recorded video file
python main.py --source path/to/video.mp4

# headless device (no window), audio only
python main.py --no-window

# print announcements instead of speaking (useful when developing)
python main.py --no-audio

# run detection on GPU
python main.py --device cuda
```

Press **q** in the debug window (or **Ctrl-C**) to quit.

---

## Try it without a camera

```bash
python scripts/demo_offline.py
```

This streams a scripted scene through the full decision pipeline and prints
exactly what would be spoken — demonstrating distance estimation, spatial
mapping, prioritisation, and cooldowns end-to-end.

---

## Calibration (for accurate distances)

```bash
python scripts/calibrate_focal_length.py \
    --known-height 0.297 --distance 1.0 --pixel-height 178
```

Paste the printed focal length into `DistanceConfig.focal_length_px` in
`src/config.py`.

---

## Testing

```bash
pytest -q
```

---

## Extending the system

- **Custom traffic-sign recognition:** train a classifier on the GTSRB dataset
  and add it as a second model behind the `ObjectDetector` interface.
- **Indoor depth:** swap the monocular estimator for a MiDaS depth model.
- **Voice commands:** add a speech-recognition front end to set destinations.

---

## License

Released for academic use.
