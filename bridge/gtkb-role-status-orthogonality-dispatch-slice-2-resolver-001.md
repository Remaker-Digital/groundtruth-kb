NEW

bridge_kind: implementation
Document: gtkb-role-status-orthogonality-dispatch-slice-2-resolver
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-01 UTC
Session: S379
Recommended commit type: feat
Project Authorization: PAUTH-PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH-ROLE-STATUS-ORTHOGONALITY-DISPATCH-SLICE-2-RESOLVER-ATTRIBUTION
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-3509

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S379-role-status-orthogonality-slice-2-resolver-001
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Slice 2: Status-Aware Dispatch Resolver + Active-PB Attribution

## Source / Authorizing Verdict

This proposal is filed under the umbrella scoping proposal
`gtkb-role-status-orthogonality-dispatch-scoping`, which received Loyal
Opposition GO at `bridge/gtkb-role-status-orthogonality-dispatch-scoping-004.md`
(2026-05-31). Slice 1 (the governing ADR + DCL) is VERIFIED at
`bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-010.md`. This
slice implements the resolver + attribution behavior that
`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` declares as its implementation
contract.

## Proposal Kind

`bridge_kind: implementation`. This proposal authorizes source and test
mutation only, bounded by the cited PAUTH (allowed mutation classes
`source-code`, `tests`; forbids narrative-artifact and formal-artifact
mutation). It does NOT touch GOV/ADR/DCL/PB MemBase rows, protected narrative
(`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`), packet generators, or doctor
checks — those are Slices 3-7.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions /
Input Section Gate".

1. **Owner directive (S378 prompt, 2026-05-31)** — captured in
   `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`. Role assignment and dispatch
   eligibility are orthogonal axes; multiple harnesses may share a role; only
   the single `status=active` harness per role is auto-dispatch-eligible. This
   is the owner-decision that the cited PAUTH records as its
   `owner_decision_deliberation_id`.

2. **Owner directive (S379 task, 2026-06-01)** — the owner explicitly directed
   implementation of Slice 2 (resolver + attribution code) as the slice that
   fixes the live dual-PB AXIS-1 dispatch break, with the file scope, assertion
   coverage (1-7, 10, 11), and coordination caveat enumerated in the task.

3. **Owner AskUserQuestion answers (S378, 2026-05-31)** carried forward from
   Slice 1: status taxonomy = "4-state owner-aligned" (`active`, `inactive`,
   `suspended`, `retired`; only `active` dispatch-eligible); ADR shape = "New
   successor ADR + amend old". These are the live semantics this slice
   implements.

4. **Owner decision required at Slice 2 LANDING (not now)** — registry
   reconciliation. The live `harness-state/harness-registry.json` records BOTH
   harness B (claude) AND harness C (antigravity) as `prime-builder` /
   `status=active`. Per the S379 task ("Flag it; don't silently flip C") this
   proposal does NOT modify the registry. After this slice is VERIFIED, Prime
   will surface an AskUserQuestion asking the owner whether to set C to
   `status=inactive` (restoring single-active-PB) or take another action. Until
   then the resolver will *correctly* raise multi-ACTIVE for `prime-builder`
   (see Coordination Caveat below).

No new owner approval is requested by this proposal beyond the standing S378/S379
directives above; bridge GO + the implementation-start packet provide the
mechanical implementation authorization.

## Specification Links

All citations verified LIVE against the live `specifications` table before
filing (21/21 present; 0 phantom).

