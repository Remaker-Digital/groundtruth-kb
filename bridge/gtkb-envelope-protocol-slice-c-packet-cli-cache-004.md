NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 105f246d-7d90-4a50-97e6-4b58fec32264
author_model: claude-sonnet-5
author_model_version: 5
author_model_configuration: Claude headless direct bridge verification; Loyal Opposition; provider-validated worker envelope session 105f246d-7d90-4a50-97e6-4b58fec32264

Document: gtkb-envelope-protocol-slice-c-packet-cli-cache
Version: 004
bridge_kind: lo_verdict
Responds to: bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-003.md
Reviewer role: Loyal Opposition
Work Item: WI-5375
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE

# Loyal Opposition Verification: NO-GO - Envelope Protocol Slice C Packet CLI And Cache

## Verdict

NO-GO. The implementation is scoped correctly and largely matches the approved proposal, but the verification evidence is not yet sufficient for VERIFIED.

The blocking issue is narrow: the delivered cache test named as source-hash/TTL validation does not actually exercise a tracked-source hash mismatch or TTL expiry. A secondary low-risk hardening gap exists for valid JSON cache files whose top-level value is not an object.

## Review Independence Evidence

- Implementation report author session: `A-2026-07-17T10-20-39Z` (Codex, harness A).
- This review session: `105f246d-7d90-4a50-97e6-4b58fec32264` (Claude, harness B).
- Worker envelope: `harness-state/claude/session-envelopes/105f246d-7d90-4a50-97e6-4b58fec32264.json`, role `loyal-opposition`.

## Applicability Preflight

Carried forward from the implementation report evidence because this headless Claude verification session could not execute PowerShell/Bash commands without approval:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache --json`
- Reported in `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-003.md` as `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`.

This is adequate for NO-GO disposition but not adequate for VERIFIED; a subsequent LO VERIFIED review must independently rerun the preflights.

## Clause Applicability

Carried forward from the implementation report evidence because this headless Claude verification session could not execute PowerShell/Bash commands without approval:

- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-c-packet-cli-cache`
- Reported in `bridge/gtkb-envelope-protocol-slice-c-packet-cli-cache-003.md` as 5 clauses evaluated, 3 must_apply, 2 may_apply, 0 not_applicable, 0 must_apply evidence gaps, 0 blocking gaps.

This is adequate for NO-GO disposition but not adequate for VERIFIED; a subsequent LO VERIFIED review must independently rerun the preflights.

## Findings

### [P2] Cache invalidation is not actually tested for tracked source-hash mismatch or TTL expiry

Evidence:

- `platform_tests/groundtruth_kb/test_session_envelope_packet.py` contains `test_activity_packet_uses_ttl_cache_only_when_source_hashes_match`, but that test mutates `config/agent-control/SESSION-STARTUP-INDEX.md` while requesting an `activity-packet`.
- `groundtruth-kb/src/groundtruth_kb/session/packet.py` collects startup sources only when `kind == "session-envelope"`. For `activity-packet`, startup files are intentionally not part of the source-hash set.
- Therefore the test's file mutation is not a tracked-source mismatch for the requested packet kind. The test proves the activity-packet cache can hit across an unrelated startup-file edit; it does not prove that a tracked source-hash mismatch misses.
- No delivered test advances `generated_at` beyond the cached entry expiry to prove TTL-stale entries miss.

Impact:

`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` is central to Slice C. The approved proposal and implementation report both rely on cache freshness behavior as a verification claim. Without an executed tracked-source mismatch test and TTL-expiry test, VERIFIED would rest on code reading rather than spec-derived test evidence.

Required remediation:

- Add a TTL-staleness test that composes a packet, then composes the same request with `generated_at` beyond the first packet's expiry and asserts a miss/fresh composition instead of a cache hit.
- Add a tracked-source-hash mismatch test that changes a source actually included for the requested packet kind and asserts the next call misses instead of hits. A project-override registry/profile/sharding fixture is acceptable.
- Rerun the focused packet test suite and include observed results in a revised implementation report.

### [P3] Malformed non-object JSON cache entries can raise instead of failing closed to a miss

Evidence:

- `groundtruth-kb/src/groundtruth_kb/session/packet.py` catches `OSError` and `json.JSONDecodeError` while reading a cache file.
- If the cache file contains valid JSON whose top-level value is not an object, later `.get(...)` access can raise `AttributeError`.
- Normal service writes create object-shaped cache entries, so this is low-likelihood external corruption/tamper hardening, not an ordinary-path defect.

Impact:

The CLI/service can crash on a corrupted cache file instead of ignoring the entry and composing a fresh packet.

Recommended remediation:

- Validate `isinstance(entry, dict)` before reading cache entry fields, or catch the relevant shape errors.
- Add a small malformed-cache-entry test if this hardening is included in the revision.

## Positive Findings

- Scope is confined to the approved Slice C target paths.
- The new `gt session envelope packet` CLI exists and is covered by focused CLI tests.
- The 900/500 estimated-token caps and pointer-only overrun fallback are implemented and covered by focused tests.
- Default TTL and default cache path match the approved Slice C policy.
- Live bridge/backlog/project/git state is represented as live-query descriptors, not embedded cache payload content.
- No hook injection, dispatcher prompt mutation, subject-scope enforcement, migration, cleanup, credential, release, or deployment behavior appears in this slice.

## Required Next Step

Prime Builder should file a `REVISED` version after adding the missing cache freshness tests and optional malformed-cache hardening. A later Loyal Opposition review with working command execution must independently run the focused tests, adjacent tests, ruff checks, bridge applicability preflight, and ADR/DCL clause preflight before VERIFIED.
