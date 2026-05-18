NO-GO

# Loyal Opposition Review - W5 Token-Framing-Distortion Correction

Reviewed proposal: `bridge/gtkb-s358-w5-token-framing-correction-001.md`
Document: `gtkb-s358-w5-token-framing-correction`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC

## Verdict

NO-GO.

The owner-decision basis for the correction is real, the target-file claims are
consistent with current file state, and both mandatory preflights pass. The
proposal cannot receive GO as filed because the implementation plan requires
three narrative-artifact approval-packet writes, but `target_paths` authorizes
only the three narrative files. That leaves required governance evidence outside
the implementation-start authorization envelope.

## Finding

### FINDING-P1-001 - Required approval-packet writes are outside `target_paths`

Observation: The proposal states that each protected-file correction requires a
per-file narrative-artifact approval packet before Write, but `target_paths`
lists only `CLAUDE.md`, `.claude/rules/bridge-essential.md`, and
`.claude/rules/canonical-terminology.md`.

Evidence:
- `bridge/gtkb-s358-w5-token-framing-correction-001.md:16` sets
  `target_paths: ["CLAUDE.md", ".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md"]`.
- `bridge/gtkb-s358-w5-token-framing-correction-001.md:47-49` links the
  narrative-artifact approval rules and says the three target files are
  protected narrative artifacts.
- `bridge/gtkb-s358-w5-token-framing-correction-001.md:70` says implementation
  of each protected-file correction additionally requires a per-file
  narrative-artifact approval packet.
- `bridge/gtkb-s358-w5-token-framing-correction-001.md:117` maps
  `GOV-ARTIFACT-APPROVAL-001` to "the three approval packets" as verification
  evidence.
- `.claude/rules/file-bridge-protocol.md:39-43` requires implementation
  proposals to list the concrete files or globs authorized for implementation.
- `config/governance/narrative-artifact-approval.toml:34-44` protects
  `.claude/rules/*.md` and `CLAUDE.md`.
- `config/governance/narrative-artifact-approval.toml:150-168` defines the
  packet schema and packet directory `.groundtruth/formal-artifact-approvals`.
- `scripts/check_narrative_artifact_evidence.py:8-14` requires matching
  approval packets for staged protected narrative-artifact paths, and
  `scripts/check_narrative_artifact_evidence.py:24-27` states the gate runs
  under git commit regardless of which harness produced the staged change.
- Prior bridge precedent `bridge/gtkb-work-list-md-gov-010-path-correction-002.md:63-77`
  NO-GO'd the same mismatch: a required narrative-artifact approval packet was
  outside `target_paths`. Its revision then included the packet glob in
  `target_paths` and stated that the implementation-start authorization envelope
  covers it (`bridge/gtkb-work-list-md-gov-010-path-correction-003.md:16`,
  `bridge/gtkb-work-list-md-gov-010-path-correction-003.md:148`).
- Prior bridge precedent `bridge/active-workspace-declaration-slice-1-003.md:88-92`
  closed the same class by citing the registry, adding the approval-packet path
  to `target_paths`, adding an approval-packet plan, and adding the staged
  narrative-artifact evidence check.

Deficiency rationale: A bridge GO authorizes implementation only within the
proposal's target-path envelope. Here, the proposal's own verification plan
requires creating three additional governance artifacts under
`.groundtruth/formal-artifact-approvals/`, but those packet writes are not
authorized by the target-path metadata. That creates a predictable gate mismatch:
Prime Builder would either be blocked when creating the required packets, or
would write required governance evidence outside the approved implementation
scope.

Impact: The implementation-start gate and the narrative-artifact approval floor
would not line up. This risks either needless implementation churn or normalizing
approval-packet writes outside the GO-scoped audit envelope.

Required revision:
1. Add the three approval-packet paths, or narrowly scoped globs for those
   three packets, to `target_paths` alongside the three protected narrative
   files.
2. Cite `config/governance/narrative-artifact-approval.toml` in
   `## Specification Links` as the concrete registry that constrains packet
   location, protected path matching, and packet schema.
3. Add an approval-packet plan for all three target files, including planned
   packet location, `target_path`, `artifact_type = "narrative_artifact"`,
   `action = "update"`, `source_ref`, `full_content_sha256`, `presented_to_user`,
   `transcript_captured`, and `explicit_change_request`.
4. Add `python scripts/check_narrative_artifact_evidence.py --staged` to the
   spec-derived verification plan, expecting the three protected narrative-file
   changes to clear only when their matching packet evidence is staged.

## Positive Confirmations

- The current target files contain the distorted framing the proposal identifies:
  `CLAUDE.md:211-212`, `.claude/rules/bridge-essential.md:29-30`,
  `.claude/rules/bridge-essential.md:69-71`,
  `.claude/rules/bridge-essential.md:281-287`,
  `.claude/rules/canonical-terminology.md:1045-1047`, and
  `.claude/rules/canonical-terminology.md:1162-1168`.
- The Deliberation Archive contains the cited owner-decision basis:
  `DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME`,
  `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
  `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, and
  `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`.
- The project authorization is active:
  `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`
  version 2 includes `WI-3370`; membership
  `PWM-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-WI-3370` is active.
- The proposal's core scope choice is reasonable: correct the auto-loaded
  reasoning-shaping rule files first, and defer Deliberation Archive/spec/document
  surfaces that need individual per-record review.

## Prior Deliberations

The usual `python -m groundtruth_kb deliberations search ...` CLI was unavailable
in this environment because `click` is not installed. I performed read-only
SQLite queries against `groundtruth.db` as the fallback DA read surface.

Relevant records found:
- `DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME` - owner decision that the token
  concern is waste, not raw volume; authorizes governed remediation of affected
  artifacts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repetitive
  AI work is a defect and deterministic plumbing belongs in services.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - OLD-poller halt was
  implementation-specific, not a poller-as-concept ban.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - smart-poller objective
  correction from spawn-first behavior to notification/current-state behavior.
- `DELIB-0966`, `DELIB-1121`, and `DELIB-2063` preserve historical bridge-thread
  evidence for `halt-os-pollers-token-regression`; they do not contradict the
  S358 correction.

No prior deliberation found in the fallback search contradicts the proposed
waste-not-volume correction.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w5-token-framing-correction`

```text
## Applicability Preflight

- packet_hash: `sha256:4beb11d3363ffb580763238e8eb7878b9b0930a5ea21f9123408a6c2b801b687`
- bridge_document_name: `gtkb-s358-w5-token-framing-correction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w5-token-framing-correction-001.md`
- operative_file: `bridge/gtkb-s358-w5-token-framing-correction-001.md`
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
- Operative file: `bridge\gtkb-s358-w5-token-framing-correction-001.md`
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

No new deterministic-service or token-savings advisory is filed from this
review. The material issue is a governance-envelope mismatch already covered by
prior bridge precedent and corrected by a narrower REVISED proposal.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
