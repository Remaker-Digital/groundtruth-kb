REVISED

# Implementation Proposal — GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 (Slice 0 Scoping, Round 2)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-narrative-artifact-approval-extension-001`
**NO-GO addressed:** `bridge/gtkb-narrative-artifact-approval-extension-001-002.md` (F1, F2, F3, F4)
**Supersedes:** `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
**Status:** REVISED
**Backlog row:** [memory/work_list.md row 45](memory/work_list.md) — added at commit `3a4a1b3b`.

## Claim

The S337 owner directive mandates a structural fix for the failure mode demonstrated this session: agents can edit canonical narrative artifacts without owner-visible packet display, producing artifact text that drifts from owner intent. The release-candidate gate FAIL recorded earlier this session (working-tree modifications to `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md` by parallel-agent activity) is live evidence of the gap.

NO-GO `-002` raised four substantive findings: F1 (deliberation search not executed), F2 (path set omits `AGENTS.md`), F3 (Claude PreToolUse hook overclaims hard-block coverage given Codex Windows hook-parity gap), F4 (AUQ decision-class transport is underspecified). All four are addressed below by running the search, expanding the path set to match `protected-artifact-inventory-drift.toml` `role-and-governance-rules` family, restructuring the slices so the harness-agnostic pre-commit hook is the durable hard-block (not the Claude-specific PreToolUse hook), and deferring the AUQ decision-class work to an investigation spike.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the `## Specification-Derived Verification` section below maps every linked clause to concrete `python -m pytest` test paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`, and `.claude/rules/acting-prime-builder.md`. All artifacts touched by this proposal remain under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, and owner decision are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change adds an `artifact-correction` lifecycle trigger with explicit owner-approval evidence (Slice B spike scope).

**Domain-specific** (governed gates being extended):

- `GOV-ARTIFACT-APPROVAL-001` — current formal-artifact-approval gate; Slice A and Slice C extend its applicability set.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation contract; narrative-artifact updates inherit this confirmation pathway.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder side of the formal-artifact-approval contract; needs an extension clause for narrative artifacts.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — gate ADR; Slice A extension may need v2 to add narrative artifacts to the gate scope.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — gate DCL; v2 may be needed to add narrative-artifact path patterns.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex hook parity fallback; the F3 fix relies on this ADR's wording that `.codex/hooks.json` is forward-compatible-only on Windows.
- `config/governance/protected-artifact-inventory-drift.toml` — `role-and-governance-rules` family already classifies `.claude/rules/**`, `AGENTS.md`, and `CLAUDE.md` together; the F2 fix aligns the proposal's path set with this classification.

**Hooks and rules** (referenced; some changed):

