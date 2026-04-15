"""Entry point for ``python -m groundtruth_kb``.

Zero-side-effect shim that delegates to :func:`groundtruth_kb.cli.main` so
the package supports module-style invocation in addition to the installed
``gt`` console script. Useful for CI matrices that want to avoid
console-script path resolution and for one-off debugging via
``python -m groundtruth_kb <command>``.

This module intentionally performs no work at import time beyond the
function import. All side effects happen inside :func:`cli.main`, which
is only invoked when this module is run as the program entry point.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from groundtruth_kb.cli import main

if __name__ == "__main__":
    main()
