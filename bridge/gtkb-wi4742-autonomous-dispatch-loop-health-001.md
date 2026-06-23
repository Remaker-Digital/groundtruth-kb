NEW

# gtkb-wi4742-autonomous-dispatch-loop-health - Autonomous dispatch loop health validation and worker-liveness diagnostics

bridge_kind: prime_proposal
Document: gtkb-wi4742-autonomous-dispatch-loop-health
Version: 001
Author: Prime Builder (Codex interactive session)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef2e7-67ab-7f02-9046-bf0a8cbd58a4
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop; interactive Prime Builder override via owner init keyword

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4742

target_paths: ["scripts/autonomous_dispatch_loop_health.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_autonomous_dispatch_loop_health.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py"]

implementation_scope: source, test_addition, cli_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4742 asks GT-KB to lock in the autonomous review -> implement -> verify loop proven by the 2026-06-22 dispatched worker run for `gtkb-lo-harness-turn-budget-fix` (WI-4734), and to close the worker-liveness observability gap that made the system appear idle while worker session `019eec48-908b-7592-a0c6-4e25b7ca4df0` was actively implementing. This proposal adds a durable, read-only health validator for that reference loop and extends bridge dispatcher `--diagnose` output to surface process-family liveness from the already-verified storm-watchdog heartbeat instead of duplicating watchdog logic.

The change is intentionally bounded to source and tests. It does not add work items, mutate project membership, change config, mutate formal artifacts, start or stop workers, alter dispatch routing, or perform host scheduled-task operations. It uses the existing verified watchdog process-family heartbeat (`bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md`) as the liveness evidence source and the existing verified WI-4734 bridge chain (`bridge/gtkb-lo-harness-turn-budget-fix-006.md`) as the reference autonomous-loop case.

## First-Line Role Eligibility Check

- Owner initialized this interactive session as Prime Builder via `::init gtkb pb`.
- Current bridge work-intent claim for `gtkb-wi4742-autonomous-dispatch-loop-health` was acquired by session `019ef2e7-67ab-7f02-9046-bf0a8cbd58a4` with acting role `prime-builder`.
- Status authored by this proposal: `NEW`.
- Eligibility: Prime Builder is authorized to author `NEW` implementation proposals. Loyal Opposition review remains required before any protected implementation mutation.

## In-Root Placement Evidence

All target paths are under `E:\GT-KB`:

- `scripts/autonomous_dispatch_loop_health.py`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_autonomous_dispatch_loop_health.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`

No path under `applications/`, `E:\Claude-Playground`, or any external root is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the file-bridge workflow, the append-only numbered bridge file chain, and the requirement to derive live bridge state from TAFE/dispatcher state plus versioned bridge files rather than cached summaries. The new health validator must read versioned bridge files directly and the proposal must proceed through GO before source mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this implementation proposal to cite all relevant specifications. This proposal includes concrete governing spec IDs and a spec-derived verification plan.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires machine-readable `Project Authorization`, `Project`, and `Work Item` metadata. This proposal cites the active snapshot-bound PAUTH, project ID, and `WI-4742`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to include tests and evidence derived from linked specs. The verification plan below maps each spec to a concrete test or command.
- `GOV-STANDING-BACKLOG-001` - establishes MemBase/current work items as the standing backlog authority. WI-4742 is a current member of the project and this proposal must not add new WIs to the snapshot-bound project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs use of project-scoped implementation authorization. The cited PAUTH authorizes the six snapshot-bound member WIs, including WI-4742, but does not replace bridge GO or implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - supports preserving the proven dispatch loop as a durable diagnostic artifact rather than relying on transient session memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - frames the implementation as durable artifact graph work: versioned bridge evidence, a validator, and regression tests become future-session memory anchors.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit lifecycle handling for verification/completion artifacts. The validator preserves lifecycle evidence without creating or mutating formal artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - constrains work to GT-KB platform paths and avoids adopter/application surfaces.

## Prior Deliberations

- `DELIB-20265586` - owner decision for the snapshot-bound project authorization covering WI-4742; ACID invariant prohibits treating future project additions as covered by this PAUTH.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner priority for cost-optimized automatic bridge dispatch, the broader program that made autonomous dispatch health load-bearing.
- `DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF` - decision context for re-enabling auto-dispatch after storm controls, relevant to liveness and false-idle risk.
- `DELIB-20262481` - dispatch concurrency cap context referenced by the verified storm-watchdog work.
- `DELIB-20265232` and `DELIB-20265231` - dispatch-storm review and verification context; explains why liveness/idle signals need independent health checks.
- `DELIB-20263076` - ordered fallback routing context for cross-harness dispatch.
- `bridge/gtkb-lo-harness-turn-budget-fix-006.md` - VERIFIED reference case for the autonomous loop WI-4742 names explicitly.
- `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md` - VERIFIED prior work that supplies the process-family heartbeat this proposal reuses instead of duplicating detection logic.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-001-BOUNDED-IMPLEMENTATION-2026-06-23` authorizes bounded implementation for the six current open member WIs, including WI-4742.
- Owner decision `DELIB-20265586` is the approval evidence for that PAUTH.
- No additional owner decision is required for this proposal because the planned mutations are limited to the PAUTH-allowed classes `source`, `test_addition`, and `cli_extension`, and no new WIs or formal artifacts are created.

