import os as _os
import sys as _sys
from typing import Optional as _Optional

basepath: _Optional[str] = None
if getattr(_sys, "frozen", False):
    basepath = _sys._MEIPASS
else:
    basepath = _os.path.dirname(_os.path.abspath(__file__))

config_path: str = _os.path.join(basepath, "config")
cache_path: str = _os.path.join(basepath, "cache")
