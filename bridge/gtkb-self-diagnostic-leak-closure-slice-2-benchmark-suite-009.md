# Implementation Proposal REVISED-4 - Benchmark Suite (Self-Diagnostic Leak Closure Slice 2)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-008.md` (F1 work_item header claim without groundtruth.db target authorization)
Work Item: this proposal authorizes creation of one tracking MemBase work_item at IP-7 (origin='hygiene', source_spec_id='SPEC-1662')
target_paths: ["scripts/benchmarks/__init__.py", "scripts/benchmarks/linkage_heatmap.py", "scripts/benchmarks/recall_coverage.py", "scripts/benchmarks/tool_identification.py", "scripts/benchmarks/deliberation_recall.py", "scripts/benchmarks/advisory_latency.py", "scripts/benchmarks/assertion_signal_noise.py", "scripts/benchmarks/cli.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_benchmark_linkage_heatmap.py", "platform_tests/scripts/test_benchmark_recall_coverage.py", "platform_tests/scripts/test_benchmark_tool_identification.py", "platform_tests/scripts/test_benchmark_deliberation_recall.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_benchmark_assertion_signal_noise.py", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".claude/rules/canonical-terminology.md", "groundtruth.db", ".gtkb-state/benchmarks/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json"]

## Claim

Implement six read-only benchmark scripts plus one tracking MemBase work_item under existing SPEC-1662 (GOV-18: Assertion Quality Standard) + GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 + DELIB-S312 + DELIB-S341 + INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM advisory. Glossary additions at IP-6 use the live narrative-artifact approval contract. Tracking work_item creation at IP-7 uses `db.insert_work_item()` with `origin='hygiene'` and `source_spec_id='SPEC-1662'`.

Six benchmarks: Cross-Artifact Linkage Heat Map, Recall Evidence Coverage, Tool Identification, Deliberation Recall Quality, Advisory-to-Action Latency, Assertion Signal/Noise Ratio. Each emits JSON+markdown to `.gtkb-state/benchmarks/<run_id>/`.

## Why Now

S349 surfaced LEAK 2 (broken structured-graph linkage) and LEAK 3 (assertion drift detection disabled). The Codex Self-Measurement advisory designed the architecture; this slice implements the smallest concrete read-only measurement subset.

## Changes from -007 (addressing Codex NO-GO F1)

