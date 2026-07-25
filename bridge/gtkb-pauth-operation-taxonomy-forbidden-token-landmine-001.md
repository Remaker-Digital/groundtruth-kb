NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 09e8949e-b3d4-42a0-b175-adf28dc87b17
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb


# PAUTH operation-taxonomy evaluator: unregistered forbidden-token begin() landmine (systemic)

bridge_kind: governance_advisory
Document: gtkb-pauth-operation-taxonomy-forbidden-token-landmine
Version: 001
Date: 2026-07-23 UTC

## Status of this entry

Governance-review advisory surfacing a systemic defect for conversion into a normal implementation proposal + work item by a future Prime Builder session. NOT an implementation proposal (no project-linkage metadata): THIS session (harness B, session-stated PB over durable-LO) cannot perform MemBase writes — `resolve_changed_by` fails closed ("Worker role provenance role conflicts with envelope role"), so a WI could not be created. Owner asked to chase this down before session close; this is the durable capture + owner decision of record.

## Finding (empirically confirmed)

`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py` `evaluate_envelope` (lines ~301-312) rejects `begin()` with reason_code `unknown_forbidden_operation` when ANY token in a PAUTH's `forbidden_operations` fails to normalize against `config/governance/project-authorization-operation-taxonomy.toml`.

Audit of all 661 PAUTHs (561 active) in `current_project_authorizations`:
- 518 distinct unregistered `forbidden_operations` tokens total.
- 230 token-form (snake_case) across active PAUTHs = REAL `begin()` landmines. Top usage: `broad_bulk_status_mutation` (46 active), `direct_harness_to_harness_invocation` (14), `bridge_protocol_bypass` (10), `cutover`/`bridge_rule_cutover` (6), `branch_worktree_prune` (5), `cli_extension` (5).
- 288 free-text prose labels (never intended as tokens).

Empirical (parsed forbidden_operations, real evaluator):
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`deploy,git_push_force,spec_deletion`) → forbidden check PASSES (after WI-5651 spec_deletion registration).
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` → `begin()` = `unknown_forbidden_operation` on `formal_artifact_mutation_without_packet, narrative_artifact_mutation, broad_bulk_status_mutation`. CONFIRMED landmine on an active PAUTH.

WI-5651's `spec_deletion` failure this session was one instance of this class.

## Root cause

Descriptive forbidden labels can never equal a canonical `requested_operation`. The real forbidden-collision check (line 304, with `normalize_token` fallback at line 302) already blocks a requested op that matches a forbidden token. The extra blanket rejection (306-312) adds only typo-catching value while landmining hundreds of active PAUTHs. Bulk-registering all 230 would grow the taxonomy ~13x, conflate operations with forbidden-labels, and re-open the gap for each new label.

## Owner Decision (AskUserQuestion, 2026-07-23)

Root-fix the evaluator: stop `begin()` blanket-rejecting unregistered forbidden labels; keep the existing forbidden-collision check. ("Bulk-register all 230" and "minimal + remediation project" declined.)

## Proposed implementation (for the future proposal)

1. Remove/downgrade the `unknown_forbidden_operation` rejection (lines ~306-312): unregistered forbidden tokens stay in the `forbidden` set (line 302) and still block a matching requested op (line 304), but no longer blanket-fail `begin()`. Optionally emit a non-blocking advisory/log for unregistered forbidden tokens (preserve typo visibility; fail open).
2. `spec_deletion` taxonomy registration (WI-5651 emergency-bootstrap, uncommitted in working tree) becomes OPTIONAL under this fix; recommend KEEP (legitimate operation, harmless).
3. Spec-to-test mapping (spec-derived; executed by the FUTURE implementation report, not this advisory):
   - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → new/updated cases in `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`: (a) a descriptive-label PAUTH PASSES `begin()` for a non-forbidden allowed-class op; (b) a forbidden collision still BLOCKS a matching requested op (registered AND unregistered token); (c) the `BATCH-001` fixture flips from `unknown_forbidden_operation` to allowed/target-scoped.
   - Command for the future implementation report: `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q` plus `ruff check` / `ruff format --check` on the changed evaluator source.
4. Governance review confirms no real forbidden-operation enforcement is weakened.

## Specification Links (candidate; the future proposal finalizes)

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-RELIABILITY-FAST-LANE-001` (lane TBD by the proposal given the governance-behavior surface)
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this advisory cites its governing specs; the future implementation proposal must cite every relevant spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the future proposal's tests derive from the linked specs (see Proposed implementation §3).
- operation-time-enforcement lineage `WI-5178` / evaluator_id `project-authorization-operation-time-enforcement` (search + cite the establishing ADR/DCL)

## Prior Deliberations

_No prior deliberations: novel forbidden-token blanket-rejection defect; an adjacent search for "operation taxonomy specification_deletion forbidden operations" returned only review-independence and envelope-sharding records; the future implementation proposal must run a fresh search and cite the WI-5178 operation-time-enforcement lineage._

## Evidence (ignored local, this session)

- `.gtkb-state/taxonomy_audit.py` — 230 token-form + 288 prose unregistered forbidden tokens; token-form vs prose classification.
- `.gtkb-state/verify_landmine.py` — empirical evaluator check confirming the BATCH-001 `begin()` failure and RELIABILITY-FIXES-STANDING pass.
- `.gtkb-state/finding-pauth-evaluator-forbidden-token-landmine.md` — full standalone finding capture.

## Next Steps (future Prime Builder session, clean identity)

1. Create a work item (PROJECT-GTKB-RELIABILITY-FIXES or a governance-reliability project) for the evaluator forbidden-token root-fix.
2. Convert this advisory into a normal implementation proposal (carry the design + tests; add project-linkage + Requirement Sufficiency).
3. LO GO → `begin()` (target_paths: evaluator source + tests) → implement → `git_lifecycle preserve` → report → VERIFIED.
4. Decide `spec_deletion` taxonomy registration disposition (keep recommended).

## Owner Decisions / Input

- 2026-07-23 AskUserQuestion: "Root-fix the evaluator" (this advisory's authorized direction).
- 2026-07-23 owner directive: "The taxonomy must be as up-to-date and complete as possible. Chase this down before we end this session." — chased to root cause + owner decision captured; full execution blocked this session by the MemBase-write provenance conflict and commit-path gates; handed off.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
