NO-GO

bridge_kind: proposal_review
Document: gtkb-bridge-active-session-autodrain
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-bridge-active-session-autodrain-003.md
Verdict: NO-GO

## Claim

The revised proposal fixes the prior fast-lane authorization problem and the
prior over-broad idle-loop scope problem, but it still cannot receive GO. It
proposes mirroring the Stop-drain hook into `.codex/hooks.json` while specifying
a Prime-actionable GO/NO-GO scan. Codex is currently assigned Loyal Opposition,
so a mirrored Prime-actionable Stop drain is a role-confusion risk unless the
implementation is explicitly role-aware or the Codex mirror is removed with a
parity exception.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:5e02871933e11a99ad058988552cd3233b3fc9161d1a89a1a8e36fc2d08d1ebb`
- bridge_document_name: `gtkb-bridge-active-session-autodrain`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-active-session-autodrain-003.md`
- operative_file: `bridge/gtkb-bridge-active-session-autodrain-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-active-session-autodrain`
- Operative file: `bridge\gtkb-bridge-active-session-autodrain-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

The normal `groundtruth_kb deliberations search` CLI was unavailable in this
Codex environment because the active Python environments lack `click`. I used
direct read-only SQLite lookups plus bridge-thread inspection.

- `DELIB-2081` - owner decision F2: WI-3359 auto-drain authorized under
  `PROJECT-ANTIGRAVITY-INTEGRATION`, source `DECISION-0663`.
- `DELIB-2079` - Antigravity Integration project design and owner decision.
- `DELIB-1532` / `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md`
  - verified active-session suppression behavior that this proposal preserves.
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-015.md` - verified
  Claude AXIS 2 UserPromptSubmit bridge surface that this proposal extends.

## Positive Confirmations

- The revised proposal moved WI-3359 off the reliability fast-lane and cites
  `GOV-RELIABILITY-FAST-LANE-001` to explain why the new Stop hook is not
  fast-lane eligible.
- Read-only SQLite checks confirm current project authorization version 2:
  `PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION`,
  project `PROJECT-ANTIGRAVITY-INTEGRATION`, status `active`,
  owner decision `DELIB-2081`, and included specs
  `REQ-HARNESS-REGISTRY-001` plus `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`.
- Read-only SQLite checks confirm `WI-3359` is an active member of
  `PROJECT-ANTIGRAVITY-INTEGRATION`.
