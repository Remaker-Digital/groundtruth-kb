# Advisory Intake Boundaries - WI-5054

Date: 2026-07-07
Author: Prime Builder / Codex
Mode: implementation scoping report
Bridge thread: `bridge/gtkb-wi5054-advisory-intake-boundaries-001.md`
Implementation authorization: `sha256:e144355b192b3148943b1d14c01cf4c258b8f7d6cf97c5198669d1b79ee7fa6a`
Manual test anchor: `TEST-11292`

## Claim

The advisory proposal intake workflow must reuse existing WI-4840 advisory
disposition and advisory routing behavior instead of rebuilding it. New work is
limited to live advisory intake boundaries: authoring/advisory capture,
Prime-side intake, live filtering and summarization, activity-profile surfacing,
and parity tests. ADVISORY capture is not implementation approval.

## Evidence

- Verified parent thread:
  `bridge/gtkb-advisory-proposal-intake-workflow-005.md` confirms the umbrella
  project created child work items `WI-5054` through `WI-5059` and manual tests
  `TEST-11292` through `TEST-11297`.
- WI-4840 reusable routing surface:
  `.claude/skills/advisory-disposition/SKILL.md:54` defines the advisory
  disposition decision tree. It already routes advisories to no-op, work item,
  specification intake, project authorization, bridge proposal, or deferred
  candidate, and `.claude/skills/advisory-disposition/SKILL.md:77` limits bridge
  proposal routing to concrete work with owner/project authorization, target
  paths, spec links, and verification evidence.
- WI-4840 approval boundary:
  `.claude/skills/advisory-disposition/SKILL.md:38` states only a live bridge
  `GO` plus implementation-start packet authorizes protected edits.
- Source preservation:
  `.claude/skills/advisory-disposition/SKILL.md:114` requires bridge-proposal
  routes to carry forward the source advisory, prior deliberations, target
  paths, linked specs, owner/project authorization, and spec-derived
  verification plan.
- Advisory candidate tooling:
  `scripts/advisory_backlog_router.py:11` and
  `scripts/advisory_backlog_router.py:58` state the router stages candidates and
  no longer auto-promotes advisories to `work_items`. `scripts/advisory_backlog_router.py:428`
  defines `is_live_advisory`, and `scripts/advisory_backlog_router.py:432`
  excludes promoted/rejected advisories; the helper also excludes sources already
  backed by a work item.
- Live intake scanner:
  `scripts/advisory_intake_scanner.py:4` selects only live ADVISORY entries with
  `adopt`/`adapt` classification plus a Required Prime Builder Owner-Grilling
  Gate section. `scripts/advisory_intake_scanner.py:88` rejects other
  classifications and `scripts/advisory_intake_scanner.py:92` rejects missing
  gates.
- Owner-grilling gate:
  `.claude/rules/peer-solution-advisory-loop.md:64` defines the gate authority;
  `.claude/rules/peer-solution-advisory-loop.md:67` requires the gate for
  `adopt`/`adapt`, and `.claude/rules/peer-solution-advisory-loop.md:79`
  requires Prime Builder to conduct structured owner clarification before
  derived implementation proposals exist.
- Lint boundary:
  `scripts/advisory_grilling_gate_lint.py:14` says the current lint is
  warning-only and fail-open; `scripts/advisory_grilling_gate_lint.py:27`
  defines the gate-presence check. Intake may use the gate predicate, but this
  slice does not convert the lint itself into a blocking hook.
- ADVISORY dispatch behavior:
  `.claude/rules/file-bridge-protocol.md:279` defines ADVISORY as Loyal
  Opposition-authored, Prime-actionable in interactive sessions, and
  non-dispatchable for headless runs. `.claude/rules/file-bridge-protocol.md:328`
  repeats that headless dispatch filters ADVISORY out before spawning workers.
  `.claude/rules/file-bridge-protocol.md:330` defines Prime responses as a
  normal NEW proposal for `adopt`/`adapt`, an explicit deferral, or a documented
  rejection.
- Peer-solution loop boundary:
  `.claude/rules/peer-solution-advisory-loop.md:15` defines the five
  classifications. `.claude/rules/peer-solution-advisory-loop.md:127` states
  peer advisories enter bridge as ADVISORY and are non-dispatchable for headless
  runs. `.claude/rules/peer-solution-advisory-loop.md:136` keeps artifact
  approval packets separate from peer-solution adoption decisions.

## Reusable Dependencies

- Use `advisory-disposition` as the Prime routing decision tree. Do not create a
  second advisory disposition taxonomy.
- Use `advisory_backlog_router` as the advisory candidate staging source when a
  backlog-candidate surface is needed. It stages and preserves provenance; it
  does not create implementation approval.
- Use `advisory_intake_scanner` as the intake-ready filter: live source, latest
  ADVISORY status for bridge threads, `adopt`/`adapt`, and required owner
  grilling gate.
