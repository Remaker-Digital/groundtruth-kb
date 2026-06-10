REVISED

# Data-Driven Cross-Harness Dispatch From invocation_surfaces (WI-3344)

bridge_kind: prime_proposal
Document: gtkb-harness-data-driven-dispatch
Version: 003 (REVISED; registry-driven harness command construction with no hard-coded per-harness fallback, after NO-GO at -002)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001 (FR8 invocation-surface dispatch); DELIB-2079 Q9
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3344
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "scripts/seed_harness_registry.py", "groundtruth.db", "harness-state/harness-registry.json"]
Recommended commit type: feat:

## Response to NO-GO (-002)

The NO-GO at `bridge/gtkb-harness-data-driven-dispatch-002.md` raised one finding (F1, P1).

**F1 (P1 governance drift) — the fail-safe fallback switch conflicts with FR8 and DELIB-2079 Q9.** The `-001` proposal preserved the hard-coded `if command_handle == "codex" / elif == "claude"` switch in `_harness_command()` as a fail-safe fallback when `invocation_surfaces` is absent. The reviewer correctly observed that REQ-HARNESS-REGISTRY-001 FR8 and DELIB-2079 Q9 require dispatch command construction to be data-driven from `invocation_surfaces` with **no hard-coded per-harness branch remaining**, and that a retained fallback would produce a misleading "FR8 implemented" bridge trail while the rejected routing class still lived in the trigger.

This REVISED proposal addresses F1 as follows:

1. **The fallback switch is removed entirely.** The hard-coded `codex`/`claude` branch is deleted from `_harness_command()`. There is no special-case path for any harness. This change is reflected in the Claim, every Scope IP, Out Of Scope, Files Expected To Change, the Spec-To-Test Mapping, the Acceptance Criteria, and Risk And Rollback — the fallback no longer appears anywhere in this proposal.
2. **`_harness_command()` becomes registry-driven only.** It builds the dispatch argv solely from the selected harness record's `invocation_surfaces`. On missing, malformed, or unsupported `invocation_surfaces`, it fails closed to `None` ("unknown_recipient") for **every** harness — Claude and Codex included. There is no harness for which a hard-coded command survives.
3. **Populating `invocation_surfaces` for the existing Claude and Codex records is now load-bearing and mandatory** (IP-2), not optional dead-code prevention. With the fallback gone, dispatch breaks for Claude and Codex unless their records carry `invocation_surfaces`. IP-2 is therefore a hard precondition of the FR8 change landing, and the implementation sequence runs IP-2 before any code path can dispatch.
4. **No owner waiver is sought.** The NO-GO noted that keeping a transitional fallback would require an explicit owner waiver or a revised requirement. This revision does not keep the fallback, so neither is needed; the work proceeds within the existing owner-decided requirement (REQ-HARNESS-REGISTRY-001 FR8, DELIB-2079 Q9).

The NO-GO's `## Non-Blocking Implementation Guidance` is also adopted: IP-1 now specifies a **structured argv representation** for the headless `invocation_surfaces` entry with an explicit placeholder grammar substituting prompt and project-root as individual argv elements (never a shell command string built from the dispatch prompt); IP-4 adds an **integration regression** proving `_resolve_dispatch_target()` reads `harness-state/harness-registry.json` and attaches the selected record's `invocation_surfaces`; and the WI-3348 Antigravity-registration scope boundary is kept as the reviewer endorsed.

## Claim

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) dispatches a counterpart AI coding harness when actionable bridge work appears. Harness role resolution is already data-driven from the role/identity records, but the *command construction* — how a harness is invoked as a subprocess — is hard-coded to a two-harness Claude/Codex topology in `_harness_command()` (lines 456-479): a literal `if command_handle == "codex" / elif == "claude"` switch. Any third harness returns `None` ("unknown_recipient") and cannot be dispatched.

