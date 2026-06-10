# Implementation Proposal REVISED-1 - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md` (F1, F2, F3)
Work Item: new MemBase work item to be created from this proposal under existing GOV-18 + GOV-15 governance
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py", ".claude/skills/assertion-triage/SKILL.md", ".codex/skills/assertion-triage/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".gtkb-state/assertion-triage/**"]

## Claim

Implement assertion signal/noise categorization that converts the 1,463 currently-failing GT-KB assertions into four owner-actionable categories (genuine_drift, chronic_noise, flaky, healthy) under existing GOV-18 (assertion quality) and GOV-15 (test fix gate) authority. The categorization is read-only inference over `assertion_runs` history; it produces no canonical state mutation in this slice. Retirement of any specific assertion remains a separate per-assertion owner decision under the AUQ-only enforcement stack and one-at-a-time owner-action protocol per `CODEX-WAY-OF-WORKING.md`.

## Why Now

Same rationale as -001: S349 cited LEAK 3 with quantitative evidence from `memory/MEMORY.md` showing 1463/1687 assertions failing with the failure rate normalized as "the known broad historical failure profile". Drift detection has been functionally disabled by accumulation. Categorization is the precondition for owner triage.

## Changes from -001 (addressing Codex NO-GO F1, F2, F3)

- **F1 (Requirement Sufficiency contradiction):** Removed both prerequisite SPEC creations from scope. Categorization operates under GOV-18 (assertion quality) and GOV-15 (test fix gate); retirement workflow uses existing `db.update_specification()` API with explicit per-call owner AUQ approval.
- **F2 (target_paths omits state files):** Removed approval-packet writes (no SPEC creation). Added `.gtkb-state/assertion-triage/**` to target_paths for category JSON and candidate JSON outputs.
- **F3 (per-candidate vs batch owner-decision contradiction):** Resolved to per-candidate AUQ as the single governing protocol per `CODEX-WAY-OF-WORKING.md:127-130` one-at-a-time owner-action protocol. The retirement workflow surfaces candidates as a queue/review summary (read-only inspection) that asks one current owner AUQ at a time when the owner is ready to act on a specific entry. The Risk section is updated to remove the contradictory "batch acceptance" mitigation language; the high-candidate-count concern is addressed by the queue/review summary which lets owner browse without per-item AUQ until a specific decision is requested.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- GOV-18 ASSERTION-QUALITY - meaningfulness over coverage; this slice operationalizes that principle by categorizing the assertion pile.
- GOV-03 TEST-CLARITY - every test must produce unambiguous PASS/FAIL; chronic_noise category surfaces tests that have lost clarity.
- GOV-15 TEST-FIX-GATE - no fixing failed tests without owner approval; this slice is read-only inference with no automatic retirement.
- GOV-STANDING-BACKLOG-001 - retirement candidates flow to standing backlog as candidate WIs for owner decision.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output is durable artifact.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - categorization is artifact-oriented; outputs are durable evidence files.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - assertion state transitions are lifecycle events; categorization consumes them as downstream signal.
- DCL-CONCEPT-ON-CONTACT-001 - "assertion category", "genuine_drift", "chronic_noise", "flaky" are new load-bearing concepts; glossary entries added at IP-5 in the assertion-triage SKILL.md.
- GOV-ARTIFACT-APPROVAL-001 - this slice creates no formal GOV/ADR/DCL/SPEC/PB artifacts; retirement requires per-assertion AUQ with appropriate formal-artifact-approval packet at execution time.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - categorization is repetitive plumbing.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §1.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` §127-130 (one-at-a-time owner-action protocol).
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` (assertion regression rate as Quality and Evidence portfolio metric).

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - per Codex F1 evidence in -002 NO-GO; GT-KB Self-Measurement Advisory relevant to assertion regression measurement.
- DELIB-S321-TRIAD-COMPLETENESS - per Codex F1 evidence; traceability completeness relevant to assertion linkage.
- DELIB-0473 - per Codex F1 evidence; pipeline hardening advisory weakly relevant.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- Prior MEMORY.md handoff entries (S347, S348) - cite "224/1687 PASS and 1463 FAIL" verbatim.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md - Codex NO-GO at -002; this REVISED-1 addresses F1, F2, F3.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for leaks/gaps/waste.
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO on -001 with three findings; this REVISED-1 addresses them.

No additional owner decision is required before review. Each retirement decision will be a separate AUQ at execution time per the one-at-a-time owner-action protocol.

## Requirement Sufficiency

Existing requirements sufficient.

The categorization and retirement workflow operate under existing governance:

- `GOV-18` (assertion quality) directly governs categorization as operationalizing "meaningfulness over coverage; no rubber-stamp assertions".
- `GOV-03` (test clarity) governs the chronic_noise category surface ("every test must produce unambiguous PASS/FAIL"; persistently-failing assertions have lost clarity).
- `GOV-15` (test fix gate) governs retirement decisions ("no fixing failed tests without owner approval"); the workflow enforces per-call AUQ.
- `GOV-STANDING-BACKLOG-001` governs candidate retirement entries as backlog work.
- `CODEX-WAY-OF-WORKING.md:127-130` (one-at-a-time owner-action protocol) governs the retirement AUQ cadence.

