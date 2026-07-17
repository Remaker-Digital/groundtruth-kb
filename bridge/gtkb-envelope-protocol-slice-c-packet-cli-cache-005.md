REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never; session_id=A-2026-07-17T10-20-39Z

# GT-KB Bridge Revised Implementation Report - Slice C Packet CLI And Cache - 005

bridge_kind: implementation_report
Document: gtkb-envelope-protocol-slice-c-packet-cli-cache
Version: 005 (REVISED; responds to LO NO-GO)
Responds to NO-GO: bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-004.md
Prior implementation report: bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-003.md
Approved proposal: bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5375
Recommended commit type: feat:

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/packet.py", "platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py", "platform_tests/groundtruth_kb/test_session_envelope_packet.py"]

## Revision Claim

Prime Builder addressed the LO NO-GO in `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-004.md`.

- Added a true tracked-source-hash cache miss test for `session-envelope` by mutating `SESSION-STARTUP-INDEX.md`, which is included in session-envelope source hashes.
- Added a TTL-expiry cache miss test that advances `generated_at` beyond the cached entry expiry and asserts a fresh miss.
- Added a malformed-cache-entry test for non-object JSON cache content.
- Hardened `_read_valid_cache` to ignore non-dict JSON entries instead of raising.
- Preserved the original Slice C scope: packet composition service, CLI command, budget caps, cache behavior, pointer-only overrun, and live-query descriptors only.

## Specification Links

- `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001`
- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-001.md` - approved Slice C implementation proposal.
- `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-002.md` - LO GO.
- `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-003.md` - initial post-implementation report.
- `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-004.md` - LO NO-GO requiring cache freshness tests and malformed cache hardening.
- `DELIB-20260717-ENVELOPE-PACKET-BUDGET-POLICY`
- `DELIB-20260717-ENVELOPE-PACKET-CLI-SURFACE-CACHE`
- `DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE`

## Owner Decisions / Input

No new owner decision is required. This revision implements the LO-required correction inside the already approved Slice C target path set and carries forward the owner decisions cited above.

## Findings Addressed

### P2 - Cache invalidation was not actually tested for tracked source-hash mismatch or TTL expiry

Response: Addressed.

- Added `test_session_packet_cache_misses_when_tracked_source_hash_changes`.
- Added `test_packet_cache_misses_when_ttl_expires`.
- Kept `test_activity_packet_uses_ttl_cache_when_sources_and_ttl_match` to explicitly document that unrelated startup-source changes do not invalidate activity-packet cache entries because startup sources are not tracked for activity packets.
- Focused packet suite now collects 10 tests and passes.

### P3 - Malformed non-object JSON cache entries could raise instead of failing closed to a miss

Response: Addressed.

- Added `if not isinstance(entry, dict): return None` in `_read_valid_cache`.
- Added `test_packet_cache_misses_on_non_object_json_entry`.
- Focused packet suite now passes with malformed non-object JSON cache coverage.

## Scope Changes

No new product scope was added. The only implementation delta after NO-GO is the cache-entry shape guard in `groundtruth-kb/src/groundtruth_kb/session/packet.py` and the additional focused tests in `platform_tests/groundtruth_kb/test_session_envelope_packet.py`.

## Pre-Filing Preflight Subsection

Preflights run before filing this REVISED candidate:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache --json` - passed; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache` - passed; 5 clauses evaluated, 2 must_apply, 3 may_apply, 0 blocking gaps.

The revision helper will also run candidate-content applicability and clause preflights with `--content-file` before live filing.

## Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001` | `python -m pytest platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py -q --tb=short` -> 10 passed. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Same 10-test focused suite now includes tracked-source-hash miss, TTL-expiry miss, cache hit with matching sources/TTL, and malformed non-object cache miss. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Focused suite asserts session-envelope <= 900 and activity-packet <= 500, plus pointer-only overrun. |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | `python -m pytest groundtruth-kb/tests/test_context_manifest.py platform_tests/scripts/test_activity_disposition_profiles.py -q --tb=short` -> 33 passed. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Same 33-test adjacent suite passed. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | `python -m ruff check ...` passed and `python -m ruff format --check ...` passed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Focused and adjacent suites passed; target paths remain confined to approved Slice C files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge state was `NO-GO`; Prime claimed the thread before filing this REVISED correction. |
| Remaining linked governance/project/linkage specs | Bridge metadata, PAUTH/project/work-item linkage, specification links, target paths, and candidate preflights are present in this REVISED entry. |

## Commands Run

- `python -m pytest platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_context_manifest.py platform_tests/scripts/test_activity_disposition_profiles.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/session/packet.py groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/packet.py groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/groundtruth_kb/test_session_envelope_packet.py platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache`

## Observed Results

- Focused packet/CLI suite: 10 tests collected, 10 passed.
- Adjacent context/profile suite: 33 tests collected, 33 passed.
- Ruff check: `All checks passed!`
- Ruff format check: `5 files already formatted`.
- Bridge applicability preflight: passed with no missing required/advisory specs and no blocking errors.
- ADR/DCL clause preflight: passed with no blocking gaps.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `groundtruth-kb/src/groundtruth_kb/session/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/session/packet.py`
- `platform_tests/groundtruth_kb/cli/test_session_envelope_packet_cli.py`
- `platform_tests/groundtruth_kb/test_session_envelope_packet.py`

## Risk And Rollback

Residual risk remains limited to the new packet JSON schema and approximate token estimator. The LO-identified cache freshness risk now has executed tests for matching-cache hit, tracked-source-hash miss, TTL-expiry miss, malformed non-object cache miss, and pointer-only overrun.

Rollback remains the five Slice C target files. Bridge audit files remain append-only.