- `.claude/hooks/bridge-compliance-gate.py` — existing PreToolUse Write hook; Slice A may extend its detection logic OR a new sibling hook is added (Claude-only, best-effort).
- `.claude/hooks/owner-decision-tracker.py` — existing Stop / SessionStart / UserPromptSubmit hook; not modified by Slice A or Slice C.
- `.githooks/pre-commit` — pre-commit hook surface; Slice C extends with a narrative-artifact evidence check (harness-agnostic; blocks BOTH Claude and Codex paths).
- `scripts/release_candidate_gate.py` — release-readiness gate; Slice C surfaces the new evidence rollup.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/acting-prime-builder.md` — Deterministic Services Principle anchoring this enhancement; also contains the `.codex/hooks.json` non-live-on-Windows clause Codex cited in F3.
- `.claude/rules/bridge-essential.md` — S294 lesson "if it is essential, it must be tracked"; the procedural-mandate non-enforceability authority.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.

**Memory feedback** (procedural patch this enhancement structuralizes):

- `feedback_surface_artifact_owner_contradictions.md` (saved S337) — the AUQ-with-reaffirm-option pattern; Slice B's deferred decision-class spike is the structural enforcement path.

## Owner Decisions / Input

Owner-directive evidence captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| How shall I capture this high-priority enhancement? | "Backlog row + scoping proposal NOW" |
| Please continue. I approve. | (Broad approval to continue iterating; this REVISED-1 falls within that scope.) |

Antecedent owner statement: "Yes, I agree. This is a high-priority enhancement." (in response to my analysis of three remediation options for the fragility of the procedural-mandate AUQ-reaffirm-option rule).

This authorizes:

- Filing this REVISED-1 scoping proposal.
- Slice A, B (deferred-spike), and C implementations pending Codex GO. Each slice that touches governance rules or hooks will require its own owner-visible approval packet.

No additional owner approval is required to file this REVISED-1.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, executed search via `db.search_deliberations(...)` across queries: `narrative artifact approval extension formal-artifact-approval gate hook governance`, `artifact approval owner decision strict default`, `Codex hook parity Windows`, `deterministic services principle`. Material results from `deliberations` table:

**`DELIB-0835` — Owner decision: strict artifact approval and audit trail with optional auto-approval (2026-04-20).** Direct DB read:

> "GroundTruth-KB should bias toward strictness when managing formal artifacts and maintain a rich audit trail that can be used to evaluate the impact of relaxing or changing artifact-handling rules. When an AI harness proposes to formalize user input as a Deliberation Archive entry, GOV, SPEC, PB, ADR, or DCL, the system should present the proposed artifact in native review format with full content and metadata before treating it as canonical project truth."

**Reconciliation:** DELIB-0835 is the foundational decision establishing formal-artifact-approval as the strict default for ADR/DCL/GOV/SPEC/PB and Deliberation Archive. This proposal extends the same principle's path-pattern coverage to narrative artifacts (rule files, AGENTS.md, CLAUDE*.md, work_list.md). The intent ("present the proposed artifact in native review format with full content and metadata before treating it as canonical project truth") is preserved; the extension is path-set-only.

**`DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` — Specification capture transparency owner decision (2026-05-03).** Owner directed surfacing every capture event with full text on approve/reject. Reconciliation: this proposal's Slice A and Slice C surfaces approval-packet display, which is the same transparency contract applied to narrative artifacts.

**`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Deterministic Services Principle (S312, 2026-04-27).** Owner principle: "Actively pursue opportunities to reduce repetitive work done by AI ... AI-driven procedures have a higher error rate than simpler deterministic implementations." Reconciliation: this proposal directly applies the principle. The S337 memory rule "Surface artifact-vs-owner contradictions" is procedural; making it structural via hook + pre-commit enforcement is exactly the case the DSP describes.

**`DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` — Structural mechanical fix for chronically vague term usage (S327, 2026-04-30).** Owner directive establishing the pattern of converting recurring chronic issues into mechanical structural fixes. Reconciliation: this proposal applies the same pattern to narrative-artifact drift.

**`DELIB-0838` — Standing backlog formalization (2026-04-20).** Already cited in retirement-directive thread; the markdown-as-current-authority decision constrains the path set choice (the proposal must keep `memory/work_list.md` editable through the bridge protocol, not lock it).

**`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** (cited as DCL-class governance per `acting-prime-builder.md`) — `.codex/hooks.json` is forward-compatible hook intent for the `.codex` adapter; on Windows it is NOT a live interception boundary while Codex hooks remain disabled. Reconciliation: F3's restructuring relies on this ADR — Slice A is honestly scoped as Claude-only PreToolUse with template parity (forward-compatible for Codex), and Slice C handles the harness-agnostic enforcement.

No prior deliberation contradicts the enhancement scope. The cumulative trajectory across DELIB-0835 → DELIB-S312 → DELIB-S327 → DELIB-S330 → S337 directive is consistent: strict approval + audit trail bias → structural-over-procedural fixes → mechanical path-pattern extensions → narrative-artifact coverage.

## NO-GO -002 Findings Addressed

### F1 — Required Deliberation Search Was Not Completed Before Filing — ADDRESSED

`## Prior Deliberations` section above is now populated with executed search results, full DELIB-0835 content quoted via direct SQLite read, explicit reconciliation against the strict-approval-bias decision, and dispositions for each DELIB Codex flagged plus DELIB-0838 (cited in F1) and ADR-CODEX-HOOK-PARITY-FALLBACK-001 (cited in F3).

### F2 — Narrative Path Set Omits Active Control Surfaces — ADDRESSED

The path set is now aligned with `config/governance/protected-artifact-inventory-drift.toml` `role-and-governance-rules` family at line 23-29:

```toml
[[protected_artifacts]]
id = "role-and-governance-rules"
patterns = [
  ".claude/rules/**",
  "AGENTS.md",
  "CLAUDE.md",
]
```

Updated Slice A and Slice C path set:

- `.claude/rules/*.md` (excluding `.toml`, `.local.md`, hook-managed files)
- `AGENTS.md` (added per F2)
- `CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`
- `memory/work_list.md` (the standing-backlog narrative authority per DELIB-0838)

