VERIFIED

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T15-51-27Z-loyal-opposition-a84fc7
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex auto-dispatch; workspace-write; approval-policy never

# Loyal Opposition Verification - GTKB-ISOLATION-018 Agent Red Child-Directory Cutover

bridge_kind: lo_verdict
Document: gtkb-isolation-018-agent-red-cutover
Version: 010
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-isolation-018-agent-red-cutover-009.md
Verdict: VERIFIED
Recommended commit type: refactor

## Verdict

VERIFIED.

The implementation report at `bridge/gtkb-isolation-018-agent-red-cutover-009.md`
satisfies the approved scope from `bridge/gtkb-isolation-018-agent-red-cutover-008.md`.
The three Agent Red deployment-plumbing files are now under
`applications/Agent_Red/`, the root copies are absent, the expected live
references point at the moved paths, and the intentionally preserved
production-effects legacy-root probe remains in place.

No blocking implementation findings remain.

## Review Scope

- Read live `bridge/INDEX.md`; latest status was `NEW` at
  `bridge/gtkb-isolation-018-agent-red-cutover-009.md`.
- Read the full thread chain `-001` through `-009` via the bridge show-thread
  helper and direct reads of the operative report.
- Ran mandatory applicability and ADR/DCL clause preflights on the indexed
  operative `-009` report.
- Searched the Deliberation Archive for the Agent Red child-directory cutover,
  ISOLATION-018, and production-effects-map context.
- Checked the current filesystem, git-follow history, reference updates,
  double-prefix absence, ruff lint, ruff format, and project doctor output.

## Prior Deliberations

- `DELIB-20260875` records the owner AUQ authorization for the ISOLATION-018
  Agent Red child-directory cutover PAUTH and next-session scheduling.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` records the pending migration
  waiver whose expiry condition is advanced by this closure.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` records the owner topology
  rule that Agent Red files belong under `E:\GT-KB\applications\Agent_Red\`.
- `DELIB-1952` records the prior Agent Red file-migration bridge thread.
- `DELIB-1948`, `DELIB-1915`, `DELIB-1914`, and `DELIB-1907` record related
  VERIFIED ISOLATION-018 sub-slice precedent.
- `DELIB-1382`, `DELIB-1384`, and `DELIB-1385` record related
  production-effects-map review history carried forward by the approved
  no-edit probe decision.

## Positive Evidence

- `Test-Path applications\Agent_Red\shopify.app.toml`,
  `applications\Agent_Red\package.json`, and
  `applications\Agent_Red\package-lock.json` all returned `True`.
- `Test-Path shopify.app.toml`, `package.json`, and `package-lock.json` at the
  GT-KB root all returned `False`.
- `git log --follow --oneline -- applications/Agent_Red/shopify.app.toml`
  traversed pre-move history, including `98d5d73a`, `fae8af56`, `4ebf40b8`,
  and `1eeaedd0` before the move-bearing commit.
- `scripts/session_self_initialization.py:2192-2195` now points the package
  inventory at `applications/Agent_Red/...`.
- `scripts/session_self_initialization.py:2485-2487` now reads the widget,
  docs-site, and admin package manifests from `applications/Agent_Red/...`.
- `scripts/rehearse/_dashboard_regen.py:83` now points at
  `applications/Agent_Red/package.json`.
- `memory/topics/deployment.md:70`, `Dockerfile.test:111`, and
  `memory/topics/testing.md:127` now cite
  `applications/Agent_Red/shopify.app.toml`.
- `applications/Agent_Red/CLAUDE.md:34-36` contains the ISOLATION-018 operator
  path note for Shopify CLI commands.
- `scripts/rehearse/_production_effects.py:328` and
  `platform_tests/scripts/test_rehearse_production_effects.py:230,234` still
  preserve the approved legacy-root `shopify.app.toml` probe/test lane.
- `rg -n "applications/Agent_Red/applications/Agent_Red"` returned no matches.
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\ollama_harness.py
  platform_tests\scripts\test_ollama_harness.py scripts\session_self_initialization.py
  scripts\rehearse\_dashboard_regen.py` returned `All checks passed!`.
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check ...` returned
  `4 files already formatted`.

## Specification-Derived Verification

| Specification / condition | Verification evidence | Result |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` strict-descendant placement | Destination files exist under `applications/Agent_Red/`; root copies are absent | PASS |
| `.claude/rules/project-root-boundary.md` | All changed live paths remain inside `E:\GT-KB`; Agent Red files remain under `applications/Agent_Red/` | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on operative `-009` reports no missing required specs | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report carries forward spec links and maps placement/reference/probe/code-quality checks to commands; LO reran current-state checks available in this dispatch | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live INDEX chain is coherent and this verdict is filed as the next monotonic version | PASS |
| Approved F1 production-effects option | Legacy-root probe preserved; no double-prefix string present | PASS |
| Code-quality gates | Ruff lint and format checks on changed Python files pass | PASS |

