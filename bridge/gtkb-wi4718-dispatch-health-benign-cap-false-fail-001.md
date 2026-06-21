NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f6ca6785-12f7-4d08-808f-74566b1f10c0
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Dispatch health verdict: stop misclassifying benign concurrency_cap_reached as a runtime FAIL; report accurate saturation WARN instead (WI-4718)

bridge_kind: prime_proposal
Document: gtkb-wi4718-dispatch-health-benign-cap-false-fail
Version: 001 (NEW)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4718-HEALTH-VERDICT
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4718

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

`gt bridge dispatch health` reports **FAIL** when the dispatcher is merely *saturated* (at the concurrency cap with workers busy), not failing. This was observed live this session: the dispatcher was functioning (LO drained its pending queue; Prime workers were spawning and correctly suppressing duplicate dispatch via work-intent claims), yet `health` returned FAIL and `status` returned WARN with `last_result=launch_failed`.

Root cause is a two-file interaction:

1. **Source side — generic token clobbering** (`scripts/cross_harness_bridge_trigger.py:3970`):
   ```python
   recipient_state["last_result"] = "launched" if launch.get("launched") else "launch_failed"
   ```
   Every non-launch spawn outcome is collapsed into the generic `"launch_failed"` token, regardless of the *actual* reason. When `_spawn_harness` declines to launch because the global concurrency cap is reached, it returns `{"launched": False, "reason": "concurrency_cap_reached", "live_count": N, "cap": N}` (`cross_harness_bridge_trigger.py:2768-2778`). The specific, benign reason is preserved in `recipient_state["last_launch"]["reason"]`, but `last_result` becomes the generic `"launch_failed"`.

2. **Classifier side — the actual misclassification** (`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py:412`, in `_runtime_findings_for_recipient`):
   ```python
   if (last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith("_dispatch_not_ready")) and has_pending_work:
       findings.append(f"dispatch runtime failure: {recipient_key} last_result={last_result} ...")
   ```
   `"launch_failed"` is a member of `RUNTIME_FAILURE_RESULTS` (`bridge_dispatch_config.py:26`), so this emits a `dispatch runtime failure` finding, which `_compute_health_status` escalates to **FAIL**.

The classifier is **internally inconsistent**: the very next block (line 421) checks `launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS`, and `concurrency_cap_reached` is deliberately **excluded** from that set — so the classifier already treats the *reason* as benign. The generic `last_result` token defeats that careful exclusion. The fix belongs on the classifier side because the `last_launch.reason` field (already read at `bridge_dispatch_config.py:405`) carries the authoritative cause.

**Impact.** Two harms, both characteristic of a false-positive health signal: (a) false alarm — the owner this session chased a "broken dispatcher" that was merely saturated; (b) signal masking — a chronic false FAIL trains operators to ignore the health verdict, so a *genuine* failure that coincides with cap saturation is hidden in noise. This degrades the health surface's value/cost ratio (`GOV-AUTOMATION-VALUE-VS-COST-001`) and makes a state claim that is not true (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`).

**Relationship to WI-4662 (sibling, non-overlapping).** WI-4662 (`gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover`, GO at `-002`, in implementation by a concurrent session) bounds the `previous_launch_failed` re-log spam in `dispatch-failures.jsonl` and adds a `lo_failover_exhausted` terminal record. Its proposal explicitly states the health-visibility annotation is "unchanged" — so WI-4662 does **not** fix this FAIL verdict. This work is the complementary half and is deliberately scoped to a **different file** (`bridge_dispatch_config.py`, the classifier) to avoid co-residence collision with both WI-4662 and the in-flight per-role concurrency-cap work (`WI-AUTO-SPEC-INTAKE-CA9165`, reopened 2026-06-21), which both edit `cross_harness_bridge_trigger.py`.

## Proposed Change

All edits confined to `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` plus tests in the existing `platform_tests/scripts/test_bridge_dispatch_config.py`. No change to `cross_harness_bridge_trigger.py`.

