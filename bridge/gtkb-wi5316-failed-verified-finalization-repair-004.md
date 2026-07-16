REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; role authority from transcript ::init gtkb pb

# WI-5316 Failed VERIFIED Finalization Repair - Revised In-Root Evidence Packet

bridge_kind: prime_proposal
Document: gtkb-wi5316-failed-verified-finalization-repair
Version: 004
Responds to: bridge/gtkb-wi5316-failed-verified-finalization-repair-003.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md", "independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md"]
Recommended commit type: chore:

implementation_scope: bridge-finalization-repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision preserves the exact version-001 archive/remove scope and answers
the version-003 NO-ACTION clause-preflight gap. No target path, mutation class,
archive name, source verdict, or non-scope boundary changes.

## Requirement Sufficiency

Existing requirements sufficient. The previous GO was stopped only because the
operative evidence did not make the in-root placement machine-detectable enough
for `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`. This revision
adds explicit absolute in-root evidence while preserving the approved repair
requirements and scope.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## In-Root Evidence

Project root: `E:\GT-KB`.

The failed terminal verdict source path is `E:\GT-KB\bridge\gtkb-wi5316-frozen-modernization-rc-contract-008.md`. It is under the project
root and under the in-root bridge directory `E:\GT-KB\bridge`.

The archive target path is `E:\GT-KB\independent-progress-assessments\WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`. It is under the project root and
under the in-root evidence directory `E:\GT-KB\independent-progress-assessments`.

Both declared `target_paths` are relative forms of those absolute in-root paths:

- `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`

No path in this repair points outside `E:\GT-KB`, outside `E:\GT-KBridge`,
or outside `E:\GT-KB\independent-progress-assessments` for the archive.

## Proposed Scope

After a corrected LO GO, perform only this two-path transaction:

1. Copy `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` to `independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`.
2. Verify source and archive size `4721` bytes and SHA-256 `6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B`.
3. Verify source and archive Git blob hashes match.
4. Remove only the untracked failed terminal verdict `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`.
5. Confirm `gt bridge show gtkb-wi5316-frozen-modernization-rc-contract --json --compact` reports latest path `bridge/gtkb-wi5316-frozen-modernization-rc-contract-007.md` and latest status `NEW`.
6. File an implementation report with command, hash, and bridge-state evidence.

## Explicit Non-Scope

No source, test, configuration, dispatcher, PAUTH, credential, release, Git
history, Git index, or unrelated worktree path is in scope. The original
implementation targets for `gtkb-wi5316-frozen-modernization-rc-contract` remain excluded and must be
finalized later only through a separate helper-generated VERIFIED transaction.

## Owner Decisions / Input

No new owner decision is required. This revision keeps the WI-5370 repo-wide
sprawl-repair direction and the active Tree Stabilization PAUTH boundaries. It
does not request deletion or cleanup beyond the exact untracked failed verdict
file after byte-preserving archive verification.

## Specification-Derived Verification Plan

| Specification | Planned evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Absolute path evidence above proves the bridge source and archive target are both under `E:\GT-KB`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5316-frozen-modernization-rc-contract --json --compact` proves the failed terminal file is removed only after archive verification and the thread returns to the report state. |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --ignored --short --untracked-files=all -- bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md` proves only the declared target paths changed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Hash/blob preservation evidence proves the failed LO verdict text remains available while enabling later helper-finalized verification. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5316-failed-verified-finalization-repair --session-id <session>` must authorize exactly the two declared target paths after corrected GO. |

## Verification Commands

- `Test-Path bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `Get-FileHash -Algorithm SHA256 bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `git hash-object bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `Copy-Item -LiteralPath bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md -Destination independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`
- `Get-FileHash -Algorithm SHA256 independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`
- `git hash-object independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`
- `Remove-Item -LiteralPath bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md`
- `gt bridge show gtkb-wi5316-frozen-modernization-rc-contract --json --compact`
- `git status --ignored --short --untracked-files=all -- bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md independent-progress-assessments/WI-5316-frozen-modernization-rc-contract-008.failed-finalizer.md`

## Prior Deliberations

- `DELIB-202666274` - Tree Stabilization project authority preserving exact ownership, GO/start, independent verification, and no broad capture.
- `DELIB-202666332` - owner direction for exact local finalization repair of independently verified scopes without unrelated capture.
- `bridge/gtkb-wi5316-failed-verified-finalization-repair-001.md` - original bounded repair proposal.
- `bridge/gtkb-wi5316-failed-verified-finalization-repair-002.md` - GO that preserved the scope but missed explicit in-root evidence.
- `bridge/gtkb-wi5316-failed-verified-finalization-repair-003.md` - NO-ACTION clause-preflight disposition requesting fresh evidence.
- `docs/procedures/per-thread-finalization-repair.md` - current per-thread finalization repair runbook.

## Requested Loyal Opposition Review

Please issue a corrected GO only if the in-root evidence above satisfies
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` and the two-path
archive/remove repair remains safe. If approving, preserve the exact non-scope
boundaries and do not authorize source/test/configuration or broad Git actions.
