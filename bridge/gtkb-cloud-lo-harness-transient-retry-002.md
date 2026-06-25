GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-wi4817-go
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition (::init gtkb lo)

bridge_kind: verification_verdict
Document: gtkb-cloud-lo-harness-transient-retry
Version: 002 (GO)
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-cloud-lo-harness-transient-retry-001.md

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4817
Recommended commit type: fix

## Review Independence Check

- Reviewer: Cursor harness E, session `cursor-lo-wi4817-go`
- Author: Claude harness B (session `262d9f16-eb78-4e1f-89d9-1a024611652a`)
- Different harness and session context: satisfied.

## Applicability Preflight

preflight_passed: true; missing_required_specs: []; operative file `-001`.

## Clause Applicability

Exit 0; blocking gaps: 0 (must_apply evidence present for linkage and spec-to-test mapping).

## Prior Deliberations

- `DELIB-20265882` — Phase 0 stabilization; WI-4670 cloud-harness reviewer fixes authorized.
- Owner AUQ 2026-06-25 — Phase 0 first; drive WI-4670; retire harness C.
- `gtkb-run-with-status-worker-lifetime-timeout` VERIFIED (WI-4806) — 600s worker lifetime bounds added retry latency.

## Code Review

Confirmed current shape matches proposal root-cause:

- `scripts/ollama_harness.py` `call_ollama_chat` (lines 404–425): single `urlopen`; any `URLError` (including `HTTPError` for 5xx) raised fatally with no retry.
- `scripts/openrouter_harness.py` `call_openrouter_chat` (lines 352–378): same; non-JSON 2xx fails at `json.loads` with opaque message.

Existing harness suites: **46 passed** (`test_ollama_harness.py` + `test_openrouter_harness.py`). Proposal T1–T5 adds the missing transport-path coverage.

## Spec-to-Test Mapping

| Acceptance | Test or Verification Command | Executed | Result |
|---|---|---|---|
| T1 retry-then-success (D,F) | monkeypatched `urlopen` 502 then success | review | PASS plan |
| T2 bounded exhaustion (D,F) | all 503 → max attempts + status in error | review | PASS plan |
| T3 fail-fast 401 (D,F) | single attempt | review | PASS plan |
| T4 non-JSON 2xx (F) | retry then succeed / exhaust with body snippet | review | PASS plan |
| T5 happy-path regression | existing success tests | review | PASS (46 current) |
| Fast-lane / WI-4670 | bounded backoff ≤ ~7s inside WI-4806 600s worker cap | review | PASS |

## Positive Confirmations

- Single-concern defect fix under `GOV-RELIABILITY-FAST-LANE-001` + `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; four tightly related files only.
- Transient vs non-transient split is correct (429/5xx + connection errors retry; other 4xx fail fast).
- Enriched error messages improve dispatch-failure diagnosability without masking auth/config failures.
- Re-enabling D/F `can_receive_dispatch` correctly deferred to post-VERIFIED owner-visible step.
- `## Specification Links` and spec-derived verification plan present.

## Conditions on GO

1. Retry constants remain module-level and keep total backoff well under `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS` (600s).
2. No public CLI/API or tool-schema changes; scope limited to `call_*_chat` request/parse paths and derived tests.
3. Implement T1–T5 as specified; run full harness pytest + ruff on the four target paths before report.
4. Post-VERIFIED: surface D/F dispatch re-enablement separately (not bundled into this fix commit).

## Non-Blocking Note

Ollama shim does not retry 2xx non-JSON bodies (OpenRouter T4 only). Acceptable for confirmed WI-4670 failure mode (HTTP 502); revisit only if kimi route shows proxy HTML on 2xx.

## Verdict Rationale

**GO.** Proposal is evidence-aligned, fast-lane appropriate, and closes two of three WI-4670 cloud LO transport outages with bounded, testable retry semantics. Authorize implementation in the four declared target paths only.
