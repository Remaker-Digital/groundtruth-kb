NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-s363-work-subject-aware-probe-fix
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal - Work-subject-aware testing/tool integration probe

bridge_kind: prime_proposal
Document: gtkb-work-subject-aware-testing-integration-probe
Version: 001 (NEW)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3409

target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_testing_service_integrations_work_subject_aware.py"]

## Claim

The `_testing_service_integrations` probe in `scripts/session_self_initialization.py` unconditionally queries `AGENT_RED_GITHUB_REPO` (resolved to `https://github.com/mike-remakerdigital/agent-red` per `.env.local`) regardless of the active work subject. Sessions whose `Active Work Subject: GT-KB Infrastructure Focus` (e.g., the default GT-KB platform session) see Agent Red CI labeled as "GT-KB Testing/tool rollup" in the startup banner and dashboard intelligence — a framing/coupling defect. The fix: read active work subject from `.claude/session/work-subject.json` and select query repo accordingly. Adds `queried_repo` surfacing to the rollup label so the data source is unambiguous.

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

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/session_self_initialization.py`
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/REVISED/GO/NO-GO/VERIFIED workflow
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the testing/tool integration rollup is a startup-payload artifact; this fix corrects the data-source-to-label coupling
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites relevant cross-cutting specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps acceptance criteria to specific test commands
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above with active PAUTH
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion (Owner Decisions section)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`
- `GOV-SESSION-SELF-INITIALIZATION-001` - the testing/tool rollup is a startup-payload field this fix repairs
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the change is read-only at session start; parity preserved (Codex startup hook will inherit the same behavior)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates a durable test artifact (work-subject-aware regression test)

## Prior Deliberations

- `S363 backlog review session - Repair Testing/Tool Integrations focus` - owner selected option B from the startup focus menu; subsequent AUQ chose "Work-subject-aware probe" as the fix path. (No DELIB ID yet; this proposal IS the session-anchored record.)
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - backlog source-of-truth governance; this fix improves backlog-related signal integrity in the startup
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repo migration window; this fix decouples Agent Red CI from GT-KB session reporting so the migration window doesn't obscure GT-KB CI state
- `DELIB-0876` - durable session work subject precedent; `.claude/session/work-subject.json` is the canonical state file this fix reads from

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: Owner selected "Repair Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-27 (repair surface)`: Owner selected "Fix probe defect first" — restore signal integrity before chasing CI failures.
- `S363 AskUserQuestion answer 2026-05-27 (probe fix path)`: Owner selected "Work-subject-aware probe" — fix `_testing_service_integrations` to respect active work subject when selecting query repo.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization covers this work; allowed_mutation_classes=["source","test_addition","hook_upgrade"] matches the proposal's source + test target_paths.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` requires the startup payload to report current operating state; this fix corrects the rollup's data-source-to-label coupling so the reported state matches the actual work subject. No new requirement is created. The variable `AGENT_RED_GITHUB_REPO` retains its existing meaning; a separate `GROUND_TRUTH_GITHUB_REPO` variable (already referenced at line 1726 of `scripts/session_self_initialization.py`) provides the GT-KB target.

## Proposed Scope

IP-1 - Work-subject reader helper

Add (or reuse) `_active_work_subject(project_root: Path) -> str` in `scripts/session_self_initialization.py`. Behavior:
- Reads `.claude/session/work-subject.json`
- Returns canonical value: `"GT-KB"` (default), `"application"`, or `"GT-KB+application"`
- Returns `"GT-KB"` (default) on missing file, invalid JSON, or unrecognized value (fail-soft)

If a comparable helper already exists in `scripts/workstream_focus.py`, reuse it rather than duplicate.

IP-2 - Repo selection in `_latest_github_workflow_runs`

Modify `_latest_github_workflow_runs(project_root, gh_auth_status)` to select query repo based on active work subject:
- `work_subject == "GT-KB"`: query `GROUND_TRUTH_GITHUB_REPO` env var; fall back to current git remote (which should be Remaker-Digital/groundtruth-kb)
- `work_subject == "application"`: query `AGENT_RED_GITHUB_REPO` env var; fall back to `agent-red` git remote if present, else no query
- `work_subject == "GT-KB+application"`: query GT-KB repo (default); future enhancement could surface both as dual rollups (out of scope for this slice)

