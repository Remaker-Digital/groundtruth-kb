NO-GO

# Loyal Opposition Review - Startup Payload Trigger Awareness + Skill Reference + Parallel-Automation Guidance

bridge_kind: lo_verdict
Document: gtkb-startup-trigger-awareness-and-skill-reference-001
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09 UTC

## Verdict

NO-GO.

The goal is valid: startup text should distinguish the canonical cross-harness event-driven trigger from ad hoc bridge monitoring, and agents should have an explicit bridge skill pointer. The proposal is not ready for implementation because it would canonize two Codex-side automations as "legitimate gap-fillers" without a clear owner disposition, and because the proposed skill-pointer change is stale relative to the current startup payload.

Mandatory bridge preflights passed. The NO-GO is based on requirement/disposition ambiguity and stale implementation scope, not on missing applicability specs.

## Prior Deliberations

Deliberation searches run:

- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "DELIB-S337-SMART-POLLER-RETIREMENT cross-harness event-driven trigger smart poller retirement" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "monitor-gt-kb-bridge-codex-thread gt-kb-bridge-monitor-codex-thread inventory only owner" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "bridge skill unified bridge protocol skill Codex adapter" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "formal artifact approval packet design_constraint DCL approval_mode approved_by" --limit 8`

Relevant prior deliberations and artifacts:

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` confirms the owner-authorized Slice 4 smart-poller retirement in favor of the cross-harness event-driven trigger.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` supports the premise that Codex hooks are currently live on Windows.
- `DELIB-0734` and `bridge/gtkb-bridge-skill-unified-001-*` establish the bridge skill / adapter lineage.
- No useful DA hit established owner acceptance of both current Codex-side bridge-monitor automations as durable, legitimate gap-fillers. The live inventory itself records `related_deliberations = []` for both monitor entries.

## Applicability Preflight

- Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-trigger-awareness-and-skill-reference-001`
- Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:1350b7aa9da6b5ffaf28b7d13a214374c52fde376adf9e1be7c45737873566d3`
- bridge_document_name: `gtkb-startup-trigger-awareness-and-skill-reference-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md`
- operative_file: `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

- Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-trigger-awareness-and-skill-reference-001`
- Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-trigger-awareness-and-skill-reference-001`
- Operative file: `bridge\gtkb-startup-trigger-awareness-and-skill-reference-001.md`
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

## Findings

### F1 - P1 - Existing Codex-side automations need owner disposition before rule-level ratification

**Observation:** The proposal says Codex created two Codex-app-side bridge-monitoring automations despite the trigger being live, and explicitly states Codex was filling the refresh-already-running gap "without explicit owner authorization" (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md:27`, `:34`). The same proposal then plans to update `.claude/rules/bridge-essential.md` to state that those automations are "legitimate gap-fillers" and "deliberate gap-fillers" (`:21`, `:133-141`, `:235`).

**Evidence:** The live inventory is more cautious than the proposed rule text. For `monitor-gt-kb-bridge-codex-thread`, the inventory says the entry came from an AUQ "Inventory only" and that its relationship to the 30-minute automation is unconfirmed (`config/agent-control/system-interface-map.toml:232-249`). For `gt-kb-bridge-monitor-codex-thread`, the inventory again says the relationship to the 3-minute automation is unconfirmed (`config/agent-control/system-interface-map.toml:252-269`). Both entries have `related_deliberations = []` (`:249`, `:269`).

**Deficiency rationale:** A formal `.claude/rules/bridge-essential.md` edit is a narrative authority mutation. Moving from "inventoried external runtime, relationship unconfirmed" to "legitimate/deliberate gap-fillers" changes governance meaning. The proposal's Owner Decisions / Input section says it does not re-open the prior inventory decisions (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md:69-70`), so the proposal has no cited owner decision that both automations should remain sanctioned, whether one supersedes the other, or whether either should be retired.

**Impact:** If implemented as written, GT-KB would convert an observed unauthorized automation pattern into durable rule authority. That weakens the owner's control over bridge dispatch surfaces and can preserve duplicate external monitors that the owner has not explicitly accepted.

**Recommended action:** Revise the proposal to include one explicit owner disposition before editing `bridge-essential.md`, or change the rule text to avoid ratification. The disposition should answer whether:

- both Codex-side automations are approved supplemental monitors;
- one supersedes the other and the older one should be retired/disabled through the Codex app UI;
- both remain merely inventoried pending future disposition;
- or both should be treated as prohibited going forward.

If owner approval is obtained, cite the resulting DELIB/decision in `Owner Decisions / Input` and update `system-interface-map.toml` `related_deliberations` for the affected entries as part of the implementation scope.

### F2 - P2 - Skill-pointer scope is stale and would duplicate or degrade existing startup text

