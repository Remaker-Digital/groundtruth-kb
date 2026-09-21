# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Guard live release surfaces against retired dispatch-substrate residue."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    ".claude",
    ".codex",
    "config",
    "groundtruth-kb/docs",
    "groundtruth-kb/templates",
    "groundtruth-kb/tests",
    "platform_tests",
    "scripts",
)

FORBIDDEN_PATTERNS = (
    "".join(("cross", "_", "harness", "_", "bridge", "_", "trigger")),
    "".join(("cross", "-", "harness", "-", "trigger")),
    "".join(("cross", "_", "harness", "_", "trigger")),
)

SKIPPED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache"})


EXCLUDED_RELATIVE_PATHS = frozenset(
    {
        "config/governance/timer-inventory.toml",
        "memory/topics/reference_openai_api_key.md",
        ".quality/release-candidate-tracked-secrets.json",
        "groundtruth-kb/tests/fixtures/bridge_spike_minimized_governance_hooks/credential_scan.py",
        "applications/Agent_Red/docs/owner-messages-all.json",
    }
)


def _candidate_files(root: Path, project_root: Path = PROJECT_ROOT) -> list[Path]:
    out: list[Path] = []
    for path in [root] if root.is_file() else root.rglob("*") if root.is_dir() else []:
        if not path.is_relative_to(project_root):
            continue
        relative = path.relative_to(project_root)
        if relative.as_posix() in EXCLUDED_RELATIVE_PATHS:
            continue
        if any(part in SKIPPED_DIR_NAMES for part in relative.parts):
            continue
        if path.is_file():
            out.append(path)
    return out


def test_retired_dispatch_substrate_terms_absent_from_live_release_surfaces() -> None:
    hits: list[str] = []
    for rel_root in SCAN_ROOTS:
        for path in _candidate_files(PROJECT_ROOT / rel_root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    rel_path = path.relative_to(PROJECT_ROOT).as_posix()
                    hits.append(f"{rel_path}: {pattern}")

    assert hits == []


def test_content_scan_omits_excluded_paths_but_keeps_neighboring_sources(tmp_path) -> None:
    for relative in EXCLUDED_RELATIVE_PATHS:
        excluded = tmp_path / relative
        excluded.parent.mkdir(parents=True, exist_ok=True)
        excluded.write_text("excluded fixture", encoding="utf-8")
    included = tmp_path / "config/governance/ordinary.toml"
    included.write_text("ordinary source", encoding="utf-8")
    assert _candidate_files(tmp_path, tmp_path) == [included]
