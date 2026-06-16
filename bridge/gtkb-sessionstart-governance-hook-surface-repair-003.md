NEW

# gtkb-sessionstart-governance-hook-surface-repair - Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-sessionstart-governance-hook-surface-repair
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC

author_identity: Prime Builder/Codex
author_harness_id: A
author_session_context_id: 2026-06-16T19-15-17Z-prime-builder-A-519acd
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, bridge auto-dispatch

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4575

Responds to GO: bridge/gtkb-sessionstart-governance-hook-surface-repair-002.md
Approved proposal: bridge/gtkb-sessionstart-governance-hook-surface-repair-001.md
Recommended commit type: fix:

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

implementation_scope: governance hook/settings/doctor contract reconciliation
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implemented the retirement-path repair. Live registry/settings/source inspection showed no active runtime or managed-artifact requirement for `turn-marker.py` or `delib-preflight-gate.py`; the remaining mixed-state evidence was stale count/comment/test-label text that still described those retired hooks as active governance hook additions.

The implementation makes the explicit managed-artifact and focused-test contract consistent:

- `groundtruth-kb/templates/managed-artifacts.toml` now states the actual manifest counts: 63 records, 19 hooks, and 14 settings-hook-registration records.
- `groundtruth-kb/tests/test_managed_registry.py` now describes the active 14-row settings registration matrix and states that retired dead-stub hooks/registrations remain absent.
- `groundtruth-kb/tests/test_doctor.py` now names the active `gov09-capture.py` settings-registration tests correctly instead of using stale `turn_marker` labels.

No hook files were restored. No `.claude/settings.json`, `.codex/hooks.json`, `.codex/gtkb-hooks`, `.claude/hooks`, doctor implementation code, or platform absence assertions were changed by this implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

Carried forward from the approved proposal: Mike instructed on 2026-06-16, "Proceed with bridge proposal for restoring/repairing the SessionStart governance hook surface."

Implementation-start authorization was created after the Loyal Opposition `GO`:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-sessionstart-governance-hook-surface-repair
```

Observed result: PASS. Packet hash `sha256:7f59099179e7575b101068d2d1c540bf8087a832e53faaa9496617bde142558c`; latest bridge status `GO`; authorization target globs matched the approved proposal.

No new owner decision, waiver, KB mutation, or scope expansion was required.

## Prior Deliberations

- `bridge/gtkb-sessionstart-governance-hook-surface-repair-001.md` - approved implementation proposal with the evidence-first restoration-vs-retirement decision path.
- `bridge/gtkb-sessionstart-governance-hook-surface-repair-002.md` - Loyal Opposition `GO` verdict authorizing implementation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-15-16-18-LO-HYGIENE-ASSESSMENT-advisory.md` - advisory that triggered this reconciliation.
- `bridge/gtkb-hourly-quality-scout-advisory-001.md` - prior advisory pointing toward retired-hook cleanup.
- `commit 182665e81` - historical deletion of the retired hook/template files and related settings/registry/test updates.
- `WI-4575` - reliability-fix work item under `PROJECT-GTKB-RELIABILITY-FIXES`.

## Specification-Derived Verification Plan

