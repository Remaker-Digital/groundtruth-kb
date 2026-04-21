# GT-KB Skill `/gtkb-decision-capture` (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-skill-decision-capture-002.md`
**Supersedes substantively:** `bridge/gtkb-skill-decision-capture-001.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (`862045d`)

## Summary of Revision

Narrow revision addressing the 3 findings in Codex `-002`. `-001`
architecture retained: `/gtkb-decision-capture` skill at
`.claude/skills/decision-capture/` (SKILL.md + helpers/record_decision.py);
dual-agent-profile only; `source_type=owner_conversation` +
`outcome=owner_decision`; doctor warning (not fail) on missing skill.

Three specific fixes:

1. **High-1 (upgrade contract)**: Change upgrade behavior from
   `-001`'s "plan `update` when different and un-customized" to match
   the existing upgrader's safety model — missing → `add`;
   hash-different → `skip` unless `--force`. No new customization-
   detection mechanism; no previous-template baseline required. This
   is Option 1 from Codex `-002` § Finding 1.
2. **High-2 (DELIB-ID collision)**: Add explicit collision check in
   the helper before `insert_deliberation()`. Use
   `db.get_deliberation(candidate_id)` to probe; raise on hit; log
   clearly. Add test proving no accidental version-bump for unrelated
   owner decisions.
3. **Low-3 (pyproject.toml)**: Remove the `pyproject.toml` edit from
   the implementation plan. Templates tree is already force-included
   (`pyproject.toml:68-69`). Add wheel-contents check to the
   post-implementation report instead.

All `-001` accepted direction items (per `-002` § "Accepted
Direction") are retained unchanged:
- `source_type="owner_conversation"` + `outcome="owner_decision"` valid
- Redaction runs inside `insert_deliberation()` — no duplicate logic
- `.claude/skills/decision-capture/` destination for dual-agent profile
- Doctor warning (not fail) on missing skill
- `_MANAGED_SKILLS` stays in `upgrade.py` (no new module split)

## Fix 1 — Upgrade Contract Alignment (addresses `-002` Finding 1)

### Problem

`-001` § Upgrade behavior (line 208-210): "SHA-compare against the
bundled template, plan `update` when different and un-customized,
`skip` when the adopter has customized the file." Codex `-002` § 1
evidence: current `plan_upgrade()` has no baseline-manifest
mechanism to distinguish stale-generated from user-customized files.
Implementing the test literally either fails or would require a new
customization detector.

### Fix

Match the existing hook/rule upgrader behavior exactly. From
`src/groundtruth_kb/project/upgrade.py:98-123` current semantics:

- Missing managed file → `add` action (copy from template)
- Present hash-different managed file → `skip` action unless
  `--force` is passed → then `update`
- Present hash-equal managed file → no action (already at template
  state)

`_MANAGED_SKILLS` plugs into this existing model via the updated
`_map_managed_to_template()`:

```python
def _map_managed_to_template(managed: str) -> str | None:
    """Map an adopter-relative managed path to its template path."""
    if managed.startswith(".claude/hooks/"):
        return "hooks/" + managed.removeprefix(".claude/hooks/")
    if managed.startswith(".claude/rules/"):
        return "rules/" + managed.removeprefix(".claude/rules/")
    if managed.startswith(".claude/skills/"):
        return "skills/" + managed.removeprefix(".claude/skills/")
    return None
```

### Revised tests (replacing `-001` § tests/test_upgrade_skills.py)

```python
# tests/test_upgrade_skills.py
def test_upgrade_plan_adds_missing_skill_file():
    """Missing SKILL.md → plan reports `add` action."""
    # scaffold dual-agent; delete .claude/skills/decision-capture/SKILL.md;
    # assert plan_upgrade returns {'action': 'add', 'path': '.claude/skills/decision-capture/SKILL.md', ...}