- Use the peer-solution advisory loop vocabulary for owner-facing disposition:
  `adopt`, `adapt`, `reject`, `defer`, and `monitor`.
- Use numbered bridge files and dispatcher/TAFE-derived state as the live bridge
  authority. Do not read or recreate `bridge/INDEX.md`; it is obsolete.

## New Work Boundaries

- `WI-5055` adds the `advisory-proposal` managed skill for Loyal
  Opposition/advisory-side draft-first ADVISORY capture. It must preserve source
  advisory, prior deliberations, final owner confirmation where required, and
  non-approval language.
- `WI-5056` adds the Prime Builder `advisory-intake` managed skill. It consumes
  live advisories, summarizes sources, asks owner-grilling questions, confirms
  explicit owner/project/work-item approval, and prepares child proposals only
  after the required gates exist.
- `WI-5057` adds deterministic helper behavior around live advisory filtering.
  It should use the staged/promoted/rejected/work-item-backed predicate instead
  of raw file existence alone.
- `WI-5058` surfaces the skills in activity profiles only: advisory authoring in
  `deliberation`, Prime intake in `build`, and neither in unrelated profiles.
- `WI-5059` proves the above with tests covering advisory filtering,
  owner-grilling behavior, skill registration, adapter generation, profile
  surfacing, and catalog parity.

## Exclusions

- No ADVISORY entry becomes headless-dispatchable implementation work.
- No ADVISORY entry creates protected edits without a separate child bridge
  proposal, Loyal Opposition `GO`, and implementation-start packet.
- No advisory candidate is auto-promoted to a work item; owner-batch promotion
  remains the governed path.
- No peer-solution `adopt`/`adapt` decision substitutes for formal artifact
  approval when protected formal artifacts or rule files are edited.
- No child proposal should duplicate WI-4840 advisory-disposition behavior.
  New child work should call or cite the existing routing decision tree rather
  than redefining it.

## Sequencing

1. Loyal Opposition or advisory mode captures a candidate as an ADVISORY using
   `advisory-proposal`, including source advisory, classification, prior
   deliberations, and owner-grilling gate when `adopt`/`adapt`.
2. Prime Builder processes live ADVISORY items interactively using
   `advisory-intake` and scanner/router evidence.
3. Prime Builder asks one owner-grilling question at a time when required and
   preserves the answer as governed decision evidence.
4. Prime Builder chooses the existing WI-4840 disposition route: no-op, backlog
   candidate, specification intake, project authorization, bridge proposal, or
   deferral.
5. Only a bridge-proposal route proceeds to implementation, and only after
   target paths, spec links, verification plan, Loyal Opposition `GO`, and
   implementation-start authorization exist.

## Risk / Impact

- Risk: agents may treat "advisory accepted" as "implementation approved."
  Impact: protected edits could bypass owner/project/bridge gates. Mitigation:
  keep the non-approval boundary in both skills and implementation reports.
- Risk: duplicate routing logic could drift from WI-4840. Impact: inconsistent
  advisory dispositions. Mitigation: cite and reuse `advisory-disposition`.
- Risk: raw ADVISORY counts could be mistaken for NO-GO or dispatch queues.
  Impact: headless dispatcher confusion. Mitigation: preserve ADVISORY as
  interactive-only and non-dispatchable.
- Risk: stale `bridge/INDEX.md` references could reintroduce obsolete bridge
  authority. Impact: queue state could be read from retired artifacts.
  Mitigation: use numbered bridge file chains and dispatcher/TAFE state only.

## Recommended Action

- Treat `WI-5055` through `WI-5059` as thin child slices around the boundary
  above, not as a second advisory governance subsystem.
- Keep tests close to the boundary predicates: live status, `adopt`/`adapt`,
  owner-grilling gate, no auto-promotion, profile surfacing, and generated skill
  parity.
- Continue purging `bridge/INDEX.md` references whenever they appear in
  authorized target paths.

## Decision Needed From Owner

None for WI-5054. Owner authorization is already captured by `DELIB-202665870`
and project authorization
`PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5054-INVESTIGATION-20260707`.

## TEST-11292 Mapping

- Cites WI-4840 advisory routing: satisfied by the reusable dependency section
  and `.claude/skills/advisory-disposition/SKILL.md` evidence.
- Cites owner-grilling gate: satisfied by peer-solution loop and lint evidence.
- Cites live ADVISORY routing: satisfied by file-bridge protocol and scanner
  evidence.
- Cites advisory-candidate tooling: satisfied by router staging/live predicate
  evidence.
- Cites peer-solution loop boundaries: satisfied by classification, bridge
  integration, and approval-gate evidence.
- Separates reusable dependencies from new implementation work: satisfied by the
  "Reusable Dependencies", "New Work Boundaries", and "Exclusions" sections.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
