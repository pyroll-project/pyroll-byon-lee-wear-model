import logging
import webbrowser
import numpy as np
from pathlib import Path
from pyroll.core import Profile, Roll, RollPass, CircularOvalGroove, PassSequence, DeformationUnit


#@DeformationUnit.Profile.flow_stress
#def flow_stress_lee(self: DeformationUnit):
#    strain = self.strain + 0.05
#    strain_rate = self.unit.strain_rate + 0.05
#    return (150 * (1.658 * strain ** 0.403 - self.strain) * strain_rate ** 0.116) * 1e6


def test_solve_round_oval_round(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.byon_lee_wear_model
    import pyroll.lendl_equivalent_method
    import pyroll.wusatowski_spreading
    import pyroll.profile_bulging

    in_profile = Profile.round(
        diameter=60e-3,
        temperature=1000 + 273.15,
        strain=0,
        material=["C10", "steel"],
        flow_stress=100e6,
        length=0.3
    )

    sequence = PassSequence(
        [
            RollPass(
                label="OV-1",
                roll=Roll(
                    material=["DCI", "Cast Iron"],
                    groove=CircularOvalGroove(
                        depth=15.5e-3,
                        r1=2e-3,
                        r2=60.5e-3
                    ),
                    nominal_radius=155e-3,
                    rotational_frequency=0.56,
                    shore_hardness=65
                ),
                gap=6.5e-3,
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
        from pyroll.report import report
        report = report(sequence)
        f = tmp_path / "report.html"
        f.write_text(report)
        webbrowser.open(f.as_uri())
    except ImportError:
        pass

 #   assert np.isclose(sequence.out_profile.cross_section.area, 2060e-6, atol=0.1)
  #  assert np.isclose(sequence.out_profile.wear_depth, 0.3e-3, atol=0.1)
