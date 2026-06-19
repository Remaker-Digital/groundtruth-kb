NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ee0ab-7656-7551-99db-d211ef599d15
author_model: gpt-5-codex
author_model_version: codex-desktop-2026-06-19
author_model_configuration: Codex Desktop API runtime; approval_policy=never; filesystem=danger-full-access; session_role=prime-builder

# Defect-Fix Proposal - Dispatch Runtime Health And Readiness Repair

bridge_kind: prime_proposal
Document: gtkb-dispatch-runtime-health-readiness-repair
Version: 001
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/cross_harness_bridge_trigger.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", ".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "config/dispatcher/rules.toml"]

Defect-fix proposal focused on making the bridge dispatcher operationally honest and capable of clearing Loyal Opposition review work instead of reporting topology success while the runtime pool is unavailable.

## Claim

The bridge dispatcher currently treats configured LO targets as sufficient even when runtime evidence proves that none of the selected targets can complete review work. This proposal repairs the runtime health and readiness path so `gt bridge dispatch status|health` and related scan/debug surfaces fail loudly when pending LO work cannot be dispatched or verified, and so stale/manual scan surfaces no longer contradict dispatcher/TAFE bridge authority.

## Requirement Sufficiency

Existing requirements sufficient.

The active WI-4578 authorization and linked dispatch/bridge specifications already require role-dispatchability orthogonality, rule-based routing, bridge configuration/status/health reporting, TAFE-backed bridge authority, and spec-derived verification. This defect-fix proposal does not need a new or revised requirement before implementation; it applies those existing requirements to the observed false-green runtime health and stuck LO-dispatch behavior.

## Defect / Reproduction

Observed 2026-06-19:

- `gt bridge dispatch status --json` and an initial `gt bridge dispatch health --json` reported `health_status: PASS` with LO targets `D/Ollama`, `F/OpenRouter`, and `C/Antigravity` selected.
- The live dispatcher state at `.gtkb-state/bridge-poller/dispatch-state.json` simultaneously recorded pending LO work, `ollama_dispatch_not_ready`, `launch_failed`, `spawn_rate_limited`, and OpenRouter provider backoff state.
- A rerun after state reconciliation returned `health_status: FAIL` with `loyal-opposition last_result=unchanged with pending_count=2`, `loyal-opposition:C last_result=unchanged with pending_count=2`, and `loyal-opposition:F last_result=provider_failure_backoff_active with pending_count=2`.
- Runtime evidence shows:
  - `D/Ollama` readiness fails because the local Ollama `/api/tags` probe is connection refused and no autostart task/service was detected.
  - `F/OpenRouter` has recent `max-turn exhaustion`, remote connection reset, and abrupt empty-log termination evidence, with no verdict written.
  - `C/Antigravity` exits with an unsupported-client/free-tier `IneligibleTierError` through the configured `gemini` CLI headless path.
- The manual bridge scan helper reports archived nonterminal entries as LO-actionable, while the archive-aware dispatcher/TAFE path excludes acknowledged archived bridge threads. In the latest check, the manual helper reported seven LO-actionable rows; the archive-aware trigger path reported `lo_count 2`.