- `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 — parent ADR; defines role/status
  orthogonality and the single-ACTIVE-per-role invariant this slice implements.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 — the machine-checkable
  constraint; this slice implements + tests assertions 1-7, 10, 11. Assertions
  8-9 (doctor FAIL/WARN) are Slice 6; the doctor half of assertion 6 (FAIL on
  unknown status) is Slice 6, while the resolver half (treat unknown as
  inactive) is in this slice.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 — single-harness topology +
  role-set schema; `_is_single_harness_topology` status-awareness is consistent
  with its multi-element role-set marker.
- `GOV-ACTING-PRIME-BUILDER-001` v1 — READ-accept/SET-reject contract for the
  legacy `acting-prime-builder` token; assertion 11 (legacy token matches
  prime-builder for dispatch) preserves it.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 — authority split; assertion 10 (resolver
  ignores the ephemeral session-stated role marker) preserves headless dispatch
  keyed to durable role+status.
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 — session-stated role governs in-session
  surfaces, not dispatch target selection (assertion 10).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 — unchanged; coexists.
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 — role portability preserved; resolver
  still resolves by durable role, now AND status.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 — multi-harness config preserved.
- `REQ-HARNESS-REGISTRY-001` v2 — the registry projection (`status`,
  `invocation_surfaces`) is the data surface the resolver filters on.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — this proposal's
  spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — spec-to-test mapping
  compliance (every implemented assertion maps to a test below).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — the Project
  Authorization / Project / Work Item header lines satisfy CLAUSE-PROJECT-
  METADATA-PRESENT and CLAUSE-PROJECT-AUTH-LIVE-CHECK (PAUTH active, includes
  WI-3509).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 — cross-harness enforcement context.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 — all modified files are in-root
  under `E:\GT-KB` (`scripts/`, `platform_tests/`, `bridge/`); no out-of-root
  file mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 — advisory.
- `GOV-STANDING-BACKLOG-001` v5 — WI-3509 tracked under the umbrella project;
  this is not a bulk operation.

## Clause Scope Clarification (Not a Bulk Operation)

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` fires on this proposal's
backlog/work-item vocabulary, but this is a single-work-item implementation
(WI-3509), NOT a bulk backlog operation. No bulk mutation of the standing
backlog occurs:

- No bulk inventory artifact is required — the single work item (WI-3509) was
  captured individually via the governed `gt backlog add` path, carrying its
  own provenance (source spec, related specs/deliberations/bridge threads).
- No bulk review-packet or `DECISION DEFERRED` batch marker applies — there is
  no multi-item batch to review or defer en masse.
- No formal-artifact-approval-gated bulk action occurs — the cited PAUTH
  forbids formal-artifact mutation entirely; Slice 2 mutates only source and
  test files.

The single-item capture is visible in MemBase (`gt backlog show WI-3509`) and
linked to the umbrella project via membership `PWM-PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH-WI-3509`.
The bulk-operation visibility clause is therefore not applicable.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner directive source for
  the entire umbrella; the PAUTH's owner-decision deliberation.
- `DELIB-2507` — S371 interactive session role override owner directive; the
  durable-vs-session-stated authority split that assertion 10 preserves.
- `DELIB-2079` — Antigravity 3-harness design + harness-registry architecture
  (origin of the `status` field this slice filters on).
- `DELIB-2080` — single-PB invariant + role portability (superseded in part by
  the parent ADR).
- `DELIB-2094` — VERIFIED `gtkb-harness-role-portability-fr9` (WI-3341 history).
- `DELIB-2342` / `DELIB-2344` — prior bridge role-intent sentinel reviews
  (kept role authority distinct from mirror/checksum surfaces).
- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` — Slice 1 owner waiver; not
  directly applicable here (no formal-artifact mutation in Slice 2) but
  documents the Slice 1 closure this slice builds on.

No prior deliberation rejected the status-aware-resolver approach; Slice 1's
VERIFIED ADR/DCL is the direct authorizing precedent.

## Requirement Sufficiency

**Existing requirements sufficient.**

`ADR-ROLE-STATUS-ORTHOGONALITY-001` and `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
(both VERIFIED into MemBase at Slice 1) fully specify the resolver behavior,
the status taxonomy, the three-way resolution outcome, the fail-closed
treatment of missing/unknown status, the legacy-token semantics, the
session-marker exclusion, and the single-harness-topology status-awareness. No
new or revised requirement is needed before implementation.

## target_paths

Machine-readable authorized paths (the implementation-start gate reads this
single line via `TARGET_PATHS_RE`; the bullets below are human-readable detail):

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/_kb_attribution.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_kb_attribution.py", "bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-*.md", "bridge/INDEX.md"]

Proposal-filing phase:

- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-001.md` (this file)
- `bridge/INDEX.md` (NEW entry insertion at top)

Implementation phase (post-GO; authorized by the implementation-start packet
against the eventual GO, bounded by the PAUTH `source-code` + `tests` classes):

- `scripts/cross_harness_bridge_trigger.py` — `_record_has_role`,
  `_resolve_dispatch_target`, `_is_single_harness_topology`, and the
  `_resolve_dispatch_target` call site in `run()`.
- `scripts/_kb_attribution.py` — rename + docstring/framing update for
  active-PB attribution semantics.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — status-aware
  resolver + topology tests (assertions 1-7, 10, 11).
- `platform_tests/scripts/test_kb_attribution.py` — active-PB attribution test.
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-*.md` (next
  monotonic post-implementation report version).

