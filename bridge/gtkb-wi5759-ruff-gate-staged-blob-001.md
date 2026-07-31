NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker; manual dispatch per DELIB-202667523; resolved role prime-builder for this filing

# Implementation Proposal - Fix ruff-format Commit Gate To Check Staged LF Blobs Instead Of CRLF Worktree Bytes (WI-5759)

Document: gtkb-wi5759-ruff-gate-staged-blob
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5759

target_paths: ["scripts/check_ruff_format.py", "platform_tests/scripts/test_check_ruff_format.py"]

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write during filing; the implementation touches only the two target_paths files and is covered by the cited project authorization. This proposal performs no approval-evidence work; it requires no approval packets.

---

## Problem

Source advisory: `bridge/gtkb-lo-ruff-format-gate-crlf-worktree-defect-advisory-001.md` (read in full; root cause re-verified against `scripts/check_ruff_format.py` at HEAD).

The pre-commit ruff-format guardrail checks the wrong bytes:

- `staged_python_files()` (lines 57-71) collects staged `*.py` paths from `git diff --cached --name-only --diff-filter=ACM` - correct.
- `check_files()` (lines 115-127) then invokes `ruff_cmd + ["format", "--check", *files]` against those **worktree paths**. Ruff opens each file from the working tree; the staged blob (`git show :0:<path>`) - the LF-normalized content git will actually commit - is never consulted.

On a Windows checkout, worktree bytes carry CRLF (or mixed EOL) while `git add` normalizes the index blob to LF. The gate therefore reports "would be reformatted" on line endings alone, regardless of actual formatting. Measured impact in the surfacing incident (advisory Evidence 3): 9 of 13 gate-reported WI-5441 files failed on carriage returns alone (HEAD-clean AND LF-normalized-clean), inflating the blocker count from four real files to thirteen and rejecting a `write_verdict.py --finalize-verified` transaction - a direct block on terminal VERIFIED closure. This is a standing, harness-independent defect that can fire on any commit touching any Python file on any CRLF checkout.

`.gitattributes` also carries no `*.py` normalization rule (advisory Evidence 2). That half is advisory Option B and is **explicitly out of scope here**: the repository-wide `*.py` renormalization is separately-owned hygiene per the WI-5759 description and the 2026-07-29 triage, because its one-time renormalization commit has a large blast radius that must not be folded into this gate correction.