Categorization is read-only inference over existing `assertion_runs` table; outputs go to `.gtkb-state/assertion-triage/`. No new product behavior. Retirement of a specific assertion uses existing `db.update_specification()` API with explicit per-call AUQ.

## Current Implementation Baseline

Unchanged from -001 §"Current Implementation Baseline".

## Proposed Scope

### IP-1: Implement categorization script

Create `scripts/assertion_categorize.py`:

- CLI: `python scripts/assertion_categorize.py [--since YYYY-MM-DD] [--output-dir <path>] [--dry-run]`
- Queries `assertion_runs` history for each currently-failing assertion.
- Applies four-category decision logic:
  - `genuine_drift`: latest FAIL, prior 5+ PASS, transition within 7 days
  - `chronic_noise`: latest 50+ consecutive FAIL
  - `flaky`: latest 10 runs include both PASS and FAIL with ≥1 transition
  - `healthy`: stable PASS, or stable FAIL for `status='specified'` spec
- Writes per-assertion JSON to `.gtkb-state/assertion-triage/categories/<assertion_id>.json`.
- Emits summary markdown with counts per category.
- Read-only; no MemBase mutations.

### IP-2: Implement retirement workflow with one-at-a-time AUQ

Create `scripts/assertion_retirement_workflow.py`:

- CLI:
  - `--review-candidates` - read-only inspection mode; lists chronic_noise candidates as a queue/review summary with rationale and historical evidence. No AUQ prompted; owner browses freely.
  - `--ask <assertion_id>` - presents exactly one AUQ for one specific candidate (per `CODEX-WAY-OF-WORKING.md:127-130`). Returns owner answer plus packet path.
  - `--apply-decision <assertion_id> <retire|accept|keep> --packet <path>` - applies the owner decision validated against the AUQ packet.
- The workflow surfaces candidates in browsable form without per-item AUQ until owner explicitly invokes `--ask`. This satisfies both the per-candidate AUQ rule (each retirement decision is one AUQ) and the high-volume-handling concern (owner can review the list without being prompted for each entry).
- Writes candidate JSON to `.gtkb-state/assertion-triage/candidates/<assertion_id>.json`.

### IP-3: Wire into assertion-check hook (advisory display only)

Update `.claude/hooks/assertion-check.py` to read latest categorization run and append per-category counts to existing PASS/FAIL output. Format: `"Assertions: PASS=224 FAIL=1463 (genuine_drift=N, chronic_noise=N, flaky=N, healthy=N, uncategorized=N)"`. No write gating; display only.

### IP-4: Tests

`platform_tests/scripts/test_assertion_categorize.py` and `test_assertion_retirement_workflow.py` with 13 tests per -001 §"Tests" with this addition:

- `test_review_candidates_does_not_prompt_auq` - verify review-candidates mode emits no AUQ-prompt envelope and no MemBase write.

### IP-5: Add assertion-triage skill

Create `.claude/skills/assertion-triage/SKILL.md`. Register in capability registry. Run adapter generator. Add glossary entries for new concepts per DCL-CONCEPT-ON-CONTACT-001.

## Tests

Per -001 §"Tests" plus the addition above. Total: 14 tests.

## Verification Plan

Per -001 §"Verification Plan" with these adjustments:

- No SPEC creation evidence required (no SPECs created in this slice).
- Verify categorization output paths fall entirely under `.gtkb-state/assertion-triage/`.
- Verify zero MemBase mutations during categorization runs.
- Verify retirement workflow's `--review-candidates` mode produces no AUQ prompts.
- Verify `--apply-decision` requires valid AUQ packet (test rejects missing/invalid packet).
- Carry forward applicability and clause preflight outputs from -001 and rerun against -003.

## Risks and Rollback

Per -001 §"Risks and Rollback" with this revision:

- **Removed the contradictory batch-AUQ mitigation language.** The high-candidate-count concern is now addressed by the queue/review summary mode that lets owner browse without per-item prompts; only explicit `--ask` invocations produce AUQs.
- Per-candidate AUQ overhead is bounded because owner only invokes `--ask` for entries the owner has decided to act on.

## Sequenced Follow-Ons

Per S349 parallelization directive, no longer waiting for any other slice.

Independent follow-ons after Slice 3 VERIFIED:

- Slice 3a: Formal SPEC creation for categorization contract once baseline data confirms threshold stability.
- Slice 3b: Doctor check that flags ungated genuine_drift entries as P0 after baseline confirms genuine_drift is a small set.
- Slice 3c: Optional batch-decision protocol update (would require governance change to `CODEX-WAY-OF-WORKING.md` one-at-a-time rule; not in scope here).

## Recommended Commit Type

`feat:` - new functionality (two scripts, hook update, skill, capability registry entry).

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section (13 blocking + 3 advisory).
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.gtkb-state/assertion-triage/**`.
- `## Requirement Sufficiency` subsection with exactly one operative state: "Existing requirements sufficient".
- `## Recommended Commit Type`.
- explicit `Changes from -001` section enumerating each NO-GO finding addressed.
- explicit one-at-a-time owner-decision protocol consistent throughout.
