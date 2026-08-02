REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved ::init gtkb pb; manual physical-bridge processing with dispatcher/TAFE disabled
author_metadata_source: explicit current-session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-dsv4pro-r2
Version: 011
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-010.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808

target_paths: ["scripts/harness_probe_dsv4pro_r2.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r2.py"]
implementation_scope: corrective_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# REVISED Implementation Proposal — Correct Run-2 Containment and Timeout Authority

## Revision Claim

Accept F1 and correct F2's approval premise. The proposed two-file correction
will remove the production `default=10.0` timer policy and make the documented
`--timeout` argument required. The same correction will implement the already
accepted canonical-root discovery and injected non-descendant-CWD behavior from
version 009. The focused test will reject every numeric production timeout
literal, including parser defaults, rather than exempting one.

This revision is a proposal only. No source or test mutation occurred after
version 010. A fresh independent GO, exact work-intent claim, and valid
implementation-start packet remain mandatory before either target is edited.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5808, the Harness Onboarding
Contract, the isolation placement ADR, the active timer-governance owner
decision, and version 010 fully define the required behavior. The correction
removes a file-local timer policy, requires explicit timeout input, makes root
authority independent of CWD, and tests the failure path behaviorally. No new
or revised formal requirement is required before implementation.

## Findings Addressed

### F1 — Accepted: the parser default is a hard-coded runtime timer policy

`scripts/harness_probe_dsv4pro_r2.py` currently declares `--timeout` with
`default=10.0`. Ordinary invocations that omit the argument therefore inherit a
file-local numeric policy. The current test detects only `timeout=` call-site
literals and explicitly excuses the parser default, so its passing result does
not establish the owner-directed timer contract.

The implementation will make `--timeout` a required, documented positive
floating-point input and will supply no numeric default or fallback in the
probe. The execution authority for each run is therefore explicit at the CLI
boundary and can later be supplied by the Timer Governance project's central
typed configuration without another probe-local policy. The parser will reject
omission before any probe subprocess starts. Existing validation will continue
to reject zero or negative values.

The test will inspect the production source/AST and fail on any numeric timeout
default, `timeout=` literal, retry delay, polling interval, or equivalent local
fallback. It will also assert that omitting `--timeout` exits nonzero and that an
explicit positive value reaches all subprocess calls unchanged.

This focused correction coordinates with active Timer Governance work,
including WI-5806's centralized timer/concurrency configuration and WI-5873's
repository-wide pytest-timeout correction. It does not duplicate or narrow
those project-wide deliverables.

### F2 — Corrected: active parent-project PAUTH is the controlling approval

WI-5808 is an active member of `PROJECT-GTKB-HARNESS-TEST`. The active,
list-free, no-expiry whole-project authorization
`PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730` applies to every active
project work item. Under the owner's explicit project-only inheritance rule,
the legacy work-item `approval_state: unapproved` field is noncontrolling and
does not create an AUQ or separate WI approval gate.

The active project PAUTH does not bypass this NO-GO, the fresh GO requirement,
claim/start enforcement, exact target scoping, or independent verification.

## Carried-Forward Containment Correction

1. Derive the canonical GT-KB root from the installed probe path, independent
   of the invoking CWD, and validate `groundtruth-kb/` plus `.claude/rules/`
   markers before treating it as root authority.
2. If the derived root is marker-invalid, report root resolution unavailable
   and `project_root_containment: false`; never fall back to the invoking CWD.
3. Add an optional observed-CWD parameter at the report/containment seam.
   Production supplies `Path.cwd()`; tests supply a synthetic absolute
   non-descendant path as data only.
4. Assert the synthetic non-descendant result is false without creating,
   changing into, enumerating, or reading any out-of-root path.
5. Preserve venv, Git-read, GT CLI, session-envelope, determinism, snake_case,
   and read-only probe contracts.

## Exact Scope and Exclusions

Files proposed to change after fresh GO/claim/start:

- `scripts/harness_probe_dsv4pro_r2.py`
- `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`

No scope expansion from version 009 is proposed. Explicit exclusions remain:

- every other WI-5808 run-specific probe or test;
- the duplicate r2b bridge chain and its target bytes as a second carrier;
- project, PAUTH, work-item, specification, test-registry, ADR/DCL/GOV, or
  Deliberation Archive mutation;
- out-of-root fixtures, symlinks, junctions, temporary directories, or live
  dependencies;
- dispatcher, TAFE, harness identity, route, eligibility, credentials, Git
  push, deployment, release, destructive cleanup, or external-system work.

The original r2 chain remains the sole carrier. Before implementation, Prime
Builder must re-check the two exact preimages and peer-report collision state.
Any r2b collision denial stops work; it is not a bypass signal.

## Specification Links

- Required: `GOV-HARNESS-ONBOARDING-CONTRACT-001` — defines the machine-checkable
  harness capability and containment floor.
- Required: `GOV-FILE-BRIDGE-AUTHORITY-001` — requires the append-only,
  role-correct bridge lifecycle and independent verdict.
- Required: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — makes active
  parent-project authorization the implementation approval surface.