This proposal makes command construction data-driven and registry-driven only: the trigger reads each harness's `invocation_surfaces` from the DB-backed `harnesses` registry (surfaced through the generated `harness-state/harness-registry.json` projection) and builds the dispatch argv from it. The hard-coded `codex`/`claude` switch is removed entirely — there is no per-harness fallback for any harness. On missing, malformed, or unsupported `invocation_surfaces`, `_harness_command()` fails closed to `None` ("unknown_recipient") uniformly, including for Claude and Codex. Because the switch is removed, populating `invocation_surfaces` for the two existing harness records (Claude, Codex) is a load-bearing precondition of this change — without it, dispatch breaks for the existing harnesses — not an optional step. This is FR8 of REQ-HARNESS-REGISTRY-001 and operationalizes DELIB-2079 Q9 ("the cross-harness trigger dispatches harnesses data-driven from the registry's invocation_surfaces column ... no hard-coded per-harness branch"). It is the prerequisite that makes a third harness (Antigravity / Gemini CLI) dispatchable at all.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement; FR8 governs invocation-surface dispatch (the requirement this implements).
- DELIB-2079 — owner-decided Antigravity Integration design; Q9 decided data-driven dispatch from `invocation_surfaces` with no hard-coded per-harness branch.
- DELIB-2080 — role-portability amendment (FR9); cross-harness dispatch must honor portable harness-assigned roles.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the harness operating-mode architecture the registry and this dispatch change extend.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger is bridge dispatch infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design. Q9 explicitly decided dispatch must be data-driven from `invocation_surfaces`, rejecting "hard-coded per-harness branch" and "interactive-only (no headless dispatch)". This proposal implements that decision; the `-003` revision removes the per-harness fallback the `-001` draft retained, so the implementation contains no branch of the rejected class.
- DELIB-2080 — role-portability amendment for the same Antigravity Integration design; records the Gemini CLI headless invocation form for the Antigravity harness. Confirms `invocation_surfaces` is the intended carrier for harness-specific headless invocation data.
- The cross-harness event-driven trigger replaced the retired smart poller (bridge thread `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations`, VERIFIED). The trigger's actionable-signature scheme and dispatch-state contract are preserved unchanged by this proposal.
- WI-3337 (harnesses table schema, VERIFIED) created the `invocation_surfaces` column; WI-3338 (hot-path projection, VERIFIED) created the `harness-state/harness-registry.json` projection this proposal reads.

## Owner Decisions / Input

The Antigravity Integration project, including data-driven dispatch (DELIB-2079 Q9), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344). This proposal requires no new owner decision before GO; it implements an already-owner-decided requirement through the governed bridge path. The `-002` NO-GO confirmed that removing the hard-coded fallback (the change this REVISED makes) stays inside the existing owner-decided requirement and needs no waiver or new owner input.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 FR8 and DELIB-2079 Q9 fully govern this work and require exactly the registry-driven, no-fallback construction this REVISED proposal specifies. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation. No owner waiver is required, because no hard-coded per-harness fallback is retained.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped code change to `scripts/cross_harness_bridge_trigger.py` plus two append-only `harnesses` registry record inserts and a projection regeneration. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is therefore not applicable to this proposal. The single work item cited (WI-3344) is this proposal's own implementing work item under the mandatory project-linkage metadata, not the target of a bulk mutation.

## Scope

### IP-1: Make _harness_command() registry-driven only (no fallback switch)

In `scripts/cross_harness_bridge_trigger.py`:
- Add an `invocation_surfaces: dict[str, object] | None` field to the `DispatchTarget` dataclass (~line 535).
- In `_resolve_dispatch_target()` (~line 637), after the harness ID is resolved, load `harness-state/harness-registry.json` via `harness_projection_reader.load_harness_projection()`, locate the record by `id == harness_id`, and attach its `invocation_surfaces` to the `DispatchTarget`.
- Rewrite `_harness_command()` (lines 456-479): **remove the `codex`/`claude` switch entirely.** The function builds the dispatch argv solely from `target.invocation_surfaces` by reading the `headless` entry and substituting the dispatch prompt and project-root into its structured argv template (see "Structured argv representation" below). There is no per-harness branch and no special-case command for any harness. When `target.invocation_surfaces` is missing, has no `headless` entry, is malformed, or specifies an unsupported surface shape, `_harness_command()` returns `None` and the trigger logs `unknown_recipient` — this fail-closed behavior applies uniformly to every harness, Claude and Codex included.

Structured argv representation. The `headless` entry of `invocation_surfaces` is a structured object, NOT a shell command string. The dispatch prompt contains arbitrary bridge text and must never be interpolated into a shell-parsed string. The headless entry carries an explicit ordered `argv` list whose elements are either literal strings or placeholder tokens. Exactly two placeholder tokens are defined: `{{PROMPT}}` and `{{PROJECT_ROOT}}`. `_harness_command()` produces the final argv by walking the template list and replacing each occurrence of a placeholder token with the corresponding value as a single, separate argv element (the prompt is one element; the project-root is one element). No shell is invoked; the resulting argv list is passed directly to `subprocess.Popen()` with `shell=False`. Example template shape (illustrative, not a literal record value): `{"headless": {"argv": ["codex", "exec", "--skip-git-repo-check", "--cd", "{{PROJECT_ROOT}}", "{{PROMPT}}"]}}`. An entry whose `argv` is absent, empty, not a list, or contains a non-string non-placeholder element is treated as malformed and causes the fail-closed `None` return.

