NO-GO

# Loyal Opposition Review - GT-KB Session Work Subject Proposal

bridge_kind: review
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
target_paths: ["bridge/gtkb-session-work-subject-001.md", "memory/work_list.md", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/AGENTS.md", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py"]
reviewed_file: bridge/gtkb-session-work-subject-001.md
reviewed_status: NEW

## Role Authority

- Effective role: Loyal Opposition
- Authority source path: E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/.claude/rules/operating-role.md
- Required durable role: active_role: loyal-opposition
- Observed durable role: active_role: loyal-opposition
- Scanner name: Codex automated Loyal Opposition bridge review scan

## Verdict

NO-GO for implementation as currently proposed.

The subject distinction is directionally correct: existing code already has an
application/GT-KB focus state, startup text, and path guard, and the current
startup report can mix Agent Red release posture with GT-KB infrastructure
posture. However, this bridge entry is not ready to authorize implementation
because it conflicts with the standing backlog's current planning authority,
uses bridge metadata that the protocol gate rejects, and leaves durability and
portable adopter delivery underspecified.

## Findings

### F1 - Implementation is ahead of the governed backlog sequence

Severity: High

Evidence:

- `bridge/gtkb-session-work-subject-001.md:210-286` proposes six
  implementation phases across Agent Red hooks, startup, dashboard,
  release-readiness, tests, mutation guardrails, and upstream GT-KB delivery.
- `memory/work_list.md:189-197` defines the active related work as
  `GTKB-ISOLATION-007 - Create detailed Phase 7 plan: work subject and root
  enforcement`, not implementation. Its required outcome is a detailed plan
  integrating work subject with root-boundary checks, dashboard/control-plane
  session controls, durable mode projection, multi-harness role awareness, and
  generated subject-specific startup files. It also says the plan may revise
  this bridge proposal after root/service/control-plane/overlay requirements
  are clear.
- `memory/work_list.md:149-187` shows prerequisite Phase 3 through Phase 6
  planning items still in the sequence before Phase 7.

Risk/impact:

Approving implementation now would let Prime Builder bake subject behavior
into hooks and startup paths before the root boundary, service boundary,
control plane, and overlay decisions have been reduced to an implementable
plan. That creates a real risk of local-only behavior that does not survive the
intended Agent Red/GT-KB isolation model.

Required action:

Revise this thread as a Phase 7 implementation plan, or provide owner-approved
evidence that the backlog sequence has been changed and implementation is now
authorized. The revised proposal must explicitly state how it depends on, or
supersedes, the Phase 3-6 planning items.

### F2 - Bridge metadata is invalid for the protocol gate and not aligned to the live work item

Severity: High

Evidence:

- `bridge/gtkb-session-work-subject-001.md:5-9` declares
  `bridge_kind: implementation_proposal` and `work_item_ids:
  [GTKB-SUBJECT-001]`.
- Upstream GT-KB accepts only `proposal`, `review`,
  `implementation_report`, and `verification` as bridge kinds
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:20-25`).
- The hard gate enforces valid `bridge_kind` and at least one blocking target
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:675-701`).
- A gate check through the upstream CLI entry point returned `exit_code=1` for
  this workspace and included `gtkb-session-work-subject` violations:
  `missing or invalid bridge_kind metadata for hard gate` and `latest bridge
  entry is awaiting Loyal Opposition review`.
- Search evidence found `GTKB-SUBJECT-001` only in the proposal, while the live
  standing backlog and dashboard refer to `GTKB-ISOLATION-007`
  (`memory/work_list.md:189-197`,
  `docs/gtkb-dashboard/dashboard-data.json:7272-7275`).

Risk/impact:

The bridge item itself becomes noisy or invalid release-gate evidence. The
work cannot be reliably traced to the governed standing backlog, and future
status/gate tools may continue to flag the thread even if the implementation
intent is otherwise sound.

Required action:

Reissue the proposal with valid metadata, normally:

```text
bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
```

If `GTKB-SUBJECT-001` is intended to be a real work item, create or cite its
governed record and explain how it relates to `GTKB-ISOLATION-007`.

### F3 - The proposed verification plan starts from an unclean Agent Red baseline

Severity: Medium

Evidence:

- I ran:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
```

- Result: `1 failed, 28 passed`.
- Failure:
  `tests/scripts/test_session_self_initialization.py:895` expected
  `["GTKB-GOV-010"]`, but the live model returned
  `["GTKB-ISOLATION-007", "GTKB-GOV-010"]`.
- The failing test is inside the proposal's own verification surface
  (`bridge/gtkb-session-work-subject-001.md:311-318`).

Risk/impact:

Prime Builder cannot use the listed focused regression set to prove the
implementation unless the existing subject/backlog expectation drift is first
normalized. Otherwise implementation failures and pre-existing test drift will
be conflated.

Required action:

Revise the verification plan to make the current focused baseline clean, or
explicitly include the subject-aware test update required before implementation
verification can be trusted.

### F4 - Durable subject storage and precedence remain unresolved

Severity: Medium

Evidence:

- The proposal requires `work subject GT-KB` to switch current and future
  session interpretation until changed back
  (`bridge/gtkb-session-work-subject-001.md:288-305`).
- The proposal asks whether subject should remain in the current untracked hook
  state or move to a tracked `work-subject.md` record
  (`bridge/gtkb-session-work-subject-001.md:340-351`).
- Current Agent Red state uses `.claude/hooks/.workstream-focus-state.json`,
  defaults to application on missing/invalid state, and writes the state file
  from `save_state()` (`scripts/workstream_focus.py:17`,
  `scripts/workstream_focus.py:172-215`).

Risk/impact:

"Durable" can mean different things across one harness session, a fresh local
session, a clean clone, an upgraded adopter project, or a generated overlay.
Without choosing the storage contract, implementation can pass local tests but
still fail fresh-session determinism or multi-harness projection.

Required action:

Define the storage contract in the revised proposal: state file path, schema,
tracked/untracked status, invalid/stale handling, exact precedence between an
explicit owner prompt and stored subject, and how scaffold/upgrade projects get
the default application subject.

### F5 - Portable GT-KB delivery needs explicit managed-artifact coverage

Severity: Medium

Evidence:

- The proposal says to update GT-KB scaffold templates and doctor/preflight
  visibility (`bridge/gtkb-session-work-subject-001.md:279-286`).
- Upstream scaffold output is registry/template driven for hooks, rules, and
  dual-agent bootstrap files
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:124-147`,
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:272-312`,
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:370-452`).
- The current adopter `AGENTS.md` template still describes generic bridge
  startup behavior, not work-subject startup scoping
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/AGENTS.md:74-80`).

Risk/impact:

Agent Red-only changes would not guarantee that clean GT-KB adopter projects
default to application subject or receive the same guardrails after
`gt project init` / upgrade.

Required action:

In the revised plan, name the exact managed artifacts/templates to add or
change, whether they are scaffolded, upgraded, or doctor-only, and the upstream
tests that prove clean-adopter default behavior and upgrade preservation.

## Accepted Direction To Preserve

- Keep backward-compatible aliases for `application mode` and `GT-KB mode`.
  Current tests cover those commands (`tests/hooks/test_workstream_focus.py:47-69`).
- Preserve the existing path guard classification as a starting point:
  `scripts/workstream_focus.py:96-128` defines GT-KB and application path
  groups, and `scripts/workstream_focus.py:452-482` blocks cross-subject
  mutating tool use.
- Preserve separate reporting for Agent Red release state and GT-KB
  infrastructure posture. Current startup rendering already exposes both
  (`scripts/session_self_initialization.py:2856-2873`), which is the ambiguity
  the work-subject model should resolve rather than hide.

## Required Action Items Before GO

1. Reissue as a valid bridge proposal with accepted `bridge_kind` metadata and
   governed work-item alignment.
2. Reconcile the proposal with the standing backlog: either make it the
   `GTKB-ISOLATION-007` detailed plan or provide owner-approved authority for
   implementation now.
3. Specify durable subject storage, invalid/stale handling, prompt precedence,
   and multi-harness/fresh-session behavior.
4. Add subject-aware baseline test updates so the focused Agent Red regression
   command can pass before post-implementation verification.
5. Specify the upstream managed-artifact, scaffold, upgrade, and doctor changes
   required for clean adopters.

## Decision Needed From Owner

None for this NO-GO. Prime Builder can revise the bridge entry.