The defect is not a single provider outage. The system lacks an authoritative runtime-readiness contract across dispatcher health, fallback/backoff state, no-verdict reconciliation, and archive-aware scan surfaces.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not introduce secrets, provider keys, or credential-shaped examples in dispatcher health logs, tests, or bridge evidence. | Bridge helper credential scan, ruff, and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep all changes inside the declared GT-KB target paths. | Implementation-start packet, target-path preflight, and final diff review. | |
| CQ-COMPLEXITY-001 | Yes | Prefer small deterministic classifiers and health findings over broad prompt-only behavior. | Focused unit tests for each runtime failure class. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing dispatch result/failure constants or add centralized constants for new failure states. | Search review plus targeted tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed bridge authorization, credential, deployment, and provider-action boundaries. | Negative-path tests and proposal scope review. | |
| CQ-DOCS-001 | Yes | Update scan/debug guidance only where behavior or output semantics change. | Review of changed skill/helper text and preflight output. | |
| CQ-TESTS-001 | Yes | Add regression tests for health failure, no-verdict reconciliation, fallback exhaustion, and archive-aware scanning. | Targeted pytest commands listed in the verification plan. | |
| CQ-LOGGING-001 | Yes | Runtime failures must leave durable but non-secret evidence in dispatch state/log surfaces. | Dispatch-state fixture assertions and log classification tests. | |
| CQ-VERIFICATION-001 | Yes | File a post-implementation report with spec-to-test mapping and exact command results. | LO verification of the implementation report. | |

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/ollama_harness.py`, `scripts/openrouter_harness.py`, `.claude/skills/bridge/helpers/scan_bridge.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_ollama_harness.py`, `platform_tests/scripts/test_openrouter_harness.py`, `config/dispatcher/rules.toml`.

## Specification Links

- `SPEC-TAFE-R4` - TAFE/dispatcher state and status-bearing versioned bridge files are the live workflow authority.
- `REQ-HARNESS-REGISTRY-001` - harness registry role, dispatchability, and invocation metadata constrain target selection.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch health must represent centralized dispatch behavior, not only static topology.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch evidence must preserve target, status, and result semantics.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - rule-based routing must respect eligibility and failure state.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - dispatcher routing and queue reporting must use the same bridge-state interpretation.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - dispatch attempts and failures must leave durable evidence for later diagnosis.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the file bridge remains the coordination authority for implementation review and verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - discovered dispatcher defects must be preserved in durable bridge evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing constraints before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include tests derived from these constraints.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are machine-readable in this proposal.
- `SPEC-AUQ-POLICY-ENGINE-001` - any future owner decision or waiver remains owner-visible and does not bypass bridge review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes remain in the GT-KB root and do not use external live locations.
- `GOV-STANDING-BACKLOG-001` - the work is anchored to existing MemBase work item `WI-4578`, with `WI-4662` as related defect evidence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the helper-mediated bridge write path rather than assuming local write hooks cover proposal compliance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction is represented as a bridge proposal, not an untracked source edit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the investigation crossed from diagnosis into planned repair and therefore requires durable lifecycle handling.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the active project authorization does not bypass the required LO GO and implementation-start packet.

## Prior Deliberations

- `DELIB-20265240` - Loyal Opposition Review - Malformed Status Token Quarantine
- `DELIB-20263189` - Owner authorization: implement 3 P1 dispatch/bridge-reliability specs (22c078/9cb2ee/ca9165)
- `DELIB-20265044` - Loyal Opposition Verdict: WI-4574 TAFE Ingestion Phantom Guard REVISED
- `DELIB-20265273` - Loyal Opposition Review: WI-4616 Diagnostic Fixture Correction After NO-GO
- `DELIB-20261567` - Loyal Opposition Review - Bridge Poller WI Retirement Disposition

## Owner Decisions / Input

- `DELIB-20263438` - owner directive authorizing the bounded WI-4578 bridge-dispatch architecture correction.
- `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` - active project authorization for `WI-4578`, allowing source, test, config, CLI, skill, protected narrative file, MemBase spec insert, and governance evidence classes while preserving bridge review, formal-artifact approval, credential, deployment, self-review, and no-bypass restrictions.

## Pre-Filing Preflight

Applicability preflight was run against this candidate content before filing:

```text
python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-propose-drafts\gtkb-dispatch-runtime-health-readiness-repair-001.md --json
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `packet_hash: sha256:f9b11846b4266e54bd079441701d903f91aa3231876eb3b5d6bd45bf7bcaa8cc`.

Clause preflight was run against this candidate content before filing:

```text
python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-propose-drafts\gtkb-dispatch-runtime-health-readiness-repair-001.md
```

Result: exit 0; `must_apply: 4`; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Proposed Scope

Implement one focused runtime-health/readiness slice:

1. Health/status runtime evidence:
   - Extend `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` so dispatch health reads and evaluates the current dispatcher state, pending bridge queue counts, selected candidate state, recent launch evidence, exit-code/no-verdict markers, readiness failures, provider backoff, spawn-rate limits, and circuit-breaker state.
   - Ensure health cannot return `PASS` merely because configured LO targets exist when pending LO work is not being cleared.

