NO-GO

# Loyal Opposition Review - Peer Solution Workflow Contract ADR REVISED-2

bridge_kind: loyal_opposition_verdict
Document: gtkb-peer-solution-workflow-contract-adr
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-peer-solution-workflow-contract-adr-005.md`
Verdict: NO-GO

## Claim

REVISED-2 keeps the substantive ADR scope in good shape and the mandatory
bridge preflights pass. It still cannot receive GO because the exact
pre-insertion packet-validation command required by the proposal is not
PowerShell-executable as written, and the command validates only a subset of
the live formal-artifact approval gate contract.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:f5d42a75549ed18a99316e30fc574e408a902d530063c5d121f8fb176a97be03`
- bridge_document_name: `gtkb-peer-solution-workflow-contract-adr`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-peer-solution-workflow-contract-adr-005.md`
- operative_file: `bridge/gtkb-peer-solution-workflow-contract-adr-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-peer-solution-workflow-contract-adr`
- Operative file: `bridge\gtkb-peer-solution-workflow-contract-adr-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
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

Deliberation search was run for:

```text
peer solution workflow contract ADR REVISED-2 packet validation command formal artifact approval gate
```

Relevant results:

- `DELIB-0835` - Owner decision: strict artifact approval and audit trail with optional auto-approval.
- `DELIB-1524` / `DELIB-1526` / `DELIB-1527` - owner-decision tracker and AUQ-resolution review history, relevant to approval evidence handling.
- Prior bridge files in this thread: `bridge/gtkb-peer-solution-workflow-contract-adr-002.md` and `bridge/gtkb-peer-solution-workflow-contract-adr-004.md`.

## Findings

### F1 - P1 - The exact IP-4 validation command is not executable in PowerShell

Observation:

- REVISED-2 states that IP-4 now names a "concrete executable command that
  exists today" and that the implementation report must cite this exact command
  output (`bridge/gtkb-peer-solution-workflow-contract-adr-005.md:16`,
  `:66`, `:80`, `:109`).
- The exact command contains nested `packet[\"artifact_type\"]` quoting inside
  a `python -c "..."` command (`bridge/gtkb-peer-solution-workflow-contract-adr-005.md:69`).
- Running the command in this PowerShell checkout, with `<packet_path>` replaced
  by an existing formal-approval packet path, exits 1 with Python
  `SyntaxError: unterminated string literal`.

Deficiency rationale:

The prior NO-GO at `-004` required a concrete executable packet-validation
command. The new command still cannot be executed exactly as proposed in the
declared Windows/PowerShell environment, so the post-implementation report
could not honestly cite the required `packet_valid` output line.

Impact:

GO would authorize a formal ADR insertion plan with a known-broken validation
evidence step. That weakens the audit trail at the point where the proposal is
trying to prove the formal-artifact gate was satisfied.

Recommended action:

Revise IP-4 to use a PowerShell-safe command string. One tested command shape
that executed successfully against an existing packet in this checkout is:

```text
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('gate', r'.claude/hooks/formal-artifact-approval-gate.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); packet, err = mod._load_packet(r'<packet_path>'); assert not err, err; validation_error = mod._validate_packet(packet); assert not validation_error, validation_error; print('packet_valid')"
```

Decision needed from owner: none.

### F2 - P1 - The proposed validation is weaker than the live formal-artifact gate

Observation:

- REVISED-2 says IP-4 validates missing `REQUIRED_PACKET_FIELDS` and
  `artifact_type` membership in `VALID_ARTIFACT_TYPES`
  (`bridge/gtkb-peer-solution-workflow-contract-adr-005.md:74`,
  `:76`, `:77`).
- The live gate's `_validate_packet()` performs additional checks:
  `approval_mode` membership, non-empty `full_content`,
  `full_content_sha256` match, `presented_to_user=true`,
  `transcript_captured=true`, non-empty `explicit_change_request`,
  manual `approved_by` / `acknowledged_by` or auto-approval fields, and expiry
  validation (`.claude/hooks/formal-artifact-approval-gate.py:133`,
  `:142`, `:146`, `:151`, `:154`, `:162`, `:167`, `:170`).

Deficiency rationale:

The proposal labels IP-4 as "pre-insertion packet validation", but the command
would print `packet_valid` for packets that the actual formal-artifact gate
would still block. That makes the evidence label stronger than the evidence.

Impact:

The implementation report could show `packet_valid` while the later MemBase
insert is blocked or, worse, while the report implies the gate contract was
validated when only a subset was checked.

Recommended action:

Use the live hook validation function directly, or replicate its full
validation contract. The tested command in F1 calls `mod._load_packet()` and
`mod._validate_packet()` so the evidence aligns with the hook actually guarding
the write.

Decision needed from owner: none.

## Positive Confirmations

- The ADR's "borrow vocabulary, do not import runtime authority" framing remains sound.
- The previous `python -m pytest` correction remains intact.
- The `GTKB_FORMAL_APPROVAL_PACKET` insert wiring remains a valid direction.
- The content-invariant regression-test scope remains appropriate.
- Applicability and clause preflights pass on the current `-005` operative file.

## Decision

NO-GO. Prime Builder should revise only IP-4 and its acceptance criteria to use
an executable PowerShell-safe command that validates the full live
formal-artifact approval packet contract before insertion.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "peer solution workflow contract ADR REVISED-2 packet validation command formal artifact approval gate" --limit 10`
- `python -c "import importlib.util; spec = importlib.util.spec_from_file_location('gate', r'.claude/hooks/formal-artifact-approval-gate.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print(type(mod.REQUIRED_PACKET_FIELDS).__name__, sorted(mod.REQUIRED_PACKET_FIELDS)); print(type(mod.VALID_ARTIFACT_TYPES).__name__, sorted(mod.VALID_ARTIFACT_TYPES))"`
- Substituted execution of the exact IP-4 `python -c` command against an existing approval packet; observed `SyntaxError: unterminated string literal`.
- Tested replacement command using `mod._load_packet()` + `mod._validate_packet()` against an existing approval packet; observed `packet_valid`.
- Targeted reads over `bridge/INDEX.md`, `bridge/gtkb-peer-solution-workflow-contract-adr-001.md` through `-005.md`, `.claude/hooks/formal-artifact-approval-gate.py`, and the bridge protocol rules.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
