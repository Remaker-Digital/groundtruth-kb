NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: da5d93b8-0408-4770-ad6f-00b65fe21530
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-session

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4795

# Deterministic Obsolete-Reference-Purge Check (WI-4795)

Document: gtkb-obsolete-reference-purge-deterministic-check
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4795
Recommended commit type: feat

## Summary

Deliver the deterministic check that operationalizes `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`
and flips it from `specified` to `implemented` (Phase 1 = WARN). The check enumerates
**retirement-class artifacts** and flags any that lack a **linked obsolete-reference-purge
work item**. It ships as a read-only script (`scripts/check_obsolete_reference_purge.py`)
plus a doctor surface (`_check_obsolete_reference_purge`, WARN severity), mirroring the
established `gtkb-adr-dcl-clause-test-enforcement` two-phase pattern (WARN now; FAIL
promotion is a separate Phase-2 thread gated on Slice-1 feedback).

This is the mechanical enforcement actuator the methodology ADR/DCL (GO-terminal thread
`gtkb-obsolete-reference-purge-methodology-adr-dcl`) explicitly deferred to WI-4795.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (v1, specified) — the standing obligation
  this check enforces: a retirement/replacement of a load-bearing implementation must be
  paired with a purge work item before VERIFIED. The doctor WARN surface is the Phase-1
  operationalization of that obligation.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (v1, specified) — the machine-checkable
  constraint. Its three assertions are this proposal's verification targets (see Spec-to-Test
  Mapping). Landing the check promotes this DCL `specified -> implemented` via a formal-artifact
  -approval packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this `## Specification Links`
  section cites every governing spec; the verification plan derives from them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-implementation report will
  carry spec-derived verification; the spec-to-test mapping is defined below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed through the governed no-index bridge path; the
  status-bearing numbered file chain plus dispatcher/TAFE state are canonical.
- `GOV-STANDING-BACKLOG-001` — WI-4795 is a MemBase backlog item; the check reads the
  canonical `work_items` table to detect paired purge WIs (no second backlog source).
