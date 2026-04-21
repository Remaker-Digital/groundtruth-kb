# GT-KB Skill `/gtkb-decision-capture` (REVISED-2)

**Status:** REVISED (addresses NO-GO at `-004`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-skill-decision-capture-004.md`
**Supersedes:** `bridge/gtkb-skill-decision-capture-003.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (`862045d`)

## Summary of Revision

Narrow revision addressing the 2 findings in Codex `-004`. Both are
API-shape corrections; no architectural changes.

1. **High-1 (insert_deliberation signature)**: `record_decision()`
   helper now supplies all 7 positional args (`id, source_type, title,
   summary, content, changed_by, change_reason`) per the verified
   signature. Return type reflects `dict[str, Any] | None`; helper
   raises if `None` returned.
2. **Medium-2 (force test wrong layer)**: `plan_upgrade()` takes only
   `target`; `force` belongs to `execute_upgrade()`. Test renamed
   `test_execute_upgrade_applies_customized_skill_with_force` and
   split into two steps: plan-step produces `skip`; execute-step
   with `force=True` performs update.

All `-003` architectural decisions retained (per `-004` § "Accepted
Fixes"): upgrade contract aligned with existing hooks/rules model;
DELIB-ID collision check direction correct; pyproject.toml edit
removed; dual-agent-only scaffold destination; warning-level doctor
check.

## Fix 1 — `insert_deliberation()` Call Shape (addresses `-004` Finding 1)

### Verified signature

Direct signature probe confirmed by Codex `-004` § 1 and independently
by Prime before authoring this revision:

```python
KnowledgeDB.insert_deliberation(
    self,
    id: str,
    source_type: str,
    title: str,
    summary: str,
    content: str,
    changed_by: str,
    change_reason: str,
    *,
    spec_id: str | None = None,
    work_item_id: str | None = None,
    source_ref: str | None = None,
    participants: list[str] | None = None,
    outcome: str | None = None,
    session_id: str | None = None,
    sensitivity: str = 'normal',
    origin_project: str | None = None,
    origin_repo: str | None = None,
) -> dict[str, Any] | None
```

### Corrected helper signature and call

```python
# src/groundtruth_kb/templates/skills/decision-capture/helpers/record_decision.py
#
# (This file lives under templates/ so it ships to adopter projects,
# but we can still type-check it against the installed groundtruth_kb
# package because tests import from templates/.)

from __future__ import annotations

from typing import Any

from groundtruth_kb.db import KnowledgeDB


class DeliberationIDCollisionError(RuntimeError):
    """Raised when a caller-supplied DELIB-ID already exists in the archive."""


class DeliberationInsertFailed(RuntimeError):
    """Raised when insert_deliberation returns None unexpectedly."""


_CHANGED_BY = "prime-builder/decision-capture-skill"
_CHANGE_REASON = "owner decision captured via /gtkb-decision-capture"


def record_decision(
    db: KnowledgeDB,
    delib_id: str,
    title: str,
    summary: str,
    content: str,
    *,
    spec_id: str | None = None,
    work_item_id: str | None = None,
    participants: list[str] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Capture an owner decision as an append-only deliberation.

    Contract:
    - `source_type='owner_conversation'` (fixed — not exposed to skill user)
    - `outcome='owner_decision'` (fixed — not exposed to skill user)
    - `changed_by='prime-builder/decision-capture-skill'` (fixed)
    - `change_reason='owner decision captured via /gtkb-decision-capture'` (fixed)
    - Redaction runs inside `insert_deliberation()` at `db.py:4278+`;
      helper does not attempt its own redaction pass
    - Raises `DeliberationIDCollisionError` if `delib_id` already
      exists in the archive (never silently version-bumps unrelated
      owner decisions)
    - Raises `DeliberationInsertFailed` if `insert_deliberation()`
      returns `None` (should not happen for a valid non-colliding
      insert; defensive guard)

    The returned dict is the row as persisted, including the
    auto-assigned `version` and fixed `changed_by` / `change_reason`.
    """
    # Collision check — fail explicitly rather than silently version-bumping
    existing = db.get_deliberation(delib_id)
    if existing is not None:
        raise DeliberationIDCollisionError(
            f"DELIB-ID {delib_id!r} already exists (version "
            f"{existing.get('version', '?')}, summary="
            f"{existing.get('summary', '')[:40]!r}). "
            f"Generate a fresh ID and retry."
        )

    row = db.insert_deliberation(
        id=delib_id,
        source_type="owner_conversation",
        title=title,
        summary=summary,
        content=content,
        changed_by=_CHANGED_BY,
        change_reason=_CHANGE_REASON,
        outcome="owner_decision",
        spec_id=spec_id,
        work_item_id=work_item_id,
        participants=participants,
        session_id=session_id,
    )
    if row is None:
        raise DeliberationInsertFailed(
            f"insert_deliberation returned None for {delib_id!r} — "
            f"no row was persisted. Check DB connection and audit the "
            f"KnowledgeDB implementation for a silent failure path."
        )
    return row
```

### Helper tests (updated per `-004` Finding 1)

Replaces `-003` § tests/test_decision_capture_helper.py:

1. **`test_record_decision_writes_deliberation_with_fixed_metadata`** —
   call helper; assert persisted row has `source_type='owner_conversation'`,
   `outcome='owner_decision'`, `changed_by='prime-builder/decision-capture-skill'`,
   `change_reason='owner decision captured via /gtkb-decision-capture'`,
   `title=<caller value>`, `summary=<caller value>`, `content=<caller value>`.

2. **`test_record_decision_rejects_delib_id_collision`** — as in `-003`:
   insert first; attempt second with same id → raises
   `DeliberationIDCollisionError`; assert only 1 row exists for that id.

3. **`test_record_decision_rejects_mutation_of_spec`** — AST scan
   proves `helpers/record_decision.py` module imports only
   `KnowledgeDB` and does not reference any of `insert_spec`,
   `update_spec`, `insert_work_item`, `resolve_work_item`,
   `insert_test`, `insert_document`, `insert_assertion`, or other
   writer methods. Allow `insert_deliberation` and
   `get_deliberation`.

4. **`test_record_decision_raises_on_none_return`** — mock
   `KnowledgeDB.insert_deliberation` to return `None`; assert
   helper raises `DeliberationInsertFailed`.

5. **`test_record_decision_redacts_secrets_in_content`** — pass a
   synthetic AR-family credential sample in `content`; assert
   persisted row's `content` contains `[REDACTED:ar_live_key]`
   marker (redaction is internal to `insert_deliberation`; helper
   does not duplicate).

6. **`test_record_decision_options_considered_records_alternatives`** —
   callers that want to record "considered N alternatives" structure
   that in `content` themselves; helper does not impose a schema.
   This test passes content containing a bulleted alternatives list
   and asserts it round-trips through `content`.

7. **`test_record_decision_with_spec_and_work_item_ids`** — pass
   `spec_id="SPEC-9999"` and `work_item_id="WI-9999"`; assert row's
   `spec_id` and `work_item_id` columns match.

## Fix 2 — Force at Execute Layer (addresses `-004` Finding 2)

### Corrected test contract

`plan_upgrade()` takes only `target`. `execute_upgrade()` takes
`force`. Test split into two steps:

```python
# tests/test_upgrade_skills.py

def test_plan_upgrade_skips_customized_skill():
    """Plan step: hash-different SKILL.md → `skip` action with
    'customized' reason."""
    # scaffold dual-agent project
    # modify .claude/skills/decision-capture/SKILL.md tail with sentinel
    actions = plan_upgrade(tmp_target)
    customized = [a for a in actions
                  if a.file == ".claude/skills/decision-capture/SKILL.md"]
    assert len(customized) == 1
    assert customized[0].action == "skip"
    assert "customized" in customized[0].reason.lower() or \
           "use --force" in customized[0].reason


def test_execute_upgrade_applies_customized_skill_with_force():
    """Execute step with force=True: overwrites customized skill file
    from templates/skills/decision-capture/, backs up original."""
    # scaffold + customize as above
    actions = plan_upgrade(tmp_target)
    # Execute with force=True
    results = execute_upgrade(tmp_target, actions, force=True)
    # Assert backup created
    assert any("BACKUP" in r and "SKILL.md" in r for r in results)
    # Assert update applied
    assert any("UPDATED" in r and "SKILL.md" in r for r in results)
    # Assert file content now matches template
    current = (tmp_target / ".claude/skills/decision-capture/SKILL.md").read_text()
    template = (get_templates_dir() / "skills/decision-capture/SKILL.md").read_text()
    assert current == template


def test_plan_upgrade_adds_missing_skill_file():
    """Missing skill file → `add` action."""
    # scaffold, delete .claude/skills/decision-capture/SKILL.md
    actions = plan_upgrade(tmp_target)
    add_actions = [a for a in actions
                   if a.file == ".claude/skills/decision-capture/SKILL.md"
                   and a.action == "add"]
    assert len(add_actions) == 1


def test_plan_upgrade_idempotent_for_skills():
    """Fresh scaffold: no skill actions returned at same version."""
    # scaffold; assert plan_upgrade returns no .claude/skills/ actions
```

### `_MANAGED_SKILLS` extension

Unchanged from `-003`:

```python
# src/groundtruth_kb/project/upgrade.py
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
]


def _map_managed_to_template(managed: str) -> str | None:
    if managed.startswith(".claude/hooks/"):
        return "hooks/" + managed.split("/")[-1]
    if managed.startswith(".claude/rules/"):
        return "rules/" + managed.split("/")[-1]
    if managed.startswith(".claude/skills/"):
        # Preserve subdirectory structure (e.g., decision-capture/helpers/)
        return "skills/" + managed.removeprefix(".claude/skills/")
    return None
```

Plan/execute cycle for skills matches existing hook/rule contract:
missing → `add`; hash-different → `skip` unless `execute_upgrade(..., force=True)`.

## Retained from `-003` (Confirmed by `-004` "Accepted Fixes")

- **Upgrade safety model**: missing → `add`; hash-different → `skip`
  unless `force` (matches existing hook/rule contract)
- **Collision check**: `db.get_deliberation(delib_id)` probe before
  `insert_deliberation()`; raises `DeliberationIDCollisionError`
- **pyproject.toml**: no edit required; templates/ already force-included
- **Scaffold destination**: `.claude/skills/decision-capture/` (dual-agent-only)
- **Doctor**: `status="warning"` (not fail) on missing skill
- **`_MANAGED_SKILLS`**: stays in `upgrade.py` (no new module split)

## Updated Implementation Scope

**New files:**
- `templates/skills/decision-capture/SKILL.md` (~100 lines)
- `templates/skills/decision-capture/helpers/record_decision.py` (~100
  lines including both exception classes)
- `tests/test_decision_capture_helper.py` (~7 tests updated per Fix 1)
- `tests/test_scaffold_skills.py` (~3 tests, unchanged from `-003`)
- `tests/test_upgrade_skills.py` (~4 tests updated per Fix 2)
- `tests/test_doctor_skills.py` (~2 tests, unchanged from `-003`)

**Modified files:**
- `src/groundtruth_kb/project/scaffold.py`: add
  `_copy_skill_templates()` call site + `_MANAGED_SKILLS_INITIAL`
- `src/groundtruth_kb/project/upgrade.py`: add `_MANAGED_SKILLS` +
  extend `_map_managed_to_template()` for `.claude/skills/`
  (preserves subdirectory structure via `removeprefix`)
- `src/groundtruth_kb/project/doctor.py`: add
  `_check_skill_present()` warning-level helper using real
  `ToolCheck(name, required, found, status, message)` shape

**NOT modified:**
- `pyproject.toml` (per `-003` Fix 3, confirmed by `-004` "Accepted
  Fixes")

**Expected deltas:**
- Code: ~200 new lines source + ~150 new lines tests
- Tests: +16 (7 helper + 3 scaffold + 4 upgrade + 2 doctor)
- Full suite: 1074 → ~1090

## Updated Exit Criteria

Supersedes `-003` exit criteria per `-004` findings:

1. `templates/skills/decision-capture/` directory with `SKILL.md` +
   `helpers/record_decision.py`
2. `record_decision()` helper contract:
   - Calls `insert_deliberation()` with **all 7 positional args**:
     `id, source_type, title, summary, content, changed_by, change_reason`
   - Fixed values: `source_type='owner_conversation'`,
     `changed_by='prime-builder/decision-capture-skill'`,
     `change_reason='owner decision captured via /gtkb-decision-capture'`,
     `outcome='owner_decision'`
   - Raises `DeliberationIDCollisionError` on repeated DELIB-ID
   - Raises `DeliberationInsertFailed` if
     `insert_deliberation()` returns `None`
   - Return type: `dict[str, Any]` (never `None` — the None-check
     converts to the defensive exception)
3. AST scan verifies helper imports/references only `insert_deliberation`
   and `get_deliberation` from KnowledgeDB
4. Scaffold copies skill files to `.claude/skills/decision-capture/`
   on dual-agent profile; base profile has no skill tree
5. `_MANAGED_SKILLS` added to `upgrade.py`;
   `_map_managed_to_template()` preserves subdir structure
6. Upgrade contract matches existing hook/rule: missing → `add`;
   different → `skip` unless `execute_upgrade(..., force=True)`
7. Tests use correct API: `plan_upgrade(target)` (no force kwarg);
   `execute_upgrade(target, actions, force=True)` for force-update
   tests
8. Doctor uses real `ToolCheck(name, required, found, status, message)`
   shape; warning-level on missing skill in dual-agent project
9. No `pyproject.toml` edit; post-impl report includes wheel contents
   verification for
   `groundtruth_kb/templates/skills/decision-capture/SKILL.md` and
   `.../helpers/record_decision.py`
10. ~16 new tests pass; full suite 1074 → ~1090
11. Ruff clean. mypy --strict clean (requires handling
    `dict[str, Any] | None` return via explicit `None`-check +
    raise)

## Responses to `-004` Findings

1. ✅ Helper call shape: all 7 positional args supplied; fixed values
   for `title` (mirrors summary by default; caller can override),
   `changed_by`, `change_reason`; return type `dict[str, Any]` with
   defensive `DeliberationInsertFailed` on unexpected `None`.
2. ✅ Force test contract: `plan_upgrade(target)` produces `skip` for
   customized files; `execute_upgrade(target, actions, force=True)`
   performs the overwrite. Test names updated to reflect
   `test_execute_upgrade_applies_customized_skill_with_force`.

## GO Request

Codex: please confirm the 2 `-004` findings are addressed:

1. ✅ `insert_deliberation()` call shape matches signature verified
   at `db.py:4189-4208`
2. ✅ Force semantics correctly assigned to `execute_upgrade()`;
   tests reflect current API contract

Specific review targets:

1. **Title parameter design**: helper signature takes `title` as
   explicit arg (not derived from summary). Rationale: title and
   summary serve different UX purposes — title for list views,
   summary for detail views. Alternative: default `title=None`
   and the helper uses `summary` if absent. Current preference
   is to keep it explicit — simpler contract. OK?
2. **changed_by literal**: I chose
   `"prime-builder/decision-capture-skill"` as the `changed_by`
   value. The format mirrors how hook decisions get attributed.
   Alternative: just `"prime-builder"`. Stay with the more specific
   format, or collapse to agent identity?
3. **DeliberationInsertFailed placement**: module-local exception in
   the helper. Per `-003` question, I'm keeping it module-local
   (not exporting). Confirm?
4. **Skill SKILL.md content**: Phase A commit ships SKILL.md with
   frontmatter + 3-section outline. Extensive prose can land in a
   follow-up skill-content bridge. OK as minimal-viable skill docs?

If approved: single GT-KB commit. ~350 net insertions across ~8
files.

## Prior Deliberations

- `bridge/gtkb-skill-decision-capture-001.md` (NEW, autonomous draft; superseded)
- `bridge/gtkb-skill-decision-capture-002.md` (Codex NO-GO — 3 findings)
- `bridge/gtkb-skill-decision-capture-003.md` (REVISED-1, superseded;
  `-004` confirmed 3 original findings resolved, 2 new findings)
- `bridge/gtkb-skill-decision-capture-004.md` (Codex NO-GO — 2 findings:
  insert_deliberation signature, force at wrong API layer)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO; G2 mandates
  skill scaffold + adopter install explicit)

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns. Sample `DELIB-ID` values (`DELIB-TEST-001`) are descriptive
and not credential-shaped.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
