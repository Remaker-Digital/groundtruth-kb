NEW

# Post-Implementation Report: Data-Driven Cross-Harness Dispatch From invocation_surfaces (WI-3344)

bridge_kind: implementation_report
Document: gtkb-harness-data-driven-dispatch
Version: 005 (NEW; post-implementation report for the GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001 (FR8); DELIB-2079 Q9; WI-3344
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3344
target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/seed_harness_registry.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "groundtruth.db", "harness-state/harness-registry.json"]
Recommended commit type: feat:

## Summary

This is the post-implementation report for WI-3344 (data-driven cross-harness dispatch from `invocation_surfaces`), implemented under the GO at `bridge/gtkb-harness-data-driven-dispatch-004.md`. The cross-harness event-driven trigger now builds each harness's dispatch command solely from the registry's `invocation_surfaces` column; the hard-coded `codex`/`claude` switch is gone. The implementation also restored cross-harness dispatch, which was broken in a half-applied state — IP-1 code present, IP-2 registry data absent — so the now-fallback-free trigger failed closed to `unknown_recipient` and could not dispatch a counterpart harness.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — FR8 governs invocation-surface dispatch; the requirement this implements.
- DELIB-2079 — owner-decided Antigravity Integration design; Q9 decided data-driven dispatch with no hard-coded per-harness branch.
- DELIB-2080 — role-portability amendment (FR9); records the Gemini CLI headless invocation form for the Antigravity harness.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the harness operating-mode architecture the registry and this dispatch change extend.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger is bridge dispatch infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this report carries the linked specifications forward from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results are below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 Q9 controls this work — data-driven dispatch from `invocation_surfaces`, no hard-coded per-harness branch. The implementation contains no branch of the rejected class.
- DELIB-2080 records the Gemini CLI headless invocation form, confirming `invocation_surfaces` as the carrier for harness-specific headless invocation data.
- The proposal `-003` (REVISED) received GO at `-004`; this report is the post-implementation submission for that GO. The `-002` NO-GO required removing the hard-coded fallback, which `-003` did.
- WI-3337 (harnesses table, VERIFIED) created the `invocation_surfaces` column; WI-3338 (hot-path projection, VERIFIED) created the `harness-state/harness-registry.json` projection this implementation reads.

## Owner Decisions / Input

The Antigravity Integration project, including data-driven dispatch (DELIB-2079 Q9), was owner-decided via an AskUserQuestion clarification interview on 2026-05-16 (DELIB-2079). The work is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (active; REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344, which includes WI-3344). No new owner decision was required for this implementation; it implements an already-owner-decided requirement through the governed bridge path.

## Clause Scope Clarification (Not a Bulk Operation)

This is a post-implementation report for a scoped code-and-data change: a registry-driven `_harness_command()`, two append-only `harnesses` registry record inserts, a projection regeneration, a seed-script update, and test additions. It is NOT a bulk standing-backlog operation — it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is therefore not applicable. The single work item cited (WI-3344) is this report's own implementing work item under the mandatory project-linkage metadata, not the target of a bulk mutation. All changed files are within the `E:\GT-KB` project root, consistent with `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement.

## Implementation Summary

- IP-1 — `_harness_command()` in `scripts/cross_harness_bridge_trigger.py` is registry-driven: it builds the dispatch argv solely from `target.invocation_surfaces["headless"]["argv"]`, substituting `{{PROMPT}}` and `{{PROJECT_ROOT}}` as individual argv elements; the hard-coded `codex`/`claude` switch is removed; missing/malformed `invocation_surfaces` fails closed to `None` for every harness. A `DispatchTarget.invocation_surfaces` field was added and `_resolve_dispatch_target()` attaches the selected harness record's surfaces from the projection. The IP-1 code body was present as uncommitted edits at GO time; this implementation phase additionally added a module-level `sys.path` bootstrap so the projection import resolves under all load contexts (see Implementation Notes).
- IP-2 — `invocation_surfaces` populated for the two existing harness records via `db.insert_harness()`: harness A (codex) and harness B (claude) each advanced to version 2 carrying a structured `headless` argv template; `harness-state/harness-registry.json` regenerated via `generate_harness_projection()`.
- IP-3 — `scripts/seed_harness_registry.py` updated: a `_SEED_INVOCATION_SURFACES` harness-type-keyed map seeds `invocation_surfaces` for the codex and claude records so fresh installs are consistent with the registry-driven trigger.
- IP-4 — `platform_tests/scripts/test_cross_harness_bridge_trigger.py`: `_make_synthetic_project` now writes a `harness-state/harness-registry.json` projection; `test_dispatched_child_env_does_not_inherit_disable_var`'s directly-constructed `DispatchTarget` carries `invocation_surfaces`; three new tests added (registry-driven argv construction, uniform fail-closed `None`, projection resolve-then-attach integration).

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` — IP-1: registry-driven `_harness_command()`, `DispatchTarget.invocation_surfaces`, projection lookup in `_resolve_dispatch_target()` (present as uncommitted edits at GO time); plus the module-level `sys.path` bootstrap added during this implementation phase.
- `scripts/seed_harness_registry.py` — IP-3: the `_SEED_INVOCATION_SURFACES` map and `invocation_surfaces` seeding in the `insert_harness` call.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — IP-4: the fixture projection, the direct-`DispatchTarget` fix, and three new tests.
- `groundtruth.db` — IP-2: append-only harness A and harness B version-2 rows carrying `invocation_surfaces`.
- `harness-state/harness-registry.json` — IP-2: the regenerated hot-path projection.

## Spec-To-Test Mapping

- REQ-HARNESS-REGISTRY-001 FR8 (invocation-surface dispatch) — `test_harness_command_builds_argv_from_invocation_surfaces` builds the argv from `invocation_surfaces.headless` for the codex, claude, and a non-claude/codex (gemini) harness record; `test_resolve_dispatch_target_attaches_invocation_surfaces_from_projection` exercises the resolve-then-attach projection wiring. Both PASS.
- DELIB-2079 Q9 (no hard-coded per-harness branch) — `test_harness_command_fails_closed_for_missing_or_malformed_surfaces`: NULL / no-`headless` / malformed `invocation_surfaces` returns `None` uniformly, asserted explicitly for the `claude` and `codex` `command_handle`, proving no special-case fallback survives for the existing harnesses. PASS.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the trigger continues to read `bridge/INDEX.md` as canonical and preserves the dispatch-state and actionable-signature contract; covered by the existing signature / suppression / dispatch-state suite still passing (27 of the 30 trigger tests are pre-existing and remain green).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — this report carries the spec-to-test mapping plus the executed commands and observed results below.

## Verification Commands And Observed Results

- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q` — `30 passed` (27 pre-existing trigger tests + 3 new IP-4 tests).
- `python -m pytest platform_tests/scripts/test_seed_harness_registry.py -q` — `6 passed` (IP-3 regression check; no seed-test regression).
- `python -m py_compile scripts/cross_harness_bridge_trigger.py scripts/seed_harness_registry.py` — clean.
- Live registry confirmation: `harness-state/harness-registry.json` carries harness A and harness B at version 2 with `invocation_surfaces.headless.argv` populated.

