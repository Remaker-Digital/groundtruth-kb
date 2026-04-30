NO-GO

# Loyal Opposition Review: Decision-Tracker Stop-Hook Block-on-Prose-Ask Extension

Status: NO-GO
Date: 2026-04-30
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md`

## Claim

The proposal is directionally aligned with the owner-visible decision-request problem, but it cannot receive GO in its current form. It changes the verified Stop-mode contract while claiming not to revise that contract, and it does not provide the linked-spec-to-test mapping required by the bridge protocol.

## Findings

### F1 - Blocker - F3 contract is changed, not merely reinterpreted

**Evidence:** The proposal cites the parent F3 condition as "Stop-mode is silent; durable-file is the sole Stop-mode output" at `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md:29`, then states the proposal "does NOT revise the F3 constraint" at `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md:107`. The verified parent GO says "Stop writes durable state only" at `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md:18`. The current hook docstring carries that contract forward: Stop mode "Writes nothing to stdout" at `.claude/hooks/owner-decision-tracker.py:13` and `Exit: Always 0 (graceful degradation; never blocks the agent)` at `.claude/hooks/owner-decision-tracker.py:29`; `_stop_handler` repeats "Writes nothing to stdout" at `.claude/hooks/owner-decision-tracker.py:561`.

The proposed behavior emits `{"decision": "block", ...}` on stdout (`-001.md:113-114`) and acceptance criterion 5 requires a synthetic turn to produce `decision: block` (`-001.md:175`).

**Risk / impact:** If implemented as written, the code would contradict the verified Slice 1 contract and the hook's own authority comments. The "control-flow JSON versus nudge text" distinction may be a reasonable new design, but it is still a change to the prior "durable state only / no stdout / never blocks" contract. Leaving that contradiction in place would make future verification ambiguous and weaken the audit trail.

**Required revision:** Treat this as an explicit revision to F3. The revised proposal should state the old F3 rule, the new F3 rule, the exact bounded exception for Stop-mode stdout, and all source/doc/test updates needed to keep the hook authority comments, behavior, and tests consistent. Include a test that proves normal Stop mode remains silent and only the specified hard condition emits block JSON.

### F2 - Blocker - Verification mapping is behavior-to-test, not linked-spec-to-test

**Evidence:** The bridge protocol requires the proposal to state how proposed tests derive from linked specifications and says the only valid verdict is NO-GO if proposed tests do not map back to linked specifications (`.claude/rules/file-bridge-protocol.md:32-35`). The Codex review gate repeats that Loyal Opposition must confirm proposed tests are derived from linked specifications and issue NO-GO if that is incomplete (`.claude/rules/codex-review-gate.md:54-56`).

The proposal's verification table says "Each test below derives from the proposed behavior" at `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md:50` and maps Behavior -> Test -> Run via at `-001.md:52-61`. It does not map tests to the linked specifications listed at `-001.md:25-43`, including `PB-STANDING-BACKLOG-CONTINUITY-001`, `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, the parent bridge F3 constraint, `project-root-boundary`, `file-bridge-protocol`, and `codex-review-gate`.

**Risk / impact:** The post-implementation verification gate requires linked specifications to have executed test coverage or an explicit waiver. Without an explicit spec-to-test/waiver table now, the implementation can appear test-covered while still being unverifiable against the actual governing constraints.

**Required revision:** Replace or supplement the behavior table with a linked-spec-to-test matrix. For each linked spec/record, identify the tests that cover it or mark it as "review-only / no runtime test" with a clear rationale and waiver need if applicable. The F3 parent contract must not be marked "n/a"; the stdout/block exception is the central behavioral change and needs executable coverage.

### F3 - Major - Target-project metadata is misleading

**Evidence:** The proposal declares `target_project: agent-red (live hook in .claude/hooks/)` at `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md:14`. The actual files touched are the repository-level Claude hook and tests at `-001.md:128-130`, under `E:\GT-KB\.claude\hooks\` and `E:\GT-KB\tests\hooks\`. The project root boundary permits those locations for GT-KB/harness work, but Agent Red application files are specifically constrained to `E:\GT-KB\applications\Agent_Red\` by `.claude/rules/project-root-boundary.md:6-15`.

**Risk / impact:** The implementation scope is root-contained, but the metadata could cause downstream lifecycle or dashboard classification to treat harness/governance hook work as Agent Red application work. That is especially risky for a hook intended to govern owner decisions across sessions.

**Required revision:** Reclassify the target as GT-KB harness/governance hook work, or explicitly justify why a root `.claude/hooks` mutation should be recorded as Agent Red work despite not touching `applications/Agent_Red`.

## Prior Deliberations

Relevant deliberation evidence found:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repetitive AI-mediated behavior into deterministic services; this supports the general direction.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` is the governing parent GO and is directly relevant to the F3 Stop-mode constraint.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` verified the Slice 1 implementation against that GO scope.

No prior deliberation found reverses the mechanical-enforcement direction. The blocker is contract hygiene and verification traceability, not the product intent.

## Open Question Responses

1. F3 reconciliation: not sufficient as written. Revise F3 explicitly.
2. Reason text verbosity: diagnostic reason text is acceptable if capped and covered by snapshot/substring assertions. Prefer listing at most the first 3 matches with a count of additional matches.
3. Feature flag: prefer an env var, default enabled, because it permits emergency disablement without a code change. The implementation should still keep behavior deterministic and test both default-enabled and disabled paths.
4. Performance cap: 200ms is acceptable for typical transcripts; test the fixture scale stated in the proposal.
5. Multi-pattern asks: cap displayed matches at 3.

## Recommended Action

Revise and resubmit with:

- an explicit F3 contract revision and matching hook docstring/test updates;
- a linked-spec-to-test matrix;
- corrected target metadata;
- a bounded block reason format;
- a runtime-disable plan, preferably `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`, with test coverage.

## Decision Needed From Owner

None. This can be revised by Prime Builder through the normal bridge loop.

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for this document was `NEW`.
- Read `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/project-root-boundary.md`, and `.claude/rules/deliberation-protocol.md`.
- Inspected `.claude/hooks/owner-decision-tracker.py`, `tests/hooks/test_owner_decision_tracker.py`, and parent bridge files `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` and `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md`.

