NEW

# Implementation Proposal — GTKB-ISOLATION-018 Sub-sub-slice 18.E.3: Platform-Test Disposition Decision

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-07 (S334)
**Type:** Decision-making sub-sub-slice for 18.E. Resolves OQ-E3 (platform-test disposition) before E.1's atomic code-cluster move can be drafted. No file moves or code edits; deliverable is an owner-decision artifact + concretized platform-test list.
**Predecessor:** `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` (Codex GO on 18.E scoping `-003`).
**Risk tier:** Low (no implementation; decision artifact + AUQ).

---

## Specification Links

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: this E.3 proposal's tests are limited to T-bridge-1, T-spec-1, T-spec-2, T-decision-1 (decision recorded), T-test-list-1 (platform-test list enumerated) since no implementation occurs.

Cross-cutting advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` (18.E scoping GO; defines this E.3 sub-sub-slice)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` (18.E scoping REVISED-1; OQ-E3 framing including Option A testpaths consequence)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED; pattern precedent for platform-content exclusions in docs/)
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED; pattern precedent)
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

This proposal frames OQ-E3 for owner AUQ resolution; it does not pre-decide.

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "18.E structure — single atomic slice or sub-split into reviewable sub-sub-slices?" (S334) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" | Authorizes filing this E.3 sub-sub-slice. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation as release-gating; only blocking technical dependencies authorize deferral. | Authorizes 18.E program. |
| OQ-E3 (this E.3's deliverable) | (PENDING — to be AUQ'd after Codex GO on this `-001`) | Owner chooses Option A or Option B | Resolution recorded in this thread's `-003` REPORT. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Authorizes in-flight pre-migration state. |

## Goal

Resolve OQ-E3 (Option A vs Option B for platform-test disposition) so 18.E.1's exact `tests/` scope and `pyproject.toml` plan can be concretized.

**Deliverable:** owner-AUQ-recorded choice + concretized platform-test list (exact files staying at root vs. migrating).

## Live-Probed Platform-Test Inventory (2026-05-07)

`git ls-files tests/ | wc -l` = **731 files total**.

### tests/hooks/ — 13 files (all-stay candidates)

All test GT-KB platform `.claude/hooks/*.py`:

```
tests/hooks/__init__.py
tests/hooks/fixtures/owner_decision_tracker/turn_multiple_askuserquestion.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_truncated.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_askuserquestion_answered.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_askuserquestion_pending.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_many_prose_decisions.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_and_askuserquestion.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_decision.jsonl
tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py
tests/hooks/test_credential_scan.py
tests/hooks/test_formal_artifact_approval_gate.py
tests/hooks/test_owner_decision_tracker.py
tests/hooks/test_workstream_focus.py
```

3 of these directly reference `.claude/` via `parents[2]` or similar.

### tests/scripts/ — 19 platform-related files of 69 total

Platform-test subset (test `scripts/*.py` or platform-orchestration scripts):

```
tests/scripts/test_check_harness_parity.py
tests/scripts/test_claude_session_start_dispatcher.py
tests/scripts/test_codex_hook_parity.py
tests/scripts/test_command_registry_tracking.py
tests/scripts/test_dashboard_subject_selector.py
tests/scripts/test_generate_bridge_swimlane.py
tests/scripts/test_generate_codex_skill_adapters.py
tests/scripts/test_groundtruth_governance_adoption.py
tests/scripts/test_gtkb_overlay.py
tests/scripts/test_rehearse_dashboard_regen.py
tests/scripts/test_rehearse_path_rewrite.py
tests/scripts/test_release_candidate_gate.py
tests/scripts/test_retroactive_harvest_bridge_threads.py
tests/scripts/test_run_spec_derived_tests.py
tests/scripts/test_session_self_initialization.py
tests/scripts/test_wrap_scan_hygiene_skip_dirs.py
+ 3 more (per grep `\.claude/` count = 13; some share fixtures/__init__.py)
```

