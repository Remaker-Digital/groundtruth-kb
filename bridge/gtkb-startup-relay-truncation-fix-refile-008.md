NO-GO

bridge_kind: lo_verdict
Document: gtkb-startup-relay-truncation-fix-refile
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-007.md

# Loyal Opposition Verification - Startup Relay Truncation Fix Refile

## Verdict

NO-GO.

The revised report resolves the mandatory clause-preflight gap and appears to
resolve the wrong-role default-cache regression. It does not resolve the prior
`-006` finding that stale relay-cache metadata must fail visibly. A cache dated
`2000-01-01T00:00:00Z` with internally consistent hash and byte length still
receives the normal startup relay pointer instead of `GTKB STARTUP RELAY
FAILURE`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:c0463624d88caa33120e86ee50f9216b2ab338659b14205add7705bdac36ed7d`
- bridge_document_name: `gtkb-startup-relay-truncation-fix-refile`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-relay-truncation-fix-refile-007.md`
- operative_file: `bridge/gtkb-startup-relay-truncation-fix-refile-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: PASS.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-relay-truncation-fix-refile`
- Operative file: `bridge\gtkb-startup-relay-truncation-fix-refile-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Result: PASS.

## Prior Deliberations

The thread carries forward these relevant deliberations:

- `DELIB-2078` - owner approval for the init-keyword startup-disclosure relay specification.
- `DELIB-1536` - SessionStart formalization / init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` - Loyal Opposition startup symmetry reviews relevant to wrong-role startup disclosure risk.
- `DELIB-1075` and `DELIB-1081` - startup token consumption and startup first-response repair context.

Attempted live deliberation search in this shell failed because neither the
base interpreter nor `.venv` exposes the `groundtruth_kb` module.

## Specifications Carried Forward

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001
- GOV-SESSION-SELF-INITIALIZATION-001
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- GOV-RELIABILITY-FAST-LANE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 | Code probe for stale role-scoped cache plus inspection of `_startup_relay_pointer` | yes | FAIL - stale cache accepted |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | Inspection of role-scoped cache tests and `_startup_relay_cache_paths(..., role_mode)` | yes | PASS for role suffix selection |
| GOV-SESSION-SELF-INITIALIZATION-001 | Dispatcher cache-write inspection | yes | PASS for validated startup-path cache writes |
| PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 | Startup relay pointer inspection | yes | FAIL through stale-cache acceptance |
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001 | Inspection of bounded pointer output | yes | PASS |
| SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 | Inspection of `_CANONICAL_DISPATCH_INIT_RE` and role-mode prompt parsing | yes | PASS |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | Inspection of both dispatcher implementations | yes | PASS for mirrored cache helpers |
| GOV-RELIABILITY-FAST-LANE-001 | Target-path and single-defect scope review | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Live `bridge/INDEX.md` and preflight | yes | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This verification table plus targeted checks | yes | FAIL due unmet stale-cache condition |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Bridge artifact review | yes | PASS |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | WI / bridge artifact graph review | yes | PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Revised report and bridge lifecycle review | yes | PASS |

## Positive Confirmations

- `bridge/gtkb-startup-relay-truncation-fix-refile-007.md` now passes both mandatory preflights.
- The revised dispatcher sidecars include `harness_id`, `role_mode`, `role_profile`, `generated_at`, `byte_length`, and `sha256`.
- `scripts/workstream_focus.py` validates hash, byte length, harness name, harness id, role mode, and the expected startup-disclosure body shape before issuing the relay pointer.
- The role-scoped cache path selection prevents `::init gtkb lo` from falling back to the default cache when the LO cache is missing.

## Findings

### FINDING-P1-001 - Stale relay-cache metadata is still accepted as current startup disclosure

Observation:

`scripts/workstream_focus.py` returns `consistent: true` for a role-correct LO
relay cache whose metadata has `generated_at: 2000-01-01T00:00:00Z`, provided
the body shape, hash, byte length, harness id, and role mode match. The gate
then emits the normal startup relay pointer instead of `GTKB STARTUP RELAY
FAILURE`.

Evidence:

The lightweight probe wrote:

```json
{
  "harness_name": "codex",
  "harness_id": "A",
  "role_mode": "lo",
  "role_profile": "loyal-opposition",
  "generated_at": "2000-01-01T00:00:00Z",
  "byte_length": 134,
  "sha256": "<matching body hash>"
}
```

Observed `_startup_relay_pointer(root, role_mode="lo")`:

```json
{
  "cache_path": ".codex/gtkb-hooks/last-user-visible-startup-lo.md",
  "byte_length": 134,
  "harness_id": "A",
  "role_mode": "lo",
  "generated_at": "2000-01-01T00:00:00Z",
  "consistent": true
}
```

Observed `_startup_gate_response(root, role_mode="lo")` began with
`GTKB STARTUP INPUT GATE` and included the relay pointer, not
`GTKB STARTUP RELAY FAILURE`.

Deficiency rationale:

The prior `-006` NO-GO and the `-004` GO condition required missing, malformed,
stale, wrong-harness, or non-disclosure cache content to fail visibly. The
revision fixed wrong-role and non-disclosure shape checks, but there is still no
freshness gate tied to `generated_at` or the active startup request/window.
Internal hash consistency proves the file and sidecar match each other; it does
not prove the cache is current.

Impact:

A stale but internally consistent startup disclosure can still be relayed as if
it were the current owner-visible startup disclosure. That leaves the exact
failure class called out in the previous NO-GO partially open.

Recommended action:

Add a freshness check to `_startup_relay_pointer` or the gate path. Acceptable
approaches include validating `generated_at` against a current startup-request
timestamp when available, or against a tight bounded freshness window when the
request timestamp is unavailable. Add a regression test that writes a
valid-hash, valid-role, valid-body cache with stale `generated_at` and asserts
`GTKB STARTUP RELAY FAILURE`.

## Required Revisions

Prime Builder should:

1. Implement explicit stale-cache rejection for harness-scoped and role-scoped relay caches.
2. Add a targeted test proving a valid-hash, valid-role, valid-body but stale `generated_at` cache fails visibly.
3. Rerun the T1-T6 suite, ruff checks, bridge applicability preflight, and clause preflight from an environment with the repo test/lint dependencies installed.
4. File a revised implementation report carrying forward the observed results.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Result: PASS; `missing_required_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Result: PASS; `Blocking gaps (gate-failing): 0`.

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
python -m ruff check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py
python -m ruff format --check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Result: not executable in this session's Python environments; base Python and
repo `.venv` both reported missing `pytest`, `ruff`, and `groundtruth_kb`.

```text
python scripts/implementation_authorization.py validate --target scripts/workstream_focus.py --target .codex/gtkb-hooks/session_start_dispatch.py --target .claude/hooks/session_start_dispatch.py --target platform_tests/hooks/test_workstream_focus.py --target platform_tests/scripts/test_codex_session_start_dispatcher.py --target platform_tests/scripts/test_claude_session_start_dispatcher.py --target platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Result: `authorized: false` because the post-implementation report at
`bridge/gtkb-startup-relay-truncation-fix-refile-007.md` is awaiting Loyal
Opposition review. This is an expected review-state lock, not a target-path
finding.

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
