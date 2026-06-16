NEW

# gtkb-parallel-dispatch-remediation-sweep-umbrella — Parallel Dispatch Remediation Sweep Umbrella

bridge_kind: prime_proposal
Document: gtkb-parallel-dispatch-remediation-sweep-umbrella
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-A-2026-06-16-parallel-dispatch-remediation
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop, GT-KB Prime Builder session, owner-requested dispatch remediation investigation

Project Authorization: PAUTH-PARALLEL-DISPATCH-REMEDIATION-SWEEP-001
Project: PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP
Work Item: WI-4594

target_paths: ["groundtruth.db", ".gtkb-state/owner-decision-inputs/parallel-dispatch-remediation-sweep-20260616.md", "bridge/gtkb-parallel-dispatch-remediation-sweep-umbrella-*.md"]

implementation_scope: governance, protocol, backlog_decomposition
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This is an umbrella remediation proposal for flaws found in bridge dispatch,
registered harness behavior, transcript/session-envelope evidence use, and
governance adherence during prior dispatched reviews. It creates no permission
to change dispatch source directly. It asks Loyal Opposition to review the
evidence, decompose the umbrella into specific child work items/slices, and
return GO only if the decomposition boundary is adequate.

The project/backlog setup already exists:
`PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP`, umbrella work item `WI-4594`,
linked manual acceptance test `TEST-11161`, owner decision `DELIB-20263456`,
and bounded authorization `PAUTH-PARALLEL-DISPATCH-REMEDIATION-SWEEP-001`.
The PAUTH allows bridge proposal authoring, backlog decomposition, and project
metadata only. It forbids direct protected-source mutation, source
implementation without child GO, and retired poller restoration.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge state must remain append-only and governed through status-bearing bridge files and live dispatcher/TAFE state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this umbrella must cite the dispatch, role, and bridge-governance requirements before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — child WIs must include spec-derived tests before any VERIFIED outcome.
- `GOV-STANDING-BACKLOG-001` — discovered risks are preserved as backlog/project records instead of chat-only observations.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — dispatch remediation evidence should remain connected across decisions, work items, proposals, tests, and reports.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — child remediation items should use explicit lifecycle states rather than ambiguous chat or queue status.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the transcript-backed risks are durable governance artifacts, not informal observations.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — central dispatch must expose real dispatch readiness and delivery semantics, not just launch attempts.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — dispatch work needs a durable envelope with identity, role, selected work, target, and outcome evidence.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch envelopes must be consistent enough for review, retry, and health decisions.
- `GOV-SESSION-ROLE-AUTHORITY-001` — role and dispatch authority must remain split between durable registry state and session-scoped overrides.
- `DCL-SESSION-ROLE-RESOLUTION-001` — dispatch prompts and harness workers must resolve role from the canonical registry/projection path.

## Prior Deliberations

