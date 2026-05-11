"""Minimal conftest for scripts tests.

Shields these tests from the project's heavy root conftest by providing a
minimal no-op set of fixtures. No FastAPI, no Cosmos mocks, no tenant wiring.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
