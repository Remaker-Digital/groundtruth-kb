"""AXIS 2 surface terminal-kind-GO suppression tests.

Authority:
- bridge/gtkb-axis-2-dispatchable-filter-003.md (REVISED-1)
- bridge/gtkb-axis-2-dispatchable-filter-004.md (Codex GO)
- WI-4278 under PROJECT-GTKB-RELIABILITY-FIXES (fast-lane per
  GOV-RELIABILITY-FAST-LANE-001).

Verifies that .claude/hooks/bridge-axis-2-surface.py honors the
centrally-computed `dispatchable` flag attached by
groundtruth_kb.bridge.notify.compute_actionable_pending, so terminal-kind GO
threads (governance_review, scoping, closure, parking, index/thread
reconciliation, operational_state_change, candidate_spec_intake) no longer
re-fire the in-session AXIS 2 surface. ADVISORY remains visible because it is
non-dispatchable Axis-2 work for interactive Prime disposition.

The fix is consumer-side: the upstream `_KIND_TERMINAL_TOKENS` /
`_derive_dispatchable` rule already published dispatchable=False for these
GO entries; the AXIS 2 hook previously ignored the field. The hook now
applies the compatibility-safe `getattr(item, "dispatchable", True)` filter,
matching the idiom in scripts/cross_harness_bridge_trigger.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))
_SCRIPTS = REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

_HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "bridge-axis-2-surface.py"


def _load_hook(project_root: Path) -> ModuleType:
    """Import the hook module fresh and rebind its PROJECT_ROOT to a tmp dir."""
    src_helper = REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "scan_bridge.py"
    dst_helper = project_root / ".claude" / "skills" / "bridge" / "helpers" / "scan_bridge.py"
    dst_helper.parent.mkdir(parents=True, exist_ok=True)
    dst_helper.write_bytes(src_helper.read_bytes())

    spec = importlib.util.spec_from_file_location("_test_axis2_dispatchable_filter", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PROJECT_ROOT = project_root
    return module


def _write_fixture(
    tmp_path: Path,
    *,
    slug: str,
    top_status: str,
    bridge_kind: str,
    operative_version: str = "001",
    top_version: str | None = None,
) -> None:
    """Write a fixture bridge thread to tmp_path.

    Creates:
    - bridge/INDEX.md with one Document entry, top-version line at `top_status`.
    - bridge/<slug>-<operative_version>.md with the cited `bridge_kind:` header.
    - bridge/<slug>-<top_version>.md for verdict files (GO/NO-GO) when separate.

    The hook reads bridge/INDEX.md via the canonical parse_index, which expects
    INDEX entries to point at files that exist on disk; missing files cause the
    entry to be excluded.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    if top_version is None:
        top_version = operative_version

    op_filename = f"bridge/{slug}-{operative_version}.md"
    top_filename = f"bridge/{slug}-{top_version}.md"

    # INDEX: Document header + top-line first, then operative if different.
    index_lines = [f"Document: {slug}\n", f"{top_status}: {top_filename}\n"]
    if top_version != operative_version:
        index_lines.append(f"NEW: {op_filename}\n")
    (bridge_dir / "INDEX.md").write_text("".join(index_lines), encoding="utf-8")

    # Operative file with bridge_kind header.
    operative_status = top_status if top_version == operative_version else "NEW"
    operative_body = (
        f"{operative_status}\n\nbridge_kind: {bridge_kind}\n"
        f"Document: {slug}\nVersion: {operative_version}\n\nFixture proposal body.\n"
    )
    (bridge_dir / f"{slug}-{operative_version}.md").write_text(operative_body, encoding="utf-8")

    # Top verdict file (GO/NO-GO) if separate from operative.
    if top_version != operative_version:
        verdict_body = f"{top_status}\n\nDocument: {slug}\nVersion: {top_version}\nVerdict.\n"
        (bridge_dir / f"{slug}-{top_version}.md").write_text(verdict_body, encoding="utf-8")


def test_governance_review_go_excluded_from_axis_2_surface(tmp_path: Path) -> None:
    """Primary regression: a governance_review GO must not appear on the surface.

    Pre-fix behavior: entry passes through to the signature and to the rendered
    markdown table. Post-fix behavior: filter drops the entry because
    `_derive_dispatchable` returns False for terminal-kind GO.
    """
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-gov-review-go",
        top_status="GO",
        bridge_kind="governance_review",
        operative_version="001",
        top_version="002",
    )

    signature, items = mod._compute_actionable_for_role(mod.ROLE_PRIME)

    assert items == [], (
        "Expected empty items for a governance_review GO (terminal-kind); the "
        "AXIS 2 surface must mirror cross-harness trigger dispatch suppression."
    )
    # Empty-list signature is deterministic (hash of empty JSON array).
    import hashlib
    import json

    expected_empty_sig = hashlib.sha256(
        json.dumps([], sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert signature == expected_empty_sig, "Signature must reflect the post-filter (empty) item set."


def test_implementation_proposal_go_remains_actionable(tmp_path: Path) -> None:
    """Non-regression: a real implementation_proposal GO stays on the surface."""
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-impl-go",
        top_status="GO",
        bridge_kind="implementation_proposal",
        operative_version="001",
        top_version="002",
    )

    signature, items = mod._compute_actionable_for_role(mod.ROLE_PRIME)

    assert len(items) == 1, "implementation_proposal GO must remain Prime-actionable (dispatchable=True)."
    assert items[0].document_name == "fixture-impl-go"
    assert items[0].top_status == "GO"
    assert signature, "Signature must be non-empty when items are present."


def test_advisory_entry_surfaces_despite_non_dispatchable(tmp_path: Path) -> None:
    """WI-4548 regression: ADVISORY is non-dispatchable but Prime-visible."""
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-advisory",
        top_status="ADVISORY",
        bridge_kind="loyal_opposition_advisory",
        operative_version="001",
    )

    signature, items = mod._compute_actionable_for_role(mod.ROLE_PRIME)

    assert len(items) == 1, "ADVISORY must remain visible to the Prime AXIS-2 surface."
    assert items[0].document_name == "fixture-advisory"
    assert items[0].top_status == "ADVISORY"
    assert signature, "Signature must be non-empty when ADVISORY items are present."


def test_no_go_entry_remains_actionable_regardless_of_kind(tmp_path: Path) -> None:
    """Non-regression: a NO-GO is always dispatchable=True per _derive_dispatchable,
    regardless of the operative proposal's bridge_kind. Prime revision flows
    for terminal-kind NO-GO must be preserved."""
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-gov-review-nogo",
        top_status="NO-GO",
        bridge_kind="governance_review",
        operative_version="001",
        top_version="002",
    )

    _signature, items = mod._compute_actionable_for_role(mod.ROLE_PRIME)

    assert len(items) == 1, "NO-GO must remain Prime-actionable even when operative bridge_kind is terminal."
    assert items[0].document_name == "fixture-gov-review-nogo"
    assert items[0].top_status == "NO-GO"


def test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind(tmp_path: Path) -> None:
    """Non-regression: NEW/REVISED entries are always dispatchable=True per
    _derive_dispatchable, regardless of bridge_kind. Codex review flows for
    terminal-kind proposals must be preserved."""
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-gov-review-new",
        top_status="NEW",
        bridge_kind="governance_review",
        operative_version="001",
    )

    _signature, items = mod._compute_actionable_for_role(mod.ROLE_LO)

    assert len(items) == 1, "NEW must remain Loyal-Opposition-actionable even when bridge_kind is terminal."
    assert items[0].document_name == "fixture-gov-review-new"
    assert items[0].top_status == "NEW"
