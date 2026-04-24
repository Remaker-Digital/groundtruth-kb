NEW

# GT-KB Session Work Subject Proposal

bridge_kind: implementation_proposal
scope: protocol
work_item_ids: [GTKB-SUBJECT-001]
spec_ids: []
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", "tests/hooks/test_workstream_focus.py", "scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py", "scripts/check_codex_hook_parity.py", "tests/scripts/test_codex_hook_parity.py", "docs/gtkb-dashboard/session-startup-report.md", "docs/gtkb-dashboard/dashboard-data.json", "memory/work_list.md", "bridge/INDEX.md", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/"]

## Requested Verdict

GO for implementation, or NO-GO with specific required revisions.

This proposal is for review only. It does not implement code changes, mutate
formal GOV/SPEC/PB/ADR/DCL records, release GT-KB, release Agent Red, deploy,
or change production behavior.

## Claim

GT-KB should replace the user-facing "workstream focus" concept with a durable
session **work subject** toggle:

- `work subject application`
- `work subject GT-KB`

The default subject for GT-KB adopter projects must be `application`. Ambiguous
owner directions such as "release readiness", "run the tests", "fix the
bridge", "prepare for release", or "what is next?" must be interpreted against
the active subject. The active subject must scope startup priorities, dashboard
signals, release-readiness claims, test summaries, bridge/work-item surfacing,
and mutation guardrails.

For normal GT-KB users, the default application subject prevents unintended
changes to GT-KB governance, scaffold, hook, rule, bridge, and release behavior.
For Agent Red's current dogfooding case, switching the subject to GT-KB should
prevent accidental Agent Red product changes while GT-KB is treated as an
independent releasable product.

## Prior Deliberations

Deliberation search was run before this proposal.

Relevant records:

- `DELIB-0706` states that Agent Red is the use case and GT-KB is the product
  for specification-pipeline features.
- `DELIB-0834` states that Agent Red is a fully conformant application
  sustained by GT-KB, not an ad hoc exception.
- `DELIB-0785` records a separate GT-KB release-readiness bridge thread,
  proving that "release readiness" can refer to GT-KB independently of Agent
  Red production readiness.
- `DELIB-0829` makes GT-KB governance adoption an Agent Red production-release
  gate, which is useful but also creates subject ambiguity unless the current
  subject is explicit.
- `DELIB-0840` requires fresh sessions to self-initialize with priorities and
  dashboard evidence, so subject scoping must affect startup output.
- `DELIB-0874` requires artifact-oriented governance and durable preservation
  of decisions, plans, risks, and accepted future work.
- `DELIB-0876` records the owner directive and Prime Builder investigation
  that produced this proposal.

## Investigation Findings

### Case 1 - Release readiness has two valid subjects

The phrase "release readiness" can refer to Agent Red customer/deployment
readiness or to GT-KB package/scaffold/adoption readiness.

Evidence:

- `DELIB-0785` is a GT-KB release-readiness bridge thread.
- `DELIB-0560`, `DELIB-0561`, and `DELIB-0562` concern Agent Red production
  release-gate evidence and baseline correction.
- `scripts/session_self_initialization.py` reports Agent Red release blockers
  through `metrics["regression"]["release_blocker_count"]`, while also
  reporting GT-KB upgrade posture under infrastructure.

Error pattern:

If the subject is implicit, "Are we release ready?" can be answered from the
wrong evidence set. A zero Agent Red blocker count does not prove GT-KB package
readiness, and a failing GT-KB protocol gate does not necessarily block an
Agent Red UI fix unless the GT-KB subject is active or the gate is explicitly
part of the release lane.

### Case 2 - Startup priorities can mix application work and GT-KB product work

The standing backlog currently contains Agent Red release work, GT-KB adoption
work, GT-KB mass-adoption work, and GT-KB core-spec-intake work.

Evidence:

- `memory/work_list.md` includes `GTKB-MASS-001` and `GTKB-CORE-001` as active
  GT-KB workstreams.
- The same file also includes Agent Red release items such as `GTKB-GOV-010`
  and paused commercial-readiness items.
- `scripts/session_self_initialization.py` currently has Agent Red dashboard
  scope filtering, but startup still reports GT-KB upgrade posture and action
  center items in the same generated startup model.

Error pattern:

A session that starts from an application task such as a standalone admin UI
change can be presented with GT-KB bridge/scaffold priorities. Conversely, a
GT-KB release session can be distracted by Agent Red application drift.

### Case 3 - Test summaries can be read against the wrong product

Agent Red and GT-KB have different test universes, release gates, and readiness
claims.

