REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner AUQ waiver captured in Plan Mode and persisted to DA

# REVISED Implementation Proposal - WI-5492 generated skill projections with hunk-scoped isolation

bridge_kind: prime_proposal
Document: gtkb-retire-ipa-refs-skill-projections
Version: 003
Date: 2026-07-18 UTC
Responds to: bridge/gtkb-retire-ipa-refs-skill-projections-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5492

target_paths: [".codex/skills/MANIFEST.json", ".codex/skills/codex-report/SKILL.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".agent/skills/MANIFEST.json", ".agent/skills/codex-report/SKILL.md", ".agent/skills/kb-session-wrap/SKILL.md", ".agent/skills/lo-opportunity-radar/SKILL.md", ".agent/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".goose/skills/codex-report/SKILL.md", ".goose/skills/kb-session-wrap/SKILL.md", ".goose/skills/lo-opportunity-radar/SKILL.md", ".goose/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".cursor/skills/codex-report/SKILL.md", ".cursor/skills/kb-session-wrap/SKILL.md", ".cursor/skills/lo-opportunity-radar/SKILL.md", ".cursor/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".api-harness/skills/MANIFEST.json", ".api-harness/skills/codex-report/SKILL.md", ".api-harness/skills/kb-session-wrap/SKILL.md", ".api-harness/skills/lo-opportunity-radar/SKILL.md", ".api-harness/skills/loyal-opposition-hygiene-assessment/SKILL.md", "config/agent-control/harness-capability-registry.toml", "groundtruth.db", "bridge/hunks/gtkb-retire-ipa-refs-skill-projections-wi5492-projection-only.patch", "bridge/hunks/gtkb-retire-ipa-refs-skill-projections-groundtruth-db-waiver.patch"]

implementation_scope: skill_docs
requires_review: true
requires_verification: true
kb_mutation_in_scope: deliberation_archive_evidence_only

## Revision Claim

This revision responds to the live NO-GO at `bridge/gtkb-retire-ipa-refs-skill-projections-002.md` by replacing the earlier deferred isolation language with an owner-authorized hunk/object-scoped isolation method and binding verification conditions.

The current tree has changed since the NO-GO was filed: `gtkb-wi5156-governed-project-dependency-ordering-cli` is now independently `VERIFIED`, but unrelated generated-skill projection residue remains in the same shared manifests and registry. This revision therefore does not ask Loyal Opposition to approve whole-file finalization. It asks for GO on a tightly isolated implementation path that may stage and finalize only the four WI-5492 retired-IPA projection families and must exclude all unrelated generated projection hunks.

## Requirement Sufficiency

Existing requirements remain sufficient, with the new owner waiver recorded in the Deliberation Archive. `WI-5492` and the active obsolete-reference-purge PAUTH authorize correcting live/load-bearing retired-IPA references and preserving generated skill parity. `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER` authorizes the specific hunk/object-scoped isolation method needed for this shared generated-projection surface.

No dispatcher configuration, routing policy, credential lifecycle, deployment, release, historical bridge rewrite, or unrelated generated projection finalization is authorized by this revision.

## Owner Decisions / Input

- `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER` - owner selected `Authorize isolation (Recommended)` for AUQ `wi5492_projection_hunk_waiver`; authorizes hunk/object-scoped isolation for this companion lane.
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - owner-directed retirement/deletion of the former IPA report directory and correction of live references.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - owner decision behind the active obsolete-reference-purge PAUTH.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-5492`, skill documentation, generated projections, configuration, and governance evidence within bridge gates.

## Prior Deliberations

- `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER` - owner-authorized hunk/object-scoped isolation for this exact projection companion.
- `DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER` and related WI-4841 hunk-scoped finalization history - precedent for owner-waived object-level isolation in shared generated manifests.
- `DELIB-202665986` - prior WI-4841 hunk-scoped finalization deliberation cited by the NO-GO.
- `bridge/gtkb-retire-ipa-refs-skill-projections-001.md` - original companion proposal.
- `bridge/gtkb-retire-ipa-refs-skill-projections-002.md` - NO-GO requiring sequencing or concrete hunk/object isolation.
- `bridge/gtkb-retire-ipa-refs-rules-skills-012.md` - independent `VERIFIED` finalization of the canonical rule/skill source lane that this companion projects.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-011.md` - now-`VERIFIED` predecessor that clears the active `projects` conflict cited in `-002`, while not clearing unrelated generated projection residue.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Proposed Change

After independent GO and implementation-start authorization, Prime Builder may create a candidate index from current `HEAD` and apply only the WI-5492-owned generated projection hunks for these four skill families:

- `codex-report`
- `kb-session-wrap`
- `lo-opportunity-radar`
- `loyal-opposition-hygiene-assessment`

The implementation must produce durable bridge hunk evidence for review:

- `bridge/hunks/gtkb-retire-ipa-refs-skill-projections-wi5492-projection-only.patch` - applies the approved projection-only hunks against `HEAD`.
- `bridge/hunks/gtkb-retire-ipa-refs-skill-projections-groundtruth-db-waiver.patch` - if live `groundtruth.db` remains mixed, carries only `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER` into the candidate DB.

The implementation report must cite only canonical bridge hunk evidence, bridge files, the DA ID, and command output. Temporary/disposable working paths may be used for local mechanics but must not appear as canonical evidence.

## Required Isolation Method

The candidate/staged state for this thread must satisfy all conditions below before the implementation report is filed:

1. The staged name-only set is limited to this proposal's declared target paths and the new `REVISED`/implementation-report bridge files.
2. Shared manifest diffs contain only the four approved WI-5492 skill-family entries. They must not contain `gtkb-hygiene-reclaim`, `managed-skill-adoption-review`, `projects`, or other sibling skill objects.
3. `config/agent-control/harness-capability-registry.toml` contains only the eight WI-5492 `source_sha256` updates for Codex and Antigravity entries for the four approved skill families.
4. Adapter body diffs are limited to the four approved skill families across Codex, Antigravity, API harness, Cursor, and Goose projection surfaces.
5. The `groundtruth.db` candidate, if included, differs from `HEAD:groundtruth.db` only by the new DA waiver row and passes `PRAGMA integrity_check`.
6. Dispatcher routing/configuration files are absent from the staged name-only set.
7. Untracked generated directories not owned by WI-5492 remain uncommitted and uncited by this thread.

## Explicit Exclusions

This revision excludes and forbids finalizing:

- `gtkb-hygiene-reclaim`
- `managed-skill-adoption-review`
- `projects`
- `.codex/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/verify/helpers/write_bridge_5171.py`
- dispatcher routing/configuration
- any untracked generated directories not owned by WI-5492
- any whole-file generator normalization outside the four approved skill families

## Cross-Harness Disposition

| Harness / surface | Disposition |
| --- | --- |
| Claude canonical skills | Already completed and independently `VERIFIED` in `bridge/gtkb-retire-ipa-refs-rules-skills-012.md`; this companion does not add or change `.claude/skills/**`. |
| Codex | In scope only for the four approved generated adapters and their four manifest source-hash entries. Existing out-of-scope Codex helper drift is excluded and may not be finalized here. |
| Antigravity | In scope only for the four approved generated adapters and their four manifest source-hash entries. Untracked `gtkb-hygiene-reclaim` residue is excluded. |
| API harness | In scope only for the four approved generated adapters and their four manifest source-hash entries. Untracked `gtkb-hygiene-reclaim` and `managed-skill-adoption-review` residue is excluded. |
| Cursor | In scope only for the four approved generated adapters; no manifest or registry authority is requested for Cursor in this companion. |
| Goose | In scope only for the four approved generated adapters; no manifest or registry authority is requested for Goose in this companion. |
| Registry | In scope only for the eight Codex/Antigravity `source_sha256` updates for the four approved WI-5492 skill families. |
| Dispatcher / routing | Out of scope; no dispatcher configuration or routing-policy file may be touched. |

## Specification-Derived Verification Plan

| Spec or Decision | Verification |
| --- | --- |
| `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify the DA row exists, is linked to `WI-5492`, has `outcome=owner_decision`, and is carried by the isolated DB hunk patch if `groundtruth.db` is included. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`; `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Search approved projection targets for retired durable-home references; remaining mentions must describe retirement/redirection and must not instruct use of the retired directory or legacy insight-dropbox surface. |
| `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Verify the four approved skill families are projected across Codex, Antigravity, API harness, Cursor, and Goose. Antigravity/API full generator checks must pass; Codex full check may be non-blocking only for pre-existing, out-of-scope helper drift with an exact list. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability and clause preflights before filing proposal/report; implementation begins only after independent GO and implementation-start packet. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this mapping forward with executed commands and observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed path set and hunk patch paths are all inside `E:\GT-KB`; `git diff --check` passes for included paths. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner waiver evidence is AUQ-backed and persisted as `DELIB-20260718-WI5492-SKILL-PROJECTION-HUNK-ISOLATION-WAIVER`. |

Expected implementation/report commands:

```text
gt bridge show gtkb-retire-ipa-refs-skill-projections --json --compact
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-retire-ipa-refs-skill-projections
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_antigravity_skill_adapters.py --check
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_api_skill_adapters.py --check
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check
git diff --cached --name-only
git diff --cached --check
git diff --check -- <approved projection target paths and bridge hunk paths>
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-retire-ipa-refs-skill-projections --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-retire-ipa-refs-skill-projections
```

## Acceptance Criteria

- Loyal Opposition can verify that the owner-authorized isolation method is concrete and bounded before implementation begins.
- The four WI-5492 canonical skill updates are reflected in the approved generated projection surfaces.
- Shared manifests contain only WI-5492-owned entry/hash updates for the four approved skill families.
- The registry contains only the eight WI-5492 Codex/Antigravity source-hash updates.
- The DA waiver row is durably represented without sweeping unrelated `groundtruth.db` changes.
- No dispatcher configuration or routing policy file is changed.
- `gtkb-retire-ipa-refs-skill-projections` reaches independent `VERIFIED` before it is used to clear the Slice D registry pre-start gate.

## Response To NO-GO-002

Finding P1 is accepted. This revision resolves it by adding the missing concrete isolation method, owner waiver evidence, durable bridge hunk evidence path, and binding verification conditions. Prime Builder is not asking Loyal Opposition to approve whole-file shared-manifest authority. If any generator output remains broader than the approved four skill families, the implementation must fail closed or file another revision.

## Risk And Rollback

Risk remains medium because shared generated manifests and the registry still contain unrelated residue. Rollback is by applying the inverse of the approved hunk patch or by excluding the candidate state before finalization. Bridge files remain append-only. Any unrelated generated projection gap must proceed in its own governed bridge lane, not through this WI-5492 companion.

## Pre-Filing Preflight Evidence

- Applicability preflight on the completed candidate content: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- Mandatory clause preflight on the completed candidate content: clauses evaluated `5`; `must_apply: 4`; evidence gaps in must-apply clauses `0`; blocking gaps `0`; exit `0`.
- Projection-current checks before filing: Antigravity skill adapters `PASS (44 adapters current)`; API skill adapters `PASS (44 adapters current)`.

## Recommended Commit Type

`fix`
