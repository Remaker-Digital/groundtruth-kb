REVISED

# GT-KB Session Work Subject Phase 7 Plan

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
spec_ids: []
target_paths: ["bridge/gtkb-session-work-subject-001.md", "bridge/gtkb-session-work-subject-002.md", "memory/work_list.md", "scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", "tests/hooks/test_workstream_focus.py", "scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py", "scripts/check_codex_hook_parity.py", "tests/scripts/test_codex_hook_parity.py", "docs/gtkb-dashboard/session-startup-report.md", "docs/gtkb-dashboard/dashboard-data.json", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/AGENTS.md", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/"]

## Requested Verdict

GO for using this as the `GTKB-ISOLATION-007` Phase 7 implementation plan, or
NO-GO with required revisions.

This is a planning bridge entry. It does not authorize immediate implementation
of work-subject code, mutate formal GOV/SPEC/PB/ADR/DCL records, release
GT-KB, release Agent Red, deploy, or move repositories.

## Claim

The prior work-subject proposal should be reduced from an implementation
proposal to a Phase 7 implementation plan. The plan preserves the core idea:
every session has an explicit durable **work subject**:

- `work subject application`
- `work subject GT-KB`

The active work subject scopes ambiguous owner directions, startup priorities,
release-readiness claims, test recommendations, dashboard signals, bridge/work
item surfacing, and mutation guardrails.

Implementation must wait until the Phase 3 through Phase 6 isolation plans are
complete or explicitly superseded by owner decision. Those phases define the
environment boundary, scoped service boundary, dashboard/control-plane boundary,
and copy-only overlay boundary that this Phase 7 plan depends on.

## NO-GO Remediation

### F1 - Backlog sequence

This revision is explicitly aligned to `GTKB-ISOLATION-007`, not
`GTKB-SUBJECT-001`, and is a Phase 7 plan rather than implementation
authorization.

Implementation dependencies:

- Phase 3 must define application-subject filesystem, container, CI, and dev
  environment write boundaries.
- Phase 4 must define which GT-KB operations are exposed through scoped
  services rather than raw parent-root/database authority.
- Phase 5 must define dashboard/control-plane operations, durable mode toggles,
  session-control operations, dry-run/diff previews, and audit behavior.
- Phase 6 must define copy-only overlays, source hashes, stale-overlay
  detection, and promotion paths for proposed changes.

If Phase 3 through Phase 6 change the accepted root/service/control-plane or
overlay contracts, this Phase 7 plan must be revised before implementation.

### F2 - Bridge metadata

This revision uses protocol-gate-compatible metadata:

```text
bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
```

`GTKB-SUBJECT-001` is not used as an active work item unless it is later
created as a governed backlog record.

### F3 - Baseline test drift

Before implementation verification, the Agent Red focused baseline must be
made clean. The known current failure is in
`tests/scripts/test_session_self_initialization.py`, where top-priority action
selection now includes `GTKB-ISOLATION-007` alongside `GTKB-GOV-010`.

The implementation proposal that follows this plan must either:

1. update the subject-aware startup/backlog expectation before feature changes,
   or
2. split the verification lane so pre-existing backlog-priority drift is
   resolved before work-subject behavior is judged.

Post-implementation verification must not conflate pre-existing test drift with
new work-subject regressions.

### F4 - Durable subject storage and precedence

This plan defines the storage and precedence contract below.

### F5 - Portable GT-KB delivery

This plan names the managed artifacts, scaffold/upgrade behavior, and upstream
tests required for clean adopters.

## Subject Model

### Terminology

- **Operating role** answers "who is the harness acting as?"
  Examples: Prime Builder, Loyal Opposition.
- **Work subject** answers "which product is this session about?"
  Values: `application` or `GT-KB`.
- **Bridge status** answers "where is the review lifecycle?"
  Examples: `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`.

These concepts must not be collapsed. A Loyal Opposition session can review
application-subject work or GT-KB-subject work. A Prime Builder session can
implement application-subject work or GT-KB-subject work after the appropriate
bridge verdict.

### Default

Clean GT-KB adopter projects default to work subject `application`.

Agent Red also defaults to `application` unless the owner explicitly switches
the subject or the prompt names GT-KB as the current task subject.

## Durable Storage Contract

### Canonical state file

Use an application-local runtime state file:

```text
.groundtruth/session/work-subject.json
```

The file is local operational state, not a formal GOV/SPEC/PB/ADR/DCL artifact.
It should be excluded from source control by default for normal adopters.

Schema:

```json
{
  "schema_version": 1,
  "current_subject": "application",
  "updated_at": "2026-04-23T00:00:00Z",
  "updated_by": "owner|harness",
  "source": "standalone owner command|explicit task override|startup default",
  "project_root": "absolute application root",
  "gtkb_root": "absolute GT-KB product root or null",
  "role_slot": "shared"
}
```

### Compatibility state

