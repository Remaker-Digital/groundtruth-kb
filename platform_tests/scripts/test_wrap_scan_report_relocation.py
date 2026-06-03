"""WI-4259 — wrap-scan report relocation regression tests.

Covers the spec-derived verification plan from
`bridge/gtkb-wrap-scan-report-relocation-slice-1-001.md` (GO at -002):

- the session-wrap SKILLs write wrap-scan reports to the sibling
  `.groundtruth/session/wrap-scan-reports/<id>/` dir, NOT into the manifest-only
  `.groundtruth/session/snapshots/<id>/` dir (the relocation);
- `.claude` and `.codex` mirrors agree on the relocated report paths (parity);
- a manifest-only snapshot dir yields no `check_snapshots_non_manifest` findings
  (preserved invariant); and
- a stray non-manifest file under the snapshot dir is still flagged
  SEVERITY_ERROR (the manifest-only gate is NOT weakened — owner constraint).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from wrap_scan_hygiene import (  # noqa: E402  (path inserted above)
    SEVERITY_ERROR,
    check_snapshots_non_manifest,
)

_WRAP_SKILLS = (
    _REPO_ROOT / ".claude" / "skills" / "kb-session-wrap" / "SKILL.md",
    _REPO_ROOT / ".claude" / "skills" / "kb-session-wrap-scan" / "SKILL.md",
    _REPO_ROOT / ".codex" / "skills" / "kb-session-wrap" / "SKILL.md",
    _REPO_ROOT / ".codex" / "skills" / "kb-session-wrap-scan" / "SKILL.md",
)

# Anti-patterns: a wrap-scan report path rooted in the manifest-only snapshot dir.
_SNAPSHOT_REPORT_ANTIPATTERNS = (
    "${SNAP_DIR}/wrap-scan",
    "snapshots/<SESSION_ID>/wrap-scan",
    "snapshots/${SESSION_ID}/wrap-scan",
)


# --------------------------------------------------------------------------
# SKILL.md relocation (doc-content regression)
# --------------------------------------------------------------------------


def test_session_wrap_skills_write_reports_to_sibling_dir() -> None:
    """All 4 SKILLs reference the sibling reports dir and no wrap-scan report
    path under the manifest-only snapshot dir."""
    for skill in _WRAP_SKILLS:
        content = skill.read_text(encoding="utf-8")
        assert "wrap-scan-reports" in content, f"{skill} missing relocated report dir"
        for bad in _SNAPSHOT_REPORT_ANTIPATTERNS:
            assert bad not in content, f"{skill} still writes a wrap-scan report under snapshots/: {bad!r}"


def _report_path_lines(content: str) -> list[str]:
    """Lines that reference a relocated wrap-scan report path."""
    return sorted(line.strip() for line in content.splitlines() if "wrap-scan-reports" in line and "wrap-scan-" in line)


def test_claude_codex_report_paths_parity() -> None:
    """The relocated report-path lines match between each .claude SKILL and its
    .codex mirror."""
    for name in ("kb-session-wrap", "kb-session-wrap-scan"):
        claude = (_REPO_ROOT / ".claude" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        codex = (_REPO_ROOT / ".codex" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        claude_lines = _report_path_lines(claude)
        codex_lines = _report_path_lines(codex)
        assert claude_lines, f"{name}: no relocated report-path lines found in .claude SKILL"
        assert claude_lines == codex_lines, f"{name}: .claude/.codex report-path drift"


# --------------------------------------------------------------------------
# check_snapshots_non_manifest invariant (UNCHANGED by this slice)
# --------------------------------------------------------------------------


def _make_snapshot(root: Path, session_id: str, *, extra: dict[str, str] | None = None) -> None:
    snap = root / ".groundtruth" / "session" / "snapshots" / session_id
    snap.mkdir(parents=True, exist_ok=True)
    (snap / "manifest.json").write_text(json.dumps({"manifest_schema_version": 1}), encoding="utf-8")
    for name, body in (extra or {}).items():
        (snap / name).write_text(body, encoding="utf-8")


def test_manifest_only_snapshot_dir_clean(tmp_path: Path) -> None:
    """With reports relocated, a manifest-only snapshot dir yields no findings."""
    _make_snapshot(tmp_path, "S-CLEAN")
    findings = check_snapshots_non_manifest(tmp_path)
    assert findings == [], f"manifest-only dir should be clean, got {findings}"


def test_stray_non_manifest_still_flagged(tmp_path: Path) -> None:
    """The manifest-only gate is NOT weakened: a stray non-manifest file is still
    flagged SEVERITY_ERROR (owner constraint — check_snapshots_non_manifest unchanged)."""
    _make_snapshot(tmp_path, "S-STRAY", extra={"transcript.jsonl": "{}"})
    findings = check_snapshots_non_manifest(tmp_path)
    assert len(findings) == 1, f"expected exactly one stray finding, got {findings}"
    finding = findings[0]
    assert finding["check"] == "snapshots_non_manifest"
    assert finding["severity"] == SEVERITY_ERROR
    assert "transcript.jsonl" in finding["message"]
