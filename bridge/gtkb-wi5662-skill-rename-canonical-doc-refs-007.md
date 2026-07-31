REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T16-33-25Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default;thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5662 Canonical Skill Documentation Reference Repair - Complete Inventory

bridge_kind: prime_proposal
Document: gtkb-wi5662-skill-rename-canonical-doc-refs
Version: 007
Responds to: bridge/gtkb-wi5662-skill-rename-canonical-doc-refs-006.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662
target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]
implementation_scope: documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Re-propose the canonical skill-documentation repair after v006. The source inventory is rebuilt from the GO-bound HEAD preimage, explicitly includes the `.claude/skills/send-review/SKILL.md` to `.claude/skills/gtkb-send-review/SKILL.md` replacement, and remains isolated from unrelated WI-5640 file-move hunks in `.claude/skills/gtkb-bridge/SKILL.md`.

No generated Codex/other-harness adapter is edited here; WI-5663 remains sequenced after a committed, independently reviewed canonical S1 implementation.

## Requirement Sufficiency

Existing requirements sufficient. WI-5662, `DELIB-202667193`, `DELIB-202667194`, the v006 findings, and the canonical map at `config/agent-control/gtkb-skill-rename-map.toml` define this isolated documentation slice. No additional owner decision is required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667193` - owner authorization and S1-to-S2 sequencing for the skill-rename sweep.
- `DELIB-202667194` - governed existing-work handling, skill-rename-only isolation, and WI-5640 exclusion.
- `bridge/gtkb-wi5662-skill-rename-canonical-doc-refs-006.md` - P1 complete-inventory and committed-evidence findings addressed here.

## Owner Decisions / Input

- `DELIB-202667193` authorizes the bounded sweep slice subject to per-slice GO and VERIFIED.
- `DELIB-202667194` requires exact skill-rename hunk isolation and excludes WI-5640 file-move apply output from this commit.

## Reference Inventory And Isolation Boundary

The approved patch must be generated against the bound HEAD preimage of `.claude/skills/gtkb-bridge/SKILL.md` (`60a86337c93f394a9905a6e890d126d5f2ff74ef` in v003) and must contain only these old-to-new documentation references:

| File | Old reference | New reference | Occurrence set |
| --- | --- | --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/helpers/scan_bridge.py` | `.claude/skills/gtkb-bridge/helpers/scan_bridge.py` | all scan-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/helpers/revise_bridge.py` | `.claude/skills/gtkb-bridge/helpers/revise_bridge.py` | all revise-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/verify/helpers/write_verdict.py` | `.claude/skills/gtkb-verify/helpers/write_verdict.py` | all verdict-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/helpers/impl_report_bridge.py` | `.claude/skills/gtkb-bridge/helpers/impl_report_bridge.py` | all implementation-report-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/helpers/protected_write.py` | `.claude/skills/gtkb-bridge/helpers/protected_write.py` | all protected-write-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/helpers/show_thread_bridge.py` | `.claude/skills/gtkb-bridge/helpers/show_thread_bridge.py` | all show-thread-helper occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/proposal-review/SKILL.md` | `.claude/skills/gtkb-proposal-review/SKILL.md` | all proposal-review occurrences |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/send-review/SKILL.md` | `.claude/skills/gtkb-send-review/SKILL.md` | mandatory formerly missed occurrence |
| `.claude/skills/gtkb-bridge/SKILL.md` | `.claude/skills/bridge/SKILL.md` and `.codex/skills/bridge/SKILL.md` | matching `gtkb-bridge` paths | all skill-root occurrences |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `.claude/skills/verify/helpers/write_verdict.py` | `.claude/skills/gtkb-verify/helpers/write_verdict.py` | all occurrences |
| `.claude/skills/gtkb-verify/SKILL.md` | `.claude/skills/verify/helpers/write_verdict.py`, `.claude/skills/verify/SKILL.md`, `.codex/skills/verify/SKILL.md` | matching `gtkb-verify` paths | all occurrences |

`config/agent-control/gtkb-*` references in the mixed `gtkb-bridge/SKILL.md` worktree are read-only WI-5640 evidence. They are not target replacements, must not be staged, and must remain outside the eventual commit. If the exact bound preimage cannot be reconstructed without absorbing a foreign hunk, implementation fails closed and a provenance reconciliation is required first.

## Findings Addressed

### P1 - No committed implementation evidence

Response: no implementation occurs under this REVISED proposal. A later GO attempt must stage only the reviewed patch, commit exactly the three declared documents, and file a new implementation report with commit SHA, cached path list, executed residual scan, and WI-5640 exclusion assertions.

### P1 - Incomplete reference inventory

Response: the inventory explicitly names `send-review` and requires every occurrence of each listed bare skill-dir pattern to be counted before and after the commit. Zero residual applies only to the three declared canonical document paths, not to broad repository text or WI-5640 historical/migration content.

## Specification-Derived Verification Plan

| Spec / property | Verification | Expected result |
| --- | --- | --- |
| Canonical documentation completeness | Per-target anchored residual scan over the listed old paths, including `send-review`, before and after staged patch. | Preimage count equals reviewed inventory; staged and committed residual count is zero. |
| WI-5640 isolation | `git diff --cached -- .claude/skills/gtkb-bridge/SKILL.md` and `git show <commit> -- .claude/skills/gtkb-bridge/SKILL.md` inspect `config/agent-control/gtkb-`. | No WI-5640 file-move hunk enters cache or commit; foreign worktree hunk remains unstaged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh claim, implementation authorization, exact cached path list, and commit SHA. | All protected-file gates precede commit. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` | No missing required specification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` plus report evidence. | Clause gate passes and later report is independently reproducible. |

## Acceptance Criteria

- The later commit contains only the three declared canonical `SKILL.md` paths and every listed bare skill reference, including `send-review`, is canonicalized.
- No `config/agent-control/gtkb-*` WI-5640 hunk is cached, committed, reformatted, or attributed by this slice.
- The implementation report carries immutable commit evidence, per-target residual scan result, and the two WI-5640 isolation assertions before LO review.
- No generated adapter is altered until WI-5662 is independently terminal and WI-5663 receives its own authorization.

## Cross-Harness Disposition

- **Claude Code:** this slice corrects the three canonical `.claude/skills/**` source documents.
- **Codex, Goose, Agent, API harness, and other generated adapters:** no generated projection is modified here. Their observable skill-documentation parity is restored only through the separately sequenced WI-5663 adapter-regeneration slice after WI-5662 has committed and been independently verified.
- **No waiver:** the temporary projection lag is the owner-approved S1-to-S2 sequence in `DELIB-202667193`; it is not a claim that generated adapters are current before WI-5663.

## Risks And Rollback

Risk: broad current-worktree search can blend this repair with WI-5640. Execution is limited to a bound-preimage patch and exact staged paths. Rollback is a governed revert of only the later three-file commit; it never restores or removes foreign WI-5640 worktree hunks.

## Files Expected To Change

- `.claude/skills/gtkb-bridge/SKILL.md`
- `.claude/skills/gtkb-proposal-review/SKILL.md`
- `.claude/skills/gtkb-verify/SKILL.md`

## Recommended Commit Type

`docs`
