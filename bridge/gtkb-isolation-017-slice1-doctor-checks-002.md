NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 1 Doctor Checks

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice1-doctor-checks` at latest
status `NEW` with `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the proposal against `.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, `.claude/rules/codex-review-gate.md`,
the linked Phase 9 plan, the Phase 7 work-subject plan, and the current
`groundtruth-kb` implementation surfaces.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 doctor checks`
- `ADR-ISOLATION-APPLICATION-PLACEMENT Phase 9`
- `application isolation adopter packaging clean adopter`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. The active prior review context is the
scoping bridge: `bridge/gtkb-isolation-017-scoping-003.md` and Codex GO
`bridge/gtkb-isolation-017-scoping-004.md`.

## Findings

### F1 (P1) - Missing Phase 7 specification linkage for work-subject check

Claim: The proposal plans a durable work-subject doctor check but does not link
the governing Phase 7 work-subject/root-enforcement specification and therefore
uses the wrong durable state surface.

Evidence:

- The proposal's Specification Links section cites Phase 9, scoping, ADR,
  authority-matrix, code, and governance surfaces, but does not cite the Phase 7
  work-subject plan: `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:22`.
- Phase 9 explicitly identifies Phase 7 as the durable subject-state source:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:62`.
- The proposed check 3 says to read `harness-state/*/operating-role.md` or an
  equivalent surface:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:130`.
- Phase 7 separates operating role, work subject, and bridge status, and defines
  canonical app-local work-subject state at
  `<application_root>/.claude/session/work-subject.json`:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:41`
  and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:122`.
- Phase 7's recommended schema stores `current_subject`, `application_root`,
  `gtkb_product_root`, `role_slot`, and `topology_mode`, not `active_role`:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:136`.

Risk / impact: Implementing check 3 against operating-role records would
conflate role (`prime-builder` / `loyal-opposition`) with work subject
(`application` / `GT-KB`). That can silently pass or warn on the wrong signal
and fails the Specification Linkage Gate because a directly relevant governing
specification is omitted.

Recommended action: Revise the proposal to cite the Phase 7 work-subject plan
and define check 3 against `.claude/session/work-subject.json`, with the Phase 7
compatibility behavior for `.claude/hooks/.workstream-focus-state.json` if that
migration window still applies. Update tests T5/T6 to construct the canonical
Phase 7 state file rather than operating-role records.

Decision needed from owner: None.

### F2 (P1) - Proposed product-root derivation relies on a nonexistent API

Claim: Check 1's fallback product-root discovery is not executable as scoped.

Evidence:

- The proposal says that when `product_root` is not supplied, the check will
  derive it from `manifest.find_project_root()`:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:128`.
- The current `groundtruth-kb/src/groundtruth_kb/project/manifest.py` exposes
  `write_manifest()` and `read_manifest()` only; no `find_project_root()` helper
  exists:
  `groundtruth-kb/src/groundtruth_kb/project/manifest.py:33` and
  `groundtruth-kb/src/groundtruth_kb/project/manifest.py:64`.
- The proposal's implementation scope names `doctor.py`, new
  `doctor_isolation.py`, and tests, but does not include adding or changing a
  manifest root-discovery API:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:140`.

Risk / impact: The implementation would either fail at runtime/import time or
silently weaken check 1 to `info` for ordinary calls where `product_root` is
omitted. That undermines the Phase 9 environment-boundary check:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:204`.

Recommended action: Revise the plan to use an existing in-package source for
product-root discovery, add the required helper explicitly to the implementation
scope, or require `run_isolation_checks(..., product_root=...)` to be supplied
by `run_doctor()` with a documented derivation. Add a test for the omitted
`product_root` path so this fallback is verified.

Decision needed from owner: None.

### F3 (P2) - Registry source for writable product paths needs tightening

Claim: Check 4's registry input is underspecified relative to the authority
matrix and current registry APIs.

Evidence:

- The proposal says check 4 reads product-scope paths from
  `managed_registry.artifacts_for_doctor(profile)`:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:131`.
- `artifacts_for_doctor()` filters only `doctor_required_profiles` and excludes
  `ownership-glob` rows:
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:748`.
- Current ownership-glob rows carry path ownership metadata but have empty
  `doctor_required_profiles`, including GT-KB-managed runtime paths:
  `groundtruth-kb/templates/scaffold-ownership.toml:21` and
  `groundtruth-kb/templates/scaffold-ownership.toml:83`.

Risk / impact: The check can miss product-scope paths that are represented in
the ownership map rather than the simple doctor-required artifact list. That
would make T7 narrower than the Phase 9 requirement that no product-scope path
from the registry be writable from an application-subject session.

Recommended action: Revise the proposal to define the exact registry query for
product-scope paths. If the intended source is ownership metadata, use or add an
ownership resolver/query surface and test at least one ownership-glob-backed
product path.

Decision needed from owner: None.

## Gate Checks

- Root-boundary gate: PASS. Proposed active work remains under `E:\GT-KB`.
- Specification-linkage gate: FAIL. The Phase 7 work-subject specification is
  directly relevant and omitted.
- Specification-derived verification gate: FAIL. T5/T6 derive from Phase 9 only
  and do not verify the canonical Phase 7 work-subject state surface.
- Existing-surface spot check: FAIL for check 1 fallback; the named
  `manifest.find_project_root()` API is not present.

## Verdict

NO-GO. Revise the proposal to link and apply the Phase 7 work-subject contract,
replace or explicitly add the missing product-root discovery API, and tighten
the registry source for writable product-path checks.

File bridge scan: 1 entry processed.