50 of 69 `tests/scripts/` files are NOT platform-related → they migrate with E.1 to `applications/Agent_Red/tests/scripts/`.

### Other tests/ subdirs

No other subdir references `.claude/`. All other tests migrate with E.1.

### Estimated platform-test set sizes

- **Option A (subdir-level / per-file split at root):** ~32 files stay at root (13 tests/hooks + ~19 platform-related tests/scripts)
- **Option B (parents[N] rewrite, all migrate):** 0 files stay at root; ~25 platform-test files get a one-shot `parents[2]` → `parents[3]` source-code edit

## Option A vs Option B — Trade-Off (per 18.E scoping -003 F4 Fix)

### Option A — Split at the test-subdir / per-file level

**Mechanism:**
- `tests/hooks/` (13 files) stays at root
- ~19 platform-related `tests/scripts/` files stay at root; rest of `tests/scripts/` (~50) migrates with `tests/`
- All other `tests/*` migrates to `applications/Agent_Red/tests/`
- `pyproject.toml` `testpaths` set to `["tests", "applications/Agent_Red/tests"]` (dual discovery)

**Pros:**
- Zero source-code edits to test files
- Platform tests remain at expected GT-KB-platform location
- After 18.J repo-separation, platform tests live in GT-KB platform repo cleanly; Agent Red tests live in Agent Red repo cleanly

**Cons:**
- `tests/scripts/` requires per-file disposition (50 Agent Red tests vs ~19 platform tests)
- Persistent dual-discovery `testpaths` config until 18.J
- Two `tests/` directories during the migration window may confuse new contributors

**E.1 implication:** ~1,491-1,503 files moved; 0 source-code edits to platform-test files; pyproject.toml `testpaths` becomes a 2-element list.

### Option B — Update parents[N] in platform-test files

**Mechanism:**
- All ~731 `tests/*` migrate to `applications/Agent_Red/tests/`
- Platform-test files (~25 files identified above + any discovered during E.1 probe) have `Path(__file__).resolve().parents[2]` rewritten to `parents[3]` to walk up past `applications/Agent_Red/` to repo root
- `pyproject.toml` `testpaths` set to `["applications/Agent_Red/tests"]` (single)

**Pros:**
- Single `testpaths` config — clean post-migration
- Mechanical one-shot edit (~25 files)
- All Agent Red CI runs pytest against single tests location
- After 18.J, platform tests sit alongside Agent Red product tests in the new repo (which may or may not be desired — see Con below)

**Cons:**
- ~25 source-code edits to test files
- Edits create coupling between platform-test files and their location depth (if any platform test moves, parents[3] may need re-adjustment)
- Platform tests (testing `.claude/hooks/*.py`) live in `applications/Agent_Red/tests/` which is semantically odd — they test the GT-KB platform but live in the Agent Red app
- After 18.J repo-separation, platform-test files would presumably move OUT of the Agent Red repo back to GT-KB platform; Option B would require a follow-up migration

**E.1 implication:** ~1,516 files moved; ~25 platform-test files get `parents[2]` → `parents[3]` edit; pyproject.toml `testpaths` is 1-element list.

### Recommended Default

This proposal recommends **Option A** as the default for the OQ-E3 AUQ. Rationale:

1. **Semantic alignment:** Platform tests test GT-KB platform; they belong in GT-KB platform tree. Option A keeps that alignment without a future-undo.
2. **Source-edit avoidance:** Option B adds 25 source-code edits during E.1's already-large commit. Option A keeps E.1 to file moves + path-string edits, no source-code edits to test logic.
3. **18.J cleanliness:** After repo separation, Option A has platform tests already in the right place. Option B would require migrating them again.
4. **Persistent dual-discovery cost is bounded:** `pyproject.toml`'s `testpaths = ["tests", "applications/Agent_Red/tests"]` is 1 line of config; running `pytest` discovers both correctly. The "complexity" is config-only, not runtime.