## Spec-to-Test Mapping

The table above is the spec-derived verification matrix for this verdict. Each
linked implementation constraint has an executed check or a recorded
environment-limited attempt. The targeted production-effects suite was rerun by
LO through `uv run --with pytest --with pytest-timeout`; the broad nested
selector remains a sandbox-permission limitation documented below.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:ef53436cf860205a294a450ebbdc3fb8abdcec01e1d3201d3b06a0963d72c40f`
- bridge_document_name: `gtkb-isolation-018-agent-red-cutover`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-agent-red-cutover-009.md`
- operative_file: `bridge/gtkb-isolation-018-agent-red-cutover-009.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-018-agent-red-cutover`
- Operative file: `bridge\gtkb-isolation-018-agent-red-cutover-009.md`
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

## Verification Limits

- The report's venv pytest commands could not be rerun verbatim because
  `groundtruth-kb\.venv\Scripts\python.exe -m pytest` resolves to a malformed
  pytest installation (`pytest.__file__` and `pytest.__version__` are `None`)
  and no `pytest.exe` exists in either checked venv.
- The targeted production-effects suite was rerun through `uv run --with pytest
  --with pytest-timeout` and passed with 28 tests.
- The broader `groundtruth-kb/tests -k "isolation or registry or root_boundary"`
  selector was attempted through `uv run --no-cache --with pytest-timeout` with
  the reported `--basetemp` shape, but fails in this Codex sandbox on
  permission errors creating temp/scaffold paths. The implementation report's
  recorded 198-pass result remains Prime-provided evidence; LO did not observe a
  cutover-specific failure in the current file state.
- `gt project doctor --json` runs but reports broad pre-existing project health
  failures and warnings unrelated to the selected cutover, including AUQ
  coverage, historical owner-input bridge coverage, DA harvest coverage, and
  product-path writability. These do not contradict the cutover file-placement
  evidence.

## Commands Executed

```powershell
Get-Content .\bridge\INDEX.md
$env:PYTHONIOENCODING='utf-8'; python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-isolation-018-agent-red-cutover --format json --preview-lines 0
$env:PYTHONIOENCODING='utf-8'; python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover
$env:PYTHONIOENCODING='utf-8'; python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover
uv run --with pytest --with pytest-timeout pytest platform_tests\scripts\test_rehearse_production_effects.py -q --tb=short --timeout=60
uv run --no-cache --with pytest-timeout pytest tests -k 'isolation or registry or root_boundary' --tb=short -q --timeout=60 --basetemp E:\GT-KB\.tmp-codex-iso018\lo-pytest-basetemp
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\session_self_initialization.py scripts\rehearse\_dashboard_regen.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\session_self_initialization.py scripts\rehearse\_dashboard_regen.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb project doctor
```

Observed results: bridge helper drift check passed; preflights passed; targeted
production-effects pytest passed; ruff passed; broad selector and doctor limits
are recorded above.

## Opportunity Radar

No separate advisory is filed from this selected-entry dispatch. The only
material efficiency cue is the recurring pytest-runner ambiguity; it is already
visible in the verification-limit evidence and is better handled by existing
project doctor / environment-health surfaces than by this cutover verdict.

## Owner Action Required

None.

File bridge scan contribution: 1 selected actionable entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
