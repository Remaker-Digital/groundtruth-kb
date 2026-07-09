REVISED

# Implementation Proposal (REVISED) - Antigravity Supported Skill-Target Parity Alignment (+ WI-4841 completion)

bridge_kind: prime_proposal
Document: gtkb-antigravity-supported-skill-target-parity-alignment
Version: 003
Date: 2026-07-09 UTC
Responds to: bridge/gtkb-antigravity-supported-skill-target-parity-alignment-002.md

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: ["platform_tests/skills/test_advisory_disposition_skill.py", "platform_tests/skills/test_skill_governance_lifecycle_skill.py", "platform_tests/skills/test_formal_artifact_packet_helper_skill.py", "platform_tests/skills/test_managed_skill_adoption_review_skill.py", "config/agent-control/harness-capability-registry.toml", ".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json"]

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

## Revision History (why -003 supersedes -001/-002)

The `-001` NEW proposal (GO at `-002`) asserted in its Problem / Context that the
managed-skill-adoption-review `.claude` canonical source "already exist[s]" and
scoped only the generated adapters, the registry, the manifest, and the tests
(the `.claude` source was NOT in `target_paths`). Canonical-state verification for
this session found that premise false:

- `.claude/skills/managed-skill-adoption-review/SKILL.md` does NOT exist on disk
  and has no git history (checked `Test-Path`, recursive `.claude/skills` search,
  and `git log --all`).
- The only surviving artifact of the skill is an UNTRACKED
  `.codex/skills/managed-skill-adoption-review/SKILL.md` full skill body (no
  adapter marker, no git history) - authored under the prior scaffold thread's
  `.codex` write-boundary block, never accompanied by a canonical source.
- No `skill.managed-skill-adoption-review` entry exists in the capability
  registry.

Both harness adapter generators project FROM a capability's `canonical_source`
file (they read and sha256 the source; they never manufacture it). With no
`.claude` canonical source, the generators cannot produce the codex/antigravity
adapters, so WI-4841 registration is unreachable under the `-002` GO's
`target_paths` (which omit the `.claude` source). This REVISED corrects the
premise and adds `.claude/skills/managed-skill-adoption-review/SKILL.md` to
`target_paths`. The `.claude` source will be created by faithfully
reconstructing the existing untracked `.codex` adapter body (frontmatter +
review checklist), which is the intended canonical content.

