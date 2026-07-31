REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T17-09-58Z-prime-builder-A-41e0e1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; role prime-builder; approval_policy=never; sandbox=workspace-write; reasoning_effort=xhigh

# REVISED Blocker Record - WI-5047 dispatcher budget model update still needs governed control-surface authority

bridge_kind: implementation_report
Document: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch
Version: 005 (REVISED; blocker response)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC
Responds to: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-004.md
Prior report: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md
Responds to GO: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-002.md
Approved proposal: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5047
work_item_ids: [WI-5047]

target_paths: [".api-harness/routing.toml", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "groundtruth.db", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/tests/test_doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

implementation_scope: blocker_record_only
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
additional_owner_authority_required: true
Recommended commit type: docs(governance)

---

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-004.md`.

No source, test, configuration, MemBase, dispatcher-state, credential, deployment, or git-history mutation was attempted in this dispatch. The selected work remains blocked because the already-applied partial WI-5047 change cannot be verified until `config/dispatcher/rules.toml` reports `budget.harnesses.D.model = "kimi-k2-7-code-cloud"`, and the only governed dispatcher-control surface available in this checkout still lacks a transaction for that budget model field.

Directly editing `config/dispatcher/rules.toml` remains prohibited by `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`. Adding the missing `gt bridge dispatch config set-model` capability would require protected source/test changes outside the current WI-5047 target-path and mutation-class authority. This headless worker cannot collect fresh owner authority or mint a broader PAUTH. This artifact therefore records the blocker in the append-only bridge chain and stops.

## Requirement Sufficiency

New or revised requirement required before implementation.

Existing owner decision `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` authorizes the desired end state: switch Ollama/D to Kimi and update the necessary dispatcher model-label/status metadata. It does not, in the currently active PAUTH for this thread, authorize source-level dispatcher control-surface implementation.

The next implementation-ready path requires one of these interactive owner-authority outcomes:

1. A new or expanded PAUTH/work item that explicitly permits protected source and test changes for a dispatcher budget-model transaction, followed by a separate bridge proposal and Loyal Opposition `GO`.
2. An owner-approved alternative governed path that changes the dispatcher budget model metadata without bypassing `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`.

This auto-dispatch cannot choose either path or fabricate authority for it.

## First-Line Role Eligibility And Work-Intent Claim

Role resolution and actionability were checked before this `REVISED` draft was prepared:

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
```

Observed result: harness `A` (`codex`) resolves to role `prime-builder`.

```text
groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch --json --compact
```

Observed result:

```json
{
  "compact": true,
  "latest_path": "bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-004.md",
  "latest_status": "NO-GO",
  "slug": "gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch",
  "version_count": 4
}
```

Work-intent claim acquired for this dispatch:

```json
{
  "acquired_at": "2026-07-06T17:17:33Z",
  "acting_role": "prime-builder",
  "claim_kind": "draft",
  "project_id": "PROJECT-HARNESS-EQUIVALENCE-PHASE-3",
  "rowid": 30425,
  "session_id": "2026-07-06T17-09-58Z-prime-builder-A-41e0e1",
  "thread_slug": "gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch",
  "ttl_expires_at": "2026-07-06T17:27:33Z"
}
```

Prime Builder is authorized to respond to latest `NO-GO` with `REVISED`. Prime Builder is not authorized to author `GO`, `NO-GO`, or `VERIFIED`.

## Blocking Evidence

The partial WI-5047 implementation remains in the same state reported by `-003` and confirmed by `-004`.

Active Ollama routing points to Kimi:

```text
.api-harness/routing.toml
[routing.ollama].default_model = "kimi-k2-7-code-cloud"
[routing.ollama.skills].bridge-review = "kimi-k2-7-code-cloud"
[routing.ollama.skills].verification = "kimi-k2-7-code-cloud"
[routing.ollama.skills].implementation = "kimi-k2-7-code-cloud"
[models.kimi-k2-7-code-cloud].model_id = "kimi-k2.7-code:cloud"
```

Harness D headless argv points to Kimi:

```json
["groundtruth-kb/.venv/Scripts/python.exe","scripts/ollama_harness.py","-p","{{PROMPT}}","--skill","bridge-review","--model","kimi-k2-7-code-cloud"]
```

Dispatcher budget metadata still points to DeepSeek:

```text
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch config --json
budget.harnesses.D.model = "deepseek-v4-pro-cloud"
```

The dispatcher control surface still exposes only these mutating config commands:

```text
add-harness
remove-harness
set-caps
set-eligibility
set-rule
set-weights
```

There is no `set-model`, `set-budget-model`, or equivalent transaction in the live `gt bridge dispatch config --help` output. Read-only source inspection confirms `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` has setters for eligibility, weights, caps, rules, and add/remove harnesses, but no budget model setter.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - the remaining defect is owner-visible model identity drift between D runtime routing and dispatcher budget/status metadata.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state and selected target behavior must remain truthful and governed.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher config changes must be made through governed control/status surfaces.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - direct edits to `config/dispatcher/rules.toml` are prohibited; the missing CLI transaction is the active blocker.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - source-level follow-up work needs explicit bounded project authorization before implementation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder may file this `REVISED` blocker record after latest `NO-GO` but cannot self-review or implement outside a live `GO` packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target-path metadata remain declared.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries forward the governing specification links and explicitly names the additional authority gap.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - no verification request is made because the accepted implementation is incomplete.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - this bridge file is filed through the Codex helper-mediated path, not a raw bridge write.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the blocker is preserved as governed bridge state rather than chat or scratch memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source-control-surface expansion needs durable authorization and bridge review.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the repeated automated dispatch cycle is a lifecycle signal requiring owner-held or headless-ineligible disposition.
- `GOV-STANDING-BACKLOG-001` - `WI-5047` remains the durable backlog authority for the model route switch.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this work remains platform harness configuration; no `applications/` or Agent Red files are in scope.

## Owner Decisions / Input

Carried-forward owner/project authority:

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - owner decision to switch Ollama/D to `kimi-k2.7-code:cloud` and update necessary routing, harness projection, dispatcher model-label/status metadata, and focused tests.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706` - bounded implementation authorization for the original WI-5047 target paths and mutation classes.

Required owner-authority artifact is absent in this headless dispatch: no new or expanded PAUTH currently authorizes protected source/test changes for a dispatcher budget-model transaction. This worker cannot interactively present AskUserQuestion or decide that the existing owner decision should be stretched into a broader source-control-surface authorization.

If Loyal Opposition sustains this blocker, Prime Builder asks Loyal Opposition to include the exact latest-verdict marker `**Hold for Owner Decision:**` in its next `NO-GO` verdict so the verified owner-hold dispatch suppression mechanism keeps this thread visible to interactive Prime Builder while preventing further headless Prime redispatch loops.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - owner decision for the Kimi route switch and dispatcher model-label/status update target.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - prior DeepSeek route decision, superseded for this forward work.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - owner deliberation identifying harness/model metadata truthfulness and dispatcher reliability as release-relevant.
- `DELIB-20266507` - owner authorization for dispatcher health repair; adjacent context only, not an authorization for this WI-5047 source-surface expansion.
- `bridge/gtkb-wi4885-owner-hold-dispatch-suppression-004.md` - VERIFIED owner-hold suppression mechanism for latest `GO` or `NO-GO` verdicts.
- `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-004.md` - VERIFIED headless-ineligible suppression precedent for explicit latest-verdict language.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` - approved proposal.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-002.md` - Loyal Opposition `GO`.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md` - Prime Builder partial implementation/blocker report.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-004.md` - Loyal Opposition `NO-GO` confirming stale dispatcher budget metadata and missing control-surface transaction.

## Findings Addressed

### P1 - Stale dispatcher configuration metadata

Status: accepted and still blocked.

The necessary end state is clear: D dispatcher budget metadata must report `kimi-k2-7-code-cloud`. The authorized mutation path is not available in the current control surface, and direct TOML mutation remains prohibited. No new implementation was attempted.

### P1 - Separate dispatcher control-surface proposal required

Status: accepted as the safe follow-up shape, but not filed by this headless worker.

A separate implementation proposal for a `gt bridge dispatch config set-model` or equivalent transaction needs protected source/test target paths and an owner-authority artifact/PAUTH that is not present in this selected dispatch context.

## Scope Changes

No source, test, configuration, MemBase, dispatcher transaction state, deployment, credential, or git-history scope changes were made by this response.

This revision adds one bridge audit artifact only:

- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-005.md`

## Pre-Filing Preflight Subsection

Candidate-content preflights are executed against this completed draft before live filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-005.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-005.md
```

Observed applicability result for this completed content:

- `packet_hash`: `sha256:dc14f6e5b894616c5ea8fc2c25577b0ece1e3860b9afe56bbbcd368204716b24`
- `preflight_passed`: `true`
- `missing_required_specs`: []
- `missing_advisory_specs`: []
- `content_source`: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-005.md`

Observed clause applicability result for this completed content:

- Bridge id: `gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`
- Clauses evaluated: 5
- `must_apply`: 3
- `may_apply`: 2
- `not_applicable`: 0
- Evidence gaps in must-apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory; exit 0 = pass.

The governed revision helper repeats these gates before writing the live bridge file.

## Specification-Derived Verification

This blocker record performs no implementation, so verification is limited to live-state checks proving the blocker remains and no verification is requested.

| Specification / governing surface | Command evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show ... --json --compact`; `bridge_claim_cli.py claim ...` | Latest status was `NO-GO` at `-004`; Prime Builder claim row `30425` was acquired; `REVISED` is role-correct. |
| `ADR-CROSS-HARNESS-PARITY-001` | `gt bridge dispatch config --json`; harness registry argv read; `.api-harness/routing.toml` read | D route and headless argv point to Kimi, while dispatcher budget metadata still points to DeepSeek. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` / `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | `gt bridge dispatch config --help`; source read of `bridge_dispatch_transactions.py` | No governed budget-model setter exists; direct config edit remains prohibited. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PAUTH scope carried from the approved thread; `gt backlog authorize-implementation --help` | Broader source/test authority requires owner-decision evidence; this worker did not create one. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report's explicit no-implementation posture | No `VERIFIED` request is made. |

## Dispatch Blocker Note

Repeated headless Prime dispatch cannot resolve this thread until an interactive owner-authority path exists for the missing dispatcher control-surface transaction. If Loyal Opposition agrees the blocker remains valid, its next `NO-GO` should use the exact marker `**Hold for Owner Decision:**` or explicit headless-ineligible language so the dispatcher does not keep sending this owner-authority gap to unattended Prime workers.

## Risk And Rollback

Risk: another blocker-only `REVISED` can continue the headless dispatch loop if the next Loyal Opposition verdict does not activate owner-hold or headless-ineligible suppression.

Risk: the partial WI-5047 state remains truthful for runtime D dispatch but not for dispatcher budget/status metadata. The thread should stay visible for interactive Prime Builder until the missing authority and control-surface transaction are resolved.

Rollback is not applicable to this response because it changes no implementation targets. Bridge audit files are append-only; correction is by filing the next numbered bridge artifact.

## Recommended Commit Type

`docs(governance)` - append-only blocker record; no implementation files are changed.

File bridge scan contribution: 1 entry processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
