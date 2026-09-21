"""FAB-05 rule-file retirement — grep-absence / presence regression test.

Encodes the HYG-018/026/027/038 acceptance criteria from
bridge/gtkb-fab-05-rule-file-retirement-003.md (GO at -004) as deterministic
assertions over the live tree. All paths are repo-root-relative.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES = REPO_ROOT / ".harness-baseline-configuration" / "rules"


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


# ---- HYG-018: OS-poller stack archived; runbook is a DEPRECATED stub --------


def test_file_bridge_protocol_no_poller_cadence():
    text = _read(".harness-baseline-configuration/rules/file-bridge-protocol.md")
    assert "every 3 minutes" not in text
    assert "scheduled every 3 minutes" not in text
    assert "automated every 3 minutes" not in text


# ---- HYG-026: Cursor-era rule files archived; index path corrected ----------


def test_no_playground_link_in_active_rules():
    # The HYG-026 concern is a live markdown LINK to an out-of-root Claude-Playground
    # path (the Cursor-era dashboard runbook had one). project-root-boundary.md
    # legitimately discusses the E:\Claude-Playground archive boundary in prose, so
    # only the clickable-link form is forbidden in active auto-loaded rules.
    for rule in RULES.glob("*.md"):
        low = rule.read_text(encoding="utf-8").lower()
        assert "](e:/claude-playground" not in low, f"Playground link in {rule.name}"
        assert "](e:\\claude-playground" not in low, f"Playground link in {rule.name}"


# ---- HYG-027: duplicated normative blocks deduped ---------------------------


def test_report_depth_context_is_pointer_stub():
    # Pointer-not-delete: the file still exists (required by the governance-adoption
    # test + skill frontmatter) but now points to canonical report-depth.md.
    p = RULES / "report-depth-prime-builder-context.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "report-depth.md" in text
    assert len(text) < 2000, "pointer stub should be short, not the duplicated content"


# ---- HYG-038: backlog authority repointed ----------------------------------


def test_rc1_announcement_no_work_list_ref():
    text = _read("groundtruth-kb/docs/announcements/v0.7.0-rc1.md")
    assert "memory/work_list.md" not in text
