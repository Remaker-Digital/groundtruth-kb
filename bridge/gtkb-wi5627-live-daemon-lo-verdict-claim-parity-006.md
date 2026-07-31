GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5627 Live Daemon LO Verdict Claim Parity

bridge_kind: lo_verdict
Document: gtkb-wi5627-live-daemon-lo-verdict-claim-parity
Version: 006
Responds to: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md
Date: 2026-07-19 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

## Verdict

GO. Version 005 answers the version 004 blocker by abandoning noncanonical `.gtkb-state` scratch evidence as a load-bearing proof and requiring the next implementation report to carry a new append-only canonical hunk patch plus a self-contained hash-ledger reconstruction. It also identifies a real in-scope live-daemon defect: after leases and LO verdict claims are acquired against `selected`, `_execute_live_spawns` currently reverses the batch before provider spawn, so worker primary/correlation metadata can diverge from the governed lease and claim order.

This GO authorizes only the exact two-path WI-5627 source/test implementation required to preserve canonical selected-document order through the live daemon claim and spawn lifecycle, plus the canonical hunk evidence needed to verify that implementation. It does not authorize dispatcher configuration, runtime-state, lease-file, routing, ranking, eligibility, allowance, role, identity, provider configuration, process-control, live-worker, MemBase, database, credential, deployment, release, push, destructive-cleanup, or unrelated dirty-byte mutation.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `TEST-11672`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-HARNESS-ISOLATION-001`

## Applicability Preflight

- bridge_document_name: `gtkb-wi5627-live-daemon-lo-verdict-claim-parity`
- content_file: `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md`
- packet_hash: `sha256:26b7010a3fa9a8523f840cd5ce189bb344b97585d740a93aa5172f48e7f900d6`
- candidate_evidence_hash: `sha256:059031662b7a119b9059c2530feb3618119b2f87e212a28bdd6c4e86e2075999`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

- Mandatory clause gate against `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md`: PASS.
- Clauses evaluated: 5.
- must_apply: 3.
- may_apply: 2.
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps: 0.

## First-Line Role Eligibility and Independence

- Active writer role: Loyal Opposition, per owner transcript role assignment in this interactive session.
- Authorized status token: `GO`.
- Proposal author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Independence result: PASS.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes this bounded reliability repair lane while preserving bridge, claim, implementation-start, independent verification, and focused-commit gates.
- `DELIB-202666762` established the dispatcher-owned pre-launch LO verdict-claim lifecycle that WI-5627 applies to the production daemon path.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires canonical bridge evidence to avoid noncanonical scratch and session-state dependencies.
- `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-004.md` is the direct NO-GO this revision answers.

## Evidence Reviewed

- Latest bridge state before this verdict: `REVISED` at `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md`.
- v005 proposal SHA256: `7893717F3018D3FDAA7A26855545AF0EC5BA9BAAF16F45B7916C6F8D23DB3B11`.
- Current `scripts/gtkb_dispatcher_daemon.py` still contains `spawn_items = list(reversed(selected))` immediately before `_spawn_harness`, after document leases and LO verdict claims are acquired on `selected`.
- Current diff stat for the two declared targets is large and commingled: 965 insertions and 4 deletions across `scripts/gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.
- Historical patch artifact exists at `bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch`, SHA256 `96870F21538BC7AA57E553B57FC00C96AB008E905DD1EE864464EBD15ECEFF4F`, with numstat 61/0 for `scripts/gtkb_dispatcher_daemon.py` and 360/0 for `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.
- Reverse applicability of the historical hunk patch against current bytes exits 0, but v005 correctly requires a new canonical evidence package for the revised implementation rather than relying on prior `.gtkb-state` scratch reconstruction.

## Positive Findings

1. The v004 blocker is directly addressed. The revised proposal no longer asks LO to accept a forward proof that depends on a missing noncanonical scratch directory; it requires a new append-only canonical hunk patch and self-contained hash ledger in the next report.
2. The added order-preservation defect is real and in scope. The live daemon currently claims and leases one order, then reverses the selected batch at the provider-spawn boundary. That can split primary/correlation metadata from lease and claim metadata.
3. The target set remains exact and bounded to the two already-approved daemon source/test paths.
4. The verification plan correctly requires ordered-list equality, not set equality, so the regression should fail on the current reversal and pass only when selection, leases, claims, spawn items, primary id, environment, and telemetry align.

## Implementation Conditions

- Acquire fresh WI-5627 work-intent and schema-v3 implementation-start authorization for exactly:
  - `scripts/gtkb_dispatcher_daemon.py`
  - `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- Preserve one canonical order throughout:
  - `spawn_items == selected_documents == document_lease_slugs == verdict_claim_slugs`
  - first slug equals `primary_bridge_id`, `GTKB_DISPATCH_PRIMARY_BRIDGE_ID`, and launch/result telemetry bridge id fields.
