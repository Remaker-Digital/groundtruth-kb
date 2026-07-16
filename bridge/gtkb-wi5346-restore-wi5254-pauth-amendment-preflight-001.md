NEW

# Restore the WI-5254 structured PAUTH amendment preflight

bridge_kind: prime_proposal
Document: gtkb-wi5346-restore-wi5254-pauth-amendment-preflight
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T18:55:41Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5346

target_paths: ["scripts/implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore the independently specified WI-5254 fail-closed preflight in
`scripts/implementation_authorization.py`. The current worktree retains nine
executable tests for the feature, but the implementation entry point
`validate_structured_pauth_spec_amendment` and its authorization-packet
backstop are absent. The exact current regression is nine failures: eight
`AttributeError` failures and one missing `AuthorizationError` from
`create_authorization_packet`.

The implementation will parse exactly one structured replacement PAUTH JSON
envelope, validate authorization/project identity and list fields, compare its
included/excluded specification sets with the current PAUTH, and allow a
no-delta envelope without synthetic owner evidence. A real specification delta
must cite an in-root formal-artifact approval packet that parses, passes the
shared approval-packet schema, is owner-approved, and covers the exact
authorization/project/spec delta. `create_authorization_packet` will invoke the
same validator before an implementation claim can be consumed. No test or
database mutation is needed. Concurrent WI-5178 operation-time enforcement in
the shared script must be preserved byte-for-byte outside this bounded hunk.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` — requires every active-project PAUTH specification-set amendment to fail closed without a covering owner approval packet; explicitly names `scripts/implementation_authorization.py` as an enforcement surface.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires the implementation-start packet to prove the operative project authority before protected mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO, matching work-intent claim, implementation-start authority, and independent VERIFIED for this protected source repair.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to carry the complete governing specification set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5346 to the active Authority Foundations project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the post-implementation report to execute and map the nine existing amendment tests.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — requires the repair to preserve concurrent WI-5178 changes in the same source file.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — forbids restoring the preflight by weakening other authority, bridge, or operation-time checks.
- `GOV-STANDING-BACKLOG-001` — WI-5346 is the durable hygiene record for the false-closure regression discovered during RC acceptance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires every live implementation and verification dependency to remain within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — requires the discovered implementation loss, repair proposal, tests, and verification evidence to remain linked as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — distinguishes the earlier WI-5254 VERIFIED lifecycle event from WI-5346's newly discovered repair lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the RC finding to be preserved as WI-5346 and resolved through the governed implementation path.

## Prior Deliberations

- `DELIB-202666274` — authorizes all required Authority Foundations modernization repairs at project scope while retaining independent GO, claim/start, VERIFIED, and mechanical-operation gates.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — explains why WI-5254 was mechanically retired after VERIFIED; WI-5346 repairs the concrete implementation loss without weakening that parent-retirement decision.

## Owner Decisions / Input

`DELIB-202666274` records the owner's explicit project-level authorization for
all work required to complete the modernization program. The active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
covers source work for WI-5346 and includes the amendment-approval DCL. No new
owner decision is required. This proposal does not request staging, commit,
push, release, deployment, dispatcher/TAFE mutation, harness mutation,
credential lifecycle, or destructive cleanup.

## Requirement Sufficiency

Existing requirements sufficient. The required behavior is completely defined
by `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`, the shared
approval-packet contract, and the nine existing executable tests. No new or
revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -k "structured_pauth_amendment or backstops_structured_pauth_amendment" -q --tb=short` | All 9 selected tests pass, including no-delta, exact owner coverage, malformed/ambiguous envelope, identity, unreadable packet, and creation-time backstop cases. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Same nine-test command plus `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -k structured_pauth_amendment -q --tb=short` | Packet creation and proposal preflight both fail closed before implementation for missing or invalid owner evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory applicability and clause preflights for this document plus the post-implementation report's exact command/output mapping | No missing required specifications or blocking clause gaps; every cited spec is mapped to observed evidence. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py` and a hunk-level diff review against the pre-start hash | Ruff passes; only the WI-5346 validator/import/call-site hunk changes; concurrent WI-5178 code remains intact. |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5346 --json` | The durable hygiene item remains linked to this repair and later receives exact VERIFIED/finalization evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and an implementation-report path inventory | `CLAUSE-IN-ROOT` passes and every dependency/evidence path resolves under `E:\GT-KB`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5346 record, numbered proposal/report/verdict chain, and final exact-scope evidence | The distinct repair lifecycle is traceable without rewriting WI-5254's historical VERIFIED event. |

## Risk / Rollback

The file is shared with active WI-5178 operation-time enforcement, so a
whole-file replacement would be unsafe. Implementation must record the
pre-start SHA-256, add only the validator/import/call-site hunk, and review the
resulting diff for foreign-hunk preservation. The validator must use the shared
formal-approval parser/schema/coverage functions rather than inventing a second
packet contract. Rollback is the exact WI-5346 hunk only; no database or test
artifact requires reversal.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5346-restore-wi5254-pauth-amendment-preflight`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores required fail-closed behavior whose tests and governing DCL
already exist.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
