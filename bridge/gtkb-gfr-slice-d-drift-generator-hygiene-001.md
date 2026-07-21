NEW
::init gtkb lo
::open build

# Implementation Proposal — GFR Slice D: Drift & generator hygiene

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-d-drift-generator-hygiene
Version: 001
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5646

target_paths: ["scripts/check_dev_environment_inventory_drift.py", "scripts/check_harness_parity.py", ".claude/skills/gtkb-skill-rollout/SKILL.md", ".claude/skills/gtkb-harness-parity-review/SKILL.md", "platform_tests/scripts/test_drift_hook_remediation_text.py", "platform_tests/scripts/test_parity_strict_on_rename.py"]

Implementation proposal for governance friction reduction — Slice D (drift & generator hygiene).

## Claim

Slice D of the Governance Friction Reduction program (per GO'd advisory `bridge/gtkb-governance-friction-reduction-002.md`) addresses four findings that prevent future cascade failures. The advisory documented that the skill-rename rollout surfaced 21 stale `surface` paths and 46 stale on-disk dirs that parity only flagged as `EXTRA`/`MISSING` *after* the fact, and that the drift hook blocked a commit without telling the agent how to fix it. The fix is to make the drift hook self-remediating, capture the rename playbook as a durable skill, add generator-map visibility to parity review, and add a strict-on-rename guard — **no existing gate is weakened**.

This slice implements four findings:

1. **Finding 2.5 — Self-remediating drift hook**: `scripts/check_dev_environment_inventory_drift.py` already imports the collector (`collect_dev_environment_inventory.py`), but the FAIL message does not print the remediation command. The fix adds a remediation hint to `render_summary()` when `material_inventory_drift` is true: `"Remediation: run 'python scripts/collect_dev_environment_inventory.py' to regenerate the baseline."` This eliminates the post-block search for the regeneration entry point.

2. **Finding 4.3 — `gtkb-skill-rollout` playbook skill**: The skill-rename rollout was executed from session memory, not a checklist. The advisory documented that stale-`surface`-path (21) and stale-on-disk-dir (46 deletions) bugs were both "the rename didn't cascade." The fix creates a new `gtkb-skill-rollout` skill that captures the rename playbook as a durable, repeatable procedure. Per LO note N3, the playbook explicitly includes "update `skill-rename-map.toml`" as step 2 — this was Slice 0 of the actual rollout and the map was the ground-truth artifact that prevented name-discrepancy propagation.

3. **Finding 4.4 — Parity review generator-map**: `gtkb-harness-parity-review` should list per-harness generator scripts and flag harnesses with declared capabilities but no generator (cursor/goose had none, causing WI-5641/5642). The fix adds a "Generator Inventory" section to the `gtkb-harness-parity-review` skill that enumerates generators and flags missing ones. This is a skill-documentation addition, not a new generator.

4. **Finding 4.5 — Strict-on-rename guard**: The rename surfaced 21 stale `surface` paths and 46 stale on-disk dirs that parity only flagged *after* the fact. The fix adds a `--strict-on-rename` flag to `scripts/check_harness_parity.py` that compares current on-disk skill dirs against `skill-rename-map.toml` and flags any dir whose name differs from its `canonical_name` — catching the cascade at check time, not after.

## Requirement Sufficiency

Existing requirements are sufficient for this slice. The advisory's findings are all documentation, error-message, and convenience-check additions — no new specifications or requirement changes are needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/check_dev_environment_inventory_drift.py` ✅
- `scripts/check_harness_parity.py` ✅
- `.claude/skills/gtkb-skill-rollout/SKILL.md` ✅ (new skill directory)
- `.claude/skills/gtkb-harness-parity-review/SKILL.md` ✅ (existing skill, additive content)
- `platform_tests/scripts/test_drift_hook_remediation_text.py` ✅ (new test file)
- `platform_tests/scripts/test_parity_strict_on_rename.py` ✅ (new test file)

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines who may author which status tokens; this proposal is authored by Prime Builder.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — these changes preserve durable artifacts (skill playbook, parity guard, drift remediation text).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-to-test mapping; TEST-11691 covers new checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes the three mandatory header lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` — the GFR program was added via WIs WI-5643–WI-5646 under formal-artifact-approval DELIB-202667078.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — these changes convert session-discovered procedures into durable skill artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the new skill is a durable artifact triggered by the advisory's threshold crossing.
- `ADR-CROSS-HARNESS-PARITY-001` — relevant to the parity strict-on-rename guard (Finding 4.5).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — relevant to the generator inventory addition (Finding 4.4).

## Prior Deliberations

- `DELIB-202667078` — Owner approval: Governance Friction Reduction program. Owner approved the 4-slice program.
- `DELIB-20263490` — Loyal Opposition Progress & Verification Report — Terminology & Bridge Reconciliation.

### Helper-suggested candidates

_No prior deliberations beyond those listed above._

## Owner Decisions / Input

- `DELIB-202667078` (AUQ GFR-PAUTH-001) — Owner answer: "1 - Yes, proceed".
- `PAUTH-GFR-PROGRAM-20260721` — Active project authorization covering WI-5643–WI-5646.

## Cross-Harness Disposition

This proposal touches `.claude/skills/gtkb-skill-rollout/SKILL.md` (new) and `.claude/skills/gtkb-harness-parity-review/SKILL.md` (additive), which are harness-surface files.

| Harness | Surface | Parity Status | Disposition |
|---|---|---|---|
| Claude Code | `.claude/skills/` (canonical source) | N/A — canonical | New skill `gtkb-skill-rollout` created here; `gtkb-harness-parity-review` edited here. |
| Codex | `.codex/skills/` (generated adapter) | **Requires adapter regeneration** | After implementation, run `python scripts/generate_codex_skill_adapters.py --update-registry` to regenerate the Codex adapter. |
| Antigravity | No skill adapter | N/A | No action required. |
| Cursor | No skill adapter | N/A | No action required. |
| Goose | No skill adapter | N/A | No action required. |
| OpenRouter | No skill adapter | N/A | No action required. |

**No typed waiver required.** The only downstream action is regenerating the Codex skill adapter after implementation.

## Proposed Scope

### Finding 2.5 — Self-remediating drift hook

**File:** `scripts/check_dev_environment_inventory_drift.py`

In `render_summary()`, after the existing blocking/warning output, add a remediation hint when `material_inventory_drift` is true:

```python
if result.get("material_inventory_drift"):
    lines.append("")
    lines.append("Remediation: run 'python scripts/collect_dev_environment_inventory.py' to regenerate the baseline.")
```

This is a 3-line addition to the existing function. The remediation command is already known in-code (the collector is imported at line 152).

### Finding 4.3 — `gtkb-skill-rollout` playbook skill

**File:** `.claude/skills/gtkb-skill-rollout/SKILL.md` (new)

Create a new skill capturing the skill-rename playbook. The SKILL.md frontmatter includes:

```yaml
---
name: gtkb-skill-rollout
description: Playbook for renaming or adding canonical skills, including rename-map update, adapter regeneration, and stale-dir cleanup.
argument-hint: "[rename|add|cleanup]"
---
```

The body documents the ordered playbook (per LO note N3, step 2 is the rename-map update):

1. **Rename the canonical skill directory** under `.claude/skills/`
2. **Update `config/agent-control/skill-rename-map.toml`** — add/update the `[[skills]]` entry with the new `dir` and `canonical_name`; set `registry_old_name` if the old name is still referenced
3. **Fix `canonical_source`/`surface` paths** in the renamed SKILL.md frontmatter
4. **Fix frontmatter** — update `name:` to match the new canonical name
5. **Regenerate adapters** — run `python scripts/generate_codex_skill_adapters.py --update-registry`
6. **Clear stale on-disk dirs** — remove any old adapter directories that match the previous name
7. **Run parity** — run `python scripts/check_harness_parity.py` to verify no EXTRA/MISSING
8. **Run strict-on-rename** — run `python scripts/check_harness_parity.py --strict-on-rename` (new in Finding 4.5)

### Finding 4.4 — Parity review generator-map

**File:** `.claude/skills/gtkb-harness-parity-review/SKILL.md`

Add a "Generator Inventory" section to the existing skill body:

```markdown
## Generator Inventory

| Harness | Generator Script | Adapter Surface |
|---|---|---|
| Claude Code | (canonical source — no generator needed) | `.claude/skills/` |
| Codex | `scripts/generate_codex_skill_adapters.py` | `.codex/skills/` |
| Antigravity | **No generator** — inline loading | N/A |
| Cursor | **No generator** — Claude-compatible loading | N/A |
| Goose | **No generator** — inline loading | N/A |
| OpenRouter | **No generator** — inline loading | N/A |

When a harness declares capabilities in `config/agent-control/harness-capability-registry.toml` but has no generator script, flag it as a **generator gap** — adapter regeneration is not possible for that harness, and skill changes must be manually synced.
```

### Finding 4.5 — `--strict-on-rename` flag

**File:** `scripts/check_harness_parity.py`

Add a `--strict-on-rename` CLI flag and implementation:

```python
parser.add_argument(
    "--strict-on-rename",
    action="store_true",
    help="Compare on-disk skill dirs against skill-rename-map.toml and flag stale names.",
)
```

When `--strict-on-rename` is set:
1. Load `config/agent-control/skill-rename-map.toml`
2. For each `[[skills]]` entry, compare `dir` against the actual on-disk directory name in `.claude/skills/`
3. If the on-disk dir name differs from `dir`, add a `STALE_NAME` result to the report
4. If a `[[skills]]` entry's `canonical_name` differs from the SKILL.md frontmatter `name:`, add a `NAME_MISMATCH` result
5. Return non-zero if any `STALE_NAME` or `NAME_MISMATCH` results are found

Add a new function `_check_rename_map_consistency(project_root: Path) -> list[dict]` that performs the comparison and returns stale-name/mismatch findings.

### Test additions

**File:** `platform_tests/scripts/test_drift_hook_remediation_text.py` (new)

Test that `render_summary()` includes the remediation hint when `material_inventory_drift` is true, and does NOT include it when false.

**File:** `platform_tests/scripts/test_parity_strict_on_rename.py` (new)

Test that `--strict-on-rename` flag:
1. Returns `STALE_NAME` when an on-disk dir name differs from `skill-rename-map.toml` `dir`
2. Returns `NAME_MISMATCH` when `canonical_name` differs from SKILL.md frontmatter `name:`
3. Returns zero (pass) when all names are consistent
4. Returns non-zero (fail) when any stale names or mismatches are found

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "drift remediation text, new skill, parity guard, skill documentation additions",
  "provenance": "GO'd advisory gtkb-governance-friction-reduction-002; owner decision DELIB-202667078",
  "canonical_authority": "check_dev_environment_inventory_drift.py; check_harness_parity.py; .claude/skills/gtkb-skill-rollout/SKILL.md; .claude/skills/gtkb-harness-parity-review/SKILL.md",
  "primary_route": "additive: remediation text, new skill, new parity flag, new test files",
  "before_behavior": "drift hook blocks without remediation hint; rename playbook is session memory only; parity doesn't check rename-map consistency",
  "after_behavior": "drift hook prints remediation command; rename playbook is a durable skill; parity has strict-on-rename guard; generator inventory is documented",
  "self_descriptive_naming": "strict-on-rename, STALE_NAME, NAME_MISMATCH, gtkb-skill-rollout",
  "obsolete_guidance_disposition": "no existing guidance is superseded; all changes are additive",
  "history_preservation": "no existing artifacts are deleted or rewritten",
  "baseline": "existing tests + ruff check + ruff format --check",
  "expected_result": "all tests pass, ruff clean, new checks work",
  "rollback": "revert the commit; no data migration or state change",
  "hard_invariants": "existing parity checks unchanged; drift hook behavior unchanged (only output extended); no gate weakened",
  "fail_closed_conditions": "strict-on-rename is opt-in (flag); drift remediation is advisory text",
  "essential_context_preservation": "all changes are durable artifacts (scripts, skills, tests)"
}
```

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Visual inspection of spec links | yes | (pending) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_drift_hook_remediation_text.py platform_tests/scripts/test_parity_strict_on_rename.py -q --tb=short` | (pending) | (pending) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify proposal author identity | yes | (pending) |
| `GOV-12` | Verify TEST-11691 exists and is linked to WI-5646 | yes | (pending) |
| `GOV-13` | Verify TEST-11691 is assigned to PHASE-001 | yes | (pending) |

## Acceptance Criteria

1. `check_dev_environment_inventory_drift.py` `render_summary()` includes remediation text when `material_inventory_drift` is true.
2. `.claude/skills/gtkb-skill-rollout/SKILL.md` exists with the 8-step rename playbook, including step 2 "update `skill-rename-map.toml`" (LO note N3).
3. `.claude/skills/gtkb-harness-parity-review/SKILL.md` includes the Generator Inventory section with per-harness generator scripts.
4. `check_harness_parity.py` supports `--strict-on-rename` flag that returns `STALE_NAME`/`NAME_MISMATCH` results.
5. New test files pass.
6. All existing tests pass.
7. `ruff check` and `ruff format --check` pass on modified scripts.
8. Codex skill adapter is regenerated after implementation.
9. No existing governance gate is weakened or removed.

## Risks / Rollback

- **Risk: `--strict-on-rename` false positives** — new skill dirs not yet in `skill-rename-map.toml` will be flagged. Mitigation: the check only compares entries that exist in the map; unlisted dirs are not flagged (they're handled by the existing `EXTRA` check in regular parity).
- **Risk: New skill not auto-loaded** — `gtkb-skill-rollout` won't be in any activity envelope's auto-load list. Mitigation: it's a reference skill, not a workflow skill; it's loaded on-demand via `gt skills load`.
- **Risk: Generator inventory table drift** — if new harnesses are added, the table in `gtkb-harness-parity-review/SKILL.md` may become stale. Mitigation: the table is documentation; the parity check is the authoritative source.
- **Rollback:** Revert the commit. No data migration. All changes are additive.

## Files Expected To Change

- `scripts/check_dev_environment_inventory_drift.py` — add remediation text to `render_summary()`
- `scripts/check_harness_parity.py` — add `--strict-on-rename` flag and `_check_rename_map_consistency()` function
- `.claude/skills/gtkb-skill-rollout/SKILL.md` — new skill with rename playbook
- `.claude/skills/gtkb-harness-parity-review/SKILL.md` — add Generator Inventory section
- `platform_tests/scripts/test_drift_hook_remediation_text.py` — new test file
- `platform_tests/scripts/test_parity_strict_on_rename.py` — new test file

## Recommended Commit Type

`feat`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
