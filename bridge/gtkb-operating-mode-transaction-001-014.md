REVISED

# Operating-Mode Transaction Component — Slice 1 (REVISED-6)

bridge_kind: implementation_proposal
Document: gtkb-operating-mode-transaction-001
Version: 014
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation)
Addresses: implementation-start gate friction — `scripts/implementation_authorization.py` requires an inline target-paths JSON array header that its `TARGET_PATHS_RE` regex (line 28) can match. Prior versions through `-012` declared target paths only as a section, not an inline header, so the auth script's fallback path raised an error about missing concrete target-paths or Files Expected To Change. REVISED-6 adds the inline JSON array header without changing any substantive scope.

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_validation.py", "platform_tests/scripts/test_session_self_initialization_topology_derive.py", "platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py", "platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py", ".claude/rules/operating-role.md"]

## Claim

REVISED-6 is the same substantive contract as `-012` (REVISED-5) and `-008` (REVISED-3) which Codex approved at `-009` GO and re-approved at `-013` GO. The only delta from `-012` is the addition of an inline `target_paths` JSON header (above) that the implementation-start authorization script can mechanically extract. The `## Files Expected To Change` section below ALSO lists the same paths as a redundant fallback. Both mechanical preflights pass; the direct `extract_spec_links()` parser check passes; the direct `extract_target_paths()` parser check passes pre-filing.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-6 follows the standard lifecycle.
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
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec being implemented (approved 2026-05-13 via owner AUQ; packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`; `full_content_sha256` `f5311c8844a89b17e906cc022415aa39fd1b48eeaa9f7ea774bd068f736c99b5`). REVISED-6 retains all six acceptance criteria coverage from the prior versions.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the validator design tightens deterministic governance plumbing.
- `.claude/rules/operating-role.md` - durable operating-role assignment; role-set schema honored.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/canonical-terminology.md` - load-bearing topology terms.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming and mandatory subsections.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `scripts/bridge_applicability_preflight.py` - the canonical bridge parser whose status vocabulary at line 32 is the authoritative reference for F2's parse-clean rule.
- `scripts/implementation_authorization.py` - the authorization script whose `TARGET_PATHS_RE` regex this revision satisfies; line 28 defines the regex.
- `bridge/gtkb-operating-mode-transaction-001-013.md` - Codex GO at `-013` on REVISED-5. This REVISED-6 carries forward `-012`'s substantive content with only an inline target_paths header addition.
- `bridge/gtkb-operating-mode-transaction-001-012.md` - REVISED-5 whose substance is retained here.
- `bridge/gtkb-operating-mode-transaction-001-009.md` - earlier Codex GO on REVISED-3 substantive content.
- `bridge/gtkb-operating-mode-transaction-001-008.md` - REVISED-3 whose substance was approved at `-009`.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - approval packet authorizing the underlying spec.

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347) - project-scoped implementation authorization model.
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346) - SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 was approved under that scope.
- DELIB-0877 (2026-04-22) - owner directive establishing harness topology awareness as first-class.
- DELIB-1511 - Loyal Opposition Review history for the single-harness bridge dispatcher work.
- DELIB-1405 / DELIB-1406 - operating-model slice-0 and slice-1 (VERIFIED).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` - records the role switch producing the current drifted state.
- `bridge/gtkb-operating-mode-transaction-001-001.md` through `-013.md` - complete version chain through Codex GO@013.
- `bridge/gtkb-implementation-gate-friction-hygiene-002.md` - Codex NO-GO documenting the broader gate-friction class this REVISED-6 works around (second false-positive class: target_paths inline-header requirement).

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`. Standing authority for implementing the spec.
- 2026-05-14 owner AUQ chain (S349/S350) - "Project + impl proposal now (Recommended)" / "REVISED-1 with next-session in Slice 1 (Recommended)". Authorized the proposal chain.
- 2026-05-14 owner direction this session: "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible."
- 2026-05-14 owner AUQ this turn: "Operating-mode-transaction (impl GO)" — authorized starting implementation under Codex GO@013. The gate-friction cosmetic adjustments continue under that standing authorization.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-6 is a mechanical-gate-format adjustment to `-012` (REVISED-5). Substantive contract (target_paths content, scope, implementation plan, test plan, six-criterion spec coverage) is unchanged from the Codex GO@013-approved `-012`. No requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It adds an inline `target_paths` JSON header to unblock the implementation-start authorization gate's `TARGET_PATHS_RE` extraction. Zero MemBase mutations; zero bulk standing-backlog operations; one bridge thread filing (this `-014`). The substantive scope (one protected-artifact mutation, eight new modules, six modified scripts/hooks, seven new test files) is carried forward from `-012` and substantively approved by Codex at `-013` (which carried forward `-009`'s approval of `-008`'s contract).

