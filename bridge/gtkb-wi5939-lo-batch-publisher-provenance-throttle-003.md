NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5939-lo-batch-publisher-provenance-throttle
Version: 003
Date: 2026-08-05 UTC
Responds to: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-002.md
Approved proposal: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5939

target_paths: ["scripts/lo_batch_publish.py", "platform_tests/scripts/test_lo_batch_publish.py"]

# WI-5939 Implementation Report - governed LO batch publisher promoted to a tracked module

Implementation of the proposal approved at
`bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-002.md` (GO, Loyal
Opposition harness E, reviewer session `c305d00a-2bfd-4030-a875-a6a828e138ea`).

## Authorization Chain

- GO verdict: `-002.md`, no blocking conditions; clause preflight exit 0;
  PAUTH operation-time evaluation `allowed` for `implementation_packet_create`
  and `implementation_start`.
- Work-intent claim: `claim_kind: go_implementation`, session
  `5ce32d92-003b-4a04-a5f9-d3de2493c992`.
- Implementation-start packet created from the GO; classified targets
  `scripts/lo_batch_publish.py` (`source`) and
  `platform_tests/scripts/test_lo_batch_publish.py` (`test`), both PAUTH-allowed.

## Changes Implemented

Two net-new tracked files. No existing tracked file was modified. The superseded
runtime-state script `.gtkb-state/_lo_publish_from_recs.py` was **not** touched,
as declared (runtime state is not a governed mutation surface).

### `scripts/lo_batch_publish.py` (new, `source`)

| Change | Proposal ref | Implementation |
|---|---|---|
| C0 promote to tracked module | structural defect | Module now lives at the tracked path; `PROJECT_ROOT` is derived from `__file__`, and the module contains no `.gtkb-state` reference. Input JSON schema preserved, plus an optional `prior_deliberations` field. |
| C1 runtime session provenance | defects 1, 5 | `resolve_publisher_identity()` resolves author metadata via the governed `load_author_metadata` precedence and raises `PublisherProvenanceError` when the session id or identity is unresolved. No import-time `GTKB_HARNESS_NAME` injection; `harness_name_from_identity()` derives the harness from the resolved identity. |
| C2 computed review independence | defect 2 | `assert_review_independence()` reads the responded-to artifact's `author_session_context_id` via `extract_author_metadata`, refuses on equality (self-review) and refuses when the value is missing or unreadable (fail closed), raising `ReviewIndependenceError`. The emitted body prints both compared session ids as evidence instead of a boilerplate claim. |
| C3 runtime date | defect 3 | `published_date` is computed with `datetime.now(UTC)` at publication time and threaded into the body. |
| C4 honest deliberation disclosure | defect 4 | `prior_deliberations_markdown()` renders reviewer-supplied citations when present; otherwise it discloses that no search was performed by this transport and explicitly states that this is not a finding that none exist. |
| C5 serialization and throttling | defect 6 | `publish_batch()` publishes serially with a bounded `min_interval_seconds` (default 5.0s) between items and emits throttle events; `publish_one()` retries only contention-shaped failures with exponential backoff (`2s, 4s, 8s, ...`, capped by `max_retries`), and fails fast on deterministic errors. Claims are released in a `finally` block. |

### `platform_tests/scripts/test_lo_batch_publish.py` (new, `test`)

18 tests implementing T1-T7 from the approved test plan.

## Specification Links

Carried forward from the approved proposal `-001.md`:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary
- `config/agent-control/SESSION-STARTUP-INDEX.md` section Session-context review independence (normative)
- `.claude/rules/codex-review-gate.md` section Review Independence Gate
- `.claude/rules/deliberation-protocol.md`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/codex-decision-ledger.md` (2026-04-29 tracked-surface bias)
- `DELIB-202667721`

The GO's advisory (non-blocking) uncited specs are acknowledged here for
completeness: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. This change is consistent with them: the
work is captured as durable artifacts (WI-5939, WI-5940, WI-5941) with explicit
lifecycle states rather than as transient session context.

## Spec-to-Test Mapping (executed)

| Test(s) | Specification clause | Result |
|---|---|---|
| `test_t1_self_review_is_refused`, `test_t1_distinct_sessions_are_accepted` | file-bridge-protocol Review Independence Boundary | PASS |
| `test_t2_missing_author_session_fails_closed`, `test_t2_unreadable_artifact_fails_closed` | same, fail-closed clause; codex-review-gate Review Independence Gate | PASS |
| `test_t3_no_hardcoded_uuid_literal_in_module`, `test_t3_body_carries_runtime_session`, `test_t3_provenance_fails_closed_without_session` | GOV-SOURCE-OF-TRUTH-FRESHNESS-001; GOV-FILE-BRIDGE-AUTHORITY-001 | PASS |
| `test_t4_no_hardcoded_iso_date_literal_in_module`, `test_t4_body_uses_supplied_runtime_date` | GOV-FILE-BRIDGE-AUTHORITY-001 | PASS |
| `test_t5_absent_deliberations_disclose_rather_than_claim`, `test_t5_supplied_deliberations_are_rendered` | deliberation-protocol | PASS |
| `test_t6_batch_publication_is_throttled`, `test_t6_no_delay_before_first_publication`, `test_t6_contention_is_retried_with_exponential_backoff`, `test_t6_non_contention_failure_is_not_retried`, `test_t6_non_actionable_predecessor_is_refused` | bridge-essential; DELIB-202667526 | PASS |
| `test_t7_module_lives_on_the_tracked_surface`, `test_t7_module_does_not_depend_on_runtime_state_paths` | codex-decision-ledger tracked-surface bias | PASS |

## Commands Executed And Observed Results

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_batch_publish.py -q
  -> 18 passed, 1 warning in 0.90s   (and 18 passed in 0.63s after formatting)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> 2 files already formatted

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_bridge_work_intent_registry.py -q
  run 1 -> 1 failed, 57 passed, 2 skipped in 13.15s
  run 2 -> 58 passed, 2 skipped in 9.45s   (identical command)
```

