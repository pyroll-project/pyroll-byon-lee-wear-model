from matplotlib import pyplot as plt

from pyroll.report import hookimpl
from pyroll.core import RollPass, Unit


@hookimpl
def unit_plot(unit: Unit):
    """Plot wear contour for one groove of roll pass contour."""
    if isinstance(unit, RollPass):
        fig: plt.Figure = plt.figure(constrained_layout=True, figsize=(6, 4))
        ax: plt.Axes
        axl: plt.Axes
        ax, axl = fig.subplots(nrows=2, height_ratios=[1, 0.3])
        ax.set_title("Groove Wear Analysis")

        ax.set_aspect("equal", "datalim")
        ax.grid(lw=0.5)

        roll_surface = ax.plot(*unit.contour_lines.geoms[0].xy, color="k", label="roll surface")
        wear_cross_section = ax.fill(*unit.roll.groove_wear_cross_section.boundary.xy, color="red", alpha=0.5, label="wear cross section")
        wear_contour = ax.plot(*unit.roll.groove_wear_contour_line.xy, color='red', ls='--', label="wear contour")

        axl.axis("off")
        axl.legend(handles=roll_surface + wear_cross_section + wear_contour, ncols=3, loc="lower center")
        fig.set_layout_engine('constrained')

        return fig
