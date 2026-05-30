REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-s363-work-subject-aware-probe-revised-1
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal REVISED-1 - Work-subject-aware testing/tool integration probe

bridge_kind: implementation_proposal
Document: gtkb-work-subject-aware-testing-integration-probe
Version: 003 (REVISED-1)
Reviewed-against: bridge/gtkb-work-subject-aware-testing-integration-probe-002.md (NO-GO)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3409

target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_testing_service_integrations_work_subject_aware.py"]

## Revision Claim

REVISED-1 addresses both findings in NO-GO -002:

- **FINDING P1-001 (Missing governing fast-lane specification)**: this revision adds `GOV-RELIABILITY-FAST-LANE-001` to `## Specification Links` and to the verification mapping, plus an explicit fast-lane eligibility statement under `## Requirement Sufficiency`.
- **FINDING P1-002 (Proposed work-subject values do not match canonical schema)**: this revision replaces the made-up `"GT-KB"` / `"GT-KB+application"` canonical values with the existing runtime canonical schema: `gtkb_infrastructure` (default, GT-KB repo) and `application` (Agent Red repo). The implementation reuses constants from `scripts.workstream_focus` (`FOCUS_GTKB_INFRASTRUCTURE`, `FOCUS_APPLICATION`) and calls `load_state(project_root)` directly rather than re-parsing the JSON. The non-canonical `"GT-KB+application"` token is dropped entirely; if dual-mode work-subject is needed in the future, it will be added to the canonical schema first and the probe extended in a sibling slice.
- Advisory non-blocker noted: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` added to Specification Links (the revised proposal still discusses test-fixture lifecycle, so the citation is now warranted).

Target paths are unchanged; the implementation surface remains scoped to `scripts/session_self_initialization.py` (modified) and `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (NEW).

## Claim

The `_testing_service_integrations` probe in `scripts/session_self_initialization.py` unconditionally queries `AGENT_RED_GITHUB_REPO` (resolved to `https://github.com/mike-remakerdigital/agent-red` per `.env.local`) regardless of the active work subject. Sessions whose `Active Work Subject: GT-KB Infrastructure Focus` (canonical value `gtkb_infrastructure` per `scripts.workstream_focus.FOCUS_GTKB_INFRASTRUCTURE`) see Agent Red CI labeled as "GT-KB Testing/tool rollup" in the startup banner and dashboard intelligence — a framing/coupling defect. The fix: read the active work subject from `scripts.workstream_focus.load_state(project_root)`, select query repo accordingly, and surface `queried_repo` to the rollup label so the data source is unambiguous.

## Defect / Reproduction

Live probe evidence (S363 backlog review, 2026-05-27):

```
$ cat .env.local | grep AGENT_RED_GITHUB_REPO
AGENT_RED_GITHUB_REPO=https://github.com/mike-remakerdigital/agent-red

$ python -c "from scripts.session_self_initialization import _testing_service_integrations; from pathlib import Path; i = _testing_service_integrations(Path('.'), [], fast_hook=False); print(i['release_candidate_gate']['latest_run_summary'])"
success on develop@1817db0, updated 2026-05-07T00:33:27Z   # Agent Red develop snapshot, 3 weeks old

$ gh run list --limit 5 --repo Remaker-Digital/groundtruth-kb --json workflowName,headBranch,headSha,conclusion,createdAt | python -c "import json,sys; [print(f'{r[\"createdAt\"][:19]}  {r[\"workflowName\"]:25}  {r[\"headBranch\"]:10}  {r[\"headSha\"][:7]}  {r[\"conclusion\"]}') for r in json.load(sys.stdin) if r['workflowName'] == 'Release Candidate Gate']"
2026-05-27T09:14:07  Release Candidate Gate     develop     7ee608e   failure   # GT-KB develop, today's reality
```

GT-KB session sees Agent Red CI (success/2026-05-07) labeled as "GT-KB Testing/tool rollup" when GT-KB's actual RC Gate is failing on develop@7ee608e (today).

The variable name `AGENT_RED_GITHUB_REPO` correctly identifies its intent — it was meant for Agent Red CI. But `_testing_service_integrations` uses it as the universal probe target without checking the active work subject.

Canonical schema reference (from runtime code):

