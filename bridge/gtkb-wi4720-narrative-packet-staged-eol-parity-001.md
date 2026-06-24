NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef217-c239-7df0-8c15-537755d0eb70
author_model: GPT-5 Codex
author_model_version: codex-session
author_model_configuration: Codex desktop restart/resume session; approval_policy=never; resolved_role=prime-builder

# GT-KB Bridge Implementation Proposal - WI-4720 narrative staged EOL parity

bridge_kind: prime_proposal
Document: gtkb-wi4720-narrative-packet-staged-eol-parity
Version: 001
Status: NEW
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4720

target_paths: ["scripts/check_narrative_artifact_evidence.py", "platform_tests/scripts/test_check_narrative_artifact_evidence.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

## First-Line Role Eligibility Check

`gt harness roles` reports harness `A` (`codex`) as active `prime-builder`.
This is a fresh Prime Builder `NEW` proposal for unstarted authorized work item
`WI-4720`. Prime Builder acquired a draft work-intent claim for
`gtkb-wi4720-narrative-packet-staged-eol-parity` before substantive drafting;
after restart, the active claim was refreshed as row `23725`.

## Proposal Claim

`WI-4720` reports a reliability defect in the narrative-artifact evidence path:
the narrative approval packet generator records `full_content_sha256` over
LF-normalized text, while `scripts/check_narrative_artifact_evidence.py
--staged` compares that hash to the raw staged git blob bytes. A protected
narrative file staged with CRLF bytes can therefore fail `VERIFIED`
finalization even when the packet's full-content text is exactly the same
after the narrative-artifact normalization already used by the packet builder
and hook-side content checks.

This proposal fixes the checker side of that mismatch by making the staged
blob comparison use the same text normalization as the packet content:

- decode staged narrative-artifact blobs as UTF-8 text;
- normalize CRLF and lone CR to LF before hashing;
- compare the packet's `full_content_sha256` to that normalized staged-text
  hash; and
- keep substantive content mismatches, invalid packet hashes, unreadable staged
  blobs, and missing packets as failures.

This proposal does not add `.gitattributes`, does not rewrite protected
narrative files, does not create or modify approval packet artifacts, and does
not change formal or narrative artifact governance policy. It aligns the
universal staged evidence checker with the existing LF-normalized packet
contract for text narrative artifacts.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | yes | Use synthetic file content and avoid credential-shaped fixture strings. | Bridge helper credential scan plus focused diff review. | N/A |
| CQ-PATHS-001 | yes | Keep implementation inside the declared in-root checker and test target paths. | Applicability preflight, target-path review, and implementation-start packet. | N/A |
| CQ-COMPLEXITY-001 | yes | Add a small EOL-normalized staged-hash helper rather than rewriting packet discovery or Git staging. | Focused unit tests for pass/fail parity and source review. | N/A |
| CQ-CONSTANTS-001 | yes | Reuse existing required-field and reason-code patterns; introduce no broad new config constants. | Source review and regression assertions for existing failure reasons. | N/A |
| CQ-SECURITY-001 | yes | Preserve fail-closed behavior for invalid packets, unreadable blobs, and substantive mismatches. | Negative-path tests for invalid packet hash and mismatched content. | N/A |
| CQ-DOCS-001 | yes | Keep documentation in bridge proposal/report evidence; avoid mutating governed narrative docs. | LO review of bridge artifacts. | N/A |
| CQ-TESTS-001 | yes | Add focused CRLF staged-blob regression coverage and an end-to-end generated-packet check. | Targeted pytest commands in the verification plan. | N/A |
| CQ-LOGGING-001 | no | No new logging or telemetry path is required for this checker parity fix. | Confirm no logging changes in diff. | No logging behavior added. |
| CQ-VERIFICATION-001 | yes | Run targeted pytest plus Ruff lint and format checks on all changed Python paths before reporting. | Commands listed in the verification plan. | N/A |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this source/test change to begin
  only after a valid bridge `GO`, implementation-start packet, and matching
  work-intent claim.
- `.claude/rules/file-bridge-protocol.md` - requires `target_paths`,
  requirement sufficiency, project authorization metadata, prefiling
  preflights, and specification-derived verification.
- `.claude/rules/project-root-boundary.md` - confines all work and evidence to
  `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete
  specification links for the proposal and for Loyal Opposition review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the post-GO
  report to map executed tests back to these governing surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  project authorization, project, work item, and target-path linkage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the reliability defect concerns
  durable approval evidence and finalization, so the bridge chain must preserve
  the rationale and verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix must keep artifact evidence
  and executable checks aligned rather than relying on harness-local or
  ambient Git configuration behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a finalization-blocking evidence
  defect must be tracked through the bridge lifecycle before terminal
  `VERIFIED` state.
- `GOV-ARTIFACT-APPROVAL-001` - narrative approval packets inherit the
  full-content owner-visible approval evidence discipline.
- `config/governance/narrative-artifact-approval.toml` - defines the protected
  narrative-artifact path family and records that Slice C is enforced by
  `scripts/check_narrative_artifact_evidence.py`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed source, tests, and
  evidence stay under the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - `WI-4720` is an open reliability work item in
  the authorized project snapshot.

## Project Authorization

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`
  is active for the snapshot-bound 31 open member work items in
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- `WI-4720` is included in that authorization snapshot.
- Owner decision `DELIB-20265586` authorizes bounded implementation work for
  the project drive.
- Allowed mutation classes include `source`, `test_addition`,
  `hook_upgrade`, `cli_extension`, and `scaffold_update`. This proposal uses
  only source and test-addition scope.
- New work items added after the authorization snapshot remain outside this
  proposal and outside this authorization.

## Requirement Sufficiency

Existing requirements sufficient.

The live narrative-artifact packet contract already normalizes full-content
text to LF before hashing, and the current staged checker is the surface whose
raw-byte comparison diverges from that contract. No new GOV/SPEC/ADR/DCL/PB/REQ
artifact is required to implement a checker-side parity fix.

## Target Paths And Exclusions

In scope:

- `scripts/check_narrative_artifact_evidence.py`
- `platform_tests/scripts/test_check_narrative_artifact_evidence.py`
- `groundtruth-kb/tests/test_cli_approval_packet.py`

Out of scope:

- `.gitattributes`
- `.claude/hooks/narrative-artifact-approval-gate.py`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `config/governance/narrative-artifact-approval.toml`
- any formal artifact, narrative artifact, or approval packet mutation
- any change to owner-decision, AUQ, bridge dispatcher, or git finalization
  policy

If implementation discovers that `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`
must change, Prime Builder will stop and file a revised bridge proposal before
touching that source path.

## Planned Implementation

1. Add a small staged-blob text normalization helper in
   `scripts/check_narrative_artifact_evidence.py` that decodes the staged blob
   as UTF-8, normalizes CRLF and lone CR to LF, and computes the staged content
   hash from normalized text.
2. Update packet matching and packet validation so `--staged` uses the
   normalized staged-text hash when comparing to `full_content_sha256`.
3. Preserve existing failure behavior for missing staged blobs, invalid JSON,
   missing required packet fields, packet-internal hash mismatches, and
   substantive text differences.
4. Add focused regression coverage for CRLF staged content with a valid
   LF-normalized narrative packet.
5. Add an end-to-end CLI-facing regression that proves a CRLF target staged
   with a generated narrative approval packet passes the staged evidence
   checker without depending on an in-repo `.gitattributes` change.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification evidence after GO |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` | Prime Builder will run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4720-narrative-packet-staged-eol-parity` after `GO` and cite the resulting packet in the implementation report. |
| `GOV-ARTIFACT-APPROVAL-001` and `config/governance/narrative-artifact-approval.toml` | Focused tests will prove the evidence checker accepts the same LF-normalized text that the packet records, while still rejecting invalid packet hashes and substantive content mismatches. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report will map each executed pytest/Ruff command to this plan and carry forward this table. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability and clause preflights on the proposal, report, and LO verdict should pass with zero required-spec or blocking-clause gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | Target-path review and command working directories will verify all changes and evidence are in-root under `E:\GT-KB`. |
| `GOV-STANDING-BACKLOG-001` | Bridge/project metadata and `gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json` will keep `WI-4720` tied to the authorized project snapshot. |

Planned commands after implementation:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_narrative_artifact_evidence.py groundtruth-kb/tests/test_cli_approval_packet.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_narrative_artifact_evidence.py platform_tests/scripts/test_check_narrative_artifact_evidence.py groundtruth-kb/tests/test_cli_approval_packet.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_narrative_artifact_evidence.py platform_tests/scripts/test_check_narrative_artifact_evidence.py groundtruth-kb/tests/test_cli_approval_packet.py
```

## Prior Deliberations

- `DELIB-20265586` - owner decision authorizing this snapshot-bound bounded
  implementation drive for `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20261601` / `bridge/gtkb-generate-approval-packet-cli-008.md` -
  Loyal Opposition found that relying on `git add` alone does not
  mechanically guarantee raw staged bytes match LF-normalized packet content;
  this proposal chooses the checker-side normalization solution instead of
  depending on ambient Git configuration.
- `DELIB-1575` / `bridge/gtkb-narrative-artifact-approval-extension-001-011.md`
  - verifies the narrative-artifact approval extension whose Slice C checker
  is being repaired.
- `DELIB-0835` - owner-visible full-content approval evidence remains strict;
  this proposal preserves substantive content identity and changes only EOL
  normalization parity for text artifacts.
- `bridge/gtkb-platform-sot-consolidation-wi4348-phase1-rule-state-strip-004.md`
  - observed related `VERIFIED` finalization failure that exposed the raw blob
  versus LF-normalized packet mismatch.

## Owner Decisions / Input

No new owner decision is required.

The operative owner authorization is
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`
with owner decision `DELIB-20265586`. This proposal does not request formal
artifact mutation, narrative artifact mutation, deployment, credential work,
destructive cleanup, or any new work item outside the snapshot-bound
authorization.

## Acceptance Criteria

- A CRLF-staged protected narrative file with a valid LF-normalized full-content
  packet passes the staged evidence checker.
- A CRLF-staged protected narrative file with a packet for different
  substantive text still fails.
- A packet whose `full_content_sha256` does not match its own `full_content`
  still fails.
- Existing no-packet, missing-staged-blob, invalid packet, and unprotected-path
  behavior remains intact.
- Focused pytest and Ruff lint/format checks pass on the target paths.

## Pre-Filing Preflight Evidence

Candidate preflight commands for this completed draft:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4720-narrative-packet-staged-eol-parity --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4720-narrative-packet-staged-eol-parity-001.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4720-narrative-packet-staged-eol-parity --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4720-narrative-packet-staged-eol-parity-001.md
```

Observed applicability result on the completed draft:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- packet hash `sha256:fb90dae0110db9e4e8fa90d92f91e5d251121a208cb933c536a2b9b0426b94dc`

Observed clause result on the completed draft:

- exit `0`
- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`

The Codex bridge-propose helper reruns the bridge compliance audit before
writing the live bridge file.

## Risk And Rollback

Risk: normalizing staged text weakens byte-for-byte equality for narrative text
artifacts. Mitigation: the protected narrative-artifact packet contract already
stores LF-normalized UTF-8 text; the checker remains strict about packet
schema, packet-internal hash, target path, and substantive content.

Risk: binary or non-UTF-8 files under protected narrative patterns would now
fail decode before comparison. Mitigation: the configured protected
narrative-artifact set is text-oriented; decode failures should remain
governance failures rather than silent passes.

Rollback: revert the source/test implementation commit after `GO`, then file a
new bridge report or revision explaining the rollback. Do not edit or delete
numbered bridge artifacts.

## Loyal Opposition Asks

1. Confirm this proposal has sufficient existing requirements for checker-side
   EOL normalization parity.
2. Issue `GO` if the source/test target paths and verification plan are
   approved under the project authorization.
3. Issue `NO-GO` if the fix must instead use `.gitattributes`, target-file
   rewriting, or a new formal requirement before implementation.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
