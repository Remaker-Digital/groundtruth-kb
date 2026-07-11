NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

# Report-metrics enrichment from the canonical default snapshot

bridge_kind: prime_proposal
Document: gtkb-wi5181-report-metrics-enrichment
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-11 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5181-REPORT-METRICS-20260711
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5181

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source | test_addition | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

After WI-5180 is independently implemented and verified, enrich only the
existing `gt bridge dispatch report` compact JSON workflow view and human
workflow view from the latest valid canonical default-metrics snapshot. Keep
the full `gt bridge dispatch report --json` contract unchanged, preserve the
existing status, in-flight, and role queues, and introduce no competing report
or metrics command.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCH-REPORT-METRICS-ENRICHMENT-001`
defines the dependency, exact report variants, snapshot-only source, bounded
metric categories, explicit null and availability semantics, full-JSON
preservation, privacy boundary, read-only behavior, and acceptance criteria.
The active PAUTH limits future work to the two declared paths and excludes
provider calls, raw-runtime recomputation, sensitive content, dispatcher or
role mutation, claims, production state, tuning, deployment, and competing
report or metrics stores.

## Dependency Gate

WI-5174 is terminal. WI-5180 is the required upstream canonical default-metrics
snapshot provider and is not yet independently VERIFIED. This proposal may be
reviewed now, but implementation must not start until WI-5180 reaches its
canonical terminal state and the normal independent GO, matching claim, and
implementation-start gates are live.

## In-Root Placement Evidence

All declared targets and this bridge artifact are inside `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py` and
`platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`. No
external live dependency or application-isolation exception is introduced.

## Specification Links

- `SPEC-DISPATCH-REPORT-METRICS-ENRICHMENT-001` controls snapshot-only compact and human enrichment, full-JSON preservation, availability semantics, privacy, and read-only acceptance criteria.
- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` defines the sole canonical snapshot authority and its bounded, nullable, coverage-aware metrics contract.
- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` preserves the existing report surface, role-actionability queues, and bounded compact workflow contract.
- `SPEC-HARNESS-OBSERVABILITY-SELF-TUNING-PROGRAM-001` keeps this child observational and separate from diagnostic, snapshot, and advisory-tuning work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` require PAUTH, independent GO, matching claim, and implementation-start evidence before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires executed spec-derived tests before independent VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` requires all live targets and authority to remain in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` preserve approval, proposal, test, report, and verification lineage without treating their capture as implementation approval.

## Prior Deliberations

- `DELIB-202666088` records the owner's explicit approval of `SPEC-DISPATCH-REPORT-METRICS-ENRICHMENT-001`.
- `DELIB-202666087` records the owner's explicit `Approve WI-5181 PAUTH` decision.
- `DELIB-202666085` and `bridge/gtkb-wi5180-default-dispatch-metrics-snapshot-001.md` establish the owner-authorized upstream snapshot provider; WI-5180 remains an implementation dependency, not a substitute for its eventual verification.
- WI-5174 terminal bridge and commit evidence establish the existing compact-report surface that this child extends rather than replaces.

## Owner Decisions / Input

- `DELIB-202666088` is the governed specification-only approval for the report-metrics child.
- `DELIB-202666087` authorizes `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5181-REPORT-METRICS-20260711`.
- The PAUTH authorizes this proposal only. Protected implementation remains blocked until WI-5180 is independently VERIFIED, an independent Loyal Opposition GO is live, and a matching work-intent claim plus implementation-start packet are present.

## Proposed Scope

1. Add a bounded `recent_work_metrics` object only to the compact JSON workflow projection, derived solely from the latest valid canonical default-metrics snapshot.
2. Render an equivalent `Recent-work metrics` section only in the existing compact or default human workflow view, after status, in-flight work, and role queues.
3. Preserve existing compact workflow queue semantics and make unavailable, partial, stale, and `null` metrics explicit without suppressing workflow information.
4. Preserve provider-reported cost and benchmark-estimated cost as separate labeled values; do not recompute raw runtime measurements or infer unknown values.
5. Add focused CLI coverage proving full JSON remains unchanged, compact and human views agree on snapshot identity and coverage, output stays bounded and read-only, and unavailable or stale snapshots do not hide queues.

## Existing Target-State Boundary

`platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py` currently
contains a pre-existing foreign uncommitted removal of a module-cache reset
loop. It is outside WI-5181 and must be preserved, not amended, staged, or
claimed by this work. Before implementation, coordinate with the owning change
or construct an additive patch that excludes the foreign hunk; do not use this
proposal to normalize unrelated test drift.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Full JSON compatibility | Capture the established `gt bridge dispatch report --json` fixture contract before and after enrichment; assert no metrics key or semantic change appears in the full JSON payload. |
| Compact snapshot projection | Seed a canonical valid snapshot and assert compact JSON exposes the bounded `recent_work_metrics` identity, schema, source window, freshness, record count, coverage, distributions, and role or harness breakouts. |
| Human parity | Assert the human workflow view renders `Recent-work metrics` with the same snapshot identity, coverage, and explicit availability state as compact JSON. |
| Null, partial, stale, and unavailable | Exercise absent, partial, stale, and null-valued snapshots; assert explicit reason and bounded state while existing status, in-flight, and queues remain present. |
| Cost separation and privacy | Assert provider-reported and benchmark-estimated costs remain separately labeled and serialized output excludes prompt, message, generated text, tool argument or result, provider-body, credential, secret, and environment content. |
| Read-only operation | Snapshot tracked dispatcher configuration, registry, dispatch state, bridge artifacts, and metrics records before report invocation; assert every tracked artifact is unchanged. |

Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` after isolating the pre-existing foreign hunk, then run the affected dispatcher-report and default-metrics suites. Run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` over both declared Python paths.

## Acceptance Criteria

- Full report JSON remains contract-compatible and receives no metrics key.
- Compact JSON and the human workflow view expose equivalent bounded metrics from one latest valid canonical snapshot.
- Missing, partial, stale, and unknown values are explicit and do not hide workflow status, in-flight work, or actionable queues.
- Costs remain source-labeled; no raw data recomputation or unknown-value invention occurs.
- Every report variant remains read-only and content-safe.
- Implementation starts only after WI-5180 is terminal and ordinary bridge/claim gates are satisfied.

## Risks / Rollback

- Risk: metrics accidentally expand the full JSON contract. Mitigation: keep enrichment inside the compact workflow builder and lock the full payload with a regression fixture.
- Risk: stale or absent data masks queues or becomes a false zero. Mitigation: preserve workflow construction order and represent unavailable or unknown state explicitly.
- Risk: raw runtime content leaks into a display projection. Mitigation: accept only the canonical snapshot's approved aggregates and assert prohibited-content exclusions.
- Risk: the foreign test hunk is accidentally absorbed. Mitigation: preserve the hunk exactly and coordinate before touching the file.
- Rollback: revert the single WI-5181 implementation commit; no snapshot, dispatcher, routing, role, claim, configuration, or production-state mutation occurs.

## Pre-Filing Preflight Subsection

Candidate-content applicability and ADR/DCL clause preflights will run against
this completed proposal before the status-bearing bridge file is written.
Filing is permitted only when both report no blocking gap.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