The existing `.claude/hooks/.workstream-focus-state.json` remains a
backward-compatible read path for one migration window. On first successful
read, the hook should write the canonical `.groundtruth/session/work-subject.json`
file and continue using the new path.

### Missing, invalid, or stale state

- Missing file: default to `application` and create state lazily only when a
  subject-changing command is received.
- Invalid JSON or unknown subject: warn, default to `application`, and write a
  repair record on the next subject-changing command.
- Project-root mismatch: treat state as stale, warn, default to `application`,
  and do not silently reuse it.
- Timestamp age alone does not make state stale. Root mismatch, schema mismatch,
  or invalid subject does.

### Precedence

1. A standalone owner command `work subject application` or
   `work subject GT-KB` changes the current session and persists the new state.
2. An explicit task phrase such as "for GT-KB, run release readiness" overrides
   the persisted subject for that task only unless it is a standalone subject
   command.
3. The persisted subject applies to ambiguous prompts.
4. If no valid persisted subject exists, use `application`.

Backward-compatible aliases remain accepted:

- `application mode`, `app mode`, `agent red mode`
- `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`

New user-facing text should prefer `work subject ...`.

## Root-Boundary Enforcement Plan

Implementation must use the root topology accepted by earlier isolation phases.
The Phase 7 hook must not rely on string-prefix checks alone when a safer
resolved-path boundary helper is available.

Required behavior:

- Resolve the active project root, application root, and GT-KB product root.
- In `application` subject, block or warn before mutating GT-KB product paths.
- In `GT-KB` subject, block or warn before mutating application product paths
  unless the task explicitly names an application migration, adopter upgrade,
  or app-local fixture.
- Refuse path traversal or symlink tricks that escape the allowed root.
- Keep existing path-category behavior as a compatibility layer while root
  enforcement becomes the governing check.

Required messages:

```text
Current work subject is application. This change targets GT-KB governance or
behavior. Switch with standalone `work subject GT-KB` before proceeding.
```

```text
Current work subject is GT-KB. This change targets application artifacts.
Switch with standalone `work subject application` before proceeding.
```

Bridge-function/use repairs remain governed by `GOV-FILE-BRIDGE-AUTHORITY-001`:
Loyal Opposition may repair the bridge and downstream bridge-dependent
artifacts when the work is scoped to sustaining bridge function and use.

## Startup Scoping Plan

Startup must display:

- `Default work subject: Application`
- `Current work subject: Application` or `Current work subject: GT-KB`
- exact toggle commands
- a sentence explaining that ambiguous prompts are interpreted against the
  active work subject
- a reminder that live `bridge/INDEX.md` is the sole bridge-state authority

Application subject startup:

- Prioritize Agent Red application, customer, release, deployment, and app-local
  governance work.
- Show GT-KB infrastructure posture only as supporting context unless it is an
  explicit Agent Red release gate.
- Do not mix GT-KB package readiness into Agent Red release readiness claims.

GT-KB subject startup:

- Prioritize GT-KB package, scaffold, governance, adopter-upgrade, protocol-gate,
  clean-adopter, and upstream release-readiness work.
- Show Agent Red only as dogfood/adopter evidence unless the task explicitly
  asks for application work.

Both subjects:

- Re-read live `bridge/INDEX.md` before deciding bridge state.
- Separate latest `NEW`/`REVISED` review entries from latest `GO`/`NO-GO`
  continuation entries.
- Label bridge entries with subject when the subject is mechanically known.

## Release-Readiness Scoping Plan

Application subject:

- "Release readiness" means Agent Red customer/deployed application readiness.
- Report Agent Red blockers, app release gates, production deployment posture,
  app tests, and customer-impact risks.

GT-KB subject:

- "Release readiness" means GT-KB package, scaffold, CLI, docs, templates,
  governance, adopter upgrade, clean-adopter tests, bridge protocol gates, and
  upstream package release posture.

Both:

- Every readiness claim must name its subject.
- Do not write "green" or "ready" as a combined claim unless both subjects were
  intentionally in scope and separately verified.

## Test Scoping Plan

Application subject default test recommendations:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
python scripts/release_candidate_gate.py --skip-frontend
```

GT-KB subject default test recommendations in the upstream checkout:

```powershell
python -m pytest tests/test_file_bridge.py tests/test_project_scaffold.py tests/test_preflight_checks.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

If both subjects are tested, final reports must include separate sections:

- `Application Test Result`
- `GT-KB Test Result`

## Dashboard And Control-Plane Plan

Dashboard data and UI must carry work-subject labels for:

- action-center items
- bridge entries
- readiness signals
- test rollups
- drift/path reports
- session mode controls

Control-plane operations from Phase 5 must expose subject changes through typed
operations, not arbitrary file edits. Each operation must include:

- selected harness role slot
- target project root
- target work subject
- immediate-vs-next-session effect
- dry-run/diff preview
- audit record
- rollback record where applicable

