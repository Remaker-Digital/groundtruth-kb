NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5957-config-hooks-platform-classification
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5957
related_work_items: ["WI-5969", "WI-5933", "WI-5967"]

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

**No KB mutation.** This proposal performs no MemBase write and does not modify
`groundtruth.db`.
**No approval-evidence work.** This proposal creates no formal-artifact-approval packet
and writes no approval-packet path.
**No dispatcher or TAFE mutation.** No dispatcher configuration, substrate, scheduled task,
routing rule, or harness registry entry is changed.
**No harness-surface target.** `target_paths` contains no `.claude/hooks/**`,
`.codex/**`, or skills path, so no Cross-Harness Disposition is required. The change is to
the classifier that gates writes to such paths, not to the paths themselves.

# WI-5957 - Classify `config/hooks/**` as a platform governance surface

## Problem Statement

`workstream_focus.classify_root` returns `application_product` for every path under
`config/hooks/`. While the session work subject is `gtkb_infrastructure` - the default and
correct subject for GT-KB platform work - `guard_tool_use` therefore refuses the write with
`BLOCKED (GTKB-WORK-SUBJECT)`.

`config/hooks/` contains platform hook implementations, all `gtkb-`-prefixed: measured
2026-08-06 it holds `gtkb-advisory-router-scan.py`, `gtkb-assertion-check.py`,
`gtkb-bridge-axis-2-surface.py`, `gtkb-bridge-compliance-gate.py`,
`gtkb-bridge-proposal-wi-id-collision-gate.py`,
`gtkb-code-quality-baseline-proposal-check.py`, `gtkb-credential-scan.py`,
`gtkb-delib-search-gate.py`, `gtkb-delib-search-tracker.py`, `gtkb-destructive-gate.py`,
and more. None is application product.

## Root Cause

The defect is a single omission with a self-documenting cause.

`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` (`scripts/workstream_focus.py` lines 252-276)
is matched **before** the blanket `config/` entry in `APPLICATION_PREFIXES` (line 241), and
WI-5100 used that ordering to carve six platform config subdirectories out of the blanket
rule: `config/agent-control/`, `config/dispatcher/`, `config/governance/`,
`config/harness-parity/`, `config/project-templates/`, `config/registry/`.

`config/hooks/` was not included. The comment introducing that carve-out states the
consequence outright:

> "Any `config/<other>` path still falls through to application_product."

So this is not a subtle classifier bug. It is a known-by-design fallthrough whose reach into
a directory of platform hooks went unnoticed.

Measured live 2026-08-06:

```
application_product                config/hooks/gtkb-bridge-axis-2-surface.py
application_product                config/hooks/gtkb-bridge-compliance-gate.py
current_repo_bridge_or_governance  config/governance/timer-inventory.toml
current_repo_bridge_or_governance  .claude/hooks/bridge-compliance-gate.py
```

## Live Impact (two blocked changes, both recorded)

1. **WI-5933 Slice B is stuck half-applied.** Change C4 requires the identical guard in both
   AXIS-2 hook copies. `.claude/hooks/bridge-axis-2-surface.py` was updated;
   `config/hooks/gtkb-bridge-axis-2-surface.py` was refused by this gate. The tracked
   baseline therefore still coerces an unresolved session role to `ROLE_PRIME` - precisely
   the defect C4 removes - and the change cannot be committed in that state.
2. **WI-5967 will hit the same wall.** Its Cross-Harness Disposition already excludes
   `config/hooks/gtkb-bridge-compliance-gate.py` from `target_paths` as a disclosed,
   tracked parity gap for exactly this reason
   (`bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-001.md`).

The available workaround - switching the work subject to `application` - is not acceptable:
it would misrepresent GT-KB platform work as application work and defeat the guard's
purpose. Both changes accepted a disclosed gap rather than subvert the control, which is why
the defect is still open and worth fixing at the source.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `GOV-ARTIFACT-APPROVAL-001` - in the authorizing PAUTH's linked-spec set; no formal
  artifact is created or mutated by this change.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each acceptance
  criterion to a test.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the parity obligation this defect currently
  makes unsatisfiable for `config/hooks/**`; restoring correct classification restores the
  ability to comply.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the platform/application boundary this
  classifier implements. The change makes the classifier agree with the boundary rather than
  altering it.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - discharged by the disposition below.
