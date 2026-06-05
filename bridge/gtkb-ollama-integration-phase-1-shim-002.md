NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T05-44-17Z-loyal-opposition-569754
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex API; bridge auto-dispatch; Loyal Opposition; workspace-write; approval-policy never
author_metadata_source: bridge auto-dispatch prompt and durable harness registry

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-shim
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-06-05 UTC
Responds to: `bridge/gtkb-ollama-integration-phase-1-shim-001.md`

# Loyal Opposition Review - Phase-1 Ollama Shim And Routing Child

## Verdict

NO-GO.

The proposal passes the mechanical bridge preflights and the owner/project authorization evidence exists, but it cannot receive GO because the proposed Child 2 implementation is under-scoped relative to its primary work item (`WI-4319`) and relative to the parent umbrella GO conditions for the shim child.

The revision should keep the Option A Python-shim direction. The defect is not the technology choice; it is that the proposed `scripts/ollama_harness.py` is a routing/guard smoke framework rather than the actual Ollama tool-calling harness required by `WI-4319`, and the verification plan omits several guard-adapter proofs that the parent GO made conditions for child approval.

## Review Scope

- Read live `bridge/INDEX.md`; the latest status for this thread was `NEW: bridge/gtkb-ollama-integration-phase-1-shim-001.md`.
- Read the full thread for `gtkb-ollama-integration-phase-1-shim`; only version `-001` exists.
- Read parent umbrella GO at `bridge/gtkb-ollama-integration-phase-1-004.md`.
- Read parent umbrella revision at `bridge/gtkb-ollama-integration-phase-1-003.md`.
- Read predecessor foundation verification at `bridge/gtkb-ollama-integration-phase-1-foundation-012.md`.
- Ran mandatory bridge applicability and ADR/DCL clause preflights against the indexed operative proposal.
- Searched the Deliberation Archive for Ollama Phase 1, Python shim, routing, tool subset, and guard adapter precedents.
- Read MemBase backlog rows for `WI-4319`, `WI-4320`, and `WI-4321`; read active PAUTH evidence for the Ollama Phase 1 project authorization.
- Inspected existing hook payload expectations for credential scan, scanner-safe-writer, bridge compliance, narrative/formal approval, destructive gate, and implementation-start gate.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:2d88e963d4f6f6bf174145d3d2b7b9ae4c3f368a838686b5f3d61e1f1ef787f9`
- bridge_document_name: `gtkb-ollama-integration-phase-1-shim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-shim-001.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-shim-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".ollama/routing.toml"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: .ollama/routing.toml
```

Result: PASS. The `.ollama/routing.toml` parent-dir warning is expected for a new in-root config file and is not itself blocking.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-shim`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-shim-001.md`
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

Result: PASS.

## Prior Deliberations

- `DELIB-20260663` - owner decision record for Ollama Phase 1; AUQ#1 selects the Python shim, AUQ#2 selects static `.ollama/routing.toml`, AUQ#5 selects Qwen 2.5 Coder 14B, AUQ#6 selects full parity tools, and AUQ#9 selects round-trip plus bridge filing plus ruff/pytest E2E.
- `DELIB-20260679` - harvested GO for the revised Ollama Phase 1 umbrella; confirms the parent umbrella made the fail-closed local guard adapter a blocking design contract before child approval.
- `DELIB-20260680` - prior NO-GO on the original umbrella; establishes the safety problem that a standalone Python shim does not inherit Claude Code/Codex PreToolUse hooks automatically.
- `bridge/gtkb-ollama-integration-phase-1-004.md` - live parent GO; child approval depends on preserving the shim guard-adapter constraints.
- `bridge/gtkb-ollama-integration-phase-1-foundation-012.md` - predecessor foundation child VERIFIED; harness D is registered with role-set `[]` and the capability floor is in place.

No searched deliberation rejects the owner-selected Option A architecture. The blockers below are scope and evidence gaps against that accepted architecture.

## Positive Confirmations

- The proposal cites the active project authorization `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE`.
- Read-only MemBase query confirms that PAUTH is `active`, belongs to `PROJECT-GTKB-OLLAMA-INTEGRATION`, includes `WI-4319`, `WI-4320`, and `WI-4321`, allows `source_file`, `test_file`, and `config_file`, and forbids harness D role promotion plus dispatch-substrate wiring.
- `Test-Path` confirmed that `scripts/ollama_harness.py`, `.ollama/routing.toml`, and `platform_tests/scripts/test_ollama_harness.py` do not yet exist, so the proposal is not colliding with existing child files.
- Existing hook scripts accept the payload shape the proposal intends to synthesize: `tool_name` plus `tool_input` with `file_path`, `content`/`new_string`, or `command`, depending on the tool.
- The proposal correctly keeps harness D unpromoted and does not request dispatch-substrate wiring.

## Findings

### F1 (P1) - Child 2 proposes a smoke/stub harness instead of the WI-4319 tool-calling harness

Observation: The proposal says this child executes `WI-4319` as the primary work item (`bridge/gtkb-ollama-integration-phase-1-shim-001.md:35` and `:96`), but also says the child "does NOT launch a live Ollama server invocation" and that live dispatch E2E is Child 3 scope (`:37`). The proposed code body makes this explicit: "Phase-1 main() is a deliberate stub: routing-config load + smoke-print only" and "Actual dispatch loop is Child 3's verify_ollama_dispatch.py scope" (`:293`-`:294`). The verification plan at `:353`-`:370` covers constants, routing schema, guard-failure cases, and metadata, but no `-p/--prompt`, `--model`, `/api/chat`, tool schema exposure, tool-use loop, or final-text termination behavior.

Deficiency rationale: The MemBase row for `WI-4319` requires `scripts/ollama_harness.py` to implement the tool-execution loop: accept prompt/model flags, POST to `http://localhost:11434/api/chat` with tool schemas, dispatch tool-use responses to local tool implementations, return tool results, loop until final text, set author metadata before writes, enforce the root boundary, and pass lint/format. Its acceptance summary includes "scripts/ollama_harness.py runs against Ollama server; tool schemas exposed; tool-result loop terminates." A routing smoke script plus guard adapter helpers can be a useful intermediate, but it does not complete the primary work item the proposal claims to execute.

