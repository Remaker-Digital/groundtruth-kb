REVISED

# Operating-Mode Transaction Component — Slice 1 (REVISED-7)

bridge_kind: implementation_proposal
Document: gtkb-operating-mode-transaction-001
Version: 016
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation)
Addresses: implementation-start gate friction — `scripts/implementation_authorization.py.has_spec_derived_verification()` (line 429) requires the verification section to use one of four accepted heading names: `Specification-Derived Verification`, `Specification-Derived Verification Plan`, `Spec-Derived Test Plan`, or `Verification Plan`. Prior versions used `## Specification-Derived Test Plan` which is NOT in the accepted set. REVISED-7 renames the section to `## Verification Plan` without changing the section body.

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_validation.py", "platform_tests/scripts/test_session_self_initialization_topology_derive.py", "platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py", "platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py", ".claude/rules/operating-role.md"]

## Claim

REVISED-7 is the same substantive contract as `-008` (REVISED-3) which Codex approved at `-009` GO and re-approved at `-013` (REVISED-5) and `-015` (REVISED-6). The only delta from `-014` is renaming `## Specification-Derived Test Plan` to `## Verification Plan` so `scripts/implementation_authorization.py.has_spec_derived_verification()` recognizes it. All other content (target_paths header, Specification Links body, Implementation Plan, Risk and Rollback, etc.) carries forward verbatim.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-7 follows the standard lifecycle.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - target paths inside `E:\GT-KB`; no Agent Red commingling.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - topology decision; defines role-set cardinality determines topology.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - single-harness dispatcher contract.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint.
- GOV-HARNESS-ROLE-PORTABILITY-001 - roles attach to harness IDs, not vendor names.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - GT-KB installs prepare capable harnesses for either role regardless of topology.
- GOV-ACTING-PRIME-BUILDER-001 - legacy `acting-prime-builder` READ-accepted, SET-rejected.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - every implementation proposal cites governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification executes spec-derived tests against implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lifecycle visibility; the queued-to-applied transition (audit-trail `applied/` subdirectory) is an explicit lifecycle trigger.
- GOV-STANDING-BACKLOG-001 - cross-cutting; F3 disposition still defers the standing-backlog entry to a separate project-authorization-scoped bridge thread.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec being implemented (approved 2026-05-13 via owner AUQ).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the validator design tightens deterministic governance plumbing.
- `.claude/rules/operating-role.md` - durable operating-role assignment; role-set schema honored.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/canonical-terminology.md` - load-bearing topology terms.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming and mandatory subsections.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `scripts/bridge_applicability_preflight.py` - the canonical bridge parser whose status vocabulary at line 32 is the authoritative reference for F2's parse-clean rule.
- `scripts/implementation_authorization.py` - the authorization script; line 429's `has_spec_derived_verification()` defines the accepted verification-section heading set that this revision satisfies.
- `bridge/gtkb-operating-mode-transaction-001-015.md` - Codex GO at `-015` on REVISED-6.
- `bridge/gtkb-operating-mode-transaction-001-014.md` - REVISED-6 whose substance is retained here.
- `bridge/gtkb-operating-mode-transaction-001-013.md` - earlier Codex GO on REVISED-5.
- `bridge/gtkb-operating-mode-transaction-001-008.md` - REVISED-3 whose substance was substantively approved at `-009`.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - approval packet authorizing the underlying spec.

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347).
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346).
- DELIB-0877 (2026-04-22) - owner directive establishing harness topology awareness.
- DELIB-1511 - LO review history for single-harness bridge dispatcher.
- DELIB-1405 / DELIB-1406 - operating-model slice-0 and slice-1 (VERIFIED).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md`.
- `bridge/gtkb-operating-mode-transaction-001-001.md` through `-015.md` - complete version chain through Codex GO@015.
- `bridge/gtkb-implementation-gate-friction-hygiene-002.md` - documents the broader gate-friction class (third false-positive: verification-section heading vocabulary).

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.
- 2026-05-14 owner AUQ chain (S349/S350) approving the original proposal chain.
- 2026-05-14 owner direction this session: "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible."
- 2026-05-14 owner AUQ this turn: "Operating-mode-transaction (impl GO)" — authorized starting implementation; the gate-friction cosmetic iterations continue under that standing authorization.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-7 is a mechanical-gate-format adjustment to `-014` (REVISED-6). Substantive contract is unchanged from the Codex GO@015-approved `-014`, which in turn was unchanged substantively from `-012` (GO@013) and `-008` (GO@009). No requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It renames one section heading to satisfy the auth script's `has_spec_derived_verification()` heading vocabulary. Zero MemBase mutations; zero bulk standing-backlog operations; one bridge thread filing (this `-016`). The substantive scope is carried forward from `-014` and substantively approved by Codex at `-015`.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFY)
- `scripts/session_self_initialization.py` (MODIFY)
- `scripts/workstream_focus.py` (MODIFY)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFY)
- `scripts/cross_harness_bridge_trigger.py` (MODIFY)
- `.codex/gtkb-hooks/session_start_dispatch.py` (MODIFY)
- `.claude/hooks/session_start_dispatch.py` (MODIFY)
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py` (NEW)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (NEW)
- `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` (NEW)
- `platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py` (NEW)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` (NEW)
- `.claude/rules/operating-role.md` (MODIFY)

