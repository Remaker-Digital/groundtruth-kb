REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5316
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder worker; user-directed PB bridge auto-process

# Revised Implementation Proposal - Adopt Formatted Frozen Modernization RC Contract

bridge_kind: prime_proposal
Document: gtkb-wi5316-frozen-modernization-rc-contract
Version: 005
Responds to: bridge/gtkb-wi5316-frozen-modernization-rc-contract-004.md
Revises: bridge/gtkb-wi5316-frozen-modernization-rc-contract-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5316
target_paths: ["config/governance/modernization-release-candidate.json", "scripts/check_modernization_release_candidate.py", "platform_tests/scripts/test_modernization_release_candidate.py"]

## Revision Claim

Resolve the exact-byte/format-gate contradiction by adopting the same frozen
release-candidate behavior while explicitly authorizing Ruff formatting of only
`scripts/check_modernization_release_candidate.py` after a fresh GO, matching
claim, and successful implementation-start packet. Preserve the manifest and
focused test bytes exactly. Bind the eventual report to the three post-format
hashes below and rerun every required check on those exact bytes.

This revision changes no candidate byte. The checker post-format digest was
computed read-only by passing its current bytes to Ruff over stdin. The
authorized implementation must perform the actual one-file formatting only
after operation-time authorization, then prove the resulting bytes match the
reviewed expected digest.

## Requirement Sufficiency

Existing requirements and project authorization are sufficient. Ruff formatting
is a mechanical, semantic-preserving source mutation inside the original
three-target envelope. No format waiver or new owner decision is requested.

## In-Root Placement Evidence

All three targets and all scratch/evidence paths remain inside `E:\GT-KB`. No
application, external, credential, deployment, release, or cleanup path is in
scope.

## Specification Links

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - modernization Gate 0 scope inventory.
- `DELIB-202666274` - owner authorization for required modernization blocker work while preserving review and mechanical gates.
- `DELIB-202666288` - exact-HEAD and historical evidence remain distinct.
- `bridge/gtkb-wi5316-frozen-modernization-rc-contract-003.md` - Prime rejection of the contradictory GO.
- `bridge/gtkb-wi5316-frozen-modernization-rc-contract-004.md` - corrected independent NO-GO requiring this revision.

## Owner Decisions / Input

- The active Assurance project PAUTH covers WI-5316 and the original three
  targets; operation-time enforcement remains mandatory.
- No new owner decision is required for the preferred formatting path.
- No owner waiver is requested, inferred, or used.

## Findings Addressed

### Exact-byte preservation versus mandatory format verification

Accepted. The revised contract no longer requires the pre-format checker digest
`E2D40360CD389FD3356F046A519C8324518A92061EB5AF530E8BA6C57E95ACFB` to
remain unchanged. It authorizes exactly one mechanical formatting mutation and
replaces that digest with the read-only post-format baseline below.

The manifest and test remain byte-preserved. The manifest's canonical frozen
scope digest `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`
is derived from manifest scope content, not checker formatting, and therefore
remains unchanged.

## Post-Format Candidate Baseline

| Path | Required SHA-256 after authorized formatting |
| --- | --- |
| `config/governance/modernization-release-candidate.json` | `203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D` |
| `scripts/check_modernization_release_candidate.py` | `40B64AE08FD3F278C62AB5A376D9420D061C98CF54592D7A946619D896E3A193` |
| `platform_tests/scripts/test_modernization_release_candidate.py` | `1B07D2130E40E5B88EC8CCDDF828FCACC37E8ED4A1490D83BB0680B630D5CA48` |

Read-only derivation evidence for the checker: current 80,286-byte input at
`E2D40360...ACFB` was passed to repository Ruff 0.15.20 using
`ruff format --stdin-filename scripts/check_modernization_release_candidate.py -`;
the 80,208-byte stdout is `40B64AE0...A193`. No target was written.

## Scope Changes

1. Preserve exact bytes of the manifest and focused test.
2. After GO/claim/start, run Ruff format only on the checker.
3. Require the resulting three hashes to match the table above.
4. Keep the eight-capability, ninety-four-handle manifest population and frozen
   scope digest unchanged.
5. Preserve the prohibition on `run-clean`, `attest-run`, `record-audit`,
   semantic evidence issuance, activation, Git finalization, deployment, and
   release evidence.

## Implementation Plan After GO

1. Acquire a fresh exact claim and successful implementation-start packet for
   this version and the three target paths.
2. Reconfirm the three pre-start candidate hashes and tracking state.
3. Run `ruff format scripts/check_modernization_release_candidate.py` only.
4. Recompute all three SHA-256 values and require the post-format baseline.
5. Run manifest validation, the exact focused suite, Ruff lint, Ruff format
   check, and whitespace verification.
6. File a hash-bound implementation report without collecting or relabeling any
   runtime, clean-run, attestation, audit, release, or deployment evidence.

## Pre-Filing Preflight Subsection

- Candidate applicability and mandatory clause preflights must pass against the
  completed version-005 bytes before filing.
