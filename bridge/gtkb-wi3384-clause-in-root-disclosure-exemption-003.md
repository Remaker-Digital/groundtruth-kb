NEW

# gtkb-wi3384-clause-in-root-disclosure-exemption - Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi3384-clause-in-root-disclosure-exemption
Version: 003
Author: Prime Builder (Codex, harness A, interactive Prime Builder override)
Date: 2026-06-14 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec750-9b9d-7012-ace0-6bfa08048062
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder session override via ::init gtkb pb

responds_to: bridge/gtkb-wi3384-clause-in-root-disclosure-exemption-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3384

target_paths: ["scripts/adr_dcl_clause_preflight.py", "config/governance/adr-dcl-clauses.toml", "platform_tests/scripts/test_clause_in_root_disclosure_exempt.py"]

implementation_scope: source, config, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

implementation_authorization_packet_hash: sha256:ba98fef83d58fcd57827f62a71f7657a255530a0e8fcbabc8c1b698882e24396

---

## Summary

Implemented the GO'd WI-3384 safe-hybrid fix for the CLAUSE-IN-ROOT detector.

Changes:

1. `scripts/adr_dcl_clause_preflight.py`
   - Added the opt-in `failure_pattern_disclosure_exempt` field to the clause model and loader.
   - Added paired `<!-- in-root-disclosure -->` / `<!-- /in-root-disclosure -->` block stripping for failure-pattern scanning only when the flag is enabled.
   - Re-appends raw `target_paths` metadata lines from the original content before running the failure pattern, preserving enforcement on declared artifact paths.
   - Documented the marker convention in the preflight module docstring.

2. `config/governance/adr-dcl-clauses.toml`
   - Enabled `failure_pattern_disclosure_exempt = true` only for `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.
   - Added an in-scope config comment documenting the marker convention and the target-path scan preservation rule.

3. `platform_tests/scripts/test_clause_in_root_disclosure_exempt.py`
   - Added six focused regression tests covering the marked-disclosure positive case, target-path false-negative guard, unmarked prose guard, unchanged behavior for other clauses, the rehearsal exception, and loader default behavior.

No formal spec, GOV, ADR, DCL, narrative-artifact, schema, deployment, or credential mutation was performed.

## Specification Links

Carried forward from the proposal and GO:

- `GOV-STANDING-BACKLOG-001` - WI-3384 is the backlog authority for this governance-detector defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation proceeded under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the CLAUSE-IN-ROOT detector still enforces in-root artifact declaration, while allowing marked non-artifact disclosure context.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed as the next version in `bridge/INDEX.md`, preserving the append-only bridge trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target-path metadata are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping and executed verification results are below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory context for durable governance-detector refinement.

## Prior Deliberations

Carried forward from the proposal and GO:

- `DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION` - owner authorization for the bridge-protocol reliability clean-fix batch, including WI-3384.
- Cycle-17 owner AskUserQuestion on 2026-06-14 - owner selected the safe-hybrid WI-3384 design.
- WI-4530 reproduction context - the false positive prevented literal non-artifact path disclosure in a valid in-root proposal.

## Owner Decisions / Input

No new owner input is required for this implementation report. The bounded PAUTH, LO `GO` at `-002`, and session-held work-intent claim authorized source/config/test implementation and this post-implementation report.

## Spec-to-Test Mapping

| Specification / acceptance criterion | Evidence |
|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: marked non-artifact disclosure must not refute otherwise in-root evidence | `test_marked_disclosure_mention_not_refuted` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: declared out-of-root artifact paths in `target_paths` must still refute, even if wrapped in a marker | `test_out_of_root_target_paths_still_refutes` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: unmarked out-of-root prose remains conservative and still refutes | `test_unmarked_mention_still_refutes` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: existing rehearsal exception remains preserved | `test_rehearsal_exception_preserved` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation stayed inside authorized source/config/test paths | target paths above; no other WI-3384 implementation files changed |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: bridge metadata, INDEX entry, spec links, target paths, and executed verification evidence are present in this report | this bridge file plus `bridge/INDEX.md`; bridge preflight results to be added after filing |
| Other clauses remain unchanged unless they opt in to the new flag | `test_other_clauses_unchanged` and `test_flag_default_false` |
| Existing clause-preflight behavior remains stable | `platform_tests/scripts/test_adr_dcl_clause_preflight.py` |

## Verification Results

Focused WI-3384 regression:

```text
Command: python -m pytest platform_tests/scripts/test_clause_in_root_disclosure_exempt.py -q --tb=short -o addopts=""
Result: PASS

......                                                                   [100%]
6 passed in 1.23s
```

Existing clause-preflight regression suite:

```text
Command: python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short -o addopts=""
Result: PASS

.....................                                                    [100%]
21 passed in 1.78s
```

Lint gate:

```text
Command: python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_clause_in_root_disclosure_exempt.py
Result: PASS

All checks passed!
```

Format gate:

```text
Command: python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_clause_in_root_disclosure_exempt.py
Result: PASS

2 files already formatted
```

Bridge applicability preflight:

```text
Command: python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3384-clause-in-root-disclosure-exemption
Result: PASS

- content_file: bridge/gtkb-wi3384-clause-in-root-disclosure-exemption-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

Clause preflight:

```text
Command: python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi3384-clause-in-root-disclosure-exemption
Result: PASS

- Bridge id: gtkb-wi3384-clause-in-root-disclosure-exemption
- Operative file: bridge\gtkb-wi3384-clause-in-root-disclosure-exemption-003.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Risk / Rollback

Risk remains low and scoped:

- The new behavior is opt-in and enabled only for CLAUSE-IN-ROOT.
- The primary declaration surface, `target_paths`, is always scanned from the original content.
- Unmarked prose still refutes, preserving conservative default behavior.
- Other clauses continue to scan full content unless they explicitly opt into the flag.

Rollback is straightforward: remove the config flag/comment, the loader field, the failure-pattern scan helper branch, and the focused regression file. No migration or data cleanup is required.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
