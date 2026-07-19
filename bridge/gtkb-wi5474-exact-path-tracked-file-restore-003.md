NEW
::init gtkb lo
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5474-exact-path-tracked-file-restore - 003

bridge_kind: implementation_report
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5474-exact-path-tracked-file-restore-002.md
Approved proposal: bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ::open build

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474
Recommended commit type: `feat:`

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_exact_restore.py"]

## Implementation Claim

Implemented the independently approved exact-path tracked-file restore across
the four declared targets. The production CLI now exposes
`restore-deleted-path` with exactly one `--path` and one `--source-ref`.
Repeated arguments are denied in live and dry-run modes. Safe path
normalization rejects absolute, escaping, `.git`, pathspec-like, whitespace,
comma/brace, and other multi-path forms.

The repository boundary resolves one unambiguous commit, reads one regular-file
blob with byte-safe Git plumbing, captures NUL-delimited exact status and the
complete staged-blob index surface, and creates the absent target exclusively
from the selected blob bytes. The service requires the target status to be
exactly one unstaged deletion, refreshes every precondition immediately before
mutation, then proves:

- restored bytes and the restored Git blob equal the selected source blob;
- the index snapshot is unchanged;
- all unrelated status bytes are unchanged.

A failed postcondition removes the newly restored target before returning a
stable denial. Structured output includes the normalized path, requested and
resolved source, source mode/blob, restored blob, target status transition,
and before/after index and unrelated-status hashes. Human output includes the
same principal path/commit/blob evidence.

The 27-case integration module uses only isolated temporary Git repositories
created under the GT-KB project root and cleaned after each case. No restore
operation was invoked against the live GT-KB worktree. No dispatcher, TAFE,
harness, runtime, MemBase, credential, Git staging/commit/history/push,
deployment, or release configuration was modified.

## Authorization Evidence

- Latest approved proposal:
  `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md`.
- Independent GO:
  `bridge/gtkb-wi5474-exact-path-tracked-file-restore-002.md`.
- Active authorization:
  `PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718`,
  restrictively including only `WI-5474`.
- Work-intent claim: row 32982, kind `go_implementation`, session
  `019f6668-9974-7d72-a456-826f9a67e627`.
- Implementation-start schema: v3.
- Implementation-start packet hash:
  `sha256:64ecc4d59da1bfccdee84edaf70038428df2b8e12938d1f134ccd65d31c44e03`.
- Pre-start packet hash:
  `sha256:14f9c75c0f129eae7849a1964c4fa6fabd20e835110abe3b69911c8bee295208`.
- Exact target preflight returned four in-scope targets, zero out-of-scope
  targets, and zero unused targets before implementation and after final
  verification.
- Operation-time validation returned `authorized: true` for each of the four
  target paths immediately before manual mutation and again before mechanical
  formatting.

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

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision carried by the active singleton V2 authorization.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remained
  binding. This implementation did not inspect or mutate dispatcher
  configuration or runtime state.
- No new owner decision is required. This report requests only independent
  implementation verification.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes the
  bounded defect-repair carrier while retaining all later gates.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - freezes
  dispatcher-configuration mutation; this source/test-only implementation is
  outside that held surface.
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md` - independently
  VERIFIED package baseline extended by this implementation.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md` - approved
  implementation proposal.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-002.md` - independent GO
  authorizing the exact four-file implementation.

## Spec-to-Test Mapping

| Specification | Executed verification | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Claim/start/target preflights, exact numbered chain check, governed report helper | PASS: latest pre-report state remained GO v002; the report advances append-only to v003. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `test_git_lifecycle_exact_restore.py` through `python -m groundtruth_kb.git_lifecycle` | PASS: production CLI/service/repository boundaries perform the operation; tests use raw Git only for fixture setup and assertions. |
| `GOV-WORK-TREE-HYGIENE-001` | Focused success case, denial matrix, mismatch/drift cases, scoped status and diff checks | PASS: exact target restored; unrelated staged/modified/deleted/untracked status and index blobs remain unchanged. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Frozen `test_modernization_git_lifecycle.py` suite | PASS: 2 passed; all pre-existing lifecycle assertions remain green. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Active V2 PAUTH query, claim row 32982, schema-v3 packet, per-path validation | PASS: the exact implementation envelope authorized all four targets. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | V2 authorization inspection | PASS: included work-item set is exactly `["WI-5474"]`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Schema-v3 begin output and exact target-path preflight | PASS: active project, WI, proposal, GO, and target scope match. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `implementation_authorization.py validate` for each target before mutation/formatting | PASS: every validation returned `authorized: true`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Approved proposal/spec carry-forward and applicability preflight evidence | PASS: all approved specification links are carried into this report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, PAUTH, project, WI, and report linkage fields | PASS: all identifiers remain exact and consistent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus both executed pytest suites and static checks | PASS: every linked specification has observed executed evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Integration fixture-root/cleanup checks in the focused suite | PASS: all temporary repositories were in-root and the fixture root was empty after execution. |
| `GOV-STANDING-BACKLOG-001` | Existing WI-5474 and TEST-11572 linkage carried through proposal/GO/report | PASS: no duplicate work item or second backlog authority was created. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI, TEST, PAUTH, numbered proposal/GO/report chain | PASS: all durable implementation evidence has a governed canonical home. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact source/test diff plus this implementation report | PASS: behavior, tests, and lifecycle evidence remain linked. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | GO -> claim -> schema-v3 start -> implementation -> NEW report sequence | PASS: implementation now awaits independent VERIFIED; WI-5474 remains open. |

## Commands Run

1. Exact target-path start and final preflight:
   `groundtruth-kb/.venv/Scripts/python.exe scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --candidate-paths groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py --json`.
   Observed result: `verdict: in_scope`; 4 in scope, 0 out of scope, 0
   unused.
2. Work-intent claim:
   `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5474-exact-path-tracked-file-restore --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 7200`.
   Observed result: row 32982, `claim_kind: go_implementation`.
3. Implementation start:
   `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 40`.
   Observed result: schema v3 packet with hashes recorded above and latest
   status GO.
4. Operation-time authorization, run for each exact target:
   `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target <target>`.
   Observed result for every target: `authorized: true`.
5. Final focused suite:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short`.
   Observed final result: `27 passed, 1 warning in 62.19s`.
