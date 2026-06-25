NEW

# gtkb-cloud-lo-harness-transient-retry — Bounded transient-failure retry for the D (ollama) and F (openrouter) cloud LO harness shims

bridge_kind: prime_proposal
Document: gtkb-cloud-lo-harness-transient-retry
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

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

## Summary

Two cloud Loyal-Opposition harness shims abort fatally on any single HTTP hiccup, with no retry, which is the confirmed cause of two of the three WI-4670 reviewer outages:

- `call_ollama_chat` (`scripts/ollama_harness.py:404-425`): one `urllib.request.urlopen`; any `URLError` (HTTP 502/503/504 arrive as the `HTTPError` subclass, plus timeouts/connection resets) is raised fatally at line 417. Confirmed mode: HTTP 502 Bad Gateway from the kimi-k2 cloud route killed the worker with no verdict.
- `call_openrouter_chat` (`scripts/openrouter_harness.py:352-378`): same single-`urlopen` shape; additionally, a 2xx response whose body is not JSON (an SSE chunk, an HTML proxy/CDN page, or an empty body) dies at `json.loads` (line 375) with the opaque message "completions response was not JSON" and no status/body context. Confirmed mode: exactly that error, with auth verified healthy.

(The third WI-4670 outage, harness C/gemini, was an unfixable account-tier EOL and has already been retired via `gt harness retire` per owner AUQ. The cross-cutting worker-lifetime timeout is already VERIFIED under WI-4806.)

**Fix (same shape in both shims).** Introduce a small bounded retry-with-backoff wrapper around the request+parse so a dispatched cloud LO worker survives transient cloud failures and produces its verdict:

1. Retry on transient conditions only: `HTTPError` with status in {429, 500, 502, 503, 504}; `URLError` from timeout/connection reset; and (openrouter only) a 2xx body that fails `json.loads` (treated as a transient proxy/stream glitch).
2. Bounded attempts (default 3) with capped exponential backoff (1s, 2s, 4s — total ≤ ~7s, comfortably inside the WI-4806 worker-lifetime bound). Constants are module-level so they stay well under the worker timeout.
3. Fail fast (no retry) on non-transient client errors (4xx except 429).
4. On exhaustion or a non-transient error, raise the existing `*HarnessError` with an enriched message: HTTP status code (when available) plus a truncated body snippet, so the dispatch-failure log captures a diagnosable cause instead of an opaque one.

The change is confined to the request/parse path of the two `call_*_chat` functions plus a private retry helper in each shim; no public API, CLI surface, routing schema, or tool-call behavior changes. This restores D and F as headless reviewers (interactive LO via Cursor E already works); re-enabling their `can_receive_dispatch` is a separate, owner-visible step after VERIFIED.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs this work: WI-4817 is origin=defect, single-concern, ~4 tightly-related files, no new public API; it is a member of `PROJECT-GTKB-RELIABILITY-FIXES` and covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, so no per-fix deliberation/authorization/formal-approval packet is required while all bridge review and safety gates remain in force.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed and versioned via the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: the proposal cites its governing specs and derives its tests from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the verification plan maps the fix to executed pytest cases.
- `GOV-STANDING-BACKLOG-001` — WI-4817 (fast-lane defect, depends-on WI-4670) is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved: the fix is captured as durable artifacts (WI-4817, this bridge thread, derived tests) with a post-implementation report and VERIFIED verdict to follow.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — preserved: the artifact graph stays intact (defect WI -> proposal -> tests -> report -> verdict).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — preserved: lifecycle states are respected (WI-4817 candidate -> resolved on VERIFIED).

## Prior Deliberations

- `DELIB-20265882` — Dispatcher target-architecture grill resolutions (owner decision, 2026-06-24). Branch 10 ("stabilize first") names the WI-4670 cloud-harness fixes as Phase-0 acute work that must precede the daemon build; this proposal implements two of those three fixes (D, F). The deliberation does not prescribe the retry mechanism, so this is not a revisit of a rejected approach.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — OpenRouter harness registry integration model; relevant to F as the integration context, but it does not address transient-failure handling, which this proposal adds.
- No prior deliberation addressed bounded transient-retry hardening for the cloud LO shims specifically; the scaffold-seeded INTAKE-* review-eligibility candidates concern review/verdict gating, not harness transport reliability, and are not relied upon here.

## Owner Decisions / Input

This is fast-lane defect work (no per-fix owner approval required), but it traces to explicit owner direction this session:

- `DELIB-20265882` (owner decision, AUQ-backed) authorizes Phase-0 stabilization including the WI-4670 cloud-harness reviewer fixes.
- Owner AUQ 2026-06-25 (this session): owner selected "Phase 0 first" sequencing, then "Author + drive WI-4670," then "Retire C" (C retired accordingly).

No further owner decision is required to implement; re-enabling D/F dispatch after VERIFIED will be surfaced separately.

## Requirement Sufficiency

Existing requirements sufficient — WI-4670's acceptance ("a dispatched cloud-model LO worker produces a valid bridge verdict file on a real NEW proposal") plus `GOV-RELIABILITY-FAST-LANE-001` fully constrain this defect fix. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

All tests run with the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --no-header
```

Acceptance-to-test mapping (WI-4817 acceptance; both shims, via monkeypatched `urllib.request.urlopen`):

- T1 retry-then-success: `urlopen` raises `HTTPError(502)` on the first call, returns a valid JSON body on the second -> `call_*_chat` returns the parsed dict; attempt count == 2. (D and F.)
- T2 bounded exhaustion: `urlopen` raises `HTTPError(503)` on every attempt -> `*HarnessError` raised after exactly the configured max attempts; message includes the status code. (D and F.)
- T3 non-transient fail-fast: `urlopen` raises `HTTPError(401)` -> `*HarnessError` raised immediately with no retry (attempt count == 1). (D and F.)
- T4 (F only) non-JSON 2xx: `urlopen` returns a 2xx non-JSON body twice then valid JSON -> retried and succeeds; and an all-non-JSON case -> `OpenRouterHarnessError` whose message includes a truncated body snippet.
- T5 happy-path regression: existing `call_*_chat` success tests still pass (single attempt, no added latency when the first call succeeds).

Code-quality gates on the changed files (both lint and format are enforced at verification):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
```

## Risk / Rollback

Risk surface is the request/parse path of two `call_*_chat` functions plus a private per-shim retry helper. The change only adds resilience: a previously-fatal transient failure now retries within a bounded window; non-transient errors still fail (with a clearer message), so it cannot mask a genuine auth/config failure. Added latency is bounded (<= ~7s) and only incurred on actual transient failures, well inside the WI-4806 worker-lifetime timeout. Single-commit rollback: revert the one commit; source and tests are bundled together.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-cloud-lo-harness-transient-retry`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken behavior (dispatched cloud LO workers dying on transient HTTP failures); no new capability surface is added.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
