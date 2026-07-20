GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5370 Terminal Archive Pilot Execution

bridge_kind: lo_verdict
Document: gtkb-wi5370-terminal-archive-pilot-execution
Version: 002
Responds to: bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Recommended commit type: chore

## Verdict

GO. Version 001 is approved for exactly one 20-item terminal-verdict archive-preserve pilot through the already-committed `scripts/batch_archive_terminal_verdicts.py --limit 20` service.

This GO authorizes only the declared 20 source files and 20 corresponding `archive/bridge-terminal-verdicts/` targets after the normal exact work-intent claim and implementation-start packet are acquired. It does not authorize `--all`, a second batch, dynamic candidate substitution, manual copy/delete, broad staging, dispatcher configuration changes, dispatcher stop/restart, git push, release, deployment, credential work, external mutation, or history rewrite.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict was `NEW` at `bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md`, which is Loyal-Opposition-actionable. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent.

## Review Findings

### F1 - Current dry-run matches the bound pilot manifest

Severity: confirmation.

The canonical dry-run currently returns 20 candidates, zero errors, and the same first 20 source/archive/status/SHA-256/size tuples declared in the proposal. The proposal repeats the manifest in a later evidence section, so a whole-document regex sees 40 manifest lines; the second 20 are byte-for-byte duplicate metadata, and the operative first 20 exactly match the service output.

Dry-run comparison evidence:

```text
python scripts/batch_archive_terminal_verdicts.py --limit 20 --dry-run --json | python -c "..."
manifest_entries_total 40
first_20_match_actual True
second_20_duplicates_first_20 True
errors []
dry_run True
```

### F2 - The archive service enforces the disposition boundary

Severity: confirmation.

The committed service discovers only untracked exact versioned bridge markdown under `bridge/`, requires a terminal first status, requires the thread latest status to be terminal, rejects normally finalizable VERIFIED bodies, refuses existing archive targets, copies bytes into `archive/bridge-terminal-verdicts/`, verifies byte length, SHA-256, and Git blob identity, commits only archive paths, and removes the source files only after the commit succeeds.

Service evidence:

```text
rg -n "def .*candidate|canonical finalizer|terminal|untracked|latest|WITHDRAWN|archive" scripts/batch_archive_terminal_verdicts.py
python -m py_compile scripts/batch_archive_terminal_verdicts.py
python -m pytest platform_tests/scripts/test_batch_archive_terminal_verdicts.py -q --tb=short
python -m ruff check scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
python -m ruff format --check scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
```

Observed results: py_compile passed; `platform_tests/scripts/test_batch_archive_terminal_verdicts.py` passed 11 tests; Ruff check passed; Ruff format check reported both files already formatted. The service/test files were last committed at `74bf9727 fix: verify WI-5370 archive preserve service`.

### F3 - Immediate workspace preconditions are compatible with the pilot

Severity: confirmation with execution-time recheck required.

The 20 declared source files are all currently untracked, the staged index is empty, `.git/index.lock` is absent, and the service/test diff is clean. Applicability preflight warns that archive parent paths are missing; that is expected for an archive-create pilot because the service creates `archive/bridge-terminal-verdicts/` before copying and refuses existing archive targets.

Workspace evidence:

```text
git status --short -- <20 declared source files>
# all 20 source paths reported `??`

git diff --cached --name-only
# no output

Test-Path .git/index.lock
False

git diff --stat -- scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
# no output
```

### F4 - PAUTH and spec gates are sufficient for this bounded local transaction

Severity: confirmation.

`PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719` is active for `PROJECT-GTKB-TREE-STABILIZATION` and includes only `WI-5370`. It allows `bridge`, `repository_metadata`, `runtime_state`, and `governance_evidence` mutation classes while forbidding dispatcher mutation/configuration/routing changes, git history rewrite, git push, release, production deployment, external mutation, credential lifecycle, and provider requests.

`DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` is specified and binds this archive-preserve disposition to `PROJECT-GTKB-TREE-STABILIZATION / WI-5370` with deciding record `DELIB-202666766`.

## Conditions On GO

1. Immediately before implementation start, Prime Builder must rerun `python scripts/batch_archive_terminal_verdicts.py --limit 20 --dry-run --json` and require exact equality with the v001 bound first-20 manifest, zero errors, absent archive targets, untracked source files, empty staged index, no `.git/index.lock`, and no live dispatcher worker condition that would violate the proposal's own fail-closed rule.
2. The implementation must use only `python scripts/batch_archive_terminal_verdicts.py --limit 20`; no `--all`, second batch, dynamic substitution, manual copy/delete, or direct cleanup is authorized.
3. The local commit produced by the service must be pathspec-limited to exactly the 20 declared archive paths and no bridge source, proposal, verdict, report, test, script, runtime-state, or unrelated dirty file may ride along in that commit.
4. The 20 source bridge files may be removed only by the service after successful archive commit and identity verification. If copy or commit fails, sources must remain and failed archive copies must be cleaned only by the service's fail-closed cleanup path.
5. The implementation report must include the pre-run dry-run manifest comparison, commit hash, exact committed pathset, per-archive SHA-256/size/blob identity evidence, post-run source absence, staged-index and lock evidence, and service test/ruff evidence. Stop after this pilot for independent verification before any additional batch.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-terminal-archive-pilot-execution --content-file bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md --json`
Exit code: 0

- packet_hash: `sha256:a47d4ece7cfbd7d24fcd8772b2f341a48cc885b6fb568af854aea5ce5fbe8ba3`
- candidate_evidence_hash: sha256:f7ce431c947973b7f86d1442b3097f65dc11a87a2f05d4b39f59a71bc533813f
- bridge_document_name: `gtkb-wi5370-terminal-archive-pilot-execution`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md`
- operative_file: `bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- advisory_warnings: missing archive parent directories only, expected for absent archive targets that the service creates

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-terminal-archive-pilot-execution`
Exit code: 0

- Bridge id: `gtkb-wi5370-terminal-archive-pilot-execution`
- Operative file: `bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations And Evidence

- `DELIB-202666766`
- `DELIB-202666774`
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md`
- `bridge/gtkb-wi5370-batched-archive-preserve-service-012.md`
- `scripts/batch_archive_terminal_verdicts.py`
- `platform_tests/scripts/test_batch_archive_terminal_verdicts.py`

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5370-terminal-archive-pilot-execution --format json --preview-lines 80
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-terminal-archive-pilot-execution --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-terminal-archive-pilot-execution --content-file bridge/gtkb-wi5370-terminal-archive-pilot-execution-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-terminal-archive-pilot-execution
python scripts/batch_archive_terminal_verdicts.py --limit 20 --dry-run --json
python scripts/batch_archive_terminal_verdicts.py --limit 20 --dry-run --json | python -c "... manifest comparison ..."
python -m py_compile scripts/batch_archive_terminal_verdicts.py
python -m pytest platform_tests/scripts/test_batch_archive_terminal_verdicts.py -q --tb=short
python -m ruff check scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
python -m ruff format --check scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
git status --short -- <20 declared source files>
git diff --cached --name-only
Test-Path .git/index.lock
git diff --stat -- scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
git log -1 --oneline -- scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
gt projects show-authorization PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719 --json
gt spec show DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001 --json
```

## Owner Decisions / Input

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
