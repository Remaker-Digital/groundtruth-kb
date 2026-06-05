NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Agent Red Child-Directory Cutover REVISED-2

Document: gtkb-isolation-018-agent-red-cutover
Version reviewed: bridge/gtkb-isolation-018-agent-red-cutover-005.md
Verdict: NO-GO
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-06-05 UTC

## Summary

The `-005` revision fixes the prior mandatory preflight blockers and expands scope to the Docker/test surfaces called out in `-004`, but it still cannot receive GO. The proposed `_production_effects.py` change updates the Shopify surface path to `applications/Agent_Red/shopify.app.toml` while preserving `MOVE` semantics in a renderer that blindly prefixes every `MOVE` row with `applications/Agent_Red/`. That would create a misleading generated target path: `applications/Agent_Red/applications/Agent_Red/shopify.app.toml`.

No owner input is requested in this auto-dispatch response. Prime can unblock with a revised proposal that preserves production-effects-map semantics and completes the Python code-quality gate for every changed Python file.

## Prior Deliberations

Deliberation search was attempted through the normal `gt deliberations search` CLI, but this shell has no `gt` shim and the direct CLI module path is missing the `click` dependency. I therefore used read-only SQLite queries against `groundtruth.db` / `current_deliberations`.

- `DELIB-20260875` records owner authorization for the ISOLATION-018 Agent Red child-directory cutover PAUTH and next-session scheduling.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` records the owner topology rule that Agent Red files belong under `E:\GT-KB\applications\Agent_Red\`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` records the pending-migration waiver for Agent Red root files until ISOLATION-018 is VERIFIED.
- `DELIB-1952` records the prior `gtkb-isolation-018-agent-red-file-migration` bridge thread.
- `DELIB-1915` and `DELIB-1907` surfaced as related VERIFIED ISOLATION-018 sub-slice precedent.
- `DELIB-1382`, `DELIB-1384`, and `DELIB-1385` surfaced as related production-effects-map review history.

## Findings

### F1 - P1 - Production-effects map would double-prefix the moved Shopify path

Claim: The revision says `scripts/rehearse/_production_effects.py` should change the Shopify surface from `"shopify.app.toml"` to `"applications/Agent_Red/shopify.app.toml"` while the row remains `MOVE`, and it updates the live test to assert the new row path with `disposition == "MOVE"`.

Evidence:

- `bridge/gtkb-isolation-018-agent-red-cutover-005.md:183` proposes exactly one `_production_effects.py` edit: `"shopify.app.toml"` -> `"applications/Agent_Red/shopify.app.toml"`.
- `bridge/gtkb-isolation-018-agent-red-cutover-005.md:236` through `:237` proposes updating the test to find row path `"applications/Agent_Red/shopify.app.toml"` and still assert `row["disposition"] == "MOVE"`.
- Current renderer logic at `scripts/rehearse/_production_effects.py:928` through `:931` labels every MOVE row as "relocate to applications/Agent_Red/<path>" and computes `target = f"applications/Agent_Red/{r['path']}"`.
- The current preview test at `platform_tests/scripts/test_rehearse_production_effects.py:388` through `:398` only checks that disposition section headings exist; it does not assert that rendered MOVE targets are non-duplicated.

Impact: If Prime implements the revision as written, the machine-readable row may pass the revised single-row test while the human production-effects map reports a nonsensical relocation target: `applications/Agent_Red/shopify.app.toml` -> `applications/Agent_Red/applications/Agent_Red/shopify.app.toml`. That degrades the migration evidence surface this same lane exists to preserve and can mislead future cutover/hygiene work.

Recommended action: Revise the proposal to preserve the renderer invariant. Acceptable options include:

1. Keep the legacy-root probe as `"shopify.app.toml"` and treat absence after cutover as closure evidence, while separately documenting the relocated destination through another check.
2. If `_production_effects.py` should track already-relocated application paths, change the disposition/renderer semantics so paths already under `applications/Agent_Red/` are not emitted as `applications/Agent_Red/applications/Agent_Red/...`.
3. Add a regression assertion that reads `production-effects-map.md` and fails if any MOVE target is double-prefixed.

### F2 - P2 - Code-quality verification omits a changed Python test file

Claim: The revision proposes editing `platform_tests/scripts/test_rehearse_production_effects.py` but its ruff gates cover only the three Python files under `scripts/`.

Evidence:

- `bridge/gtkb-isolation-018-agent-red-cutover-005.md:37` includes `platform_tests/scripts/test_rehearse_production_effects.py` in `target_paths`.
- `bridge/gtkb-isolation-018-agent-red-cutover-005.md:330` lists that same test file as an expected file change.
- The verification commands at `bridge/gtkb-isolation-018-agent-red-cutover-005.md:295` through `:296` run `ruff check` and `ruff format --check` only on `scripts/session_self_initialization.py`, `scripts/rehearse/_production_effects.py`, and `scripts/rehearse/_dashboard_regen.py`.
- `.claude/rules/file-bridge-protocol.md` requires both `ruff check <changed.py>` and `ruff format --check <changed.py>` before filing a post-implementation report whose changes include Python files.

Impact: A post-implementation report following this plan could omit required lint/format evidence for a live Python test file. That creates avoidable verification churn and weakens the specification-derived verification record.

Recommended action: Add `platform_tests/scripts/test_rehearse_production_effects.py` to both ruff commands, or state a concrete repo-native equivalent that covers the changed Python test file.

## Positive Evidence

- The live latest status in `bridge/INDEX.md` was `REVISED: bridge/gtkb-isolation-018-agent-red-cutover-005.md`, making the entry Loyal Opposition-actionable.
- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-isolation-018-agent-red-cutover --format json` returned `drift: []`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover` passes on `-005` with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover` exits 0 on `-005` with no blocking gaps.
- The revision correctly adds `Dockerfile.test`, `memory/topics/testing.md`, and `platform_tests/scripts/test_rehearse_production_effects.py` to `target_paths` for the prior `-004` F2 surface gap.

## Applicability Preflight

- packet_hash: `sha256:aefba2955532fa822c5ac711061793e849ac02d78e7836e69edcd93243722c81`
- bridge_document_name: `gtkb-isolation-018-agent-red-cutover`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-agent-red-cutover-005.md`
- operative_file: `bridge/gtkb-isolation-018-agent-red-cutover-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-agent-red-cutover`
- Operative file: `bridge\gtkb-isolation-018-agent-red-cutover-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Verification Limits

- `python -m pytest platform_tests/scripts/test_rehearse_production_effects.py -q --tb=short` could not run in this shell because the default Python reports `No module named pytest`.
- `.venv\Scripts\python.exe -m pytest --version` also reports `No module named pytest`.
- The verdict therefore relies on static source/proposal evidence for the renderer invariant and records the dependency gap rather than treating unrun tests as a proposal defect.

## Required Revision

Revise the bridge packet to:

1. Correct the `_production_effects.py` plan so an already-relocated `applications/Agent_Red/...` surface cannot be rendered as a MOVE target under `applications/Agent_Red/applications/Agent_Red/...`.
2. Add a regression assertion for the rendered `production-effects-map.md` output, not only the JSON row path/disposition.
3. Include every changed Python file, including `platform_tests/scripts/test_rehearse_production_effects.py`, in the ruff check and ruff format verification commands.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
