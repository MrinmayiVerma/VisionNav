"""Generate architecture / design diagrams for the project report as PNGs."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "img")
os.makedirs(OUT, exist_ok=True)

BLUE = "#2E5E8C"
LBLUE = "#D6E4F0"
GREEN = "#2E8B57"
LGREEN = "#D6F0E0"
ORANGE = "#C9742E"
LORANGE = "#F5E3CE"
GREY = "#444444"


def box(ax, x, y, w, h, text, fc, ec, fs=10, bold=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                       linewidth=1.5, edgecolor=ec, facecolor=fc)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color="#111111", fontweight="bold" if bold else "normal",
            wrap=True)


def arrow(ax, x1, y1, x2, y2, color=GREY, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, linewidth=1.6, color=color))


# --------------------------------------------------------------------------- #
# 1. High-level system architecture (layered)
# --------------------------------------------------------------------------- #
def system_architecture():
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    ax.text(5, 11.5, "VisionNav — System Architecture", ha="center",
            fontsize=14, fontweight="bold", color=BLUE)

    # Input layer
    box(ax, 0.5, 9.8, 4, 1, "Camera (Webcam / Phone)", LBLUE, BLUE, bold=True)
    box(ax, 5.5, 9.8, 4, 1, "GPS Receiver (optional)", LBLUE, BLUE, bold=True)
    ax.text(0.2, 10.9, "INPUT LAYER", fontsize=9, color=BLUE, fontweight="bold")

    # Perception layer
    box(ax, 0.5, 7.7, 4, 1, "Threaded Video Capture", LGREEN, GREEN)
    box(ax, 5.5, 7.7, 4, 1, "Route Guide (waypoints)", LGREEN, GREEN)
    box(ax, 0.5, 6.2, 4, 1, "Object Detector (YOLOv8)", LGREEN, GREEN, bold=True)
    ax.text(0.2, 8.8, "PERCEPTION LAYER", fontsize=9, color=GREEN, fontweight="bold")

    # Reasoning layer
    box(ax, 0.3, 4.1, 3, 1, "Distance Estimator", LORANGE, ORANGE)
    box(ax, 3.6, 4.1, 3, 1, "Spatial Mapper", LORANGE, ORANGE)
    box(ax, 6.9, 4.1, 2.8, 1, "Prioritiser /\nAnnouncer", LORANGE, ORANGE, bold=True)
    ax.text(0.2, 5.2, "REASONING LAYER", fontsize=9, color=ORANGE, fontweight="bold")

    # Output layer
    box(ax, 2.7, 1.8, 4.6, 1, "Speech Engine (pyttsx3, threaded)", LBLUE, BLUE, bold=True)
    box(ax, 7.6, 1.8, 2, 1, "Debug Window\n(dev only)", "#EEEEEE", GREY, fs=9)
    ax.text(0.2, 2.9, "OUTPUT LAYER", fontsize=9, color=BLUE, fontweight="bold")

    box(ax, 3.2, 0.2, 3.6, 0.9, "Audio Feedback to User", "#FCEAEA", "#B23A3A", bold=True)

    # arrows
    arrow(ax, 2.5, 9.8, 2.5, 8.7)
    arrow(ax, 7.5, 9.8, 7.5, 8.7)
    arrow(ax, 2.5, 7.7, 2.5, 7.2)
    arrow(ax, 2.5, 6.2, 1.8, 5.1)
    arrow(ax, 2.5, 6.2, 5.0, 5.1)
    arrow(ax, 1.8, 4.1, 7.5, 3.3, color=ORANGE)
    arrow(ax, 5.0, 4.1, 7.8, 5.1, color=ORANGE)
    arrow(ax, 8.3, 4.1, 5.5, 2.8)
    arrow(ax, 7.0, 7.7, 8.3, 5.1, color=GREEN)
    arrow(ax, 5.0, 1.8, 5.0, 1.1, color="#B23A3A")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "architecture.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 2. Data-flow / processing pipeline
# --------------------------------------------------------------------------- #
def data_flow():
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.set_xlim(0, 16); ax.set_ylim(0, 4); ax.axis("off")
    stages = [
        ("Capture\nframe", LBLUE, BLUE),
        ("Detect\nobjects", LGREEN, GREEN),
        ("Estimate\ndistance", LORANGE, ORANGE),
        ("Map\nzone", LORANGE, ORANGE),
        ("Rank &\nfilter", LORANGE, ORANGE),
        ("Build\nsentence", LGREEN, GREEN),
        ("Speak", "#FCEAEA", "#B23A3A"),
    ]
    x = 0.3
    w = 1.95
    for i, (t, fc, ec) in enumerate(stages):
        box(ax, x, 1.4, w, 1.2, t, fc, ec, fs=10, bold=(i in (1, 4, 6)))
        if i < len(stages) - 1:
            arrow(ax, x + w, 2.0, x + w + 0.25, 2.0)
        x += w + 0.25
    ax.text(8, 3.5, "Per-Frame Processing Pipeline", ha="center",
            fontsize=13, fontweight="bold", color=BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dataflow.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 3. Class / module diagram (LLD)
# --------------------------------------------------------------------------- #
def class_diagram():
    fig, ax = plt.subplots(figsize=(9.5, 7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    ax.text(5, 11.5, "Module / Class Diagram (LLD)", ha="center",
            fontsize=14, fontweight="bold", color=BLUE)

    def cls(x, y, w, h, name, members):
        box(ax, x, y, w, h, "", "#FFFFFF", BLUE)
        ax.add_patch(FancyBboxPatch((x, y + h - 0.55), w, 0.55,
                     boxstyle="round,pad=0.0", linewidth=0, facecolor=LBLUE))
        ax.text(x + w / 2, y + h - 0.28, name, ha="center", va="center",
                fontsize=10, fontweight="bold", color=BLUE)
        ax.text(x + 0.12, y + h - 0.75, members, ha="left", va="top",
                fontsize=8, color="#222222", family="monospace")

    cls(0.4, 8.8, 4.3, 2.4, "NavigationPipeline",
        "+ process(frame)\n  -> detect -> distance\n  -> spatial -> announce\n  -> speak")
    cls(5.3, 9.4, 4.2, 1.8, "ObjectDetector",
        "+ load()\n+ detect(frame)\n  -> list[Detection]")
    cls(0.4, 6.2, 3.0, 2.0, "DistanceEstimator",
        "+ estimate(det)\n+ urgency_for(d)\n+ annotate(det)")
    cls(3.7, 6.2, 2.8, 2.0, "SpatialMapper",
        "+ zone_for(det)\n+ annotate(det)")
    cls(6.7, 6.2, 2.8, 2.0, "Announcer",
        "+ rank(dets)\n+ build(dets)\n  -> Announcement")
    cls(0.4, 3.8, 3.0, 1.8, "SpeechEngine",
        "+ start()/stop()\n+ speak(ann)\n  (threaded queue)")
    cls(3.7, 3.8, 2.8, 1.8, "VideoStream",
        "+ start()/stop()\n+ read() (threaded)")
    cls(6.7, 3.8, 2.8, 1.8, "RouteGuide",
        "+ update(lat,lon)\n  -> Guidance")
    cls(2.5, 1.3, 5.0, 1.9, "Detection / BoundingBox (dataclasses)",
        "label, confidence, box, distance_m,\nzone, urgency, priority")

    arrow(ax, 2.5, 8.8, 1.9, 8.2)
    arrow(ax, 2.5, 8.8, 5.0, 8.2)
    arrow(ax, 2.5, 8.8, 8.0, 8.2)
    arrow(ax, 4.7, 9.9, 5.3, 9.9)
    arrow(ax, 1.9, 6.2, 4.5, 3.2)
    arrow(ax, 5.0, 6.2, 5.0, 3.2)
    arrow(ax, 8.0, 6.2, 6.5, 3.2)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "classes.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 4. Sequence diagram (runtime interaction)
# --------------------------------------------------------------------------- #
def sequence_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 11); ax.axis("off")
    ax.text(6, 10.5, "Runtime Sequence (one frame)", ha="center",
            fontsize=14, fontweight="bold", color=BLUE)

    actors = ["Camera", "Pipeline", "Detector", "Distance/\nSpatial", "Announcer", "Speech"]
    xs = [1, 3.2, 5.2, 7.2, 9.0, 11.0]
    for name, x in zip(actors, xs):
        box(ax, x - 0.75, 9.2, 1.5, 0.7, name, LBLUE, BLUE, fs=8, bold=True)
        ax.plot([x, x], [0.5, 9.2], color="#AAAAAA", linestyle="--", linewidth=1)

    steps = [
        (0, 1, "read() frame", 8.4),
        (1, 2, "detect(frame)", 7.6),
        (2, 1, "list[Detection]", 6.9),
        (1, 3, "annotate(dist, zone)", 6.1),
        (3, 1, "enriched dets", 5.4),
        (1, 4, "build(dets)", 4.6),
        (4, 1, "Announcement", 3.9),
        (1, 5, "speak(ann)", 3.1),
        (5, 5, "queue + TTS thread", 2.3),
    ]
    for a, b, label, y in steps:
        x1, x2 = xs[a], xs[b]
        if a == b:
            ax.annotate("", xy=(x1 + 0.6, y - 0.2), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="-|>", color=GREY))
            ax.text(x1 + 0.7, y - 0.1, label, fontsize=8, va="center")
        else:
            arrow(ax, x1, y, x2, y)
            ax.text((x1 + x2) / 2, y + 0.12, label, ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "sequence.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    system_architecture()
    data_flow()
    class_diagram()
    sequence_diagram()
    print("Diagrams written to", os.path.abspath(OUT))
    print(os.listdir(OUT))