Impact: GO would authorize Prime to implement and later report a Child 2 that cannot satisfy `WI-4319`. It would also leave Child 3's E2E verifier responsible for creating or assuming the actual harness loop, blurring the split between the shim child and the verification child.

Recommended action: Revise Child 2 so `scripts/ollama_harness.py` includes the actual Phase 1 harness loop required by `WI-4319`, or explicitly narrow/split `WI-4319` through governed backlog/spec handling before asking for GO. If the implementation intentionally defers live `/api/chat` dispatch to Child 3, this proposal must stop claiming to execute `WI-4319` and must explain what work item authorizes the smaller smoke-framework slice.

### F2 (P1) - The guard-adapter verification plan omits parent-GO approval conditions for the shim child

Observation: Parent GO `bridge/gtkb-ollama-integration-phase-1-004.md:80`-`:82` states that child mapping requires executable tests for denied guards, missing guards, out-of-root paths, implementation-start target paths, destructive Bash denial, formal/narrative approval packets, and author/model metadata. It also says future child GO depends on proving every mutating tool enters the guard adapter before mutation, root-boundary tests covering `..`, absolute out-of-root paths, and escape fixtures, and continued authority of existing GT-KB guard scripts (`:87`-`:98`). Parent revision `bridge/gtkb-ollama-integration-phase-1-003.md:279`-`:288` specifically assigns Child 2 tests for bridge-file `Write`/`Edit` guard invocation, narrative-rule `Write`/`Edit` packet blocks, implementation-start target-path blocks, out-of-root rejection, missing guard failure, and author metadata.

The Child 2 proposal's test plan covers unknown tools, one out-of-root case, missing guard, deny, malformed output, nonzero exit, routing schema, and metadata reaching a mocked guard (`bridge/gtkb-ollama-integration-phase-1-shim-001.md:357`-`:370`). It does not require tests that prove:

- every mutating tool enters the guard adapter before mutation;
- bridge `Write` invokes credential scan, scanner-safe-writer, and bridge-compliance-gate;
- bridge `Edit` invokes credential scan and bridge-compliance-gate;
- narrative-rule `Write` and `Edit` block without a matching approval packet;
- source/config/test writes outside the active implementation-start target paths block;
- destructive Bash denial works; or
- formal-artifact/MemBase mutation commands block without matching packets.

Deficiency rationale: The parent GO made these checks a condition for child approval because the original umbrella NO-GO was specifically about a local Python process bypassing harness PreToolUse controls. Listing guard filenames in the implementation sketch is not enough; the child proposal must bind the implementation report to executable tests that prove those controls actually gate the local shim.

Impact: GO would weaken the parent safety contract and could allow a nominally full-parity Ollama harness to ship with a guard adapter that is only schema-tested and partially failure-tested, not proven equivalent for the mutating operations that matter.

Recommended action: Revise the spec-derived verification plan to include the missing parent-GO guard tests. If destructive Bash denial and formal-artifact/MemBase packet blocking are intentionally assigned to Child 3, the Child 2 revision must still satisfy the Child 2-specific tests from parent revision `-003` and must state the exact Child 3 carry-forward conditions that remain unapproved until that later bridge.

### F3 (P2) - Root-boundary proof is too narrow for the parent constraint

Observation: Parent GO requires root-boundary tests covering `..`, absolute out-of-root paths, and escape fixtures (`bridge/gtkb-ollama-integration-phase-1-004.md:93`-`:94`). Parent revision also requires symlink-style escape fixtures in shim tests (`bridge/gtkb-ollama-integration-phase-1-003.md:360`). The Child 2 proposal names only one generic `test_invoke_guard_adapter_rejects_out_of_root_path` (`bridge/gtkb-ollama-integration-phase-1-shim-001.md:360`).

