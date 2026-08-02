REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5414-artifact-lifecycle-package-finalization-repair
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5414-artifact-lifecycle-package-finalization-repair-004.md

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5414
target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py"]
implementation_scope: current_committed_provenance_reconciliation_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5414 Revised Proposal — Current Committed Artifact-Lifecycle Provenance

## Revision Claim

Prime Builder accepts NO-GO-004's finding that version 003 could not close the
approved work through a carrier-only `NO-ACTION`. The original exact-untracked-
byte premise is now obsolete, however: both package files are tracked and clean
in current HEAD. This revision replaces the stale finalization instruction with
a no-byte current-provenance reconciliation and independent verification lane.

No source or test change is proposed. The historical version-001 hash for
`decontamination.py` is not current and must not be restored over legitimate
later committed evolution. `__init__.py` still has the approved historical
hash. A later report, after fresh independent GO plus exact claim/start, must
re-observe current hashes and verification without editing either path.

## Current Authorization And Dependencies

WI-5414 is open and an active member of active
`PROJECT-GTKB-TREE-STABILIZATION`. Its active list-free project PAUTH covers the
member WI despite the legacy `approval_state: unapproved` field, under the
owner's project-inheritance rule. WI-5415 and WI-5457 are terminal VERIFIED;
the original dependency hold is cleared.

## Exact Current Target Evidence

Path-scoped Git status is empty for both targets at HEAD
`75decbfa704fe50288aecbc5669def329a0825df`.

| Target | Current SHA-256 | Last-path commit | Disposition |
|---|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py` | `0F34D3C7E96426423BBA303A4C9FAAF4028444D221F39521D4A9CCE01C192A5C` | `f9731c41f5a3898fc86a3bffbc7c25f771c32f28` | Clean committed postimage; version-001 hash `A5AC...DB3` is historical and must not be restored |
| `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py` | `BBEFD5CD37787094DFF954B01300447CEF171206CF0A776CE8EF72CFBCBA2A2D` | `9373c523164ecfa8a2acadfe4c6e7fd1dcb008ee` | Clean committed postimage; still matches the approved historical carrier hash |

The exact-byte reconciliation is therefore asymmetric by design: preserve both
current clean postimages, record provenance, and do not force either path back
to a historical byte identity.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- Versions 001 and 002 record the original exact-byte proposal and independent
  GO when both files were untracked carriers.
- Version 004 rejects the incomplete version-003 closure and requires a
  substantive revision or implementation evidence.
- WI-5415 terminal commit `9b83849e63a102c94649e36fe3f5ae08d2e90fbf`
  and WI-5457 terminal commit `0bfc2d3b` clear the original dependencies.
- The owner's 2026-08-01 project-inheritance direction confirms that active
  project PAUTH, not the legacy per-WI approval field, is controlling.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` requires timer
  and concurrency policy to remain centralized and evidence-tuned.

## Owner Decisions / Input

No new owner decision is required. This revision remains inside the active
Tree Stabilization project and its inherited PAUTH. It does not authorize
source edits, dispatcher/TAFE action, credentials, destructive cleanup, Git
finalization, deployment, or release.

## Requirement Sufficiency

Existing requirements are sufficient. The remaining work is evidence and
lifecycle reconciliation, not a new artifact-lifecycle behavior. The exact
current bytes, terminal dependencies, 25-test package lane, static checks, and
independent review fully determine acceptance.

## Revised Scope

1. Preserve both current committed target postimages without semantic or byte
   edits.
2. Treat the version-001 hashes as historical provenance, not current restore
   instructions. Explicitly retain the current `decontamination.py` drift and
   the still-matching `__init__.py` identity.
3. After independent GO, acquire a fresh exact claim and schema-v3 start packet
   only to bind the two-path evidence transaction; do not mutate the targets.
4. File a factual no-byte implementation report with fresh hashes, Git status,
   dependency readback, 25-test results, Ruff, format, compile, diff, candidate
   and live preflights.
5. Keep `gates.py`, registry discovery, checker/test code, other package files,
   bridge runtime, dispatcher, TAFE, harness configuration, database, Git
   finalization, and unrelated worktree state outside the target set.

## Specification-Derived Verification Plan

