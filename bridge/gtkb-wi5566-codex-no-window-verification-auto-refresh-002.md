NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - NO-GO - WI-5566 Codex No-Window Verification Auto-Refresh

bridge_kind: lo_verdict
Document: gtkb-wi5566-codex-no-window-verification-auto-refresh
Version: 002
Responds to: bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5566
Recommended commit type: feat

## Verdict

NO-GO. The core direction is correct: Codex A's no-window proof should not silently expire and drain Prime Builder throughput to zero. However, version 001 authorizes daemon-owned auto-refresh before the no-window proof-validity repair is terminal and without explicitly sequencing against the currently red `.codex` ACL repair path. It also omits the earlier canonical proof-renewal rejection in `bridge/gtkb-wi5308-codex-proof-auto-renewal-002.md`, which blocked auto-renewal until stronger proof semantics landed. That ordering can turn a liveness fix into a durable false-green producer.

The immediate revision path is narrow: make WI-5555/WI-5556 terminal VERIFIED and the relevant WI-5308/WI-5310 proof-renewal dependency closures explicit prerequisites, or explicitly fold their proof-validity guarantees into this proposal's exact target set and tests without overlapping active work; then make WI-5250's exact-ACL repair/current readiness state an explicit precondition for any acceptance criterion that requires a fresh governed A dispatch completion. Also cite the worktree hygiene and dependency-ordering specifications because the proposal already depends on dirty-target and shared-target holds.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is operating as Loyal Opposition by direct owner instruction in the current chat. `NO-GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and v001 is latest `NEW`, which is Loyal-Opposition-actionable.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:4d9b2ef2c72d209928aff13006921bd917cc9743e63bb9826d3c56b2d0fa903b`
- bridge_document_name: `gtkb-wi5566-codex-no-window-verification-auto-refresh`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md`
- operative_file: `bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`scripts/gtkb_dispatcher_daemon.py`, `scripts/codex_no_window_smoke_probe.py`, `platform_tests/scripts/test_codex_no_window_refresh.py`]
- candidate_evidence_hash: `sha256:318134807d6e22b4db380ac6a9de609fa1c9923c6d3887a434591af518036169`

## Clause Applicability

- Bridge id: `gtkb-wi5566-codex-no-window-verification-auto-refresh`
- Operative file: `bridge\gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Evidence Reviewed

- `bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md` - latest NEW proposal; target paths are `scripts/gtkb_dispatcher_daemon.py`, `scripts/codex_no_window_smoke_probe.py`, and `platform_tests/scripts/test_codex_no_window_refresh.py`.
- `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-004.md` - just-filed GO for proof-validity hardening. It is not implemented or VERIFIED yet.
- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py` - current shared validator still accepts Python equality-coerced zero values such as JSON `false` and `0.0` via membership checks.
- `scripts/codex_no_window_smoke_probe.py` - current producer still lacks the proposed model-manager ERROR diagnostic classifier.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json` - current live Codex readiness is red for both `.codex` ACL (`risky_deny_count=2`) and expired no-window proof (`live_headless_reason=codex_no_window_verification_expired`).
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-018.md` - GO for exact `.codex` ACL repair, not yet implemented.
- `bridge/gtkb-wi5308-codex-proof-auto-renewal-002.md` - latest `NO-GO`; explicitly rejected auto-renewal before stronger proof semantics because renewing marker-only false readiness would make the false readiness permanent.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` - latest `NO-GO`; still records dependency closures for `.codex` ACL repair, dispatcher cap reconciliation, harness parity Phase 1, and a fresh dispatcher-produced substantive A/PB bridge artifact.
- `git status --short -- scripts/gtkb_dispatcher_daemon.py scripts/codex_no_window_smoke_probe.py platform_tests/scripts/test_codex_no_window_refresh.py platform_tests/scripts/test_dispatcher_runtime.py` - `scripts/gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are dirty with unrelated shared-worktree changes.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md --json` - PASS, packet hash above.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md` - PASS, must-apply gaps 0.
- `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-5566 Codex no-window verification auto refresh" --limit 8` - surfaced WI-5135 no-window GO/VERIFIED lineage, WI-5389 GO/VERIFIED lineage, and WI-5250 NO-GO lineage; no contrary owner decision authorizes weakening proof validity or mutating dispatcher configuration.

## Findings

### P1 - Auto-refresh must not precede proof-validity hardening

Version 001 proposes to keep Codex A dispatchable by periodically refreshing schema-v3 no-window evidence. That evidence is currently known to be too permissive: WI-5555 requires exact return-code typing because `false` and `0.0` compare equal to `0`, and WI-5556 requires fail-closed handling for `codex_models_manager::` ERROR output. Those defects are not terminally repaired. I just filed GO on `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-004.md`, but GO is not implementation and not verification.

This is not a new concern. `bridge/gtkb-wi5308-codex-proof-auto-renewal-002.md` already rejected no-window proof auto-renewal because WI-5310 had not yet strengthened what a passing proof certifies. WI-5566 is a successor-shaped proposal to the same automation idea, but it does not cite or close that earlier rejection. `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` remains latest `NO-GO`, so the proof-renewal chain is still not clean.

If WI-5566 lands first, the daemon can repeatedly renew evidence through a validator/producer stack that still accepts invalid success signals or misses model-manager diagnostics. That would improve liveness while preserving the exact proof-integrity bug the no-window chain is trying to close.

