GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via current owner transcript role assignment

# Loyal Opposition Revised Proposal Review - GO - WI-5474 Exact-Path Restore Fail-Closed Completion

bridge_kind: lo_verdict
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 006
Responds to: bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474
Recommended commit type: fix

## Verdict

GO. Version 005 is approved as a revised proposal for one narrow correction to the previously NO-GO exact-path restore implementation: root-only repository pseudo-path inputs such as `.` and `./.` must return a governed `OperationDenied("unsafe_scope_path", ...)` denial through the production CLI instead of reaching `Path.parts[0]` and raising `IndexError`.

This is a proposal-review GO, not VERIFIED. The existing candidate implementation remains unverified until Prime Builder files a fresh implementation report after implementing the v005 correction under a new exact claim and implementation-start packet. This GO does not authorize running the restore operation against the live GT-KB worktree or restoring the 17 currently deleted tracked bridge predecessors.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict was `REVISED` at `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`, which is Loyal-Opposition-actionable. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 005 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent. This verdict reviews Prime Builder's v005 revision, not this session's earlier v004 NO-GO text as its own work product.

## Review Findings

### F1 - v005 addresses the sole v004 blocker

Severity: confirmation.

Version 004 rejected the implementation only because repository-root pseudo-paths `.` and `./.` crashed with `IndexError` instead of returning a governed denial. Version 005 accepts that finding, narrows the correction to `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py` and `platform_tests/scripts/test_git_lifecycle_exact_restore.py`, preserves `__main__.py` and `service.py` byte-for-byte, and requires tests through the production CLI boundary for `.`, `./.`, and equivalent root-only spellings.

The current live candidate bytes still reproduce the defect, which is the expected pre-implementation state for this proposal:

```text
groundtruth-kb\.venv\Scripts\python.exe -c "... normalize_repo_path(root, raw) ..."
. IndexError tuple index out of range
./. IndexError tuple index out of range
././ OperationDenied scope path must be repository-relative
././bridge -> bridge
```

### F2 - The correction is bounded and does not authorize live restoration

Severity: confirmation.

The target envelope remains the original four files, but v005 explicitly limits the correction work to the normalization guard and focused tests, preserves the two non-correction implementation targets, and forbids dispatcher configuration/runtime changes, TAFE state mutation, leases, harness roles, credentials, MemBase mutation, Git staging/history/push, deployment, release, and live GT-KB restore execution.

`git ls-files --deleted -- bridge` currently reports 17 deleted tracked bridge predecessor files. That confirms the cleanup need, but v005 correctly does not attempt to authorize their restoration. It authorizes only the source/test correction after GO; restoration of those 17 files must remain a later governed operation using the verified restore surface.

### F3 - Existing non-blocking evidence supports the revision boundary

Severity: confirmation.

The pre-existing exact-restore suite remains green before the correction, and the frozen modernization Git-lifecycle module also passes. These checks do not verify the unimplemented v005 fix, but they establish the baseline that Prime Builder must preserve when adding the root-only denial guard.

Observed results:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short
27 passed, 1 warning in 49.60s

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
2 passed, 1 warning in 200.85s

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
4 files already formatted
```

`python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --dry-run --json` still returned `verified_overall=False` and selected no tests. I treat this as runner-discovery debt, not as a proposal GO blocker; it remains relevant to final VERIFIED evidence and overlaps the active WI-5630 discovery repair thread.

## Conditions On GO

1. Implement only the v005 root-only/no-concrete-component guard and the focused tests needed to prove governed `unsafe_scope_path` denial through the production CLI boundary.
2. Preserve `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py` and `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py` byte-for-byte unless the fresh implementation report proves a separately authorized necessity.
3. Do not run `restore-deleted-path` against the live GT-KB checkout and do not restore the 17 deleted tracked bridge files under this GO.
4. The implementation report must include fresh exact claim and implementation-start evidence, direct proof that `.`, `./.`, and equivalent root-only spellings return JSON code `unsafe_scope_path` with no traceback and no mutation, the full exact-restore suite, the modernization Git-lifecycle module, Ruff check, Ruff format check, py_compile, git diff check, applicability preflight, and mandatory clause preflight.
5. VERIFIED must remain hunk-focused and must not whole-file-finalize unrelated existing dirty bytes in the four-file envelope.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md --json`
Exit code: 0

- packet_hash: `sha256:39543aeb95533ff1fa7b77f66789083bd57eb6d42ba6de555f774ad4650b5942`
- live operative packet hash also observed: `sha256:ae36581cdc12f1200c2c0cf02189829419bd0e72c2ccd58850ccb2cc8ecf7dd5`
- candidate_evidence_hash: sha256:0cae23e2b4ee30a4625dd3bfddd67dc3c8a9fc740ee6620014b02f75a6a78b0c
- bridge_document_name: `gtkb-wi5474-exact-path-tracked-file-restore`
- content_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`
- operative_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`, `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`, `platform_tests/scripts/test_git_lifecycle_exact_restore.py`]

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md`
Exit code: 0

- Bridge id: `gtkb-wi5474-exact-path-tracked-file-restore`
- Operative file: `bridge\gtkb-wi5474-exact-path-tracked-file-restore-005.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

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

## Prior Deliberations And Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md`
- `TEST-11572`

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5578-provider-verdict-status-consistency-recovery --format json --preview-lines 60
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5474-exact-path-tracked-file-restore --format json --preview-lines 100
Get-FileHash bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md -Algorithm SHA256
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md
gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718 --json
gt backlog show WI-5474 --json
groundtruth-kb\.venv\Scripts\gt.exe tests show TEST-11572 --json
groundtruth-kb\.venv\Scripts\python.exe -c "... normalize_repo_path(root, raw) ..."
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --dry-run --json
git ls-files --deleted -- bridge
```

## Owner Decisions / Input

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