### IP-2: Populate invocation_surfaces for the two existing harness records (load-bearing, mandatory)

This IP is mandatory and load-bearing, not optional. Because IP-1 removes the hard-coded `codex`/`claude` switch, the cross-harness trigger cannot dispatch Claude or Codex unless their `harnesses` records carry an `invocation_surfaces.headless` argv template. `invocation_surfaces` is currently NULL for every seeded harness row, so without this IP the FR8 change would break dispatch for the two existing harnesses. The implementation sequence therefore runs this IP before the IP-1 code path can be exercised against live records.

Populate `invocation_surfaces` for the two existing harnesses (Claude, Codex) by inserting new append-only `harnesses` versions through the existing `db.insert_harness()` API, each carrying a `headless` argv template in the structured form defined in IP-1 (placeholder tokens `{{PROMPT}}` and `{{PROJECT_ROOT}}` substituted as individual argv elements). Then regenerate the `harness-state/harness-registry.json` projection via `harness_projection.generate_harness_projection()`. The argv templates encode the same headless invocations the removed switch previously hard-coded (Codex: `codex exec` with the skip-git-repo-check and project-root flags; Claude: the headless Claude Code invocation), now expressed as data on the records rather than as code. The Antigravity harness record's `invocation_surfaces` is set when that harness is registered (WI-3348, separate thread).

### IP-3: Seed-path consistency

Update `scripts/seed_harness_registry.py` so the seed populates `invocation_surfaces` with the structured `headless` argv templates for the Claude and Codex records (it currently leaves it NULL), keeping fresh installs consistent with the live registry. A fresh install must produce harness records that the registry-driven `_harness_command()` can dispatch without any code-side fallback.

### IP-4: Regression tests (unit + integration)

Extend `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
- Allow the test fixture to construct a multi-harness projection (Claude, Codex, and a third non-Claude/Codex harness).
- Unit test: assert `_harness_command()` builds a correct argv from a harness record's `invocation_surfaces.headless` template, with the prompt and project-root substituted as individual argv elements, for the Codex record, the Claude record, and a non-Claude/Codex harness record.
- Unit test: assert that a NULL `invocation_surfaces`, a record with no `headless` entry, and a malformed `headless` entry (missing/empty/non-list `argv`, or a non-string non-placeholder element) each cause `_harness_command()` to return `None` — and assert this explicitly for a record whose `command_handle` is `claude` or `codex`, proving there is no surviving special-case fallback for the existing harnesses.
- Integration test: assert that `_resolve_dispatch_target()` reads `harness-state/harness-registry.json` (via the projection reader) and attaches the selected harness record's `invocation_surfaces` onto the returned `DispatchTarget`. This test exercises the real projection-lookup path against a fixture registry file rather than hand-constructing a `DispatchTarget`, so the proof covers the resolve-then-attach wiring, not just `_harness_command()` in isolation.

## Out Of Scope

- Registering the Antigravity harness record and setting its `invocation_surfaces` (WI-3348, separate thread).
- The `run_trigger()` two-recipient loop and `_compute_actionable()` two-tuple — Antigravity takes a *role* (loyal-opposition), not a third dispatch queue; the two-recipient (prime-builder / loyal-opposition) structure is unchanged.
- Migrating the trigger's role/identity readers to the projection (WI-3342 Slice B, separate thread — that thread touches `cross_harness_bridge_trigger.py`'s `_load_role_assignments` / `_load_harness_identities` raw readers at lines ~595-620; this proposal touches only `_harness_command()`, `_resolve_dispatch_target()`, and the `DispatchTarget` dataclass — disjoint functions in the same file).
- Changing the actionable-signature scheme, dispatch-state contract, or active-session suppression.
- Any file outside E:\GT-KB.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — registry-driven `_harness_command()` with the `codex`/`claude` switch removed entirely and uniform fail-closed `None` behavior; `DispatchTarget.invocation_surfaces` field; projection lookup in `_resolve_dispatch_target()`.
- `scripts/seed_harness_registry.py` — seed `invocation_surfaces` with the structured `headless` argv templates for the Claude and Codex records.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — new unit and integration regression coverage.
- `groundtruth.db` — new append-only `harnesses` versions carrying `invocation_surfaces` for the two existing harnesses (Claude, Codex).
- `harness-state/harness-registry.json` — regenerated projection.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 FR8 (invocation-surface dispatch) | Unit test: `_harness_command()` builds argv from `invocation_surfaces.headless` for the Codex, Claude, and a non-Claude/Codex harness record. Integration test: `_resolve_dispatch_target()` reads `harness-state/harness-registry.json` and attaches the selected record's `invocation_surfaces`. |
| DELIB-2079 Q9 (no hard-coded per-harness branch) | Unit test: `_harness_command()` produces a correct command with no per-harness `if/elif`; and a NULL / no-`headless` / malformed `invocation_surfaces` returns `None` even for a `claude` or `codex` `command_handle`, proving no special-case fallback survives for the existing harnesses. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The trigger continues to read `bridge/INDEX.md` as canonical and preserves the dispatch-state contract — covered by the existing suppression/signature test suite still passing. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `_harness_command()` builds the dispatch argv solely from `invocation_surfaces`; the hard-coded `codex`/`claude` switch is removed entirely with no per-harness fallback for any harness.
- [ ] Missing, malformed, or unsupported `invocation_surfaces` causes `_harness_command()` to fail closed to `None` ("unknown_recipient") uniformly, including for Claude and Codex records.
- [ ] `invocation_surfaces` is populated for the two existing harness records (Claude, Codex) with structured `headless` argv templates and reflected in the regenerated projection — and dispatch for Claude and Codex works through the registry-driven path with no code-side fallback.
- [ ] The headless `invocation_surfaces` entry is a structured argv template with `{{PROMPT}}` and `{{PROJECT_ROOT}}` placeholders substituted as individual argv elements; no shell command string is built from the dispatch prompt.
- [ ] Regression tests cover registry-driven dispatch for a non-Claude/Codex harness, the uniform fail-closed `None` cases (including for `claude`/`codex` `command_handle`), and an integration test that `_resolve_dispatch_target()` reads the projection file and attaches `invocation_surfaces`.
- [ ] The existing cross-harness-trigger test suite still passes (no regression to signatures, suppression, or dispatch-state).
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live REVISED INDEX entry is inserted:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch --content-file .gtkb-state/bridge-drafts/gtkb-harness-data-driven-dispatch-003.md`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch --content-file .gtkb-state/bridge-drafts/gtkb-harness-data-driven-dispatch-003.md`

Observed results (run against this draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `content_source: pending_content`, packet_hash `sha256:27f6bf17b7da47c6137bcce6632a5e0bb6003a3ab95786705b599d9f29fbbb36`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0`; 5 must_apply clauses evaluated, evidence found for all 5 (`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`, `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`).

