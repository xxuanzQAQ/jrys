"""init"""

from gsuid_core.sv import Plugins

Plugins(name="JRYS", force_prefix=[], allow_empty_prefix=True)

from . import jrys  # noqa: F401, E402