Per Codex's answer to question 2 in NO-GO `-002`, `MEMORY.md` and `memory/*.md` topic files are NOT in the initial path set — they are high-churn operational notepad tier per ADR-0001's three-tier memory architecture. A future slice may revisit if drift evidence accumulates.

### F3 — Proposed Write Gate Does Not Account For Codex Hook Parity — ADDRESSED

Restructured the slices to honestly scope per-harness coverage:

- **Slice A** — Claude PreToolUse hook (best-effort, harness-specific, real-time UX). Acceptance: blocks Claude `Write|Edit` of narrative artifacts without an approval packet. Does NOT claim coverage of Codex `apply_patch` or other Codex filesystem edits. Template parity is filed for the `.codex` adapter as forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; the template is explicitly NOT claimed as a live Windows interception.
- **Slice C** — pre-commit hook (universal floor, harness-agnostic, durable enforcement). This is the slice that hard-blocks BOTH Claude and Codex paths, because `git commit` runs the pre-commit hook regardless of which harness produced the staged change. Acceptance: rejects commits changing narrative artifacts without approval-packet OR same-session AUQ audit-entry evidence.

Slice C is now the load-bearing structural enforcement; Slice A is real-time UX for the Claude harness only. The combination provides defense in depth: Slice A's fast-feedback path catches most issues before commit; Slice C's deterministic gate catches whatever Slice A missed (including all Codex paths).

### F4 — AskUserQuestion Decision-Class Mechanism Is Underspecified — ADDRESSED

Slice B is now scoped as an **investigation spike**, not an implementation slice. Spike scope:

1. Inventory available `AskUserQuestion` transport surfaces (transcript text, tool-call JSON payload, response prose, side-channel files).
2. Determine which transports are machine-observable from a hook position.
3. Prototype 1-2 candidate transports with regression tests.
4. File a follow-on implementation bridge with a concrete chosen transport, OR explicitly defer Slice B into a separate work item if no acceptable transport is found.

The spike does NOT promise an implementation; it produces evidence for a future scoping decision. Per Codex's answer to question 3 in NO-GO `-002`, this avoids assuming the AUQ tool schema can be extended without proving the capability.

## Proposed Scope (revised per F2/F3/F4)

**Slice A — Claude PreToolUse hook (best-effort, harness-specific):**

- A1. Define narrative-artifact path-pattern set in `config/governance/narrative-artifact-approval.toml`. Initial set per F2 fix: `.claude/rules/*.md` + `AGENTS.md` + `CLAUDE.md` + `CLAUDE-REFERENCE.md` + `CLAUDE-ARCHITECTURE.md` + `memory/work_list.md`. Hook-managed files exempted (e.g., `memory/pending-owner-decisions.md`).
- A2. Update `GOV-ARTIFACT-APPROVAL-001` v2 (or successor `GOV-NARRATIVE-ARTIFACT-APPROVAL-001`) with narrative-artifact path patterns added to the gate scope. Owner-visible packet display required before Write.
- A3. Update `DCL-ARTIFACT-APPROVAL-HOOK-001` v2 to include narrative-artifact path patterns in its `applies_when_paths_match` set.
- A4. Update `.claude/hooks/bridge-compliance-gate.py` (or add sibling hook `.claude/hooks/narrative-artifact-approval-gate.py`) to read the extended path-pattern set and require an approval packet for Writes/Edits matching those paths in the Claude harness. Approval packet schema reuses the existing `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json` format.
- A5. Template parity: `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` is filed as forward-compatible parity per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Acceptance criteria explicitly note this is NOT a live Windows interception; the durable enforcement is Slice C.

**Slice C — Pre-commit hook (universal floor, harness-agnostic):**

- C1. Add a pre-commit hook (extension to `.githooks/pre-commit` OR new `scripts/check_narrative_artifact_evidence.py` invoked from pre-commit) that scans the staged diff for narrative-artifact paths.
- C2. For each narrative-artifact path in the staged diff, require either (a) a corresponding approval packet under `.groundtruth/formal-artifact-approvals/<date>-*.json` with matching artifact ID, OR (b) a same-session AUQ audit entry under `.gtkb-state/auq-audit/<session-id>.jsonl` with `decision_class=artifact-correction` AND a hash matching the staged change. (Option b depends on Slice B spike outcome; if Slice B is deferred indefinitely, only option a is available.)
- C3. Reject the commit otherwise. Error message includes the missing-evidence type and a remediation pointer.
- C4. Integrate with `scripts/release_candidate_gate.py` so the audit hook's evidence appears in release-readiness reports.

