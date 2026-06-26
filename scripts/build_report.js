const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageBreak, TableOfContents, PageNumber, Header, Footer,
} = require("docx");

const IMG = path.join(__dirname, "..", "docs", "img");
const img = (f) => fs.readFileSync(path.join(IMG, f));

// ---------- helpers -------------------------------------------------------- //
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });

const P = (t, opts = {}) => new Paragraph({
  spacing: { after: 120, line: 276 },
  alignment: opts.center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
  children: Array.isArray(t) ? t : [new TextRun({ text: t, ...opts })],
});

const bullet = (t) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60, line: 276 },
  children: [new TextRun(t)],
});

const num = (t) => new Paragraph({
  numbering: { reference: "nums", level: 0 },
  spacing: { after: 60, line: 276 },
  children: [new TextRun(t)],
});

const code = (lines) => {
  const arr = Array.isArray(lines) ? lines : lines.split("\n");
  return arr.map((ln, i) => new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
    spacing: { after: 0, line: 240 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 18, color: "2E5E8C", space: 6 },
    },
    children: [new TextRun({ text: ln || " ", font: "Consolas", size: 18 })],
  }));
};

const picture = (file, w, h, caption) => [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: "png", data: img(file), transformation: { width: w, height: h } })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: caption, italics: true, size: 18, color: "555555" })],
  }),
];

const B = "CCCCCC";
const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 1, color: B },
  bottom: { style: BorderStyle.SINGLE, size: 1, color: B },
  left: { style: BorderStyle.SINGLE, size: 1, color: B },
  right: { style: BorderStyle.SINGLE, size: 1, color: B },
};
const cell = (text, { head = false, w = 3120, bold = false } = {}) => new TableCell({
  borders: cellBorders,
  width: { size: w, type: WidthType.DXA },
  shading: head ? { type: ShadingType.CLEAR, fill: "2E5E8C" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({
    spacing: { after: 0 },
    children: [new TextRun({ text, bold: head || bold, color: head ? "FFFFFF" : "000000", size: 19 })],
  })],
});
const table = (rows, widths) => new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths,
  rows: rows.map((r, ri) => new TableRow({
    children: r.map((c, ci) => cell(c, { head: ri === 0, w: widths[ci] })),
  })),
});
const spacer = () => new Paragraph({ spacing: { after: 120 }, children: [new TextRun("")] });

