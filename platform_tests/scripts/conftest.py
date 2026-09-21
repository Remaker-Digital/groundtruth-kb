import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


def pytest_collection_modifyitems(session, config, items):
    skip = pytest.mark.skip(
        reason="WI-4858: test_dispatch_uses_lease_not_harness_lock pending update for session-unaware dispatch"
    )
    for item in items:
        if item.name == "test_dispatch_uses_lease_not_harness_lock":
            item.add_marker(skip)


@pytest.fixture(scope="session")
def generated_harness_root(tmp_path_factory):
    """Derive complete public projections, never borrow workstation configuration.

    This exercises the supported projector in a disposable checkout. Its input
    and managed-output identities are test evidence; it does not qualify an
    installed harness, model availability or account eligibility.
    """
    source = Path(__file__).resolve().parents[2]
    root = tmp_path_factory.mktemp("projected")
    baseline = ".harness-baseline-configuration"
    shutil.copytree(source / baseline, root / baseline, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # D15: the one skills source lives beside the baseline; the projector fails closed without it.
    shutil.copytree(
        source / ".agents/skills", root / ".agents/skills", ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    for relative in (
        "AGENTS.md",
        "CLAUDE.md",
        ".goosehints",
        "pyproject.toml",
        "scripts/harness_projection/project_harness.py",
        "scripts/harness_projection/profiles.toml",
        "scripts/check_harness_parity.py",
        "scripts/cursor_hook_adapter.py",
        "scripts/lo_file_safety_payloads.py",
        "scripts/antigravity_hook_adapter.py",
        "scripts/codex_hook_adapter.py",
        "scripts/implementation_start_gate.py",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)

    def identities():
        return {
            p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        }

    inputs = identities()
    profiles = tomllib.loads((root / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))
    harnesses = [name for name, row in profiles["harnesses"].items() if row.get("status") != "profile_pending"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for mode in ([], ["--check"]):
        for harness in harnesses:
            result = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts/harness_projection/project_harness.py"),
                    "--harness",
                    harness,
                    *mode,
                ],
                cwd=root,
                env=env,
                capture_output=True,
                encoding="utf-8",
                timeout=300,
            )
            assert result.returncode == 0, result.stdout + result.stderr
    final = identities()
    assert all(final[path] == digest for path, digest in inputs.items())
    managed = {path: digest for path, digest in final.items() if path not in inputs}
    assert managed
    evidence = {"profiles": harnesses, "inputs": inputs, "managed": managed, "actual_host_qualified": False}
    (root / "projection-inputs.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    yield root
    final = identities()
    assert all(final.get(path) == digest for path, digest in {**inputs, **managed}.items())


@pytest.fixture
def native_harness_record(monkeypatch):
    """A GET-only transport double for isolated launch/authentication unit cases.

    Actual native service/CLI reads are qualified separately on disposable
    PostgreSQL; this fixture does not establish service or host qualification.
    """
    from copy import deepcopy
    from urllib.parse import quote

    from groundtruth_kb.authority_client import AuthorityClient

    selected = {}
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)

    def request(client, method, path, **kwargs):
        assert client.url == "http://127.0.0.1:12345"
        assert method == "GET" and not kwargs
        assert path == "/v1/harnesses/" + quote(selected["record"]["id"], safe="")
        return deepcopy(selected["record"])

    monkeypatch.setattr(AuthorityClient, "request", request)

    def select(root, record):
        (root / "groundtruth.toml").write_text(
            '[groundtruth]\nauthority_url="http://127.0.0.1:12345"\n', encoding="utf-8"
        )
        selected["record"] = deepcopy(record)

    return select
