GO

# Loyal Opposition Review - Post-Stop Dispatch Reconciliation Hook Order

bridge_kind: lo_verdict
Document: gtkb-prime-worker-post-stop-dispatch-retry-slice-3
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-27 UTC
Reviewed file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`
Verdict: GO

## Claim

The revised proposal resolves the prior NO-GO findings. It replaces the
unworkable in-script sleep-and-retry design with a bounded Stop-hook order
change: clear the stopping harness active-session lock before running
`cross_harness_bridge_trigger.py --stop-hook`.

The implementation scope is now concrete, parser-supported, in-root, and
testable. Loyal Opposition approves implementation of the revised Slice 3
proposal as scoped in `target_paths`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation searches were attempted with the repo CLI. Direct
`python -m groundtruth_kb ...` was unavailable because the root Python
environment does not have the package installed. Retrying with
`uv run --project groundtruth-kb` and a writable local `UV_CACHE_DIR` succeeded
but returned no rows for:

```text
post-Stop dispatch retry hook order active session suppression Slice 3
Prime worker delivery 4-slice sequence S350
active session suppression 120-second TTL cross-harness trigger
```

Thread-local prior evidence remains relevant and sufficient for this review:

- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-002.md` identified
  the exact prior blockers and explicitly listed Stop hook reordering as an
  acceptable remediation shape.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md` is latest
  `VERIFIED`, so the original Slice 1 dependency is closed.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:eb7ca9b08290c71dfb79c900e3d312e681dbe1f9fc994b92b142e7a7d61d293d`
- bridge_document_name: `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`
- operative_file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`
- Operative file: `bridge\gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

None blocking.

## Positive Confirmations

- The revised proposal directly addresses F1 from `-002` by changing hook order
  instead of relying on an intra-hook sleep while the same hook's lock removal
  has not run.
- The implementation-start target-path parser accepts the revised metadata:
  `[".codex/hooks.json", ".claude/settings.json", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]`.
- The target paths are root-contained GT-KB platform files and do not touch
  `applications/` paths.
- The proposal adds deterministic parser tests for both hook formats and a
  fixture-level active-lock lifecycle regression.
- The direct dispatch-governance specs missing from the original proposal are
  now cited and mapped to verification evidence.

## Implementation Context For Prime Builder

Approved target paths:

- `.codex/hooks.json`
- `.claude/settings.json`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

Implement only the revised Stop-order design in `-003`: session-stop heartbeat
must run immediately before `cross_harness_bridge_trigger.py --stop-hook`, and
the later duplicate session-stop heartbeat must be removed from both hook
registrations. Do not restore interval pollers or the retired smart poller.

Required verification:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check platform_tests/scripts/test_cross_harness_bridge_trigger.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
git diff --check -- .codex/hooks.json .claude/settings.json platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

Review note: the current working tree already contains unrelated-looking
changes in `.codex/hooks.json`, `.claude/settings.json`, and
`platform_tests/scripts/test_cross_harness_bridge_trigger.py`. Prime Builder
must preserve unrelated user/parallel changes and keep the Slice 3
implementation report scoped to the approved target paths and exact diff.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prime-worker-post-stop-dispatch-retry-slice-3 --format json --preview-lines 1000
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
uv run --project groundtruth-kb python -m groundtruth_kb deliberations search "post-Stop dispatch retry hook order active session suppression Slice 3" --limit 8 --json
uv run --project groundtruth-kb python -m groundtruth_kb deliberations search "Prime worker delivery 4-slice sequence S350" --limit 8 --json
uv run --project groundtruth-kb python -m groundtruth_kb deliberations search "active session suppression 120-second TTL cross-harness trigger" --limit 8 --json
python - <<extract_target_paths smoke via stdin>>
rg and line-window reads over bridge/INDEX.md, .codex/hooks.json, .claude/settings.json, scripts/implementation_authorization.py, and scripts/cross_harness_bridge_trigger.py
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
