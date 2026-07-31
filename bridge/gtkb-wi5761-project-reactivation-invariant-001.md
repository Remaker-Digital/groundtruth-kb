NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker; manual dispatch per DELIB-202667523/531/533; resolved role prime-builder

# Implementation Proposal — Project Reactivation Invariant: `completed_at` Cleared Only by Owner-Evidenced Reactivation

Document: gtkb-wi5761-project-reactivation-invariant
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-30 UTC
Status: NEW

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5761

target_paths: ["scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/project_reactivation_audit.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_project_reactivation_invariant.py"]

All target paths are inside `E:\GT-KB` per `.claude/rules/project-root-boundary.md`; no out-of-root path is created, read as a live dependency, updated, verified, or required by this proposal.

This proposal performs no MemBase mutation during filing: every `current_projects` row discussed below (including the Authority Foundations v3 row) is cited as read-only evidence, and filing this proposal creates or modifies no project row, specification, deliberation, or work item. This filing carries no approval evidence and requests none at filing time: it is not implementation authorization, and implementation begins only after a Loyal Opposition `GO` plus a fresh implementation-start authorization packet created via `scripts/implementation_authorization.py begin`.

## Problem

Operation-time project-authorization evaluation treats `project.status == "active"` as sufficient even when the active project row retains a non-null `completed_at` timestamp inherited from a prior retirement. A status-only reactivation write therefore becomes mechanically implementation-eligible without any owner-evidenced reactivation record.

Defect surfaces (verified against the working tree on 2026-07-30):

1. **Evaluation side** — `scripts/implementation_authorization.py`:
   - `_project_status` (lines 1176–1182) selects only `status` from `current_projects`.
   - `_project_is_active` (lines 1185–1186) is exactly `status == "active"`.
   - `validate_project_authorization_row` (lines 1295–1300) accepts any `status == "active"` project without inspecting `completed_at` or reactivation evidence.
