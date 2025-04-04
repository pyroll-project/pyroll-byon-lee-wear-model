import math

import numpy as np

from pyroll.core.hooks import Hook
from pyroll.core import SymmetricRollPass, root_hooks
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.multipolygon import MultiPolygon
from shapely.lib import clip_by_rect

SymmetricRollPass.Roll.shore_hardness = Hook[float]()
"""Shore hardness of the roll material."""

SymmetricRollPass.Roll.oval_round_wear_coefficient = Hook[float]()
"""Coefficient for Byon & Lee wear model for oval - round passes."""

SymmetricRollPass.Roll.round_oval_wear_coefficient = Hook[float]()
"""Coefficient for Byon & Lee wear model for round - oval passes."""

SymmetricRollPass.rolled_billets = Hook[float]()
"""Number of rolled billets in this roll pass."""

SymmetricRollPass.Roll.wear_radius = Hook[float]()
"""Worn groove radius."""

SymmetricRollPass.Roll.groove_wear_contour_lines = Hook[LineString]()
"""Wear contour of the groove."""

SymmetricRollPass.Roll.groove_wear_cross_section = Hook[Polygon]()
"""Wear cross section of the groove."""

SymmetricRollPass.Roll.max_wear_depth = Hook[float]()
"""Max. depth of the wear contour."""

SymmetricRollPass.Roll.wear_area = Hook[float]()
"""Worn area of the groove."""

SymmetricRollPass.Roll.wear_radius_offset = Hook[float]()
"""Offset of wear radius."""

SymmetricRollPass.OutProfile.detachment_points = Hook[Point]()
"""Detachment points of Profile and RollPass."""


@SymmetricRollPass.Roll.oval_round_wear_coefficient
def default_byon_lee_wear_coefficient(self: SymmetricRollPass.Roll):
    return 35.9e-12


@SymmetricRollPass.Roll.round_oval_wear_coefficient
def default_byon_lee_wear_coefficient(self: SymmetricRollPass.Roll):
    return 19.6e-12


@SymmetricRollPass.OutProfile.detachment_points
def detachment_points(self: SymmetricRollPass.OutProfile):
    return MultiPoint([Point(self.contact_lines.geoms[0].coords[0]), Point(self.contact_lines.geoms[0].coords[-1])])


@SymmetricRollPass.Roll.wear_radius_offset
def wear_radius_offset(self: SymmetricRollPass.Roll):
    rp = self.roll_pass
    op = self.roll_pass.out_profile
    _wear_radius_offset = op.detachment_points.geoms[0].y + self.groove.r2 - rp.height / 2 - np.sqrt(
        self.wear_radius ** 2 - op.detachment_points.geoms[0].x ** 2)
    return _wear_radius_offset


@SymmetricRollPass.Roll.wear_radius
def wear_radius(self: SymmetricRollPass.Roll):
    roll = self
    rp = self.roll_pass
    ip = rp.in_profile

    def weight(correction_factor: float) -> float:
        _weight = 1 - correction_factor * (
                (rp.roll_force ** 2 * rp.out_profile.length * rp.rolled_billets) / roll.shore_hardness)
        return _weight

    if "round" in ip.classifiers and "oval" in rp.classifiers:
        weight = weight(self.round_oval_wear_coefficient)
        if weight <= 0.75:  # Condition from Byon-Lee weight should be between 0.8 and 1
            return 0
        self.logger.debug(f"Weight function on Byon-Lee model for round - oval pass: {weight}.")
        _wear_radius = self.groove.r2 * weight + ip.equivalent_radius * (1 - weight)
        return _wear_radius


    elif "oval" in ip.classifiers and "round" in rp.classifiers:
        weight = weight(self.oval_round_wear_coefficient)
        self.logger.debug(f"Weight function on Byon-Lee model for oval - round pass: {weight}.")
        if weight <= 0.75:  # Condition from Byon-Lee weight should be between 0.8 and 1
            return 0

        return self.groove.r2 * weight + 0.75 * rp.out_profile.bulge_radius * (1 - weight)
    else:
        return 0


@SymmetricRollPass.Roll.groove_wear_contour_lines
def groove_wear_contour_lines(self: SymmetricRollPass.Roll) -> MultiLineString:
    rp = self.roll_pass
    op = self.roll_pass.out_profile

    z_coordinates_wear_contour = np.linspace(
        op.detachment_points.geoms[0].x,
        op.detachment_points.geoms[1].x,
        100)

    if self.wear_radius == 0:
        self.logger.warning("Wear radius is 0 either pass-sequence unsuitable or model detected catastrophic wear.")
        return rp.contour_lines

    y_coordinates_wear_contour = np.sqrt(self.wear_radius ** 2 - z_coordinates_wear_contour ** 2) + self.wear_radius_offset

    points = list(zip(z_coordinates_wear_contour, y_coordinates_wear_contour))

    upper_wear_contour_line = LineString(points)

    offset = self.roll_pass.contour_lines.geoms[0].distance(upper_wear_contour_line)
    moved_upper_wear_contour_line = translate(upper_wear_contour_line, xoff=0, yoff=-offset)

    lower_wear_contour_line = rotate(moved_upper_wear_contour_line, angle=180, origin=(0, 0))
    contur_lines = MultiLineString([moved_upper_wear_contour_line, lower_wear_contour_line])

    return contur_lines


@SymmetricRollPass.Roll.groove_wear_cross_section
def groove_wear_cross_section(self: SymmetricRollPass.Roll):
    poly = []
    for cl, wcl in zip(self.roll_pass.contour_lines.geoms, self.groove_wear_contour_lines.geoms):
        boundary = list(cl.coords) + list(reversed(wcl.coords))
        _poly = Polygon(boundary)
        _clipped_poly = clip_by_rect(_poly, -self.roll_pass.out_profile.width / 2, -math.inf,
                                     self.roll_pass.out_profile.width / 2, math.inf)
        poly.append(_clipped_poly)

    return MultiPolygon(poly)


@SymmetricRollPass.Roll.max_wear_depth
def max_wear_depth(self: SymmetricRollPass.Roll):
    return self.wear_radius + self.wear_radius_offset - self.groove.r2


@SymmetricRollPass.Roll.wear_area
def wear_area(self: SymmetricRollPass.Roll):
    return self.groove_wear_cross_section.area


root_hooks.append(SymmetricRollPass.OutProfile.detachment_points)
root_hooks.append(SymmetricRollPass.Roll.wear_radius)
root_hooks.append(SymmetricRollPass.Roll.wear_radius_offset)
root_hooks.append(SymmetricRollPass.Roll.max_wear_depth)
