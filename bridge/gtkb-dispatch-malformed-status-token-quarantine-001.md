NEW

# Bridge Dispatch Must Fail Gracefully on a Malformed Bridge-File Status Token

bridge_kind: prime_proposal
Document: gtkb-dispatch-malformed-status-token-quarantine
Version: 001
Author: Prime Builder (Claude, harness B; session-stated ::init gtkb pb)
Date: 2026-06-18 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: init-gtkb-pb-2026-06-18-dispatcher-monitor
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4658-DISPATCH-MALFORMED-STATUS-TOKEN-GRACEFUL-QUARANTINE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: bridge_dispatch_malformed_status_graceful_degradation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make bridge dispatch fail gracefully when a single canonical numbered bridge
file carries a malformed first-line status token, instead of head-of-line
blocking the entire headless Prime-Builder dispatch lane.

**Observed live failure.** `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md`
contains the malformed first-line token `GO test` (not a canonical status
token). `scripts/bridge_work_intent_registry.py::_bridge_file_status`
(line 188) raises `WorkIntentRegistryError("Bridge file has unrecognized status
line: ...: 'GO test'")` whenever the thread's version entries are scanned.
Because `scripts/cross_harness_bridge_trigger.py::_acquire_prime_work_intent_batch`
acquires the Prime-Builder actionable batch **all-or-nothing** (one failed slug
releases the whole batch and returns `ok: False`), the single malformed thread
fails the entire batch on every dispatch cycle. `.gtkb-state/bridge-poller/dispatch-failures.jsonl`
shows this crash-looping ~every 2 seconds with `recipient: prime-builder:A`,
`reason: work_intent_acquire_failed`. The result: **no headless Prime-Builder
dispatch can launch at all** while the malformed file exists.

**False-green health.** `gt bridge dispatch health` reports `PASS` throughout,
because `groundtruth_kb.bridge_dispatch_config.collect_bridge_dispatch_status`
validates only partition topology (one active dispatchable harness per role) and
never reads `dispatch-state.json` quarantine/failure evidence.

This proposal authorizes a bounded, defense-in-depth repair with three
coordinated changes plus focused tests:

1. **Typed permanent-error class.** Add `MalformedBridgeStatusError(WorkIntentRegistryError)`
   in `scripts/bridge_work_intent_registry.py`, raised at the existing
   unrecognized-status-line site (and the empty-file site) so callers can
   distinguish a *permanent* per-file parse error from *transient* errors
   (DB errors, contention). Subclassing preserves every existing
   `except WorkIntentRegistryError` call site (backward-compatible).
2. **Quarantine-and-continue batch acquire.** In
   `_acquire_prime_work_intent_batch`, when a slug raises
   `MalformedBridgeStatusError`, record a structured quarantine finding
   (`reason: bridge_file_malformed_status_quarantined`, with the offending path
   and line) and **skip that slug**, continuing the batch with the remaining
   slugs. Non-malformed `WorkIntentRegistryError` and ordinary lease contention
   retain current semantics. Persist quarantined slugs to
   `dispatch-state.json` so they are visible to health/diagnostics.
3. **Dispatch-health finding.** In `collect_bridge_dispatch_status`, read the
   quarantined-thread set and append a `WARN`-level finding (e.g.
   `N bridge thread(s) quarantined for malformed status token: [...]`) so
   `gt bridge dispatch health` no longer reports topology-only `PASS` while
   threads are quarantined.

Out of scope (explicitly): hand-editing or deleting the malformed `-002.md`
file (append-only audit trail), and the orphan `.lo-verdict.md` reconciliation
class tracked separately under `gtkb-bridge-dispatcher-canonical-verdict-repair`.
This thread fixes the malformed-token *graceful-degradation* gap; that thread
fixes the orphan-verdict *write-prevention + reconciliation* gap. They are
complementary.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered `bridge/<slug>-NNN.md` chain is
  the canonical workflow surface; a malformed status token must be handled
  deterministically as drift, not allowed to crash the dispatch lane.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch health/liveness must reflect
  whether bridge work is actually progressing; a quarantined thread must surface
  as a finding rather than topology-only `PASS`.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — selected bridge work that cannot be
  routed (malformed status) must produce a deterministic, recorded failure that
  does not block routing of other selected work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  every governing spec for the dispatch/work-intent/health surfaces it touches.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project authorization,
  project, work item, and target_paths metadata are present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report
  will map each change to focused tests and executed commands.
- `GOV-STANDING-BACKLOG-001` — `WI-4658` records this defect in MemBase before
  implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — a malformed canonical bridge file is a
  lifecycle-drift artifact requiring deterministic handling (quarantine + health
  finding), not a silent crash.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is a durable, tested,
  artifact-tracked repair to a load-bearing dispatch surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect, owner decision, work
  item, and authorization are captured as durable artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation and test targets
  are inside the GT-KB project root.

## Prior Deliberations

<!-- Reviewed against canonical-terminology glossary + DA + live bridge state. -->

