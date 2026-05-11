NO-GO

# Loyal Opposition Review - Claude AXIS 2 UserPromptSubmit Bridge Surface

bridge_kind: loyal_opposition_verdict
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`
Verdict: NO-GO

## Claim

The proposed UserPromptSubmit hook is directionally the right Claude-side
mechanism for in-session AXIS 2 surfacing. It avoids the rejected periodic
spawn/Routine design and uses Claude's native prompt-time hook surface.

It cannot receive GO as written because it would create and activate a new
bridge automation while deferring two required canonicalization surfaces:
`config/agent-control/system-interface-map.toml` and the overlapping
`.claude/rules/bridge-essential.md` AXIS 2 section. The proposal also does not
carry an explicit AskUserQuestion owner-approval reference for adding a new
bridge automation, even though `bridge-essential.md` requires one.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from
  `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW:
  bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review for:

```text
Claude AXIS 2 UserPromptSubmit bridge surface active session notification bridge automation
bridge-essential adding new bridge automation owner approval system-interface-map Axis 2
UserPromptSubmit owner-decision-tracker hook pending owner decisions Claude hook
```

Relevant prior-decision evidence:

- `DELIB-1517` and `DELIB-1516` - prior NO-GO reviews on
  `gtkb-claude-code-bridge-status-thread-automation-001`; these rejected the
  cloud/Desktop scheduler conflation and support the proposal's move away from
  periodic-spawn automation.
- `DELIB-1520` - VERIFIED record for trigger-awareness and the two-axis bridge
  automation model.
- `DELIB-1521` - GO on the two-axis bridge automation articulation; approved
  pattern-level documentation without ratifying concrete automations.
- `DELIB-0121` - historical Codex bridge ops/reporting automation context, not
  a current approval for this Claude-side automation.
- `DELIB-1527` - owner-decision tracker pattern bounds; relevant precedent for
  UserPromptSubmit hooks that surface owner/decision state at prompt time.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:299a36d995f8efdc820ff364486476e332187f2b7e26cbf75ea7e6848a28ea5c`
- bridge_document_name: `gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`
- operative_file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- Operative file: `bridge\gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`
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

## Findings

### F1 - P1 - New bridge automation canonicalization is deferred past activation

Observation:

- The proposal implements an active Claude-side bridge automation by adding
  `.claude/hooks/bridge-axis-2-surface.py` and registering it in
  `.claude/settings.json`
  (`bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`,
  IP-1 through IP-3).
- `.claude/rules/bridge-essential.md` says adding a new bridge automation
  requires owner approval, axis classification, a new `[[systems]]` entry in
  `config/agent-control/system-interface-map.toml`, and an update to that
  section if the new automation overlaps an existing surface
  (`.claude/rules/bridge-essential.md:148-158`).
- The proposal omits `config/agent-control/system-interface-map.toml` from
  `Specification Links`, omits a system-interface-map update from "Files
  Expected To Change", and has no verification for a new system inventory row.
- The proposal explicitly defers the `.claude/rules/bridge-essential.md`
  update to a follow-on slice, even though this hook directly implements the
  "future Claude-native equivalent" in the current AXIS 2 section
  (`.claude/rules/bridge-essential.md:137-140`).

Deficiency rationale:

The bridge automation rule is not merely documentation after the fact. It is a
creation contract for new bridge automation. If this slice receives GO as
written, Prime can activate a new UserPromptSubmit automation while the
authoritative system map still lacks the concrete automation row and the
canonical AXIS 2 rule still says the Claude-native equivalent is future work.
That creates a live-runtime / canonical-inventory mismatch on the bridge
surface the proposal exists to repair.

Impact:

Dashboard/startup readers and future bridge reviews would see stale authority:
an active Claude AXIS 2 hook in `.claude/settings.json`, but no
system-interface-map row and no updated `bridge-essential.md` ownership of the
new overlap. This is exactly the kind of bridge-function drift the
bridge-essential rule is meant to prevent.

Recommended action:

Revise the proposal so the implementation slice either:

1. includes the required `config/agent-control/system-interface-map.toml` row
   and the overlapping `.claude/rules/bridge-essential.md` update, with the
   required narrative-artifact approval packet for the protected rule file; or
2. splits the work so a prior scoping/canonicalization thread obtains GO for
   those required surfaces before the active hook registration is implemented.

The revised spec-to-test mapping should verify the system map row, hook
registration, and updated AXIS 2 wording together.

Decision needed from owner: none for this NO-GO. An owner waiver of the
canonicalization timing would need to be explicit and cited.

### F2 - P1 - Required owner approval for adding bridge automation is not cited as AskUserQuestion evidence

Observation:

`.claude/rules/bridge-essential.md` requires "Owner approval via
AskUserQuestion" before adding new bridge automation
(`.claude/rules/bridge-essential.md:148-154`). The proposal cites an owner
directive that closing the gap is important and an AUQ autonomous-execution
directive, but it does not cite an AskUserQuestion decision specifically
approving creation of this new bridge automation.

Deficiency rationale:

The autonomous-execution directive is broad authorization to proceed through
the queue with little input. It is not the same as the specific approval named
by `bridge-essential.md` for adding a new bridge automation. Because this
proposal depends on that approval, the `Owner Decisions / Input` section needs
the exact AskUserQuestion evidence or an explicit owner waiver.

Impact:

GO would treat general urgency/automation instructions as a substitute for the
canonical owner-decision channel on bridge automation. That weakens the audit
boundary for one of GT-KB's highest-priority control surfaces.

Recommended action:

Revise the `Owner Decisions / Input` section to cite the specific
AskUserQuestion approval for this Claude AXIS 2 automation, or obtain and cite
one before resubmission. If the owner intends the S341 directive to waive the
AUQ-specific approval requirement, cite that as an explicit waiver.

Decision needed from owner: none for this NO-GO. Prime Builder can request the
specific approval in a revised path if needed.

## Positive Confirmations

- The selected mechanism is better aligned with Claude's pull-based
  interaction model than the previously rejected scheduled Routine/Desktop
  proposal.
- Applicability and clause preflights pass on the operative file.
- The hook implementation and tests are correctly scoped under `E:\GT-KB`.
- Deferring the protected `.claude/rules/bridge-essential.md` edit would be
  acceptable for an investigation-only slice, but not for a slice that
  activates the new bridge automation itself.

## Decision

NO-GO. Revise to carry the required automation-canonicalization surfaces and
specific owner-approval evidence before implementing the active Claude AXIS 2
UserPromptSubmit hook.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- `$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "Claude AXIS 2 UserPromptSubmit bridge surface active session notification bridge automation" --limit 10`
- `$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "bridge-essential adding new bridge automation owner approval system-interface-map Axis 2" --limit 10`
- `$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "UserPromptSubmit owner-decision-tracker hook pending owner decisions Claude hook" --limit 10`
- Targeted reads over `bridge/INDEX.md`, the proposal, `.claude/rules/bridge-essential.md`,
  `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`,
  `config/agent-control/system-interface-map.toml`, `.claude/settings.json`,
  `scripts/cross_harness_bridge_trigger.py`, `.claude/hooks/owner-decision-tracker.py`,
  and the prior Claude bridge-status thread.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
