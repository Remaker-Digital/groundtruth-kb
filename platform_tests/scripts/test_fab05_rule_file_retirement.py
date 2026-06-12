"""FAB-05 rule-file retirement — grep-absence / presence regression test.

Encodes the HYG-018/026/027/038 acceptance criteria from
bridge/gtkb-fab-05-rule-file-retirement-003.md (GO at -004) as deterministic
assertions over the live tree. All paths are repo-root-relative.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES = REPO_ROOT / ".claude" / "rules"


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


# ---- HYG-018: OS-poller stack archived; runbook is a DEPRECATED stub --------


def test_poller_stack_archived_no_tracked_source_files():
    # The 22 tracked poller scripts moved to the archive; the source tree retains
    # no tracked poller scripts (gitignored runtime logs are out of FAB-05 scope).
    src = REPO_ROOT / "independent-progress-assessments" / "bridge-automation"
    archive = REPO_ROOT / "archive" / "os-poller-2026-04-25"
    assert archive.is_dir(), "archive/os-poller-2026-04-25/ must exist"
    assert (archive / "claude-file-bridge-scan.ps1").is_file()
    assert (archive / "repair-permanent-bridge-automation.ps1").is_file()
    # No tracked .ps1/.vbs remain at the source top level (logs/ is gitignored).
    if src.is_dir():
        stragglers = [p.name for p in src.glob("*.ps1")] + [p.name for p in src.glob("*.vbs")]
        assert not stragglers, f"poller scripts still at source: {stragglers}"


def test_runbook_is_deprecated_stub_no_poller_mandate():
    runbook = _read(".claude/rules/bridge-permanent-operations-runbook.md")
    assert "DEPRECATED" in runbook
    assert "bridge-essential.md" in runbook
    assert "WI-4404" in runbook
    # No live 3-minute poller cadence mandate / repair-command procedure remains.
    assert "3-minute cycle" not in runbook
    assert "-VerifyOnly" not in runbook
    assert "repair-permanent-bridge-automation.ps1" not in runbook


def test_file_bridge_protocol_no_poller_cadence():
    text = _read(".claude/rules/file-bridge-protocol.md")
    assert "every 3 minutes" not in text
    assert "scheduled every 3 minutes" not in text
    assert "automated every 3 minutes" not in text


# ---- HYG-026: Cursor-era rule files archived; index path corrected ----------


def test_cursor_era_rule_files_archived():
    for name in (
        "session-start-prompt.md",
        "prompt-organize-reports-in-dropbox.md",
        "exec-summary-report-guide.md",
        "project-progress-dashboard-runbook.md",
    ):
        assert not (RULES / name).exists(), f"{name} must be archived out of .claude/rules/"
        assert (REPO_ROOT / "independent-progress-assessments" / "archive" / "cursor-legacy" / name).is_file(), (
            f"{name} must be in cursor-legacy archive"
        )


def test_index_cursor_legacy_path_corrected():
    text = _read(".claude/rules/codex-knowledge-base-index.md")
    assert "independent-progress-assessments/archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md" in text
    # No bare (wrong) archive/cursor-legacy/ path line remains.
    assert "`archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md`" not in text


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


def test_severity_model_block_deduped_and_renamed():
    text = _read(".claude/rules/codex-review-operating-contract.md")
    # The mislabeled/duplicated "## Severity Model" heading is gone; the single
    # surviving block is renamed "## Review Coordination".
    assert text.count("## Severity Model") == 0
    assert text.count("## Review Coordination") == 1
    assert text.count("## Implementation Boundary") == 1


def test_auq_block_pointer_not_duplicate():
    text = _read(".claude/rules/acting-prime-builder.md")
    # The verbatim duplicate body is gone; a pointer to the canonical home remains.
    assert "prime-builder-role.md" in text
    assert "PROSE_DECISION_PATTERNS" not in text


def test_report_depth_context_is_pointer_stub():
    # Pointer-not-delete: the file still exists (required by the governance-adoption
    # test + skill frontmatter) but now points to canonical report-depth.md.
    p = RULES / "report-depth-prime-builder-context.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "report-depth.md" in text
    assert len(text) < 2000, "pointer stub should be short, not the duplicated content"


def test_prime_builder_scope_note_present():
    text = _read(".claude/rules/prime-builder.md")
    assert "prime-builder-role.md" in text


# ---- HYG-038: backlog authority repointed ----------------------------------


def test_standing_priorities_repointed_to_membase_backlog():
    text = _read(".claude/rules/codex-standing-priorities.md")
    # work_list.md is no longer the idle-work AUTHORITY (a historical mention of
    # its retirement is allowed); the MemBase backlog is now cited.
    assert "recorded in `memory/work_list.md`" not in text
    assert "GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT" not in text
    assert "gt backlog list" in text
    assert "GOV-STANDING-BACKLOG-001" in text


def test_rc1_announcement_no_work_list_ref():
    text = _read("groundtruth-kb/docs/announcements/v0.7.0-rc1.md")
    assert "memory/work_list.md" not in text