```
$ grep -n "FOCUS_GTKB_INFRASTRUCTURE\|FOCUS_APPLICATION" scripts/workstream_focus.py | head -4
FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"
FOCUS_APPLICATION = "application"
SUBJECT_GTKB = FOCUS_GTKB_INFRASTRUCTURE

$ cat .claude/session/work-subject.json | python -c "import json,sys; print(json.load(sys.stdin).get('current_subject'))"
gtkb_infrastructure
```

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/session_self_initialization.py`
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/REVISED/GO/NO-GO/VERIFIED workflow
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the testing/tool integration rollup is a startup-payload artifact; this fix corrects the data-source-to-label coupling
- `GOV-RELIABILITY-FAST-LANE-001` - governing specification for the reliability fast-lane; this proposal is eligible per the criteria below in `## Requirement Sufficiency` (small single-concern startup reliability defect fix; source + test-addition target paths; no deploy, no force-push, no spec deletion)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs in this section
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps acceptance criteria to specific test commands
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above with active PAUTH
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new regression test creation is a lifecycle trigger; advisory clause satisfied by the test-creation step in IP-4
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion (Owner Decisions section)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`
- `GOV-SESSION-SELF-INITIALIZATION-001` - the testing/tool rollup is a startup-payload field this fix repairs
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the change is read-only at session start; parity preserved (Codex startup hook will inherit the same behavior via the shared script)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates a durable test artifact (work-subject-aware regression test)

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization underlying `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; this proposal applies the authorization per its eligibility criteria
- `S363 backlog review session - Repair Testing/Tool Integrations focus` - owner selected option B from the startup focus menu; subsequent AUQs chose probe-defect-first and work-subject-aware fix path
- `DELIB-0876` - durable session work subject precedent; `.claude/session/work-subject.json` is the canonical state file this fix reads from (via `scripts.workstream_focus.load_state`)
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - backlog source-of-truth governance; this fix improves backlog-related signal integrity in the startup
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repo migration window; this fix decouples Agent Red CI from GT-KB session reporting so the migration window does not obscure GT-KB CI state

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: Owner selected "Repair Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-27 (repair surface)`: Owner selected "Fix probe defect first" - restore signal integrity before chasing CI failures.
- `S363 AskUserQuestion answer 2026-05-27 (probe fix path)`: Owner selected "Work-subject-aware probe" - fix `_testing_service_integrations` to respect active work subject when selecting query repo.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization covers this work per `GOV-RELIABILITY-FAST-LANE-001`; `allowed_mutation_classes=["source","test_addition","hook_upgrade"]` matches the proposal's source + test-only target_paths.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` requires the startup payload to report current operating state; this fix corrects the rollup's data-source-to-label coupling so the reported state matches the actual work subject. No new requirement is created. The variable `AGENT_RED_GITHUB_REPO` retains its existing meaning; a separate `GROUND_TRUTH_GITHUB_REPO` variable (already referenced at line 1726 of `scripts/session_self_initialization.py`) provides the GT-KB target.

### Reliability Fast-Lane Eligibility (per GOV-RELIABILITY-FAST-LANE-001)

This proposal qualifies for the reliability fast-lane standing authorization:

1. **Small single-concern defect fix**: one read-only state coupling bug in one probe function with a single-purpose remediation (work-subject-aware repo selection).
2. **Source + test-addition target paths only**: `scripts/session_self_initialization.py` (modified, source) + `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (NEW, test_addition). No `groundtruth.db` mutation, no protected-artifact mutation, no infrastructure mutation.
3. **No forbidden operations**: no deploy, no `git push --force`, no spec deletion (matches `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.forbidden_operations`).
4. **Bounded scope**: ~50-80 LOC change including tests; one diff, one PR-equivalent commit.
5. **Reversible**: rollback is a single revert of `scripts/session_self_initialization.py` + drop of the new test file.

## Proposed Scope

IP-1 - Work-subject reader (reuse existing canonical helper)

Reuse `scripts.workstream_focus.load_state(project_root)` rather than introduce a new helper. The function returns a `WorkSubjectState` dataclass whose `.current_subject` attribute is one of:

- `FOCUS_GTKB_INFRASTRUCTURE` (value `"gtkb_infrastructure"`) - GT-KB platform work; query the GT-KB repo
- `FOCUS_APPLICATION` (value `"application"`) - adopter/Agent Red work; query the Agent Red repo

The probe imports these constants directly to avoid string drift:

```
from scripts.workstream_focus import (
    FOCUS_APPLICATION,
    FOCUS_GTKB_INFRASTRUCTURE,
    load_state,
)
```

Fail-soft behavior: if `load_state()` raises or returns no recognized current_subject, default to `FOCUS_GTKB_INFRASTRUCTURE` (the canonical default for GT-KB checkouts).

IP-2 - Repo selection in `_latest_github_workflow_runs`

Modify `_latest_github_workflow_runs(project_root, gh_auth_status)` to select query repo based on active work subject (resolved via IP-1 helper):

- `current_subject == FOCUS_GTKB_INFRASTRUCTURE`: query `GROUND_TRUTH_GITHUB_REPO` env var; fall back to current git remote (which on a clean GT-KB clone points to `Remaker-Digital/groundtruth-kb`)
- `current_subject == FOCUS_APPLICATION`: query `AGENT_RED_GITHUB_REPO` env var; fall back to `agent-red` git remote if present, else return no_recent_run for all integrations (probe cannot determine target)
- Unknown / unrecognized value: default to `FOCUS_GTKB_INFRASTRUCTURE` branch (fail-soft)

The returned dict adds two new fields surfaced for downstream rendering:

- `queried_repo`: the actual repo slug used (e.g., `"Remaker-Digital/groundtruth-kb"`)
- `queried_work_subject`: the canonical work-subject value (e.g., `"gtkb_infrastructure"`) for audit transparency

These are NOT canonical state mutations; they are query-result metadata.

IP-3 - Rollup labeling

In the startup payload rendering functions (line 4162 etc.) and dashboard intelligence (line 2742 etc.):

- The current rollup label uses `{subject_label}` (work-subject-aware) but the data underneath was Agent Red regardless. After IP-2 the data matches the label. The label format is extended to surface `queried_repo` explicitly:

  `"<subject_label> Testing/tool rollup (queried repo: <queried_repo>): 0 failing, 6 manual, 13 ready/passing"`

- This makes the data source unambiguous regardless of which work subject is active and keeps a single label format across all sessions.

IP-4 - Regression test

`tests/scripts/test_testing_service_integrations_work_subject_aware.py` adds four tests using `FOCUS_GTKB_INFRASTRUCTURE` / `FOCUS_APPLICATION` constants imported from `scripts.workstream_focus`:

1. `test_gtkb_infrastructure_session_queries_gt_kb_repo` - fixture with `.claude/session/work-subject.json` containing `current_subject=gtkb_infrastructure`; mock env vars; assert query target is GT-KB repo (`GROUND_TRUTH_GITHUB_REPO` value or git-remote fallback)
2. `test_application_session_queries_agent_red_repo` - fixture with `current_subject=application`; mock env vars; assert query target is Agent Red repo
3. `test_missing_work_subject_defaults_to_gtkb_infrastructure` - no work-subject file (or unreadable); assert default branch is taken (queries GT-KB repo)
4. `test_rollup_label_includes_queried_repo` - assert the rendered rollup string includes the queried_repo identity

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 (correct rollup data source) | test_gtkb_infrastructure_session_queries_gt_kb_repo | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_gtkb_infrastructure_session_queries_gt_kb_repo -v | PASS |
| GOV-RELIABILITY-FAST-LANE-001 (fast-lane eligibility) | Inspection of target_paths + Reliability Fast-Lane Eligibility subsection | Manual review of this proposal section + verification that target_paths matches PAUTH allowed_mutation_classes | source + test_addition only, matches PAUTH |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each acceptance has a test) | All 4 regression tests | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v | All 4 PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (rollup labeling matches data source) | test_rollup_label_includes_queried_repo | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_rollup_label_includes_queried_repo -v | PASS |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 (Codex parity) | Manual: verify .codex/gtkb-hooks/session_start_dispatch.py inherits same scripts/ probe | grep `session_self_initialization` .codex/gtkb-hooks/session_start_dispatch.py | Codex hook calls into shared scripts/session_self_initialization.py; no fork |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (test creation lifecycle) | New test file creation | git status after impl shows new test file | tests/scripts/test_testing_service_integrations_work_subject_aware.py present |

## Acceptance Criteria

1. `_testing_service_integrations` reads active work subject via `scripts.workstream_focus.load_state(project_root)` (with fail-soft default to `FOCUS_GTKB_INFRASTRUCTURE`).
2. Query repo selection branches: `gtkb_infrastructure` -> `GROUND_TRUTH_GITHUB_REPO` or current git remote; `application` -> `AGENT_RED_GITHUB_REPO`.
3. Returned integration data includes `queried_repo` and `queried_work_subject` for downstream rendering.
4. Startup rollup label includes the `queried_repo` identity (e.g., "GT-KB Testing/tool rollup (queried repo: Remaker-Digital/groundtruth-kb): ...").
5. All 4 regression tests PASS via `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v`.
6. Live session re-run shows GT-KB CI when `current_subject=gtkb_infrastructure` (the actual current-commit failures on develop), not Agent Red CI.
7. WI-3409 transitions to `resolved` upon VERIFIED.

## Risks / Rollback

- Risk: work-subject branching adds a new failure mode in startup (if the work-subject file is malformed or contains an unrecognized value, the probe might select the wrong repo). Mitigation: fail-soft default to `FOCUS_GTKB_INFRASTRUCTURE` (the most common case); test coverage for missing/invalid file; reuse of canonical `load_state()` so this proposal does not introduce a new failure mode independent of the existing helper.
- Risk: changing the rollup label format may break downstream dashboard rendering that parses the label string. Mitigation: rendering code is read-only consumer of the integration dict, not the label string; the structured `queried_repo` field is the canonical source for downstream consumers.
- Risk: `GROUND_TRUTH_GITHUB_REPO` env var may not be set in all environments. Mitigation: fall back to current git remote (`git remote get-url origin`) which on a clean GT-KB clone points to `Remaker-Digital/groundtruth-kb`.
- Rollback: revert the patch to `scripts/session_self_initialization.py` and drop the new test file. Single-commit revert; no DB or protected-artifact state to unwind.

## Files Expected To Change

- `scripts/session_self_initialization.py` (modified: import workstream_focus constants + helper + probe + repo selection + rollup labeling)
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (NEW)

## Recommended Commit Type

`fix` - defect repair of a coupling/labeling issue in the startup probe; no new capability surface.
