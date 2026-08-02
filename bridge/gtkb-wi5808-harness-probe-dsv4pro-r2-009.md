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
Version: 009
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-008.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808

target_paths: ["scripts/harness_probe_dsv4pro_r2.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r2.py"]
implementation_scope: corrective_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# REVISED Implementation Proposal — Correct DeepSeek V4 Pro Run-2 Root Containment

## Summary

Accept both blocking findings in version 008 and re-open a lawful implementation
path without fabricating a post-implementation report. Version 005 is a malformed
historical report carrier because it lacks the required `::open build` envelope
line. The committed probe also returns a false-positive containment result when
invoked from a working directory whose ancestor chain contains no GT-KB markers:
`_resolve_project_root()` returns that same working directory, after which the
containment check compares the directory to itself.

This revision proposes a two-file correction. The probe will identify the
canonical GT-KB root independently of the invoking working directory, inject the
observed working directory into the containment decision, and fail the
containment result when that directory is not a descendant of the validated
canonical root. The test will exercise a synthetic non-descendant path through
the injected behavioral seam while every live file and dependency remains inside
`E:\GT-KB`.

This document is a revised proposal, not a revised implementation report. No new
source or test mutation has occurred after version 008. A fresh independent GO,
exact work-intent claim, and implementation-start packet remain mandatory before
either target may be edited. After implementation, Prime Builder must file a new,
envelope-valid post-implementation report with exact executed evidence.

## Findings Disposition

### F1 — Accepted: version 005 is not a dispatchable report envelope

Version 005 begins with `NEW` and `::init gtkb pb` but has no `::open build`
line. That historical file is append-only evidence and will not be rewritten,
deleted, or represented as a valid current report. This version 009 uses the
required three-line envelope. A later post-implementation report will likewise
use a canonical status, `::init gtkb pb`, and `::open build` envelope and will
carry forward the complete specification-to-test mapping, commands, and observed
results.

### F2 — Accepted: current containment logic trusts an untrusted fallback root

Current source returns `cwd.resolve()` when `_resolve_project_root()` reaches the
filesystem root without finding the `groundtruth-kb/` and `.claude/rules/`
markers. `_check_project_root_containment()` then tests whether the same CWD is
relative to that fallback and necessarily returns true. The current failure-path
test acknowledges that it checks only the result shape. The implemented
behavior therefore does not satisfy WI-5808 deliverable (1).

### F2 test mechanism — Corrected for the mandatory project-root boundary

Version 008 requests an integration test that invokes the probe from a real
directory outside `E:\GT-KB`. That mechanism would create or read an out-of-root
live test dependency and conflicts with `.claude/rules/project-root-boundary.md`.
The behavioral requirement remains binding; only the fixture mechanism is
corrected. The implementation will expose the observed CWD as an injectable
input and test a synthetic absolute non-descendant path without creating,
reading, or depending on any external file or directory. The production CLI
continues to supply the real `Path.cwd()` value.

### Approval premise — Corrected to inherited project authority

WI-5808 is an active member of `PROJECT-GTKB-HARNESS-TEST`. The active,
list-free, no-expiry project authorization
`PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730` covers source, test,
test addition, configuration, documentation, metadata, governance evidence,
and bridge work for every active project member. The legacy work-item field
`approval_state: unapproved` is noncontrolling under the owner's project-only
inheritance doctrine. No separate WI approval or owner AUQ is required for this
correction. Project authorization does not bypass the current NO-GO or any
claim/start/review/finalization gate.

## Current Baseline Evidence

- Strict lifecycle resolution of the full physical version 001 through 008
  chain succeeds with latest status `NO-GO` at version 008 and no quarantined
  paths or blocking diagnostics.
- `scripts/harness_probe_dsv4pro_r2.py` is tracked and clean at 314 lines,
  SHA-256 `3caef2c1ec16523bd455a648e148fc53ebe2a7c5822accfaf343314d7982ba94`.
