GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T06-27-09Z-loyal-opposition-b48257
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex headless bridge auto-dispatch; durable role loyal-opposition; workspace-write; approval-policy never

# Loyal Opposition Verdict - Ollama Integration Phase 1 Shim Revision

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-shim
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-shim-003.md
Verdict: GO

## Verdict

GO.

The REVISED proposal closes the prior NO-GO. It corrects Child 2 from a routing/guard smoke framework into the actual Phase 1 Ollama tool-calling harness required by `WI-4319`, while keeping Child 3 responsible for live E2E and doctor coverage. The proposal now binds the parent umbrella's fail-closed guard-adapter requirements to Child 2 tests and names the root-boundary escape classes that must be rejected before guard invocation or mutation.

Implementation is authorized only for the target paths declared in `bridge/gtkb-ollama-integration-phase-1-shim-003.md`:

- `scripts/ollama_harness.py`
- `.ollama/routing.toml`
- `platform_tests/scripts/test_ollama_harness.py`

No harness D role promotion, dispatch-substrate wiring, formal spec insert, protected narrative edit, or MemBase mutation is included in this GO.

## Prior Deliberations

- `DELIB-20260663` - owner-decision record for the Ollama Phase 1 12-AUQ grilling pass. It selects Option A Python shim, static `.ollama/routing.toml`, Qwen 2.5 Coder 14B, full parity tools, Phase 1 E2E expectations, and registered/no-active-role status for harness D.
- `DELIB-20260680` - prior Loyal Opposition NO-GO on the Ollama Phase 1 umbrella. It required the fail-closed local guard-adapter contract that the parent GO later made binding on child proposals.
- `bridge/gtkb-ollama-integration-phase-1-004.md` - parent umbrella GO. It makes child approval depend on preserving fail-closed guard-adapter tests, root-boundary escape tests, existing GT-KB guard-script authority, and no harness D role promotion or dispatch wiring.
- `bridge/gtkb-ollama-integration-phase-1-shim-002.md` - prior Child 2 NO-GO. It required the revised proposal to include the actual `WI-4319` tool-calling loop, parent guard-adapter tests, and specific root-boundary escape classes.

The deliberation search also returned unrelated historical bridge records; no searched deliberation contradicted the revised Option A / Child 2 scope.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:ada818a262c80163d258437797e0005b076573576690d11a4a1c08cd3aee497f`
- bridge_document_name: `gtkb-ollama-integration-phase-1-shim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-shim-003.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-shim-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".ollama/routing.toml"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The `.ollama/routing.toml` parent-directory warning is expected for a new configuration path and is not a missing-spec defect.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-shim`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-shim-003.md`
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

## Backlog And Future-Work Check

`WI-4319`, `WI-4320`, and `WI-4321` exist as open/backlogged work items under `PROJECT-GTKB-OLLAMA-INTEGRATION`. The project backlog also retains later Phase 1 work for live E2E verification (`WI-4322`), doctor integration (`WI-4323`), formal specs (`WI-4324`), and protected narrative updates (`WI-4325`).

No duplication or future-work conflict blocks GO. The revised proposal explicitly keeps Child 3's live E2E and doctor work out of Child 2 while still requiring Child 2 to supply the actual local harness loop and unit proof.

## Review Findings

No blocking findings.

Positive confirmations:

- Prior F1 is resolved. `bridge/gtkb-ollama-integration-phase-1-shim-003.md` now states that Child 2 implements prompt/model CLI flags, `/api/chat` requests, GT-KB tool schemas, local tool dispatch, tool-result round trips, final-text termination, author metadata, root-boundary enforcement, and fail-closed guard-adapter tests.
- Prior F2 is resolved. The revised verification plan requires mutating-tool adapter-entry proof, bridge `Write`/`Edit` guard invocation, narrative/formal approval denial fixtures, implementation-start target-path denial, destructive Bash denial, and guard failure-mode checks.
- Prior F3 is resolved. The revised plan names `..`, absolute out-of-root paths, symlink/escape fixtures, and valid in-root not-yet-existing paths as separate root-boundary cases.
- Owner decision evidence is substantive. `DELIB-20260663` directly supports Option A, static TOML routing, Qwen 2.5 Coder 14B, full parity tool exposure, and Phase 1 round-trip/bridge-filing proof expectations.
- Mechanical gates pass. Applicability preflight reports no missing required or advisory specs, and clause preflight reports zero blocking gaps.

## Conditions For Post-Implementation Report

Prime Builder's later implementation report must carry forward:

- the linked specifications from `-003`;
- the full spec-to-test mapping promised in `-003`;
- exact observed results for pytest, ruff lint, ruff format check, CLI help, and the mocked `/api/chat` lane;
- evidence that Write/Edit/Bash cannot side-effect before the guard adapter allows;
- evidence that root-boundary rejection happens before guard invocation for traversal, absolute out-of-root, and escape-fixture paths;
- evidence that Child 2 did not perform harness D role promotion, dispatch-substrate wiring, formal spec insertion, protected narrative edits, or MemBase mutation.

## Commands Executed

```powershell
Get-Content bridge\INDEX.md
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-ollama-integration-phase-1-shim --format markdown --preview-lines 1200
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-shim
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260663 --json
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations search "DELIB-20260663 Ollama Python shim routing qwen tool subset" --limit 8 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4319 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4320 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4321 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog list --project PROJECT-GTKB-OLLAMA-INTEGRATION --json
Select-String -Path bridge\gtkb-ollama-integration-phase-1-shim-003.md -Pattern "Revision Claim|actual Phase 1|Specification Links|Requirement Sufficiency|AUQ#9|Findings Addressed|Implementation Scope|Specification-Derived Verification Plan|Child 3 carry-forward|Owner Action Required"
Select-String -Path bridge\gtkb-ollama-integration-phase-1-shim-002.md -Pattern "F1 \(P1\)|stub harness|Required Revisions|guard-adapter|root-boundary"
Select-String -Path bridge\gtkb-ollama-integration-phase-1-004.md -Pattern "GO|fail-closed|guard|Child 2|WI-4319|Required|Root"
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
