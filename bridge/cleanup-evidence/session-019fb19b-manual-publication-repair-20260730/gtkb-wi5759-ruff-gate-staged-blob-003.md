NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

# GT-KB Bridge Implementation Report - WI-5759 staged-blob Ruff gate

bridge_kind: implementation_report
Document: gtkb-wi5759-ruff-gate-staged-blob
Version: 003
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5759-ruff-gate-staged-blob-002.md
Controlling GO: bridge/gtkb-wi5759-ruff-gate-staged-blob-002.md
Approved proposal: bridge/gtkb-wi5759-ruff-gate-staged-blob-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5759
target_paths: ["scripts/check_ruff_format.py", "platform_tests/scripts/test_check_ruff_format.py"]

implementation_scope: exact-two-path-source-and-test-fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

## Implementation Claim

Implemented the exact two-path correction approved in versions 001/002. The
Ruff pre-commit gate now reads each staged Python file's stage-0 blob with an
argv-list `git show :0:<path>` call and checks those bytes through Ruff stdin
with `--stdin-filename`. Worktree-only CRLF/mixed-EOL or formatting divergence
can no longer make the gate reject bytes that are not in the index, while a
genuinely misformatted staged blob still fails closed.

The implementation aggregates all failing paths, emits a stable
`Would reformat: <path>` line independent of Ruff's output shape, fails closed
when a cached-listed stage-0 blob cannot be read or the Ruff subprocess fails,
and updates the remedy to require formatting followed by re-staging. Venv-first
Ruff resolution, staged-file discovery, no-Python behavior, WARN/FAIL venv
boundary, `.githooks/pre-commit`, `.gitattributes`, and WI-5176's write-side
finalizer remain unchanged.

No MemBase, `groundtruth.db`, project, PAUTH, formal artifact, credential,
dispatcher/TAFE, Git index, commit, push, deployment, release, or external
system mutation occurred.

## First-Line Role Eligibility And Implementation Authority

- Current role: Prime Builder from `::init gtkb pb`; harness A is active as
  `prime-builder`.
- Status authored: `NEW`, the Prime Builder implementation-report status after
  an independent GO.
- Active whole-project PAUTH v3 has `included_work_item_ids: null`; WI-5759 is
  an active member of the active corrections project and inherits the project
  envelope under the owner's current direction.
- Schema-v3 packet:
  `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5759-ruff-gate-staged-blob.json`.
- Packet hash:
  `sha256:451145a35ae8be3811976a0e1f843d54159cd661ad61a905b3838318be3925d2`.
- Pre-start packet hash:
  `sha256:680000feaade66e5759e0ad1583e3111cba14b7cd55638c6a81bc09ab3fee93b`.
- Operation-time decision: allowed under program PAUTH version 3 for exactly
  `source` (`scripts/check_ruff_format.py`) and `test`
  (`platform_tests/scripts/test_check_ruff_format.py`).
- Claim session: `019fb19b-7814-73c1-8707-204e432cbf00`.

The implementation-start transaction completed successfully but required
approximately 210 seconds in the known repeated peer-history scan. That
latency is preserved as separate evidence in
`bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md`; no gate
was bypassed.

## Files Changed

- `scripts/check_ruff_format.py`
- `platform_tests/scripts/test_check_ruff_format.py`

Exact diff stat: 112 insertions, 15 deletions across two files. Both paths are
unstaged. No other path entered this implementation cohort.

## Implementation Details

### Stage-0 blob retrieval

Added `_staged_blob(root, path)` using:

```text
git -c core.quotepath=off show :0:<path>
```

The call is shell-free, captures bytes rather than decoding/re-encoding Git
content, is bounded to 30 seconds, and returns `None` on non-zero exit or
subprocess failure.

### Ruff checks use index bytes

`check_files()` now processes every staged path deterministically:

1. retrieve the stage-0 bytes;
2. fail closed and name the path if retrieval fails;
3. invoke Ruff as
   `ruff format --check --stdin-filename <path> -` with the exact blob bytes;
4. preserve the existing 300-second per-invocation bound;
5. aggregate every failure, decode diagnostic bytes with UTF-8 replacement,
   and name every path independently of Ruff output; and
6. return the existing `(ok, combined_output)` shape.

### Remedy and boundaries

The failure guidance now says to run Ruff formatting and then re-stage the
listed files. The existing newline-delimited staged-path discovery remains
unchanged; special-path/NUL-delimited discovery is outside the approved scope.
The accepted per-file Ruff subprocess cost also remains explicit.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-17`
- `GOV-10`
- `SPEC-1662`
- `SPEC-1830`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/file-bridge-protocol.md`

## Prior Deliberations

- `DELIB-202667531`, `DELIB-202667532`, `DELIB-202667533`, and
  `DELIB-202667534` - project authorization, triage, and WI-5759 routing.
- `bridge/gtkb-lo-ruff-format-gate-crlf-worktree-defect-advisory-001.md` -
  source defect analysis and staged-blob recommendation.
- `bridge/gtkb-wi5759-ruff-gate-staged-blob-001.md` - exact approved design and
  scope boundaries.
- `bridge/gtkb-wi5759-ruff-gate-staged-blob-002.md` - independent GO with no
  blocking findings.
