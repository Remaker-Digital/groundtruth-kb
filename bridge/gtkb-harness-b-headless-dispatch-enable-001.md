NEW

bridge_kind: prime_proposal
Document: gtkb-harness-b-headless-dispatch-enable
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC
Implements: WI-4661
Project Authorization: PAUTH-WI-4661-HARNESS-B-HEADLESS-DISPATCH-ENABLE
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4661
target_paths: ["config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_config.py"]
Recommended commit type: feat:
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 806e5944-602e-41ac-b030-cdd18fd50242
author_model: claude-opus-4-7
author_model_version: Claude Opus 4.7
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style; 1M context

# Enable Headless Dispatch of Prime-Builder Work to Harness B (Claude Code)

## Claim

Per owner directive 2026-06-18 (`DELIB-20265223`), enable headless bridge dispatch of Prime-Builder-actionable work to harness B (Claude Code). The change is a single-file, two-line edit to `config/dispatcher/rules.toml` plus one focused regression test.

This proposal supersedes the premise of the in-flight `bridge/gtkb-harness-b-interactive-status-orthogonality-001.md` (Codex-authored, WI-4645, NEW), which is built on the opposite premise — that B's interactive-only state is the *intentional steady state*. The orthogonality proposal's "Loyal Opposition Ask #1" explicitly invited this alternative: *"If Loyal Opposition prefers changing harness B's live status instead of adding a doctor visibility check, that would be a different registry mutation and should be sent back as a NO-GO or a separate owner decision."* `DELIB-20265223` is that separate owner decision.

## Specification Links

- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — establishes the three-axis orthogonality model (role, status, dispatchability) and confirms each axis can be mutated independently. This change exercises the dispatchability axis only.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — Prime Builder and Loyal Opposition are portable harness-assigned roles; enabling B's headless dispatch reinforces (does not violate) this portability by making B's PB authority addressable via headless dispatch.
- `REQ-HARNESS-REGISTRY-001` — the harness registry projection consumes the dispatcher config overlay (`apply_dispatch_config_to_record` per `harness_projection.py:208-211`); editing `config/dispatcher/rules.toml` is the canonical surface for `can_receive_dispatch` mutation per this requirement.
- `GOV-SESSION-ROLE-AUTHORITY-001` — interactive-session role authority and headless dispatch authority remain separate. This change enables the headless axis for B; it does not modify session-stated role override behavior.
- `DCL-SESSION-ROLE-RESOLUTION-001` — session role resolution is unchanged; this proposal touches dispatchability config only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal and its post-implementation report are filed and tracked through the governed bridge protocol path with append-only versioning.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives its test from the linked specifications and will be executed against the implementation before VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths (`config/dispatcher/rules.toml` and `platform_tests/scripts/test_bridge_dispatch_config.py`) are inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner decision (`DELIB-20265223`), work item (`WI-4661`), authorization (`PAUTH-WI-4661-HARNESS-B-HEADLESS-DISPATCH-ENABLE`), bridge proposal, implementation report, and test are preserved as durable, linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — premise shift on the orthogonality proposal is preserved as a governed artifact relationship rather than transient chat interpretation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4661 remains open through the bridge lifecycle (NEW → GO → implement → report → VERIFIED) and is resolved only after VERIFIED.
- `GOV-STANDING-BACKLOG-001` (may-apply) — this change does not perform a bulk operation on backlog items; it modifies a single configuration file under one bounded PAUTH, so the bulk-ops visibility clause does not apply here.

## Authorization

This proposal uses active project authorization `PAUTH-WI-4661-HARNESS-B-HEADLESS-DISPATCH-ENABLE` (anchoring `DELIB-20265223`). Allowed mutation classes: `configuration_change`, `test_addition`. Forbidden operations: `harness_registry_mutation`, `invocation_surfaces_mutation`, `narrative_artifact_mutation`, `formal_artifact_mutation`, `deployment`. Included work item: `WI-4661`. Included specs: `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`.

No formal-artifact mutation, harness-registry mutation, MemBase harness-row mutation, narrative-artifact mutation, production deployment, or credential action is requested. Target paths are a single configuration file and a single test file only.

## Prior Deliberations