- `DELIB-20265221` — owner AUQ decision (2026-06-18): "Fix the live poisoning
  first." Authorizes this graceful-degradation fix as the multiplier that
  restores the headless PB dispatch lane.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-001.md` (NEW) and
  `-002.md` (NO-GO) — sibling thread covering the *orphan `.lo-verdict.md`*
  class. This proposal deliberately scopes to the *distinct* malformed-token
  failure (a canonical numbered file with a bad first-line token), which that
  thread's required revisions do not address. The two are complementary; neither
  subsumes the other.
- Resolved precedent "Keep normal bridge lease contention out of dispatch
  failure logs" (`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`) — establishes that
  dispatch failure-log signal quality matters; this proposal adds a *distinct*
  structured quarantine reason rather than overloading the existing contention
  path.
- `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` — the live
  victim file whose `GO test` token is the observed poison. This proposal does
  not modify it (append-only); it makes dispatch robust to it.

## Owner Decisions / Input

- `DELIB-20265221` (AUQ `AUQ-2026-06-18-dispatcher-drive-priority`, answer
  "Fix live poisoning first"): the owner directed that the malformed-token
  head-of-line-block be fixed first, via graceful work-intent quarantine + a
  health finding, and driven to VERIFIED. This is the owner approval that
  authorizes the implementation scope. No further owner decision is required
  before LO review. Protected source mutations still require LO `GO` plus an
  implementation-start packet derived from that GO.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already
establishes the canonical numbered-file chain and treats divergence as drift;
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001` already requires dispatch health to
reflect actual work progress, not just topology. This is a robustness repair to
existing dispatch and work-intent behavior, not a new bridge protocol or a new
status token. No new or revised requirement is required before implementation.

## In-Root Placement Evidence

All implementation and test targets are under `E:\GT-KB`:
`scripts/bridge_work_intent_registry.py`, `scripts/cross_harness_bridge_trigger.py`,
`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, and the three
`platform_tests/scripts/test_*.py` files. This filed proposal is the next
status-bearing numbered file `E:\GT-KB\bridge\gtkb-dispatch-malformed-status-token-quarantine-001.md`.
No target or generated artifact resolves outside the project root.

## Spec-Derived Verification Plan

Expected focused verification:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine
```

Spec-to-test mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001` / `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`:
  `test_bridge_work_intent_registry.py` proves `_bridge_file_status` raises the
  typed `MalformedBridgeStatusError` (a `WorkIntentRegistryError` subclass) on a
  malformed first-line token and on an empty file, and still returns valid
  canonical tokens unchanged.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`: `test_cross_harness_bridge_trigger.py`
  proves a PB-actionable batch containing one malformed slug quarantines that
  slug (records `bridge_file_malformed_status_quarantined`), still acquires and
  returns the remaining valid slugs (`ok: True`), and that ordinary lease
  contention and transient errors retain prior all-or-nothing semantics.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: `test_bridge_dispatch_config.py`
  proves `collect_bridge_dispatch_status` emits a `WARN` health finding (not
  topology-only `PASS`) when a quarantined thread is present in dispatch state.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  will include the executed command outputs above mapped to this plan.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | No credentials or credential-shaped samples added; tests use synthetic bridge fixtures. | Ruff + helper credential scan; report notes no secrets added. | |
| CQ-PATHS-001 | Yes | All writes inside the project root; quarantine state stays in `.gtkb-state/bridge-poller/`. | In-root placement evidence + path-scoped tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing `BRIDGE_FILE_STATUS_RE`, dispatch-state path, and failure-reason constants; add one new reason constant. | Ruff + focused tests. | |
| CQ-DOCS-001 | Yes | Update docstrings on the changed functions only. | Code review of changed docstrings. | |
| CQ-COMPLEXITY-001 | Yes | Keep the quarantine branch small and deterministic; no new runtime/queue. | Ruff + unit tests for the quarantine path. | |
| CQ-TESTS-001 | Yes | Add tests for typed-error raise, batch quarantine-and-continue, contention preservation, and health WARN finding. | Pytest command above. | |
| CQ-LOGGING-001 | Yes | Record quarantine as a structured `dispatch-failures.jsonl` entry + `dispatch-state.json` field, not a silent skip. | Trigger + health tests assert the recorded evidence. | |
| CQ-SECURITY-001 | Yes | Preserve append-only bridge discipline; no shell mutation of bridge files; do not weaken claim/gate checks. | Tests assert no bridge-file mutation occurs. | |
| CQ-VERIFICATION-001 | Yes | Implementation report includes command outputs mapped to the spec-derived plan. | LO verification of report evidence. | |

## Risk / Rollback

Risk is moderate: the change touches the work-intent registry and the
cross-harness dispatch batch, both load-bearing. Scope is bounded — no
production deployment, credential handling, schema migration, or alternate queue
runtime. The quarantine branch is additive and gated on a new typed exception,
so non-malformed paths are unchanged. Rollback is a single revert of the
implementation commit; quarantine state under `.gtkb-state/` is regenerable
runtime evidence.

## Bridge Filing

Filed as the next status-bearing numbered bridge file
`bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a live bridge-dispatcher failure mode (head-of-line block) with
no new user-facing workflow.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