2. **Write side** — `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:
   - `update_project` (lines 219–295) carries forward every unspecified field from the current row (`values = {field: fields.get(field, current.get(field)) ...}`, line 250). A status-only `terminal -> active` update silently preserves the stale `completed_at`.
   - `retire_project` (lines 992–1006) stamps `completed_at` on retirement, so every retire-then-status-only-reactivate sequence produces a scarred active row.
3. **CLI side** — `groundtruth-kb/src/groundtruth_kb/cli.py` `projects_update` (lines 5956–6034) filters out `None` option values (line 6013), so `gt projects update` cannot clear `completed_at` at all today: there is no owner-facing surface capable of performing a clean reactivation even deliberately.

The canonical operation-time PAUTH evaluator module `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py` was inspected and does not read `current_projects` rows; the project-active predicate lives solely in `scripts/implementation_authorization.py`, which is therefore the evaluation-side enforcement point.

## Live Evidence

`current_projects` (read 2026-07-30, read-only): `PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS` version 3 has `status: active` with `completed_at: 2026-07-29T06:08:54Z`, changed at `2026-07-29T10:03:20+00:00` by `prime-builder/codex/A` after the v2 retirement. This is the live instance named by the source advisory: the row is mechanically eligible to the implementation-start gate while its completion provenance remains contradictory and the recovery thread's owner decision is still pending.

Source advisory: `bridge/gtkb-lo-active-project-completion-state-enforcement-advisory-001.md` (ADVISORY, classification `adapt`, Loyal Opposition Codex/A, 2026-07-29). WI-5761 (P1, origin `defect`, project `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`) captures the advisory disposition.

## Reactivation Invariant (design point — recommended default)

The invariant definition itself is a design point. This proposal presents it with a recommended default and flags it for the Loyal Opposition reviewer rather than an owner AskUserQuestion; the reviewer may escalate to an owner decision if the recommended default is judged owner-material.

**Recommended default:** `completed_at` is null iff `status == "active"`, enforced fail-closed at evaluation. Operationally decomposed:

- **INV-1 (evaluation, fail-closed):** a project row accepted as *active* for any authorization decision MUST have `completed_at IS NULL`. An active row with non-null `completed_at` is DENIED at evaluation with a distinct reactivation-invariant error. The existing retirement-reconciliation carve-out (`status == "retired"` with `PROJECT_RETIREMENT_RECONCILIATION_CLASS` in `allowed_mutation_classes`) is unaffected: retired rows are expected to carry non-null `completed_at`.
- **INV-2 (lifecycle write, fail-closed):** a project write whose resulting row would have `status == "active"` and non-null `completed_at` is rejected. A `terminal -> active` transition is valid only as an owner-evidenced reactivation write: it must explicitly clear `completed_at` AND cite owner evidence (a `DELIB-*` id) in `change_reason`. Status-only reactivation is rejected.
- **INV-3 (terminal stamping, unchanged):** terminal transitions continue to stamp `completed_at` (existing `retire_project` behavior). The converse direction of the biconditional (terminal implies non-null `completed_at`) is surfaced by the audit as a report-only finding, not a fail-closed evaluation denial, because evaluation only accepts active rows plus the retirement-reconciliation carve-out.

Rejected alternative (presented for the reviewer): treating active-with-`completed_at` as merely a WARN at evaluation. Rejected because the advisory's impact is precisely that mechanical eligibility already exists; a warning does not close the owner-decision boundary bypass.

## Proposed Change

1. `scripts/implementation_authorization.py` (fix):
   - Extend `_project_status` to a row-reading helper that also selects `completed_at` (or add a sibling helper) without changing its public behavior for existing callers.
   - Change `_project_is_active` to require `status == "active" AND completed_at IS NULL`.
   - In `validate_project_authorization_row`, when `status == "active"` but `completed_at` is non-null, raise `AuthorizationError` with a distinct message naming the project id, the retained `completed_at` value, and WI-5761's reactivation invariant, so the denial is diagnosable and distinct from the generic not-active denial.
2. `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (fix):
   - In `update_project`, after merging `values`: if the resulting row would have `status == "active"` and non-null `completed_at`, raise `ProjectLifecycleError` directing the caller to the owner-evidenced reactivation path.
   - Recognize an owner-evidenced reactivation write: `terminal -> active` transitions require (a) `completed_at` explicitly cleared in the same write and (b) `change_reason` citing at least one `DELIB-*` owner-evidence id; otherwise reject.
   - Add a `reactivate_project(project_id, *, changed_by, change_reason, owner_evidence_deliberation_id)` service method that performs the compliant write (status `active`, `completed_at` cleared, evidence id validated as present in `change_reason` text and non-empty).
3. `groundtruth-kb/src/groundtruth_kb/cli.py` (fix):
   - Add `gt projects reactivate <project-id> --owner-evidence <DELIB-id> --change-reason <text>` wired to `reactivate_project`.
   - Add a `--clear-completed-at` flag to `gt projects update` so the field is clearable at all (the current `None`-filtering makes clearing impossible); the lifecycle-service invariant still governs whether the resulting row is valid.
4. `scripts/project_reactivation_audit.py` (new, read-only):
   - Enumerate `current_projects` rows violating INV-1 (`status == 'active' AND completed_at IS NOT NULL`) and report INV-3 converse findings (terminal with null `completed_at`) as informational.
   - Emit JSON and human-readable output; exit non-zero when INV-1 offenders exist so the audit is CI/doctor-consumable later.
   - Migration stance for historical rows: the audit enumerates; it never auto-mutates. The one known offender (Authority Foundations v3, above) is repaired only through the owner-evidenced reactivation path (or owner-directed retirement) after the recovery thread's pending owner decision — per the source advisory, history is not silently normalized, deleted, or bypassed.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization: operation-time evaluation is the mechanical enforcement of the owner's project-level authorization; accepting a lifecycle-scarred active row breaches the owner-decision boundary this spec defines. INV-1 restores the boundary.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — VERIFIED-driven completion/retirement: completion provenance written by governed completion/retirement must not be silently contradicted by a status-only write. INV-2/INV-3 protect that provenance.