// ---------- title page ----------------------------------------------------- //
const titlePage = [
  new Paragraph({ spacing: { before: 600, after: 200 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "VISIONNAV", bold: true, size: 56, color: "2E5E8C" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: "A Real-Time Computer Vision Assistive Navigation System", bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
    children: [new TextRun({ text: "for Visually Impaired Individuals", bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: "B.Tech Final Year Major Project Report", italics: true, size: 26 })] }),
  ...picture("architecture.png", 430, 309, "System architecture overview"),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 80 },
    children: [new TextRun({ text: "Department of Computer Science & Engineering", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ text: "Bachelor of Technology", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Academic Year 2025–2026", size: 24 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- content -------------------------------------------------------- //
const content = [
  // ABSTRACT
  H1("Abstract"),
  P("Visually impaired individuals face significant challenges when moving through indoor and outdoor environments. The traditional white cane, while invaluable, can only detect the presence of nearby obstacles through physical contact; it cannot identify what an object is, recognise traffic signs, or provide directional guidance toward a destination. This project, VisionNav, presents a real-time computer-vision assistance system that addresses these limitations."),
  P("VisionNav uses a single, inexpensive camera to continuously detect obstacles and important objects such as pedestrians, vehicles, traffic lights, and stop signs. For each detected object the system estimates its distance using a monocular pinhole-camera model and determines its direction relative to the user (left, ahead, or right). A prioritisation engine then selects the most safety-critical objects and converts them into short, natural-language sentences that are spoken to the user through an offline text-to-speech engine. An optional GPS-based module provides turn-by-turn route guidance."),
  P("The system is built in Python using the YOLOv8 object-detection model, OpenCV, and pyttsx3. It employs a multi-threaded architecture so that frame capture, inference, and speech occur concurrently, achieving real-time performance on commodity hardware. The design emphasises modularity, testability, and extensibility, enabling future enhancements such as custom traffic-sign recognition and monocular depth estimation."),
  new Paragraph({ children: [new PageBreak()] }),

  // TOC
  H1("Table of Contents"),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
  new Paragraph({ children: [new PageBreak()] }),

  // 1. INTRODUCTION
  H1("1. Introduction"),
  H2("1.1 Background and Motivation"),
  P("According to the World Health Organization, hundreds of millions of people worldwide live with moderate-to-severe visual impairment or blindness. For these individuals, independent mobility is one of the most important factors affecting quality of life, employment, and social participation. The white cane remains the most widely used mobility aid, but it provides only tactile feedback about objects within roughly one metre and at ground level. It cannot warn of overhanging obstacles, identify the nature of an object, distinguish a parked car from a moving one, read a stop sign, or guide a user along a route."),
  P("Advances in deep-learning-based computer vision and the falling cost of camera hardware now make it feasible to build an affordable electronic travel aid that perceives the environment far more richly than a cane and communicates that information through audio. VisionNav is designed as exactly such an aid."),

  H2("1.2 Problem Statement"),
  P("Develop a real-time computer-vision system that detects obstacles, recognises important objects and traffic signs, estimates their distance and direction, and provides timely audio feedback so that a visually impaired user can navigate indoor and outdoor environments more safely and independently than is possible with a traditional cane alone."),

  H2("1.3 Objectives"),
  num("Detect obstacles and common objects in real time from a single camera feed."),
  num("Recognise safety-relevant objects including pedestrians, vehicles, traffic lights, and stop signs."),
  num("Estimate the distance to each detected object using only a monocular camera."),
  num("Determine each object's direction (left, ahead, right) relative to the user."),
  num("Prioritise objects by safety relevance and convey them through concise, non-overwhelming audio feedback."),
  num("Provide optional GPS-based turn-by-turn route guidance toward a destination."),
  num("Run on affordable, portable hardware while remaining modular and extensible."),

  H2("1.4 Scope and Limitations"),
  P("The system targets pedestrian navigation using a forward-facing camera. Object detection relies on the 80-class COCO model, restricted to classes relevant to walking. Distance estimation is approximate and assumes the object's class has a roughly standard physical size. The system is an assistive aid intended to complement — not replace — the white cane or guide dog, and it does not guarantee detection of every hazard."),
  new Paragraph({ children: [new PageBreak()] }),

  // 2. LITERATURE SURVEY
  H1("2. Literature Survey"),
  P("Electronic travel aids (ETAs) for the visually impaired have been studied for several decades. Early approaches used ultrasonic or infrared rangefinders that converted distance into audio tones; these detected obstacles but could not identify them. More recent work leverages computer vision and deep learning."),
  H2("2.1 Existing Approaches"),
  table([
    ["Approach", "Capability", "Limitation"],
    ["White cane", "Tactile detection of ground-level obstacles within ~1 m", "No object identity, no overhead/distant hazards, no guidance"],
    ["Ultrasonic ETAs", "Distance-to-obstacle as audio tone", "Cannot identify object type or read signs"],
    ["RGB-D / stereo systems", "Accurate depth maps", "Bulky, expensive, higher power draw"],
    ["CNN detection systems", "Identify object classes from a camera", "Often offline-only analysis; few give prioritised real-time audio"],
  ], [2200, 3580, 3580]),
  spacer(),
  H2("2.2 Gap Addressed"),
  P("Many vision-based prototypes detect objects but announce everything they see, overwhelming the user, or perform analysis offline without real-time audio. VisionNav addresses this gap by combining real-time monocular detection, approximate distance and direction estimation, and — crucially — a prioritisation layer that decides what is worth saying and suppresses repetition, all on inexpensive hardware with fully offline speech."),
  new Paragraph({ children: [new PageBreak()] }),

  // 3. REQUIREMENTS
  H1("3. System Requirements"),
  H2("3.1 Functional Requirements"),
  bullet("FR1: The system shall capture live video from a connected camera."),
  bullet("FR2: The system shall detect and classify objects in each frame in real time."),
  bullet("FR3: The system shall estimate the distance to each detected object."),
  bullet("FR4: The system shall classify each object's direction as left, ahead, or right."),
  bullet("FR5: The system shall prioritise objects by safety relevance and proximity."),
  bullet("FR6: The system shall announce the highest-priority objects via spoken audio."),
  bullet("FR7: The system shall suppress repeated announcements of the same object."),
  bullet("FR8: The system shall issue an immediate alert for objects in the danger zone."),
  bullet("FR9: The system shall optionally provide GPS turn-by-turn route guidance."),
  H2("3.2 Non-Functional Requirements"),
  bullet("NFR1 (Performance): End-to-end latency low enough for real-time use (target ≥ 10 FPS on CPU)."),
  bullet("NFR2 (Usability): Audio must be concise and must not overwhelm the user."),
  bullet("NFR3 (Reliability): Speech output must never block the vision loop."),
  bullet("NFR4 (Portability): Must run offline on commodity / portable hardware."),
  bullet("NFR5 (Maintainability): Modular design with unit-tested core logic."),
  H2("3.3 Hardware Requirements"),
  table([
    ["Component", "Minimum", "Recommended"],
    ["Camera", "640×480 USB / phone webcam", "720p wide-angle camera"],
    ["Processor", "Quad-core CPU", "CPU + CUDA GPU / Jetson Nano"],
    ["RAM", "4 GB", "8 GB"],
    ["Audio", "Bone-conduction / earphones", "Bone-conduction headset"],
    ["GPS (optional)", "USB / phone GPS", "Dedicated GNSS module"],
  ], [2600, 3380, 3380]),
  spacer(),
  H2("3.4 Software Requirements"),
  table([
    ["Software", "Purpose"],
    ["Python 3.10+", "Implementation language"],
    ["Ultralytics YOLOv8", "Object detection"],
    ["OpenCV", "Camera capture and image processing"],
    ["pyttsx3", "Offline text-to-speech"],
    ["NumPy", "Numerical operations"],
    ["pytest", "Unit testing"],
  ], [3680, 5680]),
  new Paragraph({ children: [new PageBreak()] }),

  // 4. SYSTEM DESIGN (HLD)
  H1("4. System Design (High-Level Design)"),
  H2("4.1 Architectural Overview"),
  P("VisionNav follows a layered, pipeline-oriented architecture. Each layer has a single responsibility and communicates with the next through simple, dependency-free data objects. This separation makes the system easy to understand, test, and extend."),
  ...picture("architecture.png", 520, 374, "Figure 4.1 — Layered system architecture"),
  P("The four layers are:"),
  bullet("Input Layer — acquires raw data: video frames from the camera and, optionally, GPS fixes."),
  bullet("Perception Layer — runs YOLOv8 object detection on frames and tracks route waypoints."),
  bullet("Reasoning Layer — enriches detections with distance and direction, then prioritises them and decides what to announce."),
  bullet("Output Layer — converts decisions into spoken audio (and an optional debug window for developers)."),

  H2("4.2 Data Flow"),
  P("Each frame flows through a fixed sequence of processing stages. The pipeline is deliberately linear and stateless per frame (apart from the announcer's cooldown memory), which keeps reasoning about correctness simple."),
  ...picture("dataflow.png", 600, 188, "Figure 4.2 — Per-frame processing pipeline"),

  H2("4.3 Module Responsibilities"),
  table([
    ["Module", "Responsibility"],
    ["camera.py", "Threaded capture; always supplies the latest frame"],
    ["detector.py", "YOLOv8 inference; returns a list of Detection objects"],
    ["distance.py", "Monocular distance estimate + urgency band per detection"],
    ["spatial.py", "Maps each detection to a left / ahead / right zone"],
    ["announcer.py", "Scores, filters, and phrases announcements; cooldowns"],
    ["tts.py", "Threaded, priority-queued offline speech output"],
    ["navigator.py", "GPS waypoint route guidance"],
    ["pipeline.py", "Orchestrates all stages for each frame"],
    ["config.py", "All tunable parameters in one place"],
  ], [2600, 6760]),
  new Paragraph({ children: [new PageBreak()] }),

  // 5. LOW-LEVEL DESIGN (LLD)
  H1("5. Low-Level Design"),
  H2("5.1 Module / Class Structure"),
  P("The class diagram below shows the principal classes and their key operations. Detections are represented as plain dataclasses (Detection, BoundingBox) carrying all derived metadata, so that the logic modules never depend on heavy libraries and remain unit-testable."),
  ...picture("classes.png", 520, 382, "Figure 5.1 — Module / class diagram"),

  H2("5.2 Runtime Interaction"),
  P("The sequence diagram shows how the pipeline coordinates the components for a single frame. The Speech component receives the announcement and hands it to a background thread, so the main loop is never blocked waiting for audio to finish."),
  ...picture("sequence.png", 560, 335, "Figure 5.2 — Runtime sequence for one frame"),

  H2("5.3 Key Algorithms"),
  H3("5.3.1 Monocular Distance Estimation"),
  P("Using the pinhole-camera model, an object of known real height H (metres) that appears with pixel height h, viewed by a camera of focal length f (pixels), lies at distance:"),
  ...code(["distance = (H * f) / h"]),
  P("A one-time calibration determines f for a given camera. Typical real heights per class (person = 1.70 m, car = 1.50 m, stop sign = 0.75 m, …) are stored in configuration. The raw distance is then mapped to an urgency band:"),
  ...code([
    "if   distance <= 1.5 m : urgency = DANGER",
    "elif distance <= 3.0 m : urgency = WARNING",
    "elif distance <= 6.0 m : urgency = NOTICE",
    "else                   : urgency = INFO",
  ]),

  H3("5.3.2 Spatial Zone Mapping"),
  P("The horizontal centre of each bounding box is compared against frame-width fractions to assign a direction:"),
  ...code([
    "fraction = box.center_x / frame_width",
    "if   fraction < 0.38 : zone = LEFT",
    "elif fraction > 0.62 : zone = RIGHT",
    "else                 : zone = AHEAD",
  ]),

  H3("5.3.3 Prioritisation"),
  P("Every detection is scored so that a very close object outranks a far-away but nominally more important one. The score combines a per-class base priority, a large additive boost proportional to urgency, and a bonus for objects directly ahead in the walking path:"),
  ...code([
    "priority = base_priority[class]",
    "         + urgency_level * 50",
    "         + (25 if zone == AHEAD else 0)",
  ]),

  H3("5.3.4 Repeat Suppression (Cooldown)"),
  P("To avoid overwhelming the user, each (class, zone) pair is announced at most once per cooldown window (default 4 s). DANGER items use a shortened cooldown so urgent repeats still get through, and they pre-empt any speech already queued. A global minimum gap between sentences further smooths the audio stream."),

  H2("5.4 Core Data Structures"),
  table([
    ["Type", "Fields", "Purpose"],
    ["BoundingBox", "x1, y1, x2, y2", "Object location; derives width/height/centre/area"],
    ["Detection", "label, confidence, box, distance_m, zone, urgency, priority", "A detected object with all derived metadata"],
    ["Announcement", "text, urgency", "A sentence to be spoken"],
    ["Waypoint", "lat, lon, instruction", "One step of a navigation route"],
  ], [1900, 3760, 3700]),
  new Paragraph({ children: [new PageBreak()] }),

  // 6. IMPLEMENTATION
  H1("6. Implementation"),
  H2("6.1 Technology Stack"),
  P("The system is implemented in Python 3.10+. YOLOv8-nano is chosen as the detection model because it offers the best speed-to-accuracy trade-off for edge devices and is only ~6 MB. OpenCV handles camera I/O, pyttsx3 provides offline speech (no internet or API key required), and a multi-threaded design keeps capture, inference, and speech concurrent."),

  H2("6.2 Threaded Capture"),
  P("Reading frames and running inference in the same loop wastes time blocking on I/O. A background thread continuously grabs frames and the main loop always receives the latest one, minimising latency:"),
  ...code([
    "def _update(self):",
    "    while self._running:",
    "        ok, frame = self._cap.read()",
    "        with self._lock:",
    "            self._frame = frame   # keep only the latest",
  ]),

  H2("6.3 Detection Wrapper"),
  P("The detector hides the Ultralytics API behind a stable interface so the model can be swapped without touching the rest of the system:"),
  ...code([
    "def detect(self, frame) -> list[Detection]:",
    "    results = self._model.predict(frame, conf=..., classes=...)",
    "    return [Detection(label, conf, BoundingBox(*xyxy))",
    "            for box in results[0].boxes]",
  ]),

  H2("6.4 Announcer"),
  P("The announcer ties the reasoning together — ranking, filtering out far/non-urgent clutter, applying cooldowns, and composing a sentence such as \u201CStop. Car ahead, very close\u201D or \u201CA person ahead, 3 metres\u201D."),

  H2("6.5 Safe Speech Output"),
  P("Speech runs on a worker thread fed by a bounded priority queue. DANGER messages jump the queue and clear pending lower-priority messages, guaranteeing the user always hears the most urgent thing first while the vision loop continues uninterrupted."),
  new Paragraph({ children: [new PageBreak()] }),

  // 7. TESTING
  H1("7. Testing"),
  H2("7.1 Strategy"),
  P("The safety-critical reasoning (distance, spatial mapping, prioritisation, cooldowns, and geo-math) is implemented in modules with no camera, model, or audio dependencies, so it can be exhaustively unit-tested. Integration is verified with an offline demo that streams scripted scenes through the full decision pipeline."),
  H2("7.2 Unit Test Results"),
  table([
    ["Test", "What it verifies", "Result"],
    ["test_distance_pinhole_math", "Pinhole distance formula", "PASS"],
    ["test_urgency_bands", "Distance → urgency mapping", "PASS"],
    ["test_spatial_zones", "Left / ahead / right mapping", "PASS"],
    ["test_priority_close_object...", "Close object outranks far one", "PASS"],
    ["test_announcer_cooldown...", "Repeat suppression", "PASS"],
    ["test_announcer_ignores_info...", "Far clutter stays silent", "PASS"],
    ["test_danger_message_phrasing", "Danger phrasing & urgency", "PASS"],
    ["test_haversine_known_distance", "Great-circle distance", "PASS"],
    ["test_bearing / compass_word", "Bearing & compass words", "PASS"],
    ["test_route_guide_advances...", "Waypoint advance on arrival", "PASS"],
  ], [3200, 4360, 1800]),
  spacer(),
  P("All 12 unit tests pass (pytest). The offline demo confirms correct end-to-end behaviour: far objects are silent, a close pedestrian is announced with its distance, a stop sign is prioritised over a distant person, and an object in the danger zone produces an immediate \u201CStop\u201D alert."),
  new Paragraph({ children: [new PageBreak()] }),

  // 8. RESULTS
  H1("8. Results and Discussion"),
  P("Running the offline decision demo produces the following representative output, illustrating each behaviour of the system:"),
  ...code([
    "Frame 1: person(ahead, 8.5m, INFO)        >> (silent)",
    "Frame 2: person(ahead, 3.4m, NOTICE)      >> \"A person ahead, 3 metres\"",
    "Frame 3: car(left,10m), bicycle(right,9m) >> (silent)",
    "Frame 4: car(ahead, 2.2m, WARNING)        >> \"A car ahead, 2 metres\"",
    "Frame 5: stop sign(ahead,4m)+person(far)  >> \"A stop sign ahead, 4 metres\"",
    "Frame 6: dog(ahead, 1.6m, WARNING)        >> \"A dog ahead, 2 metres\"",
  ]),
  P("The results demonstrate that the system behaves as intended: it stays silent for distant, non-urgent objects (Frames 1 and 3), speaks when an object becomes relevant (Frame 2), and correctly prioritises the most safety-critical object when several are present (Frame 5, where the nearby stop sign is chosen over the distant person). Distance estimates fall within a reasonable margin for the configured focal length, which is sufficient for the coarse proximity bands the system uses."),
  P("On a typical quad-core laptop CPU, YOLOv8-nano at a 416-pixel inference size sustains real-time throughput; the threaded design ensures the speech output and frame capture never stall the detection loop."),
  new Paragraph({ children: [new PageBreak()] }),

  // 9. LIMITATIONS & FUTURE WORK
  H1("9. Limitations and Future Work"),
  H2("9.1 Limitations"),
  bullet("Distance estimation assumes a roughly standard physical size per object class; unusually sized objects yield less accurate estimates."),
  bullet("Detection is limited to the COCO classes; specialised traffic signs beyond stop signs are not yet recognised."),
  bullet("A single forward-facing camera cannot perceive hazards outside its field of view."),
  bullet("Performance depends on lighting; very low light reduces detection quality."),
  H2("9.2 Future Work"),
  bullet("Add a dedicated traffic-sign classifier trained on the GTSRB dataset behind the existing detector interface."),
  bullet("Replace the geometric distance estimate with a monocular depth network (e.g. MiDaS) for arbitrary objects, especially indoors."),
  bullet("Add voice-command input so the user can set a destination hands-free."),
  bullet("Deploy on an embedded board (NVIDIA Jetson) in a wearable form factor with bone-conduction audio."),
  bullet("Incorporate object tracking to estimate object velocity and warn of approaching vehicles."),
  new Paragraph({ children: [new PageBreak()] }),

  // 10. CONCLUSION
  H1("10. Conclusion"),
  P("VisionNav demonstrates that an affordable, single-camera computer-vision system can meaningfully extend the capabilities of a traditional white cane. By detecting and identifying objects, estimating their distance and direction, prioritising the most safety-critical information, and delivering it as concise offline speech, the system helps a visually impaired user understand their surroundings and move more confidently and independently."),
  P("The project's layered, modular design — with safety-critical logic isolated into fully unit-tested, dependency-free modules — provides a solid, extensible foundation. The clear extension points for custom sign recognition, learned depth, and embedded deployment outline a credible path from this prototype toward a deployable assistive device."),
  new Paragraph({ children: [new PageBreak()] }),

  // REFERENCES
  H1("References"),
  num("World Health Organization. \u201CBlindness and vision impairment.\u201D WHO Fact Sheets."),
  num("J. Redmon et al. \u201CYou Only Look Once: Unified, Real-Time Object Detection,\u201D CVPR 2016."),
  num("G. Jocher et al. \u201CUltralytics YOLOv8,\u201D Ultralytics, 2023."),
  num("T.-Y. Lin et al. \u201CMicrosoft COCO: Common Objects in Context,\u201D ECCV 2014."),
  num("R. Ranftl et al. \u201CTowards Robust Monocular Depth Estimation (MiDaS),\u201D IEEE TPAMI, 2020."),
  num("G. Bradski. \u201CThe OpenCV Library,\u201D Dr. Dobb's Journal of Software Tools, 2000."),
  num("R. Hartley and A. Zisserman. Multiple View Geometry in Computer Vision, Cambridge University Press, 2004."),
  num("J. Stallkamp et al. \u201CThe German Traffic Sign Recognition Benchmark (GTSRB),\u201D IJCNN 2011."),
];

// ---------- document ------------------------------------------------------- //
const doc = new Document({
  creator: "VisionNav Project",
  title: "VisionNav Project Report",
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "2E5E8C" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "1F4060" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: "Arial", color: "333333" },
        paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
      { reference: "nums", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
    ],
  },
  sections: [{
    properties: { page: {
      size: { width: 12240, height: 15840 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
    } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E5E8C", space: 4 } },
      children: [new TextRun({ text: "VisionNav — Assistive Navigation System", size: 16, color: "777777" })],
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Page ", size: 16, color: "777777" }),
                 new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "777777" })],
    })] }) },
    children: [...titlePage, ...content],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(__dirname, "..", "VisionNav_Project_Report.docx");
  fs.writeFileSync(out, buf);
  console.log("Report written:", out, "(", buf.length, "bytes )");
});
