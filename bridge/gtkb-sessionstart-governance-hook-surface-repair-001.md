NEW

# gtkb-sessionstart-governance-hook-surface-repair - SessionStart Governance Hook Surface Repair

bridge_kind: prime_proposal
Document: gtkb-sessionstart-governance-hook-surface-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC

author_identity: Prime Builder/Codex
author_harness_id: A
author_session_context_id: 019ed175-c0c5-70a0-a9ef-439e3c514b2e
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, Default collaboration mode

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4575

target_paths: [".claude/hooks/turn-marker.py", ".claude/hooks/delib-preflight-gate.py", ".claude/settings.json", ".codex/gtkb-hooks/turn-marker.py", ".codex/gtkb-hooks/delib-preflight-gate.py", ".codex/hooks.json", "groundtruth-kb/templates/hooks/turn-marker.py", "groundtruth-kb/templates/hooks/delib-preflight-gate.py", "groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py", "groundtruth-kb/tests/test_doctor_adoption_drift.py", "platform_tests/scripts/test_fab09_safety_gate_registration.py"]

implementation_scope: governance hook/settings/doctor repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the SessionStart governance hook surface flagged by the June 15 Loyal Opposition advisory by reconciling the expected managed-artifact contract for `turn-marker.py` and `delib-preflight-gate.py` against the current repository state, doctor checks, settings registrations, and focused tests.

The implementation must not blindly resurrect retired stubs. Current evidence is contradictory: the June 15 advisory says the registry and SessionStart path expect `turn-marker.py` and `delib-preflight-gate.py`, while current platform tests assert those hook files and template twins are intentionally absent as retired dead stubs. This proposal authorizes an evidence-first repair: if the live managed-artifact registry or doctor implementation still requires these hooks, restore the missing files and settings registrations coherently; if the current retirement contract is authoritative, remove or update stale settings/doctor/test expectations so `gt project doctor` no longer reports retired hooks as missing governance surface.

Acceptance criteria:

- The project has exactly one explicit contract for `turn-marker.py` and `delib-preflight-gate.py`: either managed-present-and-registered, or retired-and-absent-from managed artifacts, settings registrations, doctor expectations, and active hook parity tests.
- The `.claude` and `.codex` governance hook surfaces agree with that contract where Codex parity is applicable.
- The affected `gt project doctor` managed-artifact/settings-hook checks pass or no longer emit findings for retired hooks.
- Focused tests listed below pass, and any remaining full doctor timeout or unrelated doctor failure is reported separately with evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected hook, settings, source, and test files require bridge-mediated authorization before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites the governing specifications and maps verification to those specifications before requesting `GO`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata required by the implementation-start gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must execute tests derived from the linked specs before a `VERIFIED` outcome.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4575 is an active reliability-fix backlog item under `PROJECT-GTKB-RELIABILITY-FIXES`; scope is limited to small hook/settings/doctor/test repair.
- `GOV-STANDING-BACKLOG-001` - WI-4575 is tracked in the durable MemBase backlog; this proposal does not perform a bulk standing-backlog operation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Changes to `.codex` hook parity or hook-registration expectations must preserve the Windows Codex fallback contract.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are in-root under the GT-KB project root and no Agent Red lifecycle-independent repository paths are touched.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - Doctor and managed-artifact enforcement must reflect the governance capabilities GT-KB expects adopters and hosted workflows to carry.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Any repaired governance surface must have governed test evidence before being treated as release-ready.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The advisory contradiction and repair decision are preserved as a durable bridge artifact rather than being handled as untracked chat-only work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix must keep registry, settings, hook files, doctor checks, and tests traceable as one artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The implementation must explicitly resolve whether the two hooks are active or retired rather than leaving them in a mixed lifecycle state.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-15-16-18-LO-HYGIENE-ASSESSMENT-advisory.md` - June 15 advisory claims missing `turn-marker.py` and `delib-preflight-gate.py` settings registrations and managed-artifact expectations, specifically citing its lines 17, 79, 161, and 221.
- `bridge/gtkb-hourly-quality-scout-advisory-001.md` - Earlier advisory reports the opposite repair direction: these two hook scripts were deleted from templates but allegedly remained in `managed-artifacts.toml`, recommending registry/settings prune.
- `bridge/gtkb-da-governance-completeness-implementation-017.md` and related governance-completeness bridge history - The two hooks entered the governance hook surface as part of the DA/governance completeness workstream.
- `commit 182665e81` - Tracked deletion of `.claude/hooks/turn-marker.py`, `.claude/hooks/delib-preflight-gate.py`, and their `groundtruth-kb/templates/hooks/` template twins, plus settings/registry/test updates.
- `WI-4575` - MemBase reliability item for doctor-hygiene repairs, including stale `turn-marker`/`delib-preflight-gate` managed-artifact cleanup, under `PROJECT-GTKB-RELIABILITY-FIXES`.

## Owner Decisions / Input

Mike instructed in this session on 2026-06-16: "Proceed with bridge proposal for restoring/repairing the SessionStart governance hook surface." That authorizes filing this implementation proposal. It does not authorize direct protected-file implementation without a Loyal Opposition `GO` verdict and a successful `python scripts/implementation_authorization.py begin --bridge-id gtkb-sessionstart-governance-hook-surface-repair` packet.

## Requirement Sufficiency

Existing requirements sufficient.

The repair is a bounded reliability/governance-surface reconciliation under the cited bridge authority, project-linkage, hook-parity, lifecycle, doctor/adoption, and governed-testing specifications. No new or revised requirement is needed before implementation because the desired end state is not a new behavior contract; it is restoration of a single coherent contract across managed artifacts, live hook/settings surfaces, doctor checks, and focused tests.

## Implementation Plan

1. Re-inspect `groundtruth-kb/templates/managed-artifacts.toml`, `.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/`, `.codex/gtkb-hooks/`, and `groundtruth-kb/templates/hooks/` for any live `turn-marker.py` or `delib-preflight-gate.py` expectations.
2. Re-inspect `scripts/session_start_dispatch_core.py` and doctor code/tests to confirm whether SessionStart behavior really expects these two hooks or whether the June 15 advisory cited stale line references.
3. Choose the narrower repair that makes the current authoritative contract coherent:
   - Restoration path: recreate active hook files/template twins and register them in the correct settings event(s) only if live registry/doctor/session-start code proves they remain required.
   - Retirement path: remove stale doctor/test/comment/registration expectations and preserve tests asserting the hooks are retired only if the current registry/tests prove retirement is authoritative.
4. Keep `.claude` and `.codex` surfaces aligned where Codex parity applies; do not create no-op stub governance hooks that only satisfy file-existence checks.
5. Update focused tests to encode the chosen contract and prevent reintroducing the mixed state.

## Spec-Derived Verification Plan

| Specification | Verification command or check | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-sessionstart-governance-hook-surface-repair` after `GO` | PASS packet authorizing only the declared `target_paths` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sessionstart-governance-hook-surface-repair` | `preflight_passed: true`, no missing required specs |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Review changed paths plus `git diff --name-only` | All changed paths remain in-root under the GT-KB checkout |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Inspect and, if changed, run focused Codex hook parity tests/checker for `.codex/hooks.json` and `.codex/gtkb-hooks` | `.codex` surface either matches the restored hook contract or deliberately has no retired-hook expectation |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-STANDING-BACKLOG-001` | Confirm implementation touches only this proposal's small reliability target set and does not mutate MemBase backlog/PAUTH rows | No bulk backlog operation; no KB mutation |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python -m pytest groundtruth-kb/tests/test_managed_registry.py -q --tb=short` | PASS; managed-artifact registry encodes one coherent active/retired contract |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python -m pytest platform_tests/scripts/test_fab09_safety_gate_registration.py -q --tb=short` | PASS; active hook implementation and retired-hook absence assertions match chosen lifecycle state |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest groundtruth-kb/tests/test_doctor.py -q --tb=short -k "settings_hook_registration or managed_artifact or managed_registry"` | PASS; focused doctor tests no longer encode a mixed-state expectation |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | Run the affected `gt project doctor` check path, preferably `gt project doctor --json` with a bounded timeout and/or the narrow doctor helper tests above | PASS for affected managed-artifact/settings-hook checks; unrelated timeout/failure, if any, documented separately |
| Python quality gates | `python -m ruff check <changed .py files>` and `python -m ruff format --check <changed .py files>` when Python files change | PASS |
| General diff hygiene | `git diff --check` | PASS |

## Risk / Rollback

Primary risk is repairing in the wrong direction: resurrecting retired dead stubs would create false-green governance instrumentation, while pruning a real SessionStart expectation would hide a governance gap. The mitigation is evidence-first reconciliation against live registry rows, settings files, SessionStart code, doctor checks, and tests before choosing restoration or retirement.

Rollback is a single implementation-commit revert. If restoration is chosen and later rejected, restore the current retirement contract from the pre-implementation tree. If retirement is chosen and later rejected, restore the deleted hook/template files from `182665e81^` and reintroduce their managed-artifact/settings registrations in one coherent change.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-sessionstart-governance-hook-surface-repair`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - this repairs drift in an existing governance/doctor hook surface and does not introduce a new feature surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