6. Final frozen baseline:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short`.
   Observed final result: `2 passed, 1 warning in 192.17s`.
7. Focused lint:
   `groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`.
   Observed result: `All checks passed!`
8. Focused formatting:
   `groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`.
   Observed result: `4 files already formatted`.
9. Compilation:
   `groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`.
   Observed result: exit 0, no output.
10. Diff hygiene:
    `git diff --check -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py`.
    Observed result: exit 0; only Git's advisory LF-to-CRLF worktree
    conversion warnings appeared.

The sole pytest warning in both suites is the existing repository-level
`PytestConfigWarning: Unknown config option: asyncio_mode`; it did not affect
test collection or results.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`
  - SHA-256:
    `A9E7550F6D79139D1C21DB8BF442DD9AC6DD698FA406E6193F6AB2000D759F7F`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`
  - SHA-256:
    `087AAA049928E04DFECB7E88272876A1FD85933D97175654D1EB1463E7B94496`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`
  - SHA-256:
    `ED1375E5FD27D6480DA909A1B679016E080D51CA59641181EC4D8DAA7C329327`
- `platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  - SHA-256:
    `44EE0806ACC1E15871F25832C8F8AA67D5DA9AE0AD2E1C6E98612841C9720943`

Exactly the four declared implementation targets changed. The three tracked
source files add 306 lines; the new focused test module contains 447 lines.
All unrelated dirty paths were excluded.

## Acceptance Criteria Status

- PASS - one command accepts exactly one safe repository-relative path and
  one explicit source ref; repeated path/ref options are denied in live and
  dry-run modes.
- PASS - multi-path denial covers both encoded pathspec/comma/brace/whitespace
  forms and repeated `--path` options, resolving GO observation F7.
- PASS - success requires exactly one unstaged worktree deletion with no
  staged target change.
- PASS - the selected ref resolves to one unambiguous commit and the selected
  path resolves to one regular-file blob before mutation.
- PASS - restored worktree bytes and Git blob equal the selected source blob,
  including restoration from a different explicit commit.
- PASS - the staged-blob index snapshot is byte-for-byte unchanged.
- PASS - every unrelated NUL-delimited status byte remains unchanged.
- PASS - every pre-mutation denial returns a stable actionable code without
  creating the target.
- PASS - byte, index, or unrelated-status postcondition failure removes the
  newly restored target and returns a stable denial.
- PASS - JSON and human-readable output carry the required commit/blob/status
  evidence.
- PASS - the frozen WI-5421 lifecycle baseline remains green.
- PASS - all implementation and verification were confined to the four
  targets and isolated in-root temporary repositories.
- PASS - no live GT-KB restore was executed; scoped status shows only the
  expected source/test implementation changes, resolving GO observation F6.
- PASS - no dispatcher/TAFE configuration or runtime state, Git index/history,
  credential, external system, deployment, or release mutation occurred.

## Risk And Rollback

Residual risk is bounded to concurrent filesystem or Git-state change between
the final refreshed precondition snapshots and the exclusive target creation.
Exclusive create prevents overwriting a concurrently reappearing target;
post-write blob, index, and unrelated-status checks detect later drift. On a
failed postcondition the operation removes only the newly restored target.
It does not attempt to reverse an unrelated concurrent actor's change.

The operation intentionally accepts only regular-file blobs. Symlinks, trees,
submodules, unsafe paths, implicit refs, ambiguous refs, and every target state
other than an unstaged deletion remain denied.

Rollback is a separately governed revert of only the four implementation
targets listed above, followed by both pytest suites and the static checks.
The append-only proposal, GO, report, and future verdict files must not be
rewritten or deleted. No rollback is currently indicated.

## Loyal Opposition Asks

1. Independently verify the implementation against every linked
   specification and the exact executed evidence above.
2. Recompute the four file hashes and confirm only the four approved targets
   are attributable to WI-5474.
3. Confirm the focused success, denial, mismatch, index-drift,
   unrelated-drift, JSON, and human-output cases plus the frozen WI-5421
   baseline.
4. Return `VERIFIED` with atomic commit finalization if all evidence passes;
   otherwise return `NO-GO` with concrete findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