## Standing Backlog Bulk-Visibility Evidence

- Inventory artifact: live `gt projects show PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001 --json` output is the current member-WI inventory; it shows the snapshot-bound open set `WI-4625`, `WI-4626`, `WI-4647`, `WI-4741`, `WI-4742`, and `WI-4758`.
- Review packet: this bridge proposal is the per-WI review packet for WI-4742; Loyal Opposition must record GO before implementation and VERIFIED after the post-implementation report.
- Owner-approval packet: `PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-001-BOUNDED-IMPLEMENTATION-2026-06-23` plus `DELIB-20265586` explicitly approve the snapshot-bound project action while excluding any future added WIs.
- DECISION DEFERRED marker: any work outside the snapshot-bound six-WI inventory, including newly added project members or config mutation for WI-4758, remains deferred until a fresh owner approval exists.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4742 states the acceptance target precisely: add durable end-to-end validation/benchmark of the review -> implement -> verify loop using the `019eec48` WI-4734 reference run, and close the worker-liveness observability gap by deduplicating/extending the verified storm-watchdog process-family work. The governing bridge, project-authorization, backlog, and artifact-lifecycle specs above provide enough implementation constraints. No new or revised GOV/SPEC/ADR/DCL/REQ artifact is required.

## Proposed Scope

1. Add `scripts/autonomous_dispatch_loop_health.py`, a read-only validator for autonomous-loop bridge evidence.
   - Defaults to the reference thread `gtkb-lo-harness-turn-budget-fix`.
   - Accepts options such as `--bridge-id`, `--expected-wi`, `--expected-session-id`, and `--json`.
   - Reads numbered bridge files directly from `bridge/<slug>-NNN.md`, not aggregate queue summaries.
   - Confirms the reference lifecycle includes proposal, GO, implementation report, NO-GO, revised report, and VERIFIED status evidence; confirms `Work Item: WI-4734`; confirms session evidence for `019eec48-908b-7592-a0c6-4e25b7ca4df0`.
   - Emits stable JSON suitable for future benchmarks and a concise human-readable summary for operator use.
2. Extend `scripts/cross_harness_bridge_trigger.py --diagnose` with a worker process-family liveness section.
   - Reads `.gtkb-state/ops/storm-watchdog-heartbeat.txt` when present.
   - Parses heartbeat counters such as `codex`, `family`, `noncodex`, `threshold`, and `noncodexThreshold`.
   - Reports heartbeat freshness and warns when dispatcher state appears idle but the watchdog heartbeat shows live codex or non-codex harness-family processes.
   - Treats absent or unparsable heartbeat as diagnostic degradation, not a hard failure.