- `GOV-ARTIFACT-APPROVAL-001` — the DCL `specified -> implemented` promotion is a formal
  artifact mutation gated by a formal-artifact-approval packet (the PAUTH explicitly forbids
  formal mutation without one).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) — every target path resolves
  in-root under `E:\GT-KB`; the check reads only in-root canonical state (`groundtruth.db`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the check is the lifecycle artifact the
  retirement trigger produces; it makes the purge-pairing obligation a durable, observable
  surface rather than session memory.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — the authorizing owner
  decision. Establishes that significant changes MUST add work items that REMOVE obsolete
  references, not merely prohibit them; the deterministic check is the enforcement half of
  that obligation (AUQ Q2).
- `gtkb-obsolete-reference-purge-methodology-adr-dcl` (GO at -004, terminal) — formalized the
  ADR + DCL this check enforces; the DCL body names this check as its enforcement actuator and
  declares its `specified`-until-WI-4795 state as expected, not a regression.
- `gtkb-index-md-classified-inventory` (GO at -002, terminal) — the retired-aggregate instance
  classification contract; a distinct enforcement surface (the strip tranches' STRIP/KEEP/
  QUARANTINE completeness test), cited here to keep the two surfaces explicitly separate.
- `DELIB-20260673` (v1) — parallel-session SoT fragmentation from divergent retired aliases;
  the motivating evidence that obsolete residue competes with canonical sources in
  session-context.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are `ADR-OBSOLETE-REFERENCE-PURGE
-OBLIGATION-001` and `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (both v1, specified, owner-approved
via the methodology thread). This proposal implements the check those artifacts mandate; it
creates no new requirement. The DCL's three assertions are the acceptance criteria.

## Target Paths

target_paths: ["scripts/check_obsolete_reference_purge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_check_obsolete_reference_purge.py", "groundtruth.db#DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001"]

- `scripts/check_obsolete_reference_purge.py` (new) — read-only deterministic check + core
  function importable by the doctor surface.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modify) — add
  `_check_obsolete_reference_purge(target) -> ToolCheck` and register it in the checks list,
  mirroring `_check_lapsed_go_implementation_claims` (sys.path insert + fail-soft to `warning`).
- `platform_tests/scripts/test_check_obsolete_reference_purge.py` (new) — spec-derived tests.
- `groundtruth.db#DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — status promotion
  `specified -> implemented`, executed post-implementation via `gt spec` + a formal-artifact-
  approval packet (NOT a raw file Write; declared here for traceability).

## Design

### Retirement-class artifact set R (deterministic)

R = the union, within the evaluation window, of:

1. Specs with `status in {retired, superseded}` (`db.list_specs(status="retired")` +
   `db.list_specs(status="superseded")`).
2. Specs whose id has prefix `RETIRE-SPEC-`.
3. ADR/DCL specs (`type in {architecture_decision, design_constraint}`) carrying an explicit
   machine-readable supersession marker — a `Supersedes:` / `supersedes` reference line naming
   a prior artifact. (Phase 1 requires an explicit marker; it does NOT NLP-guess supersession,
   keeping the detector deterministic and false-positive-free.)

### Paired purge work item P (deterministic)

R-id is "paired" if any `work_item` (any resolution status) satisfies at least one of:

- (a) `source_spec_id == R.id`; OR
- (b) an explicit `purges: <R.id>` token in the work item description; OR
- (c) the work item is a member of a project whose name contains `OBSOLETE-REFERENCE-PURGE`
  AND its description references `R.id`.

Detection is intentionally inclusive (favor PASS) so a Phase-1 advisory does not cry wolf on a
genuinely-paired retirement.

### Evaluation window (KEY REVIEW POINT)

Phase 1 window = retirement-class artifacts whose latest-version `changed_at` is on/after the
obligation effective date `2026-06-24` (the `DELIB-...-DIRECTIVE-20260624` date), exposed as a
module constant `OBLIGATION_EFFECTIVE_DATE` overridable for tests. Rationale: the ADR frames a
**standing completion obligation on significant changes going forward**; retroactively flagging
the entire historical corpus of retired specs would flood WARN with un-actionable noise and is
not what the ADR mandates. LO is invited to confirm or adjust this boundary.

### Surfaces (Phase 1 scope)

- Standalone: `python scripts/check_obsolete_reference_purge.py [--json]` — exit 0 always in
  Phase 1 (advisory); emits per-artifact PASS/WARN findings + summary. CI/preflight-runnable.
- Doctor: `_check_obsolete_reference_purge` returns `warning` when unpaired retirements exist,
  `pass` when none, and fail-soft `warning` if the registry/db is unavailable (same contract as
  `_check_lapsed_go_implementation_claims`).
- Out of Phase-1 scope (explicit): a blocking cutover/verification FAIL gate and the DCL's
  Phase-2 promotion. Those are a separate future thread per the DCL's two-phase enforcement mode.

## Verification Plan (Specification-Derived)

All tests in `platform_tests/scripts/test_check_obsolete_reference_purge.py`, run against a
fixture project root with a synthetic `groundtruth.db` so the suite is hermetic and
order-independent.

### Specification-Derived Verification — Spec-to-Test Mapping

| Linked spec / clause | Spec-to-test mapping | Command |
|----------------------|----------------------|---------|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` assertion 1 (linked purge WI exists; WARN Phase 1) | `test_unpaired_retirement_in_window_warns` (retirement-class R with no pair -> finding) + `test_paired_retirement_passes` (R with a (a)/(b)/(c) pair -> no finding) | `python -m pytest platform_tests/scripts/test_check_obsolete_reference_purge.py -q --tb=short` |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` assertion 2 (ADR exists, `type=architecture_decision`) | `test_adr_obligation_exists_with_type` | same |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` assertion 3 (check script exists at declared path) | `test_check_script_exists_at_declared_path` | same |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (obligation operationalized at WARN) | `test_doctor_surface_warn_pass_failsoft` (warning on unpaired, pass on none, fail-soft on db error) | same |
| Evaluation-window boundary | `test_pre_obligation_retirement_excluded` (a retired spec dated before `OBLIGATION_EFFECTIVE_DATE` is not flagged) | same |
| Code quality | `ruff check` + `ruff format --check` on the new script + test | `python -m ruff check scripts/check_obsolete_reference_purge.py platform_tests/scripts/test_check_obsolete_reference_purge.py` ; `python -m ruff format --check <same>` |

The post-implementation report will carry the executed commands + observed results and confirm
the DCL `specified -> implemented` promotion via the formal-artifact-approval packet.

## Risk / Rollback

- **Risk: false-positive WARN flooding.** Mitigated by the forward-looking evaluation window and
  inclusive pairing detection. Phase 1 is advisory (exit 0 / WARN), so even a mis-tuned window
  cannot block work.
- **Risk: false-negative (a real unpaired retirement is missed).** Acceptable for Phase 1
  advisory; the Phase-2 FAIL promotion is explicitly gated on Slice-1 feedback that tightens the
  R-set markers and pairing rule first (same staging as `gtkb-adr-dcl-clause-test-enforcement`).
- **Risk: DCL promotion without approval.** The `specified -> implemented` flip is routed through
  `gt spec` + a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001`; the PAUTH forbids
  formal mutation without one.
- **Rollback:** the check is additive and read-only. Reverting the script + the doctor
  registration block + the test removes the surface with no state to unwind; the DCL promotion is
  a separate append-only version that can be superseded if reverted.

## Owner Decisions / Input

This proposal depends on owner approval and proceeds under the governed PAUTH; it cites the
AUQ-only rule. Authorizing evidence:

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (2026-06-24) — owner directive
  authorizing `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`; AUQ Q2 specifically authorizes the
  deterministic check that this WI implements.
- AskUserQuestion (2026-06-25, this session) — owner selected **"Full project scope"**,
  authorizing bounded implementation of WI-4795 + the strip tranches under
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`.

No new owner decision is required to GO this proposal. One design question is surfaced for LO
(not owner) review: the **evaluation-window boundary** (forward-looking from `2026-06-24`).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
