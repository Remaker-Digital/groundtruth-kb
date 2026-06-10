NEW

# Startup Relay Cache In-Window Self-Heal When Inner Freshness Contract Fails (WI-3486)

bridge_kind: prime_proposal
Document: gtkb-startup-relay-cache-ttl-self-heal
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-SESSION-SELF-INITIALIZATION-001; GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001; WI-3486
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3486
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The interactive startup-disclosure relay cache fails closed for the remainder of its outer 30-minute TTL window when the inner SessionStart write becomes stale, and it self-heals only at the next SessionStart. When the owner types `::init gtkb pb` (or `::init gtkb lo`) on an interactive session whose relay cache is older than the TTL, the relay path serves a startup-relay FAILURE diagnostic instead of the owner-visible startup disclosure, with no in-window regeneration.

Evidence — the outer relay cache is written ONLY at SessionStart, then validated against a hard 1800-second TTL on the UserPromptSubmit init-keyword path:

- `scripts/workstream_focus.py:100` sets `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS = STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS` (`30 * 60`).
- `scripts/workstream_focus.py:1212-1225` (`_startup_relay_cache_fresh`) returns `False` once `age_seconds > STARTUP_RELAY_CACHE_MAX_AGE_SECONDS`, where `age_seconds` is measured from the cache metadata's `generated_at` to the lifecycle-guard reference time.
- `scripts/workstream_focus.py:1299-1309` (`_startup_relay_pointer`) folds `freshness_ok` into `consistent`; when only freshness fails, `consistent` becomes `False`.
- `scripts/workstream_focus.py:1366-1378` (`_startup_gate_response`) returns the `_startup_relay_failure_context(...)` diagnostic (which instructs the harness to "NOT treat startup as satisfied … report this startup-relay failure to the owner") whenever `consistent` is `False`. This is the path reached at `scripts/workstream_focus.py:1482` from the interactive init-keyword handler.
- The only writer is `.claude/hooks/session_start_dispatch.py:495-527` (`_write_startup_relay_cache`, stamping `generated_at = _now_iso()` at line 518) plus `_write_role_scoped_startup_relay_caches` (lines 530-551), invoked exclusively from the SessionStart `main()` at lines 636-637 after the inner freshness-contract validation passes. No UserPromptSubmit path regenerates the cache.

Observed symptom (S373, 2026-05-30): a `::init gtkb pb` relay on a long-lived session failed validation because the relay cache age exceeded the 1800-second TTL; the cache only auto-regenerated on a later SessionStart (forensic snapshot at `.gtkb-state/startup-relay-defect-evidence/`). The recently-VERIFIED `gtkb-startup-enhancements-p2-freshness-contract` thread does NOT moot this: it removed the inner startup-service *payload* cache short-circuit inside `scripts/session_self_initialization.py` (a different cache). The outer relay cache (`.claude/hooks/last-user-visible-startup-{pb,lo}.md` + `.meta.json`) and its 1800-second validator in `scripts/workstream_focus.py` are untouched and remain SessionStart-bound.

This proposal adds a minimal in-window self-heal: when the interactive init-keyword relay path finds the relay cache stale on the freshness dimension while it is otherwise structurally consistent, it regenerates the relay cache in-process (by invoking the same writer the SessionStart path uses) and re-reads it, instead of waiting out the outer TTL. It is a genuine small single-concern defect fix with no new API, CLI, requirement, or externally visible behavior beyond removing the fail-closed gap.

## Specification Links

- GOV-SESSION-SELF-INITIALIZATION-001 — requires the fresh-session self-initialization disclosure to be presented to the owner; a relay path that fails closed for up to 30 minutes and serves a failure diagnostic instead of the disclosure is non-compliance with this requirement. This is a WI-3486 governing specification.
- GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 — requires proactive session-lifecycle engagement without a degraded stale-cache fallback; the outer-TTL fail-closed gap forces the owner to wait for the next SessionStart rather than receive in-window regeneration, which this fix corrects.
- GOV-RELIABILITY-FAST-LANE-001 — governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the change is within bridge-governed reliability infrastructure; `bridge/INDEX.md` remains canonical workflow state and is unchanged by this fix.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the startup disclosure is a governed emitted artifact; in-window regeneration preserves the governed artifact path rather than serving a degraded fallback.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward.

## Fast-Lane Eligibility

