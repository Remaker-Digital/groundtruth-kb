NO-GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 004
Responds to: bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Verification Verdict - NO-GO - WI-5474 Exact-Path Tracked-File Restore

## Verdict

NO-GO. The implementation is tightly scoped and the focused suite passes, but the path-normalization boundary still crashes on repository-root pseudo-paths `.` and `./.` instead of returning a governed `OperationDenied` denial. This violates the fail-closed exact-path contract for a live restore command intended to protect a dirty GT-KB worktree.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `NO-GO`, a Loyal Opposition verification status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Implementation report author session context: `019f6668-9974-7d72-a456-826f9a67e627`.
- GO reviewer session context: `20dd407b-d159-4c05-9700-63511dadff11`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md --json
```

Result:

- packet_hash: `sha256:22e3f844343f759d7d51e767062b5f81d5a690851dba840a8b4f077870159f97`
- bridge_document_name: `gtkb-wi5474-exact-path-tracked-file-restore`
- content_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md`
- operative_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:bc86718392c0f08583c0dc046a09e860e41b23ff0e19dd5825010c778c607085`

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore
```

Result:

- Bridge id: `gtkb-wi5474-exact-path-tracked-file-restore`
- Operative file: `bridge\gtkb-wi5474-exact-path-tracked-file-restore-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: 0

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-authorized bounded defect-repair envelope carried by the active WI-5474 PAUTH.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher-configuration mutation hold remained binding.
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md` - independently verified git-lifecycle baseline extended by WI-5474.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-002.md` - independent GO authorizing this four-file implementation.

## Specifications Carried Forward

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

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain read and governed verdict preflight | yes | PASS: v003 is latest verifier-actionable report |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Direct normalization repro plus production CLI boundary review | yes | FAIL: root pseudo-paths raise unhandled `IndexError` before governed denial |
| `GOV-WORK-TREE-HYGIENE-001` | Focused restore suite plus direct root-path repro | yes | FAIL: exact-path guard is not fail-closed for `.` and `./.` |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | v003 frozen-baseline evidence review | yes | No independent blocker found |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | v003 claim/start/PAUTH evidence review | yes | No independent blocker found |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | v003 PAUTH evidence review | yes | No independent blocker found |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | v003 target/PAUTH/report metadata review | yes | No independent blocker found |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | v003 implementation-start evidence and target path review | yes | No independent blocker found |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | yes | PASS: `missing_required_specs=[]` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, PAUTH, project, WI, and report linkage | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --dry-run --json` | yes | `verified_overall=false`; several linked specs have no derived tests |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path review | yes | PASS: changed paths are in-root |
| `GOV-STANDING-BACKLOG-001` | WI/report/test linkage review | yes | No independent blocker found |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Report and durable evidence review | yes | Blocked by exact-path denial defect |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Source/test/report traceability review | yes | Blocked by missing root pseudo-path regression |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge lifecycle review | yes | PASS; latest remains verifier-actionable until this verdict |

## Positive Confirmations

- Bridge chain is coherent: v001 `NEW`, v002 `GO`, v003 implementation-report `NEW`.
- Applicability preflight passes with `missing_required_specs: []`.
- Mandatory clause preflight passes with zero blocking gaps.
- Focused restore suite passes: `27 passed`.
- Ruff check passes on all four implementation targets.
- Ruff format check passes on all four implementation targets.
- The implementation is bounded to the approved four targets: three modified source files plus one new focused test module.

## Findings

### F1 - P1 - Repository-root pseudo-paths crash instead of returning stable governed denial

Observation: `normalize_repo_path()` strips leading `./` segments at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:17` through `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:19`, then constructs `Path(raw)` at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:20`. The first guard checks `not raw`, absoluteness, and `..` at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:21` through `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:22`, but root pseudo-path `.` remains truthy and has no parts. The next guard indexes `path.parts[0]` at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py:23`, producing an unhandled `IndexError`.

Independent reproduction:

```text
. IndexError tuple index out of range
./. IndexError tuple index out of range
./ OperationDenied unsafe_scope_path
././ OperationDenied unsafe_scope_path
bridge/target.md => bridge/target.md
```

Deficiency rationale: The implementation report claims safe path normalization rejects unsafe, pathspec-like, whitespace, comma/brace, and multi-path forms at `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md:30` through `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md:35`, and its acceptance section claims multi-path and unsafe denial coverage at `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md:208` through `bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md:212`. The actual parameterized unsafe-path coverage at `platform_tests/scripts/test_git_lifecycle_exact_restore.py:182` through `platform_tests/scripts/test_git_lifecycle_exact_restore.py:195` omits `.` and `./.`. Because `restore_deleted_path()` calls `normalize_repo_path()` before any Git-status or blob checks at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py:169` through `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py:173`, these inputs bypass the governed `OperationDenied` path. The production CLI catches `OperationDenied` at `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py:248` through `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py:250`, but it does not catch this `IndexError`.

Impact: A live restore attempt with `--path .` or `--path ./.` is not a safe denial with machine-readable code and no surprise traceback/exit mode. For a command intended to unlock governed restoration of tracked bridge deletions in a dirty repository, the exact-path boundary must be closed on every root-ish or multi-target spelling.

Required revision: treat any normalized path with no concrete file component, including `.` and `./.`, as `OperationDenied("unsafe_scope_path", ...)` before indexing `path.parts[0]`. Add those cases to `test_cli_denies_unsafe_or_multipath_input()` and, ideally, a direct unit-level regression for `normalize_repo_path()`.

## Required Revisions

1. Fix `normalize_repo_path()` so `Path(".")` and any stripped root pseudo-path are denied as `unsafe_scope_path`, not allowed to raise `IndexError`.
2. Add focused tests for `.`, `./.`, and any equivalent root-ish spelling that previously produced an empty `path.parts`.
3. Rerun the focused restore suite, Ruff check, Ruff format check, applicability preflight, clause preflight, and spec-derived dry run; refresh the implementation report evidence.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5474-exact-path-tracked-file-restore --format json --preview-lines 50
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --content-file bridge/gtkb-wi5474-exact-path-tracked-file-restore-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore --dry-run --json
python -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
in-memory Python reproduction of normalize_repo_path(Path('.').resolve(), case) for '.', './.', './', '././', and 'bridge/target.md'
git status --short -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py bridge/gtkb-wi5474-exact-path-tracked-file-restore-*.md
```

Observed key outputs:

```text
Applicability preflight: preflight_passed=true; missing_required_specs=[]; blocking_errors=[]
Clause preflight: Blocking gaps (gate-failing): 0
Spec-derived dry run: verified_overall=false
Focused pytest: 27 passed
Ruff check: All checks passed!
Ruff format: 4 files already formatted
Root pseudo-path repro: '.' and './.' raise IndexError tuple index out of range
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, gtkb-verify
