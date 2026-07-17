NEW
::init gtkb lo
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5366-agent-red-frontend-gate-paths - 005

bridge_kind: implementation_report
Document: gtkb-wi5366-agent-red-frontend-gate-paths
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5366-agent-red-frontend-gate-paths-004.md
Approved proposal: bridge/gtkb-wi5366-agent-red-frontend-gate-paths-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5366

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

target_paths: ["scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

Recommended commit type: fix:

## Implementation Claim

The release-candidate frontend lane now routes its widget test/build and all
three admin builds to the real packages below `applications/Agent_Red`.
`_frontend_gates()` uses one explicit Agent Red root, one widget package, and
three explicit admin package paths instead of inferring package role from
legacy root-relative strings. The existing one-time PowerShell sync command,
admin-only `npm_config_ignore_scripts=true`, and fail-closed subprocess
behavior are preserved.

The focused test now proves the exact ordered six-command sequence and the
admin-only environment override. No package, dependency, credential, bridge
file, dispatcher setting, or application source was created or changed.

Post-implementation SHA-256 at stable HEAD
`5d79c10d9232d34fc828e71fe8268969d131b70d`:

| Path | SHA-256 |
| --- | --- |
| `scripts/release_candidate_gate.py` | `64CB7384689FB61568F4AAA6DAD083B4F6BF2B86010A71808020BDD74B161C00` |
| `platform_tests/scripts/test_release_candidate_gate.py` | `9A6376C5A7D49DE97CCBCD2B78AE0D847D87F75888EF116BD1D09D9C7D7697D0` |

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Owner Decisions / Input

No new owner decision is required. The active Assurance project PAUTH and
independent GO authorize this exact two-file path correction. The owner
requires acceptance evidence, preservation of concurrent dirt, no direct
harness contact, and no harness impairment; this implementation satisfies
those boundaries.

## Prior Deliberations

- `bridge/gtkb-wi5366-agent-red-frontend-gate-paths-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5366-agent-red-frontend-gate-paths-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`; `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Stable-head focused module passed `33/33`; the strengthened test asserts the exact widget test/build, sync, and three admin-build command sequence. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Ruff, format, and `git diff --check` passed. The diff contains only the approved frontend function and focused test hunks; missing-tool failure coverage remains green. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | All four package manifests were found below `applications/Agent_Red`; no root package or compatibility fallback was added. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Current diff is limited to `23` insertions and `23` deletions in the two approved paths; no neighboring WI-5165 or WI-5381 path is included. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `GOV-STANDING-BACKLOG-001` | WI-5366 remains linked to proposal, GO, implementation report, tests, and exact hashes. The separate missing application-local sync/build surface remains owned by WI-5381. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Claim acquired at `2026-07-17T17:43:19Z`; implementation-start packet finalized at `2026-07-17T17:43:42Z` for exactly the two target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Stable-current-head pytest, Ruff, format, diff, and package-manifest evidence are included below for independent rerun. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short --timeout=300`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/release_candidate_gate.py platform_tests/scripts/test_release_candidate_gate.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/release_candidate_gate.py platform_tests/scripts/test_release_candidate_gate.py`
- `git diff --check -- scripts/release_candidate_gate.py platform_tests/scripts/test_release_candidate_gate.py`
- `Get-Item` for the widget and three admin `package.json` paths below `applications/Agent_Red`
- `Get-FileHash -Algorithm SHA256` for both approved target files

## Observed Results

- Stable-head pytest: `33 passed, 1 warning in 81.54s`; HEAD start and end both
  `5d79c10d9232d34fc828e71fe8268969d131b70d`.
- Ruff lint: `All checks passed!`
- Ruff format: `2 files already formatted`.
- `git diff --check`: exit `0`; only line-ending conversion warnings.
- Package manifests present:
  `applications/Agent_Red/widget/package.json`,
  `applications/Agent_Red/admin/standalone/package.json`,
  `applications/Agent_Red/admin/provider/package.json`, and
  `applications/Agent_Red/admin/shopify/package.json`.
- The earlier `33/33` pass whose HEAD changed during execution is intentionally
  excluded from acceptance evidence.

## Files Changed

- `platform_tests/scripts/test_release_candidate_gate.py`
- `scripts/release_candidate_gate.py`

Excluded out-of-scope dirty paths: 1565.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this corrects stale package paths in an existing
  release gate and its focused regression test.

```text
     .../scripts/test_release_candidate_gate.py         | 24 +++++++++++++---------
     scripts/release_candidate_gate.py                  | 22 ++++++++------------
     2 files changed, 23 insertions(+), 23 deletions(-)
```

## Acceptance Criteria Status

- [x] Widget test/build and all three admin builds address real packages below
  `applications/Agent_Red`.
- [x] The focused test proves the complete ordered six-command lane.
- [x] Environment sync remains exactly once and all three admin build
  environments carry `npm_config_ignore_scripts=true`.
- [x] Existing missing-npm and command-failure behavior remains fail closed.
- [x] No root package, fallback path, dependency installation, or skip was
  introduced.
- [x] Focused tests, Ruff, format, diff hygiene, hashes, and manifest checks
  pass at a stable current HEAD.
- [x] The implementation diff is limited to the approved hunks in two paths.
- [ ] Independent Loyal Opposition must return VERIFIED.

## Risk And Rollback

The real frontend build is not claimed as passing in this report. WI-5381
already owns the missing application-local `scripts/sync-admin-env.ps1` and
broader Agent Red build/dependency self-containment. Running the current root
sync script would target nonexistent root `admin/*` directories and consume
credential-bearing `.env.local`; it was deliberately not executed here.

Rollback must revert only these WI-5366 source and test hunks through a
separately governed transaction. Preserve every WI-5165/WI-5381/concurrent
hunk, application package, database row, bridge version, staged entry, and
unrelated worktree byte.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