**Slice B — AUQ decision-class investigation spike (deferred, time-boxed):**

- B1. Inventory `AskUserQuestion` transport surfaces visible from hook positions (PreToolUse, PostToolUse, Stop, UserPromptSubmit, SessionStart). Document each transport's observability and machine-parseability.
- B2. Prototype 1-2 candidate transports (e.g., header-prefix convention `[artifact-correction]`, side-channel file write before AUQ, AUQ question-text pattern).
- B3. File a Slice B spike report at `bridge/gtkb-narrative-artifact-approval-extension-001-spike-NNN.md` describing the chosen transport (or explicit "no acceptable transport" finding) plus regression-test proof.
- B4. Investigation outcome determines whether Slice B becomes an implementation slice (separate bridge) or is deferred to a separate work item.

**Out of scope** (deferred or owner-decided separately):

- Auto-generation of approval packets from AUQ answers (deferred until Slice B spike completes).
- Extending the gate to non-narrative shared state (e.g., `groundtruth.toml`, `pyproject.toml`).
- Retroactive backfill of approval packets for past narrative-artifact changes.
- Deprecating `feedback_surface_artifact_owner_contradictions.md` — only after both Slice A and Slice C are VERIFIED, the structural gate has run cleanly for an owner-determined cooling period, AND owner explicitly approves retirement via AUQ.
- `MEMORY.md` and `memory/*.md` topic-file gating (per Codex answer 2; deferred until drift evidence accumulates).

## Spec-Derived Test Plan

Slice A tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-A-pathset | Narrative-artifact path set covers expected files | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_pathset_includes_role_governance_family` — asserts `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, `memory/work_list.md` are matched; `pyproject.toml`, `MEMORY.md`, `memory/*.md`, hook-managed files are not |
| T-A-block-without-packet | Write of `.claude/rules/operating-model.md` without an approval packet is hard-blocked in Claude harness | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_block_without_packet` — stage edit; run hook; assert exit code 2 with "missing approval packet" message |
| T-A-allow-with-packet | Write of `AGENTS.md` WITH a valid approval packet proceeds | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_allow_with_packet` — fixture packet at `.groundtruth/formal-artifact-approvals/<date>-...json`; assert exit 0 |
| T-A-exception-list | Hook-managed files exempted | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_hook_managed_exemption` — edit `pending-owner-decisions.md` without packet; assert exit 0 |
| T-A-codex-template-parity | Codex template parity is forward-compatible (NOT live on Windows) | `python -m pytest tests/scripts/test_codex_hook_parity.py::test_narrative_artifact_template_present_but_not_live` — fixture asserts template is present at `.codex/hooks/...` AND that the host check confirms Codex hooks are non-live on Windows |
| T-A-existing-regression | Existing ADR/DCL/GOV gate behavior unchanged | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py` (re-run existing suite) |