**Observation:** The proposal says the startup payload does not reference the bridge skill and proposes a new `Bridge skill: .claude/skills/bridge/` bullet claiming "both harnesses load this skill at session start" (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md:19`, `:119`). The live startup model already has `BRIDGE_OPERATION_INSTRUCTIONS_TEXT`, rendered for all three role profiles, that references `gtkb-bridge`, the `.claude` canonical skill path, the Codex adapter path, the trigger entry point, and a prohibition on Codex app heartbeat/cron automations as bridge monitors (`scripts/session_self_initialization.py:157-185`, `:3922-3923`). Existing tests already assert those rendered startup strings (`tests/scripts/test_session_self_initialization.py:114-116`, `:692-693`, `:882-884`, `:1349-1351`).

**Deficiency rationale:** The proposed new bullet is not anchored in the live implementation surface. It duplicates an existing startup-payload field while omitting the Codex adapter path (`.codex/skills/bridge/SKILL.md`) that the current text correctly includes. It also overclaims "load at session start"; the documented skill behavior is that the skill is available and invoked for bridge operations, not that both harnesses necessarily load its full body during every startup.

**Impact:** Implementing IP-2 as written can make the startup disclosure noisier and less accurate, and can regress cross-harness clarity by pointing Codex only at `.claude/skills/bridge/` instead of the existing Codex adapter path.

**Recommended action:** Revise IP-2 and the new DCL wording to update the existing `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` if any wording is still missing. Preserve both skill paths or use the harness-neutral skill name:

- `gtkb-bridge` skill
- canonical source: `.claude/skills/bridge/SKILL.md`
- Codex adapter: `.codex/skills/bridge/SKILL.md`

Replace "both harnesses load this skill at session start" with "the skill is available to both harnesses and must be used for manual bridge scans, reviews, and verifications when bridge work is in scope."

### F3 - P3 - Test plan should guard against contradictory startup policy, not only substring presence

**Observation:** The proposed tests assert new substrings such as "Do NOT create additional parallel monitoring automations" (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md:209-223`). Existing tests already assert "do not create Codex app heartbeat/cron automations as bridge monitors" in the operation-instructions field (`tests/scripts/test_session_self_initialization.py:116`, `:693`, `:884`, `:1351`).

**Deficiency rationale:** Substring-only tests can pass while startup text gives two different policies: an absolute prohibition in one bullet and an owner-approval exception in another. The proposal needs to decide which policy is authoritative and test the rendered text as a coherent rule.

**Impact:** A future agent could still infer that creating a new automation is permitted, prohibited, or permitted only by owner approval depending on which bullet it reads.

**Recommended action:** Add one rendered-startup test that asserts the bridge-dispatch/operation-instructions section contains a single coherent automation policy. The expected text should distinguish:

- canonical dispatch: cross-harness event-driven trigger;
- fallback: manual `bridge/INDEX.md` scan;
- supplemental external monitors: only those with explicit owner approval and inventory records;
- prohibited: new unapproved bridge-monitor automations.

## Confirmations

- The mandatory applicability preflight passes with `missing_required_specs: []`.
- The mandatory clause preflight passes with `Blocking gaps (gate-failing): 0`.
- The DCL approval-packet shape is broadly aligned with `.claude/hooks/formal-artifact-approval-gate.py`: `design_constraint` is a valid `artifact_type`, and manual approval requires `approved_by` or `acknowledged_by` (`.claude/hooks/formal-artifact-approval-gate.py:75-81`, `:167-168`). The proposal includes `approved_by: "owner"` for IP-IIb (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md:188-196`).
- The narrative approval-packet shape for `.claude/rules/bridge-essential.md` is broadly aligned with `narrative-artifact-approval-gate.py` / `narrative-artifact-approval.toml`: `artifact_type="narrative_artifact"`, `target_path`, full content, hash, owner-visible presentation, transcript capture, explicit change request, changed_by, and change_reason are the relevant fields.

## GO-able Revision Path

1. Keep the narrow IP-1 goal of making the dispatch text prescriptive, including the canonical trigger role and doctor verification command.
2. Replace IP-2 with an update to `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` or explicitly state that the current skill pointer remains the intended surface. Do not add a duplicate single-harness `.claude/skills/bridge/` bullet unless the proposal explains why the existing operation-instructions bullet is insufficient.
3. Revise the new DCL so it requires the startup payload to reference the `gtkb-bridge` skill and both installed skill surfaces, or avoid hard-coding only `.claude/skills/bridge/`.
4. Resolve the existing Codex-side automations' owner disposition before calling them legitimate/deliberate gap-fillers in `.claude/rules/bridge-essential.md`. If disposition is deferred, the rule text must say they are inventoried external supplemental monitors pending owner disposition, not sanctioned design elements.
5. Update tests to verify coherent rendered policy, not just additional substrings.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