- `GOV-STANDING-BACKLOG-001` — WI-5761 is the MemBase backlog authority for this work; this proposal implements a tracked backlog item rather than discretionary scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this thread follows the governed bridge protocol (NEW -> LO review -> GO -> implementation-start packet -> report -> VERIFIED).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites every governing specification identified by the pre-filing preflight.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the invariant is enforced mechanically at both write time (lifecycle service) and review/evaluation time (operation-time authorization), the required two-layer defense in depth.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — target paths under `groundtruth-kb/src/groundtruth_kb/project/**` are platform-layer lifecycle code; this change touches no application subtree and preserves the platform/application placement contract.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the test plan below derives every test from the linked specifications, and the post-implementation report will carry the spec-to-test mapping plus executed-command evidence required before any `VERIFIED`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect, invariant decision, and historical-row disposition are preserved as durable artifacts (this thread, WI-5761, cited deliberations) rather than transient session state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — project reactivation is an explicit lifecycle state transition; this proposal gives it a governed trigger (owner-evidenced reactivation write) instead of an implicit status flip.
- `.claude/rules/project-root-boundary.md` — all target paths are in-root (declaration above).
- `.claude/rules/file-bridge-protocol.md` — proposal structure: `Specification Links`, `target_paths`, `Requirement Sufficiency`, spec-derived verification plan, `Owner Decisions / Input`, recommended commit type.

## Prior Deliberations

Deliberation search performed 2026-07-30: `gt deliberations search "project reactivation completed_at authorization" --limit 5`.

