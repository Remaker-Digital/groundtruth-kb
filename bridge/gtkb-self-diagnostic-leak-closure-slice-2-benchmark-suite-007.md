# Implementation Proposal REVISED-3 - Benchmark Suite (Self-Diagnostic Leak Closure Slice 2)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-006.md` (F1 narrative-artifact packet schema mismatch)
Work Item: new MemBase work item to be created from this proposal under existing SPEC-1662 (GOV-18: Assertion Quality Standard) + GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 governance
target_paths: ["scripts/benchmarks/__init__.py", "scripts/benchmarks/linkage_heatmap.py", "scripts/benchmarks/recall_coverage.py", "scripts/benchmarks/tool_identification.py", "scripts/benchmarks/deliberation_recall.py", "scripts/benchmarks/advisory_latency.py", "scripts/benchmarks/assertion_signal_noise.py", "scripts/benchmarks/cli.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_benchmark_linkage_heatmap.py", "platform_tests/scripts/test_benchmark_recall_coverage.py", "platform_tests/scripts/test_benchmark_tool_identification.py", "platform_tests/scripts/test_benchmark_deliberation_recall.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_benchmark_assertion_signal_noise.py", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".claude/rules/canonical-terminology.md", ".gtkb-state/benchmarks/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json"]

## Claim

Implement six read-only benchmark scripts under existing SPEC-1662 (GOV-18: Assertion Quality Standard), GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DELIB-S312, DELIB-S341, and the INSIGHTS-2026-05-10 advisory. Glossary additions at IP-6 use the live narrative-artifact approval contract.

## Why Now

Same as -001, -003, -005.

## Changes from -005 (addressing Codex NO-GO F1)

- **F1 (narrative-artifact packet schema mismatch):** IP-6 rewritten to match the live narrative-artifact gate schema verified against `.claude/hooks/narrative-artifact-approval-gate.py`, `scripts/check_narrative_artifact_evidence.py`, and `config/governance/narrative-artifact-approval.toml:153-160`:
  - `artifact_type='narrative_artifact'` (underscore)
  - `action='update'`
  - Required fields: `target_path`, `source_ref`, `approval_mode`
  - `full_content` = complete post-edit `.claude/rules/canonical-terminology.md` content (not entry-only)
  - Verification: `scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage).
- GOV-19 OUTSIDE-IN-TESTING.
- GOV-STANDING-BACKLOG-001.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.
- ADR-DA-READ-SURFACE-PLACEMENT-001.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.
- DCL-CONCEPT-ON-CONTACT-001 - "benchmark", "linkage heat map", "advisory latency", "metric snapshot" are new load-bearing concepts; IP-6 places entries in canonical-terminology.md.
- GOV-ARTIFACT-APPROVAL-001 - protected narrative-artifact edit at IP-6 requires the per-artifact approval packet.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §3.
- `.claude/rules/peer-solution-advisory-loop.md`.
- `.claude/rules/canonical-terminology.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

## Prior Deliberations

- S349 self-diagnostic investigation.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.
- DELIB-1469, DELIB-S321-TRIAD-COMPLETENESS, DELIB-1212, DELIB-0731.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-1512, DELIB-1513 - prior review history around DCL-CONCEPT-ON-CONTACT-001.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md - Codex NO-GO at -002.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-004.md - Codex NO-GO at -004.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-006.md - Codex NO-GO at -006 (addressed here).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" + "parallelize this work to the maximum extent possible".
- 2026-05-13 UTC, S349: Codex returned NO-GO three times (-002, -004, -006); this REVISED-3 addresses the latest finding.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient. Same as -005.

## Current Implementation Baseline

Unchanged from -005. Additionally:

- Narrative-artifact gate schema verified against `.claude/hooks/narrative-artifact-approval-gate.py`, `scripts/check_narrative_artifact_evidence.py`, `config/governance/narrative-artifact-approval.toml`.

## Proposed Scope

### IP-1: Implement shared common module

Same as -005.

### IP-2: Implement six benchmark scripts

Same as -005.

### IP-3: Implement CLI

Same as -005.

### IP-4: Tests

Same as -005.

### IP-5: Add gtkb-benchmarks skill

Same as -005.

### IP-6: Add canonical glossary entries for benchmark-suite concepts (CORRECTED narrative-artifact schema)

1. Read current `.claude/rules/canonical-terminology.md` content.

2. Compute post-edit content by inserting four entries (`benchmark`, `linkage heat map`, `advisory latency`, `metric snapshot` - definitions per -005 IP-6) under "## GT-KB DA Read-Surface and Operational Vocabulary".

3. Compute `full_content_sha256` over the complete post-edit content.

4. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json` with the live narrative-artifact schema:

   ```json
   {
     "artifact_type": "narrative_artifact",
     "action": "update",
     "target_path": ".claude/rules/canonical-terminology.md",
     "source_ref": "bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-007.md",
     "approval_mode": "approve",
     "full_content": "<complete post-edit canonical-terminology.md content>",
     "full_content_sha256": "<sha256 of complete post-edit content>",
     "presented_to_user": true,
     "transcript_captured": true,
     "explicit_change_request": "S349 AUQ 'File both, sequenced' + 'parallelize this work to the maximum extent possible'",
     "changed_by": "prime-builder/claude/B",
     "change_reason": "DCL-CONCEPT-ON-CONTACT-001 compliance for benchmark-suite concepts introduced by gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite",
     "approved_by": "owner"
   }
   ```

5. Set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var to packet path before Edit.

6. Edit `.claude/rules/canonical-terminology.md` to byte-equality with the post-edit content.

7. Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` to verify.

## Tests

Per -005 §"Tests".

## Verification Plan

Per -005 with these corrections:

- Verify packet uses `artifact_type='narrative_artifact'` (underscore), `action='update'`, `target_path`, `source_ref`, `approval_mode`.
- Verify `full_content` equals complete post-edit canonical-terminology.md content.
- Verify `full_content_sha256` matches.
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