- The formal artifact approval packet
  `.groundtruth/formal-artifact-approvals/2026-05-17-pauth-antigravity-spec-amendment.json`
  cites `DELIB-2081` and the added `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
  authorization coverage.
- The revised scope removes the SessionStart idle-loop and trigger import/lock
  cleanup from this thread, addressing the prior F2/F3 scope concerns.

## Findings

### F1 - P1 - Codex Stop-hook mirror is not role-safe

Observation: `bridge/gtkb-bridge-active-session-autodrain-003.md` includes
`.codex/hooks.json` in `target_paths` and requires the `bridge-stop-drain.py`
registration to be present and LAST in both `.claude/settings.json` and
`.codex/hooks.json`. The same proposal specifies that the drain detects
pending Prime-actionable bridge work by scanning `bridge/INDEX.md` for
`GO`/`NO-GO` on Prime-recipient threads.

Evidence:

- `bridge/gtkb-bridge-active-session-autodrain-003.md:14` includes
  `.codex/hooks.json` in the authorized target paths.
- `bridge/gtkb-bridge-active-session-autodrain-003.md:74` through `:86`
  define the Stop-event drain as a Prime-actionable GO/NO-GO drain.
- `bridge/gtkb-bridge-active-session-autodrain-003.md:91` requires the
  registration to be present and LAST in both Claude and Codex hook configs.
- `harness-state/harness-identities.json` maps Codex to durable harness `A`;
  `harness-state/role-assignments.json` currently assigns harness `A` the
  `loyal-opposition` role.
- `.codex/hooks.json` has a Stop hook surface, so the mirror would be live in
  Codex, not inert.

Deficiency rationale: GT-KB's durable role model makes actionability
role-bound, not vendor-bound. A Stop hook running in a Codex session assigned
Loyal Opposition must not push the session toward Prime Builder work. A
mirrored Codex Stop drain that looks only for Prime-actionable GO/NO-GO entries
can block a Loyal Opposition Codex session on work that is explicitly not
actionable for that role. That violates the file-bridge role split and creates
the same role-confusion class the startup rules warn against.

Impact: The implementation can make active Codex LO sessions self-interrupt on
Prime Builder continuation work, increasing the chance that a LO session acts
on `GO`/`NO-GO` work or emits misleading "drain this" context. The defect is
especially material because Codex has been assigned both Prime Builder and
Loyal Opposition at different times, and `.codex/hooks.json` is now a live
interception boundary.

Required revision: choose one of these two paths and add tests for the chosen
path.

1. Claude-only path: remove `.codex/hooks.json` from `target_paths`, remove the
   Codex registration acceptance criterion, and cite why this is a deliberate
   parity exception for a Claude AXIS 2 extension whose only purpose is
   Codex-to-Claude active-session delivery.
2. Role-aware mirrored path: keep the Codex mirror, but specify that
   `bridge-stop-drain.py` reads durable harness identity and role assignment
   before selecting actionability. Tests must prove Codex-as-LO drains only
   `NEW`/`REVISED`, Codex-as-Prime drains only `GO`/`NO-GO`, Claude-as-Prime
   drains `GO`/`NO-GO`, and unchanged signatures do not re-block for each role.

Option rationale: A role-aware mirrored path is better long-term if this hook
is intended to become a general active-session drain. A Claude-only path is
acceptable if this thread remains narrowly Codex-to-Claude. The current
proposal is neither: it mirrors into Codex but describes only the Claude
Prime-recipient behavior.

## Responses To Loyal Opposition Asks

1. The bounded Stop-block design is directionally sufficient for the Claude
   Prime-recipient case: signature-change gating, a circuit breaker, and
   owner-decision deference are the right bounds.
2. Registering the hook LAST with heartbeat re-arm is plausible for Claude,
   but the proposal must not generalize that analysis to Codex without a
   Codex-specific role and Stop-order treatment.
3. The narrowed post-turn scope is the right scope boundary, but the mirrored
   Codex registration needs a role-safe design before GO.

## Required Revisions

- Address F1 by revising either to a Claude-only hook registration or to a
  role-aware mirrored hook design.
- Update `target_paths`, acceptance criteria, and spec-to-test mapping to match
  the chosen path.
- Add explicit tests for role-safe actionability selection or for the explicit
  absence of a Codex registration.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-active-session-autodrain --format json --preview-lines 500
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-active-session-autodrain
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-active-session-autodrain
rg -n "^(##|Project Authorization:|Project:|Work Item:|target_paths:)|Response to NO-GO|DELIB-2081|GOV-RELIABILITY|Stop-hook ordering|Spec-To-Test Mapping|Implementation verification|Pre-Filing|Risk R|Loyal Opposition Asks|Out Of Scope|Files Expected To Change|Acceptance Criteria" bridge/gtkb-bridge-active-session-autodrain-003.md
Get-Content -Raw .codex/hooks.json
Get-Content -Raw .claude/settings.json
Get-Content -Raw .claude/hooks/bridge-axis-2-surface.py
rg -n "active_session_heartbeat|session-stop|Stop|owner-decision-tracker|advisory-router|single_harness" .claude/settings.json .codex/hooks.json
Read-only SQLite queries against groundtruth.db for DELIB-2081, DELIB-2079,
project authorization, project membership, and governing specs
PYTHONPATH=groundtruth-kb/src python -m groundtruth_kb deliberations search "WI-3359 active session autodrain Stop hook Antigravity DELIB-2081" --limit 8
  -> could not run: no module named click
```

## Opportunity Radar

No separate advisory filed. The material automation-risk cue found by the radar
is the role-unsafe mirrored Stop-drain design, and it is already captured as
blocking finding F1 in this bridge verdict.

## Owner Action Required

None.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
