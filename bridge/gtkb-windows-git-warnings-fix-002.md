NO-GO

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 841db6b6-8c9b-4b6f-a465-d28e782ece9d
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity IDE session; Loyal Opposition proposal review

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4394-WINDOWS-GIT-WARNINGS
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4394

# Loyal Opposition Review - Windows Git configuration warning noise fix Proposal Review

bridge_kind: lo_verdict
Document: gtkb-windows-git-warnings-fix
Version: 002
Reviewer: Loyal Opposition (Antigravity)
Date: 2026-06-17 UTC
Verdict: NO-GO
Responds to: bridge/gtkb-windows-git-warnings-fix-001.md

## Verdict

NO-GO. The proposal to suppress Git configuration warning noise on Windows by setting `GIT_CONFIG_GLOBAL=NUL` introduces critical runtime crashes and breaks developer commit workflows.

## Applicability Preflight

- packet_hash: `sha256:863ed80256ef22e7979a441997532b19c22cb6fd8750e4d32445088779ee154f`
- bridge_document_name: `gtkb-windows-git-warnings-fix`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-windows-git-warnings-fix-001.md`
- operative_file: `bridge/gtkb-windows-git-warnings-fix-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-windows-git-warnings-fix`
- Operative file: `bridge\gtkb-windows-git-warnings-fix-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260616-MAY29-HYGIENE-WI-4394-AUTHORIZE` — Owner authorized moving WI-4394 to PROJECT-GTKB-MAY29-HYGIENE and starting proposal phase.

## Findings

### FINDING-P1-001 - GIT_CONFIG_GLOBAL=NUL fatal crash on Windows

- **Observation**: Setting `GIT_CONFIG_GLOBAL=NUL` in `os.environ` on Windows causes all downstream git subprocesses that access configuration files to crash immediately with:
  `fatal: unknown error occurred while reading the configuration files`
  This occurs because Windows Git treats `NUL` as a path and fails when attempting to read/parse the null device.
- **Deficiency Rationale**: The proposed design would completely break Git integration in GroundTruth-KB when run on Windows, causing all git commands to throw fatal errors.
- **Proposed Solution**: Drop the use of `GIT_CONFIG_GLOBAL=NUL` on Windows.
- **Prime Builder Implementation Context**: Ensure the environment variables set in `scripts/_env.py` and `groundtruth-kb/src/groundtruth_kb/__init__.py` do not write `GIT_CONFIG_GLOBAL=NUL`.

### FINDING-P1-002 - Bypassing Global Config Blocks User Identity Resolution

- **Observation**: Even if setting the global config variable to an empty/non-existent file worked (e.g. by setting it to a temporary dummy path), doing so completely hides the user's global `user.name` and `user.email` configuration. In repositories without locally defined author information, this causes all git commits (such as `gt sweep-commit` or manual commits run in the harness context) to fail with `Author identity unknown` / `fatal: unable to auto-detect email address`.
- **Deficiency Rationale**: The proposed suppression breaks necessary commit write-paths unless developers duplicate their global identity configuration into local `.git/config` files for every worktree/repository.
- **Proposed Solution**: Keep `GIT_CONFIG_NOSYSTEM=1` (which is safe), but instead of overriding `GIT_CONFIG_GLOBAL`, suppress the target permission warning (`unable to access C:\Users\micha/.config/git/ignore: Permission denied`) by setting `XDG_CONFIG_HOME` to a safe, writeable temporary directory (e.g., `C:\Users\micha\AppData\Local\Temp` or a directory under the temp profile) in `os.environ`. This redirects lookups for `git/ignore` to a safe writeable path, preventing sandbox permission warnings while still allowing Git to successfully read `.gitconfig` from `USERPROFILE` (resolving the global user identity).
- **Prime Builder Implementation Context**: Implement `XDG_CONFIG_HOME` redirection rather than `GIT_CONFIG_GLOBAL` overrides.

## Required Revisions

1. **Drop `GIT_CONFIG_GLOBAL=NUL`**: Remove `GIT_CONFIG_GLOBAL` mutation from `scripts/_env.py` and `groundtruth-kb/src/groundtruth_kb/__init__.py`.
2. **Implement `XDG_CONFIG_HOME` Redirection**: Configure the parent Python process environment to set `XDG_CONFIG_HOME` to a writeable path (e.g. using `tempfile.gettempdir()`) if on Windows.
3. **Update Test Cases**: Update the test plan and assertions in `platform_tests/scripts/test_git_warnings_env.py` to assert that `XDG_CONFIG_HOME` is set to a safe temporary location and `GIT_CONFIG_NOSYSTEM` is `1`.

## Commands Executed

```powershell
cmd /c "set GIT_CONFIG_GLOBAL=NUL && git commit --dry-run -m test"
cmd /c "set GIT_CONFIG_GLOBAL=C:\nonexistent_file && git commit --dry-run -m test"
cmd /c "set GIT_CONFIG_GLOBAL=C:\nonexistent_file && git var GIT_AUTHOR_IDENT"
cmd /c "git config -l --show-origin"
```

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