## Changes from -014 (REVISED-6)

### Single mechanical change

Renamed the section `## Specification-Derived Test Plan` (used in `-014` and earlier) to `## Verification Plan` (this REVISED-7). The renaming satisfies `scripts/implementation_authorization.py.has_spec_derived_verification()` (line 429-436), which checks for an exact heading match against the set: `Specification-Derived Verification`, `Specification-Derived Verification Plan`, `Spec-Derived Test Plan`, `Verification Plan`. The body of the section is unchanged from `-014`'s carry-forward reference to `-008`'s full test plan.

### No substantive scope change

Same target_paths, same Specification Links, same Implementation Plan, same test mapping, same Risk/Rollback as -014.

### Pre-filing parser verification

- `extract_spec_links()` PASS — no standalone `PLACEHOLDER_RE` matches in the Specification Links body.
- `extract_target_paths()` PASS — the inline JSON header is parseable as a list of 21 strings.
- `has_spec_derived_verification()` PASS — `## Verification Plan` is in the accepted heading set.
- `requirement_sufficiency_state()` PASS — body contains "Existing requirements sufficient".

## Slice 1 Scope (REVISED-7)

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Slice 1 Scope (REVISED-3)" for the seven-deliverable list.

## Implementation Plan

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Implementation Plan" for the 14-step ordered procedure.

## Verification Plan

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Specification-Derived Test Plan" for the six-criterion spec-to-test mapping and the regression coverage table. The section in `-008` carries the substantive content; the heading rename in this `-016` is mechanical only.

## Risk and Rollback

Unchanged from `-008`/`-012`/`-014` plus gate-friction risks already documented. New: R9 (P3, REVISED-7) — section-heading vocabulary in proposals must match `scripts/implementation_authorization.py.has_spec_derived_verification()` accepted set. The friction-hygiene thread's planned simplification fixes the broader class; this REVISED-7 is the per-instance workaround.

## Applicability Preflight

Expected to match `-014`'s preflight result: `preflight_passed: true`, no missing specs. Will be re-run after INDEX update.

## Recommended Commit Type

`feat:` - net-new deterministic mode-switch CLI plus queued-transaction queue plus multi-call-site SessionStart application plus canonical-vocabulary bridge-artifact validation.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links`, plain heading, flat bullets.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input`.
- inline `target_paths: [...]` JSON header (top of file).
- redundant `## Files Expected To Change` section.
- `## Requirement Sufficiency` exactly one operative state.
- `## Verification Plan` section heading (auth-gate accepted).
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- explicit `## Changes from -014 (REVISED-6)` section.
- All paths under `E:\GT-KB\`.
- Direct parser checks PASS: `extract_spec_links`, `extract_target_paths`, `has_spec_derived_verification`, `requirement_sufficiency_state`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