- Produce a new append-only canonical hunk patch under `bridge/hunks/` for the revised WI-5627 implementation evidence.
- The next report must include patch path, SHA256, Git blob id when available, byte size, numstat, per-target pre/post SHA256, forward applicability against reconstructed preimages, reverse applicability against post-implementation bytes, and post-forward SHA256 equality.
- Do not cite `.gtkb-state`, harness-local scratch, temporary reconstruction paths, or other noncanonical session state as load-bearing evidence.
- Whole-file staging/finalization of either target remains prohibited while the files contain foreign dirty bytes; use hunk-only finalization or an equivalent governed exact-hunk path.
- Do not touch dispatcher configuration, runtime JSON/state, lease files, provider routes, harness state, credentials, deployment, release, push, destructive cleanup, MemBase, or `groundtruth.db`.

## Commands Executed

```powershell
& .\groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi5627-live-daemon-lo-verdict-claim-parity --format json --preview-lines 400
```

Result: full chain read; latest `REVISED` at v005.

```powershell
& .\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --content-file bridge\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md --json
```

Result: PASS; packet hash `sha256:26b7010a3fa9a8523f840cd5ce189bb344b97585d740a93aa5172f48e7f900d6`; missing required/advisory specs `[]`; blocking errors `[]`.

```powershell
& .\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --content-file bridge\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md
```

Result: PASS; 5 clauses evaluated, 3 must-apply, 0 evidence gaps in must-apply clauses, 0 blocking gaps.

```powershell
rg -n "revers|selected|spawn_items|_execute_live_spawns|primary_bridge_id|GTKB_DISPATCH_PRIMARY_BRIDGE_ID|_spawn_harness|verdict" scripts\gtkb_dispatcher_daemon.py
```

Result: current source shows `spawn_items = list(reversed(selected))` immediately before `_spawn_harness`, after lease and verdict-claim acquisition on `selected`.

```powershell
git diff --stat -- scripts\gtkb_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py
git diff --check -- scripts\gtkb_dispatcher_daemon.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py
```

Result: large commingled target diff; diff-check exit 0 with only LF-to-CRLF warnings.

```powershell
Get-FileHash bridge\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-005.md -Algorithm SHA256
Get-FileHash bridge\hunks\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch -Algorithm SHA256
git apply --numstat bridge\hunks\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
git apply -R --check --whitespace=error bridge\hunks\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
```

Result: proposal SHA256 `7893717F3018D3FDAA7A26855545AF0EC5BA9BAAF16F45B7916C6F8D23DB3B11`; historical hunk SHA256 `96870F21538BC7AA57E553B57FC00C96AB008E905DD1EE864464EBD15ECEFF4F`; numstat 61/0 and 360/0; reverse check exit 0.

## Disposition

WI-5627 may proceed under the governed bridge/claim/start path for the exact two target files and the canonical hunk evidence required by this GO. No dispatcher configuration changes are authorized.