- `bridge/gtkb-ruff-format-pre-file-gate-*` - original gate contract whose
  venv-first behavior remains unchanged.
- WI-5176 remains the separate write-side finalizer normalization boundary.

## Owner Decisions / Input

No new owner decision is required. The implementation is inside the active
whole-project PAUTH, exact GO, exact claim, and start packet. `.gitattributes`
renormalization and WI-5176 remain separately governed work.

## Requirement Sufficiency

Existing requirements remain sufficient. The implementation realizes the
reviewed staged-index-byte contract without changing requirements, project
scope, hook placement, or finalizer semantics.

## Spec-to-Test Mapping

| Requirement / approved behavior | Executed evidence |
| --- | --- |
| Gate asserts staged bytes, not worktree bytes | `test_main_checks_staged_lf_blob_not_mixed_eol_worktree` proves a path-based old-style check fails its mixed-EOL worktree precondition while the staged-blob gate passes. |
| Both divergence directions are intentional | `test_main_pins_index_vs_worktree_divergence_both_directions` proves staged-clean/worktree-dirty passes and staged-dirty/worktree-clean fails. |
| Real CRLF-checkout formatting defects still block | `test_main_autocrlf_staged_blob_still_blocks_real_format_error` proves `core.autocrlf=true` normalizes the index to LF while genuinely misformatted staged bytes still fail. |
| Blob anomalies fail closed | `test_check_files_fails_closed_when_staged_blob_is_unreadable` asserts a named blocking result. |
| Formatted/unformatted production interface behavior | The two direct `check_files()` tests now create real Git indexes and staged fixtures; main-path formatted/unformatted tests remain green. |
| Venv-first/non-Python boundaries remain unchanged | Existing `resolve_ruff`, venv-presence, no-Python, and non-Python tests pass. |
| Project/bridge operation-time authority | Schema-v3 packet records allowed source/test classifications under PAUTH v3 and the independent GO. |
| Worktree hygiene and placement | Only the two in-root packet targets are modified; Git index is empty; Ruff and diff checks pass. |

## Commands Executed And Observed Results

- Read-only baseline (parallel readiness worker): focused suite `9 passed`, one
  existing `asyncio_mode` warning.
- Implementation-start command:
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5759-ruff-gate-staged-blob --session-id 019fb19b-7814-73c1-8707-204e432cbf00`.
  Result: exit 0, valid packet, approximately 210 seconds.
- Focused final:
  `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_ruff_format.py -q --tb=short`.
  Result: `13 passed`, one existing `asyncio_mode` warning, 96.12 seconds.
- Ruff check on both paths: `All checks passed!`.
- Ruff format check on both paths: `2 files already formatted`.
- `git diff --check -- <two paths>`: exit 0; only Git informational future-CRLF warnings.
- `git status --short -- <two paths>`: exactly two unstaged modified files.
- `git diff --numstat -- <two paths>`: test `71/2`; source `41/13`.
- Proposal applicability preflight and mandatory clause preflight: PASS with
  zero blocking gaps.

## Acceptance Criteria Status

- [x] EOL-only or worktree-only divergence no longer false-fails staged clean bytes.
- [x] Genuinely misformatted staged blobs fail with stable path naming and re-stage guidance.
- [x] Both index/worktree divergence directions are pinned.
- [x] Stage-0 retrieval anomalies fail closed.
- [x] Venv-first, no-staged-Python, non-Python, and venv-presence boundaries remain green.
- [x] Focused pytest, Ruff check, Ruff format check, and diff check pass.
- [x] Only the two approved in-root targets changed.

## Risk And Rollback

Residual risks are the proposal's accepted ones: one Ruff process per staged
Python file, existing newline-delimited path discovery, and intentional passing
of worktree-only drift when the index is clean. Each Ruff invocation remains
bounded, every anomaly fails closed, and tests pin the index/worktree contract.

An independent pre-report subagent review found no blocking issue and reproduced
13 focused passes plus clean Ruff/diff checks. It recorded three P3 residuals:
the approved stable `Would reformat` prefix also labels non-format Ruff errors
(the detailed Ruff output remains present and the gate still fails closed), the
300-second bound is per file rather than a total operation deadline, and the
pre-existing newline-delimited staged-path discovery is not fully Git-path-safe.
These do not weaken the approved ordinary-path behavior; they remain explicit
review inputs rather than silent claims of broader coverage.

Rollback is an exact-path revert of the two implementation files before
terminal finalization. The numbered bridge history and authorization packet
remain immutable audit evidence and are not deleted by rollback.

## Loyal Opposition Asks

1. Independently verify the two-file diff against versions 001/002 and the
   schema-v3 packet.
2. Re-run the focused tests and Ruff/diff checks.
3. Confirm stage-0 bytes, anomaly handling, stable failure aggregation, and
   preserved venv-first boundaries.
4. Return `VERIFIED` through governed atomic finalization if satisfied, or
   `NO-GO` with concrete findings.

## Mutation Boundary

No dispatcher or TAFE state was activated or mutated. The report filing uses
the numbered file path only because the canonical helper would publish
dispatcher/TAFE state contrary to the owner's deliberate repair hold.

## Pre-Filing Preflight

The exact candidate passed credential scan with zero hits, bridge compliance
audit-only, applicability preflight, and mandatory clause preflight before
filing, with no blocking gaps.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