- `DELIB-20265223` (this session, 2026-06-18) — the anchoring owner decision. Owner verbatim: *"Yes. I would like headless dispatch of PB-actionable work to Claude Code and Codex."* Source-type `owner_conversation`; outcome `owner_decision`; participants `owner, prime-builder/claude-B`.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner decision establishing role/status/dispatchability orthogonality. This change operationalizes the dispatchability axis without touching role or status.
- `DELIB-20263438` — owner requirement: corrected bridge-dispatch architecture; role↔dispatchability orthogonal; rule-based dispatch over roles/subjects/`::open-activities`; availability/cost/quality selection. Confirms that flipping `can_receive_dispatch` does not auto-promote B in target selection (selection_order still favors A on cost).
- `DELIB-20260665` — premise-shift surfacing 2026-06-04 ("B is active PB again; June 1 'Claude-offline' premise no longer holds"). Earlier informational surfacing on the substrate axis; today's change is the symmetric premise shift on the dispatchability axis.
- `DELIB-20263296` — GO for role-eligibility guard work; distinguishes interactive session-role evidence from headless dispatch role checks. Confirms the two-axis split this proposal exercises.
- `DELIB-20261713` — GO for FAB-01 dispatch substrate revival; approves the launchability and capability-axis split.
- `DELIB-20261029` — Loyal Opposition Advisory Report: Harness Capability and Role Suitability (Antigravity & Claude Code), 2026-05-27. Provides the historical capability-suitability framing this change updates.

## Owner Decisions / Input

- `DELIB-20265223` (owner decision, 2026-06-18, S447 session) authorizes this implementation. Owner verbatim text recorded as AUQ-equivalent evidence (`auq_id: S447-OWNER-DIRECTIVE-2026-06-18-HARNESS-B-HEADLESS-DISPATCH`; `auq_answer: "Yes. I would like headless dispatch of PB-actionable work to Claude Code and Codex."`).
- No additional owner decision required before Loyal Opposition review. If Loyal Opposition prefers also re-ranking the dispatcher selection rules to prefer B (e.g., adjusting `dispatch_cost`) or to update `selection_order`, that would be a separate owner-decision scope and should be NO-GO'd back rather than bundled here.
- `bridge/gtkb-harness-b-interactive-status-orthogonality-001.md` (Codex/A NEW) becomes stale under this owner decision. Loyal Opposition review of that thread should NO-GO citing `DELIB-20265223`, and Prime Builder (Codex/A) should either WITHDRAW or pivot it to a smaller doctor-visibility patch consistent with the new steady state (e.g., "active PB headless-dispatchable" rather than "suspended interactive-only").

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SINGLE-HARNESS-OPERATING-MODE-001` and the canonical-terminology entries for role-assignment, role-set, and single-harness operating mode already establish dispatchability as an orthogonal axis the owner may modify by configuration. No new specification is required; the change is a parameter flip within the existing schema.

## Scope

### IP-1: Flip `[harnesses.B]` dispatchability and tags

Edit `config/dispatcher/rules.toml` `[harnesses.B]` block as follows:

- `can_receive_dispatch = false` → `can_receive_dispatch = true`
- `tags = ["prime-builder", "interactive-only", "event-source"]` → `tags = ["prime-builder", "event-source"]`
- `description = "Claude Code: Prime Builder for interactive work; not a dispatched PB target."` → `description = "Claude Code: active Prime Builder; headless-dispatchable PB fallback (A wins on cost by default)."`

All other `[harnesses.B]` fields (`can_fire_events=true`, `dispatch_cost=70`, `dispatch_quality=95`, `dispatch_availability=75`) are unchanged. The existing `selection_order = ["availability", "cost", "quality", "reviewer_precedence", "harness_id"]` (line 9) is also unchanged, so A (cost 35) continues to win the cost step over B (cost 70) for most PB dispatches; B becomes the fallback target.

### IP-2: Add focused regression test

Add a test to `platform_tests/scripts/test_bridge_dispatch_config.py` that:

- loads the live `config/dispatcher/rules.toml` and asserts `[harnesses.B] can_receive_dispatch == True`;
- asserts `"interactive-only" not in [harnesses.B].tags`;
- asserts the registry projection (`harness-state/harness-registry.json` via `groundtruth_kb.harness_projection.read_roles`) reports harness B's `can_receive_dispatch` as `True` after the change;
- asserts `gt bridge dispatch status` machine-readable output lists B in the dispatchable prime-builder candidate pool.

The test must not depend on network, MemBase row state, or any harness-state mutation; it reads the toml + the projection only.

## Out Of Scope

- No change to `harness-state/harness-registry.json` (auto-regenerated by projection on next read).
- No MemBase harnesses-table row mutation (the projection-overlay path makes `config/dispatcher/rules.toml` the canonical source of truth for `can_receive_dispatch`).
- No change to `selection_order`, `dispatch_cost`, `dispatch_quality`, `dispatch_availability`, or `dispatch_max_items` for any harness.
- No change to harness B's `invocation_surfaces` (the existing `claude -p` argv is preserved; this proposal does not authorize argv revision).
- No change to `selection_order` rules in `[[rules]]` blocks; bridge-prime-builder-default and bridge-loyal-opposition-cheap-fast-default selection logic is unchanged.
- No narrative artifact (`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`) mutation.
- No production deployment or external credential action.

## Pre-Filing Checks

Draft checks to run before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-b-headless-dispatch-enable --content-file .gtkb-state/bridge-propose-drafts/gtkb-harness-b-headless-dispatch-enable-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-b-headless-dispatch-enable --content-file .gtkb-state/bridge-propose-drafts/gtkb-harness-b-headless-dispatch-enable-001.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-harness-b-headless-dispatch-enable-001.md --json --strict
```

