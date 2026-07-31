REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-31T19-46-49Z
author_model: goose-deepseek-v4-pro
author_model_version: goose-desktop-interactive
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-advisory-pb-session-focus-lo-contamination
Version: 002
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-advisory-pb-session-focus-lo-contamination-001.md

Project Authorization: none (this is an advisory-correction proposal; the advisory thread does not carry its own PAUTH)
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: pending MemBase creation (blocked by WI-5841 Goose claim resolution)

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/scripts/test_bridge_state_report_role_filter.py", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md"]
implementation_scope: source,test,configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation.
No approval-evidence work: creates no formal-artifact approval packet.

# Implementation Proposal — Role-Scoped Bridge State-Report Output

## Summary

Add a `--role` parameter to `gt bridge state-report` that filters output by
caller role, and strengthen the Prime Builder and Loyal Opposition startup
overlays with explicit session-focus menu generation rules so that LO-scope
bridge entries can never appear in a PB session-focus menu.

Root cause per Advisory `-001`: the bridge state-report emits the
`lo_actionable` list to all callers regardless of role. No programmatic guard
prevents a PB agent from transcribing it into a session-focus menu.

## Problem — one defect, two failure surfaces

### Surface 1 — CLI output is role-agnostic

`gt bridge state-report --json` returns a `bridge.lo_actionable` list
containing every NEW/REVISED/NO-ACTION bridge entry. A PB caller receives the
exact same payload as an LO caller. The key name encodes role assignment but
provides no structural barrier to a PB agent mechanically transcribing the
list into session-focus options.

**Observed:** Goose G transcribed all 26 entries into a PB session-focus menu
option on 2026-07-31.

### Surface 2 — overlay rule is prose, self-enforced by agent attention

`PRIME-BUILDER-STARTUP-OVERLAY.md` § Bridge handling correctly states:

> "Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness.
> Never process latest `NEW`, `REVISED`, or `VERIFIED` as actionable queue work
> (that is a role-confusion defect to diagnose)."

This is correct but is consumed by an LLM agent that must self-enforce it.
With the full `lo_actionable` list in context, a model's transcription
instinct can override the filter rule. The overlay text needs a stronger,
explicit session-focus-menu generation instruction that the model can apply
as a checklist item, not a general rule.

## Proposed Implementation

### F1 — Role-scoped bridge state-report (`state_report.py`)

Add a `--role` (or `--caller-role`) parameter to the `state-report` CLI:

```text
gt bridge state-report --role pb    # suppresses lo_actionable; foregrounds GO/NO-GO
gt bridge state-report --role lo    # foregrounds lo_actionable; moves GO/NO-GO to pb_only
gt bridge state-report              # current behavior preserved (backward compatible)
```

JSON output with `--role pb`:

```json
{
  "bridge": {
    "status_mix": {"GO": 121, "NO-GO": 167, ...},
    "pb_actionable": [
      // GO + NO-GO entries — PB scope
    ],
    "lo_only": {
      "count": 26,
      "note": "NEW/REVISED/NO-ACTION entries are LO scope. Omitted from pb_actionable."
      // slugs listed but not in actionable array
    },
    "total_thread_count": 2404
  }
}
```

JSON output with `--role lo`:

```json
{
  "bridge": {
    "status_mix": {"GO": 121, "NO-GO": 167, ...},
    "lo_actionable": [
      // NEW + REVISED + NO-ACTION entries — LO scope
    ],
    "pb_only": {
      "count": 288,
      "note": "GO/NO-GO entries are PB scope. Not actionable for LO."
    },
    "total_thread_count": 2404
  }
}
```

The key invariant: with `--role pb`, no array in the output can contain
entries whose latest status is NEW, REVISED, NO-ACTION, VERIFIED, or
ADVISORY. An agent mechanically iterating any array cannot produce an
LO-scope session-focus option.

**Non-breaking:** the default (no `--role`) preserves the current output
format exactly for backward compatibility with existing scripts.

### F2 — Overlay text strengthening (startup overlays)

Add to `PRIME-BUILDER-STARTUP-OVERLAY.md` § Disclosure:

```markdown
**Session-Focus Menu Generation Rule (HARD):** When constructing the numbered
session-focus menu from bridge state-report output, entries whose latest status
is NEW, REVISED, NO-ACTION, or VERIFIED MUST be excluded from every menu option.
Do not include them under any qualification, hedge, or owner-instruction framing.
The only bridge-status entries a PB session-focus menu may contain are GO and
NO-GO. If using `gt bridge state-report --role pb`, the `pb_actionable` array
already enforces this exclusion; if using the un-scoped output, apply the filter
programmatically before constructing the menu. Presenting a LO-scope entry as a
PB menu option is a role-confusion defect and must fail closed.
```

Add to `LOYAL-OPPOSITION-STARTUP-OVERLAY.md` the reciprocal:

