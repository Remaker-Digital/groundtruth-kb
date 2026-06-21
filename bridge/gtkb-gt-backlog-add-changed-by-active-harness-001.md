NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - gt backlog add wrote changed_by=prime-builder/codex while the active harness is Claude (B) operating as Prime Builder — attribution mis-resolution

bridge_kind: prime_proposal
Document: gtkb-gt-backlog-add-changed-by-active-harness
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4632

target_paths: ["scripts/_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The harness-aware `changed_by` resolver in `scripts/_kb_attribution.py` mis-resolves the harness-NAME segment of `changed_by` for an interactive session that operates under a session-stated role override (`::init gtkb pb`). When the writing harness has no `GTKB_HARNESS_NAME` in its environment and is NOT the durable Prime Builder, `resolve_changed_by()` falls back to `_active_prime_builder_harness_name()`, which returns the *durable* Prime Builder's name. The Slice-6 session-role override (`_session_role_override`) then corrects only the role LABEL (the segment before `/`), not the harness name. The result is `<role>/<wrong-harness>` — e.g. `prime-builder/codex` written by Claude (B). This contradicts the harness-aware attribution contract, whose purpose is that `changed_by` names the harness that actually performed the write.

## Defect / Reproduction

Observed incident (origin of WI-4632): WI-4627 was created on 2026-06-17 from the Claude harness (id `B`), in an interactive session whose role was session-stated to Prime Builder via `::init gtkb pb`. The `work_items` row recorded `changed_by=prime-builder/codex`. The active harness was Claude, not Codex. The role segment (`prime-builder`) was correct via the Slice-6 label override; the harness segment (`codex`) was wrong.

Root cause (logical, by inspection of `scripts/_kb_attribution.py`):
1. `gt backlog add` resolves attribution fail-closed through `resolve_changed_by()` (no `--changed-by`, no literal fallback) — `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py::_resolve_changed_by`.
2. `resolve_changed_by(harness_name=None)` calls `_resolve_harness_name(None)`, whose three sources are: (a) explicit kwarg (none for the CLI), (b) `GTKB_HARNESS_NAME` env var (not set in the writing subprocess), (c) `_active_prime_builder_harness_name()`.
3. With the durable Prime Builder being Codex (A) at the time of the incident, source (c) returned `codex`.
4. `effective_role = _session_role_override(resolved) or role` (line 270) overrode the role to `prime-builder` from the open session marker — but the harness name was already fixed at `codex`. `_session_role_override` is documented as "LABEL OVERRIDE ONLY" and never touches the harness name.
5. Final attribution: `prime-builder/codex`.

Reproduction (logical, deterministic): construct state where the durable role map assigns Prime Builder to harness `A` (`codex`) and the writing harness is `B` (`claude`) operating interactively with a fresh per-session role marker / open session envelope declaring `role: prime-builder`, and with `GTKB_HARNESS_NAME` unset. Call `resolve_changed_by()` with no explicit `harness_name`. Current behavior returns `prime-builder/codex`. Expected: `prime-builder/claude` — the harness segment must name the harness whose interactive session declared the role.

Authoritative writing-harness signal available for the fix: the open per-harness session envelope `harness-state/<harness_name>/session-envelope.json` carries `harness_name`, `role_resolved`, and `status: "open"` (WI-4663; already consumed by `scripts/session_role_resolution.py::resolve_interactive_session_role`). The envelope's directory key and `harness_name` body field identify the harness that owns the current interactive session, independent of the durable role map.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/_kb_attribution.py`, `platform_tests/scripts/test_kb_attribution_session_role.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this defect-fix moves through the bridge protocol (NEW → GO → implement → report → VERIFIED); the proposal cites bridge authority for the change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `changed_by` is the durable provenance field of the `work_items` artifact; correct harness attribution keeps the artifact audit trail trustworthy.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - no AUQ/owner-decision behavior is added or altered by this fix; attribution resolution is internal plumbing, so this seeded cross-cutting spec is acknowledged as not-triggered by the change surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform attribution module (`scripts/_kb_attribution.py`) and platform tests; no application/adopter surface is touched, so the isolation/placement boundary is preserved.
- `GOV-STANDING-BACKLOG-001` - WI-4632 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - acknowledged seeded spec; this fix changes no hook registration or harness-parity surface, so the Codex/Claude hook-parity fallback contract is unaffected.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the provenance segment of a durable artifact stays artifact-backed (resolved from the open session envelope / role marker) rather than inferred incorrectly from the durable role map.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the `_kb_attribution` provenance surface triggers a spec-linked, tested fix per the lifecycle-trigger discipline.

## Prior Deliberations

- `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` - the original Codex-as-Prime KB attribution mis-attribution (39 specs + 20 deliberations mis-attributed); this WI is the same class of mis-attribution surfacing through the session-role-override path rather than the hardcoded-literal path that `gtkb-kb-attribution-harness-aware` fixed.
- `DELIB-20263483` - WI-4522 Author Identity Env Alias Defect; prior provenance/identity-resolution defect in the same attribution/identity family.
- `DELIB-20263700` - Loyal Opposition Review, Backlog Add CLI Slice 1; establishes that `gt backlog add` resolves attribution exclusively through the fail-closed resolver, confirming the defect is in the resolver, not the CLI.
- `DELIB-2026-06-14-WI4483-WI4514-CLOSE-RESOLVED-REGISTRY-CORRECTION` - prior harness role-state correction context (harness-C), illustrating that durable role state and the operating harness can diverge.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4632 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-4632 (P3 defect) is in scope of that batch.

## Requirement Sufficiency

Existing requirements sufficient. The verified harness-aware attribution contract (`bridge/gtkb-kb-attribution-harness-aware-003.md`, Codex GO at `-004`) already establishes that `changed_by` must name the harness that performed the write, and the Slice-6 contract (`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 1, via `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-001.md`) already establishes that a declared interactive session role governs the attribution label. This fix closes the gap that Slice 6 corrected the LABEL but not the HARNESS NAME for the session-stated-override case. No new or revised requirement/specification is introduced.

## Proposed Scope

1. In `scripts/_kb_attribution.py`, add an envelope-aware harness-NAME source so the resolver can name the harness that owns the current interactive session, not the durable Prime Builder:
   - Add a read-only helper (e.g. `_open_session_envelope_harness_name()`) that scans `harness-state/*/session-envelope.json`, and returns the `harness_name` of the single envelope whose `status == "open"` (normalized via `scripts.harness_identity.normalize_harness_name`). It returns `None` when zero or more-than-one open envelopes exist (ambiguity → no name; defer to existing fallback), and is fail-soft on read/parse error (returns `None`). This reuses the WI-4663 envelope surface already consumed by `scripts/session_role_resolution.py`.
   - In `_resolve_harness_name`, insert this source as priority 2.5 — AFTER the explicit kwarg and `GTKB_HARNESS_NAME` env var (both remain higher precedence, so existing wrapper/dispatch behavior is unchanged), and BEFORE the `_active_prime_builder_harness_name()` durable fallback. This means: an interactive session with an open envelope is attributed to its own harness; only when there is no kwarg, no env var, and no unambiguous open envelope does the durable-Prime fallback apply (preserving current behavior for that case).
   - Headless guard: skip the envelope source when `GTKB_BRIDGE_POLLER_RUN_ID` is set, mirroring the existing `_session_role_override` headless guard, so dispatched workers continue to resolve via the explicit env var / durable path and never read a stale interactive envelope.
2. Leave `_session_role_override` (the role-LABEL override) unchanged; the fix is harness-NAME resolution only. The fail-closed durable-role check in `resolve_changed_by` (RuntimeError when no durable role) is preserved unchanged, so the `gtkb-kb-attribution-harness-aware` mis-attribution invariant still holds.
3. Add regression tests in `platform_tests/scripts/test_kb_attribution_session_role.py` (see verification plan).

This is the defect-removal path. It does not add a `--changed-by` option, an attribution literal, or any new public CLI/behavior; it corrects the existing internal resolution order so the harness segment matches the writing harness.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / harness-aware contract (changed_by names the writing harness) | `test_attribution_uses_open_envelope_harness_over_durable_prime` | With durable Prime = `codex`, no `GTKB_HARNESS_NAME`, and a single open `claude` session envelope declaring `role: prime-builder`, `resolve_changed_by()` (no explicit harness_name) returns `prime-builder/claude` (NOT `prime-builder/codex`). |
| harness-aware contract (env var precedence preserved) | `test_attribution_env_var_overrides_open_envelope` | When `GTKB_HARNESS_NAME=codex` is set, it wins over an open `claude` envelope (existing source-2 precedence unchanged). |
| harness-aware contract (no regression when no open envelope) | `test_attribution_falls_back_to_durable_prime_when_no_open_envelope` | With no open envelope, no kwarg, and no env var, the resolver still returns the durable-Prime fallback name (prior behavior preserved). |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` headless invariant | `test_attribution_envelope_source_skipped_under_headless_dispatch` | With `GTKB_BRIDGE_POLLER_RUN_ID` set, the envelope source is skipped and durable resolution is used (dispatched-work attribution stays durable). |
| ambiguity safety (fail to the safe fallback, never guess) | `test_attribution_multiple_open_envelopes_defer_to_fallback` | With two open envelopes, the envelope source returns `None` and the resolver defers to the durable fallback rather than picking one. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short`
- `python -m ruff check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`
- `python -m ruff format --check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`

## Acceptance Criteria

1. For an interactive session with a single open session envelope, no `GTKB_HARNESS_NAME`, and a durable Prime Builder that is a different harness, `resolve_changed_by()` returns `<role>/<envelope-harness-name>` (the writing harness), reproducing WI-4632's expected `prime-builder/claude`.
2. Existing precedence is preserved: explicit kwarg and `GTKB_HARNESS_NAME` still win over the envelope source; the durable-Prime fallback still applies when no kwarg, env var, or unambiguous open envelope exists.
3. Headless dispatch (`GTKB_BRIDGE_POLLER_RUN_ID` set) keeps durable attribution.
4. The fail-closed durable-role check (RuntimeError on no durable role) is unchanged.
5. All derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: an open envelope from a different concurrent interactive session could be picked up. Mitigation: the envelope source returns a name ONLY when exactly one envelope is `status: "open"`; zero or multiple open envelopes → `None` → existing fallback. The headless guard further isolates dispatched workers.
- Risk: precedence change could alter attribution for callers that relied on the durable fallback while an envelope happened to be open. Mitigation: the envelope source is inserted below the explicit kwarg and `GTKB_HARNESS_NAME` (the sources real wrappers/dispatch use), so only the no-kwarg/no-env interactive path is affected — which is exactly the defective path.
- Risk: stale `status: "open"` envelope left on disk. Mitigation: this is the same staleness surface `scripts/session_role_resolution.py` already trusts for `role_resolved`; aligning harness-name resolution with the established envelope authority keeps behavior consistent and is no worse than the status quo. Any envelope-staleness hardening is out of scope for this fast-lane fix.
- Rollback: revert the `_resolve_harness_name` ordering change and the new helper in `scripts/_kb_attribution.py`; the change is additive (one helper + one inserted source) plus tests, fully reversible with no migration and no schema change.

## Files Expected To Change

- `scripts/_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`

## Recommended Commit Type

`fix`
