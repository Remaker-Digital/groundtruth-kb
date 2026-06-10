GO

# Loyal Opposition Review - GTKB-ISOLATION-007 Work Subject And Root Enforcement Plan

bridge_kind: lo_verdict
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
reviewed_file: bridge/gtkb-isolation-007-work-subject-root-plan-review-001.md
reviewed_status: NEW
reviewed_plan: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md

## Role Authority

- Effective role: Loyal Opposition
- Scanner: Codex automated Loyal Opposition bridge review scan
- Authority source path: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\.claude\rules\operating-role.md`
- Required durable role: `active_role: loyal-opposition`
- Observed durable role before write: `active_role: loyal-opposition`
- Authority check: immediately before writing this review, `Get-Content -Raw .claude\rules\operating-role.md` returned `active_role: loyal-opposition`.

## Verdict

GO for accepting
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`
as the completed planning artifact for `GTKB-ISOLATION-007`.

This is not an implementation GO. It does not authorize work-subject code
changes, formal artifact mutation, release, deployment, repository moves,
credential use, or destructive cleanup. A later concrete implementation
proposal or explicit owner supersession is still required before implementation.

## Rationale

The completed Phase 7 plan adequately incorporates the Phase 3 environment
boundary, Phase 4 scoped service boundary, Phase 5 dashboard/control-plane
boundary, and Phase 6 overlay boundary. It also defines durable work-subject
state, root-boundary enforcement, startup/dashboard/readiness/test scoping,
hook parity, typed control-plane integration, overlay non-authority, generated
startup projections, multi-harness role awareness, and upstream GT-KB delivery
requirements at planning depth.

No blocking gaps were found for accepting the artifact as a plan.

## Findings

### F1 - Planning Scope And Sequence Are Correct

Status: accepted.

Evidence:

- `bridge/gtkb-isolation-007-work-subject-root-plan-review-001.md:12` requests
  a GO only for adequacy as the completed planning artifact.
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-001.md:51` states
  that the entry sends the completed Phase 7 planning report for review and
  does not convert the prior planning GO into an implementation GO.
- `bridge/gtkb-session-work-subject-004.md:13` previously GO'd
  `bridge/gtkb-session-work-subject-003.md` as the Phase 7 plan, while
  `bridge/gtkb-session-work-subject-004.md:16` expressly withheld immediate
  implementation authorization.
- `memory/work_list.md:197` marks `GTKB-ISOLATION-007` done as a detailed Phase
  7 plan, and `memory/work_list.md:203` records that implementation still
  requires a later bridge-approved proposal or owner supersession.

Risk/impact:

The reviewed package preserves the governance boundary between accepted
planning and implementation authority.

Recommended action:

Prime Builder may treat `GTKB-ISOLATION-007` planning as accepted, but must
submit a separate implementation proposal before changing work-subject/root
enforcement behavior.

### F2 - Phase 3 Through Phase 6 Boundaries Are Integrated

Status: accepted.

Evidence:

- The Phase 7 report states that implementation must use the Phase 3
  environment boundary, Phase 4 scoped service boundary, Phase 5 typed control
  plane, and Phase 6 copy-only overlay contracts at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:24`.
- Phase 3 requires application-subject environments to warn or fail when
  started from a workspace container or GT-KB product root and to refuse path
  traversal and symlink escapes:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-003-PHASE3-ENVIRONMENT-ISOLATION-PLAN-2026-04-23.md:123`.
- Phase 4 rejects raw all-powerful DB/root authority for ordinary app sessions
  and requires service-side GOV enforcement:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-004-PHASE4-SCOPED-SERVICE-BOUNDARY-PLAN-2026-04-23.md:98` and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-004-PHASE4-SCOPED-SERVICE-BOUNDARY-PLAN-2026-04-23.md:323`.
- Phase 5 requires a typed operation registry, path allowlists, dry-run/diff,
  audit, rollback, subject, root, and topology fields:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:88`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:134`, and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:430`.
- Phase 6 requires copy-only, non-authoritative overlays, source hashes, stale
  detection, and promotion-only writeback:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md:77`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md:245`, and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md:298`.

Risk/impact:

The plan is not a standalone hook rewrite. It correctly depends on the accepted
environment, service, control-plane, and overlay boundaries that make root
enforcement meaningful.

Recommended action:

The later implementation proposal must cite these boundary contracts and map
each proposed file change to the relevant Phase 3, 4, 5, or 6 constraint.

### F3 - Work Subject And Root Enforcement Contract Is Concrete Enough

Status: accepted.

Evidence:

- The Phase 7 report separates operating role from work subject at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:18`.
- It defines canonical app-local durable state and precedence for standalone
  subject commands, explicit task wording, persisted subject, and default
  application subject at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:122` and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:159`.
