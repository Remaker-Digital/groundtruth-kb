"""Tests for the gtkb-propose scaffolding helper (PROJECT-GTKB-GOV-PROPOSAL-STANDARDS Slice 4).

GO: bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md.

The deterministic helper carries the testable logic (the SKILL.md is
orchestration narrative). These tests verify the emitted scaffold is
structurally gate-compliant: status-token first line, all required sections,
inline-JSON target_paths, a VERIFICATION_HEADING_TOKENS-matching heading,
Prior-Deliberations seeding (+ empty-justification), the self-review checklist,
and the draft-only write boundary.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "scripts" / "gtkb_propose_scaffold.py"


def _load():
    spec = importlib.util.spec_from_file_location("gtkb_propose_scaffold", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_h = _load()


def _scaffold(**overrides):
    kwargs = dict(
        slug="my-demo-thread",
        work_item="WI-1234",
        project="PROJECT-DEMO",
        pauth="PAUTH-DEMO",
        target_paths=["scripts/foo.py", "platform_tests/scripts/test_foo.py"],
    )
    kwargs.update(overrides)
    return _h.build_scaffold(**kwargs)


# --- slug validation ---------------------------------------------------------


def test_slug_validation():
    assert _h.validate_slug("good-slug-123") is None
    for bad in ("Bad-Slug", "has_underscore", "trailing-", "-leading", "double--hyphen", ""):
        assert _h.validate_slug(bad) is not None, bad


def test_slug_collision_against_index(tmp_path):
    index = tmp_path / "INDEX.md"
    index.write_text(
        "# Bridge Index\n\nDocument: existing-thread\nNEW: bridge/existing-thread-001.md\n",
        encoding="utf-8",
    )
    assert _h.slug_collision("existing-thread", index) is not None
    assert _h.slug_collision("brand-new-thread", index) is None
    # Missing INDEX degrades to no collision.
    assert _h.slug_collision("anything", tmp_path / "absent.md") is None


# --- scaffold structure ------------------------------------------------------


def test_scaffold_first_line_is_status_token():
    body = _scaffold()
    first = next(line.strip() for line in body.splitlines() if line.strip())
    assert first == "NEW"


def test_scaffold_has_all_required_sections():
    body = _scaffold()
    for section in _h.REQUIRED_SECTIONS:
        assert section in body, f"missing required section: {section}"
    # Project-linkage metadata lines present and filled from inputs.
    assert "Project Authorization: PAUTH-DEMO" in body
    assert "Project: PROJECT-DEMO" in body
    assert "Work Item: WI-1234" in body
    # 6-field author metadata block.
    for field in (
        "author_identity:",
        "author_harness_id:",
        "author_session_context_id:",
        "author_model:",
        "author_model_version:",
        "author_model_configuration:",
    ):
        assert field in body, field


def test_scaffold_target_paths_inline_json():
    body = _scaffold(target_paths=["scripts/a.py", "b/c.py"])
    m = re.search(r"^target_paths:\s*(\[.+\])\s*$", body, re.MULTILINE)
    assert m, "target_paths inline-JSON line not found"
    parsed = json.loads(m.group(1))
    assert parsed == ["scripts/a.py", "b/c.py"]


def test_scaffold_verification_heading_token():
    body = _scaffold()
    assert _h.VERIFICATION_HEADING in body
    # Heading must contain a VERIFICATION_HEADING_TOKENS substring.
    assert "verification plan" in _h.VERIFICATION_HEADING.lower()
    assert "spec-derived verification" in _h.VERIFICATION_HEADING.lower()


# --- prior deliberations seeding --------------------------------------------


def test_prior_deliberations_seeding():
    body = _scaffold(prior_deliberations=[("DELIB-9001", "A relevant decision"), ("DELIB-9002", "Another")])
    assert "`DELIB-9001`" in body
    assert "A relevant decision" in body
    assert "`DELIB-9002`" in body
    assert "_No prior deliberations" not in body


def test_prior_deliberations_empty_justification():
    body = _scaffold(prior_deliberations=[])
    assert "_No prior deliberations" in body


# --- self-review checklist ---------------------------------------------------


def test_self_review_checklist_commands():
    text = _h.self_review_checklist("my-demo-thread")
    assert "bridge_applicability_preflight.py --bridge-id my-demo-thread" in text
    assert "adr_dcl_clause_preflight.py --bridge-id my-demo-thread" in text
    assert "phantom-spec sweep" in text.lower() or "phantom" in text.lower()
    assert "inline json" in text.lower() or "inline-json" in text.lower()
    assert "gtkb-bridge-propose" in text


# --- write boundary ----------------------------------------------------------


def test_helper_writes_only_draft_path(tmp_path):
    body = _scaffold()
    path = _h.write_draft("my-demo-thread", body, project_root=tmp_path)
    assert path == tmp_path / ".gtkb-state" / "propose-drafts" / "my-demo-thread-001.md"
    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("NEW")
    # Never writes under bridge/.
    assert not (tmp_path / "bridge").exists()


def test_always_applicable_specs_seeded_by_default():
    body = _scaffold()
    for sid in _h.ALWAYS_APPLICABLE_SPECS:
        assert f"`{sid}`" in body, sid
