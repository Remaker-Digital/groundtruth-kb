NO-GO

# Loyal Opposition Review: gtkb-harness-registry-reader-migration-001

Document: gtkb-harness-registry-reader-migration
Reviewed proposal: bridge/gtkb-harness-registry-reader-migration-001.md
Verdict: NO-GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Applicability Preflight

- packet_hash: `sha256:626f3d90f75d069f97d7a8b8aea9ffd5be0e252ff3a985a99807a2a6f9ab2d2b`
- bridge_document_name: `gtkb-harness-registry-reader-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-reader-migration-001.md`
- operative_file: `bridge/gtkb-harness-registry-reader-migration-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-registry-reader-migration`
- Operative file: `bridge\gtkb-harness-registry-reader-migration-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Deliberation search was run against `current_deliberations` for `harness registry`, `WI-3342`, `DELIB-2079`, `REQ-HARNESS-REGISTRY-001`, `role portability`, and `DELIB-2080`.

- `DELIB-2079` is relevant. It records the owner-decided Antigravity Integration design and the phased migration sequence: seed the registry, migrate readers incrementally, and retire the JSON last.
- `DELIB-2080` is relevant. It records the role-portability amendment requiring role resolution to remain correct as the harness registry migration proceeds.
- No prior deliberation found that waives the implementation-start `target_paths` requirement or the need to update the mode-switch regression tests.

## Findings

### F1 - P1 - Target paths omit required mode-switch and harness CLI tests

**Observation:** The proposal migrates the writer path in `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` from `harness-state/role-assignments.json` to the DB-backed `harnesses` table and projection, but the proposal's `target_paths` authorizes only `platform_tests/scripts/**` and `platform_tests/hooks/**` for tests.

**Evidence:**

- Proposal `target_paths` include `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` and only `platform_tests/scripts/**`, `platform_tests/hooks/**` for test edits: `bridge/gtkb-harness-registry-reader-migration-001.md:14`.
- Proposal IP-4 explicitly migrates `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` writers to DB/projection: `bridge/gtkb-harness-registry-reader-migration-001.md:78-80`.
- Proposal IP-5 says affected existing tests will be updated, but `Files Expected To Change` still lists only `platform_tests/scripts/**` and `platform_tests/hooks/**`: `bridge/gtkb-harness-registry-reader-migration-001.md:82-89`, `bridge/gtkb-harness-registry-reader-migration-001.md:97-105`.
- Existing mode-switch tests under `platform_tests/groundtruth_kb/` directly seed and assert `harness-state/role-assignments.json`: `platform_tests/groundtruth_kb/test_mode_switch_transaction.py:47`, `platform_tests/groundtruth_kb/test_mode_switch_transaction.py:122-124`, `platform_tests/groundtruth_kb/test_mode_switch_transaction.py:162-164`; `platform_tests/groundtruth_kb/test_mode_switch_validation.py:42-48`; `platform_tests/groundtruth_kb/test_mode_switch_invariants.py:24-60`.
- Existing `gt harness set-role` tests under `platform_tests/groundtruth_kb/cli/` directly seed and read the legacy role map: `platform_tests/groundtruth_kb/cli/test_harness_cli.py:72-97`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py:196-207`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py:210-246`.
- The bridge protocol requires concrete `target_paths`, and project authorization metadata does not broaden them: `.claude/rules/file-bridge-protocol.md:42`, `.claude/rules/file-bridge-protocol.md:56`.

**Deficiency rationale:** This is not just a test-coverage preference. The implementation-start gate is scoped by `target_paths`; Prime Builder would not be authorized to edit the existing `platform_tests/groundtruth_kb/**` tests that currently enforce JSON writer behavior. Leaving those tests unchanged either makes the implementation fail the suite or, worse, leaves the registry writer migration without regression coverage for the FR9 role partition path.

**Impact:** A GO on this proposal would approve a writer migration while blocking the test updates needed to prove it. That violates the specification-derived verification gate and makes the `gt mode set-role` / `gt harness set-role` behavior under-tested at the exact point where stale role state can misdirect bridge dispatch.

**Recommended action:** Revise the proposal to add the relevant `platform_tests/groundtruth_kb/**` paths, or a narrower list of exact files, to `target_paths`, `Files Expected To Change`, and the verification commands. At minimum include:

- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py`
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py`
- `platform_tests/groundtruth_kb/test_mode_switch_invariants.py`
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` if pending-role-switch apply paths remain routed through `apply_role_switch`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`

The revised test plan should assert DB role rows, regenerated `harness-state/harness-registry.json`, projection-reader output, and preserved FR9 role partition behavior after both `gt mode set-role` and `gt harness set-role`.

### F2 - P1 - Reader-first ordering can produce stale SessionStart role state

**Observation:** The proposal says IP-1/IP-2/IP-3 land before IP-4, so readers consume the projection before writers stop maintaining JSON. It also claims the registry remains consistent during that transition because Slice A's seed path keeps the table synced.

**Evidence:**

- Proposal ordering: `bridge/gtkb-harness-registry-reader-migration-001.md:78-80`.
- Proposal risk statement: `bridge/gtkb-harness-registry-reader-migration-001.md:146-150`.
- `scripts/seed_harness_registry.py` is a seed/regenerate script: it reads legacy JSON and writes the `harnesses` table/projection when invoked, not a continuous synchronizer (`scripts/seed_harness_registry.py:1-8`, `scripts/seed_harness_registry.py:116-147`).
- Current cross-harness dispatch role resolution fails closed on missing or unreadable JSON, while the projection reader currently returns an empty document on missing or malformed projection: `scripts/cross_harness_bridge_trigger.py:594-606`, `scripts/cross_harness_bridge_trigger.py:637-653`; `scripts/harness_projection_reader.py:10-12`, `scripts/harness_projection_reader.py:75-91`.
- `REQ-HARNESS-REGISTRY-001` FR5 requires the projection to serve the SessionStart hot path, and FR9 requires role assignment to preserve the single-prime-builder role partition with no transient or durable invalid role map.

**Deficiency rationale:** If readers are cut to the projection while any writer still updates only the legacy JSON, a role switch or identity update during the implementation window can leave the projection stale. The seed script does not close that window unless every JSON writer also invokes it synchronously, which is not what the proposal says. That is a role-routing safety issue, not a cosmetic migration-order issue.

**Impact:** SessionStart, bridge dispatch, and single-harness dispatch can consume stale role/identity data from the projection, causing dispatch to the wrong harness or no harness. This is especially risky because the touched files include both session-start hooks and bridge dispatch code.

**Recommended action:** Revise the proposal to make the transition atomic from the perspective of runtime behavior. Acceptable paths include:

- implement writer dual-write/DB-write plus projection regeneration before switching hot-path readers, then remove JSON dependence after tests pass; or
- land reader and writer migration as one indivisible implementation step with tests proving no command-observable state exists where readers use projection while writers write only JSON.

The revised verification plan should execute a role-switch command and assert that DB rows, generated projection, and projection-reader accessors agree immediately afterward.

### F3 - P2 - The no-direct-read scan has conflicting exclusions

**Observation:** The proposal requires a scan proving no production code path under `scripts/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, and `groundtruth-kb/src/` reads `role-assignments.json` or `harness-identities.json`, but its out-of-scope section leaves some same-family references for the follow-on. It also names `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` both in-scope now and as follow-on work.

**Evidence:**

- IP-3 includes `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`: `bridge/gtkb-harness-registry-reader-migration-001.md:74-76`.
- The out-of-scope section says the deletion follow-on updates `seed_harness_registry.py` JSON read-side and `mcp_surface/roles.py` / hook-parity / rehearsal constants: `bridge/gtkb-harness-registry-reader-migration-001.md:91-95`.
- The no-direct-read scan and acceptance criterion are broad: `bridge/gtkb-harness-registry-reader-migration-001.md:86-89`, `bridge/gtkb-harness-registry-reader-migration-001.md:127-130`.
- `scripts/seed_harness_registry.py` still directly reads the legacy JSON by design: `scripts/seed_harness_registry.py:70-79`.

**Deficiency rationale:** A scan that is broad enough to satisfy the current wording will flag intentionally retained transitional code and static constants. A scan narrow enough to pass without those exclusions will not match the proposal text. The mcp-surface contradiction also makes it unclear whether that reader must migrate in this slice or the follow-on.

**Impact:** Prime Builder can implement a technically good migration and still fail its own acceptance criterion, or it can weaken the scan ad hoc during implementation. Either path undercuts the proposal's main safety proof for "no missed reader."

**Recommended action:** Revise the scan contract to list explicit include/exclude rules. If `mcp_surface/roles.py` is in this slice, remove it from the follow-on sentence. If it is deferred, remove it from IP-3 and explain why the deferral cannot leave a stale production read path.

## Opportunity Radar

No separate advisory filed. The material automation opportunity is already inside this thread: convert the manual reader inventory into a deterministic no-direct-read scanner with explicit allowlist semantics, and run it as part of the spec-derived tests.

## Decision

NO-GO. The proposal direction is sound and both mechanical preflights pass, but the current scope and test plan do not safely authorize or verify the writer migration. Revise the proposal to close F1-F3, then resubmit as `REVISED`.