| Obligation | Required evidence |
|---|---|
| Package residue and dynamic import contract | Run `test_modernization_artifact_decontamination.py` plus `test_doctor_registry_dynamic_import_contract.py` with the centralized diagnostic timeout override; require 25/25 pass. |
| Current provenance | Exact two-path status, SHA-256, HEAD blobs, last-path commits, and historical-hash disposition. |
| Evaluability and hygiene | Ruff check, Ruff format check, `py_compile`, and `git diff --check` on the exact package/test lane. |
| Project authority | Active project membership and operation-time PAUTH allow results for the exact two targets. |
| Bridge governance | Candidate/live applicability, mandatory clause gate, exact claim/start, factual report, and independent VERIFIED. |
| Nonimpairment | Zero target-byte delta; no package restore, registry behavior change, dispatcher/TAFE state change, or unrelated scope adoption. |

The focused lane already completed under delegated Prime audit with `25 passed,
1 warning in 108.27s` when the diagnostic outer pytest bound was raised from the
repository's unhealthy 30-second default to 600 seconds. The default timer had
killed healthy subprocess-reader work. Existing WI-5873 owns that centralized
timer correction; this proposal creates no duplicate WI or local timer literal.

## Acceptance Criteria

1. Both targets remain tracked, clean, unstaged, and byte-unchanged throughout
   the reconciliation.
2. Current hashes and last-path commits are recorded; historical exact-byte
   values are not misrepresented as current authority.
3. The combined package lane passes all 25 tests under the centralized
   diagnostic bound; Ruff, format, compile, and diff checks pass.
4. WI-5415 and WI-5457 remain terminal and no unrelated dependency is absorbed.
5. The report contains exact current project/PAUTH, claim/start, target,
   applicability, and clause evidence.
6. No source/test semantic edit, historical-byte restore, dispatcher, TAFE,
   harness, credential, destructive, Git-finalization, deployment, release, or
   external-system mutation occurs.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5414 versions 001-004, current clean HEAD identities, terminal WI-5415/WI-5457 dependencies, and delegated 25-test evidence",
  "canonical_authority": "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; active Tree Stabilization PAUTH",
  "primary_route": "independent review, exact evidence-bound claim/start, no-byte report, independent verification",
  "before_behavior": "The chain still describes two untracked exact-byte carriers even though both files are now tracked and one has legitimate later committed evolution.",
  "after_behavior": "The chain preserves current committed bytes, records exact provenance and historical-hash disposition, and completes through independently verified no-byte reconciliation.",
  "self_descriptive_naming": "The artifact-lifecycle package finalization-repair thread and exact two-path evidence table identify the residue and current disposition directly.",
  "obsolete_guidance_disposition": "The version-001 instruction to preserve the old decontamination.py hash is superseded; it remains immutable historical evidence and is not executed.",
  "history_preservation": "Versions 001-004, dependency commits, historical hashes, current postimages, and later evolution remain distinct and append-only.",
  "baseline": {"head": "75decbfa704fe50288aecbc5669def329a0825df", "targets": 2, "target_state": "tracked and clean", "focused_tests": 25},
  "expected_result": {"target_byte_changes": 0, "focused_tests_passed": 25, "historical_restore": false, "independent_verification": true},
  "rollback": {"instructions": "No implementation rollback; supersede any incorrect evidence append-only in the next numbered artifact.", "verification": "Recheck current hashes, clean status, dependency terminals, and 25-test lane."},
  "hard_invariants": ["no target-byte change", "no historical hash restore", "no unrelated package path", "no dispatcher or TAFE mutation", "no Git finalization"],
  "fail_closed_conditions": ["target or authority drift", "test/static failure", "missing claim/start", "attempted restore or unrelated edit", "missing independent review"],
  "essential_context_preservation": "Preserve original exact-byte intent, current committed provenance, asymmetric hash disposition, terminal dependencies, timer evidence ownership, and no-byte lifecycle route."
}
```

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: required; zero missing required/advisory
  specifications and zero blocking errors.
- Mandatory ADR/DCL clause preflight: required; zero blocking must-apply gaps.
- Exact two target paths are clean; no protected target mutation is performed
  by proposal filing.

## Risk And Rollback

The main risk is overwriting legitimate later code to recreate historical
carrier bytes. The revised scope prohibits that operation and binds acceptance
to zero target-byte changes. Rollback is append-only evidence correction, not a
source restore. No timer or concurrency literal is introduced.

## Files Expected To Change

None during implementation reconciliation. The two declared paths are evidence
subjects and must remain byte-identical.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