Out-of-scope concrete paths (NOT authorized): `groundtruth.db` and MemBase
formal-artifact rows; any `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`
(narrative — Slice 4); `scripts/single_harness_bridge_dispatcher.py` and
`groundtruth_kb/...mode_switch/derive` (see Scope Decision 2); packet generators
(Slice 5); `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (Slice 6);
`harness-state/harness-registry.json` (Slice 7 reconciliation); any config,
hook, or deployment file.

## Implementation Design (Precise Changes)

### File 1 — `scripts/cross_harness_bridge_trigger.py`

**1a. `_record_has_role` (~L951-957) — assertion 11.** Extend role matching so a
role-set containing the legacy `acting-prime-builder` token matches the
`prime-builder` label (READ-accept + compatibility/provenance semantics per
`GOV-ACTING-PRIME-BUILDER-001`):

```
def _record_has_role(h_info, wanted):
    raw = h_info.get("role")
    if isinstance(raw, str):
        candidates = {raw.strip().lower()}
    elif isinstance(raw, (list, tuple, set, frozenset)):
        candidates = {str(r).strip().lower() for r in raw}
    else:
        candidates = set()
    if wanted in candidates:
        return True
    # assertion 11: acting-prime-builder (legacy) matches prime-builder.
    if wanted == "prime-builder" and "acting-prime-builder" in candidates:
        return True
    return False
```

**1b. `_resolve_dispatch_target` (~L920-1007) — assertions 1-6.** Signature
becomes `(needed_role_label, project_root, state_dir: Path | None = None) ->
DispatchTarget | None`. The optional `state_dir` preserves the existing 2-arg
test callers; the production call site passes it so the zero-active audit can be
emitted. Logic:

- Unknown role label → raise `ValueError` (unchanged).
- Compute `role_matching` (records whose role-set contains the label, via 1a).
- Add `_is_active(h_info)`: `status = h_info.get("status"); return isinstance(status, str) and status.strip().lower() == "active"`. Missing / null / empty / any non-`active` value → inactive (assertions 5, 6 resolver-half).
- `active_matching = [(hid, rec) for (hid, rec) in role_matching if _is_active(rec)]`.
- `len(active_matching) == 0`: if `state_dir` is provided, emit ONE record to `dispatch-failures.jsonl` via `_record_dispatch_failure` with `reason="no_active_target_for_role"`, `recipient=needed_role_label`, `error_message` naming the role (and, when role-set members exist but are inactive, listing their IDs). Return `None` (assertion 2; NO raise).
- `len(active_matching) > 1`: `raise ValueError(f"multiple active harnesses for role {needed_role_label!r}: {sorted(ids)}")` (assertion 3).
- exactly one: proceed with the existing identity-resolution + drift-check +
  `invocation_surfaces` attach path and return the `DispatchTarget` (assertion
  4; downstream unchanged).

The status filter operates on the records returned by `_read_role_assignments`,
which (per WI-3342 IP-4) reads `harness-state/harness-registry.json` — each
record already carries `status`. No new file read is introduced.

**1c. `_is_single_harness_topology` (~L1181-1209) — assertion 7.** In addition to
the existing "exactly one harness AND role-set contains both `prime-builder` and
`loyal-opposition`" check, require `record.get("status")` to equal `active`
(case-insensitive). Missing/unknown status → not active → returns `False` (the
trigger then proceeds on its normal multi-harness path, where the resolver finds
the inactive single harness as zero-active → sentinel + audit). Fail-closed on
unreadable role-map is unchanged.

**1d. `_resolve_dispatch_target` call site in `run()` (~L1385-1415).** Pass
`state_dir`; thread the sentinel. The `pending_by_target` tuples gain a 5th
element (the failure reason):

- `except ValueError` (multi-active / drift / unknown label / missing identity):
  unchanged — record `dispatch_target_resolution_failed` to
  `dispatch-failures.jsonl`, append `(None, ..., "dispatch_target_resolution_failed")`.
- returned `None` (zero-active sentinel; resolver already emitted the
  `no_active_target_for_role` audit): append `(None, ..., "no_active_target_for_role")`
  WITHOUT a second `_record_dispatch_failure` call (no double entry).
- success: append `(target, ..., None)`.

In the consumption loop, the `target is None` branch sets
`results[recipient] = {"launched": False, "reason": <failure_reason>}` and writes
`recipients_state[recipient]["last_result"] = <failure_reason>` (+ `updated_at`)
so the persisted `dispatch-state.json` reflects the DCL resolution table's
`last_result` column for the 0/2+ rows. The final `_write_dispatch_state` already
persists `recipients_state`.

### File 2 — `scripts/_kb_attribution.py`

The active-status filter already lives upstream: `load_role_assignments`
(`scripts/harness_roles.py`) returns ONLY `status=="active"` harnesses (it
filters and strips `status` from the record). So `_kb_attribution` already
resolves attribution against active harnesses; this change makes the framing
accurate and the intent explicit. No functional logic is duplicated (status data
is not available at this layer, by design).

- Rename `_sole_prime_builder_harness_name` → `_active_prime_builder_harness_name`
  (def ~L125; sole caller in `_resolve_harness_name` ~L150). No test references
  the old private name (verified by repo grep).
- Update the function docstring to state it returns the single ACTIVE Prime
  Builder's name (0 or >1 → `None`), and that the active-filter is applied
  upstream by `load_role_assignments`.
- Update the module docstring priority-3 line (~L16-18) and the
  `resolve_changed_by` priority-3 line (~L204-207): "The active Prime Builder
  harness in the harness registry (exactly one harness holding `prime-builder`
  with `status == "active"`; raises `RuntimeError` if zero or multiple active
  Prime Builders exist)."

### File 3 — `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