1. **Add a benign-reason constant** near the existing `RUNTIME_FAILURE_*` sets (`bridge_dispatch_config.py:54`):
   ```python
   # Reasons a non-launch ('launch_failed') spawn outcome can carry that are benign
   # backpressure, not a runtime failure. The trigger collapses all non-launch
   # outcomes to last_result="launch_failed"; the specific cause is in
   # last_launch.reason. concurrency_cap_reached means "all worker slots busy" —
   # saturation, surfaced as WARN, never FAIL.
   BENIGN_NONLAUNCH_LAUNCH_REASONS = frozenset({"concurrency_cap_reached"})
   ```

2. **Defer the generic `launch_failed` to the specific reason** in `_runtime_findings_for_recipient` (replacing the line-412 block):
   ```python
   last_result_is_runtime_failure = (
       last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith("_dispatch_not_ready")
   )
   # WI-4718: 'launch_failed' is the generic non-launch token written by the trigger
   # for ANY non-launch outcome; the specific cause is last_launch.reason. Defer to
   # it so benign backpressure is not misreported as a runtime failure. A genuine
   # launch reason (in RUNTIME_FAILURE_LAUNCH_REASONS, e.g. spawn_rate_limited) or an
   # absent reason still flags via the unchanged paths below.
   if last_result == "launch_failed" and launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS:
       last_result_is_runtime_failure = False
   if last_result_is_runtime_failure and has_pending_work:
       findings.append(
           f"dispatch runtime failure: {recipient_key} last_result={last_result} with pending_count={pending_count}"
       )
   ```

3. **Report accurate saturation as WARN** (mirroring the existing `last_result=="unchanged"` warning at `bridge_dispatch_config.py:452`), so saturation stays visible without false alarm:
   ```python
   if last_result == "launch_failed" and launch_reason == "concurrency_cap_reached" and has_pending_work:
       live = _int_value(last_launch.get("live_count"), default=0)
       cap = _int_value(last_launch.get("cap"), default=0)
       findings.append(
           f"dispatch runtime warning: {recipient_key} saturated "
           f"(live_count={live}/cap={cap}) with pending_count={pending_count}"
       )
   ```

The `dispatch runtime warning:` prefix is the same one `_compute_health_status` treats as non-FAIL (only `dispatch runtime failure` / `no active dispatchable` / `config error` escalate to FAIL), so saturation surfaces as WARN, never FAIL.

