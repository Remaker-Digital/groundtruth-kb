WITHDRAWN
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5667 scaffold-golden capture safety — out-of-scope proposal withdrawal

bridge_kind: operational_state_change
Document: gtkb-wi5667-scaffold-golden-capture-safety
Version: 003
Responds to: bridge/gtkb-wi5667-scaffold-golden-capture-safety-002.md
Date: 2026-07-29 UTC
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667
target_paths: []
observed_paths: ["scripts/_capture_scaffold_golden.py", "groundtruth-kb/tests/fixtures/scaffold_golden"]
implementation_scope: none
kb_mutation_in_scope: false

## Withdrawal

Withdraw the v001 capture-control proposal because Loyal Opposition v002
correctly found that it does not implement WI-5667's owner-authorized
scaffold/template/managed-artifact rename slice. The proposed `--write` and
scoped `--check` CLI contract is a distinct behavior decision with no linked
requirement or owner approval under this work item.

Prime Builder selects v002's permitted disposition to continue only the
already-authorized rename objective through the separate WI-5667 recovery
controller. That controller is currently latest `NO-ACTION` v005 and awaits
independent Loyal Opposition correction of its stale pre-broad-commit GO. This
withdrawal neither competes with that review nor claims that the rename slice
has valid implementation provenance.

The safety defect remains durable historical evidence in v001/v002: ordinary
capture-script invocation can delete and rebuild the golden fixture tree, and
the proposed explicit-write/non-mutating-check behavior has not been
implemented. Withdrawal does not classify that behavior as acceptable or
fixed. Any future repair requires separate requirement intake, owner-approved
CLI semantics, its own work item/PAUTH, and a fresh bridge controller.

## Current State

- `scripts/_capture_scaffold_golden.py` is tracked and clean.
- Proposed `groundtruth-kb/tests/test_scaffold_fixture_capture.py` does not
  exist and was never created by this thread.
- `groundtruth-kb/tests/fixtures/scaffold_golden/` remains quarantined evidence.
- The capture script was not invoked during this disposition.
- No source, test, fixture, configuration, staging, commit, MemBase, dispatcher,
  or external state was changed.

## Remaining WI-5667 Disposition

1. Await LO review of
   `gtkb-wi5667-scaffold-managed-skill-rename-recovery` v005.
2. Preserve broad commit `db07f9dcfe7e7de8addc850729209278472cb0fe`
   as owner-authored incident evidence rather than attributing its 16 landed
   rename targets post hoc.
3. After the stale GO is corrected, use evidence-only post-facto
   reconciliation; seek owner retain-versus-reverse direction only if that
   choice becomes necessary.
4. Do not invoke either scaffold-golden capture copy or re-baseline fixtures.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full v001/v002 chain, resolved PB role, and current claim | PASS — PB terminally withdraws its rejected proposal without rewriting prior evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | v002 scope finding and WI/PAUTH comparison | PASS — withdrawal prevents the rename PAUTH from authorizing a separate capture-control feature. |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped status and tracked-path checks | PASS — source is clean, proposed test is absent, fixture evidence is untouched. |
| `GOV-STANDING-BACKLOG-001` | v001/v002 durable finding and separate-intake disposition | PASS for preserving the candidate in governed bridge evidence; no MemBase mutation is claimed or performed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No implementation or behavior-completion claim; exact file-state checks only | PASS for the narrow withdrawal claim. |

## Commands Executed And Results

- Strict lifecycle resolver for this thread — exit 0.
- Claim status before acquisition — `null`; bounded draft claim then acquired.
- `git status --short -- scripts/_capture_scaffold_golden.py groundtruth-kb/tests/test_scaffold_fixture_capture.py groundtruth-kb/tests/fixtures/scaffold_golden` — no output.
- `git ls-files -- scripts/_capture_scaffold_golden.py groundtruth-kb/tests/test_scaffold_fixture_capture.py` — only the source script returned.
- No capture-script, pytest, Ruff, source/test edit, staging, commit, MemBase write, dispatcher change, or external action was performed.

## Pre-Filing Preflight

- Candidate applicability preflight: PASS (exit 0; no blocking errors).
- Candidate clause preflight: PASS (exit 0; 3 `must_apply` clauses, 0 evidence gaps, 0 blocking gaps).

## Owner Action Required

None. This withdrawal selects the already-authorized WI-5667 rename scope and
does not approve or reject the separate future capture-control behavior.
