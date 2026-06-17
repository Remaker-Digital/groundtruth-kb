NEW

# gtkb-windows-git-warnings-fix — Windows Git configuration warning noise fix

bridge_kind: prime_proposal
Document: gtkb-windows-git-warnings-fix
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-17 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: 72752cd1-a8d7-4110-81b0-5a3867f35eb3
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity IDE session

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4394-WINDOWS-GIT-WARNINGS
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4394

target_paths: ["scripts/_env.py", "groundtruth-kb/src/groundtruth_kb/__init__.py", "platform_tests/scripts/test_git_warnings_env.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves WI-4394 by configuring global Git environment overrides inside the Python parent process environment to suppress unreadable global/system configuration and root directory warnings on Windows. Specifically, it will set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=NUL` (or `NUL` on Windows / `/dev/null` on Unix) globally in `scripts/_env.py` and `groundtruth-kb/src/groundtruth_kb/__init__.py`.

Currently, Git CLI commands run via Python subprocesses on Windows frequently emit warnings like "unable to access C:\Users\micha/.config/git/ignore: Permission denied" or "could not open directory $cache/: Permission denied". These warnings clutter verification loops, tests, and git status output, potentially leading agents down irrelevant permission-fixing paths. By setting these env variables in the parent environment, all spawned Git subprocesses inherit them and suppress this noise, while real worktree changes remain visible.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — This proposal is filed as a NEW implementation proposal on the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Links specifications to verify compliance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project linkage header fields are defined at the top.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification plan maps specs to tests.
- `GOV-STANDING-BACKLOG-001` — Work item WI-4394 is tracked in the unified backlog.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Bounded implementation authorization is provided by PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4394-WINDOWS-GIT-WARNINGS.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (Advisory) — This proposal is recorded as a project artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (Advisory) — Verification transitions are tracked per trigger.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (Advisory) — Follows artifact-oriented governance.

## Prior Deliberations

- `DELIB-20260616-MAY29-HYGIENE-WI-4394-AUTHORIZE` — Owner selected Option A to move WI-4394 to PROJECT-GTKB-MAY29-HYGIENE and authorize it.

## Owner Decisions / Input

- `DELIB-20260616-MAY29-HYGIENE-WI-4394-AUTHORIZE` — Owner authorized this implementation scope in conversation 72752cd1-a8d7-4110-81b0-5a3867f35eb3.

## Requirement Sufficiency

- Existing requirements sufficient — Covered by GOV-RELIABILITY-FAST-LANE-001 and GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001.

## Spec-Derived Verification Plan

| Spec / Concern | Target Test / Verification Command | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-windows-git-warnings-fix` | PASS (applicability preflight checks pass) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-windows-git-warnings-fix` | PASS (clause preflight checks pass) |
| Environment configuration | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_warnings_env.py -q --no-header` | PASS (asserts that `GIT_CONFIG_NOSYSTEM` and `GIT_CONFIG_GLOBAL` are set correctly in `os.environ` after import) |

## Risk / Rollback

- **Risk**: Very low. Only sets environment variables for Git config overrides, preventing Git from loading system/global configuration files. This is standard practice in isolated/reproducible test environments to avoid local machine configuration leakage.
- **Rollback**: `git checkout HEAD -- scripts/_env.py groundtruth-kb/src/groundtruth_kb/__init__.py`

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-windows-git-warnings-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
