NEW

# WI-5222 - Calibrate the generous dispatch envelope to a 60-minute model window

bridge_kind: prime_proposal
Document: gtkb-wi5222-60-minute-generous-dispatch-envelope
Version: 001
Date: 2026-07-13 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: interactive Prime Builder; owner-directed telemetry calibration; governed bridge workflow

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5222

target_paths: [".api-harness/routing.toml", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_lo_harness_turn_budget.py"]

implementation_scope: timer-policy calibration and exact regression assertions only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Replace the previously VERIFIED eight-hour provider-session allowance with the
owner-approved 3,600-second model-execution window derived from retained run
telemetry. Keep the existing 600-turn ceiling and 900-second per-operation
bound. Preserve the established timer ordering by giving the dispatcher worker
a 600-second completion/reconciliation margin (`4,200` seconds total) and by
letting the canonical lease derivation add its existing 300-second margin
(`4,500` seconds total).

The retained successful-run telemetry is the calibration evidence: among the
ten longest operationally successful runs, eight completed within 60 minutes;
the owner explicitly accepts the 1:40:02 H run and 4:05:31 D run as historical
outliers under the new policy. This proposal does not relabel either historical
success as a harness defect and does not rewrite telemetry.

## Requirement Sufficiency

Existing requirements sufficient.

Existing specifications are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
already governs dispatcher execution and truthful timeout classification;
`SPEC-DISPATCHER-CONTROL-SURFACE-001` governs observable, controlled operation;
and the harness onboarding/template requirements require aligned provider and
outer envelopes. The owner decision changes the policy value and supersedes the
prior eight-hour allowance without requiring a new architectural surface.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. The only configuration source is
`.api-harness/routing.toml`; no dispatcher runtime JSON, lease, lock, credential,
or out-of-root dependency is in scope.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs worker lifetime, timeout classification, lease ordering, and dispatcher execution.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires the effective timer policy and runtime state to remain observable through canonical dispatcher reporting.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires provider harness execution limits to support genuine governed PB/LO work.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - governs the shared F/H provider runtime and routing configuration.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - requires H to consume the shared provider timing contract truthfully.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - requires D timing changes to preserve its governed tool-loop behavior and parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires append-only proposal, verdict, report, and verification handling.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite all governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH, project, and work-item linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent execution of every mapped acceptance test before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - `WI-5222` and `TEST-11376` are the MemBase carriers for this owner-directed change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the owner policy decision and implementation work to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the decision-to-work-item-to-bridge lifecycle used here.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires implementation and verification artifacts for this policy mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all implementation and evidence to remain in the GT-KB root.

## Prior Deliberations

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` - controlling owner decision; adopts the 60-minute model window and accepts two longer historical outliers.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - predecessor generous-first policy; superseded only for the numeric whole-run allowance after telemetry review.
- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` - predecessor refinement rule; the fresh owner decision is explicit authority to calibrate now from the retained fleet sample.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` - authorized and preserved the prior 600/900/28,800/29,400 envelope that WI-5222 now narrows.
- `DELIB-202666178` - independent GO for the predecessor WI-5200..5202 generous repair.
- `DELIB-202665716` - independent VERIFIED evidence for model-aware dispatcher timer resolution and telemetry.

## Owner Decisions / Input

Mike directed: "a 60-minute window before you declare FAIL is likely to be
adequate" and designated it the new generous allowance after reviewing the ten
longest successful runs. The decision is durably captured as
`DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`; implementation authority
is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713`.

## Proposed Scope

### IP-1 - Provider model window

In `.api-harness/routing.toml`, change only the
`session_timeout_seconds` value for `routing.ollama`,
`routing.alibaba-cloud-studio`, and `routing.openrouter` from `28,800` to
`3,600`. Preserve `max_turns = 600`, `timeout_seconds = 900`, every model and
skill route, and all foreign formatting/Goose/model hunks already present in
the dirty file.

### IP-2 - Outer worker and derived lifecycle timers

In `scripts/dispatcher_runtime.py`, replace the `29,400`-second generous worker
floor with `4,200` seconds and update its policy comment to cite the controlling
owner decision. Keep the existing `600`-second worker completion margin and the
canonical `_document_lease_ttl_seconds()` derivation unchanged. Consequently:

- every configured A/B/C/D/F/H default worker lifetime is `4,200` seconds;
- D's routed `3,600`-second session plus the existing margin also resolves to
  `4,200` seconds;
- the document lease derives to `4,500` seconds;
- reset-straggler age derives from the `4,200`-second role floor plus its
  existing 300-second margin.

No role, harness, model, routing, ranking, eligibility, circuit-breaker,
operation-timeout, turn-budget, or cleanup algorithm changes.

### IP-3 - Exact regression and parity assertions

Update only timer expectations in the seven listed existing test modules plus
`test_lo_harness_turn_budget.py`. Tests must prove all three route blocks retain
`900/3,600/600`, every dispatcher harness profile resolves to `4,200`, D's
route-derived profile remains ordered, lease/reset derivation resolves to
`4,500`, and timeout telemetry still identifies the configured worker lifetime.

The shared files already carry separately governed WI-5217/WI-5220 or foreign
changes. Implementation and finalization must therefore use exact WI-5222
hunks. Whole-file staging of any overlapping target is prohibited.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `TEST-11376` | Focused dispatcher lifetime, lease, reset, and timeout-telemetry tests | model window `3,600`; worker `4,200`; lease/reset `4,500`; no preemption before the model window |
| `ADR-CLOUD-HARNESS-TEMPLATE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | `test_cloud_harness_base.py`, `test_openrouter_harness.py`, and `test_alibaba_cloud_studio_harness.py` | F/H consume `900/3,600/600` routing values and retain shared runtime behavior |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | `test_ollama_harness.py` plus D lifetime-profile tests | D consumes `900/3,600/600`; routed session plus margin resolves to `4,200` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `test_lo_harness_turn_budget.py` and canonical dispatcher report/config checks | D/F/H remain 600-turn, role-correct, and observable; no routing/eligibility drift |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run all nine approved test modules, Ruff check, Ruff format check, and `git diff --check` | all WI-5222-owned tests pass; exact hunk scope is clean |
| Genuine governed behavior | Independently dispatch the post-implementation report through an eligible D or H LO session | one selected WI-5222 report receives a compliant VERIFIED or actionable NO-GO; exit and lease reconcile canonically |

## Acceptance Criteria

- [ ] `WI-5222`, `TEST-11376`, `PHASE-015`, owner decision, and PAUTH remain linked and current.
- [ ] D/F/H retain 600 turns and 900-second per-operation bounds.
- [ ] D/F/H provider sessions receive exactly 3,600 seconds.
- [ ] A/B/C/D/F/H dispatcher worker defaults are 4,200 seconds, preserving a 600-second outer completion margin for provider sessions.
- [ ] Document leases and reset-straggler age derive to 4,500 seconds without direct runtime-state edits.
- [ ] Timeout telemetry remains truthful and identifies the configured lifetime source.
- [ ] No role, model, route, eligibility, ranking, credential, or unrelated hunk changes.
- [ ] All spec-derived tests pass and an independent genuine dispatcher-produced LO verdict closes the implementation report.
- [ ] Finalization stages only WI-5222 hunks and its append-only bridge chain.

## Risks / Rollback

The intentional risk is that a legitimate run resembling the historical
1:40:02 H or 4:05:31 D examples will now time out. The owner explicitly accepts
that tradeoff. A second risk is an incorrectly ordered outer timer that kills a
provider before its 60-minute session boundary; the derived-value tests make
that a blocking failure. A third risk is absorbing unrelated dirty work from
the nine overlapping targets; exact patch inspection and hunk-only staging are
mandatory.

Rollback is a focused restoration of the three `28,800` session values and the
`29,400` worker constant plus their exact assertions. Runtime state and lease
files are never edited; normal reconciliation releases any live lease.

## Files Expected To Change

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

## Recommended Commit Type

`fix(dispatcher): calibrate generous execution envelope to 60 minutes`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