`ruff format` was run once to normalize `scripts/lo_batch_publish.py` before the
`--check` gate; tests were re-executed after formatting and still pass.

### Disclosure: one regression test failed on the first run

`platform_tests/scripts/test_bridge_work_intent_registry.py::test_release_commit_wait_cannot_outlive_total_deadline`
FAILED on the first combined run and PASSED on an immediate re-run of the
identical command, and PASSES in isolation (1.32s). Evidence that this is a
pre-existing, order/timing-dependent flake and not a WI-5939 regression:

1. The failing test's module does not import `lo_batch_publish` (grep: no match).
2. `scripts/bridge_work_intent_registry.py` is unmodified by this change
   (`git status --porcelain` on that path is empty).
3. The two new files were not part of that pytest invocation at all - only the
   two named regression modules were collected.
4. The test asserts a wall-clock deadline bound, so it is sensitive to elapsed
   suite time and host load.

This is **not** claimed as green. It is captured as **WI-5941** with a concrete
remediation candidate (injected logical clock, matching the WI-5784 approach at
commit `277630edb`). Reviewer attention is invited on this point specifically.

## Acceptance Criteria Check

| # | Criterion | Status |
|---|---|---|
| 1 | Module exists at the tracked path; no `.gtkb-state` path required | MET (`test_t7_*`) |
| 2 | No hardcoded session-id or date literal | MET (`test_t3_no_hardcoded_uuid_literal_in_module`, `test_t4_no_hardcoded_iso_date_literal_in_module`) |
| 3 | Independence computed; fails closed on equality or missing/unreadable metadata | MET (`test_t1_*`, `test_t2_*`) |
| 4 | Body never asserts an unperformed deliberation search | MET (`test_t5_*`) |
| 5 | Multi-item publication serialized with bounded delay/backoff | MET (`test_t6_*`) |
| 6 | T1-T7 pass; ruff check and ruff format --check pass | MET (18 passed; both ruff gates clean) |
| 7 | Existing publication regression suites continue to pass | MET with the disclosed intermittent flake above (58 passed on re-run; failure independently attributed to WI-5941) |

## Target-Path Containment

`git status --porcelain` for the declared targets shows exactly:

```
?? platform_tests/scripts/test_lo_batch_publish.py
?? scripts/lo_batch_publish.py
```

`.gtkb-state/_lo_publish_from_recs.py` remains untouched, as declared.

## Residual Items (disclosed, not in scope)

- Two publishers coexist until the owner removes the superseded runtime-state
  script. That removal is an owner hygiene action; this change cannot perform it
  because runtime state is not a governed mutation surface.
- Audit-trail remediation of the 120 already-published templated verdicts remains
  **WI-5940**.
- The intermittent deadline test is **WI-5941**.

## Owner Decisions / Input

- **AUQ 2026-08-05 (next lane):** owner selected "P0: close the rogue-publish hole".
- **AUQ 2026-08-05 (verdict provenance):** owner selected "Genuine review; metadata
  is the bug" - no re-review of the 120 published verdicts; correction deferred to
  WI-5940.
- **AUQ 2026-08-05 (script disposition):** owner initially selected "Fix provenance
  + throttle in place".
- **AUQ 2026-08-05 (target surface, superseding the preceding item):** after the
  PAUTH gate refused governed mutation of the `runtime_state` path, owner selected
  "Promote to tracked source" - the authority for C0 and the declared target paths.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization.

## Recommended Commit Type

`feat:` - introduces a net-new tracked governed capability surface
(`scripts/lo_batch_publish.py`) plus its test module. Confirmed by the GO verdict
(Positive Confirmation 5).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