- `DELIB-202667531` — owner advisory-triage decision (2026-07-29): fix-class advisories first, conversion of the 2026-07-29 LO advisory set into work items and proposals authorized; capture is not implementation approval. WI-5761 originates here.
- `DELIB-202667532` — owner north-star scoring decision shaping the same triage queue ordering.
- `DELIB-202667534` — leader-session sequencing record for the advisory-corrections program under which this proposal is dispatched.
- `DELIB-202667523` / `DELIB-202667533` — leader-session manual-dispatch records covering this proposal worker.
- `DELIB-202667524` — CF-10: leader-only MemBase mutation serialization until WI-5675/WI-5714 land; this proposal respects it (no MemBase mutation during filing; implementation mutations only post-GO through the packet path).
- `DELIB-20265559` — GO: Project PAUTH Autocomplete VERIFIED Gate; prior decision tying PAUTH lifecycle to project completion state — direct precedent that completion state is authorization-relevant.
- `DELIB-20264662` — NO-GO: Project VERIFIED-Completion Owner-Confirmed AUQ Trigger (REVISED-1); prior review insisting completion-state transitions carry owner-visible evidence.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — owner decision completing a PAUTH via AskUserQuestion; precedent that authorization completion transitions are owner-evidenced acts, which the reactivation direction must mirror.
- Source advisory Prior Deliberations carried forward: `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and `DELIB-202666274` preserve the complete lifecycle and later mechanical gates; neither approves a status-only reactivation shortcut.

No prior deliberation selects a reactivation invariant; that is why the invariant is presented above as a flagged design point with a recommended default.

## Owner Decisions / Input

- `DELIB-202667531` — owner decision (advisory triage, 2026-07-29) authorizing fix-class-first conversion of the 2026-07-29 Loyal Opposition advisories, including the source advisory behind WI-5761, into governed work items and bridge proposals. That decision authorizes filing this proposal; it is not implementation approval.
- `DELIB-202667533` — leader-session dispatch record under which this worker files exactly this one proposal.
- No new owner decision is requested at filing time. The reactivation-invariant selection is deliberately presented as a design point with a recommended default for the Loyal Opposition reviewer (per the dispatch instruction recorded in `DELIB-202667531`/`DELIB-202667534` sequencing); the reviewer may escalate it to an owner AskUserQuestion if judged owner-material. Historical-row repair for Authority Foundations v3 remains gated on the recovery thread's pending owner decision and is explicitly out of this proposal's mutation scope.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (implementation authority flows only from an owner-authorized active project) and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (completion/retirement is governed, evidence-bearing lifecycle state) jointly entail that a row simultaneously claiming active status and retaining completion provenance is outside both specs' authorized states; the proposed invariant operationalizes their intersection. No new or revised requirement is needed for this defect-class fix; the design point flagged above selects an enforcement default within existing requirement scope.

## Specification-Derived Test Plan

Tests are derived from the linked specifications and the invariant decomposition; all run under `platform_tests/` with the project venv interpreter.

| # | Test | Derived from | Location |
|---|------|--------------|----------|
| T1 | Fixture project retired then status-only reactivated (row: `status='active'`, `completed_at` non-null): `validate_project_authorization_row` / `_project_is_active` DENY with the distinct reactivation-invariant `AuthorizationError`; `begin` path fails closed. | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; INV-1 | `platform_tests/scripts/test_project_authorization.py` (extend) |
| T2 | Owner-evidenced reactivation (explicit `completed_at` clear + `DELIB-*` citation in `change_reason`, via `reactivate_project` and via `gt projects reactivate`) produces `status='active'`, `completed_at IS NULL`; the same project then PASSES operation-time evaluation. | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 + GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001; INV-1/INV-2 | `platform_tests/scripts/test_project_reactivation_invariant.py` (new) |
| T3 | Write-gate: `update_project` rejects status-only `terminal -> active` (stale `completed_at` carried forward) and rejects any write whose resulting row is active with non-null `completed_at`; `gt projects update --status active` alone fails with the directing error; `--clear-completed-at` without owner evidence still fails. | GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001; INV-2 | `platform_tests/scripts/test_projects_cli.py` (extend) + new file |
| T4 | Retirement-reconciliation carve-out regression: retired project + authorization carrying `PROJECT_RETIREMENT_RECONCILIATION_CLASS` still evaluates as before (non-null `completed_at` expected, not denied). | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | `platform_tests/scripts/test_project_authorization.py` (extend) |
| T5 | Historical-row audit: on a fixture DB containing one scarred active row, one clean active row, and one retired row, `scripts/project_reactivation_audit.py` enumerates exactly the scarred row as an INV-1 offender, reports the terminal-with-null row as informational, exits non-zero on offenders and zero on a clean DB, and performs no writes. | GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001; INV-3/audit | `platform_tests/scripts/test_project_reactivation_invariant.py` (new) |

Verification commands (implementation report will carry observed results): `ruff check` and `ruff format --check` on every changed `.py`; `pytest platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_reactivation_invariant.py` via the project venv `python.exe`.

## Risk and Rollback

- **Risk:** fail-closed denial of active projects carrying stale `completed_at` — exactly the scar class this defect fix targets. The only known live offender is Authority Foundations v3, which is already quarantined in prose by its recovery thread; the distinct error message names the repair path. Blast radius otherwise limited to the two predicates and the lifecycle write path; no schema change; append-only history untouched.
- **Risk:** legitimate automation that reactivates projects status-only would begin failing. Search of the working tree found no such caller; the audit script gives operators a deterministic pre-upgrade census.
- **Rollback:** single revert of the implementing commit restores prior behavior; the audit script is standalone and read-only; no data migration is performed, so rollback has no data path.

## Recommended Commit Type

Recommended commit type: `fix` — repairs broken authorization behavior (evaluation accepting contradictory lifecycle state; write path unable to express a clean reactivation) with no new capability surface beyond the repair's own reactivation/audit tooling.
