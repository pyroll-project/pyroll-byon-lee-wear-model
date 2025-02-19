import importlib.util

from . import roll_pass

REPORT_INSTALLED = bool(importlib.util.find_spec("pyroll.report"))

VERSION = "3.0.0"

if REPORT_INSTALLED:
    from pyroll.report import plugin_manager
    from . import report
    plugin_manager.register(report)