- `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py` is tracked and clean
  at 361 lines, SHA-256
  `fba7f2e75bca95f53bbaf31efb2199a79a6f13c1e9e749d24379f485a77e2661`.
- Both target files were included in custodial commit
  `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`; neither has drifted since that
  commit. Custodial inclusion is baseline evidence, not focused WI-5808
  verification or finalization.
- Fresh focused baseline on 2026-08-01: pytest `21 passed, 1 warning` in 25.31
  seconds; Ruff check passed; Ruff format check reported both files formatted;
  the in-root probe exited 0 with all six current checks true. These results do
  not cover the false-positive external-CWD behavior.

## Requirement Sufficiency

**Existing requirements are sufficient.** WI-5808 deliverable (1),
`GOV-HARNESS-ONBOARDING-CONTRACT-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, the mandatory project-root boundary,
and version 008 fully define the correction: root authority must be independent
of the invoking CWD, marker absence must not make the CWD self-authorizing, and
the failure path must be behaviorally asserted. No new or revised formal
specification is required.

The test substitution above is not a requirement waiver. It preserves the exact
false-result assertion while satisfying the stronger in-root evidence boundary.

## Proposed Design

1. **Canonical-root discovery independent of CWD.** Resolve the installed probe
   path from `Path(__file__)`, derive its expected GT-KB root, and validate the
   existing `groundtruth-kb/` plus `.claude/rules/` markers before treating the
   path as root authority. Do not return the invoking CWD as a fallback root.
2. **Fail-closed root-resolution result.** If the independently derived root is
   not marker-valid, surface root resolution as unavailable and report
   `project_root_containment: false`; do not perform project-relative checks
   against an unvalidated fallback.
3. **Injectable observed CWD.** Add an optional observed-CWD parameter to the
   report/containment seam. Production calls use `Path.cwd()`. Tests supply a
   synthetic absolute non-descendant path and require false. The synthetic path
   is data only; the test must not create it, change into it, enumerate it, or
   read from it.
4. **Preserve all other probe contracts.** Venv, Git read health, GT CLI,
   session-envelope, determinism, snake_case report keys, documented `--timeout`
   input, and read-only behavior remain unchanged. No new hard-coded timeout,
   interval, retry, or throttle value is introduced.
5. **Envelope-valid report after implementation.** The later report will be a
   new numbered file after a fresh GO and will use a complete dispatchable
   envelope. It will cite the fresh implementation-start evidence as
   transaction-time authority without restamping or fabricating packet evidence
   at review time.

## Exact Scope And Exclusions

Files expected to change after fresh GO/claim/start:

- `scripts/harness_probe_dsv4pro_r2.py`
- `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`

Explicitly excluded:

- every other WI-5808 run-specific probe or test;
- the duplicate r2b bridge chain and its target bytes as an independent
  implementation carrier;
- project, PAUTH, work-item, test-registry, specification, ADR/DCL/GOV, and
  Deliberation Archive mutation;
- `.claude/rules/project-root-boundary.md` mutation;
- any out-of-root fixture, symlink, junction, temporary directory, or live
  dependency;
- dispatcher, TAFE, runtime, harness identity, route, eligibility, credential,
  Git push, deployment, release, destructive cleanup, or external-system work.

## Duplicate-Carrier Coordination

`gtkb-wi5808-harness-probe-dsv4pro-r2b` is a duplicate clean-slug recovery
thread for the same WI and the exact same two target paths. Its current strict
head is version 008 `NO-GO`. The original
`gtkb-wi5808-harness-probe-dsv4pro-r2` thread is designated the sole carrier for
this correction. Prime Builder will not claim, edit, report, or request
verification under both threads.

Immediately before implementation start, Prime Builder must re-check the exact
two target preimages and peer-report collision diagnostics. If the r2b history
mechanically blocks the claim or implementation-start packet, stop and obtain a
governed r2b disposition; do not bypass the collision guard and do not duplicate
the correction under r2b.

## Specification Links

- Required (blocking): `GOV-HARNESS-ONBOARDING-CONTRACT-001` — defines the harness capability floor
  and machine-checkable containment assertion.
- Required (blocking): `GOV-FILE-BRIDGE-AUTHORITY-001` — requires this append-only numbered chain,
  role-correct statuses, and a later independently reviewed verdict.
- Required (blocking): `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — makes the active parent
  project authorization the operative approval surface while preserving every
  downstream implementation gate.