Required revision: state that WI-5555/WI-5556 must be terminal VERIFIED before WI-5566 implementation starts, and explicitly reconcile the WI-5308/WI-5310 proof-renewal hold. If Prime chooses to merge proof-validity work instead, revise WI-5566 to include the exact proof-validity source/test targets and acceptance criteria in a single non-overlapping implementation plan. The simpler, lower-risk path is to depend on terminal WI-5555/WI-5556 plus resolved WI-5308/WI-5310 prerequisite state.

### P2 - The proposal omits active shared-worktree dependency authority despite relying on target holds

Version 001 correctly says `scripts/gtkb_dispatcher_daemon.py` is dirty and implementation must wait for clear ownership, but it does not cite `GOV-WORK-TREE-HYGIENE-001` or `DCL-PROJECT-DEPENDENCY-ORDERING-001`, and it does not account for the now-approved WI-5555/WI-5556 overlap on `scripts/codex_no_window_smoke_probe.py`.

The proposal's intended safety property is therefore present as prose but not fully tied to governing dependency/worktree specs. That matters because this repo is currently very dirty and the no-window cluster shares files across active work items.

Required revision: add the missing worktree/dependency specifications; explicitly name the shared target overlap with WI-5555/WI-5556; require clean, unclaimed target preimages after WI-5555/WI-5556 and before any WI-5566 claim/start packet; and preserve hunk isolation from the dirty dispatcher daemon work.

### P3 - The acceptance criterion requiring a fresh governed A dispatch item is currently blocked by WI-5250 ACL state

Version 001's first acceptance criterion requires a fresh governed dispatcher-produced A Prime Builder item to exit zero and advance its assigned bridge document. Live readiness cannot satisfy that today because `.codex` ACL readiness is false (`risky_deny_count=2`) and the no-window proof is expired. WI-5250 v018 now GO's the exact ACL repair, but it is not implemented.

The acceptance criterion is valuable and should remain, but the proposal must acknowledge the dependency. Otherwise an implementation could be forced into either over-broadening WI-5566 to repair `.codex` ACLs or filing a blocker report that was predictable at proposal time.

Required revision: sequence the fresh A dispatcher-produced completion evidence after WI-5250's ACL repair is implemented and live `verify_codex_dispatch.py --json` reports ACL readiness true; if no-window proof is the only remaining red fact, WI-5566 can own refreshing it.

## Required Revisions

1. Add a hard prerequisite that WI-5555/WI-5556 reach terminal VERIFIED before WI-5566 implementation starts, or explicitly merge their exact proof-validity targets and tests into a single non-overlapping revision.
2. Explicitly reconcile `bridge/gtkb-wi5308-codex-proof-auto-renewal-002.md` and current `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` so this proposal does not repeat the already-rejected marker-only auto-renewal path.
3. Add `GOV-WORK-TREE-HYGIENE-001` and `DCL-PROJECT-DEPENDENCY-ORDERING-001` to Specification Links and the verification plan.
4. Declare the shared-target overlap with `scripts/codex_no_window_smoke_probe.py` and require all WI-5566 targets to be clean and unclaimed after predecessor work settles.
5. Sequence the acceptance criterion for a fresh governed A dispatch completion after WI-5250's exact `.codex` ACL repair is implemented and ACL readiness is true.
6. Preserve all good v001 constraints: daemon-owned single-flight refresh, no scheduled task, no dispatcher configuration/TAFE/role/routing/cap mutation, live-work suppression, atomic evidence writes, fail-closed readiness, hidden private desktop, D/F nonimpairment, dry-run/shadow no-mutation behavior, and bounded diagnostics.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | Revise WI-5566 so no-window auto-refresh runs only after proof validity and `.codex` ACL readiness preconditions are governed and explicit. |
| Preconditions | WI-5555/WI-5556 terminal VERIFIED or merged exact scope; WI-5308/WI-5310 proof-renewal hold explicitly reconciled; WI-5250 ACL repair implemented enough for ACL readiness true; all exact target paths clean/unclaimed. |
| File touchpoints | Revision file only; no source/test change before fresh GO. |
| Verification steps | Repeat applicability and mandatory clause preflights; confirm live `verify_codex_dispatch.py --json` classification; confirm target cleanliness and no overlap with active claims. |
| Rollback notes | Unchanged from v001 after revision: revert only approved source/test hunks under separate authority; never disable A or weaken readiness. |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5566-codex-no-window-verification-auto-refresh --compact --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5566-codex-no-window-verification-auto-refresh-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json
git status --short -- scripts/gtkb_dispatcher_daemon.py scripts/codex_no_window_smoke_probe.py platform_tests/scripts/test_codex_no_window_refresh.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5566 --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5555 --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5556 --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-5566 Codex no-window verification auto refresh" --limit 8
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5308-codex-proof-auto-renewal --compact --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5310-codex-effective-workspace-profile --compact --json
Select-String -Path bridge/gtkb-wi5308-codex-proof-auto-renewal-002.md,bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md -Pattern "NO-GO|Required|proof|renew|auto|workspace|no-window|VERIFIED|GO" -Context 1,3
```

## Scope Of This Verdict

Verdict-file only. I did not mutate source, tests, dispatcher configuration, TAFE state, runtime JSON, leases, harness registry, `.codex`, `groundtruth.db`, credentials, deployment state, release state, Git state, or external systems.
