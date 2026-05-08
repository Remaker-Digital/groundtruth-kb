NEW

# Implementation Proposal — GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 (Slice 0 Scoping)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-narrative-artifact-approval-extension-001`
**Type:** High-priority owner-directed governance-infrastructure enhancement. Slice 0 = scoping (this proposal); Slice A = extend formal-artifact-approval to narrative artifacts; Slice B = AUQ decision-class hook; Slice C = post-hoc audit hook. Each slice files separately; this proposal scopes all three to give Codex visibility into the full surface before the first slice ships.
**Status:** NEW
**Backlog row:** [memory/work_list.md row 45](memory/work_list.md) — added in same session at commit `3a4a1b3b`.

## Claim

The S337 owner directive mandates a structural fix for the failure mode: agents can edit canonical narrative artifacts (`.claude/rules/*.md` rule files, `memory/work_list.md` narrative entries, `MEMORY.md` sections) without owner-visible packet display, producing artifact text that drifts from owner intent. The current formal-artifact-approval gate (`GOV-ARTIFACT-APPROVAL-001`) covers ADR/DCL/GOV/SPEC/PB mutations only; narrative artifacts are unguarded.

S337 demonstrated the failure: the owner was surprised by `.claude/rules/operating-model.md §2` and `.claude/rules/canonical-terminology.md:348-350` text stating `memory/work_list.md` persists post-migration as a generated view. The owner did not recognize having approved that text. The validated feedback rule "Surface artifact-vs-owner contradictions" (saved S337) is the procedural patch; this enhancement makes it structural.

This proposal scopes three slices that collectively close the gap.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test plan below derives from each slice's surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, owner decision, ADR, DCL are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change adds an `artifact-correction` lifecycle trigger with explicit owner-approval evidence.

**Domain-specific** (governed gates being extended):

- `GOV-ARTIFACT-APPROVAL-001` — current formal-artifact-approval gate; Slice A extends its applicability set.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation contract; Slice A inherits this confirmation pathway for narrative artifacts.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder side of the formal-artifact-approval contract; needs an extension clause for narrative artifacts.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — gate ADR; Slice A extension may need a v2 to add narrative artifacts to the gate scope.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — gate DCL; v2 may be needed to add narrative-artifact path patterns to the hook.

**Hooks and rules** (referenced; some changed):

