import logging
import webbrowser
from pathlib import Path

from pyroll.core import Profile, PassSequence, RollPass, Roll, CircularOvalGroove, FalseRoundGroove


def test_solve(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.byon_lee_wear_model
    import pyroll.profile_bulging

    in_profile = Profile.from_groove(
        groove=FalseRoundGroove(
            flank_angle=60,
            r1=0.2e-3,
            r2=10.3e-3,
            depth=8.7e-3
        ),
        gap=2.1e-3,
        filling=20.7 / 21.94,
        temperature=1100 + 273.15,
        strain=0,
        material=["steel"],
        density=7.5e3,
        flow_stress=100e6,
        specific_heat_capacity=690,
        thermal_conductivity=23,
        length=12
    )

    sequence = PassSequence(
        [
            RollPass(
                label="Oval Groove",
                orientation="h",
                roll=Roll(
                    groove=CircularOvalGroove(
                        depth=4.5e-3,
                        r1=1e-3,
                        r2=20e-3,
                    ),
                    nominal_diameter=208e-3,
                    shore_hardness=84
                ),
                velocity=11.7,
                gap=3.5e-3,
                coulomb_friction_coefficient=0.4,
                rolled_billets=3000,

            ),
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