The three parity-test alignments and the antigravity=adapter cross-harness
matrix are unchanged from `-001`.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202665926` (this session's predecessor
owner AUQ) ratifies antigravity support and is the typed parity waiver the
WI-4839..4842 proposals contemplated ("no direct skill adapter target ...
requires a separate target-path-covered proposal or typed parity waiver"). No
new requirement capture is needed; this change aligns tests and registry to the
ratified platform behavior and completes the WI-4841 scaffold by projecting an
already-authored skill body into its canonical location.

## Problem / Context

The Codex-style adapter generator projects managed skills to antigravity
(`.agent/skills/*` adapters plus registry `[capabilities.antigravity] status =
"adapter"`), reflecting antigravity (harness C) now being an active dispatchable
Loyal Opposition harness. Three skill parity tests still assert
`antigravity["status"] == "unsupported"`, from pre-antigravity-harness proposal
language, and now FAIL against the current registry:

- `test_advisory_disposition_skill.py` (line 159) - regressing the previously VERIFIED WI-4840.
- `test_skill_governance_lifecycle_skill.py` (line 147).
- `test_formal_artifact_packet_helper_skill.py` (its 4-harness assertion loop, line 172).

WI-4841 (managed-skill-adoption-review) lacks a capability registry entry and a
focused parity test. Contrary to the `-001` premise, it ALSO lacks a canonical
`.claude` source; only an untracked `.codex` adapter body exists (see Revision
History). The canonical source must be created before the generators can project
its adapters.

## Proposed Scope

1. Create the canonical source `.claude/skills/managed-skill-adoption-review/SKILL.md`
   by faithfully reconstructing the existing untracked
   `.codex/skills/managed-skill-adoption-review/SKILL.md` body (frontmatter
   name/description + When To Use / When Not To Use / Required Context /
   Structural Review Checklist / Output / Artifact Routing / Adopted From
   sections). This is the canonical content the `.codex` adapter was projected
   from before the canonical source was lost.
2. Add the `skill.managed-skill-adoption-review` capability registry entry
   (`kind="skill"`, `canonical_source=".claude/skills/managed-skill-adoption-review/SKILL.md"`,
   `required_for_roles`, `parity_class="baseline"`), plus a base
   `[capabilities.claude] status="native"` block and a `[capabilities.cursor]
   status="unsupported"` block with a reason - modeled on the
   `skill.advisory-disposition` block. The codex + antigravity blocks are filled
   by the generators.
3. Run BOTH adapter generators with `--update-registry` so they read the new
   canonical source and produce the codex adapter, the antigravity adapter, the
   codex/antigravity registry blocks, and the `.codex/skills/MANIFEST.json`
   entry: `scripts/generate_codex_skill_adapters.py --update-registry` then
   `scripts/generate_antigravity_skill_adapters.py --update-registry`. Confirm
   the generators touch ONLY the managed-skill-adoption-review adapters, the
   registry, and the manifest (the other 42 skills are current; both `--check`
   PASS). Yielded matrix: claude=native, codex=adapter, antigravity=adapter,
   cursor=unsupported.
4. Align the antigravity parity assertions in the three named tests to
   `antigravity = "adapter"`, consistent with the actual registry matrix and
   `DELIB-202665926`. In `test_formal_artifact_packet_helper_skill.py`, rewrite
   the 4-harness assertion loop so antigravity asserts `adapter`, cursor asserts
   `unsupported`, and ollama/openrouter are dropped (they are not enumerated in
   these skills' registry blocks and `DELIB-202665926` is antigravity-scoped).
5. Add `platform_tests/skills/test_managed_skill_adoption_review_skill.py`
   modeled on `test_formal_artifact_packet_helper_skill.py`, asserting the
   generator-produced matrix (claude=native, codex=adapter, antigravity=adapter,
   cursor=unsupported) plus adapter existence, manifest entry, canonical-source
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

- `DELIB-202665926` (owner AUQ, 2026-07-09): antigravity is a supported managed-skill projection target; align stale `antigravity = "unsupported"` tests to `antigravity = "adapter"`; serves as the typed parity waiver for WI-4839..4842.
- Owner AUQ, this session (2026-07-09, session `ac6ded12-902d-4b58-b9f2-b31dedb5d5b8`): after canonical-state verification found the `-001` "`.claude` source already exists" premise false, the owner selected "One REVISED -003, full scope" - correct the premise and add the `.claude` canonical source to `target_paths` while retaining the full scope (register skill + align three parity tests + new test), rather than splitting the thread or registering from the `.codex` source.
- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842`: active project authorization (no expiry) covering WI-4839, WI-4840, WI-4841, WI-4842 with mutation classes source + test.

## Prior Deliberations

- `DELIB-202665926` - owner ratification; the authority for this proposal.
- `DELIB-20266596` - owner AUQ approval for bounded WI-4839..4842 skill-scaffold implementation.
- `DELIB-20265883` - owner-directed creation of PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT.
- `bridge/gtkb-antigravity-supported-skill-target-parity-alignment-002.md` - the LO GO (antigravity, harness C) on the `-001` premise; this REVISED corrects the false `.claude`-source-exists premise it inherited.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-014.md` - prior NO-GO (blocked on the Codex `.codex` write boundary, since resolved); the source of the untracked `.codex` adapter body reconstructed here. This umbrella supersedes that thread's remaining WI-4841 scope; the scaffold thread is to be WITHDRAWN after this thread VERIFIES.
- `bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-021.md` - prior NO-GO; its stale antigravity test assertion is aligned here.
- `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-010.md` - VERIFIED WI-4840 whose parity test is currently regressed by the antigravity registry state and is un-regressed here.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run pytest over the four skill tests (test_advisory_disposition_skill.py, test_skill_governance_lifecycle_skill.py, test_formal_artifact_packet_helper_skill.py, test_managed_skill_adoption_review_skill.py) via the project venv python -> all pass (un-regresses WI-4840). |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run scripts/generate_codex_skill_adapters.py --check and scripts/generate_antigravity_skill_adapters.py --check -> both PASS (now 43 current); registry matrix consistent with DELIB-202665926. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run pytest over platform_tests/skills/test_skill_catalog_contract.py -> pass. |
| Code quality | ruff check plus ruff format --check on the four changed/added test files (both gates). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability + clause preflights pass (missing_required_specs empty; 0 blocking gaps). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under E:/GT-KB. |

## Acceptance Criteria

- The canonical `.claude/skills/managed-skill-adoption-review/SKILL.md` source exists and is the registry's `canonical_source` for `skill.managed-skill-adoption-review`.
- The three regressed skill parity tests pass with `antigravity = "adapter"` assertions (WI-4840 un-regressed).
- WI-4841 managed-skill-adoption-review has a capability registry entry, generated codex + antigravity adapters, a manifest entry, and a focused parity test, all consistent with the antigravity=adapter matrix.
- `generate_codex_skill_adapters.py --check` and `generate_antigravity_skill_adapters.py --check` both PASS; catalog-contract test pass.
- No skill outside the PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT cluster is modified.

## Cross-Harness Disposition

Per `DELIB-202665926`, antigravity (harness C, active Loyal Opposition) IS a
supported managed-skill adapter target. Claude = native canonical source;
Codex and Antigravity = generated adapters; Cursor/Ollama/OpenRouter remain
`unsupported` (per existing registry enumeration) until separately decided.

## Risks / Rollback

Low. Changes are parity-test-assertion alignment plus one new skill canonical
source, its registry entry, its generated adapters/manifest entry, and a focused
test, bounded to the skill-activation-enforcement cluster. Rollback is a revert
of the four test files, the new `.claude` source, the registry entry, and the
managed-skill-adoption-review generated adapters/manifest entry; bridge and
project-authorization records are append-only.

## Recommended Commit Type

fix - aligns regressed parity tests to the ratified platform reality and completes the WI-4841 scaffold; no new user-facing capability beyond the scaffolded review skill.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