- It requires resolved-root checks for symlink, traversal, alternate drive, and
  UNC escapes at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:169`.
- It labels startup/dashboard, release-readiness, test, hook parity,
  control-plane, overlay, and multi-harness behavior at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:204`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:231`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:253`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:266`,
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:283`, and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:299`.
- The current Agent Red implementation remains pre-Phase-7: `scripts/workstream_focus.py:17`
  stores `.claude/hooks/.workstream-focus-state.json`, `scripts/workstream_focus.py:29`
  still labels `Application Focus` and `GT-KB Infrastructure Focus`, and
  `tests/scripts/test_session_self_initialization.py:92` still asserts those
  labels.

Risk/impact:

The plan gives enough contract detail to prevent a later implementation from
mistaking a terminology rename for durable root/subject enforcement.

Recommended action:

The implementation proposal should explicitly include migration from
workstream-focus state to work-subject state, root resolver tests, and
application/GT-KB lane separation in verification output.

### F4 - Portable GT-KB Delivery Is Covered

Status: accepted.

Evidence:

- The Phase 7 report requires upstream GT-KB product delivery for clean
  adopters at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:319`.
- The upstream `groundtruth-kb` checkout contains the expected managed delivery
  surfaces: `templates/project/AGENTS.md`, `templates/hooks/`,
  `templates/rules/file-bridge-protocol.md`, `src/groundtruth_kb/project/scaffold.py`,
  `src/groundtruth_kb/project/doctor.py`, and
  `src/groundtruth_kb/project/preflight.py`.
- `src/groundtruth_kb/project/scaffold.py:371` documents dual-agent template
  copying, including `AGENTS.md`, bridge rules, and Codex bootstrap surfaces;
  `src/groundtruth_kb/project/scaffold.py:407` copies managed hook templates.
- `src/groundtruth_kb/project/doctor.py:1455` exposes `run_doctor`, and
  `src/groundtruth_kb/project/preflight.py:60` and
  `src/groundtruth_kb/project/preflight.py:139` show existing preflight checks
  for bridge in-flight awareness and scaffold coverage.

Risk/impact:

The plan is not Agent Red-only. It identifies the product packaging and
clean-adopter surfaces that must be updated for durable behavior.

Recommended action:

The later implementation proposal must include an upstream GT-KB file/test
slice for scaffold, upgrade, doctor/preflight, templates, and clean-adopter
tests, not only Agent Red dogfood changes.

### F5 - Verification Strategy Is Adequate For Planning

Status: accepted.

Evidence:

- The Phase 7 report includes a risk-to-test verification matrix beginning at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:359`.
- Acceptance criteria at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:376`
  require subject terminology/state, default application subject, explicit
  subject-changing commands, resolved-root traversal rejection,
  subject-labeled startup/dashboard/readiness/tests, live bridge authority,
  typed control-plane operations, overlay non-authority, generated startup
  safety text, and upstream clean-adopter delivery.
- This review ran document and repository evidence checks, not implementation
  tests, because the bridge request is a planning review. Command evidence used
  included `Select-String` against `bridge/INDEX.md`, `rg -n` scans of Phase
  3-7 planning reports and current hook/startup tests, `Get-ChildItem -Recurse
  -File templates` in the upstream GT-KB checkout, and a pre-write
  `Get-Content -Raw .claude\rules\operating-role.md` authority check.

Risk/impact:

The plan identifies the right verification lanes, but those lanes are still
future work because no implementation has been proposed or applied.

Recommended action:

Do not claim implementation verification from this GO. The later
post-implementation bridge report should include separate Agent Red application
and upstream GT-KB test sections.

## Required Action Items Or Conditions

No action is required before accepting this as the completed
`GTKB-ISOLATION-007` planning artifact.

Conditions for later implementation:

1. Submit a concrete implementation proposal before changing work-subject/root
   enforcement behavior.
2. Preserve the distinction between operating role, work subject, root,
   topology, and bridge role slot.
3. Implement resolved-root enforcement through the Phase 4 service and Phase 5
   typed operation registry where applicable; do not rely on prefix-only hook
   checks as the authoritative boundary.
4. Keep Phase 6 overlays non-authoritative and exclude overlay copies from
   canonical bridge, DA, MemBase, readiness, and formal approval decisions.
5. Include upstream GT-KB scaffold/template/doctor/preflight delivery and clean
   adopter tests.
6. Report application and GT-KB verification lanes separately.

## Decision Needed From Owner

None for this planning GO.
