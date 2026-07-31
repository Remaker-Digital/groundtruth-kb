GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# LO Review — WI-5688 doctor crash fast-lane revision

bridge_kind: lo_verdict
Document: gtkb-wi5688-doctor-crash-fastlane
Version: 004
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5688-doctor-crash-fastlane-003.md
Reviewed proposal: bridge/gtkb-wi5688-doctor-crash-fastlane-003.md

## Verdict Summary

**GO.** Revision 003 resolves the v002 false-PASS blocker without widening the
two-file fast-lane scope. It corrects decoding at the `git grep` subprocess
boundary, retains the exit-code contract, and requires a visible warning rather
than sweep-complete PASS when exit-zero output is absent or unusable.

## Evidence Reviewed

The current implementation calls `subprocess.run(..., capture_output=True,
text=True)` at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2576-2581`
and unconditionally calls `completed.stdout.splitlines()` at `:2603`. That is
consistent with the reproduced Windows decode failure and crash. The proposed
bytes capture plus explicit UTF-8 decode (replacement policy) preserves matched
paths for the WI-5668 warning contract; the defensive no-usable-output branch
must return `warning`, never the PASS at `:2627-2632`.

The current four-test focused baseline passed; Ruff check and format check
passed; scoped `git diff --check` was clean. The standing Reliability Fixes
PAUTH is active for source and test-addition, and `DELIB-202667528` supplies
durable owner evidence for the fast-lane route. The current author session
`de7aad12-9b24-41c8-849c-de48e349ff62` is readable and distinct from this LO
session `019fac54-c55c-75c0-8332-d7fdaf03b20a`.

## Conditions of Approval

1. Change only `doctor.py` and the named sweep test module. Do not absorb the
   sibling `session_self_initialization.py` decode class; it is tracked as
   WI-5740.
2. Preserve exit-code semantics: 0 means matches, 1 means no matches, and
   greater than 1 remains a visible unavailable/error path.
3. Add and execute the Unicode-match warning, exit-0 missing-output non-PASS,
   and zero-match PASS regressions, retaining the existing ASCII fixtures.
   Report the live doctor result with a warning while references remain.
4. No DCL, dispatcher, runtime, configuration, bridge, or broader subprocess
   policy mutation is approved by this GO.

## Deliberation Search

- `DELIB-202667528` supersedes the earlier routing decision only and records
  owner confirmation for this fast-lane route.
- `DELIB-202667193` and `DELIB-20260724-WI5668-SEVERITY-CONTRACT` require the
  doctor gate to warn while pre-rename references remain; they preclude the
  v001 empty-output false PASS.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` supplies the standing
  reliability authorization without waiving the bridge, start, report, or
  independent-verification gates.

## Applicability Preflight

- packet_hash: `sha256:007de65bfe3045b2c8c30754279b61f7bfd9eb2d8fec8b15b14a3a11ca036e43`
- bridge_document_name: `gtkb-wi5688-doctor-crash-fastlane`
- content_file: `bridge/gtkb-wi5688-doctor-crash-fastlane-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:f61c37a8387ac6d2f0e4c39a188571a1c7ea2c8f02c50b39d81719c85eaf06a7`

## Clause Applicability (mandatory)

- Operative file: `bridge/gtkb-wi5688-doctor-crash-fastlane-003.md`
- Clauses evaluated: 5; must_apply: 4; may_apply: 1; evidence gaps: 0;
  blocking gaps: 0; exit: 0.
- Must-apply clauses passed: `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`,
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
  and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Owner Action

None. Prime Builder may proceed only via the normal exact claim and
implementation-start gates.
