NEW

# gtkb-cloud-lo-harness-transient-retry — Post-Implementation Report (WI-4817)

bridge_kind: prime_proposal
Document: gtkb-cloud-lo-harness-transient-retry
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-cloud-lo-harness-transient-retry-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 262d9f16-eb78-4e1f-89d9-1a024611652a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4817

target_paths: ["scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary of Implementation

Implemented the GO'd (-002) bounded transient-retry fix in both cloud LO harness shims. Same shape in each: `import time`, module-level constants, and a bounded retry loop wrapping the request+parse in `call_*_chat`.

Module-level constants (added to both shims, identical):

- `CHAT_MAX_ATTEMPTS = 3`
- `CHAT_RETRY_BACKOFF_SECONDS = (1.0, 2.0, 4.0)` (total 7s, far under the 600s worker-lifetime cap)
- `RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})`

- `scripts/ollama_harness.py` `call_ollama_chat`: retries `HTTPError` whose `.code` is in `RETRYABLE_HTTP_STATUS`, and any non-HTTP `URLError` (timeout / connection reset), up to `CHAT_MAX_ATTEMPTS` with capped backoff; fails fast (single attempt) on non-transient client errors (e.g. 401); enriched error message includes the HTTP status and attempt count on exhaustion. A non-JSON 2xx body remains fatal — per the GO non-blocking note, D's confirmed failure mode is HTTP 502, not non-JSON.
- `scripts/openrouter_harness.py` `call_openrouter_chat`: same transport retry, PLUS a 2xx body that fails `json.loads` is retried; the enriched exhaustion error includes a 200-char body snippet for diagnosability.

`HTTPError` is caught before `URLError` (the former subclasses the latter) so the status-aware retry/fail-fast split is preserved. No public API, CLI surface, routing schema, or tool-schema change; scope is limited to the `call_*_chat` request/parse paths plus the derived tests.

## Specification Links (carried forward)

- `GOV-RELIABILITY-FAST-LANE-001` — WI-4817 is a fast-lane defect fix under `PROJECT-GTKB-RELIABILITY-FIXES` / `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; all bridge review + safety gates preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/versioned via the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — tests derived from the cited governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping executed (below).
- `GOV-STANDING-BACKLOG-001` — WI-4817 is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — preserved.

## Requirement Sufficiency

Existing requirements sufficient — the GO'd proposal's governing requirements (WI-4817 acceptance + `GOV-RELIABILITY-FAST-LANE-001`) fully constrained this defect fix. No new or revised requirement was needed; implementation matched the approved scope exactly.

## Spec-to-Test Mapping (executed)

All new tests live in `platform_tests/scripts/test_ollama_harness.py` (4) and `platform_tests/scripts/test_openrouter_harness.py` (6); both call the real `call_*_chat` with a monkeypatched `urlopen` and a no-op `time.sleep`.

| Acceptance | Test(s) | Executed | Result |
|---|---|---|---|
| T1 retry-then-success (D,F) | `test_wi4817_ollama_retry_then_success`, `test_wi4817_openrouter_retry_then_success` | yes | PASS (attempt count == 2) |
| T2 bounded exhaustion (D,F) | `test_wi4817_ollama_bounded_exhaustion`, `test_wi4817_openrouter_bounded_exhaustion` | yes | PASS (raises after CHAT_MAX_ATTEMPTS; status in message) |
| T3 fail-fast non-transient (D,F) | `test_wi4817_ollama_fail_fast_on_non_transient`, `test_wi4817_openrouter_fail_fast_on_non_transient` | yes | PASS (attempt count == 1) |
| T4 non-JSON 2xx (F) | `test_wi4817_openrouter_non_json_retry_then_success`, `test_wi4817_openrouter_non_json_exhaustion_includes_body_snippet` | yes | PASS (retry then succeed; exhaustion error includes body snippet) |
| T5 happy-path regression | `test_wi4817_ollama_happy_path_single_attempt`, `test_wi4817_openrouter_happy_path_single_attempt` + 46 pre-existing suite tests | yes | PASS (single attempt; no regressions) |

## Verification Evidence (commands + observed results)

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q
-> 56 passed in ~2.0s (was 46; +10 new WI-4817 tests)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
-> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
-> 4 files already formatted
```

## GO Conditions Compliance

1. **Retry constants module-level, backoff under worker cap** — satisfied: constants are module-level; total backoff 1+2+4 = 7s, far under `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS` (600s).
2. **No public CLI/API or tool-schema change** — satisfied: only `call_*_chat` request/parse paths + derived tests.
3. **Implement T1–T5; run pytest + ruff on the four paths before report** — satisfied (evidence above).
4. **Post-VERIFIED: surface D/F dispatch re-enablement separately** — honored: this change does NOT re-enable `can_receive_dispatch` for D or F; re-enablement will be a separate owner-visible step after VERIFIED.

## Files Changed

- `scripts/ollama_harness.py` — `import time`, retry constants, retry loop in `call_ollama_chat`.
- `scripts/openrouter_harness.py` — `import time`, retry constants, retry loop + non-JSON-2xx retry in `call_openrouter_chat`.
- `platform_tests/scripts/test_ollama_harness.py` — +4 tests + retry-response helper.
- `platform_tests/scripts/test_openrouter_harness.py` — +6 tests + retry-response helper.

Changes are in the working tree (uncommitted) for Loyal Opposition to verify the live state and finalize via the commit-finalization helper.

## Recommended Commit Type

`fix` — repairs broken behavior (dispatched cloud LO workers dying on transient HTTP failures); no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