- `.claude/rules/project-root-boundary.md` - in-root containment.

## Prior Deliberations

- `WI-5100` - the change that established the `config/` carve-out pattern and its
  before-blanket ordering. This proposal extends that same pattern to one more directory; it
  does not introduce a new mechanism or reverse a prior decision.
- `WI-5957` - the originating defect, filed 2026-08-06 when WI-5933 C4 was blocked mid-change.
- `WI-5969` - the addendum recording that the misclassification is directory-wide across
  `config/hooks/**` rather than limited to the single axis-2 file.
- `bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-001.md` - records the
  second blocked change and the decision to accept a disclosed gap rather than force the write.
- Deliberation search executed 2026-08-06 found no decision establishing `config/hooks/` as
  application product, and no decision opposing platform classification for GT-KB hook
  implementations.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already defines
the platform/application boundary and WI-5100 already established how `config/` subdirs are
carved out of the blanket application rule. This change corrects an omission in that
implementation. No requirement is created or revised.

## Proposed Change

### C1 - Add `config/hooks/` to the governance prefix carve-out

Add `"config/hooks/"` to `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` in
`scripts/workstream_focus.py`, in the WI-5100 block, keeping the list's alphabetical
ordering (between `config/harness-parity/` and `config/project-templates/`). The comment is
extended to name hook implementations alongside the existing examples.

This is deliberately the smallest correct change. Rejected alternatives:

- **Classify all of `config/` as governance.** Over-broad: it would silently reclassify any
  future genuinely application-owned `config/` subdirectory, reversing WI-5100's explicit
  design rather than completing it.
- **Special-case the individual blocked files.** Leaves every other `config/hooks/` file
  misclassified and guarantees the same defect recurs on the next one touched - the exact
  single-file framing WI-5969 corrected.

### C2 - Pin the classification

Extend `platform_tests/hooks/test_workstream_focus.py` with cases asserting the boundary in
both directions, so neither the carve-out nor the blanket rule can silently regress.

## Test Plan (specification-derived)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | C1 | `classify_root("config/hooks/gtkb-bridge-axis-2-surface.py")` returns `current_repo_bridge_or_governance` |
| T2 | C1 (directory-wide, per WI-5969) | the same holds for a second, unrelated `config/hooks/` file, so the fix is not file-specific |
| T3 | live impact | `guard_tool_use` permits a `config/hooks/**` write while the work subject is `gtkb_infrastructure` |
| T4 | WI-5100 non-regression | the six pre-existing carve-outs still classify as governance |
| T5 | boundary preserved (no over-broad fix) | an unrelated `config/<other>/` path still classifies `application_product`, proving the blanket rule survives |
| T6 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | a genuine `applications/` path still classifies `application_product` |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

The full existing `test_workstream_focus.py` suite is re-run, not just the new cases, because
`classify_root` is consumed by the work-subject guard on every tool call.

## Acceptance Criteria

1. All `config/hooks/**` paths classify as `current_repo_bridge_or_governance` (T1, T2).
2. A `config/hooks/**` write is permitted under the `gtkb_infrastructure` work subject (T3).
3. The WI-5100 carve-outs are unchanged (T4).
4. The blanket `config/` application rule still applies to other subdirectories (T5) and
   genuine application paths are unaffected (T6).
