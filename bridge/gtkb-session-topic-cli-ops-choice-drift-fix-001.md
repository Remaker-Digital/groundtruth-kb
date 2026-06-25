NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5c27c830-3746-42d9-9cb7-36bee91752f5
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder (durable PB, harness B); reliability fast-lane defect WI-4819

# Implementation Proposal — WI-4819 `gt session topic` CLI `click.Choice` omits `ops` (vocabulary-drift defect)

bridge_kind: prime_proposal
Document: gtkb-session-topic-cli-ops-choice-drift-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4819

Home rationale: WI-4819 is filed through the reliability fast-lane standing authorization (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, governed by `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), chosen by owner AskUserQuestion 2026-06-25 (archived `DELIB-20265898`). The GT-KB bridge gate requires a `Project` + `Project Authorization` on every implementation proposal (`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`); the reliability fast lane is the GOV-sanctioned home for standalone small defects. This preserves the owner's original "not envelope-disposition" intent — WI-4819 is NOT in the snapshot-bound `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` (`DELIB-20265586`). Accepted caveat: WI-4819 is now an active member of PROJECT-GTKB-RELIABILITY-FIXES and must reach VERIFIED before that project can retire.

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_cli_choice.py"]

## Summary

`groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` defines `gt session topic open` (`topic_open_cmd`, ~L103) and `gt session topic close` (`topic_close_cmd`, ~L117). Both hardcode `@click.argument("topic_type", type=click.Choice(["spec", "build", "test", "deliberation", "project"]))` — a **5-member** parallel list that drifted from the canonical **6-member** activity vocabulary `envelope.TOPIC_TYPES = ("ops", "deliberation", "build", "test", "spec", "project")` (`groundtruth-kb/src/groundtruth_kb/session/envelope.py:20`).

The runtime fully supports `ops`: `open_topic`/`close_topic` validate against `TOPIC_TYPES` (envelope.py:316, :384), and `ROUTE_TARGETS` (:23) and `PRELOAD_STATES` (:32) both carry an `ops` entry. Only the CLI's hardcoded `click.Choice` gate rejects it, so `gt session topic open ops` and `gt session topic close ops` fail at argument parsing with `click.BadParameter` ("'ops' is not one of ..."). This is a vocabulary-drift residual of WI-4683, which added `ops` to `TOPIC_TYPES` (committed at HEAD; verified `git show HEAD:.../envelope.py`) without updating the CLI's copied list.

**Fix:** source both `click.Choice` lists from `envelope.TOPIC_TYPES` so `ops` is accepted and the 6-member vocabulary cannot drift from the CLI again — repairing the bug *class*, not just this instance.

**Out of scope (explicit):** exposing a bare no-arg `gt session topic close` form. The owner noted the runtime `close_current_topic()` exists, but it is currently uncommitted/unverified (the WI-4685 single-active-invariant work sits in the working tree with its bridge thread `gtkb-wi4685-single-active-envelope-invariant` at `NEW`), and bare-close overlaps active WI-4729 (`::close` idempotency). Coupling this standalone defect to in-flight work contradicts the owner's standalone directive. Bare-close CLI exposure is left to the WI-4685 thread or a separate follow-up after that runtime verifies.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — Topic-Envelope Router Umbrella Specification; establishes the six-member activity vocabulary `{ops, deliberation, build, test, spec, project}` that `TOPIC_TYPES` encodes and the CLI must accept.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — Topic-Envelope Routing: Conformance Constraints; the open/close grammar enumerates `ops` as a valid type. The CLI Choice set is the argument-parse surface for that grammar and must match it.
- `GOV-RELIABILITY-FAST-LANE-001` — small, bounded defect fix filed through the reliability fast-lane standing authorization; full propose → GO → implement → report → VERIFIED cycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization` / `Project` / `Work Item` metadata lines are present (above).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, which authorizes GOV-RELIABILITY-FAST-LANE-001-eligible fixes by active project membership.
- `GOV-STANDING-BACKLOG-001` — WI-4819 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as an append-only, monotonically-versioned numbered bridge file (`bridge/<slug>-NNN.md`) and follows the GO/NO-GO/VERIFIED discipline. The audit trail is never deleted or rewritten in place.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing specification and maps tests to them below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping below derives tests from the linked v3 specs; `python -m pytest` is the execution command.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — placement/root boundary; all target paths are in-root under `E:\GT-KB` (`groundtruth-kb/`, `platform_tests/`); no out-of-root path and no Agent Red surface is mutated.
- `project-root-boundary` (`.claude/rules/project-root-boundary.md`) — same in-root constraint, narrative authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the defect, decision, and deferral are preserved as durable artifacts (WI-4819, this bridge thread, the cited deliberations).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability is preserved across WI ↔ proposal ↔ tests ↔ specs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4819 carries an explicit lifecycle state (`unapproved` candidate) and advances through the bridge GO/VERIFIED transitions.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 (owner-ratified 2026-06-25; DELIB-20265891) already define the six-member vocabulary and the open/close grammar that includes `ops`. The defect is a CLI surface that fails to honor an existing, ratified requirement. No new or revised requirement is needed before implementation.

## Implementation Plan

1. `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:
   - Add a module-top-level import `from groundtruth_kb.session.envelope import TOPIC_TYPES` (needed because `click.Choice(...)` is evaluated at decoration/import time, not call time). No circular import: `envelope.py` imports `groundtruth_kb.harness_projection`, never the CLI module.
   - `topic_open_cmd` (~L103): replace `click.Choice(["spec", "build", "test", "deliberation", "project"])` with `click.Choice(list(TOPIC_TYPES))`.
   - `topic_close_cmd` (~L117): same replacement.
   - No change to the typed `open_topic`/`close_topic` call sites — they already pass `topic_type` through to the runtime, which validates against `TOPIC_TYPES`.
2. `platform_tests/scripts/test_session_envelope_cli_choice.py` (new): the spec-derived regression tests below. The structural assertions guarantee future additions to `TOPIC_TYPES` propagate to the CLI automatically (drift can no longer recur).

## Spec-Derived Verification Plan (spec-to-test mapping)

| Specification (clause) | Test / verification | Command |
|---|---|---|
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — six-member vocabulary must be the CLI-accepted set (open) | `test_topic_open_choice_equals_topic_types`: the `topic_open_cmd` `topic_type` param `click.Choice.choices` equals `set(envelope.TOPIC_TYPES)` | `python -m pytest platform_tests/scripts/test_session_envelope_cli_choice.py` |
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 — six-member vocabulary must be the CLI-accepted set (close) | `test_topic_close_choice_equals_topic_types`: same assertion for `topic_close_cmd` | same |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — `ops` is a valid open type at the CLI parse surface | `test_cli_topic_open_ops_accepted`: `CliRunner` invocation of `session topic open ops` against an isolated tmp project root does NOT raise `click.BadParameter` (exit code != 2-for-usage; was a usage error pre-fix) | same |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v3 — `ops` is a valid close type at the CLI parse surface | `test_cli_topic_close_ops_accepted`: `CliRunner` invocation of `session topic close ops` against an isolated tmp project root is not rejected as an invalid choice | same |
| Anti-drift invariant (bug-class repair) | `test_both_topic_choices_sourced_from_topic_types`: both commands' Choice sets are identical to `TOPIC_TYPES`, so a future `TOPIC_TYPES` addition cannot drift the CLI | same |

Code-quality gates on touched files: `python -m ruff check <files>` and `python -m ruff format --check <files>` (both run before the post-implementation report per the file-bridge code-quality gate).

## Prior Deliberations

- `DELIB-20265287` — re-admit `ops` to the activity vocabulary; the activity-vocabulary defect classification that motivates keeping `ops` in `TOPIC_TYPES`. Direct lineage of why the CLI must accept `ops`.
- `DELIB-20265892` — owner ratified all six seed disposition profiles (`ops`/`deliberation`/`build`/`test`/`spec`/`project`); confirms the canonical six-member vocabulary the CLI must mirror.
- `DELIB-20265891` — envelope-disposition drive strategy and the WI-4685 v3 spec-amendment ratification; the broader program context this defect is a residual of.
- `DELIB-20265586` — the owner ACID-invariant that snapshot-binds `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`; the reason this defect is filed standalone rather than added to that project.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — establishes the reliability fast-lane standing authorization (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) that hosts this fix.
- `DELIB-20265898` — owner AUQ decision (2026-06-25) selecting that standing PAUTH as WI-4819's home and accepting the retirement caveat.
- Deliberation search (2026-06-25) returned no decision opposing the fix or its reliability-fast-lane classification.

## Owner Decisions / Input

- Owner directive (2026-06-25): the owner identified the defect, classified it as a "small reliability-fast-lane defect (origin=defect, component=cli/envelope)", directed it be fixed by adding `ops` to both `click.Choice` lists (preferring sourcing from `TOPIC_TYPES`), and directed it be filed via the bridge protocol (propose → GO → implement → report → VERIFIED) as a **standalone** GT-KB platform WI, explicitly NOT added to `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`.
- The owner directed the bare-close CLI consideration be weighed; this proposal records the decision to defer it (dependency on uncommitted WI-4685 runtime + overlap with WI-4729), keeping the defect tightly scoped.
- Owner AUQ (2026-06-25, `AUQ-2026-06-25-wi4819-pauth-home`, archived `DELIB-20265898`): filing surfaced the hard `Project`+`PAUTH` gate (no project-less path exists). Owner chose the reliability fast-lane standing authorization (`PROJECT-GTKB-RELIABILITY-FIXES` + `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) as WI-4819's home, accepting that WI-4819 must reach VERIFIED before that project can retire.

## Risk / Rollback

- Risk: low. The change widens an argument `click.Choice` from 5 to 6 members (a superset) and sources it from the canonical tuple. No previously-accepted value is removed; no call-site semantics change. The only behavioral change is that `ops` is now accepted (which the runtime already supported).
- Interaction with in-flight WI-4685: none. WI-4685 modifies the close *semantics* in `envelope.py` (single-active); this change touches only the CLI's accepted-type *set* in `cli_session_handoff.py` (a clean file). The two are orthogonal and edit disjoint files.
- Rollback: revert `cli_session_handoff.py` to the 5-member literals and delete the new test file. No data migration; envelope state is per-session local JSON.

## Recommended Commit Type

`fix:` — repairs broken CLI behavior (a usage-blocking defect for the `ops` activity type). The accompanying new test file is regression coverage for the fix, not a new capability surface.