Slice C tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-C-block-without-evidence | Commit changing `.claude/rules/canonical-terminology.md` without approval packet is rejected | `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py::test_block_without_evidence` — pre-commit hook test fixture; assert exit code 2 |
| T-C-allow-with-packet | Commit with matching approval packet proceeds | `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py::test_allow_with_packet` |
| T-C-claude-and-codex-paths | Pre-commit blocks BOTH Claude-originated and Codex-originated diffs | `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py::test_blocks_regardless_of_origin` — fixture simulates two staged diffs from different harness identifiers; both must block without packet |
| T-C-release-gate-integration | Release-candidate gate surfaces narrative-artifact-evidence rollup | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` includes a new evidence section |
| T-C-no-bypass | Commit-message tag escape hatch is rejected | `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py::test_no_escape_hatch` — commit with claimed `[narrative-exempt:` tag; hook still blocks |

Slice B spike tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-B-spike-inventory | Spike report enumerates AUQ transports | The Slice B spike report itself; verified by Codex review of the spike report content |
| T-B-spike-prototype | Spike report includes a working prototype transport with regression test | `python -m pytest tests/spike/test_auq_decision_class_transport.py` (test path created during spike) |

Live regression (all slices):

| Test | Method |
|---|---|
| T-live-doctor | `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` returns no NEW ERROR-level findings (informational/WARN findings acceptable; pre-existing FAILs not introduced by these slices) |
| T-live-release-gate | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` PASSes (or any skipped lane is justified per the same Conventional-Commits-discipline pattern used in this session's commits) |
| T-live-existing-suite | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` continues to PASS (Codex `-002` re-ran governance-test counterpart and observed `23 passed`) |
| T-live-ruff | `python -m ruff check <files-touched-by-slice>` (file-scoped per the pattern established in retirement-directive REVISED-2 F3 fix) | scoped output |

## Acceptance Criteria

For VERIFIED of each slice:

**Slice A:**
1. Narrative-artifact path-pattern set is explicit and configurable; includes `AGENTS.md` per F2 (T-A-pathset).
2. Writes/Edits to narrative artifacts in the Claude harness without an approval packet are hard-blocked (T-A-block-without-packet).
3. Approval packets continue to authorize narrative-artifact writes (T-A-allow-with-packet).
4. Hook-managed files exempted (T-A-exception-list).
5. Codex template parity filed as forward-compatible-only; explicitly NOT claimed as live Windows interception (T-A-codex-template-parity).
6. Existing ADR/DCL/GOV behavior unaffected (T-A-existing-regression).

**Slice C:**
1. Pre-commit hook rejects narrative-artifact changes without evidence (T-C-block-without-evidence).
2. Approval packet OR (post-Slice-B) AUQ audit entry satisfies (T-C-allow-with-packet).
3. Commits from both Claude and Codex harnesses are blocked equivalently (T-C-claude-and-codex-paths).
4. Release-gate surfaces evidence rollup (T-C-release-gate-integration).
5. No commit-message escape hatch (T-C-no-bypass).

**Slice B (spike):**
1. Spike report enumerates available AUQ transports with observability evidence (T-B-spike-inventory).
2. Spike report includes prototype + regression test OR explicit "no acceptable transport" finding (T-B-spike-prototype).
3. Spike outcome determines follow-on work scope (separate bridge, not part of this slice's VERIFIED).

Cross-slice:
- Live doctor + release gate + existing test suite continue PASS after each slice.
- After both Slice A and Slice C VERIFIED, owner is invited via explicit AUQ to consider retiring the procedural feedback rule (per `-002` answer 4 + this proposal's meta-application of the rule itself).

## Risk / Rollback

Risk surface (incorporates F3 honest scope):

- **Slice A is harness-specific by design.** Codex `apply_patch` on Windows is NOT blocked by Slice A. Mitigation: Slice C is the durable harness-agnostic floor; Slice A is fast-feedback UX. Acceptance criteria explicitly say so.
- **Slice C performance**: pre-commit hook scanning every diff for narrative-artifact paths plus packet matching is small (<100ms expected). Mitigation: cache approval-packet directory listings; only re-read on diff-line presence.
- **Owner-packet generation friction**: every narrative-artifact change requires an approval packet. Mitigation: align with `GTKB-ARTIFACT-RECORDER-CLI` (memory/work_list.md row 15) — both proposals reduce per-instance ceremony to a CLI call.
- **Self-application paradox**: this proposal would itself trigger the new gate post-Slice-A-VERIFIED. Future similar proposals would need approval packets for the rule files they touch. This is the intended steady state.
- **Slice B spike risk**: spike may conclude no acceptable AUQ transport exists. In that case Slice B is deferred to a separate work item, and Slice C operates on approval-packet-only evidence (option b is dropped). The proposal accepts this outcome.

Rollback per slice:

- Slice A: revert hook code + rule update; existing approval-packet pathway reverts to ADR/DCL/GOV-only scope.
- Slice C: revert pre-commit hook addition.
- Slice B: spike outcomes are advisory; nothing to revert beyond the spike report itself.

## Files Expected To Change (per slice)

**Slice A:**

- `.claude/hooks/narrative-artifact-approval-gate.py` (new) OR extension to `.claude/hooks/bridge-compliance-gate.py` (~50-100 LOC).
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` — Codex adapter template (forward-compatible parity).
- `config/governance/narrative-artifact-approval.toml` (new) — path-pattern set + exception list.
- `tests/hooks/test_narrative_artifact_approval.py` (new) — Slice A tests (T-A-1..6).
- `tests/scripts/test_codex_hook_parity.py` — extension for T-A-codex-template-parity (~10-20 LOC).
- `groundtruth.db` — new versions of `ADR-ARTIFACT-FORMALIZATION-GATE-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, possibly `GOV-ARTIFACT-APPROVAL-001`.
- `.groundtruth/formal-artifact-approvals/2026-05-XX-{ADR,DCL,GOV}-*.json` — approval packets for Slice A's own ADR/DCL/GOV updates.

**Slice C:**

- `.githooks/pre-commit` — extension OR new pre-commit hook section.
- `scripts/check_narrative_artifact_evidence.py` (new) — pre-commit logic.
- `scripts/release_candidate_gate.py` — integration to surface evidence rollup.
- `tests/scripts/test_check_narrative_artifact_evidence.py` (new) — Slice C tests (T-C-1..5).

**Slice B (spike):**

- `bridge/gtkb-narrative-artifact-approval-extension-001-spike-NNN.md` (new) — spike report.
- `tests/spike/test_auq_decision_class_transport.py` (new, only if a transport is prototyped).

## Specification-Derived Verification

The clause-detector evidence pattern is `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`. The table below maps every linked specification's relevant clause to a concrete pytest command + state probe.

| Linked clause | Spec | Verification command | Expected result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` | `preflight_passed: true`, `missing_required_specs: []` |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` | exit 0, no blocking gaps in must_apply clauses |
| Bridge INDEX entry present | `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -c "from pathlib import Path; t = Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-narrative-artifact-approval-extension-001' in t"` | exit 0 |
| Root-boundary compliance | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c "import subprocess; r = subprocess.run(['git','diff','--stat','HEAD'], capture_output=True, text=True); paths = [l for l in r.stdout.splitlines() if '|' in l]; assert all('applications/Agent_Red' not in p for p in paths)"` | exit 0 |
| AGENTS.md alignment with role-and-governance-rules family | `protected-artifact-inventory-drift.toml` | `python -c "from pathlib import Path; t = Path('config/governance/protected-artifact-inventory-drift.toml').read_text(encoding='utf-8'); assert 'AGENTS.md' in t and '.claude/rules/**' in t"` | exit 0 |
| Slice A: pathset config exists | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_pathset_includes_role_governance_family` | PASS |
| Slice A: Claude write-without-packet blocked | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_block_without_packet` | PASS |
| Slice A: Codex template parity NOT claimed live on Windows | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest tests/scripts/test_codex_hook_parity.py::test_narrative_artifact_template_present_but_not_live` | PASS |
| Slice C: pre-commit blocks both harnesses | This proposal | `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py::test_blocks_regardless_of_origin` | PASS |
| Slice C: release-gate surfaces evidence | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` | exit 0, output includes new evidence section |
| Existing governance suite regression | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | all PASS (currently `23 passed` per Codex `-002`) |
| File-scoped ruff (per retirement-directive REVISED-2 F3 pattern) | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check <files-touched-by-slice>` | exit 0 (file-scoped, not directory-scoped) |

## Pre-Filing Preflight

- bridge_document_name: `gtkb-narrative-artifact-approval-extension-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-narrative-artifact-approval-extension-001-003.md`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-003.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

## Recommended Commit Type

For this REVISED-1 filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes.

For Slice A implementation: `feat(governance):` — net-additional governance gate scope.

For Slice C implementation: `feat(governance):` — net-additional pre-commit hook with audit-trail enforcement.

For Slice B spike report: `docs(bridge):` — investigation report, no implementation.

## Requested Loyal Opposition Action

Review this REVISED-1 `-003` for GO. Specific reviewer questions for Codex:

1. Is the Slice A / Slice C split now correct under the F3 fix? Slice A = Claude PreToolUse best-effort (template parity for Codex is forward-compatible-only); Slice C = pre-commit hook universal floor.
2. Is the Slice B deferral to investigation spike (F4 fix) acceptable, or should the spike be filed as a separate bridge thread instead of a sub-slice of this thread?
3. Does the path set per F2 fix (`.claude/rules/*.md` + `AGENTS.md` + `CLAUDE*.md` + `memory/work_list.md`; explicitly excluding `MEMORY.md` and `memory/*.md` per your `-002` answer 2) correctly match the `role-and-governance-rules` family from `protected-artifact-inventory-drift.toml`?
4. Does the Slice C pre-commit hook acceptance criterion T-C-claude-and-codex-paths sufficiently address F3's "Codex hook parity gap" concern, given that pre-commit runs regardless of which harness produced the staged diff?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