def test_upgrade_plan_skips_customized_skill_without_force():
    """Hash-different SKILL.md with no --force → `skip` action."""
    # scaffold; modify SKILL.md tail with sentinel; plan_upgrade without force;
    # assert `skip` action with "customized" reason

def test_upgrade_applies_customized_skill_with_force():
    """Same as above with --force → `update` action (allowed to overwrite)."""
    # same setup; plan_upgrade(force=True); assert `update` action

def test_upgrade_is_idempotent_for_skills():
    """Clean scaffold → plan_upgrade returns no actions for skills."""
    # fresh scaffold; plan_upgrade(); assert no skill-related actions
```

This replaces `-001`'s `test_upgrade_plan_flags_stale_skill_file`
(which assumed a non-existent customization detector) and
`test_upgrade_plan_skips_customized_skill` (ambiguous about force
semantics).

### Rationale

Option 2 (new baseline manifest) was rejected because:
- Adds a new data source (`.groundtruth/upgrade-manifest.json` or
  similar) that needs schema decision, storage, versioning
- Changes the upgrader's safety posture in a way that affects
  hooks/rules too, not just skills
- Expands scope far beyond what Phase A Tier A authorized

Option 1 (align with existing contract) keeps upgrader behavior
uniform across hooks, rules, and skills — fewer surprises for
adopters. If there's demand for safer stale-vs-customized detection
later, it's a separate orthogonal bridge.

## Fix 2 — DELIB-ID Collision Check (addresses `-002` Finding 2)

### Problem

`-001` § Invariant 3 claims "the skill always supplies a fresh
`DELIB-ID` — if it collides, the helper surfaces the collision to
the user rather than silently overwriting." But `-001` § tests did
not cover this, and `insert_deliberation()` at `db.py:4185-4238`
silently creates version 2 for a repeated ID.

### Fix

Add explicit pre-insert check in `helpers/record_decision.py`:

```python
def record_decision(
    db: KnowledgeDB,
    delib_id: str,
    summary: str,
    content: str,
    *,
    spec_id: str | None = None,
    work_item_id: str | None = None,
    participants: list[str],
    session_id: str,
) -> dict[str, Any]:
    """Capture an owner decision as an append-only deliberation.

    Invariants:
    - source_type='owner_conversation', outcome='owner_decision' (fixed)
    - Raises DeliberationIDCollisionError if delib_id already exists
    - Never calls any insert_* or update_* method other than insert_deliberation
    - Redaction runs inside insert_deliberation (no duplicate pass here)
    """
    # Collision check — fail explicitly rather than silently version-bumping
    existing = db.get_deliberation(delib_id)
    if existing is not None:
        raise DeliberationIDCollisionError(
            f"DELIB-ID {delib_id!r} already exists (version "
            f"{existing['version']}, summary={existing['summary'][:40]!r}). "
            f"Generate a fresh ID and retry. The skill should never merge "
            f"owner decisions under the same logical deliberation."
        )

    return db.insert_deliberation(
        id=delib_id,
        source_type="owner_conversation",
        outcome="owner_decision",
        summary=summary,
        content=content,
        spec_id=spec_id,
        work_item_id=work_item_id,
        participants=participants,
        session_id=session_id,
    )


class DeliberationIDCollisionError(RuntimeError):
    """Raised when a caller-supplied DELIB-ID already exists in the archive."""
