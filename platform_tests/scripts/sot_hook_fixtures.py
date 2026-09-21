"""Shared helpers of the SoT read-discipline hook qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_sot_read_discipline_hook.py`` (``HOOK``, ``SUBSTITUTE``, ``REGISTRY``,
``registry``, ``identities``, ``run_hook``) so that no test module imports another test module.
Not collected; defines no test.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

from groundtruth_kb.project.registry_control_plane import load_registry_snapshot

HOOK = Path(".harness-baseline-configuration/hooks/sot-read-discipline.py")
SUBSTITUTE = "derived/status.txt"
REGISTRY = """[[artifacts]]
id = "fixture-work"
domain = "control_surface"
lifecycle = "active"
storage_path = "membase:work_items"
coverage_mode = "virtual"
authority_spec_id = "GOV-SOURCE-OF-TRUTH-FRESHNESS-001"
mutation_api = "gt backlog"
versioning_policy = "git_tracked"
backup_policy = "git_tracked"
health_check_function = ""
owner_role = "shared"
forbidden_substitutes = ["derived/status.txt", "derived/children/**"]
"""


def registry(root: Path, text: str = REGISTRY) -> Path:
    path = root / "config/registry/sot-artifacts.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    assert len(load_registry_snapshot(project_root=root).records) == len(tomllib.loads(text).get("artifacts", []))
    return path


def identities(root: Path) -> dict:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def run_hook(root: Path, payload, *, hook: Path = HOOK, cwd: Path | None = None, bypass=False) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    env.pop("GTKB_SOT_READ_DISCIPLINE_BYPASS", None)
    if bypass:
        env["GTKB_SOT_READ_DISCIPLINE_BYPASS"] = "1"
    before = identities(root)
    # Verify the child's actual import origin without adding product diagnostics.
    code = (
        "import os,runpy,sys; from pathlib import Path; "
        'm=runpy.run_path(sys.argv[1]); result=m["main"](); '
        'p=sys.modules.get("groundtruth_kb"); expected=os.environ.get("GTKB_EXPECTED_PACKAGE_ROOT"); '
        "assert not p or not expected or Path(p.__file__).resolve().is_relative_to(Path(expected).resolve()); "
        "raise SystemExit(result)"
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(root / hook)],
        input=json.dumps(payload),
        capture_output=True,
        encoding="utf-8",
        cwd=cwd or root,
        env=env,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert identities(root) == before, "The read hook changed its selected source tree"
    return json.loads(result.stdout)
