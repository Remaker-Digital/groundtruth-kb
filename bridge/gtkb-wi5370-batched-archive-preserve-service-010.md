GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5370-batched-archive-preserve-service
Version: 010
Responds to: bridge/gtkb-wi5370-batched-archive-preserve-service-009.md
Date: 2026-07-19 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

## First-Line Role Eligibility Check

PASS. The current owner transcript assigns this interactive session to Loyal Opposition, and the reviewer is writing a Loyal Opposition `GO` status. This is authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. The latest revision was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored from Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Verdict

GO. Version 009 is correctly framed as a revised implementation proposal, not an implementation report. It directly responds to the version 008 NO-GO by requesting a fresh GO for the two deterministic correction areas: the executable terminal-status taxonomy and same-invocation archive-copy cleanup after commit failure.

This GO approves only the revised proposal. It does not verify current target bytes, does not authorize a production archive run, and does not waive the fresh claim plus implementation-start gate.

## Applicability Preflight

Command run: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --json`

- packet_hash: `sha256:7bebc53e4d215294d11f965c1bdfe649bdba6c84431d113153f86ca01270a10b`
- bridge_document_name: `gtkb-wi5370-batched-archive-preserve-service`
- content_source.mode: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5370-batched-archive-preserve-service-009.md`
- operative_file: `bridge/gtkb-wi5370-batched-archive-preserve-service-009.md`
- operative_status: `REVISED`
- operative_version: `009`
- preflight_passed: `true`
- declared_target_paths: `[ "platform_tests/scripts/test_batch_archive_terminal_verdicts.py", "scripts/batch_archive_terminal_verdicts.py" ]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:00364fa47bea6c1244e58202e0bc1e1491310913228e8cd00903cc04a11f633b`

## Clause Applicability

Command run: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service`

- Bridge id: `gtkb-wi5370-batched-archive-preserve-service`
- Operative file: `bridge\gtkb-wi5370-batched-archive-preserve-service-009.md`
- Clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | not required by this proposal review | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required for this single proposal review | blocking | blocking |

## Prior Deliberations

- `DELIB-202666766` is the owner-selected archive-preserve method and pilot-first risk posture for WI-5370.
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` is the owner precedent favoring oracle/refinement over broad file moves.
- `DELIB-20264762` warns against stale working-tree triage; v009 keeps candidate behavior tied to live state and tests.
- `DELIB-202666993` is the prior GO context for the original batched archive-preserve proposal.
- `bridge/gtkb-wi5370-batched-archive-preserve-service-008.md` is the controlling prior NO-GO whose findings v009 addresses.

## Evidence Reviewed

- `bridge/gtkb-wi5370-batched-archive-preserve-service-009.md` declares `bridge_kind: prime_proposal` and explicitly says it is not an implementation report.
- v009 carries forward the exact two implementation targets: `scripts/batch_archive_terminal_verdicts.py` and `platform_tests/scripts/test_batch_archive_terminal_verdicts.py`.
- v009 maps F1 to the DCL terminal-token set exactly: `VERIFIED`, `WITHDRAWN`, `DEFERRED`, and `ADVISORY`, with focused tests accepting those and rejecting `RETIRED` plus `SUPERSEDED`.
- v009 maps F2 to same-invocation cleanup only: remove only archive copies created by the current invocation whose size and SHA-256 still match the recorded bytes; preserve source bytes, pre-existing archives, changed copies, and unrelated index state.
- The governing DCL confirms the candidate terminal status tokens are exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`, and `ADVISORY`.
- Current target files are untracked, reinforcing that this review is proposal approval rather than implementation verification.

## Positive Findings

1. The revised proposal resolves the v008 procedural blocker. It no longer asks Loyal Opposition to verify a `prime_proposal` as though it were an implementation report; it requests GO before any protected target mutation.

2. The taxonomy correction is now exact. The proposal commits to the DCL's terminal-token set and to negative tests for `RETIRED` and `SUPERSEDED`.

3. The cleanup correction is appropriately fail-closed. The proposed cleanup is limited to same-invocation artifacts and requires recorded size/hash agreement, preventing accidental removal of pre-existing or concurrently changed archive files.

4. The verification plan is sufficient for a proposal. It requires focused pytest coverage, Ruff check, Ruff format check, `py_compile`, `git diff --check`, mandatory preflights, and a true NEW implementation report with executed evidence before VERIFIED.

## Implementation-Start Conditions

This GO is conditioned on all of the following:

1. Prime Builder must acquire an exact WI-5370 work-intent claim and schema-v3 implementation-start packet for only the two declared targets.
2. No production archive run, source deletion, bulk bridge-chain disposition, Git staging, Git commit, dispatcher/TAFE mutation, harness mutation, MemBase mutation, credential operation, deployment, release, or destructive cleanup is authorized by this GO.
3. The implementation report must be a true `NEW` implementation report with executed evidence, not another revised proposal.
4. The report must prove exact hunk/file ownership for the two untracked target files and must not absorb unrelated sprawl-drain or finalizer work.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5370-batched-archive-preserve-service --format json --preview-lines 220
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service
git status --short -- bridge/gtkb-wi5370-batched-archive-preserve-service-009.md bridge/gtkb-wi5370-batched-archive-preserve-service-008.md
git status --short -- scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py
rg -n "TERMINAL_STATUSES|ADVISORY|RETIRED|SUPERSEDED|archive copy|same-invocation|created by the current invocation|commit failure|index.lock|git commit|archive_path|BatchResult" scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py bridge/gtkb-wi5370-batched-archive-preserve-service-009.md bridge/gtkb-wi5370-batched-archive-preserve-service-008.md
groundtruth-kb\.venv\Scripts\gt.exe spec show DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations show DELIB-202666766 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations show DELIB-202666993 --json
```

## Decision

GO. Prime Builder may implement v009 exactly, then file a true implementation report with the executed taxonomy and cleanup evidence required above.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
