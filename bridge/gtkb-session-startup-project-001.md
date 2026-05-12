NEW

# Implementation Proposal - Session Startup Project

**Document:** `gtkb-session-startup-project`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Active Workspace:** `E:\GT-KB`
**Recommended commit type:** `feat:`

## Claim

The current Prime Builder startup generator already gathers the right raw
signals, but the owner-facing focus menu is still too flat: it renders every
available option with detailed prompt text instead of first explaining the
project state and recommending the most useful next session focus.

This project updates fresh-session startup into an explicit **Session Startup**
briefing. The briefing must show the current GT-KB/application status, then
present three priority-ranked focus choices (`A`, `B`, `C`) selected from live
startup evidence, and a fourth choice (`D`) that exposes the complete
few-word focus list for custom selection.

This proposal requests authorization for implementation only after Loyal
Opposition GO. No source, hook, rule, MemBase, or approval-packet mutation is
authorized by this `NEW` file itself.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`
- `PB-SESSION-WRAP-UP-PROACTIVE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-SCHEMA-001`
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001`
- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `AGENTS.md`
- `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md`
- `config/agent-control/system-interface-map.toml`
- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `bridge/gtkb-claude-session-start-parity-001.md`

## Prior Deliberations And Evidence

- `DELIB-0840` and the verified session-self-initialization records require
  fresh sessions to disclose role/governance, dashboard, project priorities,
  and token-budget context.
- `DELIB-0841` and the lifecycle engagement records require startup/wrap-up
  behavior to simplify owner input through concrete suggested actions and
  priority choices.
- `AGENTS.md` currently requires Prime Builder startup to include
  role/governance stance, dashboard link, current project state, numbered
  session-focus choices, top priority actions, token-reduction options, and
  file bridge scan count.
- `scripts/session_self_initialization.py::_session_focus_options()` currently
  builds a fixed ordered list of thirteen options and
  `_render_session_focus_options()` renders every option with `Current signal`
  and `Prompt details`.
- The owner request on 2026-05-12 states that session startup is the most
  reliable channel for timely GT-KB status, asks for current configuration,
  operating state, bridge state, project/backlog state, and asks for three
  well-explained recommended options plus a fourth complete-list option.

## Owner Decisions / Input

The owner explicitly approved this direction on 2026-05-12:

> "YEs, this is excellent. It is precisely what I was hoping for. Please plan
> and implement this. Please call it the "session startup" project, or
> something like that."

Outstanding owner decisions before GO: none.

## Scope

### IP-1: Name the owner-facing startup surface

Update the Prime Builder report section currently headed
`## Choose This Session's Focus` so the generated owner-facing startup clearly
presents itself as the **Session Startup** surface.

The report must still include all mandatory startup contents already required
by `AGENTS.md` and the session-self-initialization records:

- role/governance stance;
- dashboard link and dashboard coverage;
- current project state;
- active work subject;
- wrap-up trigger commands;
- top priorities;
- token-reduction context;
- generated-time file bridge scan context.

### IP-2: Add compact state briefing bands

Add a compact Session Startup status briefing before focus selection. It must
summarize:

- **Configuration:** work subject, role assignment, harness identity/topology,
  dashboard/harness mode, GT-KB package/scaffold posture.
- **Operating state:** release blockers, testing/tool integration health,
  dev-environment inventory, harness parity, data freshness where available.
- **Work state:** live/generated bridge counts with the live-index caveat,
  Prime-actionable latest `GO`/`NO-GO` bridge response counts, MemBase current
  work/project rollup, standing backlog top priorities, drift count, and recent
  action-center signal.

The briefing must use the startup model already populated by live local probes
and existing dashboard intelligence. It must not replace the rule that live
`bridge/INDEX.md` remains the sole authoritative bridge queue source.

### IP-3: Rank and explain three recommended focus choices

Introduce deterministic focus recommendation logic that scores the existing
focus options from current startup evidence and selects three recommendations.

The ranking inputs must include, at minimum:

- release blocker count and release-readiness evidence;
- failing or unknown testing/tool integrations;
- Prime-actionable bridge responses (`GO` / `NO-GO`) from the live bridge
  metrics;
- bridge advisory/current-action signals where present;
- standing backlog top priorities;
- MemBase project-state rollup;
- development-environment inventory and harness parity health;
- drift changed-path count;
- startup-pruning/token-reduction candidate count.

Each recommendation must render as:

- `A.`, `B.`, or `C.`;
- a few-word option label;
- a concise evidence line explaining why this option was selected now;
- a concise expected-work line that maps to the existing option prompt.

### IP-4: Preserve a complete focus list as option D

Render `D. Full Focus List` as the escape hatch. It must contain every available
focus option as a compact few-word label that the active role can expand using
the existing option prompt details. This preserves discoverability without
spending startup space on full prompt text for every non-recommended option.

The complete list must include the current release, staging, production,
backlog, cleanup, token-reduction, and continuation options unless a future
governed change explicitly removes them.

### IP-5: Update harness-only preservation instructions

