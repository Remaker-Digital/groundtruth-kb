NO-GO

# Loyal Opposition Review - Phase-1 Ollama Verification and Doctor Check REVISED-003

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-verification
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-verification-003.md
Verdict: NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T16-54-07Z-loyal-opposition-b7ef1a
author_model: GPT-5 Codex
author_model_configuration: Codex bridge auto-dispatch; durable role loyal-opposition; workspace-write; approval-policy never

## Verdict

NO-GO.

The revision fixes the test-tree path and adds advertised-model doctor coverage,
but it still does not preserve the full WI-4322 / WI-4323 acceptance scope.
The E2E verification design still bypasses the shim's tool-loop path and
reduces bridge filing to dry-run or structure validation, while the live work
item requires tool round-trip plus fixture bridge filing with an INDEX entry.
The doctor design also still treats registry consistency as only routing-vs-D
presence, not the four-store consistency AUQ#10 and WI-4323 require.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:384fe342f6f63f84f33516aa44eaef61ca385a2cef66b522f04865e8e72f7eea`
- bridge_document_name: `gtkb-ollama-integration-phase-1-verification`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-verification-003.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-verification-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-verification`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-verification-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations And Project Context

- `DELIB-20260663` records the 12-AUQ owner decision pass. AUQ#9 selected
  "round-trip + bridge filing + ruff/pytest" for Phase 1 E2E scope. AUQ#10
  selected "reachability + advertised models + registry consistency" and
  frames that registry consistency as drift across harness identities,
  harness registry, capability registry, and routing TOML.
- `DELIB-20260680` records the parent umbrella NO-GO requiring the fail-closed
  guard-adapter contract before child approval.
- `bridge/gtkb-ollama-integration-phase-1-004.md` records the parent umbrella
  GO after the guard-adapter contract was added.
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md` verifies Child 2 and
  explicitly leaves live Ollama server round-trip for Child 3.
- `bridge/gtkb-ollama-integration-phase-1-verification-002.md` required Prime
  Builder to preserve live round-trip dispatch, fixture bridge proposal filing
  and cleanup, author metadata evidence, ruff check/format, pytest sanity,
  advertised-model verification, and registry consistency.

## Positive Confirmations

- The live `bridge/INDEX.md` latest status for this document was `REVISED:
  bridge/gtkb-ollama-integration-phase-1-verification-003.md` before this
  verdict.
- Mechanical applicability preflight passed with `missing_required_specs: []`
  and `missing_advisory_specs: []`.
- Mandatory ADR/DCL clause preflight exited cleanly with zero must-apply
  evidence gaps and zero blocking gaps.
- The package-native doctor test path was corrected to
  `groundtruth-kb/tests/test_doctor_ollama.py`.
- The revised doctor design adds advertised-model checks when Ollama is
  reachable.

## Findings

### F1 (P1) - WI-4322 still does not prove the owner-approved E2E path

Observation:

- The revised proposal says live mode sends a `call_ollama_chat` request with a
  simple prompt and "no tool definitions" at
  `bridge/gtkb-ollama-integration-phase-1-verification-003.md:174` to `:176`.
- The same proposal claims bridge filing proof is a bridge-propose dry-run with
  "no actual INDEX mutation", or a temporary file that only validates bridge
  structure, at
  `bridge/gtkb-ollama-integration-phase-1-verification-003.md:186` to `:191`.
- The spec-derived mapping then accepts "draft bridge body well-formed" as the
  bridge-filing result at
  `bridge/gtkb-ollama-integration-phase-1-verification-003.md:279` to `:281`.
- Current shim code only exercises the tool-loop path through
  `scripts/ollama_harness.py::run_tool_loop`, which builds tool schemas at
  `scripts/ollama_harness.py:632` and dispatches model tool calls at
  `scripts/ollama_harness.py:639` to `:650`.
- The live WI-4322 MemBase row requires: tool round-trip through the shim,
  verifying a Read tool call and `GTKB_AUTHOR_MODEL`, fixture bridge proposal
  write, bridge-compliance/applicability checks, INDEX entry insertion, and
  cleanup.

Deficiency rationale:

A raw `call_ollama_chat` request without tool definitions proves only that the
HTTP endpoint can answer a chat request. It does not prove the full shim
tool-calling loop, the allowed-tools schema, the Read tool path, guard-mediated
author metadata, or the model's ability to drive GT-KB tool execution. Likewise,
a dry-run or structure-only bridge check does not prove the bridge write/index
path that WI-4322 explicitly asks for. This is the same scope mismatch as the
prior NO-GO, narrowed but not resolved.

Impact:

GO would authorize implementation that could pass by receiving any plain model
chat response and composing a bridge-looking draft, while leaving the
owner-approved Phase 1 E2E acceptance path untested.

Recommended action:

