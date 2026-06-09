"""Minimal conftest for scripts tests.

Shields these tests from the project's heavy root conftest by providing a
minimal no-op set of fixtures. No FastAPI, no Cosmos mocks, no tenant wiring.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True, scope="session")
def mock_harness_registry_for_tests() -> None:
    """Mock the harness-registry.json to ensure suspended harnesses are active in tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_registry = Path(tmpdir) / "harness-registry.json"

        # Load the real harness-registry.json
        real_registry_path = REPO_ROOT / "harness-state" / "harness-registry.json"
        if real_registry_path.exists():
            try:
                data = json.loads(real_registry_path.read_text(encoding="utf-8"))
                # Make all harnesses active for tests so suspended states don't break them
                for h in data.get("harnesses", []):
                    h["status"] = "active"

                # Write to the temp registry
                tmp_registry.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

        # Set the environment variable
        old_val = os.environ.get("GTKB_HARNESS_REGISTRY_PATH")
        os.environ["GTKB_HARNESS_REGISTRY_PATH"] = str(tmp_registry)
        try:
            yield
        finally:
            if old_val is not None:
                os.environ["GTKB_HARNESS_REGISTRY_PATH"] = old_val
            else:
                os.environ.pop("GTKB_HARNESS_REGISTRY_PATH", None)
