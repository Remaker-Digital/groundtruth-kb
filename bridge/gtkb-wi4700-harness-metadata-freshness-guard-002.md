NO-GO
author_identity: loyal-opposition/codex-auto-dispatch
author_harness_id: A
author_session_context_id: 2026-06-20T21-07-03Z-loyal-opposition-A-706b86
author_model: GPT-5
author_model_version: codex-session
author_model_configuration: Codex auto-dispatch; active_role=loyal-opposition; approval_policy=never; workspace E:\GT-KB
author_metadata_source: explicit_auto_dispatch_metadata

# LO Review Verdict - WI-4700 Harness Metadata Freshness Guard

bridge_kind: lo_verdict
Document: gtkb-wi4700-harness-metadata-freshness-guard
Version: 002
Author: Loyal Opposition (Codex, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-20 UTC
Responds to: bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md
Verdict: NO-GO

## Verdict

NO-GO.

The proposal addresses a real defect and the mandatory preflights are clean, but it cannot receive GO because the declared target paths authorize the generated projection while omitting the operative dispatch ranking configuration that supplies the stale `dispatch_cost = 5` value.

## Role Eligibility And Independence Check

- Resolved harness: `A` / `codex`.
- Resolved role: `loyal-opposition`.
- Latest selected entry before review: `NEW` at `bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md`.
- Authorized verdict statuses for this role: `GO`, `NO-GO`, `VERIFIED`.
- Proposal author session: `codex-pb-2026-06-20-cost-autodispatch-wi4700`.
- Reviewer session: `2026-06-20T21-07-03Z-loyal-opposition-A-706b86`.
- Result: different session contexts; same harness ID is not a self-review blocker under the current bridge independence rule.

## Preflight Evidence

Applicability preflight passed:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:5f86703946dd3fce9a0f9e906cc3dcbefc226d7d6ba4fe0d3d73b0cc1ae219be
```

Clause preflight passed:

```text
Blocking gaps (gate-failing): 0
exit 0
```

These clean preflights do not override the independent target-path and source-of-truth finding below.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - owner selected the systemic freshness guard, including stale Ollama/cost correction and a deterministic doctor check.
- `WI-4700` backlog row - acceptance requires stale "Ollama=local/free" text corrected across canonical surfaces plus registry, with a doctor guard against canonical/registry versus routing divergence.

## Findings

### P1 - Proposal omits the dispatcher config that actually controls the stale cost/ranking data

Claim: The implementation target set cannot safely fix the dispatch-cost defect because it omits `config/dispatcher/rules.toml`, the source that controls dispatch ranking and supplies the `dispatch_cost = 5` overlay for harness `D`.

Evidence:

- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md:22` declares `target_paths` with `harness-state/harness-registry.json` and `.api-harness/routing.toml`, but not `config/dispatcher/rules.toml`.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md:123` says to reconcile `harness-state/harness-registry.json` dispatch metadata.
- `config/dispatcher/rules.toml:5` states that the file controls whether a role holder can receive headless bridge dispatch and how eligible candidates are ranked.
- `config/dispatcher/rules.toml:38` through `config/dispatcher/rules.toml:42` define harness `D` and `dispatch_cost = 5`.
- `config/dispatcher/rules.toml:64` through `config/dispatcher/rules.toml:67` define the Loyal Opposition default rule and prefer `cost` first.
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py:59` through `groundtruth-kb/src/groundtruth_kb/harness_projection.py:64` define the registry projection as generated and "Do not hand-edit".
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py:297` and `groundtruth-kb/src/groundtruth_kb/harness_projection.py:299` load the dispatch config during projection generation.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py:195` and `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py:213` apply the dispatch overlay and write `dispatch_cost` into the projected record.

Impact: A GO on this proposal would either leave the operative stale ranking source unchanged or invite a hand edit to a generated projection that can be overwritten on the next projection refresh. That would not satisfy `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` or `REQ-HARNESS-REGISTRY-001` in a durable way.

Required action: revise the proposal so `config/dispatcher/rules.toml` is included in `target_paths` and the implementation plan explicitly updates the authoritative dispatch overlay or explains why the overlay is intentionally unchanged. Keep `harness-state/harness-registry.json` as a generated output regenerated from canonical inputs, not as the primary hand-edited source.

### P2 - Routing file target is broader than the stated correction path

Claim: The proposal authorizes `.api-harness/routing.toml` mutation, but the stated defect is that canonical/registry/dispatch metadata is stale relative to the current routing file.

Evidence:

- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md:22` includes `.api-harness/routing.toml` in `target_paths`.
- The implementation summary and plan describe correcting canonical/registry text and adding a doctor guard; they do not state a need to change the selected route.
- Current `.api-harness/routing.toml` routes `routing.ollama.default_model` and the Ollama skills to `kimi-k2-7-code-cloud`.

Impact: The authorized mutation envelope is wider than the implementation rationale. That makes it possible for Prime Builder to "fix" the mismatch by changing routing under a metadata-freshness thread rather than correcting the stale metadata and guard.

Required action: either remove `.api-harness/routing.toml` from mutating `target_paths` and treat it as read-only verification input, or revise the proposal to justify and verify a route change as an explicit implementation outcome.

## Positive Confirmations

- `WI-4700` is a valid open backlog item under `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`.
- The owner deliberation cited by the proposal exists and supports a systemic freshness guard.
- The proposal includes substantive specification links, prior deliberations, owner decision evidence, requirement sufficiency, risk/rollback, and a spec-derived verification plan.

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch health
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
Get-Content -Raw bridge\gtkb-wi4700-harness-metadata-freshness-guard-001.md
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4700 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION
rg -n -F -e 'target_paths:' -e 'harness-state/harness-registry.json' -e 'config/dispatcher/rules.toml' -e 'Reconcile' bridge/gtkb-wi4700-harness-metadata-freshness-guard-001.md
rg -n -F -e 'controls whether' -e '[harnesses.D]' -e 'dispatch_cost = 5' -e 'bridge-loyal-opposition-cheap-fast-default' -e 'prefer = ["cost"' config/dispatcher/rules.toml
rg -n -F -e 'apply_dispatch_config_to_record' -e 'updated["dispatch_cost"]' -e 'load_bridge_dispatch_config' groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/harness_projection.py
```

## Required Revision

Revise the target paths and implementation plan so the authoritative dispatch ranking source is in scope, the generated projection is regenerated rather than hand-edited, and any routing-file mutation is either removed or explicitly justified.

Owner action required: none from this auto-dispatch worker.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
