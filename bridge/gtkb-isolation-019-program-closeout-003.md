REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Isolation Backstop Prerequisite (GTKB-ISOLATION-019) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-isolation-019-program-closeout
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-isolation-019-program-closeout-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-019

target_paths: ["scripts/isolation_program_backstop.py", "scripts/release_candidate_gate.py", "tests/scripts/test_isolation_program_backstop.py"]

## Revision Claim

This revision splits the original closeout bundle. It keeps only the mechanical isolation backstop and release-candidate gate integration in this bridge, and explicitly defers the final closeout report until sibling isolation threads are latest `VERIFIED`.

No closeout-report file is authorized by this revision.

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT`, including `GTKB-ISOLATION-019`.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence and single-active-application contract.
- `DELIB-1965` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice3-init-defaults-2026-05-02`.
- `DELIB-1969` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice2-registry-isolation`.

## Owner Decisions / Input

No new owner decision is required. The S350 project authorization remains in force. This revision narrows the scope to avoid premature program-closeout claims.

## Findings Addressed

### FINDING-P1-001 - Required release-gate file is outside `target_paths`

Response: Added `scripts/release_candidate_gate.py` to `target_paths`, because release-gate integration remains in scope.

### FINDING-P2-001 - Program closeout depends on sibling threads that are not terminal

Response: Removed `docs/gtkb-isolation-program-closeout-report.md` and all final closeout-report work from this bridge. The closeout report is deferred until the cited sibling threads are latest `VERIFIED`. This bridge now creates the backstop that will support future closeout evidence.

## Proposed Scope

### IP-1: Backstop script

Create `scripts/isolation_program_backstop.py`.

Required behavior:

1. Scan canonical GT-KB platform files for unauthorized `applications/<name>/` path references.
2. Allow explicitly authorized cross-scope references required by GT-KB operating-model documentation, bridge history, and test fixtures.
3. Emit JSON with `violations`, `allowed_references`, and `scanned_files`.
4. Exit non-zero if unauthorized references exist.
5. Stay read-only.

### IP-2: Release-candidate gate integration

Update `scripts/release_candidate_gate.py` to run the backstop as a non-deploying release-readiness check.

Required behavior:

1. Backstop failure fails the gate.
2. Missing backstop script fails the gate with a clear diagnostic.
3. Backstop command output is included in the release-gate result payload.

### IP-3: Tests

Add `tests/scripts/test_isolation_program_backstop.py`.

The tests must cover unauthorized reference detection, allowlist behavior, clean-tree exit code, JSON output shape, and release-gate invocation.

## Explicitly Deferred

- `docs/gtkb-isolation-program-closeout-report.md`.
- Any final claim that the isolation program is complete.
- Any retrospective phase/slice closeout table.

Future closeout-report proposal precondition: the bridge entries for the required sibling isolation work must be latest `VERIFIED`, and the new report must cite concrete live bridge versions.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Backstop detects unauthorized `applications/<name>/` references | `python -m pytest tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Backstop allows documented cross-scope references | `python -m pytest tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Backstop emits stable JSON and read-only exit codes | `python -m pytest tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Release-gate invokes the backstop and fails closed | `python -m pytest tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Changed scripts lint and format cleanly | `python -m ruff check scripts/isolation_program_backstop.py scripts/release_candidate_gate.py tests/scripts/test_isolation_program_backstop.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `scripts/isolation_program_backstop.py` exists and is read-only.
2. `scripts/release_candidate_gate.py` runs the backstop and fails closed on violations or missing script.
3. `tests/scripts/test_isolation_program_backstop.py` covers detection, allowlist, JSON shape, clean exit, and release-gate invocation.
4. No closeout report is created in this slice.
5. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

Risk: allowlist tuning may be too broad or too narrow. Mitigation: require explicit allowlist tests and JSON reporting of allowed references.

Risk: release-gate integration could add noise before the allowlist is tuned. Mitigation: gate output must include exact violating paths so failures are actionable.

Rollback: remove the release-gate call, delete `scripts/isolation_program_backstop.py`, and delete the focused tests. No documentation closeout artifact is affected.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-isolation-019-program-closeout --content-file .gtkb-state\bridge-revisions\drafts\gtkb-isolation-019-program-closeout-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-019-program-closeout --content-file .gtkb-state\bridge-revisions\drafts\gtkb-isolation-019-program-closeout-003.md`

End of revision.