Update the programmatic startup payload instructions so Claude Code and Codex
relay the new shape verbatim:

- preserve every generated heading, A/B/C/D option, evidence line, expected
  work line, and compact full-list entry;
- no longer require all thirteen numbered options to appear with full prompt
  details in the user-visible section;
- preserve the first-message init-keyword and focus-mapping rules.

### IP-6: Tests

Update focused startup tests to assert the new shape and the governing
invariants:

1. Prime Builder startup includes a `## Session Startup` section before focus
   selection.
2. Recommendations render exactly three `A`/`B`/`C` choices plus `D. Full Focus
   List`.
3. Recommendation ranking responds to live evidence: release blockers,
   failing integrations, and latest `GO`/`NO-GO` bridge responses change the
   selected ordering.
4. The full list preserves all focus labels, including release, staging,
   production, backlog, cleanup, token-reduction, and continuation choices.
5. The programmatic payload preservation text matches the new A/B/C/D startup
   shape.
6. Loyal Opposition startup still does not render Prime Builder focus choices.

## Files Expected To Change

- `scripts/session_self_initialization.py` - add Session Startup briefing,
  recommendation scoring, A/B/C/D rendering, and updated harness-only
  preservation instructions.
- `platform_tests/scripts/test_session_self_initialization.py` - update and add
  focused startup-rendering/recommendation tests.

No Agent Red live artifact is in scope. No file outside `E:\GT-KB` is in scope.
No MemBase mutation is in scope for this slice.

## Spec-to-Test Mapping

| Spec / requirement | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Proposal and implementation report remain append-only bridge files; startup text preserves live `bridge/INDEX.md` authority caveat. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on this bridge thread passes with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this mapping and executed startup tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | File inventory and tests confirm all changed paths remain under `E:\GT-KB`. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Startup-render tests assert role/dashboard/project-priority/token context remains present. |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Startup payload/report tests assert governance stance and role mapping remain in the generated startup message. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | Existing report tests continue to assert live dashboard link and KPI coverage. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | New/full-list tests assert token-reduction remains a selectable focus and startup-pruning evidence influences ranking. |
| `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` / `PB-SESSION-WRAP-UP-PROACTIVE-001` | Existing wrap-up trigger tests continue to assert startup surfaces wrap-up commands; recommendation tests assert simplified owner choice. |
| Standing-backlog records | Recommendation tests assert standing-backlog top priorities remain selectable and rankable. |
| Init-keyword startup records | Existing payload tests continue to assert first-message gating and no first-message focus mapping. |

## Acceptance Criteria

- [ ] Prime Builder startup renders a named Session Startup briefing.
- [ ] Prime Builder startup recommends exactly three evidence-ranked focus
  choices as `A`, `B`, and `C`.
- [ ] `D. Full Focus List` renders every available focus label in compact form.
- [ ] Recommendation logic uses actual generated startup model evidence rather
  than static fixed ordering alone.
- [ ] Claude/Codex programmatic relay instructions preserve the new shape.
- [ ] Loyal Opposition startup remains free of the Prime Builder focus selector.
- [ ] Focused startup tests pass.
- [ ] Applicability preflight and ADR/DCL clause preflight have been run.
- [ ] Loyal Opposition can VERIFY the post-implementation report.

## Risk + Rollback

| Risk | Mitigation |
| --- | --- |
| Startup hides a lower-ranked but important option | `D. Full Focus List` preserves every option, and the existing prompt payload remains available in the model for role expansion. |
| Ranking becomes a disguised static order | Tests exercise different evidence profiles and assert changed recommendation order. |
| Startup becomes too verbose | Status bands are compact and the full list uses labels only, replacing full prompt dumps for non-recommended options. |
| Bridge actionability confusion returns | Text continues to distinguish live `bridge/INDEX.md` authority, LO-actionable `NEW`/`REVISED`, and Prime-actionable `GO`/`NO-GO`. |
| Claude/Codex startup parity drifts | The shared generator remains the single source for both harnesses; payload preservation instructions are updated with tests. |

Rollback is `git revert <impl-commit-sha>` for implementation. This proposal is
append-only bridge history and should not be rewritten.

## Loyal Opposition Asks

1. Confirm this scope satisfies the owner-approved "session startup project"
   direction without requiring a MemBase mutation in this slice.
2. Confirm the proposed A/B/C/D selector preserves the Prime Builder numbered
   focus-choice requirement by replacing verbose numbering with a clearer
   deterministic focus selector.
3. Confirm the test plan is sufficient to prove recommendations are evidence
   driven and that the full option list remains available.

## Pre-Filing Preflight

Commands to run after this file and the INDEX entry are written:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-startup-project
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-startup-project
```

Initial applicability preflight after filing produced
`packet_hash=sha256:4f59bb36b15fab6d46735fce4031ca48556c5c07f2278230e9dd29a244a72c36`,
`preflight_passed: true`, `missing_required_specs: []`, and advisory omissions
for `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. This filing was updated before
implementation to cite those advisory specs as well.
