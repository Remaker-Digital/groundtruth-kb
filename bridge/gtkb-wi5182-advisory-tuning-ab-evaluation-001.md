NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

# Advisory-only dispatch tuning and A/B evaluation

bridge_kind: prime_proposal
Document: gtkb-wi5182-advisory-tuning-ab-evaluation
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-11 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5182-ADVISORY-TUNING-20260711
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5182

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatch_tuning_advisory.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/groundtruth_kb/test_dispatch_tuning_advisory.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_tuning_cli.py"]

implementation_scope: source | test_addition | cli_extension | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

After WI-5180 is independently implemented and verified, add a deterministic
advisory-only evaluation surface that emits `gtkb.dispatch_tuning_advisory.v1`
from immutable references to canonical metrics, benchmark, adaptation, and
approved scoring evidence. It will produce only `recommend`,
`do_not_recommend`, or `insufficient_evidence`; it will never apply a
recommendation or alter live dispatch.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCH-ADVISORY-TUNING-AB-EVALUATION-001`
fully specifies evidence inputs, outcome vocabulary, data-sufficiency behavior,
offline or shadow isolation, immutable reproducibility, privacy, cost labeling,
and the mandatory fail-closed production boundary. The active PAUTH confines
future work to the four declared paths and excludes all dispatcher,
configuration, registry, production scoring, claim, or production-state
mutation.

## Dependency Gate

WI-5180 is the canonical default-metrics provider and is not yet independently
VERIFIED. This proposal may be reviewed now, but implementation must not start
until WI-5180 is terminal and the normal independent GO, matching claim, and
implementation-start gates are live. WI-4969, WI-4792, and approved dispatch
scoring snapshots remain read-only predecessor evidence; no predecessor may be
reopened without a newly substantiated defect.

## In-Root Placement Evidence

All declared targets and this bridge artifact are inside `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/dispatch_tuning_advisory.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`,
`platform_tests/groundtruth_kb/test_dispatch_tuning_advisory.py`, and
`platform_tests/groundtruth_kb/cli/test_bridge_dispatch_tuning_cli.py`. No
external live dependency, provider call, or application-isolation exception is
introduced.

## Specification Links

- `SPEC-DISPATCH-ADVISORY-TUNING-AB-EVALUATION-001` defines advisory outcomes, evidence requirements, isolation, privacy, and the fail-closed production boundary.
- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` defines the sole canonical default-metrics snapshot authority this work may read.
- `SPEC-HARNESS-OBSERVABILITY-SELF-TUNING-PROGRAM-001` preserves the child ordering and prevents advisory evidence from becoming autonomous tuning.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` require PAUTH, independent GO, matching claim, and implementation-start evidence before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires executed specification-derived tests before independent VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` requires all live targets and authority to remain in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` preserve advisory, approval, test, report, and verification lineage without treating captured evidence as a production decision.

## Prior Deliberations

- `DELIB-202666091` records the owner's explicit approval of `SPEC-DISPATCH-ADVISORY-TUNING-AB-EVALUATION-001`.
- `DELIB-202666092` records the owner's explicit `Approve WI-5182 PAUTH` decision.
- `DELIB-20260702-DISPATCH-SCORING-SNAPSHOT-PROMOTION` is the governed predecessor decision that permits advisory evidence but not production application.
- WI-4969 and WI-4792 are terminal evidence sources for benchmark quality and adaptation impact; this proposal does not reopen either item.

## Owner Decisions / Input

- `DELIB-202666091` is the governed specification-only approval for the advisory-tuning child.
- `DELIB-202666092` authorizes `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5182-ADVISORY-TUNING-20260711`.
- The PAUTH authorizes this proposal only. Protected implementation remains blocked until WI-5180 is independently VERIFIED, an independent Loyal Opposition GO is live, and a matching work-intent claim plus implementation-start packet are present.

## Proposed Scope

1. Add an allowlisted, deterministic advisory evaluator that accepts immutable or content-addressed references to a canonical metrics snapshot, benchmark evidence, adaptation evidence, and an approved scoring snapshot.
2. Emit a bounded `gtkb.dispatch_tuning_advisory.v1` payload with hypothesis, target dimension, baseline and candidate identities, comparison mode, population, filters, window, sample-sufficiency rule, coverage, quality and guardrail measurements, separately labeled costs, limitations, and advisory-only rationale.
3. Return `insufficient_evidence` for stale, incomplete, malformed, untraceable, or insufficient input; never upgrade missing evidence to a positive recommendation.
4. Expose only a read-only evaluation command beneath the existing bridge dispatch CLI family. Its output describes an advisory; it has no activation or apply command.
5. Add focused module and CLI coverage for determinism, immutability, isolation, privacy, cost separation, insufficient evidence, and rejected production activation.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Deterministic immutable evaluation | Feed the same content-addressed fixtures in different order and assert byte-equivalent advisory payload, stable evidence references, and one allowed outcome. |
| Complete evidence declaration | Assert the emitted advisory includes the required hypothesis, dimension, baseline, candidate, mode, population, filters, source window, sample rule, coverage, metrics, guardrails, costs, limitations, privacy class, and advisory-only rationale. |
| Insufficient evidence | Exercise stale, incomplete, malformed, untraceable, and undersized evidence; assert `insufficient_evidence` and no positive recommendation. |
| Offline or shadow isolation | Assert only offline, synthetic, benchmark, and shadow modes are accepted, and candidate data cannot influence a live work-assignment path. |
| Production fail-closed boundary | Attempt every activation or apply entry point without a separate future authorization chain; assert rejection and byte-identical dispatcher configuration, registry, routing, selection, caps, and production scoring snapshot. |
| Privacy and cost semantics | Assert output excludes prompt, message, generated text, tool argument or result, provider-body, credential, secret, and environment content, while keeping provider-reported and benchmark-estimated cost distinct. |
| CLI contract | Exercise the bounded read-only command; assert its JSON is deterministic and no competing command or mutating subcommand is registered. |

Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatch_tuning_advisory.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_tuning_cli.py -q --tb=short`, then broaden to the canonical metrics, scoring, and relevant benchmark suites. Run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` over the four declared Python paths.

## Acceptance Criteria

- Every valid evaluation emits one deterministic advisory payload with immutable evidence linkage and an explicit advisory-only statement.
- Insufficient or unsafe evidence yields `insufficient_evidence`, not a recommendation.
- Evaluation modes are offline, synthetic, benchmark, or shadow-only; candidates never influence live assignment.
- No dispatch, configuration, registry, production scoring, claim, or production-state mutation is possible through the feature.
- An attempted production activation fails closed without the separate future authorization chain.
- Cost labels remain separate and prohibited content never appears.

## Risks / Rollback

- Risk: an advisory appears to be an applied configuration change. Mitigation: use a distinct advisory schema and assert no apply or activation route exists.
- Risk: incomplete evidence produces false confidence. Mitigation: validate provenance, freshness, coverage, and sample sufficiency before allowing a positive outcome.
- Risk: a candidate arm affects production. Mitigation: accept only isolated modes and assert every production mutation surface remains byte-identical.
- Risk: sensitive evidence leaks through a serializer. Mitigation: construct output from an explicit aggregate allowlist and run prohibited-content checks.
- Rollback: revert the single implementation commit; no production dispatcher state or scoring snapshot needs reversal.

## Pre-Filing Preflight Subsection

Candidate-content applicability and ADR/DCL clause preflights will run against
this completed proposal before the status-bearing bridge file is written.
Filing is permitted only when both report no blocking gap.

## Bridge Filing

This proposal will be filed as the next numbered file under `bridge/` for
`gtkb-wi5182-advisory-tuning-ab-evaluation`. The numbered bridge files are
append-only; no prior version is deleted or rewritten, and the versioned chain
plus dispatcher or TAFE state remains the live workflow authority.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatch_tuning_advisory.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/groundtruth_kb/test_dispatch_tuning_advisory.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_tuning_cli.py`

## Recommended Commit Type

`feat`
