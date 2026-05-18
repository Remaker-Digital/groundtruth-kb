VERIFIED

bridge_kind: verification_verdict
Document: gtkb-harness-data-driven-dispatch
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-data-driven-dispatch-005.md
Recommended commit type: feat:

# Loyal Opposition Verification: gtkb-harness-data-driven-dispatch-005

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:245fee871875818923f2fb9b85fad3244db2d2559927f487eb61ed32bb21ac4e`
- bridge_document_name: `gtkb-harness-data-driven-dispatch`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-data-driven-dispatch-005.md`
- operative_file: `bridge/gtkb-harness-data-driven-dispatch-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-data-driven-dispatch`
- Operative file: `bridge\gtkb-harness-data-driven-dispatch-005.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-2079` directly controls this work. Q9 decided that the cross-harness trigger dispatches harnesses data-driven from the registry `invocation_surfaces` column, with no hard-coded per-harness branch.
- `DELIB-2080` is relevant. It records full role portability and confirms the Antigravity/Gemini headless invocation belongs in `invocation_surfaces`.
- `REQ-HARNESS-REGISTRY-001` version 2 carries FR8: cross-harness bridge dispatch resolves invocation commands from the registry record's `invocation_surfaces`; no per-harness branch is hard-coded into the dispatch trigger.
- The sibling thread `gtkb-cross-harness-trigger-import-repair` latest status is `NO-GO` at `bridge/gtkb-cross-harness-trigger-import-repair-002.md`. Its `groundtruth_kb` import defect is known and separate from this WI-3344 command-construction verification.

## Specifications Carried Forward

- REQ-HARNESS-REGISTRY-001
- DELIB-2079
- DELIB-2080
- ADR-SINGLE-HARNESS-OPERATING-MODE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| REQ-HARNESS-REGISTRY-001 FR8 | Direct Python verification importing `scripts/cross_harness_bridge_trigger.py`, asserting `_harness_command()` builds Codex, Claude, and Gemini argv from `invocation_surfaces`, and asserting `_resolve_dispatch_target()` attaches A/B surfaces from `harness-state/harness-registry.json`. | yes | PASS |
| DELIB-2079 Q9 | Direct Python AST check that `_harness_command()` has no `target.command_handle` reference, plus malformed-surface checks returning `None` for `codex`, `claude`, and `gemini` handles. | yes | PASS |
| DELIB-2080 | Live projection/DB inspection confirms role-portable harness records A and B carry structured `invocation_surfaces.headless.argv`; direct third-harness `gemini` argv construction also passes without a special branch. | yes | PASS |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 | `_resolve_dispatch_target()` still resolves from durable role/identity state and attaches registry projection data without changing the role-set authority path. | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Mandatory applicability and clause preflights passed; trigger dry-run with `PYTHONPATH=E:\GT-KB\groundtruth-kb\src` read live `bridge/INDEX.md` and produced registry-driven `command_head` values for both roles without spawning. | yes | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight reports `missing_required_specs: []` for the implementation report. | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This verdict carries forward the linked specifications and records executed verification evidence for each linked governing surface. | yes | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Bridge thread preserves the NEW -> NO-GO -> REVISED -> GO -> NEW -> VERIFIED lifecycle and cites the governing owner decisions and implementation evidence. | yes | PASS |

## Positive Confirmations

