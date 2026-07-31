NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c07bb3a9-1b5b-4f30-a1e9-7c357de03ea3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless automation (keep-working-pb scheduled task); Prime Builder

# GT-KB Bridge Implementation Report - WI-3407 Composite DELIB Workflow for Decision Capture Skill

bridge_kind: implementation_report
Document: gtkb-wi3407-composite-delib-workflow-skill
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi3407-composite-delib-workflow-skill-002.md
Approved proposal: bridge/gtkb-wi3407-composite-delib-workflow-skill-001.md
Recommended commit type: feat:

Project Authorization: PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: GTKB-V1-RELEASE-STRATEGY-001
Work Item: WI-3407

Implementation-start packet hash: `sha256:980fad7416026282ee1baef9f1cc2edc2b71044c3bce65489250ee9e4fd32b14`
Implementation-start created_at: `2026-07-09T02:13:01Z`
Work-intent claim session: `c07bb3a9-1b5b-4f30-a1e9-7c357de03ea3`
Work-intent claim acquired_at: `2026-07-09T02:12:46Z`
Work-intent claim rowid: `30878`

Local commit: `2bf26a40`

target_paths: [".claude/skills/decision-capture/SKILL.md", ".claude/skills/decision-capture/helpers/record_decision.py", ".codex/skills/decision-capture/SKILL.md", ".codex/skills/decision-capture/helpers/record_decision.py", "platform_tests/skills/test_decision_capture_skill.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py"]

## Implementation Claim

Implemented the WI-3407 composite owner-decision capture workflow slice
authorized by the GO verdict, strictly within the GO target paths.

- Added a `## Composite owner-decision workflow` section to the canonical
  `.claude/skills/decision-capture/SKILL.md` documenting: when to consolidate
  several AskUserQuestion answers into one composite Deliberation Archive
  record versus split them into atomic records; the four-section composite
  content shape (`## Decisions`, `## Composed Implications`,
  `## Linked Artifacts`, `## First Concrete Actions Authorized`); source-ref /
  AUQ-id naming (AUQ-`<n>` form for AUQ answers, `§9.1` section-anchor form for
  predecessor deliberation questions, matching the `DELIB-2234` exemplar); and
  an explicit statement that the fixed write-path metadata
  (`source_type="owner_conversation"`, `outcome="owner_decision"`, fixed
  `changed_by` / `change_reason`) and the atomic single-decision path are
  preserved unchanged.
- Added a pure `compose_composite_content()` composer plus a frozen
  `CompositeDecision` dataclass and a `CompositeCompositionError` to
  `.claude/skills/decision-capture/helpers/record_decision.py`. The composer
  performs no database access and no redaction; it builds the composite
  markdown body that is then passed to the existing `record_decision()` write
  path, so composite records flow through the same append-only, fixed-metadata,
  collision-guarded insert as atomic records. Cells are pipe-escaped; empty
  optional sections are omitted; empty/blank inputs raise
  `CompositeCompositionError`.
- Left the existing atomic `record_decision()` contract, its fixed-metadata
  constants, and its collision guard byte-for-byte unchanged (the diff is a
  pure addition of 126 lines to the canonical helper, 0 deletions).
- Regenerated the Codex adapter surfaces
  (`.codex/skills/decision-capture/SKILL.md` and
  `.codex/skills/decision-capture/helpers/record_decision.py`) via
  `scripts/generate_codex_skill_adapters.py`, and staged only the
  decision-capture `source_sha256` hunk of `.codex/skills/MANIFEST.json` (the
  unavoidable consequence of the GO-mandated adapter regeneration).
- Added `platform_tests/skills/test_decision_capture_skill.py` (16 tests)
  covering the skill guidance, the composer behavior, atomic-path/fixed-metadata
  preservation, and Codex cross-harness parity.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implemented only after this thread's GO, a
  live work-intent claim (rowid 30878), and the implementation-start packet
  above; all changes committed as a single scoped commit `2bf26a40`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - work performed under the
  active v1 release-strategy PAUTH which includes WI-3407.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH did not bypass the
  bridge GO or implementation-start gate; both were satisfied.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries
  machine-readable PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the spec links are
  carried forward and mapped to tests below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and
  executed verification evidence are provided below.
