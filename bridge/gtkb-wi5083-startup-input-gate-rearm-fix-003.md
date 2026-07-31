GO

bridge_kind: lo_verdict
Document: gtkb-wi5083-startup-input-gate-rearm-fix
Version: 003
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5083-startup-input-gate-rearm-fix-001.md

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 6147bb18-d9cc-41a7-8702-1ca4a8b977cf
author_model: Claude Opus 4.6 (Thinking)
author_model_version: claude-opus-4-6
author_model_configuration: Antigravity harness, Loyal Opposition role; owner-directed manual review

## Verdict: GO (confirmatory, re-validating -002 GO)

Loyal Opposition confirms GO for WI-5083: startup-input gate must not re-arm on a mid-session continuation. This verdict re-validates the existing -002 GO (dispatcher auto-dispatch, session `C-2026-07-03T23-07-28Z`) at the owner's explicit request, after a manual deep review of the proposal, the review-ready implementation package, and the current source state.

## Review Analysis

### Root Cause Verification (confirmed against live source)

The root cause described in the proposal is verified against the current tree:

1. **`session_start_dispatch_core.py` lines 723–734:** The NORMAL_STARTUP/SPOOF_FALLBACK path constructs the startup-service command without reading stdin, so `source` is discarded. Confirmed — no `_read_session_start_source` function exists, no `--session-start-source` arg is threaded.

2. **`session_self_initialization.py` lines 7294–7327:** `_arm_startup_interaction_guard` has a signature that does NOT accept `session_start_source` or `armed_source`. The idempotency guard (lines 7302–7309) keys on `startup_guard_id == guard_id`, but `guard_id` is generated fresh each call via `_startup_guard_id()` which defaults to `_utc_now_iso()`, so the equality never holds across invocations. Confirmed — the arm re-fires unconditionally on every SessionStart.

3. **`session_self_initialization.py` lines 7555–7567:** The arm call site invokes `_arm_startup_interaction_guard` whenever `startup_emit_requested` is true, with no fresh-vs-continuation distinction. Confirmed.

### Fix Design Assessment

**Fix (a) — root cause (correct and necessary):**
- The `_read_session_start_source()` function is stdlib-light (`sys.stdin`, `json.loads`), fail-soft in every branch (tty → None, empty → None, bad JSON → None, missing `source` → None), and degrades to `None` which the startup service treats as fresh — preserving pre-WI-5083 behavior. Design is sound.
- The `_maybe_arm_startup_interaction_guard` wrapper gates on `_is_session_continuation_source(session_start_source)` and skips the arm when the source is `resume` or `compact`. This leaves any prior gate state untouched, so a session that already consumed its fresh-start gate is not spuriously re-armed. Correct.
- The `--session-start-source` CLI arg is added to the startup service's argument parser and threaded to the arm call site. Correct plumbing.

**Fix (b) — belt-and-suspenders (correct defense-in-depth):**
- In `workstream_focus.py`, the `_startup_response_pending` function gains a continuation-armed staleness check: if `armed_source` is `resume`/`compact`, the gate is cleared and not blocked. This protects against a future harness that doesn't thread the source.
- In `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`, the `_startup_input_gate_active` function gains the same check, maintaining cross-harness parity.
- The `_SESSION_CONTINUATION_SOURCES` frozenset is intentionally duplicated (not imported) across three modules to keep each SessionStart hot path import-light, mirroring the existing `_SESSION_ROLE_MARKER_NAME` parity pattern. A parity test asserts the copies stay equal. Correct pattern.

**Critical invariant preserved:** A genuine fresh-start await (`armed_source=startup`, within window) still blocks. Test §5.2b explicitly verifies this. The fix does NOT weaken the legitimate startup relay guard.

### Spec Linkage Assessment (complete)

| Spec | Relevance | Assessment |
|------|-----------|------------|
| `GOV-RELIABILITY-FAST-LANE-001` | Project home, authorization | ✅ Cited, correct |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Gate contract — relay owns first prompt | ✅ Cited, directly relevant |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Fresh-session self-initialization | ✅ Cited |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Init-keyword relay the gate serves | ✅ Cited |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Hot-path budget | ✅ Cited, change is stdlib-light |
| `ADR-CROSS-HARNESS-PARITY-001` | Codex reader + parity test | ✅ Cited, parity test covers |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge discipline | ✅ Cited |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal | ✅ Cited |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH/Project/WI metadata | ✅ Cited, metadata present |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived tests | ✅ Cited, spec-to-test mapping complete |
| `GOV-STANDING-BACKLOG-001` | WI-5083 backlog authority | ✅ Cited |

All blocking specs are cited and satisfied. The three missing advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are non-blocking and reasonably out of scope for a reliability fast-lane defect fix.

### Verification Plan Assessment

The spec-to-test mapping is complete and specific:
- §5.1: 5 test cases covering Fix (a) arm gating (continuation skip, fresh arm, absent source default)
- §5.2: 2 test cases covering Fix (b) block staleness (continuation-armed doesn't block, fresh-armed still blocks)
- §5.3: 4 test cases covering the fail-soft `source` reader
- §5.4: 1 parity test asserting the `_SESSION_CONTINUATION_SOURCES` copies stay equal

The verification commands include targeted regression, wider guard suites, ruff check + format, and cross-harness parity check. Complete.

## Applicability Preflight

- packet_hash: `sha256:1c71746253474febbbbf3d7bd819acc62cfb1667d00c08cfdd0d37e0bc926407`
- bridge_document_name: `gtkb-wi5083-startup-input-gate-rearm-fix`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5083-startup-input-gate-rearm-fix-001.md`
- operative_file: `bridge/gtkb-wi5083-startup-input-gate-rearm-fix-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5083-startup-input-gate-rearm-fix`
- Operative file: `bridge\gtkb-wi5083-startup-input-gate-rearm-fix-002.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | — | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `gtkb-codex-wrapup-startup-gate-guard-sot-001` (…004) — origin of the `_startup_input_gate_active` reader.
- `gtkb-loyal-opposition-startup-symmetry-001` (…010) — guard value finding.
- `gtkb-startup-relay-pretooluse-read-exemption-001` (…005) — Read/Grep/Glob exemption.
- `gtkb-session-start-formalization-001` (…012) — SessionStart arming machinery.
- `gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004` — shared core extraction.

## Conditions / Required Actions

None — unconditional GO. The implementation should proceed using the review-ready package's exact old→new block replacements.

## Candidate Spec (non-blocking suggestion)

The proposal correctly notes that a future `DCL-STARTUP-GATE-FRESH-START-ONLY-001` capturing "the startup-input gate arms only on a genuinely-fresh SessionStart source" would make the corrected behavior a first-class, testable constraint. This is not required for the fix but would be valuable to record as a follow-on.

## Owner Action Required

None.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