Boundary with related family WI-5176: WI-5176 is the **write-side** defect - `write_verdict.py --finalize-verified` stages worktree bytes verbatim into its disposable index, bypassing autocrlf/gitattributes normalization and landing CRLF flips in terminal commits. This proposal fixes only the **read side** (the gate's comparison source) in `scripts/check_ruff_format.py`; it does not modify `write_verdict.py`, does not claim to remediate WI-5176, and leaves that item open and untouched. The two share a root context (CRLF worktrees vs LF history) but are distinct surfaces with distinct fixes.

## Proposed Changes

Advisory Option A, as dispositioned by the owner triage: make the gate assert exactly the bytes git will commit. All changes are confined to the two `target_paths` files. The script remains stdlib-only, and the deterministic venv-first ruff resolution (`resolve_ruff`, the load-bearing F2 design from the original thread) is untouched.

### Change 1 - staged-blob retrieval helper

Add `_staged_blob(root: Path, path: str) -> bytes | None` in `scripts/check_ruff_format.py`: run `git -c core.quotepath=off show :0:<path>` with argv-list invocation (no shell), `cwd=root`, bytes capture (no text decoding), bounded timeout. Return `stdout` bytes on returncode 0, else `None`.

### Change 2 - check_files() compares index content

Rework `check_files(ruff_cmd, files, root) -> tuple[bool, str]` (signature and return type unchanged) to iterate the staged paths and, per file:

1. retrieve the staged blob via `_staged_blob`;
2. a `None` blob for a `--cached`-listed path is an anomaly and **fails closed** - it is reported as a blocking failure, never silently passed (consistent with the gate's existing fail-closed philosophy for dev-env misconfiguration);
3. otherwise pipe the blob bytes to `ruff_cmd + ["format", "--check", "--stdin-filename", <path>, "-"]` (stdin drive; `--stdin-filename` preserves per-file config resolution), with the per-invocation timeout retained.

Failures are aggregated: the combined output includes a deterministic `Would reformat: <path>` line per failing file (so failing paths are always named independent of ruff's stdout shape) plus ruff's own output. PASS output is unchanged.

### Change 3 - remedy guidance matches the new semantics

Update the `main()` FAIL remedy line to `Remedy: run  ruff format <files>  then re-stage (git add) the listed files`, because fixing worktree bytes alone does not change the staged blob the gate now asserts.

Intentional semantic tightening, stated plainly: after this change, worktree-only drift (staged blob clean, worktree copy dirty) no longer fails the gate. That is by design - git commits the index, and the worktree copy is checked when it is staged. This matches the gate's own documented purpose ("block any commit whose **staged** Python is unformatted") and what CI sees for committed content. T4 pins both directions of this boundary.

### Test updates

`platform_tests/scripts/test_check_ruff_format.py`: the two direct `check_files()` unit tests (`test_check_files_passes_on_formatted`, `test_check_files_fails_on_unformatted`) currently write bare files into `tmp_path` with no repository and no staging; they are updated to `git init` + stage their fixture content, preserving their behavioral assertions (PASS on formatted staged blob, FAIL on unformatted staged blob). New tests T1-T4 below are added. All other existing tests pass unchanged.

### Explicitly out of scope

- `.gitattributes` `*.py` renormalization (advisory Option B) - separately-owned hygiene with its own owner-visible scheduling; not part of this thread.
- `write_verdict.py` finalize-helper staging normalization - WI-5176's surface, boundary stated above.
- The advisory's secondary claim-TTL observation - separately dispositioned in the 2026-07-29 triage; not this thread's subject.
- `.githooks/pre-commit` - the invoking surface is unchanged; the fix is entirely inside the script it invokes.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the gate is the write-time layer of the two-layer ruff-format defense in depth; a mechanically false-firing gate erodes the enforcement contract, and the fix restores truthful write-time enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the false-fail rejected a VERIFIED commit-finalization transaction (the surfacing incident); repairing the gate sustains bridge finalization durability and the append-only audit trail's commit discipline.
- `GOV-17` - automation script modification approval gate: `scripts/check_ruff_format.py` is a commit-automation guardrail invoked by `.githooks/pre-commit`; this bridge proposal plus Loyal Opposition `GO` under the cited project authorization is the approval evidence for modifying it.
- `GOV-10` - tests exercise exposed production interfaces: `main()` via the active-hook subprocess invocation shape and the public `check_files()`/`staged_python_files()` functions, using the existing module-load harness.
- `SPEC-1662` (GOV-18) - assertion quality: T1 carries an in-test red-precondition assert (the worktree bytes provably fail a path-based check) so the fixture asserts behavior, not structure, and stays robust to ruff EOL-detection semantics.
- `SPEC-1830` - operational procedures must be code: the re-stage remedy is emitted by the gate itself, not left as conversational lore.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the gate is a deterministic service; determinism now extends to asserting exactly the bytes git will commit, eliminating the environment-dependent (checkout-EOL-dependent) false-fail class.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this work proceeds under the cited active project authorization plus this proposal's bridge `GO`; PAUTH metadata does not broaden `target_paths` and does not replace the live latest-`GO` requirement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section satisfies the mandatory proposal spec-linkage constraint; the verification plan maps each link to derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the eventual `VERIFIED` is conditional on creation and execution of spec-derived tests T1-T5; the implementation report will carry the executed commands and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this correction lands as a durable artifact chain (advisory -> owner triage decision -> work item -> proposal -> tests), not as transient chat remediation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change preserves traceability across the artifact graph: the advisory, the original gate thread's F2 design contract, WI-5759, and the spec-derived tests all cross-cite.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - thread lifecycle states remain explicit (NEW -> GO/NO-GO -> report -> VERIFIED); the fix itself unblocks the VERIFIED finalization lifecycle transition the defect was rejecting.
- `.claude/rules/file-bridge-protocol.md` § Pre-File Code-Quality Gates and § Mandatory VERIFIED Commit-Finalization Gate - the rule surfaces that name `scripts/check_ruff_format.py` as the commit-time format backstop whose false-fail blocked finalization; the fix preserves that contract while making it truthful.

Tests derive from these links as mapped in the verification plan below.

## Prior Deliberations

Targeted search (`gt deliberations search "ruff format gate CRLF staged" --limit 5`) returned only adjacent LO-verification records (`DELIB-20265623`, `DELIB-20261096`, `DELIB-20261239`, `DELIB-20264794`, `DELIB-20260824` - none addressing the gate's worktree-versus-index comparison), consistent with the source advisory's own finding that this defect is a first surfacing.

- `DELIB-202667531` - owner advisory-triage decision: fix-class first, authorized corrective WIs (WI-5759 is part of that set).
- `DELIB-202667532` - program north-star scoring under which WI-5759 was sequenced (convergence order 120).
- `DELIB-202667533` - advisory-triage synthesis decisions AT-01..04 (program PAUTH operating model this thread runs under).
- `DELIB-202667534` - advisory corpus disposition table: `gtkb-lo-ruff-format-gate-crlf-worktree-defect` dispositioned as fix WI `WI-5759`; this thread implements that disposition.
- `DELIB-202667523` - integrated parallel-operation program mandate and manual-dispatcher operating model (this filing is a fan-out worker product).
- `bridge/gtkb-lo-ruff-format-gate-crlf-worktree-defect-advisory-001.md` - the source advisory (classification `adapt`; Option A adopted here, Option B adapted into separately-owned hygiene).
- `bridge/gtkb-ruff-format-pre-file-gate-*` (WI-3473, GO at `-008`) - the original gate thread; its load-bearing F2 venv-first resolution design is deliberately untouched by this change.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-009.md` / `-010.md` - the incident context in which the defect surfaced and the NO-GO whose F1 attribution the advisory corrected.

## Owner Decisions / Input

- `DELIB-202667531` - owner authorization of the fix-class advisory-correction work set, including WI-5759 (advisory triage 2026-07-29). Recorded owner decision; per CLAUDE.md session-start rules, items already authorized by recorded owner decision need no fresh approval to enter the bridge protocol.
- `AUQ-20260729-ADVISORY-TRIAGE-POLICY` - the AskUserQuestion evidence behind the 2026-07-29 advisory-triage policy (fix-class first; capture is not implementation approval), under which this proposal is filed for Loyal Opposition review rather than implemented directly.
- The source advisory's owner-grilling questions (Option A/B/C selection; renormalization scheduling) are resolved by the recorded triage: Option A now as WI-5759; the `*.py` renormalization is separately-owned hygiene outside this thread, per `DELIB-202667531`/`DELIB-202667534` and the WI-5759 description.
- No further owner decision is required to review this proposal; implementation proceeds only on bridge `GO` plus an implementation-start authorization packet.

## Requirement Sufficiency

Existing requirements sufficient. The gate's own governing contract from the original thread (`gtkb-ruff-format-pre-file-gate`, WI-3473: block any commit whose **staged** Python is unformatted), `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (truthful write-time enforcement), `GOV-FILE-BRIDGE-AUTHORITY-001` (finalization durability), and the source advisory's mechanically verified defect analysis (confirmed against `scripts/check_ruff_format.py` lines 115-127 at HEAD) fully determine the required behavior: the comparison source must be the staged blob. No new or revised requirement is needed before implementation.

## Verification Plan (Spec-Derived Test Mapping)

New/updated tests live in `platform_tests/scripts/test_check_ruff_format.py` (existing tmp_path fixture-repo harness; live repository untouched):

| # | Test | Derives from |
|---|------|--------------|
| T1 | EOL false-fail regression (red-before/green-after): stage format-clean LF content, then rewrite the worktree file with CRLF/mixed-EOL bytes without re-staging; precondition-assert inside the test that a path-based `ruff format --check` on the worktree file FAILS (guards the fixture against ruff EOL-detection drift); the gate must PASS (exit 0). Fails under the current implementation; passes after the change. | advisory Evidence 1/3; GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; file-bridge-protocol § Pre-File Code-Quality Gates |
| T2 | True positive preserved: stage genuinely misformatted content; gate FAILS (exit 1), names the failing path, and prints the re-stage remedy line. | GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; SPEC-1662 |
| T3 | Windows-checkout regression: repo with `core.autocrlf=true`; write misformatted CRLF content and `git add` it (index blob LF, still misformatted); gate FAILS - the staged-blob path does not fail open on CRLF checkouts. | advisory Claim; GOV-10 (exercised through the `main()` hook-invocation shape) |
| T4 | Index-vs-worktree divergence pin, both directions: (a) staged clean + worktree misformatted (not re-staged) -> PASS; (b) staged misformatted + worktree fixed (not re-staged) -> FAIL. | advisory Evidence 1 (the gate asserts index content); SPEC-1662 |
| T5 | Existing-suite parity: the full pre-existing test set passes; the two direct `check_files()` tests are updated to stage their fixtures (behavioral assertions unchanged); the F2 venv-first resolution, no-staged-Python no-op, and WARN/FAIL venv-boundary tests pass byte-unmodified. | GOV-10; original-thread F2 contract; GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 |

Commands (implementation report will carry observed output):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_ruff_format.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py`

## Acceptance Criteria

1. EOL-only worktree divergence no longer fails the gate (T1 green; demonstrably red under the pre-change implementation).
2. Genuinely misformatted staged blobs still fail with the path named and the re-stage remedy printed (T2, T3).
3. The gate asserts index content exclusively - both divergence directions pinned (T4).
4. F2 venv-first resolution, no-staged-Python no-op, and WARN/FAIL venv-presence boundaries are unchanged (T5).
5. `ruff check` and `ruff format --check` pass on both changed files; the script remains stdlib-only.

## Risk and Rollback

- Risk: per-file ruff invocation (N stdin subprocesses replacing one batch call - the advisory's acknowledged Option A weakness). Bounded by commit-scale staged sets with the per-invocation timeout retained; a pathological mega-commit degrades sequentially and boundedly, and the gate remains a local pre-commit surface, not a CI hot path.
- Risk: path quoting/special characters on Windows. Mitigated: argv-list subprocess invocation (no shell) and `git -c core.quotepath=off`; paths are consumed verbatim from `git diff --cached --name-only` output as today.
- Risk: the intentional semantic tightening could surprise a developer whose worktree is dirty but staged content clean. Mitigated: this is the documented gate purpose (staged Python), the remedy line teaches the re-stage step, and T4 pins the boundary so the behavior is explicit and tested rather than incidental.
- Risk: `_staged_blob` anomaly handling. Fails closed with a named-path diagnostic; never a silent pass.
- Rollback: single-commit revert of the two target files restores the prior worktree-path behavior. No schema change, no MemBase write, no configuration migration, no hook re-registration.

Recommended commit type: fix

## Review Questions for Loyal Opposition

1. Is fail-closed the right severity when `git show :0:<path>` fails for a `--cached`-listed path (an anomaly that should be impossible in normal operation), or should that file WARN-skip instead?
2. Is the updated remedy line (`ruff format <files>` then re-stage) sufficient guidance, or should the gate emit an exact per-file `git add` command list?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