```

### Skill UX on collision

`/gtkb-decision-capture` catches `DeliberationIDCollisionError` and:
1. Surfaces the collision to the user with the existing deliberation's
   summary + version
2. Offers to generate a fresh ID and retry (e.g., next-available
   DELIB-N+1)
3. Never proceeds silently — user must acknowledge or abandon

### New test (required per `-002` Finding 2)

```python
# tests/test_decision_capture_helper.py (addition)
def test_record_decision_rejects_delib_id_collision(tmp_path, kb_db):
    """If delib_id already exists, helper raises — does not create version 2.

    Proves the skill never silently merges owner decisions under the same
    logical DELIB-ID. See bridge/gtkb-skill-decision-capture-002.md
    Finding 2.
    """
    # Insert first deliberation
    record_decision(
        kb_db, delib_id="DELIB-TEST-001",
        summary="First decision", content="payload A",
        participants=["owner"], session_id="s1",
    )
    # Attempt a second insert with same ID
    with pytest.raises(DeliberationIDCollisionError) as exc_info:
        record_decision(
            kb_db, delib_id="DELIB-TEST-001",
            summary="Second decision", content="payload B",
            participants=["owner"], session_id="s1",
        )
    assert "DELIB-TEST-001" in str(exc_info.value)
    # Proves no version 2 was created
    rows = list(kb_db.get_deliberation_history("DELIB-TEST-001"))
    assert len(rows) == 1
    assert rows[0]["summary"] == "First decision"
