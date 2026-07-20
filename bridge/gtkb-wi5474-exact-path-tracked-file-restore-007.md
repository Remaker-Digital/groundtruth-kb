NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata


# GT-KB Bridge Implementation Report - WI-5474 Exact-Path Restore Fail-Closed Completion

bridge_kind: implementation_report
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5474-exact-path-tracked-file-restore-006.md
Approved proposal: bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474
target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_exact_restore.py"]
Recommended commit type: fix

## Implementation Claim

The version-005 correction approved by independent GO version 006 is
implemented on the exact four-file envelope. The semantic correction changes
only `normalize_repo_path()` and the focused unsafe-input test matrix:

1. `normalize_repo_path()` now rejects an empty `Path.parts` tuple before
   indexing its first component.
2. The production CLI test matrix now includes `.`, `./.`, `././.`, and
   `.\\.`.
3. Every unsafe-input case now asserts no traceback and byte-identical target
   status, unrelated status, and Git index state.

The previously existing WI-5474 exact-restore implementation in
`__main__.py`, `repository.py`, `service.py`, and the focused test module
remains candidate work from the earlier implementation cycle. This report
asks Loyal Opposition to verify the complete WI-5474 behavior while
attributing this implementation cycle only to the narrow version-005
correction above. `__main__.py` and `service.py` were preserved byte-for-byte.

No restore operation was run against the live GT-KB checkout. None of the 17
deleted tracked bridge predecessors was restored under this GO. No dispatcher,
TAFE, harness, lease, MemBase, credential, Git index, commit, push, deployment,
release, or unrelated worktree mutation was performed.

## Implementation Authority

- Operative proposal:
  `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`.
- Independent GO:
  `bridge/gtkb-wi5474-exact-path-tracked-file-restore-006.md`, authored by
  Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`, independent
  of this Prime Builder session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- Active exact project authorization:
  `PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718`.
- Matching `go_implementation` claim row `32998` was acquired at
  `2026-07-19T06:18:32Z` for this exact thread, project, and PB session.
- Schema-v3 implementation-start authorization was finalized at
  `2026-07-19T06:19:08Z`, expires at `2026-07-19T08:19:08Z`, and has packet
  hash
  `sha256:e8a5e02951144879d46ddb8db9dbfe148fce3c428f3e387e5e143ace8f7af9ab`.
- Operation-time validation returned `authorized: true` for the two files
  changed by the correction.

## Exact Hunk Ownership

The approved production correction is exactly:

```diff
-    if not raw or path.is_absolute() or ".." in path.parts:
+    if not raw or not path.parts or path.is_absolute() or ".." in path.parts:
```

The approved focused-test correction adds exactly four root-only parameter
values, three before-state snapshots, one no-traceback assertion, and three
after-state equality assertions to the existing unsafe-input test.

Current target SHA-256 values:

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`:
  `A9E7550F6D79139D1C21DB8BF442DD9AC6DD698FA406E6193F6AB2000D759F7F`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`:
  `83C776C5BDC7CFD187AFC2AD896316B06CCFD5D10A249886F5761B6A131B1FF1`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`:
  `ED1375E5FD27D6480DA909A1B679016E080D51CA59641181EC4D8DAA7C329327`
- `platform_tests/scripts/test_git_lifecycle_exact_restore.py`:
  `C4E98506BD47A362FE400FBDF74DFA2AE3EC92735536022F8B32E621AEFF81DD`

The `__main__.py` and `service.py` hashes are identical to their recorded
pre-correction hashes. The Git index remained empty.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
  bounded defect-repair carrier while preserving the independent GO, exact
  claim, implementation-start, testing, and independent verification gates.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps
  dispatcher configuration outside this implementation.
- No new owner decision is required for the exact version-005 correction.

## Prior Deliberations And Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-006.md`
- `TEST-11572`

## Specification-Derived Verification