| Specification / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-sessionstart-governance-hook-surface-repair` passed with packet hash `sha256:7f59099179e7575b101068d2d1c540bf8087a832e53faaa9496617bde142558c`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-sessionstart-governance-hook-surface-repair` passed with `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- <approved target paths>` reported only in-root target files changed by this implementation: `groundtruth-kb/templates/managed-artifacts.toml`, `groundtruth-kb/tests/test_doctor.py`, and `groundtruth-kb/tests/test_managed_registry.py`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `rg -n --hidden --no-ignore "turn_marker\|delib_preflight\|turn-marker\|delib-preflight-gate" ...` found no `.codex` hook/settings references and no active `.claude` settings references; no Codex hook parity surface was changed. |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-STANDING-BACKLOG-001` | Implementation touched only three approved target files and did not mutate MemBase backlog or project authorization records. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_managed_registry.py -q --tb=short -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-managed` passed: 27 passed. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab09_safety_gate_registration.py -q --tb=short -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-platform` passed: 25 passed. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor.py -q --tb=short -k "settings_hook_registration or managed_artifact or managed_registry" -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-doctor` passed: 5 passed, 32 deselected. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | `gt project doctor --json` returned overall `fail` due unrelated pre-existing hygiene/SoT/backlog findings, but in-scope checks passed: `Hooks`, `File Bridge State`, `safety-gate-registration`, `capture-hook-stub-status`, and active settings registrations for `spec-event-surfacer.py`, `gov09-capture.py`, and `owner-decision-capture.py`. |
| Python quality gates | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py` passed. `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py` passed after formatting the two edited test files. |
| General diff hygiene | `git diff --check` passed. |
| Clause-test gate | `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-sessionstart-governance-hook-surface-repair` exited 0 with 0 blocking gaps. |

## Commands Run

```text
gt harness roles
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-sessionstart-governance-hook-surface-repair --format json --preview-lines 400
gt bridge dispatch status
gt bridge dispatch health
python scripts\implementation_authorization.py begin --bridge-id gtkb-sessionstart-governance-hook-surface-repair
rg -n --hidden --no-ignore "turn-marker|delib-preflight-gate" .claude .codex groundtruth-kb\templates groundtruth-kb\src\groundtruth_kb\project groundtruth-kb\tests platform_tests\scripts scripts
rg -n --hidden --no-ignore "turn_marker|delib_preflight|turn-marker|delib-preflight-gate" groundtruth-kb\templates\managed-artifacts.toml groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py platform_tests\scripts\test_fab09_safety_gate_registration.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_managed_registry.py -q --tb=short -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-managed
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab09_safety_gate_registration.py -q --tb=short -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-platform
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor.py -q --tb=short -k "settings_hook_registration or managed_artifact or managed_registry" -o addopts= --basetemp .gtkb-state\pytest-tmp-sessionstart-doctor
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_doctor.py
git diff --check
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-sessionstart-governance-hook-surface-repair
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-sessionstart-governance-hook-surface-repair
gt project doctor --json
```

Initial attempts using the system `python` failed before exercising the repo gates because `pytest` and `ruff` are not installed in that interpreter. Initial pytest attempts that used the host temp directory also failed with sandbox `PermissionError`; the final verification reran with explicit `.gtkb-state` basetemp paths and passed.

## Observed Results

- Bridge/dispatcher state: harness A resolved as active `prime-builder`; dispatcher health PASS; selected thread latest status `GO`.
- Implementation authorization: PASS, packet hash `sha256:7f59099179e7575b101068d2d1c540bf8087a832e53faaa9496617bde142558c`.
- Search after edits: retired hook names remain only in `platform_tests/scripts/test_fab09_safety_gate_registration.py` absence assertions.
- Managed registry tests: 27 passed.
- FAB-09 safety gate registration tests: 25 passed.
- Doctor focused tests: 5 passed, 32 deselected.
- Ruff lint: all checks passed.
- Ruff format check: 2 files already formatted.
- Diff hygiene: passed.
- Applicability preflight: `preflight_passed: true`; no missing required or advisory specs.
- Clause preflight: exit 0; 0 blocking gaps.
- Doctor JSON: overall fail from unrelated pre-existing project hygiene findings; in-scope hook/settings checks passed.

## Files Changed

Implementation-scoped changed files:

- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/tests/test_managed_registry.py`
- `groundtruth-kb/tests/test_doctor.py`

The broader worktree contains many unrelated staged and unstaged changes from other active bridge/work streams. This report intentionally excludes those from the implementation claim. A targeted diff check for this bridge's approved target paths reported only the three files above as this implementation's unstaged changes; staged target-file changes in `.claude/settings.json`, `.codex/hooks.json`, and `groundtruth-kb/src/groundtruth_kb/project/doctor.py` pre-existed this dispatch and were not modified for this repair.

Diff stat for the implementation-scoped files:

```text
groundtruth-kb/templates/managed-artifacts.toml | 10 +++----
groundtruth-kb/tests/test_doctor.py             |  6 ++--
groundtruth-kb/tests/test_managed_registry.py   | 39 ++++++++++++-------------
3 files changed, 26 insertions(+), 29 deletions(-)
```

## Acceptance Criteria Status

- [x] The project has one explicit contract for `turn-marker.py` and `delib-preflight-gate.py`: retired and absent from managed artifacts, settings registrations, doctor expectations, and active hook parity surfaces.
- [x] `.claude` and `.codex` hook surfaces agree with that contract for this scope: neither surface registers or requires the retired hooks.
- [x] Affected doctor managed-artifact/settings-hook checks do not emit findings for the retired hooks; active registration checks pass for `spec-event-surfacer.py`, `gov09-capture.py`, and `owner-decision-capture.py`.
- [x] Focused tests passed. Full `gt project doctor --json` still reports unrelated pre-existing failures, documented above.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: this repairs stale governance/doctor hook-surface contract text and test labels without adding a new capability.

## Risk And Rollback

Residual risk is low because the implementation did not restore or remove runtime hook files. It corrected stale manifest/test language to match the already-active retirement contract and preserved the platform tests that assert the retired hook files and template twins remain absent.

Rollback is a normal revert of the three implementation-scoped files. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the retirement-path repair satisfies the GO'd acceptance criteria.
2. Treat unrelated worktree changes and unrelated `gt project doctor --json` failures as out of scope for this verification unless they directly contradict the three implementation-scoped files or the retired-hook contract.
