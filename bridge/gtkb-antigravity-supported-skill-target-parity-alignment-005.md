REVISED

# Implementation Proposal (REVISED) - Antigravity Supported Skill-Target Parity Alignment (+ WI-4841 completion)

bridge_kind: prime_proposal
Document: gtkb-antigravity-supported-skill-target-parity-alignment
Version: 005
Date: 2026-07-09 UTC
Responds to: bridge/gtkb-antigravity-supported-skill-target-parity-alignment-004.md

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: ["platform_tests/skills/test_advisory_disposition_skill.py", "platform_tests/skills/test_skill_governance_lifecycle_skill.py", "platform_tests/skills/test_formal_artifact_packet_helper_skill.py", "platform_tests/skills/test_managed_skill_adoption_review_skill.py", "config/agent-control/harness-capability-registry.toml", ".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/MANIFEST.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ac6ded12-902d-4b58-b9f2-b31dedb5d5b8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Summary

Per owner decision `DELIB-202665926` (antigravity is a supported managed-skill
projection target), align the stale `antigravity = "unsupported"` parity
assertions in the PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT skill tests to
`antigravity = "adapter"`, and complete WI-4841 (managed-skill-adoption-review)
by creating its canonical `.claude` source, adding its capability registry entry,
generating its cross-harness adapters, and adding its focused parity test
consistent with that decision.

## Revision History

- `-001` (NEW; GO at `-002`): asserted the managed-skill-adoption-review
  `.claude` canonical source already existed and omitted it from `target_paths`.
- `-003` (REVISED; GO at `-004`): corrected that false premise - the `.claude`
  source did NOT exist (only an untracked `.codex` body) - and added
  `.claude/skills/managed-skill-adoption-review/SKILL.md` to `target_paths`.
- `-005` (this REVISED): during implementation take-over (from a stalled
  concurrent Prime session that had created only the `.claude` source),
  canonical-state verification found TWO more gaps the `-004` GO scope did not
  cover:
  1. The antigravity adapter generator writes `.agent/skills/MANIFEST.json` to
     register a new `.agent` adapter, but `-003/-004` `target_paths` omitted that
     manifest (it listed only `.codex/skills/MANIFEST.json`). This REVISED adds
     `.agent/skills/MANIFEST.json` to `target_paths`.
  2. `.agent/skills/MANIFEST.json` carries PRE-EXISTING drift unrelated to
     WI-4841: seven skills (`bridge`, `lo-opportunity-radar`, `codex-report`,
     `decision-capture`, `projects`, `gtkb-benchmarks`,
     `loyal-opposition-hygiene-assessment`) have stale `source_sha256` values
     because prior sessions edited their `.claude` sources and regenerated the
     Codex side (`generate_codex_skill_adapters.py --check` PASSES) but not the
     antigravity manifest (`generate_antigravity_skill_adapters.py --check`
     FAILS on those 7 shas). Because this proposal's acceptance criterion
     requires antigravity `--check` to PASS, regenerating the antigravity
     manifest to register managed-skill-adoption-review will ALSO normalize
     those 7 stale shas as a forced, deterministic side effect. This is
     disclosed here so Loyal Opposition can GO the widened scope knowingly.

This drift is a live instance of the detection-coverage gap captured as WI-5098
(codex-only `--check` does not detect antigravity manifest drift). This proposal
does not fix that systemic gap; it only normalizes the concrete stale shas that
block antigravity `--check` for this thread.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202665926` ratifies antigravity support
and is the typed parity waiver the WI-4839..4842 proposals contemplated. No new
requirement capture is needed; this change aligns tests and registry to the
ratified platform behavior and completes the WI-4841 scaffold by projecting an
already-authored skill body into its canonical location and its cross-harness
adapters.

## Problem / Context

Three skill parity tests still assert `antigravity["status"] == "unsupported"`,
from pre-antigravity-harness proposal language, and now FAIL against the current
registry:

- `test_advisory_disposition_skill.py` (line 159) - regressing the previously VERIFIED WI-4840.
- `test_skill_governance_lifecycle_skill.py` (line 147).
- `test_formal_artifact_packet_helper_skill.py` (its 4-harness assertion loop, line 172).

WI-4841 (managed-skill-adoption-review) lacks a capability registry entry, its
generated Codex + antigravity adapters, its manifest entries, and a focused
parity test. Its canonical `.claude` source now exists on disk (created during
take-over, a faithful reconstruction of the untracked `.codex` body) but is
untracked and unregistered.

## Proposed Scope

1. Keep the canonical source `.claude/skills/managed-skill-adoption-review/SKILL.md`
   (faithful reconstruction of the `.codex` body; verified byte-consistent).
2. Add the `skill.managed-skill-adoption-review` capability registry entry
   (`kind="skill"`, `canonical_source=".claude/skills/managed-skill-adoption-review/SKILL.md"`,
   `required_for_roles`, `parity_class="baseline"`), plus a base
   `[capabilities.claude] status="native"` block and a `[capabilities.cursor]
   status="unsupported"` block with a reason - modeled on the
   `skill.advisory-disposition` block. The codex + antigravity blocks are filled
   by the generators.
3. Run BOTH adapter generators with `--update-registry` so they read the new
   canonical source and produce the codex adapter, the antigravity adapter, the
   codex/antigravity registry blocks, the `.codex/skills/MANIFEST.json` entry,
   and the `.agent/skills/MANIFEST.json` entry:
   `scripts/generate_codex_skill_adapters.py --update-registry` then
   `scripts/generate_antigravity_skill_adapters.py --update-registry`. Yielded
   matrix: claude=native, codex=adapter, antigravity=adapter, cursor=unsupported.
   Regenerating `.agent/skills/MANIFEST.json` also normalizes the 7 pre-existing
   stale shas disclosed in Revision History (forced by the antigravity `--check`
   acceptance criterion). Confirm the generators touch ONLY the
   managed-skill-adoption-review adapters, the registry, `.codex/skills/MANIFEST.json`,
   and `.agent/skills/MANIFEST.json` (the codex side is already current: 42
   codex adapters PASS `--check`).
4. Align the antigravity parity assertions in the three named tests to
   `antigravity = "adapter"`. In `test_formal_artifact_packet_helper_skill.py`,
   rewrite the 4-harness assertion loop so antigravity asserts `adapter`, cursor
   asserts `unsupported`, and ollama/openrouter are dropped (not enumerated in
   these skills' registry blocks; `DELIB-202665926` is antigravity-scoped).
5. Add `platform_tests/skills/test_managed_skill_adoption_review_skill.py`
   modeled on `test_formal_artifact_packet_helper_skill.py`, asserting the
   generator-produced matrix (claude=native, codex=adapter, antigravity=adapter,
   cursor=unsupported) plus adapter existence, manifest entries, canonical-source
   frontmatter, and target-paths-in-root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - antigravity is now a supported parity target per `DELIB-202665926`.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - skill registry/adapter/catalog invariants.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `GOV-STANDING-BACKLOG-001` - WI linkage preserved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance linkage.

## Owner Decisions / Input

- `DELIB-202665926` (owner AUQ, 2026-07-09): antigravity is a supported managed-skill projection target; align stale `antigravity = "unsupported"` tests to `antigravity = "adapter"`; typed parity waiver for WI-4839..4842.
- Owner AUQ, this session (2026-07-09, session `ac6ded12-902d-4b58-b9f2-b31dedb5d5b8`), reframe of `-001`: selected "One REVISED, full scope" after the `.claude`-source-exists premise was found false (produced `-003`).
- Owner AUQ, this session (2026-07-09): after a concurrent Prime session (`d97ced75`) claimed the `-004` GO and then stalled, the owner authorized force-releasing its lease and taking over to complete the implementation.
- Owner AUQ, this session (2026-07-09): after take-over verification found `.agent/skills/MANIFEST.json` omitted from `target_paths` and carrying pre-existing 7-sha drift, the owner selected "REVISED -005; bundle the disclosed normalization" - add the antigravity manifest to `target_paths` and normalize the 7 pre-existing stale shas (forced by the antigravity `--check` criterion), disclosed here.
- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842`: active project authorization (no expiry) covering WI-4839..4842 with mutation classes source + test.

## Prior Deliberations

- `DELIB-202665926` - owner ratification; the authority for this proposal.
- `DELIB-20266596` - owner AUQ approval for bounded WI-4839..4842 skill-scaffold implementation.
- `DELIB-20265883` - owner-directed creation of PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT.
- `bridge/gtkb-antigravity-supported-skill-target-parity-alignment-004.md` - the LO GO on `-003`; superseded by this REVISED because implementation revealed the antigravity-manifest scope gap and pre-existing drift.
- `bridge/gtkb-antigravity-supported-skill-target-parity-alignment-002.md` - the LO GO on the original `-001` false premise.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-014.md` - prior NO-GO (Codex `.codex` write boundary, since resolved); source of the untracked `.codex` body reconstructed here. This umbrella supersedes that thread's remaining WI-4841 scope; WITHDRAWN after this thread VERIFIES.
- `bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-021.md` - prior NO-GO; its stale antigravity test assertion is aligned here.
- `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-010.md` - VERIFIED WI-4840 whose parity test is regressed by the antigravity registry state and un-regressed here.
- `WI-5098` - the detection-coverage backlog item capturing the systemic gap this thread's pre-existing drift instantiates.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run pytest over the four skill tests (test_advisory_disposition_skill.py, test_skill_governance_lifecycle_skill.py, test_formal_artifact_packet_helper_skill.py, test_managed_skill_adoption_review_skill.py) via the project venv python -> all pass (un-regresses WI-4840). |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run scripts/generate_codex_skill_adapters.py --check and scripts/generate_antigravity_skill_adapters.py --check -> both PASS; antigravity --check PASS requires the disclosed 7-sha normalization; registry matrix consistent with DELIB-202665926. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run pytest over platform_tests/skills/test_skill_catalog_contract.py -> pass. |
| Code quality | ruff check plus ruff format --check on the four changed/added test files (both gates). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability + clause preflights pass (missing_required_specs empty; 0 blocking gaps). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under E:/GT-KB. |

## Acceptance Criteria

- The canonical `.claude/skills/managed-skill-adoption-review/SKILL.md` source exists and is the registry `canonical_source` for `skill.managed-skill-adoption-review`.
- The three regressed skill parity tests pass with `antigravity = "adapter"` assertions (WI-4840 un-regressed).
- WI-4841 managed-skill-adoption-review has a capability registry entry, generated codex + antigravity adapters, entries in both `.codex/skills/MANIFEST.json` and `.agent/skills/MANIFEST.json`, and a focused parity test, all consistent with the antigravity=adapter matrix.
- `generate_codex_skill_adapters.py --check` and `generate_antigravity_skill_adapters.py --check` both PASS; catalog-contract test pass.
- No skill outside the PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT cluster is modified EXCEPT the disclosed 7-sha `source_sha256` normalization inside `.agent/skills/MANIFEST.json` (forced by the antigravity `--check` criterion; no adapter body content changes).

## Cross-Harness Disposition

Per `DELIB-202665926`, antigravity (harness C, active Loyal Opposition) IS a
supported managed-skill adapter target. Claude = native canonical source;
Codex and Antigravity = generated adapters; Cursor/Ollama/OpenRouter remain
`unsupported` (per existing registry enumeration) until separately decided.

## Risks / Rollback

Low. Changes are parity-test-assertion alignment, one new skill canonical source,
its registry entry, its generated adapters, entries in both manifests, and a
focused test, bounded to the skill-activation-enforcement cluster plus the
disclosed antigravity-manifest sha normalization. Rollback is a revert of the
listed target paths; bridge and project-authorization records are append-only.

## Recommended Commit Type

fix - aligns regressed parity tests to the ratified platform reality and completes the WI-4841 scaffold; no new user-facing capability beyond the scaffolded review skill.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
