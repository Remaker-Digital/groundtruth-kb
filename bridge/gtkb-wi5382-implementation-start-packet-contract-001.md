NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; ::open build; reasoning=xhigh; approval_policy=never
author_metadata_source: explicit_current_codex_thread_metadata

# WI-5382: Make Implementation Start Emit a Named Packet or Diagnostic

bridge_kind: prime_proposal
Document: gtkb-wi5382-implementation-start-packet-contract
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5382-IMPLEMENTATION-START-PACKET-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5382

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The implementation-start boundary must be a deterministic contract: `python scripts/implementation_authorization.py begin --bridge-id <slug>` either emits and, when not in `--no-write` mode, durably writes the exact bridge-named schema-v3 implementation-start packet for the acting session, or exits nonzero with machine-readable JSON diagnostics explaining why no packet was created.

WI-5382 captures repeated governed GO attempts where the start command reportedly produced no named schema-v3 packet and no useful output, leaving unrelated `current.json` state as the only visible artifact. Current source already contains named-cache and schema-v3 helper functions; this proposal asks Loyal Opposition to approve a narrow hardening slice that makes the CLI-level behavior observable, regression-tested, and side-effect-safe. The work must not broaden PAUTH, target path, work-intent, shared-path, currentness, or review-independence rules.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5382` and keeps owner authorization, project authorization, bridge review, work-intent, implementation-start, spec-derived verification, implementation report, and independent Loyal Opposition verification gates intact.

## Requirement Sufficiency

Existing requirements sufficient.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; WI-5382; repeated bridge NO-ACTION/NO-GO evidence citing missing named schema-v3 implementation-start packets",
  "canonical_authority": "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, and GOV-FILE-BRIDGE-AUTHORITY-001.",
  "primary_route": "Fresh Loyal Opposition GO, exact go_implementation claim, schema-v3 implementation-start packet, focused implementation report, independent VERIFIED, and focused terminal commit.",
  "before_behavior": "Eligible GO threads could report an implementation-start attempt that left no named schema-v3 packet and no actionable diagnostic, stranding protected work behind an opaque start boundary.",
  "after_behavior": "The begin command is externally auditable: success returns the same finalized schema-v3 packet written to the bridge-named cache and current pointer, while failure returns deterministic JSON denial and writes no packet state.",
  "self_descriptive_naming": "The bridge slug, PAUTH id, work item, target paths, and test plan all name the implementation-start packet contract directly.",
  "obsolete_guidance_disposition": "The repair must not make current.json authoritative over named packets, revive retired aggregate queues, bypass work-intent claims, or treat PAUTH/project membership as implementation authority by itself.",
  "history_preservation": "Prior failed-start bridge evidence, existing named-packet cache files, current.json behavior, and foreign worktree hunks remain preserved; this proposal creates only a new numbered bridge thread.",
  "baseline": {
    "work_item_state": "WI-5382 is open/backlogged with no existing bridge thread.",
    "project_authorization": "PAUTH-DISPATCHER-BLACK-BOX-WI5382-IMPLEMENTATION-START-PACKET-20260716 is active and includes WI-5382.",
    "current_code_state": "Named-cache, schema-v3 finalization, and JSON denial surfaces exist but need focused end-to-end regression around the CLI contract."
  },
  "expected_result": {
    "successful_begin": "A valid GO plus matching claim produces a schema-v3 packet, writes by-bridge/<slug>.json before current.json, and prints the same packet JSON.",
    "denied_begin": "A missing claim, stale PAUTH, invalid target, or shared-path conflict exits nonzero with {\"authorized\": false, \"error\": \"...\"} and creates neither named nor current packet state.",
    "no_write": "--no-write prints a non-durable pre-start packet for diagnostics and leaves both named and current packet paths absent."
  },
  "rollback": {
    "instructions": "If regression coverage shows the existing CLI already satisfies every acceptance condition, file an implementation report with the no-source-change evidence and only add the focused tests approved here.",
    "verification": "Rerun the focused implementation-authorization tests, PAUTH operation-time tests, and candidate/live bridge preflights before requesting verification."
  },
  "hard_invariants": [
    "No protected mutation occurs from this NEW entry alone.",
    "No source or test edit is authorized without fresh GO, matching claim, and implementation-start authorization.",
    "No dispatcher, TAFE, runtime, lease, credential, Git history, push, deployment, release, or unrelated file mutation is authorized.",
    "Denied implementation-start attempts remain side-effect-free for packet state."
  ]
}
```

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct, append-only numbered bridge filings and live bridge-state reads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - defines project-scoped PAUTH as owner-approval evidence that never replaces bridge GO, target scoping, implementation-start packets, reports, or verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires every proposal, work-intent, packet, and start operation to enforce the current PAUTH envelope and produce side-effect-free denials.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - forbids using PAUTH as a bridge bypass and preserves latest-GO, target-path, report, and verification gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable PAUTH, project, work-item, and target-path metadata in this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links and proposal preflight evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation verification to map executed tests to the linked requirements.
- `GOV-WORK-TREE-HYGIENE-001` - requires preserving existing foreign hunks and avoiding unrelated worktree adoption.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the bridge, draft, source, test, and packet surfaces in the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the defect, PAUTH, proposal, tests, report, and verdict to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports the artifact-first flow from reproduced defect through tests and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires this recurring implementation-start failure to move through a work item and governed proposal rather than an untracked repair.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly discovered fleet/bridge/TAFE/harness defects while preserving bridge, claim, implementation-start, verification, commit, and non-bypass gates.
- WI-5382 work item evidence - records the repeated no-packet/no-diagnostic implementation-start symptom and explicitly grants no source, dispatcher, TAFE, Git, or runtime mutation authority by itself.
- Bridge evidence from WI-5230, WI-5287, WI-5299, WI-5316, WI-5318, WI-5354, WI-5355, WI-5359, WI-5360, WI-5364, WI-5365, and WI-5366 - repeated latest-GO attempts that were blocked or dispositioned because implementation start produced no named schema-v3 packet or actionable start state.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded PAUTH carriers and governed proposals for in-scope fleet defects. `PAUTH-DISPATCHER-BLACK-BOX-WI5382-IMPLEMENTATION-START-PACKET-20260716` is active for WI-5382 and permits only bridge, metadata, governance evidence, source, and focused test work after all later bridge and implementation-start gates pass.