- Required (blocking): `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires active
  project authorization to be re-evaluated at implementation start and
  finalization.
- Required (blocking): `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete
  governing specification linkage in this revision.
- Required (blocking): `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires executed,
  spec-derived containment evidence before VERIFIED.
- Required (blocking): `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — supplies the in-root containment
  boundary exercised by deliverable (1).
- Required (blocking): `GOV-WORK-TREE-HYGIENE-001` — requires exact clean preimages and protection of
  the duplicate r2b ownership history.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserves proposal, report, test,
  decision, and verdict traceability.
- Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — links the corrective source/test
  evidence to WI-5808 and this bridge chain.
- Advisory: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserves explicit proposal,
  implementation-report, verification, and finalization states.
- Advisory: `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — requires deterministic,
  machine-readable probe results.

## Prior Deliberations

- `DELIB-202667726` — owner Harness Test program directive and run matrix.
- `DELIB-202667727` — owner grant of the active list-free Harness Test
  whole-project PAUTH inherited by WI-5808.
- `DELIB-202667722` — timer and throttle governance; the correction preserves
  the documented CLI timeout source and adds no timer literal.
- Owner snake_case report-key decision recorded in the WI-5808 run transcript —
  unchanged by this correction.

## Owner Decisions / Input

No new owner decision is required. The owner has already approved
`PROJECT-GTKB-HARNESS-TEST` through the active list-free PAUTH, and WI-5808 is
an active project member. This revision neither narrows the required behavior
nor expands beyond the original two paths.

If a future actor proposes using an out-of-root live fixture, activating the
r2b duplicate in parallel, expanding target paths, or changing the project
scope, that actor must stop and obtain the applicable governed direction rather
than infer it from this revision.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Requirement | Test / evidence | Expected result | Executed in this proposal |
|---|---|---|---|
| WI-5808 deliverable (1); `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `test_project_root_containment_pass` | Real in-root production CWD reports `true` | Baseline only; rerun after implementation |
| WI-5808 deliverable (1); `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Replace the shape-only failure test with `test_project_root_containment_fails_for_injected_non_descendant_cwd` | Synthetic non-descendant CWD reports `false` without any out-of-root filesystem access | No — proposed |
| Mandatory project-root boundary | Test monkeypatch/injection audit and scoped file-access assertion | Test creates, reads, and requires no path outside `E:\GT-KB` | No — proposed |
| Canonical-root authority | New focused test for invalid marker-derived root | Marker-invalid root is unavailable/fail-closed and never falls back to CWD | No — proposed |
| Existing checks (2)-(6) | Existing focused suite | Venv, Git, GT CLI, session envelope, determinism, keys, and read-only behavior remain green | Baseline 21 passed; rerun after implementation |
| `DELIB-202667722` | Existing timeout-source and no-hard-coded-timeout tests | CLI argument remains the sole subprocess timeout source | Baseline passed; rerun after implementation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus both Ruff gates and two CLI observations | Commands and exact observed results are present in the later report; no skipped or shape-only containment assertion | No — verification-stage evidence |
| Duplicate-carrier safety | Exact-path status/preimage/collision check for r2 and r2b | Only r2 is claimed; r2b remains unmodified; target preimages match the approved revision | No — start-time evidence |

## Implementation And Verification Sequence

1. Loyal Opposition reviews this exact revision and issues a fresh GO or a
   corrected NO-GO.
2. Prime Builder re-checks current project membership, list-free PAUTH,
   original-r2/r2b collision state, and the exact two target preimages.
3. Prime Builder obtains one exact r2 work-intent claim and an implementation-
   start packet. Any denial stops work; no bypass is authorized.
4. Prime Builder changes only the two declared targets and runs:
   - `python -m pytest platform_tests/scripts/test_harness_probe_dsv4pro_r2.py -q --tb=short`
   - `python -m ruff check scripts/harness_probe_dsv4pro_r2.py platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`
   - `python -m ruff format --check scripts/harness_probe_dsv4pro_r2.py platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`
   - one in-root CLI probe plus a root-safe injected non-descendant behavioral
     probe through the test seam.
5. Prime Builder files a new envelope-valid post-implementation report with the
   exact diff, packet-at-implementation evidence, command lines, observed
   results, and updated spec-to-test table. It does not rewrite version 005.
6. An independent Loyal Opposition session re-runs the mapped evidence before
   any VERIFIED/focused-finalization action.

## Acceptance Criteria

1. Marker absence or an invoking CWD outside the independently validated GT-KB
   root yields `project_root_containment: false`; the CWD is never accepted as
   its own fallback authority.
2. The production CLI obtains observed CWD from `Path.cwd()` while focused tests
   can inject a synthetic path without touching the external filesystem.
3. The shape-only failure test is replaced by a behavioral false-result
   assertion, and a marker-invalid root fails closed.
4. All pre-existing focused checks remain green; the post-implementation report
   records exact pytest, Ruff check, Ruff format-check, and probe results.
5. No live path outside `E:\GT-KB` is created, read, changed into, linked, or
   required by implementation or verification.
6. The diff is limited to the exact two declared targets and remains wholly
   attributable to this original r2 chain.
7. No r2b claim, source/test edit, report, or verification is attempted in
   parallel.
8. The later implementation report has a valid status/init/open envelope and
   does not fabricate, restamp, or require a review-time-live packet.

## Risk And Rollback

- **Root derivation coupled to script placement.** Mitigate by validating the
  same canonical markers already used by the probe and by failing closed if the
  installed path is not the governed `scripts/` placement.
- **Synthetic-path test accidentally accesses external storage.** Keep the
  injected path as data only and assert no chdir/open/enumeration occurs.
- **Regression to checks (2)-(6).** Keep those functions and report keys
  unchanged and rerun the complete focused suite.
- **Duplicate-thread attribution.** Treat r2b as a held duplicate, re-run peer
  collision checks before start, and stop on any collision denial.

Rollback is a focused revert of only the attributable post-GO hunks in the two
target files. Bridge history remains append-only. It requires no change outside
those two source/test artifacts.

## Bridge Filing Evidence

This revision is intended as the next numbered file
`bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-009.md` after version 008
`NO-GO`. Versions 001 through 008 remain immutable. `REVISED` is the
Prime-Builder-authored response status to the current NO-GO. Before live filing,
the writer must re-check that version 008 remains the strict current head and
must reject any version or `Responds to` race rather than overwrite or fork the
chain.

The numbered versioned bridge files are the append-only audit trail. No retired
aggregate bridge queue or index is created or treated as authority.

## DISARM — Governance Mechanics

The eventual correction is source-and-test-only. Every governance reference in
this proposal is read-only evidence; the exact target list is exhaustive.

## DISARM — Packet And Runtime Mechanics

The future implementation-start packet is short-lived, transaction-local
evidence derived only after a fresh GO and exact r2 claim. It is not a formal
artifact and does not replace project authorization, target scoping, review, or
verification. Packet evidence must be reported as observed at implementation
time; it must not be fabricated or restamped to satisfy later review wall-clock
liveness.

This proposal authorizes no dispatcher, TAFE, runtime, route, eligibility,
harness identity, claim, source/test, Git, credential, deployment, release, or
external-system mutation. The dispatcher remains deliberately disabled.

## Recommended Commit Type

`fix` — correct the run-2 containment false positive and replace its ineffective
failure-path test without adding a new capability or widening the two-file
scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
