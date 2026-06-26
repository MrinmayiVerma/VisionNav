"""
Route guidance (outdoor turn-by-turn).

Obstacle detection keeps the user safe locally; route guidance gets them to
a destination. This module is GPS-driven and map-provider agnostic: it takes
a pre-computed route as an ordered list of waypoints (each with a lat/lon and
an instruction such as "turn left onto Main Street") and announces the next
instruction as the user approaches each waypoint.

Bearing + great-circle distance are computed with the haversine formula, so
the module has zero external dependencies and is fully unit-testable.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

_EARTH_RADIUS_M = 6_371_000.0


@dataclass
class Waypoint:
    lat: float
    lon: float
    instruction: str


@dataclass
class GuidanceMessage:
    text: str
    distance_m: float


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2)
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial compass bearing (0-360°) from point 1 to point 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(p2)
    y = (math.cos(p1) * math.sin(p2)
         - math.sin(p1) * math.cos(p2) * math.cos(dlambda))
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def compass_word(bearing: float) -> str:
    dirs = ["north", "north-east", "east", "south-east",
            "south", "south-west", "west", "north-west"]
    idx = int((bearing + 22.5) % 360 // 45)
    return dirs[idx]


class RouteGuide:
    def __init__(self, route: List[Waypoint], arrival_radius_m: float = 12.0,
                 announce_radius_m: float = 30.0):
        self.route = route
        self.arrival_radius_m = arrival_radius_m
        self.announce_radius_m = announce_radius_m
        self._index = 0
        self._announced_for_index = -1

    @property
    def finished(self) -> bool:
        return self._index >= len(self.route)

    @property
    def current_waypoint(self) -> Optional[Waypoint]:
        if self.finished:
            return None
        return self.route[self._index]

    def update(self, lat: float, lon: float) -> Optional[GuidanceMessage]:
        """Feed the user's current GPS fix; return a guidance message if due."""
        wp = self.current_waypoint
        if wp is None:
            return None

        dist = haversine_m(lat, lon, wp.lat, wp.lon)

        # Arrived at this waypoint -> advance and announce its instruction.
        if dist <= self.arrival_radius_m:
            instruction = wp.instruction
            self._index += 1
            if self.finished:
                return GuidanceMessage("You have arrived at your destination.", dist)
            return GuidanceMessage(instruction, dist)

        # Approaching -> give a heads-up once per waypoint.
        if dist <= self.announce_radius_m and self._announced_for_index != self._index:
            self._announced_for_index = self._index
            heading = compass_word(bearing_deg(lat, lon, wp.lat, wp.lon))
            return GuidanceMessage(
                f"In {dist:.0f} metres, {wp.instruction.lower()} (head {heading}).",
                dist,
            )
        return None