- `SPEC-2098` - the Deliberation Archive protocol governs the durable
  owner-decision capture behavior the composer preserves.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001`
  - the `.codex/**` adapter surfaces were regenerated and parity was proved via
  `--check` and adapter-sha tests.
- `GOV-STANDING-BACKLOG-001` - WI-3407 remains the MemBase backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the composite workflow makes owner
  decisions that cross from chat into durable project behavior a structured,
  lifecycle-clear artifact.

## Spec-to-Test Mapping

| Requirement / specification | Test evidence |
|---|---|
| Composite owner decisions preserve DA protocol + prior-decision citations (`SPEC-2098`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) | `test_skill_documents_composite_workflow_sections`, `test_skill_names_the_four_composite_content_sections`, `test_skill_documents_consolidate_split_and_naming` |
| Helper preserves fixed DA metadata and collision behavior (`SPEC-2098`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) | `test_record_decision_fixed_metadata_unchanged`, `test_record_decision_collision_raises` |
| Composite workflow encodes S363 structure (Decisions table, Composed Implications, Linked Artifacts, First Concrete Actions, source-ref/AUQ-id) | `test_compose_produces_all_sections_and_preserves_source_refs`, `test_compose_minimal_omits_empty_optional_sections`, `test_compose_escapes_pipe_in_cells`, `test_compose_rejects_empty_or_blank_inputs` |
| Existing single-decision behavior remains available | `test_skill_preserves_atomic_path_and_fixed_metadata`, `test_composite_content_flows_through_atomic_write_path` |
| Cross-harness skill parity preserved (`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001`) | `test_codex_adapter_matches_canonical_sha`, `test_codex_helper_carries_composer_for_parity`, plus `generate_codex_skill_adapters.py --check` (PASS) and `platform_tests/scripts/test_generate_codex_skill_adapters.py` (all pass) |
| GT-KB governance adoption still includes decision-capture files | `platform_tests/scripts/test_groundtruth_governance_adoption.py` decision-capture required-file assertions (pass) |

## Required Verification Commands + Observed Results

```text
python -m pytest platform_tests/skills/test_decision_capture_skill.py -q --tb=short
```
Result: `16 passed`.

```text
python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_codex_skill_load_smoke.py platform_tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```
Result: `64 passed, 1 failed`. The single failure is
`test_codex_config_registers_formal_artifact_approval_hook_intent`, which
asserts `.codex/config.toml` `[features] hooks is True`. This is a
**pre-existing baseline failure unrelated to WI-3407**: `.codex/config.toml` is
unchanged from HEAD (not in this commit, not dirty) and intentionally carries
`hooks = false` under the committed "WI-4896 containment" comment. The test
expectation is stale relative to that containment decision. It is outside the
WI-3407 target paths and is surfaced below as a hygiene finding.

```text
python scripts/generate_codex_skill_adapters.py --check
```
Result: `PASS (42 adapters current)`.

Code-quality gates on changed Python files (`ruff check` and `ruff format
--check` run separately per protocol):

```text
python -m ruff check <changed .py>          -> All checks passed!
python -m ruff format --check <changed .py>  -> 3 files already formatted
```

## Cross-Harness Disposition

Claude Code (canonical) and Codex (adapter) surfaces are reconciled: the
canonical `.claude` SKILL.md and helper were edited, the `.codex` adapter and
helper were regenerated, `--check` passes, and the adapter-sha / helper-parity
tests pass. No other harness-specific file was mutated in this slice, matching
the GO's "Other registered harnesses: no direct harness-specific file
mutation" disposition. Note: the harness-capability registry TOML retains its
prior recorded `source_sha256` for the codex/antigravity/goose decision-capture
adapters; that registry sha is not validated by the GO's required verification
commands and updating it is out of the GO target-path scope. It is surfaced as
a hygiene finding below.

## Scope Notes

- `.codex/skills/MANIFEST.json` is not among the GO's seven `target_paths`, but
  the GO required running `generate_codex_skill_adapters.py`, which
  deterministically updates the decision-capture `source_sha256` in the
  manifest. Only that single decision-capture hunk was staged (via a
  hunk-scoped `git apply --cached`); a pre-existing unrelated advisory-disposition
  manifest hunk in the working tree was deliberately left unstaged and
  unchanged.
- The working tree carries a large pre-existing set of unrelated modified files
  on the `research` branch; none were staged. The commit is scoped to the six
  decision-capture files above.

## Hygiene Findings (out of scope; captured for follow-on)

1. `test_codex_config_registers_formal_artifact_approval_hook_intent`
   (`platform_tests/scripts/test_groundtruth_governance_adoption.py`) asserts
   `.codex/config.toml` `[features] hooks is True`, but the committed config sets
   `hooks = false` under WI-4896 containment. The test and the containment
   decision have drifted; one should be reconciled (either the test updated to
   accept the containment state, or the containment lifted when WI-4896 clears).
2. The harness-capability-registry `source_sha256` fields for the
   decision-capture codex/antigravity/goose adapters lag the canonical SKILL.md
   sha after this change. If a future check validates registry shas against
   canonical, a registry-refresh step should be added to the adapter
   regeneration flow.

## Verification Request

Requesting Loyal Opposition post-implementation verification against the linked
specifications and the spec-to-test mapping above. All GO-required verification
commands were executed; the only failure is the documented pre-existing,
out-of-scope WI-4896 config-containment test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