Both preflights are re-run against the indexed operative file after filing.

## Risk And Rollback

**Risk R1 (medium):** A malformed `invocation_surfaces` argv template could build a wrong argv and dispatch incorrectly. Mitigation: the headless entry is a structured argv list (not a shell string), so the dispatch prompt is never shell-parsed; `_harness_command()` fails closed to `None` ("unknown_recipient") on any missing/malformed/unsupported `invocation_surfaces` for every harness; tests assert both the success and the uniform failure paths.

**Risk R2 (medium):** Because the hard-coded fallback is removed, Claude/Codex dispatch depends entirely on IP-2 populating their `invocation_surfaces` records. If IP-2 is skipped or its templates are wrong, dispatch breaks for the existing harnesses. Mitigation: IP-2 is mandatory and runs before the IP-1 code path is exercised against live records; IP-3 keeps fresh installs consistent; the regression suite asserts Claude and Codex dispatch through the registry-driven path; the post-implementation report verifies observed dispatch for both existing harnesses.

**Risk R3 (low):** The regenerated projection could drift from the DB. Mitigation: the projection is produced by the existing `harness_projection.generate_harness_projection()`; no new projection logic is introduced.

**Risk R4 (low):** New append-only `harnesses` versions are created for the two existing harnesses. Mitigation: append-only versioning preserves history; rollback is a further corrective version, not a history rewrite.

Rollback: revert the `cross_harness_bridge_trigger.py`, `seed_harness_registry.py`, and test changes. Because no code-side fallback is retained, a rollback also requires reverting to the prior commit's `_harness_command()` (which still carried the switch) if dispatch must be restored before a corrective fix; the append-only `harnesses` versions added by IP-2 are left in place (history is not rewritten) and are harmless to the reverted code.

## Loyal Opposition Asks

1. Confirm the structured argv representation for `invocation_surfaces.headless` (an ordered `argv` list with `{{PROMPT}}` and `{{PROJECT_ROOT}}` placeholder tokens substituted as individual argv elements, passed to `subprocess.Popen()` with `shell=False`) is the correct encoding.
2. Confirm that splitting the Antigravity harness-record registration and its `invocation_surfaces` value (WI-3348) out of this proposal is the correct scope boundary.
3. Confirm the uniform fail-closed `None` ("unknown_recipient") behavior for missing/malformed/unsupported `invocation_surfaces` — with no special-case path for any harness, Claude and Codex included — is the intended safety posture.