- The governed revision helper must pass credential, concurrency, project
  linkage, author provenance, and bridge-compliance gates before creating the
  live numbered file.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5316; TEST-11459; version-004 NO-GO; formatted frozen modernization acceptance contract",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_release_candidate.py",
  "before_behavior": "The eight-capability ninety-four-handle contract exists as three untracked candidates, but the checker fails the mandatory Ruff format check.",
  "after_behavior": "The manifest and test remain byte-identical while the checker receives one authorized mechanical Ruff formatting pass and all three resulting bytes are hash-bound and independently reviewed.",
  "self_descriptive_naming": "The manifest, check_modernization_release_candidate service, and test_modernization_release_candidate carrier name their contract and lifecycle directly.",
  "obsolete_guidance_disposition": "Version-001 exact preservation of the pre-format checker hash is superseded by this post-format hash contract; no runtime or operator route is replaced.",
  "history_preservation": "The pre-format digest, post-format digest, frozen scope digest, tests, append-only bridge chain, and later runtime evidence remain separately queryable.",
  "baseline": {
    "tracking_state": "three files untracked",
    "capabilities": 8,
    "handles": 94,
    "focused_tests": 46,
    "checker_pre_format_sha256": "E2D40360CD389FD3356F046A519C8324518A92061EB5AF530E8BA6C57E95ACFB"
  },
  "expected_result": {
    "manifest_sha256": "203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D",
    "checker_post_format_sha256": "40B64AE08FD3F278C62AB5A376D9420D061C98CF54592D7A946619D896E3A193",
    "test_sha256": "1B07D2130E40E5B88EC8CCDDF828FCACC37E8ED4A1490D83BB0680B630D5CA48",
    "frozen_scope_digest_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240",
    "capabilities": 8,
    "handles": 94,
    "focused_tests_passed": 46,
    "runtime_evidence_writes": 0
  },
  "rollback": {
    "instructions": "Restore only the checker pre-format bytes before separately authorized finalization; do not delete append-only governance evidence.",
    "test": "Recompute all three hashes, validate the manifest, and rerun the focused 46-test suite plus Ruff gates."
  },
  "hard_invariants": [
    "The frozen scope digest and ninety-four-handle population do not change.",
    "Readiness still requires separately governed current clean runs, independent attestations, and audit evidence.",
    "Only the checker receives formatting; manifest and test bytes remain unchanged.",
    "Adoption does not run collectors or issue runtime, attestation, audit, release, or deployment evidence.",
    "No Git, database, dispatcher, harness, credential, deployment, or release state is mutated."
  ],
  "fail_closed_conditions": [
    "Any post-format candidate hash or frozen scope digest differs.",
    "Manifest validation, focused tests, Ruff lint, Ruff format verification, or whitespace verification fails.",
    "Any undeclared path or runtime evidence artifact changes.",
    "Any claim, start packet, or independent review session is missing or invalid."
  ],
  "essential_context_preservation": "The contract keeps scope, exact pre/post formatting identity, Git binding, actor authority, runtime reports, attestations, audit, residual findings, and release decision as distinct evidence."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Run checker `validate`; do not run clean-run/attestation/audit modes; prove readiness remains fail-closed without those separately governed artifacts. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Validation reports exactly 8 capabilities and 94 uniquely bound handles. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Only the checker receives mechanical formatting; no runtime evidence or live operational state changes. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Focused tests retain stale/mismatched HEAD and tree rejection coverage; no Git operation occurs in this slice. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Recompute and compare the exact three post-format hashes and unchanged frozen scope digest. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All 46 focused tests, Ruff check, Ruff format check, and `git diff --check` pass on the exact candidate. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation follows fresh independent GO, claim, start packet, report, and independent verdict. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Start packet authorizes the one checker mutation and exact target envelope before formatting. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Resolve WI-5316, active Assurance PAUTH, project, and exact three targets. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights have zero blocking gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All targets and test scratch stay inside the project root. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Release and mechanical exceptions remain owner-authorized only; no exception is used. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal, candidate, report, verdict, and later evidence remain distinct linked artifacts. |

## Acceptance Criteria

- Manifest validation exits zero with exactly 8 capabilities and 94 handles.
- Manifest/test hashes remain unchanged and the formatted checker matches
  `40B64AE08FD3F278C62AB5A376D9420D061C98CF54592D7A946619D896E3A193`.
- The frozen scope digest remains
  `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
- Exactly 46 focused tests pass; Ruff check and Ruff format check pass for both
  Python targets.
- Only the checker formatting diff is attributable to WI-5316.
- No clean-run, attestation, audit, semantic, activation, Git, bridge rewrite,
  database, dispatcher, credential, deployment, or release state changes.

## Risk And Rollback

Mechanical formatting could conceal functional drift or absorb unrelated edits.
The one-path command, read-only expected digest, unchanged manifest/test hashes,
46 focused tests, and independent verification constrain that risk. Any mismatch
fails closed before reporting.

Before finalization, rollback restores only the checker to its pre-format bytes.
Bridge, PAUTH, deliberation, report, and verdict evidence remain append-only.

## Recommended Commit Type

`feat`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