Add a `_write_registry(root, records)` helper (writes a
`harness-state/harness-registry.json` projection + matching identities from a
list of `{id, harness_name, role, status, invocation_surfaces}` dicts) and tests
for each implemented assertion (see Spec-Derived Verification Plan). All tests
construct fixtures in `tmp_path`; none read the live registry.

### File 4 — `platform_tests/scripts/test_kb_attribution.py`

Add one test pinning the active-PB attribution semantic: a tmp registry fixture
with B = `prime-builder`/`active` and C = `prime-builder`/`inactive`, exercised
via the `GTKB_HARNESS_REGISTRY_PATH` env override (honored by the projection
reader). `resolve_changed_by()` (no kwarg/env-name) resolves to
`prime-builder/claude` and does NOT raise, proving the inactive PB is filtered
(ADR-ROLE-STATUS-ORTHOGONALITY-001 Consequences §1).

## Spec-Derived Verification Plan

Every implemented DCL assertion maps to at least one test. Tests live in the two
test files above and run under the system Python interpreter that has
`groundtruth_kb` importable.

| DCL assertion | Test (intent) |
|---|---|
| 1 `dispatch_filters_by_active_status` | 1 active PB + 1 inactive PB (same role) → resolve returns the active harness; the inactive one is never selected. |
| 2 `zero_active_returns_sentinel_and_audits` | role-members all inactive → resolve returns `None`; `dispatch-failures.jsonl` has exactly one new record with `reason="no_active_target_for_role"`, `recipient=<role>`. |
| 3 `multi_active_raises_value_error` | 2 active PB (B, C) → resolve raises `ValueError` whose message names both IDs. |
| 4 `exactly_one_active_dispatches` | 1 active PB + 1 active LO → resolve returns a `DispatchTarget` with the correct `harness_id`, `command_handle`, `canonical_mode`, and attached `invocation_surfaces`. |
| 5 `status_missing_treated_as_inactive` | role-member record with no `status` key → treated inactive → zero-active sentinel. |
| 6 `status_unknown_treated_as_inactive` (resolver half) | role-member `status="bogus"` → treated inactive → zero-active sentinel. (Doctor FAIL on unknown is Slice 6.) |
| 7 `single_harness_dispatcher_status_aware` | single harness, multi-role-set: `status="active"` → `_is_single_harness_topology` True; `status="inactive"` / missing → False. |
| 10 `session_stated_role_does_not_affect_dispatch_target` | with an `.claude/session/active-session-role.json` marker present in `tmp_path`, resolve still keys off durable role+status (marker not consulted; result identical to no-marker). |
| 11 `acting_prime_builder_legacy_token_read_accepted` | role-set `["acting-prime-builder"]` + `status=active` → resolve("prime-builder") matches it and returns its `DispatchTarget`. |
| ADR Consequences §1 (attribution) | active-PB attribution test in `test_kb_attribution.py` (B active-PB + C inactive-PB → `prime-builder/claude`, no raise). |

Verification commands (run in implementation phase; results in the post-impl
report):

- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_kb_attribution.py -q --tb=short`
- `python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/_kb_attribution.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_kb_attribution.py`
- `python -m ruff format --check` on the same four files (separate gate from `ruff check`).
- Baseline-delta evidence: the pre-existing failures enumerated below remain the
  only failures; every new test passes; no previously-passing test regresses.

## Pre-Existing Test Baseline (NOT introduced by this slice)

Captured by running the affected files at the current commit BEFORE any Slice 2
change. These are documented so verification can confirm a zero-regression
delta; this slice does not fix them (see Scope Decisions).

- `platform_tests/scripts/test_governing_specs_preserved.py` — 7 failures. Root
  cause: its `_write_harness_state` helper writes `role-assignments.json` but not
  the `harness-registry.json` that `_read_role_assignments` now requires
  (fallout from the WI-3342 IP-4 registry-reader migration). They fail with
  `ValueError: harness-registry.json not found` BEFORE any status logic runs.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — 1 failure
  (`test_harness_command_builds_argv_from_invocation_surfaces`): a `--permission-mode`
  invocation-surfaces argv mismatch, unrelated to role/status.
- `platform_tests/scripts/test_kb_attribution.py` — 1 failure
  (`test_single_prime_fallback_resolves_to_claude`): reads the LIVE registry and
  the current dual-active-PB state makes priority-3 resolution `RuntimeError`.
  This is the live break surfacing in a test; it self-heals after registry
  reconciliation (Slice 7 / the landing AUQ).

Total pre-existing: 9 failures. The post-impl report will show the same 9 (minus
any that the new fixtures legitimately supersede) and zero new regressions.

## Coordination Caveat (Live Dual-PB State)

The live `harness-state/harness-registry.json` records B (claude) AND C
(antigravity) both `prime-builder` / `status=active`. This slice makes the
resolver status-aware but does NOT modify the registry. Therefore, immediately
after this slice lands, resolving `prime-builder` will still find two ACTIVE
matches and `raise ValueError` (assertion 3) — i.e., AXIS-1 PB auto-dispatch
remains broken at runtime until the registry is reconciled (C → `status=inactive`).
That reconciliation is owner-decision territory and is deliberately deferred: per
the S379 task, this proposal flags it rather than silently flipping C. Prime will
surface an `AskUserQuestion` at Slice 2 landing.

## Scope Decisions & Noted Follow-ons

1. **Pre-existing test failures are not fixed here.** Per GOV-07 (record defects
   as WIs) and GOV-15 (no fixing failed tests without owner approval), and to
   keep this slice within the owner's stated file scope, the 9 pre-existing
   failures are documented (above) and captured as a follow-on backlog WI under
   the umbrella project. The 7 governing-specs failures share one root cause
   (the stale `_write_harness_state` fixture) and would be a clean separate fix.

2. **Assertion 7 covers the named `_is_single_harness_topology` only.** The
   single-harness *dispatcher* has a separate gate,
   `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable`,
   which delegates topology to the shared
   `groundtruth_kb.mode_switch.derive.topology_from_role_map` (used by startup,
   workstream-focus, and the dispatcher). Making that path status-aware is a
   broader change beyond this slice's file scope and is noted as a follow-on
   (candidate for Slice 6/7 or a dedicated thread). Assertion 7 names
   `_is_single_harness_topology` (the cross-harness-trigger gate, in scope),
   which this slice implements + tests.

## Risk & Rollback

Risks:

- **Signature change to `_resolve_dispatch_target`.** Mitigated by making
  `state_dir` optional (default `None`); all existing 2-arg callers keep
  compiling, and the new return type `DispatchTarget | None` is already handled
  by the sole production caller (which already branches on `target is None`).
- **Behavior change: zero-active now returns a sentinel instead of raising.**
  This is the spec-required change (assertion 2). The caller already tolerates a
  `None` target. Tested directly.
- **Over-broad status matching.** Mitigated by fail-closed default
  (missing/unknown → inactive) and direct tests (assertions 5, 6).

Rollback: all changes are source + test; `git revert` of the implementation
commit fully restores prior behavior. No MemBase/append-only state is mutated by
this slice.

## Out of Scope

- Registry reconciliation (C → inactive). Slice 7 / landing AUQ.
- Doctor checks `_check_single_active_per_role` (assertions 8-9). Slice 6.
- The single-harness dispatcher's `_is_single_harness_topology_applicable` /
  `topology_from_role_map` status-awareness. Noted follow-on (Scope Decision 2).
- Fixing the 9 pre-existing test failures. Captured as a follow-on WI.
- GOV rule updates (Slice 3), protected-narrative rewrites (Slice 4), packet
  generator regen (Slice 5).
