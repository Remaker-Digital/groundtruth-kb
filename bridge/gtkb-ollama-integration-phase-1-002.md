NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T16-24Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition bridge review

# Loyal Opposition Verdict - Ollama Integration Phase 1 Umbrella

bridge_kind: lo_verdict
Document: gtkb-ollama-integration-phase-1
Version: 002
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-001.md
Verdict: NO-GO

## Verdict

NO-GO.

The strategic direction is sound: Option A, a framework-free Python shim with
static `.ollama/routing.toml`, is the least-complex integration path for a local
Ollama harness. The owner-decision evidence exists, the PAUTH exists and is
active, and the bridge mechanical gates pass.

The proposal cannot receive GO as written because its spec drafts approve a
full-parity local tool executor without defining the fail-closed adapter that
will make a standalone Python shim actually enforce the existing GT-KB
mutating-tool guardrails. A local shim does not inherit Claude Code or Codex
PreToolUse hooks automatically. The umbrella must first specify, and the child
bridges must verify, how every mutating model tool call is routed through the
same bridge, credential, narrative/formal-approval, root-boundary,
implementation-start, and destructive-command controls.

## Prior Deliberations

Deliberation/archive evidence searched or inspected:

- `DELIB-20260663` exists as `owner_conversation` / `owner_decision` for the
  12-AUQ Ollama Phase-1 grilling pass. It is backed by
  `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json`.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md`
  recommended Option A and recorded the root-boundary and author-metadata
  constraints for generated bridge files.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md`
  recommended a Python shim and explicitly stated that local workspace tool
  execution must match the schemas and security gates of Codex and Claude Code.

No searched deliberation contradicted the owner-approved Option A strategy.
The NO-GO is about missing guardrail specification, not about the owner-selected
architecture.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:49f2221d44ac681f2f0a8cb5c2a2815d3f58c0f9d9048634fd1f0ff4969aa7ab`
- bridge_document_name: `gtkb-ollama-integration-phase-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-001.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

### P1 - Full-parity local tool dispatch is not bound to the existing guardrails

Observation: The proposal says AUQ#6 authorizes full parity tools and that the
shim "triggers bridge-compliance-gate + scanner-safe-writer + destructive-gate
+ author-metadata respect" (`bridge/gtkb-ollama-integration-phase-1-001.md`
line 110). The draft DCLs then require author metadata only "before any Write
tool dispatch" (lines 200-202), require the six canonical tools and destructive
gate delegation (lines 218-224), and require capability booleans such as
`bridge_compliance_gate_respect`, `root_boundary_respect`, and
`destructive_gate_delegation` (lines 258-264). They do not define the adapter
contract that invokes the existing guard scripts or fails closed on their deny
or ask outputs.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-001.md` lines 110, 200-204,
  218-224, and 258-264.
- `.claude/hooks/bridge-compliance-gate.py` line 11 and lines 56-57 show that
  bridge compliance is a PreToolUse hook for `Write` and `Edit`.
- `.claude/hooks/scanner-safe-writer.py` lines 15-18 and 397-399 show that
  scanner-safe-writer only intercepts `Write` hook events.
- `.claude/hooks/destructive-gate.py` lines 298-299 show that destructive-gate
  only gates `Bash` hook events.
- `.claude/hooks/formal-artifact-approval-gate.py` lines 16 and 322 show that
  formal artifact approval is a `Bash` hook.
- `.claude/hooks/narrative-artifact-approval-gate.py` lines 5, 19, and 41 show
  that narrative artifact approval gates `Write` and `Edit`.
- `.claude/hooks/credential-scan.py` lines 5 and 281-282 show that credential
  scanning gates `Write` and `Edit`.

Impact: A standalone `scripts/ollama_harness.py` that directly performs
filesystem or subprocess actions can bypass the controls that make Claude Code
and Codex safe in this repository. The proposal would approve a harness that
can expose `Write`, `Edit`, and `Bash` while proving only schema exposure and
author metadata, not enforcement of bridge compliance, credential scanning,
narrative/formal approval packets, root boundary, implementation-start target
paths, or destructive-command denial. That is a governance and safety parity
gap, not just an implementation detail.

Recommended action: Revise the umbrella before child bridges are filed. Add a
blocking DCL or GOV clause for an Ollama tool-dispatch guard adapter requiring:

1. No model-requested mutating tool may write files or run shell commands
   directly.
2. `Write`, `Edit`, and `Bash` dispatch must synthesize the same hook payload
   shape used by the existing harnesses and invoke the relevant guard scripts
   before mutation.
3. Guard decisions must fail closed: any deny, ask/checkpoint, parse failure,
   missing guard, or nonzero adapter error stops the tool call.
4. The shim must enforce project-root containment before dispatch and must not
   normalize out-of-root paths back into scope.
5. Author/model metadata must be set before every bridge-file mutation path,
   not only before a nominal `Write` helper.

Child bridge verification should include focused tests that prove at least:

- bridge-file `Write` invokes credential scan, scanner-safe-writer, and bridge
  compliance;
- bridge-file `Edit` invokes credential scan and bridge compliance;
- narrative-rule `Write`/`Edit` is blocked without a matching approval packet;
- formal-artifact and MemBase mutation commands are blocked without a matching
  packet;
- destructive Bash commands are denied by the destructive gate;
- source/config/test writes outside approved target paths are blocked by the
  implementation-start gate;
- out-of-root paths are rejected; and
- successful bridge-file writes contain the required author metadata for
  harness D and the routed model.

### P2 - The umbrella verification plan treats review approval as the only test for the new safety contract

Observation: The umbrella says its own deliverable is the design and governance
contract, with no executable verification, and says the PASS criterion for the
new ADR/DCL/GOV drafts is "Codex GO with no NO-GO findings"
(`bridge/gtkb-ollama-integration-phase-1-001.md` lines 339-346).

Impact: For ordinary documentation-only governance review this can be enough,
but this proposal is introducing the policy floor for a new mutating harness.
The new governance text must itself demand executable proof in the children,
or the child proposals can pass while only demonstrating model metadata and
basic tool schema checks.

Recommended action: In the revision, make the umbrella's design contract
explicitly require child-level guard-adapter tests. The child bridge mapping
should name those tests up front, not defer the issue to implementation
judgment.

## Non-Blocking Confirmations

- `DELIB-20260663` exists and is owner-decision evidence for the 12 AUQ answers.
- `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json`
  exists and marks the deliberation packet `approved_by=owner`.
- PAUTH
  `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE`
  exists as rowid 117, status `active`, project
  `PROJECT-GTKB-OLLAMA-INTEGRATION`, and includes WI-4316 through WI-4325.
- The five new Ollama specification IDs are not yet present in MemBase, which
  is acceptable at this umbrella stage only if the governance-implementation
  child obtains per-artifact approval packets before inserting them.

## Revision Requirements

To reach GO, file `REVISED -003` with:

1. A concrete fail-closed Ollama tool-dispatch guard adapter contract.
2. Spec text updated so full-parity tools cannot be implemented as raw Python
   filesystem/subprocess operations.
3. Child bridge verification plans that include focused guard-adapter tests for
   `Write`, `Edit`, and `Bash`.
4. Explicit wording that umbrella GO, if later granted, does not authorize any
   formal spec insert or protected narrative edit without matching
   formal/narrative approval packets.

The Option A architecture, owner decision set, PAUTH existence, and child-bridge
decomposition are otherwise viable.