- **F1 (work_item header claim without groundtruth.db target):** Added `groundtruth.db` to `target_paths`. Added IP-7 specifying the tracking work_item insert (mirroring Slice 3's IP-7 pattern that Codex approved at GO -008). Added verification step that confirms the row exists. Header `Work Item:` line clarified.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no new SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - directly governs assertion-signal-noise measurement (Benchmark 6).
- GOV-19 OUTSIDE-IN-TESTING - benchmarks measure surfaces and behaviors.
- GOV-STANDING-BACKLOG-001 - benchmark output produces candidate WIs; IP-7 tracking WI flows here.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - measurement output is durable artifacts.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - benchmark reports placed on existing read paths.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.
- DCL-CONCEPT-ON-CONTACT-001 - "benchmark", "linkage heat map", "advisory latency", "metric snapshot" are load-bearing; IP-6 places entries in canonical-terminology.md.
- GOV-ARTIFACT-APPROVAL-001 - protected narrative-artifact edit at IP-6 requires per-artifact approval packet.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §3.
- `.claude/rules/peer-solution-advisory-loop.md`.
- `.claude/rules/canonical-terminology.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex LO advisory, 2026-05-11).
- DELIB-1469 - GT-KB Self-Measurement and Self-Improvement Advisory.
- DELIB-S321-TRIAD-COMPLETENESS.
- DELIB-1212, DELIB-0731 - prior gtkb-phase-a-metrics-collector bridge history.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-1512, DELIB-1513 - prior review history around DCL-CONCEPT-ON-CONTACT-001.
- DELIB-1465 - per Codex round 4 finding evidence; canonical terminology system and bounded context advisory.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md - Codex NO-GO at -002.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-004.md - Codex NO-GO at -004.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-006.md - Codex NO-GO at -006.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-008.md - Codex NO-GO at -008 (addressed in this -009).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO at -008; this REVISED-4 mirrors Slice 3's approved IP-7 tracking-WI pattern.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" + "parallelize this work to the maximum extent possible".
- 2026-05-13 UTC, S349: Codex returned NO-GO four times on this slice (-002, -004, -006, -008); this REVISED-4 addresses the latest finding.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The benchmark suite operates under `SPEC-1662 (GOV-18)`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001`, the `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM` advisory architecture, and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. IP-6 glossary edits are concept-on-contact compliance per `DCL-CONCEPT-ON-CONTACT-001`. IP-7 tracking work_item creation is standing-backlog work under `db.insert_work_item()` API contract.

## Current Implementation Baseline

- MemBase tables (`specifications`, `tests`, `work_items`, `deliberations`) support read-only queries used by benchmarks.
- `groundtruth-kb/src/groundtruth_kb/db.py` already implements lifecycle metrics that benchmarks reuse.
- `scripts/deliberation_health.py` implements thresholded DA metrics; benchmarks complement.
- No current code computes cross-artifact linkage heat map, recall coverage, tool-identification attribution, deliberation recall precision@k, advisory-to-action latency, or assertion signal/noise categorization.
- Narrative-artifact gate schema requires `artifact_type='narrative_artifact'` with `target_path`, `source_ref`, `approval_mode`, full post-edit `full_content`, and `full_content_sha256`.
- `.claude/rules/canonical-terminology.md` does not currently contain entries for "benchmark", "linkage heat map", "advisory latency", or "metric snapshot".

## Proposed Scope

### IP-1: Implement shared common module

Create `scripts/benchmarks/__init__.py` and `scripts/benchmarks/common.py` with `BenchmarkResult` dataclass (run_id, benchmark_id, window_start, window_end, value, dimensions, source_commit, source_query, generated_at), `write_run_outputs(run_id, results)`, `compute_idempotency_key()`.

### IP-2: Implement six benchmark scripts

Each is a standalone module with `run(window_start, window_end, project_root) -> BenchmarkResult`:

1. `linkage_heatmap.py` - 5x5 matrix of cross-artifact reference rates.
2. `recall_coverage.py` - per-mutation evidence-of-prior-state-review rate.
3. `tool_identification.py` - skill-attribution-marker presence rate.
4. `deliberation_recall.py` - samples 50 recent owner-decision deliberations, runs `gt deliberations search`, returns top-3 IDs.
5. `advisory_latency.py` - scans INSIGHTS-*.md ctimes and bridge ADVISORY entries.
6. `assertion_signal_noise.py` - queries `assertion_runs` history; classifies failing assertions.

### IP-3: Implement CLI

`scripts/benchmarks/cli.py` exposes `run`, `report`, `compare` subcommands.

### IP-4: Tests

`platform_tests/scripts/test_benchmark_*.py` per benchmark with 5 tests each (fixture, idempotency, dimensions, empty-data, output-writing) = 30 tests total.

### IP-5: Add gtkb-benchmarks skill

Create `.claude/skills/gtkb-benchmarks/SKILL.md`. Register in capability registry. Run adapter generator.

### IP-6: Add canonical glossary entries for benchmark-suite concepts

1. Read current `.claude/rules/canonical-terminology.md` content.
2. Compute post-edit content by inserting four entries (`benchmark`, `linkage heat map`, `advisory latency`, `metric snapshot`) under "## GT-KB DA Read-Surface and Operational Vocabulary".
3. Compute `full_content_sha256`.
4. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json`:

   ```json
   {
     "artifact_type": "narrative_artifact",
     "action": "update",
     "target_path": ".claude/rules/canonical-terminology.md",
     "source_ref": "bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md",
     "approval_mode": "approve",
     "full_content": "<complete post-edit canonical-terminology.md content>",
     "full_content_sha256": "<sha256>",
     "presented_to_user": true,
     "transcript_captured": true,
     "explicit_change_request": "S349 AUQ 'File both, sequenced' + 'parallelize this work to the maximum extent possible'",
     "changed_by": "prime-builder/claude/B",
     "change_reason": "DCL-CONCEPT-ON-CONTACT-001 compliance for benchmark-suite concepts",
     "approved_by": "owner"
   }
   ```

5. Set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET`, edit canonical-terminology.md, run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.

### IP-7: Create tracking work_item

After IP-1 through IP-6 land, insert one `work_items` row via `db.insert_work_item()`:

- `origin='hygiene'`
- `source_spec_id='SPEC-1662'`
- `title='Implement GT-KB Benchmark Suite (GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE Slice 2)'`
- `description` summarizing the six benchmarks
- `related_bridge_threads='gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite'`
- `changed_by='prime-builder/claude/B'`
- `change_reason='S349 self-diagnostic LEAK 2 closure; slice authorized by owner AUQ + parallelization directive'`

Mirrors Slice 3's IP-7 pattern that Codex approved at GO -008.

## Tests

Per IP-4 (30 tests) plus:

- `test_canonical_glossary_contains_benchmark_entries` - regression test that grep finds each of the four canonical glossary entries.
- `test_tracking_work_item_created` - regression test that the IP-7 WI row exists with origin='hygiene' and source_spec_id='SPEC-1662'.
- `test_benchmarks_no_membase_write` - verify no benchmark script writes to MemBase tables.
- `test_benchmark_output_path_in_gtkb_state` - verify all benchmark output paths under `.gtkb-state/benchmarks/`.

## Verification Plan

1. All 30+ tests PASS.
2. Single full-suite run; output captured.
3. Idempotency proof: two consecutive runs.
4. Verify all four canonical glossary entries exist with source citations.
5. Verify approval packet validates against narrative-artifact gate.
6. Verify IP-7 tracking work_item exists with expected fields.
7. Verify SPEC-1662 citation resolves in MemBase.
8. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite`.
9. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite`.

## Risks and Rollback

- Query performance: bounded by window_start/window_end.
- Deliberation recall benchmark may catch exceptions on malformed queries; reports failure rate as dimension.
- Threshold setting deferred to follow-on.
- Rollback: retire IP-7 tracking WI, delete scripts, remove skill, revert canonical-terminology.md.

## Sequenced Follow-Ons

Per S349 parallelization directive.

- Slice 2a: Formal SPEC creation once baseline data confirms metric stability.
- Slice 2b: MemBase event-ledger schema migration (per Codex advisory Phase 2).
- Slice 2c: Dashboard panels.
- Slice 2d: Doctor check.

## Recommended Commit Type

`feat:` - new functionality plus canonical-terminology.md additions bundled per DCL-CONCEPT-ON-CONTACT-001.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with 15 blocking + 5 advisory citations.
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- `target_paths` includes `groundtruth.db` matching IP-7 work_item write.
- Work Item header consistent with target_paths.
- `## Requirement Sufficiency` single state: "Existing requirements sufficient".
- `## Recommended Commit Type`.
- explicit `Changes from -007` section.