The returned dict adds a `queried_repo` and `queried_work_subject` field surfaced for downstream rendering.

IP-3 - Rollup labeling

In the startup payload (`scripts/session_self_initialization.py` rendering functions) and dashboard intelligence:
- Change `"GT-KB Testing/tool rollup"` static label to include `queried_repo` from the integration data
- Final form example: `"Testing/tool rollup (queried repo: Remaker-Digital/groundtruth-kb): 0 failing, 6 manual, 13 ready/passing"`

This makes the data source unambiguous regardless of which work subject is active.

IP-4 - Regression test

`tests/scripts/test_testing_service_integrations_work_subject_aware.py` adds three tests:
1. `test_gt_kb_session_queries_gt_kb_repo` - fixture work-subject GT-KB; mock env vars; assert query target is GT-KB repo
2. `test_application_session_queries_agent_red_repo` - fixture work-subject application; mock env vars; assert query target is Agent Red repo
3. `test_missing_work_subject_defaults_to_gt_kb` - no work-subject file; assert default behavior queries GT-KB repo (fail-soft)
4. `test_rollup_label_includes_queried_repo` - assert the rendered rollup string includes the queried_repo identity

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 (correct rollup data source) | test_gt_kb_session_queries_gt_kb_repo | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_gt_kb_session_queries_gt_kb_repo -v | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each acceptance has a test) | All 4 regression tests | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v | All PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (rollup labeling matches data source) | test_rollup_label_includes_queried_repo | pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py::test_rollup_label_includes_queried_repo -v | PASS |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 (Codex parity) | Manual: verify .codex/gtkb-hooks/session_start_dispatch.py inherits same scripts/ probe | Read .codex/gtkb-hooks/session_start_dispatch.py | Calls into shared scripts/session_self_initialization.py; no fork |

## Acceptance Criteria

1. `_testing_service_integrations` reads active work subject from `.claude/session/work-subject.json` (with fail-soft default).
2. Query repo selection branches: GT-KB session -> GROUND_TRUTH_GITHUB_REPO or current git remote; application session -> AGENT_RED_GITHUB_REPO.
3. Returned integration data includes `queried_repo` and `queried_work_subject` for downstream rendering.
4. Startup rollup label includes the queried_repo identity (e.g., "Testing/tool rollup (queried repo: Remaker-Digital/groundtruth-kb): ...").
5. All 4 regression tests PASS via `pytest tests/scripts/test_testing_service_integrations_work_subject_aware.py -v`.
6. Live session re-run shows GT-KB CI when work_subject=GT-KB (the actual current-commit failures on develop), not Agent Red CI.
7. WI-3409 transitions to `resolved` upon VERIFIED.

## Risks / Rollback

- Risk: work-subject branching adds a new failure mode in startup (if the work-subject file is malformed or contains an unrecognized value, the probe might select the wrong repo). Mitigation: fail-soft default to GT-KB (the most common case); test coverage for missing/invalid file.
- Risk: changing the rollup label format may break downstream dashboard rendering that parses the label string. Mitigation: rendering code is read-only consumer of the integration dict, not the label string; the structured `queried_repo` field is the canonical source.
- Risk: GROUND_TRUTH_GITHUB_REPO env var may not be set in all environments. Mitigation: fall back to current git remote (`git remote get-url origin`) which on a clean GT-KB clone points to Remaker-Digital/groundtruth-kb.
- Rollback: revert the patch to `scripts/session_self_initialization.py` and drop the new test file. Single-commit revert.

## Files Expected To Change

- `scripts/session_self_initialization.py` (modified: probe + repo selection + rollup labeling)
- `tests/scripts/test_testing_service_integrations_work_subject_aware.py` (NEW)

## Recommended Commit Type

`fix` - defect repair of a coupling/labeling issue in the startup probe; no new capability surface.