- Required: `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires
  project authorization at implementation start and finalization.
- Required: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires
  concrete governing links in this revision.
- Required: `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires executed
  requirement-derived evidence before VERIFIED.
- Required: `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — governs the in-root
  containment boundary.
- Required: `GOV-WORK-TREE-HYGIENE-001` — protects exact clean preimages and
  duplicate-carrier ownership.
- Advisory: `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — requires deterministic,
  machine-readable probe behavior.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve traceability across proposal,
  implementation, test, report, and verdict states.

## Prior Deliberations

- `DELIB-202667726` — owner Harness Test program and run matrix.
- `DELIB-202667727` — active Harness Test whole-project authorization.
- `DELIB-202667722` — timer/throttle governance implicated by F1.

## Owner Decisions / Input

- Owner directive in this session — implementation approval belongs only to an
  active parent project; active project WIs inherit its PAUTH.
- Owner directive in this session — eliminate hard-coded timers and centralize
  timer, throttle, threshold, fan-out, and concurrency policy in a governed SoT.

No new owner decision is required. The required-CLI design removes the local
policy now while retaining a clean migration boundary for centralized Timer
Governance work.

## Specification-Derived Verification Plan

| Requirement | Test / evidence | Expected result |
|---|---|---|
| WI-5808 timer requirement; `DELIB-202667722` | Timer-policy source/AST test | No numeric timeout default, call-site timeout literal, retry delay, or timer fallback exists in production source |
| Documented CLI timeout authority | Omission and explicit-value CLI tests | Omission fails before probe execution; explicit positive value reaches all subprocess calls unchanged |
| WI-5808 deliverable (1); `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Existing in-root containment test | Real in-root production CWD reports `true` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Injected synthetic non-descendant test | Containment reports `false` with no external filesystem access |
| Canonical-root authority | Marker-invalid derived-root test | Root resolution fails closed and never falls back to CWD |
| Existing checks (2)-(6) | Complete focused suite | Venv, Git, GT CLI, session envelope, determinism, keys, and read-only behavior remain green |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, Ruff check, Ruff format check, in-root CLI observation | Later report records exact commands and observed results with no shape-only containment assertion |
| Duplicate-carrier safety | Exact preimage, latest-status, and collision check | Only original r2 is claimed; r2b remains unmodified |

Required post-implementation commands:

- `python -m pytest platform_tests/scripts/test_harness_probe_dsv4pro_r2.py -q --tb=short`
- `python -m ruff check scripts/harness_probe_dsv4pro_r2.py platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`
- `python -m ruff format --check scripts/harness_probe_dsv4pro_r2.py platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`
- one in-root CLI run with an explicit timeout and the root-safe injected
  non-descendant behavioral assertion through the test seam.

## Acceptance Criteria

1. The probe has no numeric timeout default or equivalent local timer policy;
   `--timeout` is required, documented, and validated positive.
2. The timer test rejects every production timeout literal and no longer
   exempts an argparse default.
3. Marker absence or a non-descendant observed CWD yields containment false;
   the invoking CWD is never its own root authority.
4. Tests exercise the false branch using synthetic data only and touch no live
   path outside `E:\GT-KB`.
5. All existing focused behavior remains green and the later report includes
   exact pytest, Ruff, and probe evidence.
6. The diff is limited to the two declared targets and remains attributable to
   the original r2 chain; r2b remains untouched.
7. The post-implementation report uses a valid status/init/open envelope and
   cites implementation-time packet evidence without restamping it.

## Risk and Rollback

- **Existing callers omit `--timeout`.** The intentional fail-fast change may
  expose undocumented callers. Mitigate by checking repository call sites
  before editing and updating only the in-scope focused test invocation; any
  additional production caller requiring mutation must trigger scope review.
- **Script-placement coupling.** Validate canonical markers and fail closed if
  the probe is not installed at the governed location.
- **Synthetic path accidentally becomes I/O.** Keep it as a pure value and
  assert no chdir/open/enumeration path is used.
- **Duplicate-thread attribution.** Re-run r2/r2b collision checks before claim
  and stop on any denial.

Rollback is a focused revert of only attributable post-GO hunks in the two
targets. Bridge history remains append-only; no governance or TAFE state is
rewritten.

## Pre-Filing Evidence

- The physical chain through version 010 is append-only and version 010 is the
  current `NO-GO` head.
- This draft responds exactly to version 010 and retains the same two targets.
- Prime Builder role eligibility was checked through `gt harness roles`; harness
  A is active and assigned `prime-builder`.
- Candidate applicability and clause preflights will be executed by the
  governed revision helper before live filing; any nonzero result stops filing.
- Dispatcher and TAFE mutation remain explicitly outside scope and disabled.

## DISARM — Governance and Runtime Mechanics

The future implementation-start packet is short-lived transaction evidence,
not a formal artifact or substitute for project PAUTH, exact scope, review, or
verification. This proposal authorizes no source/test edit until fresh GO and
valid claim/start evidence exist. It authorizes no dispatcher, TAFE, route,
identity, credential, Git, deployment, release, or external-system mutation.

## Recommended Commit Type

`fix` — remove the run-2 timer-policy violation while correcting the accepted
containment false positive within the unchanged two-file scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
