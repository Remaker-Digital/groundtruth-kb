# Implementation Proposal REVISED-3 - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-006.md` (F1 narrative-artifact packet schema mismatch)
Work Item: this proposal authorizes creation of one MemBase work_item (origin='hygiene', source_spec_id='SPEC-1662') at IP-7
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py", ".claude/skills/assertion-triage/SKILL.md", ".codex/skills/assertion-triage/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".claude/rules/canonical-terminology.md", "groundtruth.db", ".gtkb-state/assertion-triage/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-assertion-category-entries.json"]

## Claim

Implement assertion signal/noise categorization under existing SPEC-1662 (GOV-18) + GOV-15. Categorization is read-only inference over `assertion_runs`. The slice creates one tracking MemBase `work_item` (origin='hygiene', source_spec_id='SPEC-1662'). Glossary additions at IP-6 use the live narrative-artifact approval contract.

## Why Now

Same as -001, -003, -005.

## Changes from -005 (addressing Codex NO-GO F1)

- **F1 (narrative-artifact packet schema mismatch):** IP-6 rewritten to match the live narrative-artifact gate schema verified against `.claude/hooks/narrative-artifact-approval-gate.py`, `scripts/check_narrative_artifact_evidence.py`, and `config/governance/narrative-artifact-approval.toml`:
  - `artifact_type='narrative_artifact'` (underscore)
  - `action='update'`
  - Required fields: `target_path`, `source_ref`, `approval_mode`
  - `full_content` = complete post-edit canonical-terminology.md content (not entry-only)
  - Verification: `scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage).
- GOV-03 TEST-CLARITY.
- GOV-15 TEST-FIX-GATE.
- GOV-STANDING-BACKLOG-001.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.
- DCL-CONCEPT-ON-CONTACT-001 - "assertion category", "genuine_drift", "chronic_noise", "flaky" are new load-bearing concepts; IP-6 places entries in canonical-terminology.md.
- GOV-ARTIFACT-APPROVAL-001 - protected narrative-artifact edit at IP-6 requires the per-artifact approval packet.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §1.
- `.claude/rules/canonical-terminology.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` §127-130 (one-at-a-time owner-action protocol).
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

## Prior Deliberations

- S349 self-diagnostic investigation.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.
- DELIB-1469.
- DELIB-0473 - prior pipeline hardening advisory.
- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-1512, DELIB-1513 - prior review history around DCL-CONCEPT-ON-CONTACT-001.
- DELIB-1559, DELIB-1561, DELIB-1563, DELIB-1575 - per Codex round 3 finding evidence; prior narrative-artifact / glossary backfill reviews.
- DELIB-1595 - canonical terminology system and bounded context model advisory.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- Prior MEMORY.md handoffs (S347, S348) - cite "224/1687 PASS and 1463 FAIL".
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md - Codex NO-GO at -002.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-004.md - Codex NO-GO at -004.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-006.md - Codex NO-GO at -006 (addressed here).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" + "parallelize this work to the maximum extent possible".
- 2026-05-13 UTC, S349: Codex returned NO-GO three times (-002, -004, -006); this REVISED-3 addresses the latest finding.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient. Same as -005.

## Current Implementation Baseline

Unchanged from -005. Additionally:

- Narrative-artifact gate schema verified against live hook code and config.

## Proposed Scope

### IP-1: Implement categorization script

Same as -005.

### IP-2: Implement retirement workflow with one-at-a-time AUQ

Same as -005.

### IP-3: Wire into assertion-check hook (advisory display only)

Same as -005.

### IP-4: Tests

Same as -005.

### IP-5: Add assertion-triage skill

Same as -005.

### IP-6: Add canonical glossary entries for assertion-category concepts (CORRECTED narrative-artifact schema)

1. Read current `.claude/rules/canonical-terminology.md` content.

2. Compute post-edit content by inserting four entries (`assertion category`, `genuine_drift`, `chronic_noise`, `flaky` - definitions per -005 IP-6) under "## GT-KB DA Read-Surface and Operational Vocabulary".

3. Compute `full_content_sha256` over complete post-edit content.

4. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-assertion-category-entries.json` with the live narrative-artifact schema:

   ```json
   {
     "artifact_type": "narrative_artifact",
     "action": "update",
     "target_path": ".claude/rules/canonical-terminology.md",
     "source_ref": "bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md",
     "approval_mode": "approve",
     "full_content": "<complete post-edit canonical-terminology.md content>",
     "full_content_sha256": "<sha256 of complete post-edit content>",
     "presented_to_user": true,
     "transcript_captured": true,
     "explicit_change_request": "S349 AUQ 'File both, sequenced' + 'parallelize this work to the maximum extent possible'",
     "changed_by": "prime-builder/claude/B",
     "change_reason": "DCL-CONCEPT-ON-CONTACT-001 compliance for assertion-category concepts introduced by gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage",
     "approved_by": "owner"
   }
   ```

5. Set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var to packet path before Edit.

6. Edit `.claude/rules/canonical-terminology.md` to byte-equality.

7. Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.

### IP-7: Create tracking work_item

Same as -005.

## Tests

Per -005 §"Tests".

## Verification Plan

Per -005 with these corrections:

- Verify packet uses `artifact_type='narrative_artifact'` (underscore), `action='update'`, `target_path`, `source_ref`, `approval_mode`.
- Verify `full_content` equals complete post-edit canonical-terminology.md content.
- Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.
- Carry forward applicability and clause preflight outputs from -005.

## Risks and Rollback

Per -005.

## Sequenced Follow-Ons

Per S349 parallelization directive.

## Recommended Commit Type

`feat:`.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links`, `## Prior Deliberations`, `## Owner Decisions / Input`.
- `target_paths` consistent with all writes.
- `## Requirement Sufficiency` single state.
- `## Recommended Commit Type`.
- explicit `Changes from -005` section.
- Narrative-artifact schema corrected per Codex round 3.