3. Mirror the same read-only heartbeat summary in `scripts/single_harness_bridge_dispatcher.py --diagnose` so single-harness and cross-harness diagnosis do not drift in the exact liveness surface WI-4742 depends on.
4. Add focused platform tests:
   - `platform_tests/scripts/test_autonomous_dispatch_loop_health.py` for validator parsing, lifecycle classification, JSON output, missing/failed cases, and the live reference bridge chain.
   - `platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` additions for heartbeat-present, heartbeat-absent, stale/unparsable, and false-idle warning cases.
   - `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` additions for the mirrored diagnose heartbeat summary.

## Out Of Scope

- No dispatch routing change.
- No worker spawning, killing, scheduled-task repoint, or host runtime mutation.
- No config mutation, including `config/agent-control/system-interface-map.toml`.
- No formal GOV/SPEC/ADR/DCL/PB/REQ mutation.
- No new work items added to `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`.
- No attempt to resolve WI-4625, WI-4626, or WI-4647 stale-open status inside this proposal.

## Spec-Derived Verification Plan

| Linked spec | Derived verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `platform_tests/scripts/test_autonomous_dispatch_loop_health.py` asserts the validator reads the numbered bridge file chain and does not depend on aggregate queue artifacts; implementation report cites `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4742-autonomous-dispatch-loop-health` after GO. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Pre-filing and post-implementation: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4742-autonomous-dispatch-loop-health` or content-file equivalent reports no missing required specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4742-autonomous-dispatch-loop-health` validates the PAUTH/project/WI metadata before protected mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New and extended pytest coverage maps validator behavior and liveness diagnostics to WI-4742 requirements; implementation report includes per-command pass/fail evidence. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001 --json` and `gt bridge threads --wi WI-4742` confirm work remains anchored to the existing member WI with no new WI added. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet validates the active PAUTH includes WI-4742 and target paths before source mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_autonomous_dispatch_loop_health.py` verifies the reference autonomous-loop evidence becomes a durable, reproducible health artifact. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Validator JSON output test confirms future sessions can consume stable artifact-state evidence instead of transient chat/session claims. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Validator lifecycle tests distinguish verified, incomplete, and missing-NO-GO/revised-report cases without mutating lifecycle artifacts. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and implementation report checks confirm all changes are confined to GT-KB platform `scripts/` and `platform_tests/` paths, with no adopter/application mutation. |

Expected implementation commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_autonomous_dispatch_loop_health.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/autonomous_dispatch_loop_health.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_autonomous_dispatch_loop_health.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/autonomous_dispatch_loop_health.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_autonomous_dispatch_loop_health.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
groundtruth-kb/.venv/Scripts/python.exe scripts/autonomous_dispatch_loop_health.py --bridge-id gtkb-lo-harness-turn-budget-fix --expected-wi WI-4734 --expected-session-id 019eec48-908b-7592-a0c6-4e25b7ca4df0 --json
groundtruth-kb/.venv/Scripts/python.exe scripts/cross_harness_bridge_trigger.py --diagnose
groundtruth-kb/.venv/Scripts/python.exe scripts/single_harness_bridge_dispatcher.py --diagnose
```

## Risk / Rollback

- Risk: heartbeat parsing could overstate liveness because the watchdog heartbeat reports process-family counts, not per-bridge ownership. Mitigation: diagnose output will label the data as process-family liveness and use it as a false-idle warning, not as proof of a specific active bridge worker.
- Risk: adding diagnose output could break existing tests that assert exact output. Mitigation: update focused tests and keep the new section stable, compact, and additive.
- Risk: the reference chain validator may be too hard-coded to WI-4734. Mitigation: expose explicit CLI options and keep WI-4734 values as defaults/reference checks, not parser assumptions.
- Rollback: remove `scripts/autonomous_dispatch_loop_health.py`, revert the additive diagnose helper/output changes in the two dispatcher scripts, and remove the focused tests. No data migration, config mutation, or formal artifact change is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4742-autonomous-dispatch-loop-health`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - adds a new read-only health validator and diagnostic surface, with regression tests, for an existing autonomous dispatch capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