5. `test_workstream_focus.py` shows no regression; both ruff gates pass.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "applicability_rationale": "scripts/workstream_focus.py implements the work-subject write guard consulted on every tool call, so any change to it is cross-cutting.",
  "provenance": "WI-5957 filed 2026-08-06 when WI-5933 change C4 was blocked mid-change; widened to directory scope by WI-5969 after config/hooks/gtkb-bridge-compliance-gate.py was found equally blocked while filing WI-5967.",
  "canonical_authority": "ADR-ISOLATION-APPLICATION-PLACEMENT-001 defines the platform/application boundary; WI-5100 established the config/ carve-out mechanism and its before-blanket match ordering. This change adds one entry to that existing carve-out and defines no new authority.",
  "primary_route": "classify_root in scripts/workstream_focus.py, consumed by guard_tool_use as a PreToolUse write gate. The route is unchanged; only the prefix table gains one entry.",
  "before_behavior": "Every path under config/hooks/ classifies application_product, so guard_tool_use refuses the write under the gtkb_infrastructure subject. Platform hook copies kept there cannot be edited by platform sessions, making cross-harness parity unsatisfiable for that directory and leaving WI-5933 C4 half-applied.",
  "after_behavior": "config/hooks/ classifies current_repo_bridge_or_governance like the other platform config subdirs, so platform sessions can edit the hook copies and complete parity. No other classification changes.",
  "self_descriptive_naming": "The new entry is the literal prefix config/hooks/, added inline to the existing WI-5100 block whose comment already explains the carve-out and its ordering; the extended comment names hook implementations explicitly.",
  "obsolete_guidance_disposition": "No guidance becomes obsolete. The WI-5100 comment stating that any config/<other> path falls through to application_product remains accurate for the directories still outside the carve-out.",
  "history_preservation": "No file is moved, renamed, or deleted; no bridge file or MemBase row is edited. The change is one added tuple entry plus additive test cases.",
  "baseline": "Measured 2026-08-06: classify_root returns application_product for config/hooks/gtkb-bridge-axis-2-surface.py and config/hooks/gtkb-bridge-compliance-gate.py, and current_repo_bridge_or_governance for config/governance/timer-inventory.toml and .claude/hooks/bridge-compliance-gate.py. test_workstream_focus.py passes before the change.",
  "expected_result": "T1-T2 show config/hooks/** classified as governance; T3 shows the write permitted; T4-T6 show the WI-5100 carve-outs, the blanket config/ rule, and genuine application paths all unchanged; the existing suite continues to pass and both ruff gates pass.",
  "rollback": "Remove the single tuple entry from CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES. The added test cases are additive and can be deleted independently. No data migration and nothing persisted to undo.",
  "hard_invariants": "The platform/application boundary of ADR-ISOLATION-APPLICATION-PLACEMENT-001; the WI-5100 ordering in which governance prefixes are matched before the blanket config/ application prefix; and the blanket rule's continued application to config/ subdirectories outside the carve-out. T4, T5, and T6 pin all three.",
  "fail_closed_conditions": "The guard continues to refuse cross-subject writes: an application-subject session is still refused gtkb_product targets, and a gtkb_infrastructure session is still refused application_product targets. This change moves one directory to its correct side of that boundary; it removes no refusal and adds no bypass. Work-subject state remains owner-controlled.",
  "essential_context_preservation": "The WI-5100 rationale comment is retained and extended rather than replaced, so the reason the carve-out exists and why ordering matters stays adjacent to the code. WI-5957 and WI-5969 retain the measured evidence and the two blocked-change instances independently of this thread."
}
```

## Risk and Rollback

- **Risk: over-broad reclassification.** The material risk for a write-gate change. Mitigated
  by scoping to exactly one prefix and by T5, which asserts an unrelated `config/` subdir
  still classifies `application_product`.
- **Risk: masking a genuine application surface.** `config/hooks/` contains only
  `gtkb-`-prefixed platform hook implementations, enumerated above from `git ls-files`. No
  application-owned file lives there.
- **Risk: regression in the write guard.** `classify_root` runs on every tool call, so the
  full existing suite is re-run rather than only the new cases.
- **Rollback:** remove the single tuple entry; delete the additive test cases.

## Owner Decisions / Input

No owner decision is required for this change, and none is claimed.

`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` v2 is active with
`included_work_item_ids: null` (no work-item restriction) and permits the `source` and
`test` mutation classes this proposal targets, so WI-5957 is already within its scope. No
PAUTH amendment is made or requested.

The originating context is the owner directive to prioritize the Dispatcher Next program:
this defect blocks cross-harness parity for `config/hooks/**`, which WI-5967's repair of the
Dispatcher Next foundation thread will require.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both declared targets are in-root platform paths
and this bridge file resides under `E:/GT-KB/bridge/`. No `applications/` path is touched.

## Recommended Commit Type

`fix:` - the change repairs a classifier that misroutes platform paths to the application
category, blocking authorized platform writes. It is not `feat:` (no new capability; the
carve-out mechanism already exists) and not `chore:` (behaviour changes: writes previously
refused are now permitted).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
