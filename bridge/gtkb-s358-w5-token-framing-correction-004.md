GO

# Loyal Opposition Review - W5 Token-Framing-Distortion Correction REVISED

Reviewed proposal: `bridge/gtkb-s358-w5-token-framing-correction-003.md`
Document: `gtkb-s358-w5-token-framing-correction`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC

## Verdict

GO.

The `-003` revision resolves the single `-002` NO-GO finding. The implementation
scope now includes the three protected narrative files and the three required
narrative-artifact approval-packet globs, cites the approval-packet registry,
adds a concrete packet plan, and carries the staged narrative-artifact evidence
check into the spec-derived verification plan.

No new blocking finding remains.

## Review Evidence

- `bridge/gtkb-s358-w5-token-framing-correction-003.md:16` extends
  `target_paths` with `.groundtruth/formal-artifact-approvals/*-claude-md.json`,
  `.groundtruth/formal-artifact-approvals/*-claude-rules-bridge-essential-md.json`,
  and `.groundtruth/formal-artifact-approvals/*-claude-rules-canonical-terminology-md.json`.
- `bridge/gtkb-s358-w5-token-framing-correction-003.md:50-61` carries the
  bridge, implementation-proposal, verification, artifact-approval, project-linkage,
  and in-root specification links, including
  `config/governance/narrative-artifact-approval.toml`.
- `bridge/gtkb-s358-w5-token-framing-correction-003.md:73-77` contains the
  required owner-decision section and explicitly says per-file narrative-artifact
  approval is still collected at implementation time, not pre-granted by this GO.
- `bridge/gtkb-s358-w5-token-framing-correction-003.md:96-106` defines the three
  planned approval packets and the expected schema fields.
- `bridge/gtkb-s358-w5-token-framing-correction-003.md:130-141` maps the linked
  specifications to verification, including
  `python scripts/check_narrative_artifact_evidence.py --staged`.
- `bridge/gtkb-s358-w5-token-framing-correction-003.md:143-150` includes acceptance
  criteria for preserving incident facts, preserving do-not-re-enable/manual-scan
  controls, and passing both bridge preflights.
- Current target-file search confirms the distorted framing is still present in
  the target surface and therefore remains a real implementation target:
  `CLAUDE.md:211-212`, `.claude/rules/bridge-essential.md:30`,
  `.claude/rules/bridge-essential.md:69`, `.claude/rules/bridge-essential.md:282`,
  `.claude/rules/bridge-essential.md:286`,
  `.claude/rules/canonical-terminology.md:1046`, and
  `.claude/rules/canonical-terminology.md:1167`.
- Project authorization is current: latest version 2 of
  `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`
  is active, includes `WI-3370`, has no expiry, and the
  `PWM-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-WI-3370` membership is active.

## Prior Deliberations

I performed the required Deliberation Archive search using read-only SQLite
queries against `groundtruth.db` in this harness.

Relevant records:

- `DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME` - owner decision that GT-KB's
  token concern is wasted, blind, or repetitive work, not raw token volume;
  authorizes governed remediation of affected artifacts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repetitive
  AI work is a defect and deterministic plumbing belongs in services.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - owner decision that the old
  poller halt was implementation-specific, not a poller-as-concept ban.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - owner decision correcting
  the smart-poller objective from spawn-first behavior to notification/current
  state behavior.

No relevant prior deliberation found in the search contradicts the
waste-not-volume correction or the bounded scope of this proposal.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w5-token-framing-correction`

```text
## Applicability Preflight

- packet_hash: `sha256:dc0ad34f349f01aa29d09cf5f04a8868907ed42eb085f0f9e328bbfd7d204e5c`
- bridge_document_name: `gtkb-s358-w5-token-framing-correction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w5-token-framing-correction-003.md`
- operative_file: `bridge/gtkb-s358-w5-token-framing-correction-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w5-token-framing-correction`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s358-w5-token-framing-correction`
- Operative file: `bridge\gtkb-s358-w5-token-framing-correction-003.md`
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

## Opportunity Radar

No separate opportunity advisory is filed from this review. The relevant
deterministic-service principle is already the substance of the proposal, and
the remaining implementation work requires owner-visible artifact approval and
human judgement over exact narrative wording.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
