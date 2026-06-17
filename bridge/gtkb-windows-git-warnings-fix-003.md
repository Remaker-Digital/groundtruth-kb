REVISED

# gtkb-windows-git-warnings-fix — Windows Git configuration warning noise fix

bridge_kind: prime_proposal
Document: gtkb-windows-git-warnings-fix
Version: 003
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

This revised proposal resolves WI-4394 by redirecting Windows Git configuration path queries to a safe temporary location, avoiding unreadable user/global-ignore configuration warnings and fatal environment crashes.

Initially, we proposed setting `GIT_CONFIG_GLOBAL=NUL`. However, as identified by the Loyal Opposition in `gtkb-windows-git-warnings-fix-002.md` (NO-GO), setting `GIT_CONFIG_GLOBAL=NUL` on Windows causes fatal Git execution crashes (unknown error reading configuration files) and bypasses user identity resolution (`user.name`/`user.email`), blocking commits.

To resolve these defects safely:
1. We keep `GIT_CONFIG_NOSYSTEM=1` (suppresses system-level config warnings).
2. We drop `GIT_CONFIG_GLOBAL=NUL`.
3. If running on Windows, we set `XDG_CONFIG_HOME` in `os.environ` to a safe, writeable temporary directory (using `tempfile.gettempdir()`). This redirects Git's search for user-specific configurations (like `git/ignore`) to a safe directory under the temp profile, completely suppressing unreadable global configuration/ignore file warnings without bypassing `.gitconfig` in `USERPROFILE` or breaking git identity resolution.

These overrides will be applied globally at module load time in `scripts/_env.py` and `groundtruth-kb/src/groundtruth_kb/__init__.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — This proposal is filed as a REVISED implementation proposal on the file bridge.
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
- `gtkb-windows-git-warnings-fix-002.md` (NO-GO) — Loyal Opposition review identifying `GIT_CONFIG_GLOBAL=NUL` crash and author identity issue.

## Owner Decisions / Input

- `DELIB-20260616-MAY29-HYGIENE-WI-4394-AUTHORIZE` — Owner authorized this implementation scope in conversation 72752cd1-a8d7-4110-81b0-5a3867f35eb3.

## Requirement Sufficiency

- Existing requirements sufficient — Covered by GOV-RELIABILITY-FAST-LANE-001 and GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001.

## Spec-Derived Verification Plan

| Spec / Concern | Target Test / Verification Command | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-windows-git-warnings-fix` | PASS (applicability preflight checks pass) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-windows-git-warnings-fix` | PASS (clause preflight checks pass) |
| Environment configuration | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_warnings_env.py -q --no-header` | PASS (asserts that `GIT_CONFIG_NOSYSTEM` is "1", `GIT_CONFIG_GLOBAL` is not mutated, and `XDG_CONFIG_HOME` is set to a safe temporary location on Windows) |

## Risk / Rollback

- **Risk**: Very low. Redirection of `XDG_CONFIG_HOME` to a writeable temp dir is safe and only affects user-specific Git search paths, leaving repository-level and global user-identity configurations intact.
- **Rollback**: `git checkout HEAD -- scripts/_env.py groundtruth-kb/src/groundtruth_kb/__init__.py`

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-windows-git-warnings-fix`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
