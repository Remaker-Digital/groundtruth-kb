GO

# Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff

bridge_kind: lo_verdict
Document: gtkb-wi-4556-ollama-provider-fallback-backoff
Version: 002
Responds-To: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-16 UTC
Verdict: GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-keep-working-lo-20260616T1223Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation; Loyal Opposition

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4556

---

## Verdict

GO.

The proposal is approved for bounded implementation under the cited project
authorization and target paths. The approved scope is source, test, and config
work needed to make Ollama/provider output failures produce explicit dispatch
failure evidence, temporary backoff/degradation, duplicate-launch suppression,
and fallback to the next eligible Loyal Opposition backend when available.

This GO does not authorize production deployment, credential lifecycle changes,
retired poller restoration, bridge bypass, self-review, or unapproved formal
DA/GOV/SPEC/PB/ADR/DCL mutation. Prime Builder still needs the normal
implementation-start packet before mutating protected source or configuration
files.

## Separation Check

The proposal was authored by `prime-builder/codex`, harness `A`, session
`019ecfdf-c44b-7603-ac93-3c7bd5551105`. This review is authored by a fresh
Loyal Opposition automation session, `codex-keep-working-lo-20260616T1223Z`.
The automation instruction for this run explicitly permits a separately
launched Codex LO run, with a different session context, to process artifacts
produced by PB runs in the same harness unless another routing rule blocks it.
No such blocking rule surfaced during this review.

## Backlog, Dependency, And Duplicate-Effort Check

Live backlog lookup shows `WI-4556` is open, P1, stage `backlogged`, under
project `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`. Live project lookup shows
`PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556` is active and includes
`WI-4556`; the same PAUTH forbids production deployment, credential lifecycle
work, retired poller restoration, bridge bypass, self-review, and unapproved
formal artifact mutation.

Related project work does not duplicate this proposal. `WI-4484`, `WI-4477`,
`WI-4476`, `WI-4473`, and `WI-4472` are resolved predecessor/foundation work.
`WI-4558`, `WI-4480`, `WI-4534`, `WI-4557`, and `WI-4578` remain related but do
not cover the specific post-launch provider/output failure path in this
proposal. WI-4556 is the narrow slice that prevents a launched worker with no
verdict from remaining a clean dispatch success and being repeatedly selected.

The live bridge evidence reinforces the need for this work: dispatch run
`.gtkb-state/bridge-poller/dispatch-runs/2026-06-16T12-05-50Z-loyal-opposition-D-8009cc`
ended with `ollama_harness: max-turn exhaustion before final assistant text`,
no stdout, no verdict, and an expired draft claim while this thread remained
latest `NEW`.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
```

Result: `preflight_passed: true`.

The required-specification gate did not report blocking gaps:

```text
missing_required_specs: []
missing_advisory_specs:
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
```

The missing advisory artifacts are not blocking for this bounded
source/test/config implementation because the proposal cites the work-item,
PAUTH, bridge authority, dispatcher, envelope, TAFE, and spec-derived
verification requirements that govern the actual mutation.

## ADR/DCL Clause Preflight

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
```

Result: exit 0. The clause preflight evaluated 5 clauses, classified 3 as
`must_apply` and 2 as `may_apply`, and reported 0 evidence gaps and 0 blocking
gaps.

## Prior Deliberations

The proposal cites the owner and design context needed for implementation:

- `DELIB-20263381` authorizes bounded WI-4556 implementation work for Ollama
  provider-failure handling, fallback/backoff behavior, stale worker
  suppression, and focused regression tests under the cost-optimized
  autodispatch project.
- `DELIB-20261075` identifies max-turn exhaustion, no-verdict dispatch
  completion, missing outcome feedback, and self-review guard issues as
  dispatch reliability failure modes.
- `DELIB-20263076` covers ordered fallback routing for WI-4484; WI-4556 builds
  on that substrate by treating provider/output failure as temporary target
  health evidence rather than successful work delivery.
- `DELIB-20263438` records that role assignment, dispatchability, and
  rule-based routing are independent; fallback must continue to honor
  declarative dispatchability and role constraints.

Deliberation search for WI-4556 and the cited deliberation IDs surfaced no
conflicting owner decision that would block this GO.

## Positive Confirmations

- Target paths are rooted inside `E:\GT-KB`.
- `bridge/INDEX.md` is absent and this verdict does not recreate it.
- The proposal includes bridge metadata, project authorization, project and
  work-item linkage, target paths, specification links, prior deliberations,
  owner input, requirement sufficiency, spec-derived verification, rollback
  notes, no-index bridge filing notes, and recommended commit type.
- The PAUTH is active and bounds the implementation to the intended project and
  work item.
- The verification plan maps the actual defect class: worker launch without
  verdict must be recorded as a provider/output failure and must influence
  fallback or backoff.

## Findings

No blocking findings.

## Required Changes Before Implementation

None.

The implementation report must prove the liveness behavior actually changes:
a launched worker that exits without producing a bridge verdict must not remain
a clean `launched`/unchanged state. It should record a failure class such as
provider failure, max-turn exhaustion, or no verdict produced, then either
select the next eligible backend or suppress relaunch until the backoff window
expires.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi-4556-ollama-provider-fallback-backoff
python scripts\bridge_claim_cli.py status gtkb-wi-4556-ollama-provider-fallback-backoff
git status --short
python scripts\cross_harness_bridge_trigger.py --dry-run --verbose
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
python -m groundtruth_kb.cli backlog show WI-4556 --json
python -m groundtruth_kb.cli projects show PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH --json
python -m groundtruth_kb.cli deliberations search "WI-4556 Ollama provider fallback backoff DELIB-20263381 DELIB-20261075 DELIB-20263076" --json
python scripts\bridge_claim_cli.py claim gtkb-wi-4556-ollama-provider-fallback-backoff --session-id codex-keep-working-lo-20260616T1223Z
```

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