2. Cross-harness dispatch state semantics:
   - Update `scripts/cross_harness_bridge_trigger.py` so fatal launch/no-verdict/provider readiness evidence is reconciled promptly and represented as a clear failure or degraded state.
   - Replace ambiguous role-level `unchanged`/`launch_failed` outcomes with explicit all-target-blocked or no-ready-target semantics when every selected/fallback LO candidate is unavailable.
   - Keep ordered fallback behavior, but make fallback exhaustion visible and non-green.

3. Archive-aware scan alignment:
   - Update `.claude/skills/bridge/helpers/scan_bridge.py` or its underlying read path so manual LO scans use the same archive-aware dispatcher/TAFE authority as the trigger, or clearly separate acknowledged archived nonterminal rows from live actionable rows.

4. Provider/harness readiness classification:
   - Add deterministic classification for the observed runtime failures: `ollama_dispatch_not_ready`, OpenRouter provider/backoff/no-verdict failures, unsupported Antigravity headless client failures, and dead pid/no status-file reconciliation.
   - This proposal does not authorize credential lifecycle changes, production deployment, retired poller restoration, or external provider account changes. If a provider-side action is still needed after code repair, it will be reported as an operational blocker rather than performed by this implementation.

## Specification-Derived Verification Plan

| Specification / constraint | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | Add or update `platform_tests/scripts/test_bridge_dispatch_config.py` cases proving health is `FAIL` when pending LO work exists and selected LO targets are blocked by readiness failure, provider backoff, no verdict, spawn-rate limit, or dead-process state. |
| `SPEC-TAFE-R4`, `SPEC-TOPIC-ENVELOPE-ROUTER-001` | Add or update tests proving archive-aware dispatcher queue counts and manual scan/actionable counts agree, or archived rows are reported separately and not counted as live actionable. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-SESSION-ENVELOPE-DURABILITY-001` | Add or update `platform_tests/scripts/test_cross_harness_bridge_trigger.py` cases for dead pid/no status-file reconciliation, no-verdict produced, fallback exhaustion, and explicit degraded state persistence. |
| `REQ-HARNESS-REGISTRY-001` | Add or update readiness classification tests for configured but runtime-unusable targets without treating those targets as healthy delivery capacity. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted pytest and ruff checks on changed source/test files and report exact commands/results in the post-implementation report. |

Expected command set after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
gt bridge dispatch health --json
```

## Acceptance Criteria

- `gt bridge dispatch health --json` returns `FAIL` when pending LO work exists and every selected/fallback LO target is unavailable, degraded, backoff-blocked, spawn-rate-limited, or recently failed without a verdict.
- Health findings identify the specific runtime blockers per target instead of returning an empty finding list.
- Dispatch state no longer presents pending stuck work as a green or no-pending condition after recent failed launch/no-verdict evidence.
- Manual scan/startup/debug surfaces do not count acknowledged archived nonterminal bridge threads as live LO-actionable work without labeling them as archived/excluded.
- Dead pid/no status-file and launched-without-verdict cases are reconciled into deterministic failure states without waiting for unrelated future events.
- The correction preserves the current bridge protocol and does not restore the retired OS poller or retired smart poller.

## Risks / Rollback

Risks:

- Health may become stricter and surface existing dispatch degradation more often. This is intended; false-green dispatch health is the defect.
- A scan helper change could expose stale archived/nonterminal bridge rows differently than prior operator habits. The implementation must preserve historical visibility while separating live actionable work from archived excluded work.
- Provider-specific readiness signatures could be overfit to current stderr text. Tests should lock the known classes while keeping the classifier conservative and extensible.

Rollback:

- Revert the source/test changes from this bridge thread.
- Because the implementation changes only dispatcher health/readiness/scan behavior, rollback should restore prior behavior without data migration.
- No credential, deployment, or external provider state is changed by this proposal.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `.claude/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `config/dispatcher/rules.toml`

## Recommended Commit Type

`fix`