## Proposed Scope

- Make `implementation_authorization.py begin` externally reliable at the CLI contract boundary: packet success must print the exact packet JSON, and non-`--no-write` success must write the same schema-v3 packet to the bridge-named cache before updating `current.json`.
- Preserve `--no-write` as a diagnostic mode that prints the computed pre-start packet and writes neither the named cache nor `current.json`.
- Preserve and, if necessary, harden structured failure behavior so every `AuthorizationError` exits nonzero with `{"authorized": false, "error": "<deterministic reason>"}` and creates no packet files.
- Add focused regression tests for successful durable begin, `--no-write`, missing-claim denial, and write-order/side-effect safety. Use temporary roots and fixtures only; do not scan or mutate the live repository packet cache.
- Preserve shared-path conflict detection, PAUTH operation-time validation, target-path bounds, latest bridge status checks, worker-role provenance, and current named-packet fallback semantics.

## Out Of Scope

- Dispatcher or TAFE mutation.
- Runtime worker, lease, dispatch eligibility, or queue mutation.
- Credential lifecycle, external-system mutation, destructive cleanup, git history rewrite, git push, deployment, release, or production action.
- Whole-file adoption of existing foreign hunks in either target.
- Relaxing PAUTH, bridge GO, work-intent claim, target-path, project membership, currentness, or review-independence requirements.
- Marking downstream blocked work items terminal without their own implementation reports and independent verification.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Focused tests in `platform_tests/scripts/test_implementation_authorization.py` covering successful durable `begin`, missing-claim denial, and denied side-effect-free packet state | Success writes/prints schema-v3 packet; denial exits nonzero with JSON and creates no packet files. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Existing and new PAUTH/bridge tests around project authorization metadata and implementation-start load | PAUTH is enforced as a necessary but insufficient boundary; proposal target paths remain the upper bound. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live `bridge_applicability_preflight.py` plus `adr_dcl_clause_preflight.py`; after GO, exact claim and implementation-start packet creation before protected mutation | Proposal and any later report are routed through the numbered bridge chain with no retired aggregate dependency. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry forward this table and exact executed commands/results | Loyal Opposition can verify every linked requirement against executed tests. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --check -- scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` plus hunk attribution in the implementation report | No unrelated or foreign hunks are adopted. |
| Source quality | `ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` and `ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` | No lint or format regressions on the exact targets. |
| Regression preservation | Focused existing implementation-authorization and bridge-work-intent subsets selected by the implementation report | Existing claim, named-packet fallback, validation, currentness, and PAUTH behavior remains green. |

## Acceptance Criteria

- A valid latest-GO bridge thread with an active matching `go_implementation` claim and valid PAUTH produces a finalized schema-v3 packet, writes `.gtkb-state/implementation-authorizations/by-bridge/<slug>.json`, writes `current.json` only after the named packet, and prints the same packet JSON.
- `--no-write` prints a diagnostic pre-start packet and leaves both named and current packet files absent.
- Missing claim, stale PAUTH, invalid target path, bridge-state drift, or shared-path conflict exits nonzero with deterministic JSON denial and leaves no packet state behind.
- Tests prove the CLI behavior through the public `main()` path, not only helper functions.
- The implementation report includes hunk-level attribution for any pre-existing dirty target bytes and does not claim unrelated bridge/program repairs as WI-5382 work.

## Risks / Rollback

Risk is moderate because the implementation-start boundary is shared by many black-box repair threads. The mitigation is to keep the patch at the CLI/packet-contract layer, use temporary-root tests, preserve all existing authorization predicates, and fail closed on any uncertain state.

Rollback is a focused revert of the WI-5382 source and test hunks after normal bridge authorization. Bridge files, PAUTH records, and evidence remain append-only audit history and are not deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight Subsection

Pre-filing candidate checks are run against this exact completed content file before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5382-implementation-start-packet-contract --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5382-implementation-start-packet-contract-001.completed.md --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5382-implementation-start-packet-contract --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5382-implementation-start-packet-contract-001.completed.md`

The live filed proposal must be rechecked after the helper writes `bridge/gtkb-wi5382-implementation-start-packet-contract-001.md`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