The dashboard must not be treated as current bridge authority. It can display
generated-time bridge summaries, but operational bridge decisions must read
live `bridge/INDEX.md`.

## Generated Startup Projection Plan

Phase 7 may generate subject-specific AI-facing startup instruction files only
after Phase 5 and Phase 6 define the projection mechanism.

Rules:

- Source policies remain canonical.
- Generated files must include source hashes and generation time.
- Generated files must say whether they are authoritative instructions or
  non-authoritative overlays.
- Projection must not remove mandatory root-boundary, bridge-authority, GOV, or
  owner-action visibility text.
- Projection must not remove ordinary AI judgment from application work.

## Multi-Harness And Role Awareness

The work subject is shared project context by default, not a role assignment.
Prime Builder and Loyal Opposition should see the same current subject when
operating in the same application root.

If later control-plane work introduces per-harness subject overrides, the UI
and state file must make the override explicit and must not silently diverge
the Prime Builder and Loyal Opposition subjects.

Bridge files should include subject metadata once the bridge parser accepts it.
Until then, subject classification may be inferred for dashboard/report display
only and must not replace live index status.

## Portable GT-KB Delivery Plan

Upstream GT-KB implementation must update or add managed artifacts for clean
adopters:

- project `AGENTS.md` template
- hook template for work-subject command parsing and mutation guardrails
- rule template for work-subject startup language
- scaffold registry entries that install those templates
- upgrade logic that preserves existing local subject state
- doctor/preflight checks for missing, invalid, or root-mismatched subject
  state
- tests proving clean-adopter default `application` behavior

Clean-adopter behavior:

- `gt project init` creates an app-local project that defaults to
  `application`.
- `gt project upgrade` does not overwrite a valid local work-subject state.
- invalid state is reported by doctor/preflight and repaired only through the
  defined operation path.

## Implementation Sequence After GO

Implementation must be proposed separately after this plan receives GO and
after Phase 3 through Phase 6 are complete or explicitly superseded.

Recommended sequence:

1. Normalize Agent Red baseline test expectations for current isolation backlog
   priority behavior.
2. Add canonical work-subject state helpers while preserving current focus
   aliases.
3. Update hook command parsing for `work subject ...`.
4. Add root-boundary enforcement using the accepted topology helper.
5. Update startup model and report rendering with subject labels.
6. Update dashboard data/action-center subject labels.
7. Update release-readiness and test recommendation text.
8. Add Codex/Claude parity checks for subject hook intent.
9. Add upstream scaffold/template/doctor delivery.
10. Run Agent Red and upstream GT-KB verification lanes.
11. File a post-implementation bridge report for Loyal Opposition verification.

## Acceptance Criteria

1. Clean GT-KB adopter projects default to work subject `application`.
2. `work subject GT-KB` persists across fresh sessions until changed back.
3. Explicit prompt wording can override persisted subject for one task without
   persisting a new subject unless it is a standalone subject command.
4. Startup priorities are subject-scoped and labeled.
5. Release-readiness claims name their subject.
6. Test recommendations and final test summaries are subject-scoped.
7. Application subject blocks or warns before GT-KB product mutations.
8. GT-KB subject blocks or warns before application mutations.
9. Bridge state is still determined only from live `bridge/INDEX.md`.
10. Existing aliases continue to work.
11. Clean-adopter scaffold/upgrade/doctor tests prove portable delivery.

## Verification Plan

Agent Red focused baseline before implementation:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
```

Agent Red post-implementation:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
python scripts/release_candidate_gate.py --skip-frontend
```

Upstream GT-KB post-implementation:

```powershell
python -m pytest tests/test_file_bridge.py tests/test_project_scaffold.py tests/test_preflight_checks.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

Manual checks:

1. Start with missing work-subject state and confirm default `application`.
2. Send `work subject GT-KB` and confirm immediate and fresh-session GT-KB
   subject.
3. Send `work subject application` and confirm return to application subject.
4. Attempt GT-KB product mutation under application subject and confirm warning
   or block.
5. Attempt application mutation under GT-KB subject and confirm warning or
   block.
6. Ask "Are we release ready?" under each subject and confirm subject-labeled
   answers.
7. Ask "Run the tests" under each subject and confirm subject-specific command
   recommendations.

## Risks

- If Phase 3 through Phase 6 choose a different root/service/control-plane or
  overlay mechanism, this plan may need revision.
- If subject state is tracked in git, normal local subject toggles could create
  unwanted repository churn. This plan avoids that by using local runtime state.
- If subject inference becomes too aggressive, explicit owner task wording may
  be misclassified. The first implementation should keep inference narrow and
  prefer explicit commands.

## Owner Decision Needed

None for this revised planning bridge entry. Implementation still requires a
future `GO` for a concrete implementation proposal or an explicit owner
directive that supersedes the bridge sequence.
