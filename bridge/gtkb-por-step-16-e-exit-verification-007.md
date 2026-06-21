REVISED
Responds-to: bridge/gtkb-por-step-16-e-exit-verification-006.md

# gtkb-por-step-16-e-exit-verification — POR Step 16.E Exit Verification Remediation Plan

bridge_kind: prime_proposal
Document: gtkb-por-step-16-e-exit-verification
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-06-20 UTC

author_identity: claude prime-builder
author_harness_id: B
author_session_context_id: 2026-06-20T21-57-59Z-prime-builder-B-024729
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: headless auto-dispatch; ::init gtkb pb

Project Authorization: PAUTH-PROJECT-POR-SPEC-HYGIENE-EXIT-VERIFICATION
Project: PROJECT-POR-SPEC-HYGIENE
Work Item: WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE

target_paths: ["scripts/remediate_por_step_16e.py", "platform_tests/scripts/test_remediate_por_step_16e.py", "scripts/por_step_16_exit_verification.py", "groundtruth.db", "config/governance/por-step-16e-waiver-manifest.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revision addresses the two P1 blockers in the version 006 NO-GO:

- **FINDING-P1-001**: The exact 48-waiver spec set and 2,120-row deletion set lived only in
  gitignored local files (`.groundtruth/remediation-manifest.json`,
  `scratch/found_test_mappings.json`). The durable audit trail could not be reconstructed
  from a clean checkout.
- **FINDING-P1-002**: The proposed exit verifier read its waiver source from the same gitignored
  `.groundtruth/` path, making the release-readiness gate environment-dependent.

**Fix**: Promote the exact owner-approved manifest to a tracked governed artifact at
`config/governance/por-step-16e-waiver-manifest.json`. Update both the remediation script and
the exit verifier to read from this tracked path. Bind the implementation to the manifest's
exact content hash so LO verification can confirm no substitution occurred.

The remediation plan is otherwise unchanged from version 005: adopt 69 tests, retire 2,120
tests, link 36 specifications, and apply the 48-spec waiver. All prior positive confirmations
from version 006 (owner decision cited, row-by-row manifest path included, clean preflights)
are preserved.

## Approved Manifest — Exact Content Commitment

The owner-approved manifest is the file currently at `.groundtruth/remediation-manifest.json`
as of 2026-06-20. Its content hash is:

```
sha256:8c1933322fe408599b61355a5d7441b834965007a62c78b49f4da59f0b6655fc
```

The implementation MUST commit `config/governance/por-step-16e-waiver-manifest.json` with
content byte-identical to this hash. The implementation report must include the hash of the
committed file. Verification must confirm byte-identical match; a hash mismatch is a NO-GO.

**Approved waived spec IDs (48 items, embedded for audit durability):**

```json
[
  "ADR-008",
  "ADR-REGISTRY-DISCOVERY-001",
  "ADR-STANDING-BACKLOG-DB-AUTHORITY-001",
  "DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001",
  "DCL-STANDING-BACKLOG-DB-SCHEMA-001",
  "GOV-14",
  "GOV-16",
  "GOV-CD-PRESERVATION",
  "PB-DARK-MODE",
  "SPEC-1653",
  "SPEC-1707",
  "SPEC-1708",
  "SPEC-1709",
  "SPEC-1710",
  "SPEC-1711",
  "SPEC-1712",
  "SPEC-1775",
  "SPEC-1776",
  "SPEC-1777",
  "SPEC-1778",
  "SPEC-1816",
  "SPEC-1818",
  "SPEC-1819",
  "SPEC-1820",
  "SPEC-1821",
  "SPEC-1822",
  "SPEC-1823",
  "SPEC-1824",
  "SPEC-1825",
  "SPEC-1826",
  "SPEC-1827",
  "SPEC-1841",
  "SPEC-1861",
  "SPEC-1862",
  "SPEC-1863",
  "SPEC-1864",
  "SPEC-1865",
  "SPEC-1866",
  "SPEC-1867",
  "SPEC-1868",
  "SPEC-1872",
  "SPEC-1875",
  "SPEC-1878",
  "SPEC-1879",
  "SPEC-1880",
  "SPEC-1881",
  "SPEC-CD-HANDOFF-FORMAT-001",
  "SPEC-GTKB-SCOPE"
]
```

Approved counts: adopt=69, retire=2120, waived_specs=48.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The bridge protocol and CLI command execution.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification linkage requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Bounded metadata headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification requires tests derived from linked specs; owner waivers must be durable and reviewable.
- `GOV-STANDING-BACKLOG-001` — Backlog management.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Release readiness; the exit verifier is a release gate and must be deterministic from a clean checkout.
- `GOV-ARTIFACT-APPROVAL-001` — Bulk-mutation governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — The in-root application placement isolation boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Modeling project memory as a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Artifact lifecycle triggers, thresholds, and states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Artifact-oriented governance as the default project interpretation stance.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — State claims derive from fresh canonical reads; the waiver source must be tracked, not workstation-local.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` — Batch-5 authorization including this WI.
- `DELIB-0822` — POR 16.D Phase 1 complete, which corrected the 2,322-test empty-spec orphan baseline.
- `DELIB-0823` — POR 16.D Phase 2 complete, which classified the 2,189 orphan baseline into Class B (1,703), C (481), and D (5).
- `DELIB-2313` — POR 16.D Phase 2 verification.
- `DELIB-20265448` — Version 002 NO-GO review.
- `DELIB-20265451` — Version 004 NO-GO review.
- `DELIB-20265456` — Owner waiver and bulk test deletion approval deliberation (approves 48 waivers + 2,120 row bulk deletion). This deliberation is the authority basis for the waived spec IDs embedded above.

## Owner Decisions / Input

- `DELIB-20265456` — Owner approved: (1) waiving spec-derived test coverage requirements for the
  48 specifications listed in the waived_specs section of the manifest; (2) bulk deletion of
  the 2,120 stale legacy test rows. The exact waived spec IDs and approved counts are now
  embedded in this proposal (see § Approved Manifest above) so the owner decision is auditable
  from the bridge thread alone, without reference to gitignored local files.

## Requirement Sufficiency

Existing requirements sufficient — The work item details specify the exit criteria for Step
16.E: untested-spec count <= 6 and orphan-test count <= 100. The owner waiver in
`DELIB-20265456` provides the additional authority for the 48-spec exemption and bulk deletion.

## Findings Addressed

### FINDING-P1-001 — Waiver and deletion authority depends on ignored local artifacts

The proposal now promotes the manifest to `config/governance/por-step-16e-waiver-manifest.json`
(a tracked, non-ignored path). The exact 48-waiver spec IDs are also embedded inline in this
proposal under § Approved Manifest so the audit trail is self-contained in the bridge thread.
The content hash `sha256:8c1933322fe408599b61355a5d7441b834965007a62c78b49f4da59f0b6655fc`
binds the implementation to the owner-approved exact bit-for-bit manifest. The implementation
report must confirm hash parity; a mismatch is a NO-GO trigger.

`DELIB-20265456` is now cited not only as a deliberation ID but with its exact scope (48
waived spec IDs + 2,120-row bulk deletion) embedded in this bridge artifact so the decision
content is reviewable without inspecting the MemBase row.

### FINDING-P1-002 — The revised exit verifier would depend on a gitignored `.groundtruth` file

`scripts/por_step_16_exit_verification.py` will be updated to load waived spec IDs from
`config/governance/por-step-16e-waiver-manifest.json` (tracked) instead of
`.groundtruth/remediation-manifest.json` (gitignored). The updated function will:

1. Accept `--waiver-manifest` CLI argument defaulting to the tracked `config/governance/` path.
2. Fail closed (exit 2, non-zero) if the manifest file is absent or contains malformed JSON.
3. Exclude waived spec IDs from the `count_implemented_or_verified_specs_without_tests` SQL
   query result so the untested-spec gate reflects the owner-approved waiver set.
4. Report the waiver manifest path and waived count in both JSON and text output.

`scripts/remediate_por_step_16e.py` will similarly accept a `--manifest` argument defaulting
to `config/governance/por-step-16e-waiver-manifest.json` and will fail closed if the file is
absent or its content hash does not match the approved sha256.

The `.groundtruth/remediation-manifest.json` local artifact may still be generated as a
workstation working artifact but is NOT an input to any tracked script or test.

## Scope Changes

- **Added** `config/governance/por-step-16e-waiver-manifest.json` to `target_paths` (tracked,
  non-ignored governed artifact; promoted from the gitignored local file).
- **Removed** `.groundtruth/remediation-manifest.json` from `target_paths` (gitignored; no
  longer a canonical input to any tracked script).
- **Updated** `scripts/por_step_16_exit_verification.py` now reads waivers from the tracked
  config path with fail-closed behavior for missing/malformed manifests.
- **Updated** `scripts/remediate_por_step_16e.py` now reads from the tracked config path and
  verifies content hash against the approved sha256.
- All other implementation scope from version 005 is unchanged.

## Implementation Sequence

1. **Write tracked manifest** — Copy `.groundtruth/remediation-manifest.json` to
   `config/governance/por-step-16e-waiver-manifest.json`. Compute sha256 and confirm it
   matches `8c1933322fe408599b61355a5d7441b834965007a62c78b49f4da59f0b6655fc`. Include the
   computed hash in the implementation report.

2. **Implement `scripts/remediate_por_step_16e.py`** — Manifest-driven adopt/retire/link
   script. Reads from tracked manifest path. Verifies content hash on startup. Dry-run mode
   performs no mutations. Captures SQLite backup before any write. Fails closed on hash
   mismatch or unmapped orphan.

3. **Update `scripts/por_step_16_exit_verification.py`** — Add waiver manifest loading with
   fail-closed behavior (exit 2 on missing file, exit 2 on malformed JSON). Exclude waived
   spec IDs from untested-spec count. Add `--waiver-manifest` CLI argument with tracked path
   as default.

4. **Run remediation dry-run** — Confirm 69 adopt + 2,120 retire + 36 link planned.

5. **Execute remediation** — Apply mutations to `groundtruth.db` against the backed-up DB.

6. **Verify exit gate** — Run `groundtruth-kb/.venv/Scripts/python.exe scripts/por_step_16_exit_verification.py --json` and confirm `passed: true`.

7. **Implement `platform_tests/scripts/test_remediate_por_step_16e.py`** — Tests covering all
   spec-derived verification plan items plus the three new coverage items (§ Spec-Derived
   Verification Plan).

8. **Run full test suite** on changed scripts.

## Spec-Derived Verification Plan

| Behavior | Test | Maps to |
|---|---|---|
| Dry-run mode performs no writes | `test_remediate_dry_run_does_not_mutate` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| Remediation script adopts 69, retires 2,120, and links 36 specs | `test_remediate_apply_lifecycle` | `GOV-ARTIFACT-APPROVAL-001` / `DELIB-20265456` |
| Boundary check fails closed on out-of-manifest orphan tests | `test_remediate_fails_on_unmapped_orphans` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |
| Exit verification CLI exits 0 post-remediation | `groundtruth-kb/.venv/Scripts/python.exe scripts/por_step_16_exit_verification.py` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |
| Exit verifier fails closed (exit 2) when waiver manifest absent | `test_exit_verifier_fails_closed_on_missing_manifest` | `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / FINDING-P1-002 |
| Exit verifier fails closed (exit 2) when manifest contains malformed JSON | `test_exit_verifier_fails_closed_on_malformed_manifest` | FINDING-P1-002 |
| Exit verifier excludes waived specs from untested-spec count | `test_exit_verifier_waived_specs_excluded` | `DELIB-20265456` |
| Remediation script fails closed on manifest content-hash mismatch | `test_remediate_fails_on_hash_mismatch` | FINDING-P1-001 |
| Committed manifest sha256 matches approved hash | Verify in implementation report via `sha256sum config/governance/por-step-16e-waiver-manifest.json` | FINDING-P1-001 |

## Pre-Filing Preflight Subsection

Applicability and clause preflights are run below after this proposal is saved
as the draft content, then the results are included in the filed version.
The clean preflight state from version 005 must be preserved; a regressionin
either preflight is a sign the proposal revision introduced a structural defect.

## Risk / Rollback

- **Risk**: Mutation of 2,120 test records in `groundtruth.db` could dirty test-audit history.
  **Mitigation**: SQLite backup captured as `groundtruth.db.pre-remediate.bak` before mutation.
  **Rollback**: Restore `groundtruth.db` from backup.
- **Risk**: Content-hash mismatch between the committed tracked manifest and the approved hash
  could indicate a substitution.
  **Mitigation**: The remediation script verifies the hash on startup; a mismatch aborts
  before any mutation.
- **Risk**: New fail-closed manifest checks in the exit verifier break CI runs on clean
  checkouts that lack the tracked manifest.
  **Mitigation**: The tracked manifest is committed under `config/governance/` so it is
  present on any clone. The only failure mode is intentional deletion of the committed file,
  which would be a governance-level defect correctly surfaced as an exit failure.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
