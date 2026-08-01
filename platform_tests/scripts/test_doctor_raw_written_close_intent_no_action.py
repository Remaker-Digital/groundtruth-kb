"""WI-5811 (detection slice): doctor guard for raw-written close-intent NO-ACTION.

Covers ``doctor._check_raw_written_close_intent_no_action``:
- untracked top-level NO-ACTION with close/disposal body -> WARN (the raw-write
  vector that bypasses every write-time gate; 2026-07-31 Goose auto-disposition).
- untracked top-level NO-ACTION with a genuine correction directive -> no WARN
  (reuses the gate's N1 ∪ N2 close-intent detector, 0/269 false-positive).
- a close-intent NO-ACTION under bridge/cleanup-evidence/** -> no WARN (already
  quarantined; the check scopes to the live top-level chain, mirroring the
  non-recursive glob("*.md") the actionability parsers use).
- fail-soft: severity is WARN, never FAIL; missing bridge dir / absent gate ->
  info.

``_run_cmd`` is monkeypatched to simulate ``git ls-files --others`` output; the
real compliance-gate hook is copied into the tmp target so the check's dynamic
detector import resolves.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for _p in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), str(_PACKAGE_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from groundtruth_kb.project import doctor  # noqa: E402

_GATE_SRC = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"

CLOSE_INTENT_BODY = (
    "NO-ACTION\n\n"
    "bridge_kind: pb_respond\n"
    "Responds to: bridge/foo-002.md\n\n"
    "# Prime Builder Response - NO-ACTION\n\n"
    "## Verdict\nNO-ACTION: Stale GO. No active claim or implementation. Disposition-close.\n\n"
    "## Thread Status\nThis is a terminal disposition. The thread's latest status is now NO-ACTION.\n"
)
LAWFUL_BODY = (
    "NO-ACTION\n\n"
    "bridge_kind: pb_no_action\n"
    "Responds to: bridge/bar-002.md\n\n"
    "# Prime Builder NO-ACTION - governance-noncompliant verdict\n\n"
    "## Verdict\nNO-ACTION. The version-002 GO cites a PAUTH that does not cover the target paths.\n\n"
    "## Required Loyal Opposition Correction\n"
    "Loyal Opposition must re-issue a corrected GO citing a PAUTH whose scope includes "
    "scripts/foo.py, or issue NO-GO against the proposal.\n"
)


def _fake_run_cmd(others: list[str]):
    def runner(cmd: list[str], *, timeout: int = 10) -> tuple[bool, str]:
        if "--others" in cmd:
            return (True, "\n".join(others))
        return (False, "")

    return runner


def _prepare(target: Path, files: dict[str, str], *, with_gate: bool = True) -> None:
    (target / "bridge").mkdir(parents=True, exist_ok=True)
    for rel, body in files.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    if with_gate:
        dst = target / ".claude" / "hooks" / "bridge-compliance-gate.py"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_GATE_SRC, dst)


def test_close_intent_no_action_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare(tmp_path, {"bridge/foo-003.md": CLOSE_INTENT_BODY})
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/foo-003.md"]))

    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status == "warning"
    assert "foo-003.md" in result.message
    assert result.required is False


def test_lawful_no_action_no_warn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare(tmp_path, {"bridge/bar-003.md": LAWFUL_BODY})
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/bar-003.md"]))

    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status == "pass"


def test_quarantine_subtree_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A close-intent file already relocated under cleanup-evidence must NOT re-alarm.
    rel = "bridge/cleanup-evidence/incident-20260731/foo-003.md"
    _prepare(tmp_path, {rel: CLOSE_INTENT_BODY})
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd([rel]))

    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status == "pass"
    assert "foo-003.md" not in result.message


def test_failsoft_severity_never_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare(tmp_path, {"bridge/foo-003.md": CLOSE_INTENT_BODY})
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/foo-003.md"]))

    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status != "fail"


def test_missing_bridge_dir_is_info(tmp_path: Path) -> None:
    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status == "info"


def test_absent_gate_is_info(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare(tmp_path, {"bridge/foo-003.md": CLOSE_INTENT_BODY}, with_gate=False)
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/foo-003.md"]))

    result = doctor._check_raw_written_close_intent_no_action(tmp_path)

    assert result.status == "info"
