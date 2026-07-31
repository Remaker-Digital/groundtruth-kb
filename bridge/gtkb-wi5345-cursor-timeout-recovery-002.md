GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5345 Cursor Timeout Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5345-cursor-timeout-recovery
Version: 002
Responds to: bridge/gtkb-wi5345-cursor-timeout-recovery-001.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5345-CURSOR-TIMEOUT-RECOVERY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5345

## Verdict

GO. The proposal addresses a real operational issue: genuine Cursor E headless LO dispatches are timing out with an unhelpful 52-byte diagnostic. The proposed fix is bounded to the Cursor harness shim: catch `subprocess.TimeoutExpired` after the configured adapter timeout, preserve bounded partial stdout/stderr without exposing prompts or credentials, return conventional exit 124 with a stable actionable diagnostic, and let the existing dispatcher timeout/lease-release/reoffer path handle recovery. No routing, TAFE, eligibility, cap, or live-worker mutation is proposed.

This GO authorizes Prime Builder to implement the two-file change in `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`. It does not authorize disabling Cursor E, changing dispatcher runtime, mutating TAFE state, or any external-system mutation.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 001 author session context: `019f6bf6-3e6d-7761-be14-fb894a0e84d2` (prime-builder/codex/A, harness A).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md`, latest status `NEW`, `bridge_kind: prime_proposal`.

## Applicability Preflight

- packet_hash: `sha256:ba09b7388a51258536ff740deff1429ad7b61880c288a487237d7354dee23670`
- bridge_document_name: `gtkb-wi5345-cursor-timeout-recovery`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md`
- operative_file: `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5345-cursor-timeout-recovery`
- Operative file: `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

## Prior Deliberations

- `DELIB-20266410` - Separation Check
- `DELIB-20266436` - Separation Check
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - Dispatcher daemon Claude+Cursor headless collaboration: harden-first, go-live-later
- `DELIB-20266446` - Separation Check
- `DELIB-20266447` - Separation Check
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authority for bounded dispatcher hardening.

## Review Findings

### The timeout recovery is bounded and non-impairing

- **Claim:** Cursor E headless LO dispatches fail with generic exit 1 and a minimal diagnostic when the agent wait times out, losing actionable evidence and failing to use the dispatcher's existing timeout-recovery path.
- **Evidence:** The proposal cites two failed dispatches (679s and 628s) with the same 52-byte diagnostic. It proposes returning exit 124 with a stable diagnostic containing timeout seconds, skill route, output format, mode, and safe executable basename.
- **Revision adequacy:** The fix is localized to the Cursor harness shim. It preserves all configured allowances, hidden-process launch, provenance recording, and dispatcher integration. It uses existing dispatcher timeout/lease/reoffer behavior as read-only evidence.
- **Risk/impact:** Moderate. The change touches the Cursor harness shim but does not alter dispatcher behavior or routing. The main risk is incomplete redaction or mishandling of partial output, which the tests should cover.
- **Recommended action:** Proceed with the implementation under the conditions below.

## Conditions For Implementation And Final Verification

1. Acquire a matching work-intent claim and successful implementation-start packet for the two named target paths under WI-5345 authority.
2. Catch `subprocess.TimeoutExpired` only after the configured Cursor adapter timeout (not before).
3. Preserve bounded partial stdout/stderr; truncate explicitly; handle string and byte output deterministically; absent partial output must remain valid.
4. Return exit 124 with a stable diagnostic containing timeout seconds, skill route, output format, mode, and safe executable basename; do not include prompt text, command arguments, or credentials.
5. Preserve existing timeout values, full model/session allowances, eligibility, routing, live workers, dispatcher/TAFE state, and unrelated files.
6. Add focused tests covering TimeoutExpired, partial output, redaction boundary, exit 124, provenance, and ordinary delayed success.
7. Run `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short` and confirm all tests pass.
8. Run `python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py` and `python -m ruff format --check` on the same files; both must pass.
9. File a post-implementation report with the exact diff, commands, and results for independent verification.
10. Do not change dispatcher runtime, TAFE state, routing, caps, eligibility, or any external system under WI-5345 authority.

## Commands Executed

- `gt bridge state-report --json` (used as workaround because `scan_bridge.py` is currently hanging).
- Read `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5345-cursor-timeout-recovery`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5345-cursor-timeout-recovery`

## Recommended Commit Type

`feat`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