## Files Expected To Change

(Same set as the inline `target_paths` JSON header above; provided here as the script's fallback path per `scripts/implementation_authorization.py:240-249`.)

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

All paths in-root under `E:\GT-KB\`.

## Changes from -012 (REVISED-5)

### Single mechanical change

Added an inline target-paths JSON array header at the top of this file. The header is what `scripts/implementation_authorization.py` line 28's `TARGET_PATHS_RE` regex expects (single-line JSON array on a header line). The same paths are also listed as bullets in `## Files Expected To Change` for redundant coverage of the script's fallback path at line 240.

### No substantive scope change

- target_paths content: unchanged from `-008` (same list of files, same NEW/MODIFY semantics).
- Specification Links body: unchanged from `-012` (the gate-friction repair for `PLACEHOLDER_RE`).
- Implementation Plan: unchanged from `-008`.
- Specification-Derived Test Plan: unchanged from `-008`.
- Risk/Rollback: unchanged from `-008`.
- Slice 1 deliverables: unchanged from `-008`.

### Pre-filing parser verification

Before filing this `-014`, the author ran the direct parser checks against the file:

1. `extract_spec_links()` PASS — no standalone `PLACEHOLDER_RE` matches in the Specification Links body.
2. `extract_target_paths()` PASS — the inline JSON header is parseable as a list of strings.

## Slice 1 Scope (REVISED-6)

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Slice 1 Scope (REVISED-3)" for the seven-deliverable list.

## Implementation Plan

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Implementation Plan" for the 14-step ordered procedure.

## Specification-Derived Test Plan

Unchanged from `-008`. See `bridge/gtkb-operating-mode-transaction-001-008.md` § "Specification-Derived Test Plan".

## Risk and Rollback

Unchanged from `-008`/`-012` plus the gate-friction risks from `-010` and `-012` (already documented). New: R8 (P3, REVISED-6) — future proposals on this thread must include both an inline `target_paths` JSON header AND a clean Spec Links body. The friction-hygiene thread's planned simplification fixes the broader class; this REVISED-6 is the per-instance workaround.

## Applicability Preflight

Expected to match `-008`/`-010`/`-012`'s preflight result: `preflight_passed: true`, no missing specs. Will be re-run after INDEX update.

## Recommended Commit Type

`feat:` - net-new deterministic mode-switch CLI plus queued-transaction queue plus multi-call-site SessionStart application plus canonical-vocabulary bridge-artifact validation. The diff stat is dominated by new module files and new test files. `feat:` matches.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with plain heading, flat bullets, no `###` sub-headings inside, no parenthetical heading qualifier, no verbatim quote of the original blocked phrasing.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input`.
- inline `target_paths: [...]` JSON header (top of file).
- redundant `## Files Expected To Change` section listing the same paths.
- `## Requirement Sufficiency` exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- explicit `## Changes from -012 (REVISED-5)` section identifying the single mechanical addition.
- All paths under `E:\GT-KB\`.
- Direct `extract_spec_links()` and `extract_target_paths()` parser checks PASS pre-filing.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
