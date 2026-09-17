"""Declared shell registrations, explicit read-policy fixtures and unchanged write extraction.

These controlled cases do not establish actual native host invocation or complete
TEST-12284, whose remaining write-gate equivalence obligations remain open.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot

from platform_tests.scripts.test_sot_read_discipline_hook import registry, run_hook

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_HOOKS = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks"
MANIFEST = BASELINE_HOOKS / "hooks.manifest.toml"
if not MANIFEST.exists():
    MANIFEST = BASELINE_HOOKS / "manifest.toml"

SOT_GATE = BASELINE_HOOKS / "sot-read-discipline.py"

SOT_REGISTRY = PROJECT_ROOT / "config" / "registry" / "sot-artifacts.toml"

# The shell-covered gates that remain after the module-removal batch: two write gates plus the read gate.
SHELL_COVERED_SCRIPTS = {
    "document_author_provenance_gate.py",
    "code-quality-baseline-proposal-check.py",
    "sot-read-discipline.py",
}


def _manifest_hooks() -> list[dict]:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8")).get("hook", [])


def _run_hook(hook: Path, payload: dict, env_extra: dict | None = None) -> dict:
    import os

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        timeout=60,
    )
    raw = (result.stdout or "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_unparsed": raw}


def _decision(response: dict) -> tuple[str | None, str]:
    """Normalize the two emit shapes the gates use into (decision, reason)."""
    if "hookSpecificOutput" in response:
        block = response["hookSpecificOutput"]
        return block.get("permissionDecision"), block.get("permissionDecisionReason") or ""
    if "decision" in response:
        return response.get("decision"), response.get("reason") or ""
    return None, ""


@pytest.fixture
def read_policy(tmp_path):
    import shutil

    root = tmp_path / "read-policy"
    hook = root / ".harness-baseline-configuration/hooks/sot-read-discipline.py"
    hook.parent.mkdir(parents=True)
    shutil.copyfile(SOT_GATE, hook)
    registry(root)
    return root


def _forbidden_substitutes(root: Path) -> list[str]:
    paths = [path for row in load_registry_snapshot(project_root=root).records for path in row.forbidden_substitutes]
    assert paths, "The behavioral fixture must exercise an actual declared restriction"
    return [path.replace("**", "nested/current.txt") for path in paths]


# --------------------------------------------------------------------------
# Manifest declarations (the defect this work item repairs)
# --------------------------------------------------------------------------


def test_every_shell_covered_gate_declares_shell_exec() -> None:
    """No pre-tool-use write or read gate may omit shell_exec.

    This is the assertion that fails if the defect regresses: a gate declared
    without shell_exec is not registered against shell events, so it guards a
    path the shell can still reach freely.
    """
    missing = [
        hook["script"]
        for hook in _manifest_hooks()
        if hook.get("event") == "pre_tool_use"
        and hook.get("script") in SHELL_COVERED_SCRIPTS
        and "shell_exec" not in (hook.get("intents") or [])
    ]
    assert missing == [], f"gates registered without shell_exec: {missing}"


def test_sot_gate_declares_shell_exec() -> None:
    """DCL-SOT-READ-HOOK-CONTRACT-001 specifies a two-surface hook."""
    hooks = [h for h in _manifest_hooks() if h.get("script") == "sot-read-discipline.py"]
    assert hooks, "sot-read-discipline.py is not registered in the baseline manifest"
    intents = hooks[0].get("intents") or []
    assert "read_access" in intents
    assert "shell_exec" in intents


# --------------------------------------------------------------------------
# Observed denial: the acceptance criteria require behavior, not matcher text
# --------------------------------------------------------------------------


def test_shell_read_of_forbidden_substitute_is_denied(read_policy: Path) -> None:
    substitutes = _forbidden_substitutes(read_policy)
    decision, reason = _decision(
        run_hook(read_policy, {"tool_name": "Bash", "tool_input": {"command": f"cat {substitutes[0]}"}})
    )
    assert decision == "block", f"shell read of {substitutes[0]!r} was not blocked (reason={reason!r})"


def test_every_registered_forbidden_substitute_is_denied_on_shell_surface(read_policy: Path) -> None:
    """GOV-SOURCE-OF-TRUTH-FRESHNESS-001 clause (a) must be mechanical, not advisory."""
    substitutes = _forbidden_substitutes(read_policy)
    allowed = []
    for path in substitutes:
        decision, _ = _decision(run_hook(read_policy, {"tool_name": "Bash", "tool_input": {"command": f"cat {path}"}}))
        if decision != "block":
            allowed.append(path)
    assert allowed == [], f"forbidden substitutes readable via shell: {allowed}"


def test_powershell_surface_is_covered(read_policy: Path) -> None:
    """Claude renders shell_exec to Bash|PowerShell; matching only "Bash" leaves half the surface open."""
    substitutes = _forbidden_substitutes(read_policy)
    decision, _ = _decision(
        run_hook(
            read_policy,
            {"tool_name": "PowerShell", "tool_input": {"command": f"Get-Content {substitutes[0]}"}},
        )
    )
    assert decision == "block"


def test_owner_bypass_still_permits_forbidden_substitute_read(read_policy: Path) -> None:
    """GO binding condition 3: the owner-authorized bypass must survive registration."""
    substitutes = _forbidden_substitutes(read_policy)
    response = run_hook(
        read_policy,
        {"tool_name": "Bash", "tool_input": {"command": f"cat {substitutes[0]}"}},
        bypass=True,
    )
    decision, _ = _decision(response)
    assert decision != "block"


# --------------------------------------------------------------------------
# Over-blocking guards (GO binding condition 2)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "git status --porcelain",
        "ls -la",
        "python -m pytest -q",
        'grep -rn "a > b" src/',  # a redirect character inside quotes is data
        "python build.py 2> err.log",  # file-descriptor prefix, not a plain write
        "cat README.md",
    ],
)
@pytest.mark.parametrize("gate", [SOT_GATE])
def test_unrecognized_or_read_only_commands_stay_allowed(gate: Path, command: str) -> None:
    decision, reason = _decision(_run_hook(gate, {"tool_name": "Bash", "cwd": ".", "tool_input": {"command": command}}))
    assert decision not in {"deny", "block"}, (
        f"{gate.name} over-blocked a benign command {command!r} (reason={reason!r})"
    )


# --------------------------------------------------------------------------
# Extraction unit behavior
# --------------------------------------------------------------------------


def _shell_payload_module():
    if str(BASELINE_HOOKS) not in sys.path:
        sys.path.insert(0, str(BASELINE_HOOKS))
    import _shell_payload

    return _shell_payload


@pytest.mark.parametrize(
    ("command", "expected_path", "expected_form"),
    [
        ("cat > a/b.md <<'EOF'\nbody\nEOF", "a/b.md", "heredoc"),
        ('echo "hi" > a/b.md', "a/b.md", "redirect"),
        ('echo "hi" | tee a/b.md', "a/b.md", "tee"),
        ("sed -i 's/x/y/' a/b.md", "a/b.md", "sed_in_place"),
        ('Set-Content -Path a/b.md -Value "GO"', "a/b.md", "set_content"),
    ],
)
def test_extractor_recognizes_write_forms(command: str, expected_path: str, expected_form: str) -> None:
    module = _shell_payload_module()
    targets = module.extract_write_targets(command, PROJECT_ROOT)
    assert [(t.path, t.form) for t in targets] == [(expected_path, expected_form)]


def test_heredoc_yields_exactly_one_target_carrying_content() -> None:
    """A heredoc must not also register as a content-less redirect for the same path.

    The duplicate would shadow the real write with strictly worse evidence.
    """
    module = _shell_payload_module()
    targets = module.extract_write_targets("cat > a/b.md <<'EOF'\nNEW\nbody\nEOF", PROJECT_ROOT)
    assert len(targets) == 1
    assert targets[0].content == "NEW\nbody"


@pytest.mark.parametrize(
    "command",
    ["git status", 'grep -rn "a > b" src/', "python x.py 2> err.log", "ls"],
)
def test_extractor_returns_no_target_for_non_writes(command: str) -> None:
    module = _shell_payload_module()
    assert module.extract_write_targets(command, PROJECT_ROOT) == []


def test_native_payload_expands_to_itself() -> None:
    module = _shell_payload_module()
    payload = {"tool_name": "Write", "tool_input": {"file_path": "x", "content": "y"}}
    assert module.expand_shell_payload(payload, PROJECT_ROOT) == [payload]


# --------------------------------------------------------------------------
# Cross-harness projection parity
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("harness", "path", "shell_names"),
    [
        ("claude", ".claude/settings.json", ("Bash", "PowerShell")),
        ("cursor", ".cursor/hooks.json", ("Shell", "Bash")),
    ],
)
@pytest.mark.timeout(300)
def test_projected_matchers_include_shell_tool_names(
    harness: str, path: str, shell_names: tuple[str, ...], generated_harness_root: Path
) -> None:
    projection = generated_harness_root / path
    data = json.loads(projection.read_text(encoding="utf-8"))
    events = data.get("hooks", {})
    entries = events.get("PreToolUse") or events.get("preToolUse") or []
    checked = 0
    for script in SHELL_COVERED_SCRIPTS:
        for entry in entries:
            if script not in json.dumps(entry):
                continue
            matcher = entry.get("matcher", "")
            # Nested shape (settings_json groups hooks under a matcher).
            if not matcher and isinstance(entry.get("hooks"), list):
                matcher = entry.get("matcher", "")
            assert all(name in matcher for name in shell_names), (
                f"{harness}: {script} matcher {matcher!r} lacks {shell_names}"
            )
            checked += 1
    assert checked, f"{harness}: no covered gate found in the projection"


@pytest.mark.timeout(300)
def test_goose_registers_gates_without_a_matcher(generated_harness_root: Path) -> None:
    """Goose's registration mode carries no matcher, so coverage there is behavioral.

    Recording this explicitly stops a future reader from concluding the Goose
    projection is missing the shell surface because its entries have no matcher
    string: it never had one, and every PreToolUse hook already receives every
    tool event.
    """
    projection = generated_harness_root / ".goose" / "plugins" / "gtkb" / "hooks" / "hooks.json"
    entries = json.loads(projection.read_text(encoding="utf-8"))["hooks"].get("PreToolUse", [])
    assert entries, "goose PreToolUse registration is empty"
    assert not any("matcher" in entry for entry in entries)


@pytest.mark.parametrize("harness", ["claude", "cursor", "goose"])
@pytest.mark.timeout(300)
def test_projection_is_clean_against_baseline(harness: str, generated_harness_root: Path) -> None:
    """DCL-HARNESS-BASELINE-PROJECTION-CONFORMANCE-001: no hand-edited projection drift."""
    result = subprocess.run(
        [sys.executable, "scripts/harness_projection/project_harness.py", "--harness", harness, "--check"],
        capture_output=True,
        text=True,
        cwd=str(generated_harness_root),
        timeout=300,
    )
    assert result.returncode == 0, f"{harness} projection drift:\n{result.stdout}\n{result.stderr}"