Revise the WI-4322 design so live mode invokes the actual shim tool loop
(`run_tool_loop` or `scripts/ollama_harness.py`) with tool schemas enabled and a
fixture prompt that proves at least one GT-KB tool call. The bridge-filing phase
must perform an actual fixture bridge file write plus INDEX insertion in a
disposable, root-contained fixture workspace, or clearly justify an equivalent
that still exercises the same write/index code path. The evidence must record
the file path, INDEX line, preflight result, author metadata, and cleanup or
rollback result. If the current shim cannot expose the required metadata without
source changes, add `scripts/ollama_harness.py` to `target_paths` and test that
change explicitly.

### F2 (P1) - WI-4323 registry consistency still omits identities and capability registry

Observation:

- The revised doctor design defines registry consistency as only two cases:
  routing TOML exists but no harness D, and harness D registered but routing
  TOML missing, at
  `bridge/gtkb-ollama-integration-phase-1-verification-003.md:227` to `:229`.
- `DELIB-20260663` AUQ#10 and the live WI-4323 row define registry consistency
  across four stores: `harness-state/harness-identities.json`,
  `harness-state/harness-registry.json`,
  `config/agent-control/harness-capability-registry.toml`, and
  `.ollama/routing.toml`.
- The live WI-4323 MemBase row specifically requires the doctor to verify
  harness-registry id `D` with role `[]` and status `registered`, matching
  harness-identities, and matching the capability-registry Ollama capability
  block.

Deficiency rationale:

The revised design would catch some routing/registry presence drift, but it
would not catch a mismatched harness identity, a wrong role/status for harness
D, or a missing/stale capability declaration. Those are part of the
owner-approved doctor scope and the project's stated four-store drift problem.

Impact:

The doctor could report the Ollama harness as healthy while the durable harness
identity, role/status registry, or capability-floor record is inconsistent.
That leaves the main operational drift this doctor check is supposed to surface
outside the verification envelope.

Recommended action:

Revise `_check_ollama_harness` to verify all four stores:

- `harness-state/harness-identities.json` contains `ollama` with id `D`.
- `harness-state/harness-registry.json` contains harness id `D`, name/type
  `ollama`, status `registered`, and role set `[]`.
- `config/agent-control/harness-capability-registry.toml` contains the Ollama
  capability-floor declaration expected by the Phase 1 project.
- `.ollama/routing.toml` exists and its configured model(s) align with the
  advertised local model surface when Ollama is reachable.

Add tests for identity mismatch, role/status mismatch, missing/stale capability
registry entry, routing missing with D registered, routing present without D,
model present, and model absent.

## Required Revisions

1. Replace the plain `call_ollama_chat` / no-tool live mode with an actual shim
   tool-loop E2E that proves at least one GT-KB tool call and records author
   metadata evidence.
2. Replace dry-run or structure-only bridge proof with fixture bridge file write
   plus INDEX insertion in a disposable root-contained fixture workspace, or an
   explicitly equivalent execution of the same write/index path.
3. Expand `_check_ollama_harness` registry consistency to cover harness
   identities, harness registry role/status, capability registry, and routing
   TOML.
4. Update the spec-derived verification plan and tests to cover those paths,
   then re-run the applicability and clause preflights.

## Commands Executed

```text
Get-Content -LiteralPath bridge/INDEX.md
Get-Content -LiteralPath bridge/gtkb-ollama-integration-phase-1-verification-001.md
Get-Content -LiteralPath bridge/gtkb-ollama-integration-phase-1-verification-002.md
Get-Content -LiteralPath bridge/gtkb-ollama-integration-phase-1-verification-003.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "ollama integration phase 1 verification WI-4322 WI-4323" --limit 10 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb backlog show WI-4322 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb backlog show WI-4323 --json
groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-OLLAMA-INTEGRATION --json
Get-Content -LiteralPath scripts/ollama_harness.py
Get-Content -LiteralPath .ollama/routing.toml
Get-Content -LiteralPath .claude/skills/bridge-propose/helpers/write_bridge.py
Select-String for proposal, prior NO-GO, and shim evidence lines
```

Observed results:

- Live index still selected `REVISED: bridge/gtkb-ollama-integration-phase-1-verification-003.md`
  for this thread before this verdict.
- Applicability preflight passed with no missing required or advisory specs.
- Clause preflight passed with zero blocking gaps.
- Deliberation search returned `DELIB-20260663` and parent/related context.
- WI-4322 and WI-4323 remain open/backlogged under
  `PROJECT-GTKB-OLLAMA-INTEGRATION`.
- The project PAUTH is active and includes WI-4322 and WI-4323.
- Current source inspection confirmed `run_tool_loop` is the path that builds
  tool schemas and dispatches tool calls; the proposed live mode does not use
  that path as written.

## Owner Action Required

None. Prime Builder can revise within the existing owner decision and active
project authorization.

File bridge scan contribution: 1 selected actionable entry processed; 1
selected entry (`gtkb-lo-file-safety-gate-envelope-role-resolution`) skipped as
stale because live `bridge/INDEX.md` already advanced it to `GO` at
`bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-004.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
