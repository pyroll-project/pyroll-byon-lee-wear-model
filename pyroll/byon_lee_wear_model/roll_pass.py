import math

import logging
import numpy as np

from pyroll.core.hooks import Hook
from pyroll.core import SymmetricRollPass, root_hooks
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.geometry.multilinestring import MultiLineString


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

SymmetricRollPass.Roll.wear_contour_line = Hook[LineString]()
"""Wear contour of the groove."""

SymmetricRollPass.Roll.wear_cross_section = Hook[Polygon]()
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

@SymmetricRollPass.Roll.wear_radius
def wear_radius(self: SymmetricRollPass.Roll):
    roll = self
    rp = self.roll_pass
    ip = rp.in_profile

    if not {"oval", "round"} & self.roll_pass.classifiers:
        logging.warning("Pass Sequence not suitable for Byon-Lee Wear Model.")
        return 0

    def weight_function(correction_factor: float) -> float:
        _weight = 1 - correction_factor * ((rp.roll_force ** 2 * rp.out_profile.length * rp.rolled_billets) / roll.shore_hardness)
        return _weight

    try:
        bulge_radius = self.roll_pass.prev_of(SymmetricRollPass).roll.groove.r2
    except IndexError:
        bulge_radius = self.roll_pass.in_profile.equivalent_radius

    if "round" in ip.classifiers and "oval" in rp.classifiers:
        weight = weight_function(roll.round_oval_wear_coefficient)
        return self.groove.r2 * weight + ip.equivalent_radius * (1 - weight)

    elif "oval" in ip.classifiers and "round" in rp.classifiers:
        weight = weight_function(roll.oval_round_wear_coefficient)

        return self.groove.r2 * weight + 0.75 * bulge_radius * (1 - weight)
    else:
        return 0


@SymmetricRollPass.Roll.wear_contour_line
def wear_contour_line(self: SymmetricRollPass.Roll) -> MultiLineString:

    op = self.roll_pass.out_profile

    z_coordinates_wear_contour = np.linspace(op.detachment_points.geoms[0].x, op.detachment_points.geoms[1].x, 100)
    y_coordinates_wear_radius = np.sqrt(self.wear_radius ** 2 - z_coordinates_wear_contour ** 2)

    points = list(zip(z_coordinates_wear_contour, y_coordinates_wear_radius))

    upper_wear_contour_line = LineString(points)



    return upper_wear_contour_line






root_hooks.append(SymmetricRollPass.Roll.wear_radius)


