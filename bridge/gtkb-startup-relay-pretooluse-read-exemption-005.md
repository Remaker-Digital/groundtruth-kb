VERIFIED

Document: gtkb-startup-relay-pretooluse-read-exemption
Reviewed-File: bridge/gtkb-startup-relay-pretooluse-read-exemption-004.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-19 UTC

# Loyal Opposition Verification - Startup Relay PreToolUse Read Exemption

## Verdict Summary

VERIFIED.

The implementation report carries forward the governing specifications, maps
the startup-relay requirements to focused tests, and the implemented code
matches the approved scope in `scripts/workstream_focus.py` and
`platform_tests/hooks/test_workstream_focus.py`.

The pending-startup guard now permits only an exact `Get-Content` read of the
harness startup disclosure cache while preserving the block for non-cache
reads, chained commands, and mutation commands. The role-scoped cache additions
also address the related `::init gtkb lo` wrong-cache risk without expanding
outside the approved target paths.

## Prior Deliberations

Deliberation Archive search command:

```text
python -m groundtruth_kb deliberations search "gtkb-startup-relay-pretooluse-read-exemption startup relay PreToolUse cache read WI-3323" --limit 8
```

Relevant results:

- `DELIB-2202` - archived bridge-thread summary for
  `gtkb-startup-relay-pretooluse-read-exemption`. This result is useful
  historical context only; live `bridge/INDEX.md` remains authoritative for
  queue state and showed latest `NEW` at `-004` before this verdict.
- `DELIB-2078` - owner approval for the init-keyword startup disclosure relay
  specification.
- `DELIB-1536` - Loyal Opposition review of SessionStart formalization and the
  init-keyword contract.
- `DELIB-1530` / `DELIB-1531` - Loyal Opposition startup symmetry reviews.
- `DELIB-2102` - related startup relay known-match suppression bridge thread.

No contrary prior deliberation was found that rejects the narrow read-only
startup cache exception or the role-scoped startup cache relay.

## Implementation Evidence

- `scripts/workstream_focus.py:1106` defines the accepted read-only
  `Get-Content ... -LiteralPath ...` command shape.
- `scripts/workstream_focus.py:1113` rejects shell control/redirection tokens
  before allowing a cache read.
- `scripts/workstream_focus.py:1132` limits allowed cache reads to the default,
  Prime Builder, and Loyal Opposition startup cache files under the active
  harness diagnostics directory.
- `scripts/workstream_focus.py:1150` validates tool name, command shape, target
  path, and allowed-cache membership.
- `scripts/workstream_focus.py:1513` keeps the startup-response pending block
  active unless the payload is the authorized startup relay cache read.
- `platform_tests/hooks/test_workstream_focus.py:1017` verifies the exact LO
  startup cache read is allowed and does not clear `startup_response_pending`.
- `platform_tests/hooks/test_workstream_focus.py:1050`,
  `platform_tests/hooks/test_workstream_focus.py:1077`, and
  `platform_tests/hooks/test_workstream_focus.py:1109` verify non-cache reads,
  chained reads, and mutation commands remain blocked.
- `platform_tests/hooks/test_workstream_focus.py:575` and
  `platform_tests/hooks/test_workstream_focus.py:626` verify explicit LO init
  uses the LO cache and rejects a default Prime Builder cache.

## Spec-Derived Verification

| Requirement / constraint | Executed verification |
|---|---|
| Startup relay can read the cached owner-visible disclosure | `test_startup_response_pending_allows_exact_startup_cache_read` |
| Startup pending gate continues blocking ordinary tool use | `test_startup_response_pending_blocks_tool_use_until_next_owner_prompt` |
| Exception is exact-path and harness-cache scoped | `test_startup_response_pending_rejects_non_cache_read` |
| Exception rejects shell chaining/additional commands | `test_startup_response_pending_rejects_chained_cache_read` |
| Exception rejects mutation commands | `test_startup_response_pending_rejects_cache_mutation` |
| LO init does not relay a Prime Builder cache | `test_canonical_lo_init_uses_role_scoped_startup_cache`; `test_canonical_lo_init_rejects_default_prime_cache` |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Observed result: `56 passed, 3 skipped, 2 xfailed`.

```text
python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `2 files already formatted`.

## Applicability Preflight

- packet_hash: `sha256:d99e2aed494444d36525aaaf2cb8b1b76763e92efcfc9e8941f9f357056f935a`
- bridge_document_name: `gtkb-startup-relay-pretooluse-read-exemption`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-relay-pretooluse-read-exemption-004.md`
- operative_file: `bridge/gtkb-startup-relay-pretooluse-read-exemption-004.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-relay-pretooluse-read-exemption`
- Operative file: `bridge\gtkb-startup-relay-pretooluse-read-exemption-004.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

No blocking findings.

File bridge scan: 1 entry processed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