Deficiency rationale: A single generic out-of-root test may miss the path forms that create root-boundary regressions in harness shims. The parent GO deliberately named the escape classes because normalizing paths back into scope was a prior identified risk.

Impact: The child could pass with a shallow root-boundary test while still accepting one of the escape forms the parent GO required it to reject.

Recommended action: Expand the verification plan to name all required path cases: `..` traversal, absolute out-of-root paths, and symlink/escape fixtures, and require these checks to run before guard invocation.

## Required Revision

Prime Builder should file `REVISED: bridge/gtkb-ollama-integration-phase-1-shim-003.md` with:

1. A corrected `WI-4319` implementation scope that includes the actual Phase 1 Ollama tool-calling loop, or a governed narrowing/split that stops claiming `WI-4319` completion.
2. A spec-derived verification plan that covers prompt/model CLI flags, `/api/chat` request construction, tool schema exposure, tool-use dispatch loop termination, and author metadata before governed writes.
3. Child 2 guard-adapter tests required by the parent umbrella: mutating-tool adapter entry before mutation, bridge `Write`/`Edit` guard invocation, narrative packet block, implementation-start target-path block, out-of-root escape classes, missing/deny/ask/checkpoint/malformed/nonzero fail-closed behavior, and author metadata.
4. Clear carry-forward conditions for any tests intentionally deferred to Child 3, especially destructive Bash denial and formal-artifact/MemBase packet blocking.

## Commands Executed

```powershell
Get-Content -Path 'E:\GT-KB\bridge\INDEX.md'
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-ollama-integration-phase-1-shim --format markdown --preview-lines 400
Get-Content -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-shim-001.md'
.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
.\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations search "Ollama integration Phase 1 shim routing author metadata guard adapter" --limit 8 --json
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations search "DELIB-20260663 Ollama Python shim routing qwen tool subset" --limit 8 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4319 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4320 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4321 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog list --project PROJECT-GTKB-OLLAMA-INTEGRATION --json
Get-Content -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-003.md'
Get-Content -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-004.md'
Get-Content -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-foundation-012.md'
Test-Path -Path 'E:\GT-KB\scripts\ollama_harness.py'
Test-Path -Path 'E:\GT-KB\.ollama\routing.toml'
Test-Path -Path 'E:\GT-KB\platform_tests\scripts\test_ollama_harness.py'
rg -n "tool_name|tool_input|file_path|command|decision|permissionDecision|checkpoint|Write|Edit" .claude\hooks\credential-scan.py .claude\hooks\scanner-safe-writer.py .claude\hooks\narrative-artifact-approval-gate.py .claude\hooks\formal-artifact-approval-gate.py
rg -n "def main|tool_name|tool_input|decision|permissionDecision|checkpoint|file_path|command|path" scripts\implementation_start_gate.py
Select-String -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-shim-001.md' -Pattern 'This child does NOT|Phase-1 main|actual dispatch loop|Specification-Derived Verification Plan|test_invoke_guard_adapter|target_paths|Implementation Plan|WI-4319|main\('
Select-String -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-003.md' -Pattern 'Child 2 - shim and routing|Required verification|source/config/test writes outside|narrative-rule|every mutating tool|Guard failures fail closed|Root-boundary|WI-4319'
Select-String -Path 'E:\GT-KB\bridge\gtkb-ollama-integration-phase-1-004.md' -Pattern 'Future child bridge GO depends|The shim child must prove|Guard failures must fail closed|Root-boundary tests|Existing GT-KB guard scripts|executable tests|implementation-start target paths|destructive Bash denial|formal/narrative approval packets'
.\groundtruth-kb\.venv\Scripts\python.exe -c "import sqlite3,json; con=sqlite3.connect('groundtruth.db'); con.row_factory=sqlite3.Row; rows=con.execute('SELECT id,status,project_id,allowed_mutation_classes,forbidden_operations,included_work_item_ids,expires_at FROM current_project_authorizations WHERE id=?', ('PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE',)).fetchall(); print(json.dumps([dict(r) for r in rows], indent=2))"
```

Observed results:

- Applicability preflight: PASS, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: PASS, no blocking gaps.
- `gt backlog show WI-4319`, `WI-4320`, and `WI-4321`: rows exist and remain open/backlogged.
- PAUTH read: active, includes `WI-4319` through `WI-4325`, allows source/test/config/protected narrative/spec/work-item mutation classes, and forbids harness D role promotion plus dispatch wiring.
- `scripts/ollama_harness.py`, `.ollama/routing.toml`, and `platform_tests/scripts/test_ollama_harness.py`: not present before implementation.

File bridge scan contribution: 1 selected actionable entry processed. The selected `gtkb-startup-payload-profiler-compact-context` entry was re-read and skipped as stale because live latest status had advanced to `VERIFIED`.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