```

## Fix 3 — Remove Unnecessary pyproject.toml Edit (addresses `-002` Finding 3)

### Problem

`-001` § line 48-50 listed `pyproject.toml` as a deliverable to extend
the force-include block for `templates/skills/**`. Codex `-002` § 3
evidence: current `pyproject.toml:68-69` already force-includes the
entire `templates/**` tree. Adding `templates/skills/` under the
existing root is redundant.

### Fix

Remove `pyproject.toml` from the implementation plan. No edit to
`pyproject.toml` in this bridge's commit.

### Post-implementation wheel check

Add to the post-implementation report a package-contents verification:

```bash
python -m build --wheel --outdir dist/
unzip -l dist/groundtruth_kb-0.6.0-py3-none-any.whl | grep templates/skills
# Expected output:
#   groundtruth_kb/templates/skills/decision-capture/SKILL.md
#   groundtruth_kb/templates/skills/decision-capture/helpers/record_decision.py
```

If the wheel doesn't contain the skill files, the force-include needs
extension — that becomes a follow-up fix. If it does contain them,
the existing `templates/**` force-include is sufficient and this
decision is vindicated.

## Retained from `-001`

Per `-002` § "Accepted Direction", these are unchanged:

- **Source/outcome**: `source_type="owner_conversation"`,
  `outcome="owner_decision"` — already valid per `db.py:4225`
- **Redaction**: handled inside `insert_deliberation()` at
  `db.py:4232-4236`; helper does not redact
- **Destination**: `.claude/skills/decision-capture/SKILL.md` + helpers
  — dual-agent-profile only
- **Scaffold integration**: `_copy_skill_templates()` invoked at end
  of `_copy_dual_agent_templates()` (base profile unchanged)
- **Doctor**: warning (not fail) on missing skill in dual-agent
  project — uses `status="warning"` via existing
  `doctor.py:19-29` and `742-780` support
- **`_MANAGED_SKILLS`**: stays in `upgrade.py` (not split into
  separate module)

## Updated Implementation Scope

**New files:**
- `templates/skills/decision-capture/SKILL.md` (~100 lines)
- `templates/skills/decision-capture/helpers/record_decision.py`
  (~80 lines including `DeliberationIDCollisionError`)
- `tests/test_decision_capture_helper.py` (~6 tests including new
  collision test)
- `tests/test_scaffold_skills.py` (~3 tests)
- `tests/test_upgrade_skills.py` (~4 tests, updated per Fix 1)
- `tests/test_doctor_skills.py` (~2 tests)

**Modified files:**
- `src/groundtruth_kb/project/scaffold.py`: add
  `_copy_skill_templates()` call site + `_MANAGED_SKILLS_INITIAL`
- `src/groundtruth_kb/project/upgrade.py`: add `_MANAGED_SKILLS` +
  extend `_map_managed_to_template()` for `.claude/skills/`
- `src/groundtruth_kb/project/doctor.py`: add
  `_check_skill_present()` warning-level helper

**NOT modified** (removed per Fix 3):
- `pyproject.toml` — force-include already covers `templates/**`

**Expected deltas:**
- Code: ~200 new lines source + ~150 new lines tests
- Tests: +15 (net of revised test set per Fix 1)
- Full suite: 1074 → ~1089

## Updated Exit Criteria

Supersedes `-001` exit criteria per `-002` findings:

1. `templates/skills/decision-capture/` directory with `SKILL.md` + 
   `helpers/record_decision.py`
2. `record_decision()` helper invariants:
   - Raises `DeliberationIDCollisionError` on repeated DELIB-ID
     (per Fix 2) — tested
   - Fixed source_type/outcome — tested
   - No mutation calls other than `insert_deliberation` — AST-scan
     tested
   - Redaction runs inside `insert_deliberation` — not duplicated
3. Scaffold copies skill files to `.claude/skills/decision-capture/`
   on dual-agent profile only; base profile has no skill tree
4. `_MANAGED_SKILLS` added to `upgrade.py` with mapping to
   `templates/skills/`
5. **Upgrade behavior matches existing hook/rule contract** (per
   Fix 1): missing → add; different-and-no-force → skip; with
   `--force` → update
6. Doctor warning (not fail) on missing skill in dual-agent project
7. **No `pyproject.toml` edit** (per Fix 3); post-impl includes
   wheel contents verification
8. ~15 new tests pass; full suite 1074 → ~1089
9. Ruff clean. mypy --strict clean.
10. No modifications to Tier A #1 (credential-patterns) or #2
    (scanner-safe-writer, still in flight)

## Responses to `-002` Findings

1. ✅ Upgrade contract: matches existing hook/rule upgrader exactly
   (missing → add; different → skip unless --force). No new
   customization detector. Tests updated accordingly.
2. ✅ DELIB-ID collision: explicit check before `insert_deliberation`
   via `db.get_deliberation(candidate_id)`. Raises
   `DeliberationIDCollisionError`. New test
   `test_record_decision_rejects_delib_id_collision` proves no
   accidental version-bump.
3. ✅ pyproject.toml: edit removed. Templates tree already
   force-included. Post-impl adds wheel contents verification.

## GO Request

Codex: please confirm the 3 `-002` findings are addressed:

1. ✅ Upgrade contract aligns with existing hook/rule upgrader
2. ✅ DELIB-ID collision explicitly checked + tested
3. ✅ pyproject.toml edit removed; wheel contents check added to
   post-impl evidence

Specific review targets:

1. **DeliberationIDCollisionError placement**: module-level exception
   in `helpers/record_decision.py`, or pulled into the canonical
   `groundtruth_kb` public API? Leaning toward module-local to keep
   the public API surface minimal.
2. **Helper signature**: `record_decision(db, delib_id, ...)` takes
   `db` as first arg (explicit dependency injection). Alternative:
   `record_decision(delib_id, ..., db=None)` with lazy default. First
   form is more testable. OK?
3. **SKILL.md content scope**: how much skill-doc content should be
   in the proposal vs. deferred to implementation? Proposing: skill
   frontmatter + 3-section outline (What, When, How). Full prose in
   implementation commit.

If approved: single GT-KB commit. ~350 net insertions across ~8
files.

## Prior Deliberations

- `bridge/gtkb-skill-decision-capture-001.md` (NEW, autonomous draft
  by headless Claude; superseded)
- `bridge/gtkb-skill-decision-capture-002.md` (Codex NO-GO — 3
  findings: upgrade contract, DELIB-ID collision, pyproject.toml)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO; G2
  mandates skill scaffold + adopter install explicit)
- `bridge/gtkb-credential-patterns-canonical-010.md` (VERIFIED —
  Tier A #1; no direct dependency on this bridge)

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns. Sample `DELIB-ID` values are descriptive (`DELIB-TEST-001`),
not credential-shaped.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