This is the minimal, behavior-preserving fix: only the `launch_failed`+`concurrency_cap_reached` combination is reclassified. Every other `last_result` failure token, every genuine `last_launch.reason` failure (line 421), `failure_class` (416), `exit_failure_reason` (426), circuit-breaker (408), and fallback-skipped (438) path is untouched.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` — governing principle: a chronic false-FAIL health signal is recurring cost (false alarm + signal masking) with no informational value; the fix restores the verdict's value/cost ratio.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the health verdict is a state claim about canonical dispatch state; reporting FAIL for a saturated-but-healthy dispatcher is an inaccurate state claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain (blocking, paths-match `bridge/**`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specs (blocking).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan below (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed files are under `E:\GT-KB` (`groundtruth-kb/src/...`, `platform_tests/...`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — WI-4718 + this proposal preserve the defect and decision as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability across WI, proposal, tests, and report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4718 candidate -> implementation -> verified lifecycle.

## Owner Decisions / Input

- The owner explicitly authorized filing this finding as a fresh bridge proposal for Codex review via `AskUserQuestion` this session (2026-06-21): asked how to scope "fix dispatch health", the owner selected **"Both fixes"** — implement the GO'd WI-4662 (being handled by a concurrent session) AND file this line-3970/classifier finding as a new proposal. That AUQ answer is captured as `DELIB-20265509` (`source_type=owner_conversation`, `outcome=owner_decision`, AUQ id `AUQ-2026-06-21-dispatch-health-scope`).
- WI-4718 has been admitted to `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` (active membership) and is covered by the bounded authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4718-HEALTH-VERDICT` (owner-decision `DELIB-20265509`; included specs `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-AUTOMATION-VALUE-VS-COST-001`; allowed mutations source + test_addition). Implementation still requires Loyal Opposition GO on this thread plus an implementation-start authorization packet; no code change is authorized by the AUQ or the PAUTH alone.

## Prior Deliberations

- Deliberation search `"dispatch health launch_failed concurrency cap false failure classification"` returned **no prior decision on this specific misclassification** — this is a newly surfaced defect, not a revisit of a rejected approach.
- `DELIB-20265484` — Loyal Opposition GO verdict for WI-4662 ("Previous Launch Failure Cooldown Failover"); the sibling dispatch-health thread whose scope explicitly leaves the health-visibility verdict unchanged, which is precisely the gap this proposal fills.
- `DELIB-20265275` — Loyal Opposition NO-GO "WI-4616 Covered-By Dispatch Reliability Reconciliation"; dispatch-reliability reconciliation context for the PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY family.
- `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md` / `-002.md` (GO) — the co-resident sibling thread; this proposal is scoped to a different file to avoid collision, mirroring the WI-4662<->WI-4703 co-residence pattern documented in that thread.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-AUTOMATION-VALUE-VS-COST-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` govern the behavior (an accurate, low-noise health verdict); WI-4718 derives a concrete, bounded classifier behavior from them. No new specification is required before implementation.

## Specification-Derived Verification Plan

New focused unit tests in `platform_tests/scripts/test_bridge_dispatch_config.py` (extending the existing `_runtime_findings_for_recipient` coverage). Spec-to-test mapping:

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — saturation is not a failure | recipient row `last_result="launch_failed"`, `last_launch.reason="concurrency_cap_reached"`, `pending_count>0` | NO `dispatch runtime failure` finding; health status not FAIL |
| `GOV-AUTOMATION-VALUE-VS-COST-001` — saturation is visible as WARN | same row with `live_count`/`cap` present | a `dispatch runtime warning: ... saturated (live_count=.../cap=...)` finding is emitted |
| No regression: genuine launch reason still fails | `last_result="launch_failed"`, `last_launch.reason="spawn_rate_limited"`, `pending_count>0` | `dispatch runtime failure` finding present (existing `test_wi4578_health_fails_for_blocked_runtime_candidates` must still pass) |
| No regression: absent reason still fails | `last_result="launch_failed"`, `last_launch={}` (no reason), `pending_count>0` | `dispatch runtime failure` finding present (conservative fail-closed) |
| No regression: other failure tokens unaffected | `last_result="circuit_breaker_active"` OR `failure_class` set, `pending_count>0` | corresponding `dispatch runtime failure` finding present |
| Benign cap with NO pending work | `last_result="launch_failed"`, `reason="concurrency_cap_reached"`, `pending_count=0`, `selected_count=0` | no findings (has_pending_work gate) |

Commands (run from `E:\GT-KB`):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
- Lint: `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`
- Format: `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`

## Risk And Rollback

- Risk: reclassifying `concurrency_cap_reached` could hide a real problem if the cap is *chronically* saturated and pending never drains. Mitigation: that condition is a *throughput*/saturation concern (owned by the per-role concurrency-cap work, `WI-AUTO-SPEC-INTAKE-CA9165`), not a dispatch *failure*; the new WARN keeps saturation visible on the health surface, and genuine failures (subprocess errors, circuit-breaker trips, `no_verdict_produced`, etc.) remain FAIL.
- Risk: the benign set is too broad. Mitigation: it is a single explicit token (`concurrency_cap_reached`); every other non-launch reason continues to flow through the unchanged classification.
- Rollback: revert the single source commit; the test additions are additive. No schema change — the fix only reads existing `last_launch.reason`/`live_count`/`cap` fields.

## Acceptance Criteria

- [ ] `last_result="launch_failed"` + `last_launch.reason="concurrency_cap_reached"` + pending work emits NO `dispatch runtime failure` finding; `_compute_health_status` does not return FAIL for that row alone.
- [ ] The same row emits a `dispatch runtime warning: ... saturated (live_count=.../cap=...)` finding (saturation stays visible).
- [ ] `last_result="launch_failed"` with a genuine failure reason (e.g. `spawn_rate_limited`) or an absent reason still emits a `dispatch runtime failure` finding (no regression; `test_wi4578_*` pass).
- [ ] All other classifier paths (circuit breaker, failure_class, exit_failure_reason, fallback-skipped, unchanged) are unchanged.
- [ ] New unit tests pass; `ruff check` + `ruff format --check` clean on changed files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
