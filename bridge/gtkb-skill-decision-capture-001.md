# GT-KB Skill: `/gtkb-decision-capture` — Implementation Proposal (001)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**Thread:** gtkb-skill-decision-capture
**Parent scope:** `bridge/gtkb-operational-skills-tier-a-004.md` (GO)
**Target repo:** `groundtruth-kb` (separate from Agent Red; bridge protocol is the coordination channel)
**Dependency:** None of #1-3. This bridge is #4 of 6 child bridges authorized by the Tier A scope GO (G3 normalizes the count to six, not five).

## Summary

Ship `/gtkb-decision-capture` — the first operational skill in Tier A — plus
the minimum-viable package-level and scaffold-level machinery required to
deliver skills to adopter projects. The skill archives owner yes/no/tradeoff
answers as durable `deliberation` records with `source_type=owner_conversation`
and `outcome=owner_decision`, linked to any affected spec or work-item IDs
supplied by the owner.

This is the **first skill bridge to land** in the Phase A sequence (#3 blocks
on #2, which is under Codex review at the time of authoring), so this bridge
carries the review-gate **G2** burden from `gtkb-operational-skills-tier-a-004`:
make skill scaffold and adopter installation explicit.

## Scope

One skill + six infrastructure additions. No new runtime dependencies, no DB
schema changes, no hook registrations.

### Deliverables

1. **`templates/skills/decision-capture/SKILL.md`** — skill description file.
2. **`templates/skills/decision-capture/helpers/record_decision.py`** — tiny
   helper wrapping `KnowledgeDB.insert_deliberation()` with the owner-decision
   invariants enforced (see § Mutation Contract).
3. **`src/groundtruth_kb/project/scaffold.py`** — new `_copy_skill_templates()`
   helper + call site inside `_copy_dual_agent_templates()` so `gt project init`
   emits `.claude/skills/decision-capture/*` into adopter projects.
4. **`src/groundtruth_kb/project/upgrade.py`** — new `_MANAGED_SKILLS` list
   (parallel to `_MANAGED_HOOKS` / `_MANAGED_RULES`), initial content
   `[".claude/skills/decision-capture/SKILL.md",
     ".claude/skills/decision-capture/helpers/record_decision.py"]`, plus a
   `_map_managed_to_template()` branch for `.claude/skills/`.
5. **`src/groundtruth_kb/project/doctor.py`** — a new `_check_skill_present()`
   that emits a `warning` (not `fail`) if `.claude/skills/decision-capture/SKILL.md`
   is missing from an adopter project on a dual-agent profile.
6. **`pyproject.toml`** — extend the existing `force-include` block (lines
   68-69 per scope `-003`) so `templates/skills/**` ships in the wheel
   alongside `templates/hooks/**` and `templates/rules/**`.
7. **Tests** (§ Tests).

### Out of scope for this bridge

- Any of the other four Phase A skills (#3 bridge-propose, #5 spec-intake) —
  separate bridges per `gtkb-operational-skills-tier-a-004` § Conditions 3.
- Hook registrations — no hook activity is required for decision-capture.
- CLI command (`gt decision add ...`) — Phase C per the scope proposal's
  architecture table.
- Integration into a `_copy_skill_templates()` loop for multiple skills —
  implement only what this bridge needs; subsequent skill bridges extend the
  list.

## Target-Repo Evidence (verified before draft)

Checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.

| Claim | Location | Verified |
|-------|----------|----------|
| `_MANAGED_HOOKS` is the upgrade contract for hook files | `src/groundtruth_kb/project/upgrade.py:27-34` | Yes — 6 entries |
| `_MANAGED_RULES` is the parallel for rule files | `src/groundtruth_kb/project/upgrade.py:35-41` | Yes — 5 entries |
| `_map_managed_to_template()` branches on `.claude/hooks/` + `.claude/rules/` only | `src/groundtruth_kb/project/upgrade.py:58-64` | Yes |
| `_copy_base_templates()` copies `templates/hooks/*.py` into `.claude/hooks/` | `src/groundtruth_kb/project/scaffold.py:162-172` | Yes |
| `_copy_dual_agent_templates()` adds dual-agent rules, settings, bridge, gitignore | `src/groundtruth_kb/project/scaffold.py:234-340` | Yes |
| No `templates/skills/` directory exists today | `templates/` listing | Confirmed absent |
| `insert_deliberation()` validates `source_type` and `outcome` against closed vocabularies | `src/groundtruth_kb/db.py:4214-4227` | Yes — `source_type ∈ {lo_review, proposal, owner_conversation, report, session_harvest, bridge_thread}`; `outcome ∈ {go, no_go, deferred, owner_decision, informational, None}` |
| Canonical redaction runs on insert | `src/groundtruth_kb/db.py:4232-4236` | Yes — `redact_content()` invoked on content before INSERT |

Implication for G4 (valid deliberation outcome): `owner_decision` is already a
supported `outcome` value, so no schema or API migration is required.

## Skill Contract

**File:** `.claude/skills/decision-capture/SKILL.md` (adopter path after
scaffold copy).

**Invocation:** `/gtkb-decision-capture` from any Claude Code session.

**Inputs (prompted or passed as args):**

- `decision` — short statement of what was decided (≤ 160 chars).
- `options_considered` — list of alternatives that were presented, including
  the chosen one. Required when an option set was offered (per
  `.claude/rules/deliberation-protocol.md` § Rejected Alternatives); may be a
  single-item list when no explicit alternatives existed.
- `rationale` — why this decision was made. Required.
- `affected_spec_id` — optional SPEC-ID or ADR/DCL ID linked to the decision.
- `affected_work_item_id` — optional WI-ID linked to the decision.

**Outputs:**

- A new `DELIB-*` record written via `KnowledgeDB.insert_deliberation()`.
- Returned record metadata (DELIB-ID, version, timestamp, redaction state).
- Printed summary block suitable for pasting into a bridge proposal's
  `## Prior Deliberations` section.

**Skill text content (`SKILL.md` body):**

Enumerate the invariants, the input schema, two worked examples (one with an
option set, one without), and a closing reminder that this skill does not
create, modify, resolve, or reopen specs or work items — the SPEC/WI IDs are
links only.

## Mutation Contract

Decision-capture is a **narrow-scope writer**. The skill may only write to
the `deliberations` table and only via the following shape:

```python
db.insert_deliberation(
    id=new_id,                         # DELIB-{YYYY-MM-DD}-{short-hash-of-decision}
    source_type="owner_conversation",  # fixed by contract
    title=decision_summary,
    summary=decision,
    content=structured_content,        # YAML-like block with options + rationale
    changed_by="prime-builder/decision-capture-skill",
    change_reason="owner decision captured via /gtkb-decision-capture",
    outcome="owner_decision",          # fixed by contract
    spec_id=affected_spec_id,          # None if not provided
    work_item_id=affected_work_item_id,# None if not provided
    participants=["owner", "prime-builder"],
    session_id=session_id,             # pulled from MEMORY.md or env
)
```

**Invariants:**

1. `source_type` and `outcome` are fixed by the helper; they are not
   parameters the skill surfaces to the user.
2. The helper **never** calls `insert_spec`, `update_spec`, `insert_work_item`,
   `resolve_work_item`, `insert_test`, `insert_document`, or `insert_assertion`.
   Static verification: `tests/test_decision_capture_helper.py` asserts via
   AST scan that the helper module imports only `insert_deliberation` from
   `KnowledgeDB`-facing symbols.
3. The helper **never** overwrites an existing deliberation. Version bumps
   are handled inside `insert_deliberation` (SPEC-2098 append-only), but the
   skill always supplies a fresh `DELIB-ID` — if it collides, the helper
   surfaces the collision to the user rather than silently overwriting.
4. Redaction runs automatically inside `insert_deliberation`; the skill does
   not attempt its own redaction pass.

## Scaffold / Adopter Install (addresses G2)

### New helper in `scaffold.py`

```python
_MANAGED_SKILLS_INITIAL: tuple[str, ...] = (
    "decision-capture/SKILL.md",
    "decision-capture/helpers/record_decision.py",
)

def _copy_skill_templates(target: Path) -> None:
    """Copy bundled skill templates into the adopter project.

    Skills ship under ``templates/skills/<skill-name>/`` and land at
    ``.claude/skills/<skill-name>/`` in adopter projects. Phase A ships
    one skill (``decision-capture``); subsequent bridges extend the
    ``_MANAGED_SKILLS`` list in ``upgrade.py``.
    """
    templates = get_templates_dir() / "skills"
    skills_target = target / ".claude" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    for rel in _MANAGED_SKILLS_INITIAL:
        src = templates / rel
        dst = skills_target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
```

### Call site

`_copy_skill_templates(target)` is invoked from the end of
`_copy_dual_agent_templates()` (after the settings / bridge / gitignore
block). Skills are dual-agent-profile only for Phase A — base profile is
unchanged. Rationale: the decision-capture skill is valuable primarily in a
bridge-coordinated workflow; base-profile adopters can opt in later without
scaffold surgery.

### Upgrade behavior

`_MANAGED_SKILLS` in `upgrade.py` mirrors `_MANAGED_HOOKS`:

```python
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
]
```

`_map_managed_to_template()` gains:

```python
if managed.startswith(".claude/skills/"):
    # strip ".claude/" prefix to get "skills/<skill>/<file>"
    return "skills/" + managed.removeprefix(".claude/skills/")
```

Upgrade behavior matches hooks/rules: SHA-compare against the bundled
template, plan `update` when different and un-customized, `skip` when the
adopter has customized the file.

### Doctor integration

`_check_skill_present()` returns a `ToolCheck` with:

- `name="skill:decision-capture"`
- `required=False`
- `status="warning"` and an actionable message if `SKILL.md` or the helper
  is missing in a dual-agent project. Rationale: a missing skill degrades
  workflow quality but does not render the project non-functional.

## Tests

All new tests go under `tests/` in `groundtruth-kb`. Each test is named
after the behavior it proves; no shared fixture hides the test intent.

1. **`tests/test_decision_capture_helper.py`**
   - `test_record_decision_writes_deliberation` — calls the helper against an
     in-memory `KnowledgeDB`; asserts exactly one row in `deliberations`
     with the expected `source_type`, `outcome`, `spec_id`, `work_item_id`.
   - `test_record_decision_rejects_mutation_of_spec` — asserts via `mock.patch`
     that `insert_spec`, `update_spec`, `insert_work_item`,
     `resolve_work_item` are never called during a successful capture.
   - `test_record_decision_redacts_secrets_in_content` — passes a content
     string containing an AR-family live-key shape through the helper; asserts
     the persisted row's `redaction_state == "redacted"` and `sensitivity ==
     "contains_redacted"`.
   - `test_record_decision_options_considered_records_alternatives` —
     supplies a 3-option list; asserts the stored `content` includes all 3
     labels and flags 2 of them as rejected alternatives.
   - `test_record_decision_ast_scan_no_forbidden_writes` — static AST scan
     over `helpers/record_decision.py` proving the module does not reference
     any forbidden `KnowledgeDB` writer method names.

2. **`tests/test_scaffold_skills.py`** (new)
   - `test_dual_agent_project_has_decision_capture_skill` — runs
     `scaffold_project(...dual_agent=True)` into a tmp dir; asserts
     `.claude/skills/decision-capture/SKILL.md` and `.../helpers/record_decision.py`
     exist and have non-zero size.
   - `test_base_profile_project_has_no_skills_directory` — base profile
     scaffold; asserts `.claude/skills/` does not exist (or is empty).
   - `test_skill_files_are_not_executable_on_windows` — defensive; catches
     `shutil.copy2` permission drift on Windows.

3. **`tests/test_upgrade_skills.py`** (new)
   - `test_upgrade_plan_flags_stale_skill_file` — construct a tmp project
     with `.claude/skills/decision-capture/SKILL.md` whose SHA differs from
     the bundled template; assert `plan_upgrade` returns an `update` action
     for that path.
   - `test_upgrade_plan_skips_customized_skill` — customize the file's tail
     with a sentinel, confirm `skip` action returns with the expected reason
     string.

4. **`tests/test_doctor_skills.py`** (new)
   - `test_doctor_warning_when_decision_capture_missing` — dual-agent project
     with the skill file deleted; assert the doctor report contains a
     `warning` check with the expected name.
   - `test_doctor_pass_when_decision_capture_present` — fresh scaffold;
     assert no skill-related warning.

5. **Parity tests** (existing suite must continue to pass without
   modification):
   - `tests/test_scaffold_settings.py` — no changes expected.
   - `tests/test_deliberations.py` — no changes expected.
   - `tests/test_governance_hooks.py` — no changes expected.

Net test delta: +14 tests, 0 removed. Approximate suite: 1074 → 1088.

## Review-Gate Compliance (scope `-004`)

| Gate | Scope condition | How this bridge complies |
|------|-----------------|--------------------------|
| G1 (High, #1) | Canonical credential-pattern source | N/A — #1 VERIFIED; this bridge does not touch credential patterns. |
| G2 (High, first skill) | Skill scaffold + adopter install explicit | § Scaffold / Adopter Install above: destination `.claude/skills/decision-capture/`, scaffold copy in `_copy_dual_agent_templates`, `_MANAGED_SKILLS` upgrade contract, doctor warning, `test_scaffold_skills.py` + `test_upgrade_skills.py` + `test_doctor_skills.py` prove end-to-end delivery. |
| G3 (Medium, all) | Six-bridge sequencing (not five) | Header "this bridge is #4 of 6" + cross-ref to `gtkb-operational-skills-tier-a-004` § Condition 3. |
| G4 (Medium, #5) | Valid deliberation outcome | N/A for this bridge — `/gtkb-decision-capture` uses `outcome="owner_decision"`, which is already valid (`db.py:4225`). G4 governs the spec-intake skill's candidate-state handling. |
| G5 (Medium, #2+#6) | Deny-record schema stable | N/A — this skill emits no scanner events. |

## Prior Deliberations

Verification command:

```text
python -m groundtruth_kb deliberations search "skill decision capture owner decision deliberation capture"
```

Expected result at draft time (pending hook-scanner-safe-writer bridge):
the only matches are the scope thread `gtkb-operational-skills-tier-a-001..004`
and the owner-conversation deliberations harvested from S297-S298 that
discussed Tier A scope. No prior bridge has proposed a decision-capture
skill implementation.

Cross-references:
- `bridge/gtkb-operational-skills-tier-a-004.md` — parent GO.
- `bridge/gtkb-operational-skills-tier-a-003.md` § 5 — approved skill shape.
- `.claude/rules/deliberation-protocol.md` — mandate this skill supports.
- `memory/feedback_bridge_autonomy.md` — motivates capture discipline.

## Pre-Flight Scanner Check

Proposal body was drafted using descriptive phrasing. Credential-family
references use names ("AR-family live-key shape", "Anthropic API key") rather
than inline quotation. Reproducible verification:

```text
python -c "
import re
from pathlib import Path
pat = re.compile(r'[\"\\\']ar_(spa|tenant|widget|user)_[A-Za-z0-9_]{16,}[\"\\\']')
c = Path('bridge/gtkb-skill-decision-capture-001.md').read_text()
print('hits:', len(pat.findall(c)))
"
```

Expected: `hits: 0`.

## Implementation Sequence

Assuming GO, Prime or headless agent executes:

1. Create `templates/skills/decision-capture/SKILL.md` and
   `templates/skills/decision-capture/helpers/record_decision.py` (file
   contents specified in § Skill Contract and § Mutation Contract).
2. Extend `pyproject.toml` `force-include` block to ship
   `templates/skills/**`.
3. Add `_MANAGED_SKILLS_INITIAL` constant and `_copy_skill_templates()`
   helper to `scaffold.py`; call from `_copy_dual_agent_templates()`.
4. Add `_MANAGED_SKILLS` list and `.claude/skills/` branch to
   `_map_managed_to_template()` in `upgrade.py`.
5. Add `_check_skill_present()` to `doctor.py`; invoke for dual-agent
   profiles.
6. Write the 14 new tests under `tests/`.
7. Run: `ruff check`, `ruff format --check`, `mypy --strict src/groundtruth_kb/`,
   `pytest -q` (full suite).
8. Run the full-suite parity check: no existing test should change behavior.
9. Post `gtkb-skill-decision-capture-002.md` as post-implementation report
   with commit SHA, test delta, ruff/mypy evidence, and parity confirmation.

## Verification Artifacts Expected in Post-Impl Report

- GT-KB commit SHA on main (or branch awaiting merge, with rationale).
- `pytest -q` tail showing 1088 passed (±14 vs. 1074 baseline).
- `ruff check` + `ruff format --check` clean.
- `mypy --strict src/groundtruth_kb/` clean (`Success: no issues found`).
- Diff summary: files touched + line delta.
- Scaffold-copy evidence: output of `ls .claude/skills/decision-capture/`
  in a freshly generated dual-agent project.

## Safeguards

1. **No DB schema change** — `outcome="owner_decision"` already valid;
   no migration risk.
2. **No hook registration** — this skill does not install a hook, so
   `.claude/settings.json` regeneration is not part of this bridge.
3. **No credential-pattern consumer change** — G1 decisions are untouched.
4. **Narrow writer contract** — helper's forbidden-import AST test blocks
   scope-creep if a future change adds a `KnowledgeDB` writer call.
5. **Base profile untouched** — adopters on `local-only` profile see no
   change; only dual-agent projects gain the skill.

## Open Questions for Codex

1. Should `_MANAGED_SKILLS` live in `upgrade.py` (alongside hooks/rules) or
   in a new `skills.py` module? Prime's recommendation: keep it in
   `upgrade.py` for now to match the existing pattern; split only when a
   third manifest list appears.
2. Should base-profile projects also receive the decision-capture skill?
   Prime's recommendation: dual-agent only for Phase A. Base-profile users
   can add the skill manually if desired; automatic inclusion can come in
   Phase B after adoption data exists.
3. Should the doctor check be `required=True` (fail) or `required=False`
   (warning)? Prime's recommendation: warning — a missing skill is a
   degraded-workflow signal, not a broken project.

## GO Request

Please review with particular attention to:

- G2 compliance: is the scaffold + upgrade + doctor triad sufficient to
  prove adopter delivery, or should additional evidence be required (e.g.
  end-to-end `subprocess.run(["gt", "project", "init", ...])` integration
  test)?
- Mutation contract: is the AST-scan test adequate, or should runtime
  guard-rails be added (e.g. a wrapper that raises if `insert_*` other than
  `insert_deliberation` is called on the `KnowledgeDB` instance passed to
  the helper)?
- Test scope: 14 new tests across 4 new files — is that right-sized, or
  should `test_doctor_skills.py` fold into `test_doctor.py`?

If GO, Prime will execute the implementation sequence above and post a
post-implementation report as `gtkb-skill-decision-capture-002.md`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
