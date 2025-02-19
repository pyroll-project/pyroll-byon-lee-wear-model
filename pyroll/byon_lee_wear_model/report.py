import numpy as np

from pyroll.report import hookimpl
from pyroll.core import RollPass, Unit

from matplotlib import pyplot as plt
from shapely.geometry.multipoint import MultiPoint
from shapely.geometry.point import Point


@hookimpl
def unit_plot(unit: Unit):
    """Plot wear contour for one groove of roll pass contour."""
    if isinstance(unit, RollPass):
        detachment_points: MultiPoint = MultiPoint([Point(unit.out_profile.contact_lines.geoms[0].coords[0]),
                                                    Point(unit.out_profile.contact_lines.geoms[0].coords[-1])])
        z_coordinates_wear_contour = np.arange(start=detachment_points.geoms[0].x, stop=detachment_points.geoms[1].x,
                                               step=1e-6)

        def wear_contour(coordinate):
            return np.sqrt(unit.wear_radius ** 2 - coordinate ** 2)

        y_coordinates_wear_contour = wear_contour(z_coordinates_wear_contour)
        minimum_wear_distance = min(y_coordinates_wear_contour)
        shift_contour = y_coordinates_wear_contour - minimum_wear_distance + detachment_points.geoms[0].y

        fig: plt.Figure = plt.figure(constrained_layout=True, figsize=(4, 4))
        ax: plt.Axes = fig.subplots()

        ax.set_aspect("equal", "datalim")
        ax.grid(lw=0.5)
        plt.title("Lendl Areas and Boundaries")
        ax.plot(*unit.contour_lines.geoms[0].xy, color="k")
        ax.plot(y_coordinates_wear_contour, shift_contour, color='C1', ls='--')

        return fig
