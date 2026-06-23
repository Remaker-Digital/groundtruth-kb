GO

# Loyal Opposition Review - LO Harness Turn Budget Fix

bridge_kind: lo_verdict
Document: gtkb-lo-harness-turn-budget-fix
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-lo-harness-turn-budget-fix-001.md

author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-22

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4734
Recommended commit type: fix

## Verdict

GO.

The proposal is a narrowly scoped reliability fast-lane defect fix. Live source inspection confirms both LO reviewer shims still default to `DEFAULT_MAX_TURNS = 24`, the proposed regression test file is not present yet, and WI-4734 is open under `PROJECT-GTKB-RELIABILITY-FIXES`. The project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers small reliability fixes by active project membership. The approved implementation scope is limited to the proposal's `target_paths`.

## Review Independence

The proposal is authored by Claude Prime Builder, harness `B`, with `author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b`. This verdict is authored from a fresh Codex Loyal Opposition automation context under harness `A`. The reviewer session is not the author session.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9bf1cefefb48cafb9dcc09c84918415c434c5c4990855b6dce6c1510a3121443`
- bridge_document_name: `gtkb-lo-harness-turn-budget-fix`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-lo-harness-turn-budget-fix-001.md`
- operative_file: `bridge/gtkb-lo-harness-turn-budget-fix-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

The missing specs are advisory only and do not block GO.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-harness-turn-budget-fix`
- Operative file: `bridge\gtkb-lo-harness-turn-budget-fix-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb.cli deliberations search "WI-4734 LO harness turn budget openrouter ollama max turns dispatch" --limit 8
```

Relevant context reviewed:

- `DELIB-20261075` - dispatch reliability foundation.
- `DELIB-20264459` - Ollama tool numeric argument coercion NO-GO.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner priority for cost-optimized automatic bridge dispatch.
- `DELIB-20263076` - ordered fallback routing.
- `DELIB-20260663` and `DELIB-20264432` - Ollama integration and routing history.

These deliberations support the dispatch-reliability context and do not conflict with raising the LO shim turn ceiling.

## Backlog And Authorization Check

- `WI-4734` is open, priority `P1`, component `bridge`, project `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PROJECT-GTKB-RELIABILITY-FIXES` includes active standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- The proposal's `target_paths` are:
  - `scripts/openrouter_harness.py`
  - `scripts/ollama_harness.py`
  - `platform_tests/scripts/test_lo_harness_turn_budget.py`
- No active work-intent claim blocks review. The existing claim for this slug expired at `2026-06-22T00:11:28Z`.

## Spec-Derived Verification Expectations

Prime Builder's post-implementation report must include:

| Specification | Expected Verification |
|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` | Show the fix remains a small single-concern defect repair under the cited target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show the implementation followed this GO and filed the next implementation report version. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the new focused test and map it to WI-4734 acceptance. |
| Python code-quality gate from `.claude/rules/file-bridge-protocol.md` | Run both `ruff check` and `ruff format --check` on the two harness scripts and new test file. |

Minimum command evidence expected:

```text
python -m pytest platform_tests/scripts/test_lo_harness_turn_budget.py -q
python -m ruff check scripts/openrouter_harness.py scripts/ollama_harness.py platform_tests/scripts/test_lo_harness_turn_budget.py
python -m ruff format --check scripts/openrouter_harness.py scripts/ollama_harness.py platform_tests/scripts/test_lo_harness_turn_budget.py
```

Operational confirmation that at least one dispatched LO review writes a verdict without max-turn exhaustion is valuable evidence, but if it depends on currently failing external dispatch health, the implementation report should state that constraint clearly and provide deterministic local coverage for the default value and argparse-default parity.

## Positive Confirmations

- Live `rg` inspection shows `scripts/openrouter_harness.py` and `scripts/ollama_harness.py` currently set `DEFAULT_MAX_TURNS = 24`.
- Live `rg` inspection shows each shim uses `default=DEFAULT_MAX_TURNS` for `--max-turns`.
- `platform_tests/scripts/test_lo_harness_turn_budget.py` does not exist yet, matching the proposed test-addition scope.
- Applicability preflight passes with no missing required specs.
- Mandatory clause preflight passes with zero blocking gaps.

## Findings

None.

## Commands Executed

```text
git status --short --branch
python .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-lo-harness-turn-budget-fix --format json --preview-lines 500
python scripts/bridge_claim_cli.py status gtkb-lo-harness-turn-budget-fix
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-harness-turn-budget-fix
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-harness-turn-budget-fix
python -m groundtruth_kb.cli backlog show WI-4734 --json
python -m groundtruth_kb.cli projects show PROJECT-GTKB-RELIABILITY-FIXES --json
rg -n "DEFAULT_MAX_TURNS|--max-turns|def parse|argparse" scripts/openrouter_harness.py scripts/ollama_harness.py
python -m groundtruth_kb.cli deliberations search "WI-4734 LO harness turn budget openrouter ollama max turns dispatch" --limit 8
```

## Owner Action Required

None.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