Observed draft results will be recorded inline after the pre-filing checks run; if any preflight fails, the proposal will be revised before Write.

## Specification-To-Test Mapping

| Specification | Verification |
| --- | --- |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | New test asserts dispatchability axis can be flipped in `config/dispatcher/rules.toml` independent of role and status; existing role/status orthogonality tests under `test_role_set_topology_*` continue to pass unchanged. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | New test asserts harness B's role remains `["prime-builder"]` and `status="active"` after the dispatchability flip (no role or lifecycle mutation). |
| `REQ-HARNESS-REGISTRY-001` | New test asserts the projection at `harness-state/harness-registry.json` (via `harness_projection.read_roles`) reports `can_receive_dispatch=true` for B after the toml change. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | No change to session-role resolution code paths; existing `test_session_role_resolution_*` continues to cover that surface. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Same as above; no resolution-rule change. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread remains append-only; post-implementation report includes command evidence, target-path diff, and test execution evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passes with `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this mapping and exact command results for the new test. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths are within `E:\GT-KB`; clause preflight confirms. |

Implementation verification will run:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check config/dispatcher/rules.toml platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check platform_tests/scripts/test_bridge_dispatch_config.py
python -m groundtruth_kb bridge dispatch status
python -m groundtruth_kb bridge dispatch health
python -m groundtruth_kb harness roles
```

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `config/dispatcher/rules.toml [harnesses.B] can_receive_dispatch` is `true` after implementation.
- [ ] `[harnesses.B].tags` is `["prime-builder", "event-source"]` (no `"interactive-only"`).
- [ ] `gt bridge dispatch status` lists harness B among dispatchable prime-builder candidates.
- [ ] `gt bridge dispatch health` continues to report PASS (both PB and LO partitions remain populated).
- [ ] New focused test passes with `pytest -q`.
- [ ] `ruff check` and `ruff format --check` pass on the new test.
- [ ] No registry row mutation, no MemBase harnesses-table mutation, no narrative-artifact mutation occurred.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before WI-4661 is marked resolved.

## Risk And Rollback

**Risk** (low):
- The cross-harness event-driven trigger will begin including B as a candidate for headless PB dispatch. Per `selection_order` (`availability → cost → quality → reviewer_precedence → harness_id`), A (availability 90, cost 35) still wins against B (availability 75, cost 70) for most decisions, so B becomes a fallback rather than a primary target. Operational risk is bounded to "claude -p headless workers occasionally spawn when A is unavailable or selection is tied past cost."
- Historical evidence (`DELIB-20261029`, 2026-05-27 LO advisory) noted Claude Code's headless `claude -p` invocation had reliability concerns. This change accepts that operational profile per owner directive; the post-impl phase should monitor `.gtkb-state/bridge-poller/dispatch-failures.jsonl` for any `claude_headless_failure` patterns and surface them via a follow-on hygiene WI if they appear materially.

**Rollback**: a single-line revert of the two `[harnesses.B]` edits in `config/dispatcher/rules.toml` restores the prior state; no registry, MemBase, bridge history, or deployment state needs to be touched. The new test would be retained as documentation of the prior post-revert state or revised to assert the reverted shape.

## Loyal Opposition Asks

1. Confirm that owner directive `DELIB-20265223` is sufficient `Owner Decisions / Input` evidence for the dispatchability flip; or surface a specific cross-cutting spec the proposal should also cite.
2. Confirm that the toml edit (`config/dispatcher/rules.toml` `[harnesses.B]` block) is the correct single source of truth for `can_receive_dispatch` and that no MemBase harnesses-table mutation is needed.
3. Confirm that the orthogonality proposal `bridge/gtkb-harness-b-interactive-status-orthogonality-001.md` should be NO-GO'd by Codex's LO review citing `DELIB-20265223`, and that WI-4645's resolution path becomes one of (a) WITHDRAW, (b) revise to a smaller doctor-visibility patch for the new steady state, or (c) close as superseded by this WI-4661 + DELIB-20265223.
4. Confirm that `selection_order` and per-harness `dispatch_cost`/`dispatch_quality`/`dispatch_availability` should NOT be changed in this proposal; B's role as a cost-disfavored fallback is the expected steady state until owner directs otherwise.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