Evidence:

- Agent Red tests live in this repository under `tests/`, with application
  paths such as `src/`, `admin/`, `widget/`, and release-gate scripts.
- GT-KB tests live in the separate upstream checkout at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/`.
- `scripts/session_self_initialization.py` reports testing-service integration
  health as implementation infrastructure while the dashboard primary scope is
  Agent Red.
- Prior GT-KB bridge verifications cite upstream commands such as
  `python -m pytest tests/test_file_bridge.py ...` in the GT-KB checkout.

Error pattern:

"Run the tests" or "tests are green" can be reported as if one suite proves
both products. That creates false confidence: Agent Red UI tests do not prove
GT-KB scaffold/release correctness, and GT-KB parser tests do not prove Agent
Red customer behavior.

### Case 4 - Current focus guard protects paths, not ambiguous intent

The existing hook is useful but incomplete.

Evidence:

- `scripts/workstream_focus.py` defines `FOCUS_APPLICATION` and
  `FOCUS_GTKB_INFRASTRUCTURE`.
- It blocks writes across broad path categories in `guard_tool_use()`.
- Its user-facing commands are `application mode` and `GT-KB mode`, and startup
  calls the state "Application Focus" or "GT-KB Infrastructure Focus".

Error pattern:

The path guard can block a direct write to `.claude/rules/`, but it does not
make the subject of "release readiness", "run tests", "fix the bridge", or
"continue last session" explicit enough. The term "focus" is also less
authoritative than "work subject" for deciding which product a session is
about.

### Case 5 - Bridge protocol gates and application release blockers can
contradict each other without subject labels

Protocol gates can fail for GT-KB bridge work while application release
blockers are zero.

Evidence:

- `gt bridge gate --require-verified --scope protocol --json` currently fails
  on older GT-KB/protocol entries such as `gtkb-mass-adoption-first-commit-
  package`, `gtkb-core-spec-intake-phase3b-answer`, `gtkb-core-spec-intake`,
  and `gtkb-azure-cicd-gates`.
- The generated startup report can simultaneously show `Release blockers: 0`
  for Agent Red.

Error pattern:

Without a subject label, "blocked" and "ready" can both be true but refer to
different products. The UI and narrative need to say which subject each claim
belongs to.

### Case 6 - Paused application threads can remain visible while GT-KB work is
active

Commercial-readiness bridge entries are Agent Red application threads, and
some are paused by owner decision.

Evidence:

- `bridge/INDEX.md` contains a 2026-04-18 pause note for the
  `commercial-readiness-spec-*` threads.
- `memory/work_list.md` now marks `GTKB-GOV-007` as paused, but those bridge
  entries still exist as historical NO-GO records.

Error pattern:

If startup or continuation logic ignores subject and lifecycle state, it can
suggest paused Agent Red commercial work while the owner is asking about GT-KB
release or vice versa.

### Case 7 - Normal GT-KB adopters should not mutate GT-KB internals

For most projects, GT-KB is infrastructure used to build the application, not
the application being built.

Evidence:

- `DELIB-0834` says Agent Red should conform to GT-KB rather than bypass it.
- `scripts/workstream_focus.py` already treats `.claude/`, `.codex/`,
  `.groundtruth/`, dashboard, and GT-KB governance paths as infrastructure.

Error pattern:

A normal adopter asking for application work should not accidentally modify
GT-KB governance, scaffold, hooks, bridge behavior, or release gates. The
system should warn with a predefined message and instruct the user to switch to
`work subject GT-KB`.

## Proposed Implementation

### Phase 1 - Terminology and durable state

1. Introduce a durable user-facing concept named `work subject`.
2. Preserve backward compatibility with the current focus state file and
   commands, but make new startup and hook messaging use subject terminology.
3. Add exact standalone commands:
   - `work subject application`
   - `work subject GT-KB`
4. Keep default subject as `application`.
5. Treat explicit owner wording as higher priority than the toggle. Example:
   "for GT-KB, run release readiness" should use GT-KB even if the current
   subject is application.

Implementation note: keep the existing `scripts/workstream_focus.py` module
name if that avoids unnecessary churn, but expose functions and startup text as
work-subject behavior. A later cleanup can rename internals.

### Phase 2 - Startup subject scoping

1. Startup disclosure must include:
   - `Default work subject: Application`
   - `Current work subject: Application` or `Current work subject: GT-KB`
   - the exact toggle commands
   - one sentence explaining ambiguous prompt interpretation
2. Startup priority selection must be scoped by subject:
   - application subject: Agent Red application/release/customer work
   - GT-KB subject: GT-KB package/scaffold/governance/adoption work
3. Dashboard action-center items must carry a subject label.
4. "Continue Last Session" must separate application bridge entries from GT-KB
   protocol/adoption entries.

### Phase 3 - Release-readiness scoping

1. In application subject, release readiness means Agent Red customer/deployed
   application readiness.
2. In GT-KB subject, release readiness means GT-KB package, scaffold,
   templates, governance, CLI, docs, adopter upgrade, clean-adopter, and
   protocol-gate readiness.
3. Startup, dashboard, and final answers must report the subject of every
   release-readiness claim.
4. If the owner asks "release readiness" and the subject state is missing,
   invalid, or stale, ask one focused clarification before doing release work.

### Phase 4 - Test scoping

1. Add subject-aware test command recommendations.
2. Application subject defaults to Agent Red test/release commands.
3. GT-KB subject defaults to upstream GT-KB test/release commands in the
   `groundtruth-kb` checkout.
4. If both test sets are run, the final report must show separate sections:
   `Application Test Result` and `GT-KB Test Result`.
5. Prevent a combined "green" claim unless both subjects were intentionally in
   scope.

### Phase 5 - Mutation guardrails

1. In application subject, attempts to mutate GT-KB governance/behavior paths
   should block or warn with a predefined instruction:
   "Current work subject is application. This change targets GT-KB governance
   or behavior. Switch with standalone `work subject GT-KB` before proceeding."
2. In GT-KB subject, attempts to mutate Agent Red application paths should
   block or warn with:
   "Current work subject is GT-KB. This change targets application artifacts.
   Switch with standalone `work subject application` before proceeding."
3. Backward-compatible aliases (`application mode`, `GT-KB mode`) may remain,
   but all new instructions should prefer `work subject ...`.

### Phase 6 - Portable GT-KB delivery

1. Add or update GT-KB scaffold templates so adopter projects get the same
   default application subject behavior.
2. Ensure `gt project init` or `gt project upgrade` preserves application
   default unless the adopter explicitly configures GT-KB product-development
   mode.
3. Add doctor/preflight visibility for stale or invalid subject state.

## Acceptance Criteria

1. A clean adopter project defaults to work subject `application`.
2. `work subject GT-KB` switches current and future session interpretation to
   GT-KB until changed back.
3. Startup priorities differ by subject and do not comingle Agent Red UI or
   customer-release work with GT-KB package/scaffold/release work.
4. "Release readiness" is reported against the active subject and names that
   subject in the output.
5. "Run the tests" produces subject-specific test recommendations and
   summaries.
6. Application subject blocks or warns before GT-KB governance/behavior
   mutations.
7. GT-KB subject blocks or warns before Agent Red application mutations.
8. Existing aliases and tests for `application mode` and `GT-KB mode` continue
   to pass or are intentionally migrated with compatibility coverage.
9. Dashboard data, startup report, and session-focus choices include work
   subject labels.
10. No formal artifact mutation is made by this implementation unless separately
    approved under the artifact approval gate.

## Verification Plan

Run in Agent Red:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
python scripts/release_candidate_gate.py --skip-frontend
```

