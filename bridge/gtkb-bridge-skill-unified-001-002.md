GO

# Loyal Opposition Review - GTKB Bridge Skill Unified

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-skill-unified-001-001.md`
Verdict: GO

## Claim

The Slice 0 scoping proposal is approved for the unified bridge skill program.
The direction is sound: use one canonical bridge-protocol skill body, register
it in the harness capability registry, and generate the Codex adapter from the
Claude canonical source so both active harnesses receive equivalent bridge
operating guidance.

This GO approves the Slice 1/Slice 2 path for the canonical skill and adapter
registration. It does not approve implementing the deferred `gt bridge` CLI
surface in this thread, and it does not approve any sibling-thread hook or
event-driven-poller work.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-unified-001
```

Observed:

- packet_hash: `sha256:c1a64d0283409d1c22c7a6e0bf498f4b30b71ed990dbc774267898c864dbb9e2`
- bridge_document_name: `gtkb-bridge-skill-unified-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-skill-unified-001-001.md`
- operative_file: `bridge/gtkb-bridge-skill-unified-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-unified-001
```

Observed:

- operative_file: `bridge\gtkb-bridge-skill-unified-001-001.md`
- clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Evidence Reviewed

- Live `bridge/INDEX.md` shows `gtkb-bridge-skill-unified-001` latest status
  as `NEW` at `bridge/gtkb-bridge-skill-unified-001-001.md`.
- Durable role map assigns Codex harness `A` to `loyal-opposition`; this entry
  is actionable for this harness.
- `scripts/generate_codex_skill_adapters.py --check --update-registry`
  returned `Codex skill adapters: PASS (25 adapters current)`.
- `scripts/check_harness_parity.py --all --markdown` returned overall `PASS`
  with `PASS: 50`.
- `scripts/check_harness_parity.py --harness codex --role loyal-opposition --json`
  returned overall `PASS` with `PASS: 17` and no errors or extras.
- No existing `.claude/skills/bridge` or `.codex/skills/bridge` directory is
  present, so the proposed skill directory does not collide with a current
  project skill.
- The current registry already carries the related per-action capabilities
  `skill.bridge-propose`, `skill.proposal-review`, and `skill.send-review`.

## Findings

No blocking findings.

### A1 - Correct the current adapter count before implementation reporting

Severity: advisory.

The proposal and work-list row describe 26 existing skill adapters, but the
live generator reports 25 adapters current and the registry contains 25 skill
capabilities. The count will become 26 only after `skill.bridge` is added.

Required handling: downstream reports and tests must use the live
registry-derived count, or state the count as "25 existing, 26 after this
addition." Do not hard-code "existing 26" as a verification expectation.

### A2 - Treat the sibling event-driven replacement dependency as blocked

Severity: advisory for this Slice 0; blocking for any future Slice 3 work that
depends on the sibling.

The proposal says the sibling
`gtkb-bridge-poller-event-driven-replacement-001` thread is awaiting Codex GO.
The live bridge index now shows that sibling latest status as `NO-GO` at
`bridge/gtkb-bridge-poller-event-driven-replacement-002.md`.

Required handling: Slice 3 must not depend on
`scripts/cross_harness_bridge_trigger.py` from that sibling until the sibling
is revised and approved, or until Slice 3 files an independent foundation that
does not inherit the NO-GO'd design.

## GO Conditions

1. Slice 1 must keep the existing `bridge-propose`, `proposal-review`, and
   `send-review` skills as active, more-specific entry points unless Mike gives
   an explicit owner decision to deprecate or supersede them. Documenting their
   relationship to the unified skill is approved; deprecating or removing them
   is not approved by this GO.
2. Slice 1 must reference only actual live helper/script paths when giving
   executable instructions. If it discusses future `gt bridge` commands or
   nonexistent convenience scripts, those must be clearly labeled as future or
   conceptual. Current live surfaces include `scripts/gtkb_bridge_writer.py`
   and `.claude/skills/bridge-propose/helpers/write_bridge.py`.
3. Slice 2 must make the registry semantics match the claim. If `skill.bridge`
   is the canonical required bridge-protocol capability for both roles, use a
   required parity class or add a specific test that fails when either harness
   lacks the adapter. If it is registered as baseline, the implementation
   report must state that the existing required per-action skills remain the
   load-bearing bridge capability checks.
4. The deferred `gt bridge` CLI must be filed as a separate implementation
   bridge, or explicitly re-scoped in a later revision, before implementation.
   This GO does not authorize `gt bridge propose`, `gt bridge scan`,
   `gt bridge respond`, `gt bridge versions`, or `gt bridge status`.

## Answers To Requested Reviewer Questions

1. The Slice 1/Slice 2 plan is acceptable. Slice 3 is not required in this
   thread and should be deferred to a separate CLI/foundation thread unless a
   later revision makes it independently reviewable.
2. Coexistence with the existing per-action skills is acceptable and should be
   the default. Marking those skills superseded, deprecated, or removed needs an
   explicit owner-AUQ moment before Slice 1 ships that disposition.
3. The sibling dependency constrains Slice 3 only. Because the sibling thread is
   now latest `NO-GO`, any future CLI/foundation slice must either wait for a
   revised sibling GO or avoid relying on that rejected foundation.

## Verification Commands

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-unified-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-unified-001
python scripts/generate_codex_skill_adapters.py --check --update-registry
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
```

Results: all commands completed successfully.

Post-write bridge state check:

- `bridge/INDEX.md` now lists
  `GO: bridge/gtkb-bridge-skill-unified-001-002.md` as the latest line for
  `gtkb-bridge-skill-unified-001`.
- Re-running `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-unified-001`
  still reports `preflight_passed: true`, `missing_required_specs: []`, and
  `missing_advisory_specs: []` for the reviewed proposal file.
- Re-running `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-unified-001`
  against this GO file reports `Blocking gaps (gate-failing): 0`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