- `INTAKE-f8bc08a3` — Intake: Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations
- `INTAKE-a815f782` — Intake: Bridge dispatch suppression scoped per bridge document (per-document lease)
- `INTAKE-2ce995f2` — Intake: Enable bounded parallel cross-harness auto-dispatch (supersede binary same-role active-session suppression)
- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` — TAFE Phase 1 R4 dispatch-track implementation authorization (WI-4497/4498/4499)
- `DELIB-S424-RESTORE-SCHEDULED-POLLER-001` — Restore Scheduled Poller Scanning with Deduplicated Dispatch
- `DELIB-20263456` — owner decision authorizing this project/backlog record and umbrella proposal filing.

The intake and TAFE deliberations are relevant because this umbrella is about
bounded parallel dispatch, per-document suppression/leases, and central
dispatcher health. The scheduled-poller deliberation is historical context only:
this proposal explicitly forbids retired poller restoration and instead asks for
reviewer decomposition around the current cross-harness/TAFE path.

## Owner Decisions / Input

- `DELIB-20263456` / `AUQ-PARALLEL-DISPATCH-REMEDIATION-SWEEP-20260616` records the owner request: search for dispatch/harness/governance flaws using transcripts, record them, create the project/backlog item, file an umbrella proposal, and ask the reviewer to decompose it into specific work items.
- Approval packet: `.groundtruth/formal-artifact-approvals/2026-06-16-DELIB-20263456.json`.
- Decision content file: `.gtkb-state/owner-decision-inputs/parallel-dispatch-remediation-sweep-20260616.md`.

No additional owner decision is required for the reviewer to decompose this
umbrella. Any child work that changes protected source/config files still needs
its own GO and implementation authorization.

## Requirement Sufficiency

Existing requirements sufficient for umbrella decomposition.

The linked dispatch, bridge, backlog, and session-role specs are sufficient for
Loyal Opposition to decide whether this umbrella is a valid decomposition
request and what child WIs/slices are required. New or revised requirements may
be required by specific child WIs before source implementation; those decisions
belong in the child proposals, not this umbrella.

## Findings To Decompose

1. **Dispatch health can PASS without delivery evidence.**
   `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py:216-253`
   computes health from config errors, active event sources, role holders, and
   dispatchable candidates. It does not incorporate launch exit codes, verdict
   production, backoff state, or post-dispatch diagnostics. Live health reported
   PASS while `.gtkb-state/cross-harness-trigger/dispatch-runs/2026-06-16T17-01-42Z-loyal-opposition-D-11aae7.exit_code`
   contained `4294967295` and
   `.gtkb-state/cross-harness-trigger/dispatch-diagnostic-post.jsonl` recorded
   `verdict_path: null`.

2. **Readiness defaults to ready for missing verifier helpers.**
   `scripts/cross_harness_bridge_trigger.py:2031-2054` returns
   `{"ready": True}` when `scripts/verify_<harness>_dispatch.py` is absent.
   Current verifier presence check showed Ollama and Antigravity verifiers
   exist, but Codex, OpenRouter, and Claude verifiers do not.

3. **Cheap-first LO ranking keeps selecting weak/failed targets.**
   `config/dispatcher/rules.toml` ranks NEW/REVISED Loyal Opposition work by
   `cost`, then availability, quality, reviewer precedence, and harness id.
   The same config ranks Ollama D at cost 5 / quality 62 and OpenRouter F at
   cost 20 / quality 72. Live dispatch state selected D first while recent
   failure logs show abrupt process exits and no-verdict diagnostics.

4. **Launch/outcome accounting is split and easy to misread.**
   `scripts/cross_harness_bridge_trigger.py:2923-3027` processes exit codes and
   can record `no_verdict_produced`, but
   `scripts/cross_harness_bridge_trigger.py:3704` sets `last_result` to
   `launched` immediately after spawn. Health/status surfaces do not yet merge
   `dispatch-state.json`, `dispatch-failures.jsonl`, and
   `dispatch-diagnostic-post.jsonl` into a single delivery verdict.

5. **Headless dispatch lacks an owner-present / headless-ineligible gate.**
   Transcript-derived handoff records show repeated headless stand-downs on
   owner-gated work:
   `memory/dispatched-2026-06-11-fab04-fab01-stand-down.md:16-24`,
   `memory/dispatched-2026-06-11-fab04-fab01-stand-down.md:95-104`,
   and
   `memory/dispatched-2026-06-11T20Z-fab01-fab03-stand-down.md:100-109`.
   `memory/dispatched-2026-06-11T20Z-fab04-git-reclamation-executed.md:30-40`
   records a headless overstep on AUQ-gated FAB-04 maintenance before the
   campaign gate was read.

6. **Work-intent claims still have attribution and race risks.**
   `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:274` records a
   claim acquired under a remote Claude session id for a thread that session did
   not touch. `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:296`
   records the broader flat-file O_EXCL/Windows rename race and session-id leak
   risk.

7. **SDK harness Bash can bypass bridge-compliance parity.**
   `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:362` records that
   OpenRouter and Ollama SDK harness `Bash` dispatch can mutate `bridge/*.md`
   without invoking bridge-compliance guards, while Write/Edit are guarded.

8. **Self-review and same-harness fallback needed a repair and deserves a
   broader invariant.** The fallback report
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/LO-BRIDGE-DISPATCH-SELF-REVIEW-FALLBACK-2026-06-13.md`
   records a defect where same-harness refusal stopped fallback instead of
   continuing to the next eligible reviewer.

9. **Registered harness parity is incomplete.**
   `harness-state/harness-registry.json` has active dispatch targets A/C/D/F and
   suspended B. Current verifier scripts are uneven, and
   `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:283` records
   Claude/Codex-only harness parity assumptions ignoring Antigravity/Ollama.

10. **Transcript/session evidence is not integrated into dispatch routing.**
    Session envelope archives exist under `harness-state/*/session-envelope-archive/`,
    and `bridge/gtkb-transcript-scan-dispatch-role-sot-007.md` /
    `bridge/gtkb-transcript-scan-dispatch-role-sot-008.md` repaired stale
    role-SoT prompt guidance. The remaining issue is that transcript-derived
    governance blockers, owner-present requirements, and repeated stand-down
    classes are not first-class dispatch routing inputs.

## Reviewer Decomposition Request

Loyal Opposition is asked to decompose this umbrella into specific child work
items and return them in the verdict. Suggested decomposition axes:

- dispatch health/readiness: fail-closed verifier coverage for all active
  dispatchable harnesses and health that reflects delivery outcomes;
- outcome telemetry: one authoritative status combining launch, exit code,
  verdict path, provider failure, no-verdict, retry/backoff, and circuit state;
- headless-ineligible routing: a per-thread or per-bridge metadata field for
  owner-present, AUQ-gated, protected-narrative, destructive, or
  uncertain-provenance work;
- work-intent/claim integrity: transaction-backed claims or equivalent
  race-safe/session-safe claim storage;
- SDK harness guard parity: hard-deny or route Bash bridge mutations through the
  same guarded writer path as Write/Edit;
- self-review/author-reviewer separation: invariant coverage across D/F/C/A and
  same-harness fallback;
- ranking/fallback policy: quality-aware and failure-aware reviewer selection
  that does not keep preferring a cheap failing target;
- transcript/session-envelope integration: promote repeated transcript-derived
  governance blockers into dispatch suppression/defer metadata.

## Spec-Derived Verification Plan

This umbrella is successful when the reviewer accepts the decomposition boundary
and the project/backlog records remain visible. Child WIs must carry their own
source-level test plans.

```text
groundtruth-kb/.venv/Scripts/gt.exe projects list --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4594 --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch config --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short -k "dispatch_prompt or provider_failure_backoff or no_verdict or author_meets_reviewer"
```

Expected result for this umbrella review:

| Specification | Verification evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge preflights on this proposal and append-only bridge filing. | No missing required specs; no status rewrite. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal metadata includes PAUTH/project/WI. | Review can trace to `PAUTH-PARALLEL-DISPATCH-REMEDIATION-SWEEP-001`, `PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP`, and `WI-4594`. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4594 --json`. | Umbrella backlog item exists with linked test `TEST-11161`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` | Reviewer confirms child WIs cover readiness, delivery, routing, telemetry, and claim/envelope gaps. | Decomposition is complete enough to prevent direct broad implementation. |
| `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` | Child decomposition includes registered harness/role verifier coverage and transcript/session-envelope integration. | Role and harness authority remain canonical and testable. |

## Risk / Rollback

Risk is over-broad remediation: a single umbrella could accidentally authorize
too much source work. This proposal mitigates that by limiting direct scope to
project/backlog/bridge metadata and asking for child WIs before implementation.
Rollback is to mark this bridge thread NO-GO/WITHDRAWN and retire or supersede
`WI-4594`; do not delete `DELIB-20263456`, the PAUTH record, or bridge files.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-parallel-dispatch-remediation-sweep-umbrella`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

chore

Justification: this proposal creates governance/backlog/bridge metadata and
does not implement source behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