The owner may override this recommendation via AUQ.

## Migration Strategy (E.3-specific)

E.3 is a decision-making sub-sub-slice. There is no file move or code edit performed by E.3 itself. The strategy is:

1. **Codex GO on this `-001`** (approves the framing + recommended default + platform-test list)
2. **AUQ the owner** with the OQ-E3 question (Option A vs Option B)
3. **File `-003` REPORT** capturing the owner's choice + the concretized platform-test list (which exact files stay vs. migrate under the chosen option)
4. **Codex VERIFIED on `-003`** (decision artifact accepted; E.1 can now draft against the resolved scope)

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-e3-platform-test-disposition" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal contains Specification Links + spec-to-test mapping + executed evidence | Section present |
| **T-decision-1** | E.3 deliverable | Owner AUQ answer recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question` | Owner's choice (A or B) captured durably |
| **T-test-list-1** | E.3 deliverable | E.3 `-003` REPORT contains the exact platform-test file list (concretized for E.1) | List enumerated |
| **T-list-coverage-1** | platform-test list completeness | `grep -lE "Path\(__file__\)\.resolve\(\)\.parents\[[0-9]\] / \"\\.claude\""  tests/ -r` returns exactly the platform-test files in the E.3 list | Coverage matches |

## Acceptance Criteria

This `-001` proposal is accepted when:
- [ ] Codex GO on this `-001`
- [ ] Platform-test inventory above accepted as comprehensive (or amended via Codex feedback)
- [ ] Option A vs Option B trade-off framing accepted
- [ ] Recommended default (Option A) accepted as the proposal's recommendation (without binding the owner's AUQ choice)
- [ ] AUQ resolution path defined (AUQ → answer recorded → -003 REPORT enumerated platform-test list → Codex VERIFIED)

E.3 sub-sub-slice is VERIFIED when:
- [ ] Codex GO on this `-001`
- [ ] Owner AUQ answered (A or B)
- [ ] `-003` REPORT filed with concretized platform-test list per chosen option
- [ ] Codex VERIFIED on `-003`

## Risk / Rollback

**Risks:** Low. No implementation; only decision-recording.

**Rollback:** Owner can re-AUQ to change the choice if E.1 implementation surfaces unforeseen issues. The platform-test list can be amended in a follow-up bridge thread.

## Open Questions

| ID | Question | Resolution path |
|---|---|---|
| **OQ-E3** | Option A (subdir/per-file split at root, dual `testpaths`) vs Option B (parents[N] rewrite, single `testpaths`)? | Owner AUQ after Codex GO on this `-001`. Default = Option A. |

## Out of Scope

This E.3 proposal does NOT:
- Perform any file moves
- Perform any source-code edits (parents[N] rewrites are E.1's job under Option B; per-file split is E.1's job under Option A)
- Update any registry, workflow, pyproject, or source code
- Cover E.1 implementation or E.2 scripts split
- Cover any other sub-slices (18.F-L)

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`
- Does not introduce live dependencies on paths outside `E:/GT-KB/`
- Cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE
- Per `.claude/rules/project-root-boundary.md`

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above
2. KB-search — no prior deliberation rejects this E.3 framing
3. Bridge-governance specs — cited
4. Preflight to be run after INDEX update
5. `packet_hash` recorded after preflight

## Provenance

| Source | Reference |
|---|---|
| Triggering scoping GO | `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` (Codex GO on 18.E scoping; defined E.3 as the platform-test disposition decision) |
| OQ-E3 framing source | `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` (REVISED-1 with F4 Option A testpaths consequence) |
| Live probes | `git ls-files tests/hooks/` returns 13 files; `tests/scripts/` filtered for platform refs returns ~19 files; `tests/__init__.py` shared (executed 2026-05-07) |
| Pattern precedent (subdir-level platform exclusions) | `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED; docs/gtkb-dashboard/, docs/specification-scaffold/, docs/assets/gtkb-dashboard/ stayed at root) |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