## Implementation Notes

- IP-2 encoded the EXACT argv the removed `_harness_command()` switch hard-coded — codex `["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]` and claude `["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]`. The `-003` proposal prose mentioned a `--skip-git-repo-check` flag for the codex headless invocation, but the actual removed switch did not contain that flag. IP-2 encoded the actual prior argv to preserve dispatch behavior; adding `--skip-git-repo-check` would be a behavior change outside this thread's GO'd scope and is recorded here as a candidate follow-up, not made in this implementation.
- IP-1's projection lookup uses a function-level `import harness_projection_reader`. A bare hook invocation (`python scripts/cross_harness_bridge_trigger.py`) puts `scripts/` on `sys.path[0]`, but importlib loading (the trigger test suite) and `python -m` do not — so without a fix 21 existing trigger tests failed with `ModuleNotFoundError: harness_projection_reader`. This implementation added a module-level `sys.path` bootstrap inserting the trigger's own directory, so the import resolves under every load context. This was a latent defect in the uncommitted IP-1 edits, surfaced by running the existing suite and fixed within this implementation phase.
- During the IP-4 test-file edits a governance hook surfaced advisories that sibling bridge threads `gtkb-prime-worker-post-stop-dispatch-retry-slice-3` and `gtkb-prime-worker-delivery-regression-slice-4` carry NO-GO status on the same module. Those threads are unimplemented (NO-GO) and concern post-stop dispatch retry and delivery regression — disjoint from WI-3344's data-driven command construction — so there is no code conflict with this implementation.

## Recommended Commit Type

`feat:` — WI-3344 adds a new capability surface (registry-driven cross-harness dispatch) and removes the hard-coded per-harness branch; it is net-new behavior plus its enabling registry data, not a repair of broken behavior.

## Acceptance Criteria

- [x] `_harness_command()` builds the dispatch argv solely from `invocation_surfaces`; the hard-coded `codex`/`claude` switch is removed with no per-harness fallback.
- [x] Missing/malformed/unsupported `invocation_surfaces` fails closed to `None` uniformly, including for Claude and Codex records.
- [x] `invocation_surfaces` is populated for harness A and harness B and reflected in the regenerated projection.
- [x] The headless entry is a structured argv template with `{{PROMPT}}`/`{{PROJECT_ROOT}}` substituted as individual argv elements; no shell command string is built from the dispatch prompt.
- [x] Regression tests cover registry-driven dispatch for a non-claude/codex harness, the uniform fail-closed `None` cases, and the `_resolve_dispatch_target()` projection-attach integration.
- [x] The existing cross-harness-trigger test suite still passes (30/30, no regression).
- [x] This post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run against this report file before the live NEW `bridge/INDEX.md` entry was inserted.

Observed results:
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:eb93c32dff4b5790fe5bb8f4242c3d5b081dfc8c1cb5be9f87bfca68395a3df0`.
- Clause preflight: exit 0; 5 must_apply clauses evaluated; `Blocking gaps (gate-failing): 0`.

## Loyal Opposition Asks

1. Confirm the implementation satisfies REQ-HARNESS-REGISTRY-001 FR8 and DELIB-2079 Q9 with no surviving hard-coded per-harness branch.
2. Confirm the IP-1 `sys.path` bootstrap is an acceptable in-scope fix for the uncommitted-edits import defect, rather than a separate-thread concern.
3. Confirm encoding the exact prior argv (no `--skip-git-repo-check`) is the correct behavior-preserving choice, with the flag addition deferred as a separate change.
