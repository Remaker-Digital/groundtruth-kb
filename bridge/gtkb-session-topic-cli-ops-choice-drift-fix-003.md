NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5c27c830-3746-42d9-9cb7-36bee91752f5
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder (durable PB, harness B); WI-4819 post-implementation report

# Implementation Report — WI-4819 `gt session topic` CLI `click.Choice` sourced from `TOPIC_TYPES`

bridge_kind: prime_proposal
Document: gtkb-session-topic-cli-ops-choice-drift-fix
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-session-topic-cli-ops-choice-drift-fix-002.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4819

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_cli_choice.py"]

## Summary

Implemented the GO'd fix (proposal -001, GO at -002). Both `gt session topic open` / `close` CLI commands now source their `click.Choice` from the canonical `envelope.TOPIC_TYPES`, so `ops` (and any future vocabulary member) is accepted at the CLI parse surface. The vocabulary-drift bug class is closed: the CLI can no longer diverge from `TOPIC_TYPES`. Implementation authorized by implementation-start packet `sha256:3c1cab39f69055cfbf26b9a2e383a334c4b41b2c02882503aa040b6e354371fb` (latest_status GO, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / WI-4819).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:
  - Added module-top-level import `from groundtruth_kb.session.envelope import TOPIC_TYPES` (required because `click.Choice(...)` evaluates at decoration/import time; no circular import — `envelope.py` imports `harness_projection`, never the CLI module).
  - `topic_open_cmd` and `topic_close_cmd`: both `click.Choice(["spec", "build", "test", "deliberation", "project"])` literals replaced with `click.Choice(list(TOPIC_TYPES))`.
- `platform_tests/scripts/test_session_envelope_cli_choice.py` (new): 5 spec-derived tests.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — six-member activity vocabulary; CLI now accepts it.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — open/close grammar enumerates `ops`; CLI parse surface now matches.
- `GOV-RELIABILITY-FAST-LANE-001` — small bounded defect fix via the reliability fast-lane standing authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is an append-only, monotonically-versioned numbered bridge file; VERIFIED finalization is owned by Loyal Opposition.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; tests executed against the implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from the GO'd proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project` / `Project Authorization` / `Work Item` metadata present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active project membership).
- `GOV-STANDING-BACKLOG-001` — WI-4819 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files are in-root under `E:\GT-KB` (`groundtruth-kb/`, `platform_tests/`); no Agent Red surface mutated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — defect, fix, tests, and decision preserved as durable artifacts (WI-4819, this thread, the cited deliberations).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability preserved across WI ↔ proposal ↔ report ↔ tests ↔ specs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4819 advances through bridge lifecycle states (candidate → GO → report → VERIFIED).

## Spec-Derived Verification Plan (spec-to-test mapping + executed results)

| Specification (clause) | Test | Result |
|---|---|---|
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — six-member vocabulary is the CLI-accepted set (open) | `test_topic_open_choice_equals_topic_types` | PASS |
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — six-member vocabulary is the CLI-accepted set (close) | `test_topic_close_choice_equals_topic_types` | PASS |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — `ops` accepted at the open parse surface (was BadParameter) | `test_cli_topic_open_ops_accepted` (isolated tmp root, runtime stubbed; + negative control rejecting an unknown type and listing `ops`) | PASS |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — `ops` accepted at the close parse surface | `test_cli_topic_close_ops_accepted` | PASS |
| Anti-drift invariant (bug-class repair) | `test_both_topic_choices_sourced_from_topic_types` (both Choice sets identical to `TOPIC_TYPES`) | PASS |

Executed commands and observed results:

- `python -m pytest platform_tests/scripts/test_session_envelope_cli_choice.py -q` → **5 passed** (0.25s).
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/scripts/test_session_envelope_cli_choice.py` → **All checks passed!**
- `python -m ruff format --check <same files>` → **2 files already formatted**.

## Acceptance Criteria Check

- `gt session topic open ops` / `close ops` no longer fail with `click.BadParameter` — satisfied (CLI-accept tests PASS).
- Both `click.Choice` sets sourced from `envelope.TOPIC_TYPES` (6-member) — satisfied (anti-drift test PASS).
- Bare-close CLI explicitly out of scope — honored (no CLI signature change beyond the Choice source).

## Requirement Sufficiency

Existing requirements sufficient (carried forward from the GO'd proposal). No new or revised requirement was needed.

## Recommended Commit Type

`fix:` — repairs a usage-blocking CLI defect for the `ops` activity type; the new test file is regression coverage for the fix, not a new capability surface. (Matches the GO verdict's recommended type.)

## Owner Decisions / Input

- Owner directive (2026-06-25): classify as reliability-fast-lane defect, fix by sourcing both `click.Choice` lists from `TOPIC_TYPES`, file standalone via the bridge protocol, defer bare-close.
- Owner AUQ (2026-06-25, `AUQ-2026-06-25-wi4819-pauth-home`, archived `DELIB-20265898`): WI-4819's home is the reliability fast-lane standing authorization (`PROJECT-GTKB-RELIABILITY-FIXES` + `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`), accepting that WI-4819 must reach VERIFIED before that project can retire.

## Prior Deliberations

- `DELIB-20265287` — `ops` re-admission to the activity vocabulary (defect lineage).
- `DELIB-20265892` — owner ratified all six seed disposition profiles.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — reliability fast-lane standing authorization.
- `DELIB-20265898` — owner AUQ home decision for WI-4819 + retirement-caveat acceptance.

## Risk / Rollback

- Risk: low. Choice widened from 5→6 (superset, sourced from the canonical tuple); no removed value, no call-site semantics change, no envelope-state change. Orthogonal to WI-4685 (now VERIFIED at HEAD) — disjoint file (`cli_session_handoff.py`).
- Rollback: revert `cli_session_handoff.py` to the literals and delete the new test file. No data migration.

## Verification Request

Loyal Opposition: please verify the spec-to-test mapping and execution evidence above against the working-tree implementation, then finalize VERIFIED via the commit-finalization helper, staging the two `target_paths` plus the verdict.
