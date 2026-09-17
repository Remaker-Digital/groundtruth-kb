"""Native authority selection from nested and foreign working directories.

The retired registry reader has no current authority. These cases preserve the
root-selection obligation through the ordinary CLI and exact native binding.
They do not restore cached role files or qualify an actual harness host.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys

import pytest

from platform_tests.groundtruth_kb.test_deepseek_sdk_harness import _serve_authority
from platform_tests.groundtruth_kb.test_harness_diagnostic import bind, register
from platform_tests.groundtruth_kb.test_native_authority_service import history_count
from platform_tests.groundtruth_kb.test_native_authority_service import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def selected_authority(native, tmp_path):
    service, client, *_ = native
    register(client)
    selected = bind(client, "selected-context", "pb")
    bind(client, "other-context", "lo")
    before = history_count(service)
    root = tmp_path / "selected"
    root.mkdir()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(root, port)
    try:
        config = root / "groundtruth.toml"
        config.write_text(f'[groundtruth]\nauthority_url="http://127.0.0.1:{port}"\n', encoding="utf-8")
        # The test selects the authority through configuration, not ambient roots.
        for name in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT"):
            env.pop(name, None)
        env["PYTHONIOENCODING"] = "utf-8"

        def gt(cwd, context, *, explicit=False):
            command = [sys.executable, "-m", "groundtruth_kb"]
            if explicit:
                command.extend(["--config", str(config)])
            command.extend(["harness", "diagnostic", "--harness-id", "A", "--native-context-id", context, "--json"])
            result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, encoding="utf-8", timeout=30)
            assert result.returncode == 0, result.stdout + result.stderr
            return json.loads(result.stdout)

        yield root, selected, gt
        assert history_count(service) == before, "Diagnostic reads must not create or amend native records"
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=15)


@pytest.mark.parametrize("context", ["selected-context", "absent-context"])
def test_native_cli_from_nested_directory_uses_parent_configuration(selected_authority, context):
    root, binding, gt = selected_authority
    nested = root / "source" / "module"
    nested.mkdir(parents=True)
    report = gt(nested, context)

    assert report["harness"]["harness_id"] == "A"
    assert report["role"]["native_context_id"] == context
    if context == "selected-context":
        assert report["role"]["session_context_id"] == binding["session_context_id"]
        assert report["role"]["role"] == "prime-builder"
        assert report["role"]["source"] == "native_session_binding"
    else:
        assert report["role"]["session_context_id"] is None
        assert report["role"]["role"] is None
        assert report["role"]["unavailable_reason"] == "no_session_binding"
    assert report["parity"]["status"] == "unqualified"
    assert list(nested.iterdir()) == [], "Nested invocation must not create local state"
    assert not (root / "groundtruth.db").exists()
    assert not (root / "harness-state").exists()


def test_native_cli_explicit_configuration_wins_over_foreign_cwd(selected_authority, tmp_path):
    root, binding, gt = selected_authority
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    decoy = foreign / "groundtruth.toml"
    decoy.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    before = decoy.read_bytes()
    report = gt(foreign, "selected-context", explicit=True)

    assert report["role"]["session_context_id"] == binding["session_context_id"]
    assert report["role"]["role"] == "prime-builder"
    assert report["parity"]["status"] == "unqualified"
    assert list(foreign.iterdir()) == [decoy]
    assert decoy.read_bytes() == before
    assert not (root / "groundtruth.db").exists()
    assert not (root / "harness-state").exists()
