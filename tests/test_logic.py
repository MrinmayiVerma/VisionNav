"""
Unit tests for the pure-logic modules (no camera / model / audio needed).

Run:  pytest -q
"""
import math

import pytest

from src.announcer import Announcer, compute_priority
from src.config import (
    AnnouncerConfig,
    DistanceConfig,
    SpatialConfig,
)
from src.distance import DistanceEstimator
from src.navigator import RouteGuide, Waypoint, bearing_deg, compass_word, haversine_m
from src.spatial import SpatialMapper
from src.types import BoundingBox, Detection, Urgency, Zone


# --------------------------------------------------------------------------- #
#  Distance estimation
# --------------------------------------------------------------------------- #
def test_distance_pinhole_math():
    cfg = DistanceConfig(focal_length_px=600.0)
    est = DistanceEstimator(cfg)
    # person (1.70 m) occupying 340 px -> 1.70 * 600 / 340 = 3.0 m
    det = Detection("person", 0.9, BoundingBox(0, 0, 50, 340))
    assert est.estimate(det) == pytest.approx(3.0, abs=0.05)


def test_distance_zero_height_is_infinite():
    est = DistanceEstimator(DistanceConfig())
    det = Detection("person", 0.9, BoundingBox(0, 100, 50, 100))
    assert est.estimate(det) == float("inf")


def test_urgency_bands():
    cfg = DistanceConfig(danger_distance_m=1.5, warning_distance_m=3.0, notice_distance_m=6.0)
    est = DistanceEstimator(cfg)
    assert est.urgency_for(1.0) == Urgency.DANGER
    assert est.urgency_for(2.0) == Urgency.WARNING
    assert est.urgency_for(5.0) == Urgency.NOTICE
    assert est.urgency_for(10.0) == Urgency.INFO


# --------------------------------------------------------------------------- #
#  Spatial mapping
# --------------------------------------------------------------------------- #
def test_spatial_zones():
    mapper = SpatialMapper(SpatialConfig(left_boundary=0.38, right_boundary=0.62), frame_width=1000)
    left = Detection("car", 0.9, BoundingBox(0, 0, 100, 100))      # cx=50  -> left
    center = Detection("car", 0.9, BoundingBox(450, 0, 550, 100))  # cx=500 -> ahead
    right = Detection("car", 0.9, BoundingBox(900, 0, 1000, 100))  # cx=950 -> right
    assert mapper.zone_for(left) == Zone.LEFT
    assert mapper.zone_for(center) == Zone.CENTER
    assert mapper.zone_for(right) == Zone.RIGHT


# --------------------------------------------------------------------------- #
#  Prioritisation / announcer
# --------------------------------------------------------------------------- #
def test_priority_close_object_outranks_far_high_priority():
    cfg = AnnouncerConfig()
    far_stop = Detection("stop sign", 0.9, BoundingBox(0, 0, 10, 10),
                         zone=Zone.LEFT, urgency=Urgency.INFO)
    near_person = Detection("person", 0.9, BoundingBox(0, 0, 10, 10),
                            zone=Zone.CENTER, urgency=Urgency.DANGER)
    assert compute_priority(near_person, cfg) > compute_priority(far_stop, cfg)


def test_announcer_cooldown_suppresses_repeats():
    t = {"now": 0.0}
    cfg = AnnouncerConfig(cooldown_seconds=4.0, min_speech_gap_seconds=0.0)
    ann = Announcer(cfg, clock=lambda: t["now"])
    det = Detection("person", 0.9, BoundingBox(0, 0, 10, 10),
                    zone=Zone.CENTER, urgency=Urgency.WARNING)

    first = ann.build([det])
    assert first is not None
    # immediately again -> suppressed by cooldown
    t["now"] = 1.0
    assert ann.build([det]) is None
    # after cooldown expires -> spoken again
    t["now"] = 5.0
    assert ann.build([det]) is not None


def test_announcer_ignores_info_only_objects():
    cfg = AnnouncerConfig(min_speech_gap_seconds=0.0)
    ann = Announcer(cfg, clock=lambda: 0.0)
    far = Detection("car", 0.9, BoundingBox(0, 0, 10, 10),
                    zone=Zone.LEFT, urgency=Urgency.INFO)
    assert ann.build([far]) is None


def test_danger_message_phrasing():
    cfg = AnnouncerConfig(min_speech_gap_seconds=0.0)
    ann = Announcer(cfg, clock=lambda: 0.0)
    det = Detection("car", 0.9, BoundingBox(0, 0, 10, 10),
                    zone=Zone.CENTER, urgency=Urgency.DANGER, distance_m=1.0)
    msg = ann.build([det])
    assert msg is not None
    assert msg.text.lower().startswith("stop")
    assert msg.urgency == Urgency.DANGER


# --------------------------------------------------------------------------- #
#  Navigation / geo math
# --------------------------------------------------------------------------- #
def test_haversine_known_distance():
    # ~111 km between 1 degree of latitude
    d = haversine_m(0.0, 0.0, 1.0, 0.0)
    assert d == pytest.approx(111_195, rel=0.01)


def test_bearing_due_east():
    b = bearing_deg(0.0, 0.0, 0.0, 1.0)
    assert b == pytest.approx(90.0, abs=0.5)


def test_compass_word():
    assert compass_word(0) == "north"
    assert compass_word(90) == "east"
    assert compass_word(180) == "south"
    assert compass_word(270) == "west"


def test_route_guide_advances_on_arrival():
    route = [
        Waypoint(0.0, 0.0, "Turn left onto Main Street"),
        Waypoint(0.0, 0.001, "Turn right onto Second Avenue"),
    ]
    guide = RouteGuide(route, arrival_radius_m=15.0, announce_radius_m=40.0)
    # Standing right on the first waypoint -> consume it, advance.
    msg = guide.update(0.0, 0.0)
    assert msg is not None
    assert "Main Street" in msg.text
    assert guide.current_waypoint.instruction.endswith("Second Avenue")
