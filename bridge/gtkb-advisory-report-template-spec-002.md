NO-GO

# Loyal Opposition Review - Advisory Report Template Spec NEW

bridge_kind: lo_verdict
Document: gtkb-advisory-report-template-spec
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-advisory-report-template-spec-001.md`
Verdict: NO-GO

## Claim

`bridge/gtkb-advisory-report-template-spec-001.md` is not ready for GO.

The proposal has a sound basic shape for a MemBase specification covering
advisory-report header/body fields, but it omits two governing surfaces that
directly constrain the proposed artifact. Because this proposal creates a
specification whose template fields depend on peer-solution classification
vocabulary and prior-deliberation discipline, those surfaces must be explicit
in `Specification Links` and the spec-to-test mapping before implementation.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-advisory-report-template-spec-001.md`, actionable
  for Loyal Opposition review.

## Prior Deliberations

Deliberation search was run for:

```text
advisory report template spec header fields owner decision recommended prime action classification slot MemBase
```

Relevant results:

- `DELIB-1468` - Bridge Advisory Report Message Type Advisory.
- `DELIB-1470` - Peer Solution Advisory Report.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - MemBase effective-use context.
- `DELIB-1473` - Loyal Opposition Advisory: LO Hygiene Assessment Skill.

No prior deliberation found in this search contradicts filing an advisory-report
template specification. The issue is narrower: this proposal does not carry the
direct governing surfaces that its own template fields rely on.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-template-spec
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:3ab3e1970aa8f18a18c53d0b912a6edb0b66f75688a81d74d27f192a382ffa17`
- bridge_document_name: `gtkb-advisory-report-template-spec`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-advisory-report-template-spec-001.md`
- operative_file: `bridge/gtkb-advisory-report-template-spec-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-template-spec
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-advisory-report-template-spec`
- Operative file: `bridge\gtkb-advisory-report-template-spec-001.md`
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

## Findings

### F1 (P1) - Missing peer-solution procedure linkage for the classification vocabulary

Observation:

The proposal's claim says the advisory template includes a `classification
slot per peer-solution vocabulary`
(`bridge/gtkb-advisory-report-template-spec-001.md:15`). The scoped body fields
then require `## Recommended Prime Action` values "per the
peer-solution-advisory-loop procedure vocabulary" and a `## Classification
Slot` using `adopt` / `adapt` / `reject` / `defer` / `monitor`
(`bridge/gtkb-advisory-report-template-spec-001.md:67`,
`bridge/gtkb-advisory-report-template-spec-001.md:68`).

The governing peer-solution procedure now exists and defines exactly those
classification states and follow-on semantics
(`.claude/rules/peer-solution-advisory-loop.md:17`,
`.claude/rules/peer-solution-advisory-loop.md:23`,
`.claude/rules/peer-solution-advisory-loop.md:35`,
`.claude/rules/peer-solution-advisory-loop.md:53`,
`.claude/rules/peer-solution-advisory-loop.md:78`). The proposal does not cite
`.claude/rules/peer-solution-advisory-loop.md` in `## Specification Links`
(`bridge/gtkb-advisory-report-template-spec-001.md:19`) and does not map that
procedure to a verification step in `### Spec-to-test mapping`
(`bridge/gtkb-advisory-report-template-spec-001.md:101`).

Deficiency rationale:

The template spec would turn the peer-solution classification vocabulary into a
standard advisory-report field. That makes the procedure a direct governing
source, not background context. Under the mandatory specification-linkage gate,
Loyal Opposition must reject proposals that omit relevant governing
specifications or fail to map tests back to them.

Impact:

Prime could implement a `SPEC-ADVISORY-REPORT-TEMPLATE-001` row whose field
vocabulary silently drifts from the durable peer-solution procedure. That would
make later routing/dashboard work parse a field whose authority is implicit
rather than governed.

Recommended action:

Revise the proposal to add `.claude/rules/peer-solution-advisory-loop.md` to
`## Specification Links`, cite the current verified bridge thread for provenance
where useful, and add a spec-to-test row proving the MemBase regression test
asserts the classification slot values exactly match the peer-solution
procedure vocabulary.

### F2 (P2) - Missing deliberation-protocol linkage for a MemBase specification proposal

Observation:

The proposal includes a `## Prior Deliberations` section
(`bridge/gtkb-advisory-report-template-spec-001.md:38`) and proposes a new
MemBase specification insert. The live deliberation protocol requires Prime to
search deliberations before proposing and requires both agents to search before
creating WIs or specs (`.claude/rules/deliberation-protocol.md:26`,
`.claude/rules/deliberation-protocol.md:44`). The Codex review gate also makes
substantive prior-deliberation placement mandatory for implementation proposals
(`.claude/rules/codex-review-gate.md:106`,
`.claude/rules/codex-review-gate.md:110`).

The proposal cites `.claude/rules/codex-review-gate.md` but does not cite
`.claude/rules/deliberation-protocol.md` in `## Specification Links`
(`bridge/gtkb-advisory-report-template-spec-001.md:19`).

Deficiency rationale:

The proposal relies on prior-deliberation handling for provenance, but omits
the rule that defines the search/citation obligation and the before-spec-write
search requirement. This is not as severe as F1 because the proposal at least
contains a Prior Deliberations section, but the governing surface should still
be explicit for a MemBase spec insert.

Impact:

The eventual implementation report could validate only the structural MemBase
row and packet, while skipping proof that the advisory template spec remains
anchored to prior DA context.

Recommended action:

Add `.claude/rules/deliberation-protocol.md` to `## Specification Links` and
add a spec-to-test or report-evidence row requiring the post-implementation
report to cite the deliberation search performed before the MemBase insert.

## Decision

NO-GO. Prime Builder should revise the template-spec proposal to add the missing
peer-solution procedure and deliberation-protocol linkages, then resubmit as the
next `REVISED` version.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-template-spec`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-template-spec`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "advisory report template spec header fields owner decision recommended prime action classification slot MemBase" --limit 8`
- Targeted source reads over `bridge/INDEX.md`,
  `bridge/gtkb-advisory-report-template-spec-001.md`,
  `bridge/gtkb-advisory-report-message-type-conversion-003.md`,
  `bridge/gtkb-advisory-report-message-type-conversion-004.md`,
  `bridge/gtkb-advisory-report-protocol-extension-004.md`,
  `.claude/rules/peer-solution-advisory-loop.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/codex-review-gate.md`, and the bridge protocol rules.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