Run in upstream `groundtruth-kb` if scaffold/template delivery is included:

```powershell
python -m pytest tests/test_scaffold_bridge_index.py tests/test_scaffold_bridge_rules.py tests/test_governance_hooks.py tests/test_preflight_checks.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

Manual verification:

1. Start a fresh session with default subject and confirm application-scoped
   startup.
2. Send `work subject GT-KB`, start/refresh session startup, and confirm
   GT-KB-scoped startup.
3. Attempt a GT-KB path mutation under application subject and confirm the
   predefined warning/block.
4. Attempt an application path mutation under GT-KB subject and confirm the
   predefined warning/block.

## Risks And Required Loyal Opposition Review Questions

1. Does this proposal create a third concept that conflicts with role
   assignment or bridge status? Proposed answer: no; role is "who am I",
   subject is "what product is this session about", bridge status is
   "where is the review lifecycle".
2. Should subject be immediate, next-session only, or both? Proposed answer:
   immediate and durable, with startup showing current state.
3. Should subject be stored in the current untracked hook state or in a tracked
   durable rule file? Proposed answer: use the current state path for
   compatibility but evaluate a tracked `work-subject.md` record if Loyal
   Opposition wants stronger fresh-session determinism.
4. How should mixed-subject tasks be handled? Proposed answer: allow explicit
   mixed scope only when the prompt names both subjects; reports must separate
   outcomes.

## Owner Decision Needed

None before Loyal Opposition review. Implementation should wait for `GO`.
