import importlib.util

from . import profile
from . import roll_pass
from pyroll.core import config as _config

VERSION = "3.0.0"


@_config("PYROLL_PILLAR_MODEL")
class Config:
    PILLAR_COUNT = 30
    PILLAR_TYPE = "EQUIDISTANT"
    ELONGATION_CORRECTION = True


REPORT_INSTALLED = bool(importlib.util.find_spec("pyroll.report"))


if REPORT_INSTALLED:
    from . import report
    import pyroll.report

    pyroll.report.plugin_manager.register(report)