This thread claims eligibility under GOV-RELIABILITY-FAST-LANE-001 and the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (covers-by-membership: WI-3486 is an active member of PROJECT-GTKB-RELIABILITY-FIXES, confirmed live in the `work_items` table — `origin=defect`, `priority=P3`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`, `resolution_status=open`). The four eligibility criteria:

1. Origin defect/regression — met. WI-3486 has `origin=defect`; the outer-TTL fail-closed gap is a defect against GOV-SESSION-SELF-INITIALIZATION-001 and GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001, observed in S373 with forensic evidence.
2. No new API/CLI/behavior beyond removing the defect — met. The fix adds no CLI surface and no public API. The relay path's output for a fresh/consistent cache is byte-identical; the only change is that a freshness-only-stale-but-structurally-consistent cache is regenerated in-window and then relayed, instead of producing a failure diagnostic. The regeneration reuses the existing SessionStart writer; no new content shape is introduced.
3. No new requirement — met. GOV-SESSION-SELF-INITIALIZATION-001 already requires the disclosure to be presented; the fail-closed gap is non-compliance with that existing requirement. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. Small single-concern scope — met. One concern: in-window self-heal of the startup relay cache. The change touches the relay reader/gate in `scripts/workstream_focus.py`, reuses the writer in `.claude/hooks/session_start_dispatch.py`, and adds regression tests; no cross-cutting change.

## Prior Deliberations

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md` (VERIFIED) removed the inner startup-service payload cache from `scripts/session_self_initialization.py`. The S373 auto-memory record flagged that this thread "likely partly mooted" WI-3486 and directed verifying residual risk before fixing or closing. This proposal records the verification: the inner-cache removal targets a different cache; the outer relay cache and its 1800-second validator in `scripts/workstream_focus.py` are independent and still SessionStart-bound, so the WI-3486 defect remains live. This proposal closes the residual gap.
- `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` (VERIFIED) corrected the read-allowlist guard in `scripts/workstream_focus.py` so the legitimate raw cache-read command shape is permitted during `startup_response_pending`. That fix concerns the read-permission guard, not the freshness TTL; it does not regenerate a stale cache. This proposal is complementary and does not revisit the allowlist.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` is the structural exemplar for a reliability-fast-lane defect fix under the same standing authorization; this proposal mirrors its scope discipline.
- The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001, PROJECT-GTKB-RELIABILITY-FIXES, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.

## Owner Decisions / Input

No owner decision required — standing fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this by active project membership; no AskUserQuestion needed.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-SELF-INITIALIZATION-001 and GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 already require the fresh-session startup disclosure to be presented proactively without a degraded fallback; the outer-TTL fail-closed gap is non-compliance with those existing requirements. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to the startup relay reader/gate plus reuse of the existing relay writer and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3486) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: In-window self-heal of the startup relay cache on freshness-only staleness

In the interactive init-keyword relay path (`scripts/workstream_focus.py`, where `_startup_gate_response` consults `_startup_relay_pointer`), add a bounded in-window regeneration step. When the relay cache for the resolved `role_mode` exists and is structurally consistent on every dimension EXCEPT freshness (sha256, byte-length, harness name, harness id, role, and startup-disclosure shape all match, but `generated_at` age exceeds `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS`), the path regenerates the relay cache by invoking the same writer the SessionStart path uses (`_write_role_scoped_startup_relay_caches` / `_write_startup_relay_cache` in `.claude/hooks/session_start_dispatch.py`), then re-reads via `_startup_relay_pointer`. If regeneration produces a fresh, consistent cache, the relay proceeds with the disclosure as normal. If regeneration fails or the re-read is still inconsistent for any reason, the existing `_startup_relay_failure_context(...)` diagnostic is returned unchanged — fail-soft is preserved.

The self-heal is gated to the freshness-only case so that a genuinely wrong-role, displaced, or corrupt cache (any non-freshness inconsistency) still produces the failure diagnostic rather than being silently overwritten. The headless dispatch path (`GTKB_BRIDGE_POLLER_RUN_ID` present) is excluded exactly as the existing marker-write branch is, so only interactive owner-typed declarations trigger regeneration.

The exact import/call wiring between `scripts/workstream_focus.py` and the writer in `.claude/hooks/session_start_dispatch.py` (direct import vs. a small shared regeneration entry point) will be finalized at implementation time within these two target files; both files are within `E:\GT-KB` and within `target_paths`. The regeneration reuses the existing role-scoped writer rather than introducing a parallel write path, so the regenerated cache is byte-equivalent to a SessionStart-generated cache.

### IP-2: Regression tests

Add tests under `platform_tests/hooks/test_workstream_focus.py`:

- A freshness-only-stale relay cache (content consistent on all non-freshness dimensions, `generated_at` older than the TTL) on the interactive init-keyword path is regenerated in-window and the relay then returns the disclosure relay source block rather than the failure diagnostic.
- A wrong-role / displaced / sha256-mismatched relay cache (a non-freshness inconsistency) is NOT regenerated and still returns the `_startup_relay_failure_context(...)` diagnostic (the self-heal is freshness-scoped only).
- A headless-dispatch invocation (`GTKB_BRIDGE_POLLER_RUN_ID` set) does not trigger regeneration.
- The fresh/consistent cache path is unchanged: no regeneration occurs and the disclosure relay source block is returned (no behavior regression).

## Out Of Scope

- The inner startup-service payload cache in `scripts/session_self_initialization.py` — owned and already VERIFIED by `gtkb-startup-enhancements-p2-freshness-contract`.
- The startup relay read-permission guard / allowlist in `scripts/workstream_focus.py` — owned and already VERIFIED by `gtkb-startup-relay-truncation-fix-refile`.
- Changing the value of `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS` or the future-skew tolerance — the TTL window itself is unchanged; only the in-window fail-closed gap is fixed.
- Changing the relay cache content, metadata schema, sha256/byte-length validation, or the SessionStart write trigger — the fix adds an in-window regeneration step and reuses the existing writer.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `scripts/workstream_focus.py` — add the freshness-only in-window regenerate-and-re-read step in the interactive init-keyword relay path (IP-1).
- `.claude/hooks/session_start_dispatch.py` — expose / reuse the existing role-scoped relay-cache writer so the interactive path can regenerate the cache in-window without duplicating the write logic (IP-1). No change to the SessionStart trigger behavior.
- `platform_tests/hooks/test_workstream_focus.py` — regression coverage for IP-1 (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-SESSION-SELF-INITIALIZATION-001 | Test: a freshness-only-stale relay cache on the interactive init-keyword path is regenerated in-window and the disclosure relay source block is returned, so the owner-visible disclosure is presented rather than a failure diagnostic. |
| GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 | Test: in-window regeneration occurs without waiting for the next SessionStart; the relay no longer fails closed for the remainder of the outer TTL window. |
| GOV-SESSION-SELF-INITIALIZATION-001 (fail-soft boundary) | Test: a non-freshness inconsistency (wrong role / displaced / sha256 mismatch) is NOT regenerated and still returns the `_startup_relay_failure_context(...)` diagnostic; a headless-dispatch invocation does not regenerate. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The relay reader continues to consult only the harness-scoped cache; `bridge/INDEX.md` and dispatch state are unchanged. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] On the interactive init-keyword relay path, a relay cache that is consistent on all dimensions except freshness is regenerated in-window and the disclosure relay source block is returned; covered by a test.
- [ ] A relay cache with a non-freshness inconsistency (wrong role / displaced / sha256 mismatch) is NOT regenerated and still returns the failure diagnostic; covered by a test.
- [ ] A headless-dispatch invocation (`GTKB_BRIDGE_POLLER_RUN_ID` set) does not trigger regeneration; covered by a test.
- [ ] The fresh/consistent relay cache path is unchanged (no regeneration, disclosure relayed); covered by a test.
- [ ] No change to `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS`, the relay cache content/metadata schema, the SessionStart write trigger, or the read-allowlist guard.
- [ ] `ruff check` and `ruff format --check` pass on the changed files.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

Risk R1 (low): regeneration silently overwrites a cache that should have surfaced a failure. Mitigation: regeneration is gated strictly to the freshness-only case — every non-freshness inconsistency (wrong role, displaced payload, sha256/byte-length mismatch, missing disclosure shape) still returns the failure diagnostic. A dedicated test asserts the non-freshness path is not regenerated.

Risk R2 (low): the interactive relay path importing the SessionStart writer introduces a coupling or import cycle between `scripts/workstream_focus.py` and `.claude/hooks/session_start_dispatch.py`. Mitigation: the wiring reuses the existing writer rather than duplicating logic; the import is bounded to the regeneration step and is exercised by the new tests. If a clean import boundary is not achievable, the regeneration entry point is factored into a small shared helper within the same two target files.

Risk R3 (low): regeneration adds latency to the init-keyword relay turn. Mitigation: regeneration runs only when the cache is already stale (the path that previously failed outright), reuses the existing in-process writer (no subprocess), and is fail-soft — on any error the existing diagnostic is returned, so the worst case is identical to today's behavior.

Rollback: the change is contained to the two source files plus the test file. Reverting `scripts/workstream_focus.py` and `.claude/hooks/session_start_dispatch.py` to their prior versions restores the prior fail-closed behavior; the regeneration step is additive and independently revertible. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm that gating the self-heal to the freshness-only-stale case (regenerate only when every non-freshness dimension is already consistent) is the correct safety boundary, versus regenerating on any inconsistency.
2. Confirm that reusing the existing SessionStart writer (`_write_role_scoped_startup_relay_caches`) from the interactive relay path — rather than introducing a parallel write path — is the right structural choice for byte-equivalence with SessionStart-generated caches.
3. Confirm the scope boundary: this thread fixes only the outer relay-cache in-window self-heal and leaves the inner payload cache (VERIFIED elsewhere) and the read-allowlist guard (VERIFIED elsewhere) untouched.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