| Specification / governing surface | Executed verification or canonical evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only v005 proposal, independent v006 GO, exact claim, helper-mediated v007 report filing, and no live restore operation. | PASS |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | The 31-case production exact-restore suite covers exact ref/path/blob handling, and the 13-case denial slice proves root-only paths fail before mutation. | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | Every unsafe-input case asserts unchanged target status, unrelated status, and index bytes; the live index remained empty. | PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | The complete exact-restore suite and frozen modernization Git-lifecycle module pass after the correction. | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact active PAUTH, claim row 32998, schema-v3 packet hash, and per-target operation-time validation preceded both protected edits. | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | v005 and this report carry the same PAUTH, project, WI, exact target envelope, and all 16 linked specifications; live preflights have no gaps. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Fresh 31-case and 2-case suites, focused 13-case root denial evidence, and all quality checks were executed after implementation. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation and fixture paths are in-root GT-KB platform paths; temporary Git fixtures remain in-root. | PASS |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5474, TEST-11572, PAUTH, proposal, GO, source/test evidence, and this report remain distinct durable lifecycle artifacts pending independent verification. | PASS |

## Commands Run And Observed Results

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short`
  - PASS: `31 passed, 1 warning in 61.28s`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short -k test_cli_denies_unsafe_or_multipath_input -vv`
  - PASS: `13 passed, 18 deselected, 1 warning in 28.41s`.
  - The listed passing cases include `.`, `./.`, `././.`, and `.\\.`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short`
  - PASS: `2 passed, 1 warning in 185.68s`.
- The pytest warning is the pre-existing unknown `asyncio_mode` configuration
  warning.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  - PASS: `All checks passed!`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  - PASS: `4 files already formatted`.
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  - PASS.
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  - PASS.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore`
  - PASS: packet
    `sha256:ae36581cdc12f1200c2c0cf02189829419bd0e72c2ccd58850ccb2cc8ecf7dd5`;
    `missing_required_specs=[]`, `missing_advisory_specs=[]`,
    `blocking_errors=[]`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore`
  - PASS: zero evidence gaps in must-apply clauses and zero blocking gaps.
- `python scripts/implementation_authorization.py validate --target <each changed target>`
  - PASS: both exact changed targets returned `authorized: true`.
- `git diff --cached --name-only`
  - PASS: no output; the index is empty.

## Acceptance Criteria Status

- PASS: `.`, `./.`, `././.`, and `.\\.` return governed
  `unsafe_scope_path` denial through the production CLI.
- PASS: no root-only spelling reaches `path.parts[0]`, emits a traceback, or
  mutates target, unrelated status, or index bytes.
- PASS: all previously passing exact-restore behavior remains green.
- PASS: the newly attributed correction is limited to the normalization guard
  and focused test additions.
- PASS: `__main__.py` and `service.py` remain byte-identical.
- PASS: no live GT-KB restore or unrelated repository, dispatcher, runtime,
  MemBase, harness, credential, push, deployment, or release operation
  occurred.
- PENDING: independent Loyal Opposition verification and later focused
  finalization under its own applicable Git authority.

## Risk And Rollback

The correction only rejects normalized values that have no concrete path
component. Valid dotted filenames and ordinary repository-relative paths
remain covered by the existing passing suite.

Before finalization, rollback is the exact reverse of the one production guard
addition plus the focused test additions described in this report. After a
future focused commit, rollback must be a separately governed forward revert.
Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the complete WI-5474 candidate implementation against v005 and v006,
   while treating only the exact guard and focused test additions as new work
   in this cycle.
2. Rerun the 31-case exact-restore suite, 13-case denial slice, modernization
   module, and quality checks.
3. Confirm `__main__.py` and `service.py` retain the stated hashes.
4. Confirm no live restore occurred and WI-5631 remained unstarted.
5. Return VERIFIED only if every required claim is substantiated; otherwise
   return NO-GO with exact findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
