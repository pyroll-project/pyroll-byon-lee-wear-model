import logging
import webbrowser
from pathlib import Path

from pyroll.core import Profile, PassSequence, RollPass, Roll, CircularOvalGroove, SwedishOvalGroove, Transport, \
    RoundGroove


def test_solve(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.byon_lee_wear_model
    import pyroll.profile_bulging

    in_profile = Profile.round(
        radius=24e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=["steel", "BST 500"],
        flow_stress=100e6,
        density=7.5e3,
        specific_heat_capacity=690,
        length=0.3
    )

    sequence = PassSequence([
        RollPass(
            label="K 02/001 - 1",
            roll=Roll(
                groove=SwedishOvalGroove(
                    r1=6e-3,
                    r2=26e-3,
                    ground_width=38e-3,
                    usable_width=60e-3,
                    depth=7.25e-3
                ),
                nominal_radius=321e-3 / 2,
                shore_hardness=65
            ),
            velocity=1,
            gap=13.5e-3,
            coulomb_friction_coefficient=0.4,
            rolled_billets=4,
        ),
        Transport(
            label="I -> II",
            duration=6.4
        ),
        RollPass(
            label="K 05/001 - 2",
            roll=Roll(
                groove=RoundGroove(
                    r1=4e-3,
                    r2=18e-3,
                    depth=17.5e-3
                ),
                nominal_radius=321e-3 / 2,
                shore_hardness=65
            ),
            velocity=1,
            gap=1.5e-3,
            coulomb_friction_coefficient=0.4,
            rolled_billets=4,
        ),
        Transport(
            label="II -> III",
            duration=3.6
        ),
        RollPass(
            label="K 02/001 - 3",
            roll=Roll(
                groove=SwedishOvalGroove(
                    r1=6e-3,
                    r2=26e-3,
                    ground_width=38e-3,
                    usable_width=60e-3,
                    depth=7.25e-3
                ),
                nominal_radius=321e-3 / 2,
                shore_hardness=65
            ),
            velocity=2,
            gap=1.5e-3,
            coulomb_friction_coefficient=0.4,
            rolled_billets=4,
        ),
        Transport(
            label="III -> IV",
            duration=3.4
        ),
        RollPass(
            label="K 05/002 - 4",
            roll=Roll(
                groove=RoundGroove(
                    r1=4e-3,
                    r2=13.5e-3,
                    depth=12.5e-3
                ),
                nominal_radius=321e-3 / 2,
                shore_hardness=65
            ),
            velocity=2,
            gap=1e-3,
            coulomb_friction_coefficient=0.4,
            rolled_billets=4,
        ),
        Transport(
            label="IV -> V",
            duration=5.2
        ),
        RollPass(
            label="K 03/001 - 5",
            roll=Roll(
                groove=CircularOvalGroove(
                    r1=6e-3,
                    r2=38e-3,
                    depth=4e-3
                ),
                nominal_radius=321e-3 / 2,
                shore_hardness=65
            ),
            velocity=2,
            gap=5.4e-3,
            coulomb_friction_coefficient=0.4,
            rolled_billets=4,
        )
    ]
    )

    try:
        sequence.solve(in_profile)
    finally:
        print("\nLog:")
        print(caplog.text)

    try:
        import pyroll.report

        report = pyroll.report.report(sequence)
        f = tmp_path / "report.html"
        f.write_text(report, encoding="utf-8")
        webbrowser.open(f.as_uri())

    except ImportError:
        pass
