
import numpy as np

from pyroll.report import hookimpl
from pyroll.core.hooks import Hook
from pyroll.core import SymmetricRollPass, RollPass, Unit

from matplotlib import pyplot as plt
from shapely.geometry.multipoint import MultiPoint
from shapely.geometry.point import Point






SymmetricRollPass.Roll.shore_hardness = Hook[float]()
"""Shore hardness of the roll material."""

SymmetricRollPass.oval_round_wear_coefficient = Hook[float]()
"""Coefficient for Byon & Lee wear model for oval - round passes."""

SymmetricRollPass.round_oval_wear_coefficient = Hook[float]()
"""Coefficient for Byon & Lee wear model for round - oval passes."""

SymmetricRollPass.rolled_billets = Hook[float]()
"""Number of rolled billets in this roll pass."""

SymmetricRollPass.wear_radius = Hook[float]()
"""Worn groove radius."""


@SymmetricRollPass.oval_round_wear_coefficient
def default_byon_lee_wear_coefficient(self: SymmetricRollPass):
    return 35.9e-12


@SymmetricRollPass.round_oval_wear_coefficient
def default_byon_lee_wear_coefficient(self: SymmetricRollPass):
    return 19.6e-12


@SymmetricRollPass.wear_radius
def wear_radius(self: SymmetricRollPass):
    if "round" in self.in_profile.classifiers and "oval" in self.classifiers:
        correction_factor = self.round_oval_wear_coefficient
        weight = 1 - correction_factor * (
                (self.roll_force ** 2 * self.roll.contact_length * self.rolled_billets) / self.roll.shore_hardness)
        radius = self.roll.groove.r2 * weight + self.in_profile.equivalent_radius * (1 - weight)
        return radius

    elif "oval" in self.in_profile.classifiers and "round" in self.classifiers:
        correction_factor = self.oval_round_wear_coefficient
        weight = 1 - correction_factor * (
                (self.roll_force ** 2 * self.roll.contact_length * self.rolled_billets) / self.roll.shore_hardness)
        radius = self.roll.groove.r2 * weight + 0.75 * self.out_profile.bulge_radius * (1 - weight)
        return radius
    else:
        return 0