- `.claude/hooks/bridge-compliance-gate.py` — existing PreToolUse Write hook; Slice A may extend its detection logic OR a new sibling hook is added.
- `.claude/hooks/owner-decision-tracker.py` — existing Stop / SessionStart / UserPromptSubmit hook; Slice B's decision-class hook may share infrastructure.
- `.claude/hooks/formal-artifact-approval-gate.py` (or equivalent) — existing approval-packet validator; Slice A extends its scope.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract; referenced.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/acting-prime-builder.md` — Deterministic Services Principle anchoring this enhancement.
- `.claude/rules/bridge-essential.md` — S294 lesson "if it is essential, it must be tracked," cited as procedural-mandate-non-enforceability authority.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.

**Memory feedback** (procedural patch this enhancement structuralizes):

- `feedback_surface_artifact_owner_contradictions.md` (saved S337) — describes the AUQ-with-reaffirm-option pattern; Slice B's decision-class hook is the structural enforcement of the pattern.

## Owner Decisions / Input

Owner-directive evidence captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| How shall I capture this high-priority enhancement? | "Backlog row + scoping proposal NOW" |

Antecedent owner statement: "Yes, I agree. This is a high-priority enhancement." (in response to my analysis of three remediation options for the fragility of the procedural-mandate AUQ-reaffirm-option rule).

This authorizes:

- Adding row 45 to `memory/work_list.md` (done in commit `3a4a1b3b`).
- Filing this NEW scoping proposal.
- Slice A, B, and C implementations pending Codex GO. Each slice will require its own owner-visible approval packet because all three slices touch governance gate code or rules.

No additional owner approval is required to file this NEW. Implementation slices require Codex GO.

## Failure Mode Analysis (S337 evidence)

The S337 session demonstrated three concrete fragility surfaces in the existing AUQ-reaffirm-option rule:

**1. Pure procedural mandate, no hook enforcement.** The rule lives in `feedback_surface_artifact_owner_contradictions.md` (memory). No mechanical check fails an AUQ when the option-set omits "reaffirm." Compare with `.claude/hooks/owner-decision-tracker.py` which blocks Stop on prose decision-asks — that's a structural gate. The reaffirm-option rule has nothing analogous. Per `.claude/rules/bridge-essential.md` S294 lesson, procedurally-mandated behavior is not tracked.

**2. Agent rationalization under cognitive load.** When mid-task and the owner has just stated something forcefully, the temptation is to skip "reaffirm current artifacts" as pedantic — exactly when the option is most needed because the owner might be operating from outdated mental model. S337 itself is the proof: I added the option only because I happened to think of it. Nothing prevented me from skipping.

**3. AUQ tool constraint.** `AskUserQuestion` allows 2-4 options. If the agent has 4 substantive action variants, "reaffirm" gets squeezed out.

Lesser failure modes: no agreed definition of "contradiction" (subtle wording disagreements get judged as non-contradictions); no Codex review check on AUQ choice-set composition; no audit-after-the-fact that artifact mutations had a "reaffirm-considered" AUQ in the same session.

## Proposed Scope

**Slice A — Extend formal-artifact-approval to narrative artifacts:**

- A1. Define narrative-artifact path-pattern set: `.claude/rules/*.md` (excluding `.toml`, `.local.md`); `memory/work_list.md` (the standing backlog narrative); `memory/MEMORY.md` and `memory/*.md` topic files (operational state — possibly out of scope; Slice A1 sub-decision); `CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md` (project-instruction surfaces).
- A2. Update `GOV-ARTIFACT-APPROVAL-001` v2 (or add a successor `GOV-NARRATIVE-ARTIFACT-APPROVAL-001`) with narrative-artifact path patterns added to the gate scope. Owner-visible packet display required before Write.
- A3. Update `DCL-ARTIFACT-APPROVAL-HOOK-001` v2 to include narrative-artifact path patterns in its `applies_when_paths_match` set.
- A4. Update `.claude/hooks/bridge-compliance-gate.py` (or `.claude/hooks/formal-artifact-approval-gate.py`) to read the extended path-pattern set and require an approval packet for Writes/Edits matching those paths. Approval packet schema reuses the existing `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json` format.
- A5. Add explicit exception for hook-managed files (e.g., `memory/pending-owner-decisions.md` is hook-owned per its preamble; the hook's writes should not require owner packet because the hook IS the owner-decision capture surface). Exception list in `config/governance/narrative-artifact-approval.toml`.

**Slice B — AskUserQuestion decision-class hook:**

- B1. Define `decision_class` taxonomy: `artifact-correction`, `scope-choice`, `approval`, `priority-elevation`, `clarification`, `deployment`, `destructive-action`, `requirement`. Each class has option-set requirements documented in `config/governance/auq-decision-classes.toml`.
- B2. Add a PostToolUse hook on `AskUserQuestion` calls that:
  - Reads the agent's structured `decision_class` annotation (new optional metadata field on AUQ; agent declares per call).
  - Validates option-set requirements per class. Example: `artifact-correction` requires at least one option whose label includes "reaffirm" or "keep current"; `destructive-action` requires at least one "abort" option; etc.
  - Logs the AUQ-with-class to a session-scoped audit file under `.gtkb-state/auq-audit/<session-id>.jsonl`.
- B3. Document `decision_class` annotation convention in `.claude/rules/file-bridge-protocol.md` and `.claude/rules/acting-prime-builder.md`.
- B4. Edge case: backwards compatibility — AUQ calls without `decision_class` annotation log a warning (not block) for one transition window, then become hard-blocked after a deprecation date set in the rule update.

**Slice C — Post-hoc audit hook:**

- C1. Add a pre-commit hook (or extend existing) that scans the staged diff for narrative-artifact paths.
- C2. For each narrative-artifact path in the staged diff, require either (a) a corresponding approval packet under `.groundtruth/formal-artifact-approvals/<date>-*.json` with matching artifact ID, OR (b) a same-session AUQ audit entry under `.gtkb-state/auq-audit/<session-id>.jsonl` with `decision_class=artifact-correction` AND a hash of the diff matching the staged change.
- C3. Reject the commit otherwise. Error message includes the missing-evidence type and a remediation pointer.
- C4. Integrate with existing `scripts/release_candidate_gate.py` so the audit hook's evidence appears in release-readiness reports.

**Out of scope** (deferred or owner-decided separately):

- Auto-generation of approval packets from AUQ answers (deferred to a follow-on slice; would require structured-output AUQ surface that doesn't exist today).
- Extending the gate to non-narrative shared state (e.g., `groundtruth.toml`, `pyproject.toml`) — separate threading.
- Retroactive backfill of approval packets for past narrative-artifact changes (deferred; the post-hoc audit hook ratchets forward, doesn't enforce backward).
- Deprecating the `feedback_surface_artifact_owner_contradictions.md` memory rule — only after all three slices are VERIFIED and the structural gate has run cleanly for an owner-determined cooling period.

## Spec-Derived Test Plan

Slice A tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-A-pathset | Narrative-artifact path set covers expected files | Unit test asserts `.claude/rules/*.md`, `memory/work_list.md`, `CLAUDE.md` are matched; `pyproject.toml`, `.gtkb-state/**`, hook-managed files are not |
| T-A-block-without-packet | Write of `.claude/rules/operating-model.md` without an approval packet is hard-blocked | Hook test: stage edit; run hook; assert exit code 2 with "missing approval packet" message |
| T-A-allow-with-packet | Write of `.claude/rules/operating-model.md` WITH a valid approval packet at `.groundtruth/formal-artifact-approvals/<date>-...json` proceeds | Hook test: create packet fixture; stage edit; run hook; assert exit code 0 |
| T-A-exception-list | Hook-managed files (`memory/pending-owner-decisions.md`) are explicitly exempted | Hook test: edit pending-owner-decisions.md without packet; assert exit code 0 |
| T-A-regression | Existing ADR/DCL/GOV gate behavior unchanged | Re-run existing `tests/hooks/test_formal_artifact_approval_gate.py` suite |
| T-A-root-boundary | All paths in the extended set are under `E:\GT-KB` | Test asserts `ADR-ISOLATION-APPLICATION-PLACEMENT-001` is satisfied |

Slice B tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-B-class-taxonomy | All declared classes have option-set requirements documented | Unit test reads `auq-decision-classes.toml`; asserts every class has at least one validation rule |
| T-B-artifact-correction-class | `artifact-correction` class requires "reaffirm"-style option | Hook test: AUQ with class=artifact-correction and 4 options none of which contain "reaffirm" or "keep current"; assert hook flags the call |
| T-B-deprecation-window | AUQ without decision_class logs warning during transition window, blocks after | Time-mocked test: before deprecation date, assert WARN; after, assert ERROR |
| T-B-audit-trail | AUQ-with-class is logged to `.gtkb-state/auq-audit/<session-id>.jsonl` | Hook test: emit AUQ; assert line appended to expected file with required fields |
| T-B-decision-class-pluggability | Adding a new class via TOML requires no code change | Integration test: append a fixture class to `auq-decision-classes.toml`; run hook; assert recognized |

Slice C tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-C-block-without-evidence | Commit changing `.claude/rules/canonical-terminology.md` without approval packet OR same-session AUQ-class evidence is rejected | Pre-commit hook test: stage edit; commit; assert exit code 2 |
| T-C-allow-with-packet | Commit with matching approval packet proceeds | Test as above with packet in place |
| T-C-allow-with-auq-audit | Commit with same-session AUQ audit entry (class=artifact-correction, matching diff hash) proceeds | Test as above with audit entry in place |
| T-C-release-gate-integration | Release-candidate gate surfaces narrative-artifact-evidence rollup | `python scripts/release_candidate_gate.py` output includes new evidence section |
| T-C-no-bypass | Hook cannot be bypassed by commit-message tag (no `[narrative-exempt:` escape hatch) | Hook test: commit with claimed escape tag; assert hook still blocks |

Live regression (all slices):

| Test | Method |
|---|---|
| T-live-doctor | `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml doctor` returns no new ERRORs after each slice |
| T-live-release-gate | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` PASSes |
| T-live-regression-suite | Existing `tests/hooks/`, `tests/scripts/`, `tests/governance/` suites continue green |

## Acceptance Criteria

For VERIFIED of each slice:

**Slice A:**
1. Narrative-artifact path-pattern set is explicit and configurable (T-A-pathset).
2. Writes/Edits to narrative artifacts without an approval packet are hard-blocked (T-A-block-without-packet).
3. Approval packets continue to authorize narrative-artifact writes (T-A-allow-with-packet).
4. Hook-managed files exempted (T-A-exception-list).
5. Existing ADR/DCL/GOV behavior unaffected (T-A-regression).

**Slice B:**
1. `decision_class` taxonomy documented and TOML-driven (T-B-class-taxonomy).
2. `artifact-correction` class enforces "reaffirm"-style option (T-B-artifact-correction-class).
3. Deprecation window warns before blocking (T-B-deprecation-window).
4. AUQ audit trail captured per session (T-B-audit-trail).

**Slice C:**
1. Pre-commit hook rejects narrative-artifact changes without evidence (T-C-block-without-evidence).
2. Approval packet OR AUQ audit entry satisfies (T-C-allow-with-packet, T-C-allow-with-auq-audit).
3. Release-gate surfaces evidence rollup (T-C-release-gate-integration).
4. No commit-message escape hatch (T-C-no-bypass).

Cross-slice:
- Live doctor + release gate + regression suite continue PASS after each slice.
- After Slice C VERIFIED, the S337 feedback memory `feedback_surface_artifact_owner_contradictions.md` can be reviewed for retirement; owner approval required before retiring (per the rule it itself encodes — meta-application).

## Risk / Rollback

Risk surface:

- **Hook noisiness**: Slice A blocks writes; if path patterns are too broad, agent productivity drops. Mitigation: deprecation window in Slice B (warn-then-block) is also applied in Slice A; explicit exception list for hook-managed files.
- **Backwards compat for in-flight bridges**: existing bridge proposals/reports written without `decision_class` annotation should not retroactively block. Slice B's deprecation window addresses this. Slice C's audit only checks staged commits, not historical state.
- **Performance**: pre-commit hook scanning every diff for narrative-artifact paths plus packet matching is small per-commit (<100ms expected) but not free. Mitigation: cache approval-packet directory listings; only re-read on diff-line presence.
- **Owner-packet generation friction**: every narrative-artifact change requires an approval packet. If packet creation is high-friction, agents will route around (e.g., bundle changes into approved bridge implementations). Mitigation: align with `GTKB-ARTIFACT-RECORDER-CLI` (row 15) — both proposals reduce per-instance ceremony to a CLI call.
- **Self-application paradox**: this proposal itself proposes narrative artifact changes (rule files, documentation). It would be approved-via-Codex-GO under the existing protocol, but post-Slice-A-VERIFIED, similar future proposals would also need approval packets for the rule files they touch. This is the intended steady state, not a defect.

Rollback per slice:

- Slice A: revert hook code + rule update; existing approval-packet pathway reverts to ADR/DCL/GOV-only scope. No data corruption; approval packets accumulated under the extended scope remain valid evidence (just unused).
- Slice B: revert hook + decision-class config; AUQ calls revert to no-class behavior. Audit trail under `.gtkb-state/auq-audit/` remains as historical evidence.
- Slice C: revert pre-commit hook addition; commits revert to current behavior.

Rollback should be unnecessary because owner explicitly directed this enhancement.

## Files Expected To Change (per slice)

**Slice A:**

- `.claude/hooks/bridge-compliance-gate.py` OR new sibling — narrative-artifact path matcher (~50-100 LOC).
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` — template parity.
- `config/governance/narrative-artifact-approval.toml` (new) — path-pattern set + exception list.
- `tests/hooks/test_narrative_artifact_approval.py` (new) — Slice A tests.
- `groundtruth.db` — new versions of `ADR-ARTIFACT-FORMALIZATION-GATE-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, possibly `GOV-ARTIFACT-APPROVAL-001`.
- `.groundtruth/formal-artifact-approvals/2026-05-XX-{ADR,DCL,GOV}-*.json` — approval packets for Slice A's own ADR/DCL/GOV updates.

**Slice B:**

- `.claude/hooks/auq-decision-class-validator.py` (new) — PostToolUse hook on AskUserQuestion.
- `groundtruth-kb/templates/hooks/auq-decision-class-validator.py` — template parity.
- `config/governance/auq-decision-classes.toml` (new) — class taxonomy + option-set requirements.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/acting-prime-builder.md` — document `decision_class` annotation convention.
- `tests/hooks/test_auq_decision_class_validator.py` (new) — Slice B tests.

**Slice C:**

- `.githooks/pre-commit` — extension OR new pre-commit hook.
- `scripts/check_narrative_artifact_evidence.py` (new) — pre-commit logic.
- `scripts/release_candidate_gate.py` — integration to surface evidence rollup.
- `tests/scripts/test_check_narrative_artifact_evidence.py` (new) — Slice C tests.

## Prior Deliberations

`db.search_deliberations("narrative artifact approval extension formal-artifact-approval gate hook governance")` to be run; expected results:

- DELIB-S337 (this session, when archived) — owner directive that motivated this enhancement.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — directly anchors this enhancement's "session-friction → service infrastructure" framing.
- DELIB-0835 (`GOV-ARTIFACT-APPROVAL-001` source) — owner decision establishing formal-artifact-approval as a strict default. This enhancement extends that default's scope, doesn't override it.
- DELIB-0838 — standing backlog as governed cross-session work authority. Slice A treats `memory/work_list.md` narrative as governed.
- DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT — narrative-artifact updates must not break lifecycle independence between platform and applications. Tested via T-A-regression.

No prior deliberation expected to contradict the enhancement scope. If one surfaces (e.g., a precedent declining to extend governance to narrative artifacts on cost grounds), this proposal will revise.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-narrative-artifact-approval-extension-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write (the hook runs the preflight and refuses Writes whose required-spec set is incomplete).

All triggered cross-cutting specs (4 advisory + 4 blocking) cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this proposal filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes in this commit.

For Slice A implementation: `feat(governance):` — net-additional governance gate scope; new ADR/DCL versions are net-additional capability surfaces.

For Slice B implementation: `feat(governance):` — net-additional hook + decision-class taxonomy.

For Slice C implementation: `feat(governance):` — net-additional pre-commit hook with audit-trail enforcement.

## Requested Loyal Opposition Action

Review this proposal for GO. Specific reviewer questions for Codex:

1. Should Slice A and Slice B be merged into a single first-slice that ships approval-gate + decision-class together? My read: split is correct because Slice A has higher coverage value (closes the gap immediately for narrative artifacts) while Slice B adds AUQ-side audit trail; if Slice A is delayed by Slice B's complexity, the gap stays open longer.
2. Should `MEMORY.md` and `memory/*.md` topic files be in Slice A's path-pattern set? Argument for: they are operational memory that influences agent behavior and could be edited without owner visibility. Argument against: they are explicitly Claude's operational notepad per ADR-0001's three-tier memory architecture; gating every memory write would create high friction.
3. Is the "decision_class" annotation a metadata field on `AskUserQuestion` (extending the tool's schema) or a separate side-channel (a comment line in the agent's response, parsed by the hook)? My read: side-channel is cleaner because it doesn't require AUQ tool changes, but is more agent-error-prone.
4. Should retiring `feedback_surface_artifact_owner_contradictions.md` be an owner-AUQ moment after Slice C VERIFIED (per the rule's own meta-application of itself), or a Prime Builder operational-cleanup decision? My read: meta-application — owner should explicitly approve retiring a behavioral rule, especially one they endorsed.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