- `scripts/cross_harness_bridge_trigger.py:466-501` now builds the command solely from `target.invocation_surfaces["headless"]["argv"]`, substitutes `{{PROMPT}}` and `{{PROJECT_ROOT}}` as individual argv elements, and returns `None` on missing or malformed surfaces.
- `scripts/cross_harness_bridge_trigger.py:466-501` contains no `command_handle` branch. A direct AST check found no `command_handle` attribute reference inside `_harness_command()`.
- `scripts/cross_harness_bridge_trigger.py:558-576` adds `DispatchTarget.invocation_surfaces`, and `scripts/cross_harness_bridge_trigger.py:726-747` attaches surfaces from `harness-state/harness-registry.json`.
- `scripts/cross_harness_bridge_trigger.py:899-907` passes the argv list directly to `subprocess.Popen()` without `shell=True`.
- `scripts/seed_harness_registry.py:57-63`, `:121`, and `:158` seed Codex and Claude `invocation_surfaces` for fresh installs.
- `harness-state/harness-registry.json` shows harness A and harness B at version 2 with populated `invocation_surfaces.headless.argv`.
- SQLite inspection of `groundtruth.db` shows append-only v2 `harnesses` records for A and B with the same structured argv templates, preserving v1 rows with null `invocation_surfaces`.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py:1296-1372` contains the expected FR8/Q9 regression tests for data-driven argv construction, uniform fail-closed behavior, and projection attachment.
- `python -m py_compile scripts/cross_harness_bridge_trigger.py scripts/seed_harness_registry.py` completed cleanly.
- Trigger dry-run with the in-repo `groundtruth-kb/src` visible produced `command_head: ["codex", "exec"]` for `loyal-opposition` and `command_head: ["claude", "-p"]` for `prime-builder`, confirming the registry-driven command path works end-to-end when the existing package import dependency is available.

## Verification Limitations And Residual Risk

- I could not independently rerun `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q` or `python -m pytest platform_tests/scripts/test_seed_harness_registry.py -q` in this Codex shell because both the default Python and the repo `.venv` report `No module named pytest`. Attempting `uv pip install --cache-dir .uv-cache pytest` was blocked by restricted network access to PyPI. I did not rely on Prime Builder's claimed pytest output for this VERIFIED verdict; I ran direct Python checks covering the FR8/Q9 behavior instead.
- A default trigger dry-run without `PYTHONPATH` still reports `No module named 'groundtruth_kb'`. That defect is already isolated in the separate `gtkb-cross-harness-trigger-import-repair` thread, latest `NO-GO` at `bridge/gtkb-cross-harness-trigger-import-repair-002.md`, and is not a WI-3344 implementation defect.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-harness-data-driven-dispatch-001.md
Get-Content bridge/gtkb-harness-data-driven-dispatch-002.md
Get-Content bridge/gtkb-harness-data-driven-dispatch-003.md
Get-Content bridge/gtkb-harness-data-driven-dispatch-004.md
Get-Content bridge/gtkb-harness-data-driven-dispatch-005.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q
python -m pytest platform_tests/scripts/test_seed_harness_registry.py -q
python -m py_compile scripts/cross_harness_bridge_trigger.py scripts/seed_harness_registry.py
uv pip install --cache-dir .uv-cache pytest
rg -n "def _harness_command|class DispatchTarget|invocation_surfaces|command_handle ==|harness_projection_reader|sys\.path|codex|claude" scripts/cross_harness_bridge_trigger.py
rg -n "_SEED_INVOCATION_SURFACES|invocation_surfaces|insert_harness|codex|claude" scripts/seed_harness_registry.py
rg -n "test_harness_command|test_resolve_dispatch_target|invocation_surfaces|DispatchTarget|harness-registry" platform_tests/scripts/test_cross_harness_bridge_trigger.py
rg -n '"id": "A"|"id": "B"|"invocation_surfaces"|"version"|"command_handle"' harness-state/harness-registry.json
python - <<direct FR8/Q9 verification script>>
python - <<seed read_legacy_harnesses invocation_surfaces verification script>>
python scripts/cross_harness_bridge_trigger.py --project-root E:\GT-KB --diagnose
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python scripts/cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.tmp\wi3344-trigger-dryrun-pypath --dry-run --verbose --max-items 2
python - <<SQLite deliberation/spec/harness-registry inspection scripts>>
```

## Opportunity Radar

No new material deterministic-service candidate emerged from this verification. The main repeated friction is test-environment availability for Loyal Opposition reruns, but the broader import/test environment problem is already represented by active bridge work (`gtkb-cross-harness-trigger-import-repair`) and should not be duplicated here.

## Owner Action Required

None.

## Decision

VERIFIED. WI-3344 satisfies REQ-HARNESS-REGISTRY-001 FR8 and DELIB-2079 Q9: command construction is registry-driven from `invocation_surfaces`, the hard-coded Codex/Claude command branch is removed, existing A/B harness records and the seed path carry structured headless argv templates, and malformed or absent surfaces fail closed uniformly.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
