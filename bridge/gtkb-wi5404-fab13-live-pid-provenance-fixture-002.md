GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5404-fab13-live-pid-provenance-fixture
Version: 002
Responds to: bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Proposal Verdict - GO - WI-5404 FAB-13 Live PID Provenance Fixture

## Verdict

GO. The proposal is appropriately narrow and addresses a real stale-fixture defect: the FAB-13 live-artifact retention test writes a live PID and log without the production-required create-time sidecar, while production liveness now requires PID create-time provenance. The target scope is limited to the fixture hunk plus a canonical hunk-patch evidence artifact, with no dispatcher, TAFE, harness, production-runtime, credential, deployment, release, or Git-history mutation authorized.

## Conditions

1. Modify only `platform_tests/scripts/test_fab13_retention_policy.py::test_dispatch_runs_prune_preserves_live_pid_artifacts` for WI-5404 behavior, plus `bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch` as the declared hunk artifact.
2. Write the `live.create_time_epoch` sidecar using the production-compatible current-process create-time value, preferably `trigger._pid_create_time_epoch(os.getpid())`, and fail closed in the implementation report if the helper cannot return a usable value.
3. Do not weaken or bypass `scripts/dispatcher_runtime.py` PID liveness or provenance checks.
4. Preserve concurrent WI-5396 exact-root hunks in `platform_tests/scripts/test_fab13_retention_policy.py`; the hunk patch must contain only the WI-5404 fixture delta against HEAD and exclude foreign hunks.
5. The implementation report must include patch path, SHA-256, byte size, preimage/postimage evidence, target hashes, and focused test/static gate results.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `GO`, a Loyal Opposition proposal-review status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Proposal author session context: `019f6668-9974-7d72-a456-826f9a67e627`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5404-fab13-live-pid-provenance-fixture --content-file bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md --json
```

Result:

- packet_hash: `sha256:72624b60f9b7f3db7b4b76edd40a5319615cce78e0115c83484d28b5ac14ebc5`
- bridge_document_name: `gtkb-wi5404-fab13-live-pid-provenance-fixture`
- content_file: `bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md`
- operative_file: `bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:76810d97bf690ad20c8ffa185b27337841eadc1c2a0b81735aac52f3bff66b81`

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5404-fab13-live-pid-provenance-fixture
```

Result:

- Bridge id: `gtkb-wi5404-fab13-live-pid-provenance-fixture`
- Operative file: `bridge\gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: 0

## Prior Deliberations

- `DELIB-202666190` - FAB-13 related verdict rationale carried by the proposal.
- `DELIB-202666188` - WI-5220 dispatcher test fixture parity VERIFIED finalization context.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded owner-authorized defect-remediation envelope.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher-configuration mutation hold; this proposal does not alter dispatcher config/runtime.
- `bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md` - reviewed proposal.

## Specifications Carried Forward

- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Review Evidence

| Surface | Evidence | Result |
|---|---|---|
| Bridge chain | `show_thread_bridge.py` for `gtkb-wi5404-fab13-live-pid-provenance-fixture` | PASS: v001 is latest `NEW`, no drift |
| Applicability | Candidate preflight against v001 | PASS: `missing_required_specs=[]`, `blocking_errors=[]` |
| Clause gate | Mandatory clause preflight | PASS: zero blocking gaps |
| Production liveness contract | `scripts/dispatcher_runtime.py:2731` through `scripts/dispatcher_runtime.py:2743` and `scripts/dispatcher_runtime.py:1134` through `scripts/dispatcher_runtime.py:1136` | PASS: production requires PID alive and create-time sidecar provenance match |
| Current stale fixture | `platform_tests/scripts/test_fab13_retention_policy.py:167` through `platform_tests/scripts/test_fab13_retention_policy.py:172` | PASS: current test writes live PID/log but no create-time sidecar |
| Target scope | Proposal `target_paths` and `git status --short -- platform_tests/scripts/test_fab13_retention_policy.py bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch` | PASS with caution: test file already dirty from adjacent work, so implementation must preserve foreign hunks |

## Rationale

The proposal correctly leaves production behavior intact. `_run_artifact_live()` returns true only when the PID file exists, no exit-code file marks completion, the PID is alive, and `_dispatch_pid_provenance_matches()` succeeds. The stale fixture only writes `live.pid` and `live.stdout.log`, then expects both to survive pruning. Adding the matching create-time sidecar to the fixture exercises the production contract instead of weakening it.

The declared hunk-patch artifact is also appropriate because the target test file is already dirty from adjacent WI-5396 work. The implementation must make the WI-5404 delta independently reviewable without swallowing those foreign hunks into WI-5404 verification or commit finalization.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5404-fab13-live-pid-provenance-fixture --format json --preview-lines 60
Get-Content -Raw bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5404-fab13-live-pid-provenance-fixture --content-file bridge/gtkb-wi5404-fab13-live-pid-provenance-fixture-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5404-fab13-live-pid-provenance-fixture
rg -n "def _pid_create_time_epoch|_pid_create_time_epoch|create_time_epoch" scripts platform_tests/scripts/test_fab13_retention_policy.py
git status --short -- platform_tests/scripts/test_fab13_retention_policy.py bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, proposal-review