```markdown
**Session-Focus Menu Generation Rule:** When constructing session-focus options
from bridge state-report output, entries whose latest status is GO, NO-GO, or
VERIFIED are PB-scope implement/revision items. Do not present them as LO
session-focus options. The only bridge-status entries an LO session-focus may
contain are NEW, REVISED, NO-ACTION, and ADVISORY.
```

### F3 — Test surface

New file: `platform_tests/scripts/test_bridge_state_report_role_filter.py`

| Test | What it asserts |
|------|----------------|
| `test_role_pb_excludes_lo_statuses` | `--role pb` output has zero NEW/REVISED/NO-ACTION in `pb_actionable` |
| `test_role_pb_includes_go_nogo` | `--role pb` output includes GO and NO-GO entries in `pb_actionable` |
| `test_role_lo_excludes_pb_statuses` | `--role lo` output has zero GO/NO-GO/VERIFIED in `lo_actionable` |
| `test_role_lo_includes_new_revised_noaction` | `--role lo` output includes NEW/REVISED/NO-ACTION in `lo_actionable` |
| `test_no_role_preserves_existing_output` | Default (no `--role`) produces the same keys and structure as current |
| `test_role_pb_lo_only_has_count_not_details` | `--role pb` `lo_only` section is informational, not actionable |
| `test_invalid_role_fails_clean` | Invalid `--role` value exits non-zero with clear error |
| `test_markdown_role_pb_excludes_lo` | `--markdown --role pb` table excludes LO entries |
| `test_json_role_pb_no_lo_actionable_key` | `--json --role pb` has no `lo_actionable` key |

## Requirement Sufficiency

Existing requirements sufficient:
- `GOV-FILE-BRIDGE-AUTHORITY-001` § First-Line Role Eligibility Check already
  prohibits PB from processing LO-status entries.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`
  establish that roles are hard boundaries, not preferences.

## Specification-Derived Verification

| Requirement | Command | Expected |
|---|---|---|
| PB output excludes LO entries | `pytest test_bridge_state_report_role_filter.py -q -k "pb"` | all PB-filter tests pass |
| LO output excludes PB entries | `pytest test_bridge_state_report_role_filter.py -q -k "lo"` | all LO-filter tests pass |
| Backward compatible | `pytest test_bridge_state_report_role_filter.py -q -k "no_role"` | passes |
| Markdown mode parity | `pytest test_bridge_state_report_role_filter.py -q -k "markdown"` | passes |
| No regression in existing state-report tests | `pytest platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py -q` | all pass |
| Lint | `ruff check state_report.py test_bridge_state_report_role_filter.py` | all pass |
| Format | `ruff format --check state_report.py test_bridge_state_report_role_filter.py` | already formatted |

## Acceptance Criteria

1. `gt bridge state-report --role pb` returns no NEW/REVISED/NO-ACTION/VERIFIED entries in any actionable array.
2. `gt bridge state-report --role lo` returns no GO/NO-GO entries in any actionable array.
3. Default (no `--role`) output is byte-identical to current output for the same bridge state.
4. PB startup overlay includes the hard session-focus menu generation rule.
5. LO startup overlay includes the reciprocal.
6. All tests pass; no regression in existing bridge state-report tests.
7. Only the four declared target files are modified.
8. No MemBase, dispatcher/TAFE, Git, deployment, or release mutation.

## Coordination Note — WI-5841 blocker

This proposal's MemBase work-item creation is blocked by the Goose G claim
resolution defect (WI-5841, GO'd at `-002`). Once WI-5841 is implemented,
the work item can be created and linked to this bridge thread. In the interim,
this proposal references the Advisory `-001` as its carrier and uses
`PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` as the project context.

## Bridge Chain Discipline

Filed as `bridge/gtkb-advisory-pb-session-focus-lo-contamination-002.md`,
appending to the Advisory chain without rewriting `-001`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — first-line role eligibility
- `GOV-SESSION-ROLE-AUTHORITY-001` — session role resolution authority
- `DCL-SESSION-ROLE-RESOLUTION-001` — interactive session role override
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact preservation
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-advisory-pb-session-focus-lo-contamination-001.md` — the
  Advisory that diagnosed this defect and proposed the fix architecture
- `WI-5686` — ENVELOPE_RESPONDER_BY_STATUS inverted (same defect class)
- `bridge/gtkb-wi5841-harness-selector-registry-derived-002.md` (GO) — the
  Goose claim resolution fix needed before MemBase writes work here

## Owner Decisions / Input

- 2026-07-31: "This item is a violation of GOV. It is never permitted for any
  session to switch roles. Please diagnose and correct this failure."
- 2026-07-31: "Correcting this defect so that this can never happen again is a
  P0 priority. Please create the Advisory Proposal and initiate the work
  necessary to fix this."

## Risk And Rollback

Risk is low. The `--role` parameter is additive; the default path is
unchanged. The overlay text changes are advisory guidance consumed by agents.
Rollback is straightforward reversion of the four target files.

## Recommended Commit Type

`fix` — corrects a role-confusion defect in bridge state-report output
surfacing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.