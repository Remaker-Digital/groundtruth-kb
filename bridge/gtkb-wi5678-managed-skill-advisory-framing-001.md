NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5678-managed-skill-advisory-framing
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5678

target_paths: [".claude/skills/gtkb-advisory-proposal/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", ".codex/skills/gtkb-advisory-proposal/SKILL.md", ".codex/skills/gtkb-bridge/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_advisory_proposal_skill.py"]

# WI-5678 Managed-Skill Governance-Advisory Framing Companion

## Claim

This is the governed companion required by
`gtkb-wi5678-genericize-advisory-role-framing-004.md`. It owns the managed-skill
and generated-projection half of WI-5678; the separate rules-only carrier owns
only `.claude/rules/canonical-terminology.md` and
`.claude/rules/file-bridge-protocol.md`.

No implementation starts through this filing. The current generator checks
report unrelated adapter drift, and `.claude/skills/gtkb-bridge/SKILL.md`
contains foreign WI-5640/WI-5662 worktree hunks. In addition, all three live
adapter generators currently point at the non-authoritative
`gtkb-harness-capability-registry.toml` worktree mirror while
`config/registry/sot-artifacts.toml` names the unprefixed
`harness-capability-registry.toml` as source of truth. This carrier may
implement only after an independent GO, its own claim and packet, reproducible
hunk/output isolation, and a separately governed WI-5663 correction of that
generator-authority split.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667454` establishes that a
governance advisory may be authored by any operating role or explicit owner
direction; the terminal `gtkb-bridge-kind-taxonomy-stabilization-008.md` chain
and `groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py` establish the live
`BridgeKind.GOVERNANCE_ADVISORY` token. This companion changes managed guidance
and projections, not runtime enum behavior.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
- ADR-CROSS-HARNESS-PARITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Prior Deliberations And Governed Dependencies

- `DELIB-202667454` — governance-advisory authorship is role-neutral and
  contrary guidance is obsolete.
- `DELIB-202667470` — WI-5678 is authorized through normal independent gates.
- `bridge/gtkb-bridge-kind-taxonomy-stabilization-008.md` — VERIFIED taxonomy
  chain for `governance_advisory` and legacy-kind migration behavior.
- `gtkb-wi5662-canonical-doc-reference-recovery` — must first leave the dirty
  canonical bridge skill at an attributable committed baseline.
- WI-5663 adapter regeneration — must establish the generated projection
  baseline and correct the systemic registry-authority split in the Codex,
  Antigravity, and API generators before this carrier uses generator output.

## Owner Decisions / Input

No new owner decision is required. This proposal preserves the already
authorized WI-5678 outcome and supplies the missing governed completion owner.

## Exact Canonical Changes

### `.claude/skills/gtkb-advisory-proposal/SKILL.md`

- Make the frontmatter description and trigger text role-neutral: Prime
  Builder, Loyal Opposition, any other operating role, or explicit owner
  direction may originate a governance advisory.
- Replace the LO-only “needs to draft” bullet with role-neutral authorship.
- Preserve owner confirmation, non-approval semantics, later PB disposition,
  independent LO GO, and implementation-start gates.

### `.claude/skills/gtkb-bridge/SKILL.md`

- Replace the retired non-implementation exemption set
  `{spec_intake, governance_review, loyal_opposition_advisory}` with the live
  taxonomy's applicable non-implementation kinds, including
  `governance_advisory`.
- Do not alter Prime/LO verdict authority, queue ownership, helper commands, or
  unrelated path-renaming hunks.

The bridge skill implementation must bind the HEAD blob
`60a86337c93f394a9905a6e890d126d5f2ff74ef`, enumerate only these WI-5678
substitutions, and stage them with a zero-context cached patch. All foreign
`config/agent-control/gtkb-*` and canonical-reference recovery hunks must remain
unstaged and unattributed.

### Managed scaffold source

`groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md` carries the same retired
exemption set and is the registered managed source copied into new scaffolded
projects. It receives the identical taxonomy substitution so future scaffolds
cannot reintroduce the stale guidance. No scaffold-golden root is read,
captured, modified, staged, rebaselined, or committed.

## Projection And Registry Contract

- Canonical source remains the two `.claude/skills/**/SKILL.md` files, with the
  managed bridge template as the scaffold source for future projects.
- Codex adapters must be emitted from the canonical sources through the
  governed generator; `.codex/skills/MANIFEST.json` must carry the matching
  normalized source SHA.
- The authoritative unprefixed capability registry must change the advisory
  capability's canonical purpose and `required_for_roles` from LO-only to both
  Prime Builder and Loyal Opposition, while retaining Claude native and Codex
  adapter declarations and matching source SHA.
- Physically present Antigravity, API-harness, and Goose copies are existing
  parity/control-plane drift, not implied targets. The authoritative WI-5055
  capability row marks Antigravity, Cursor, Ollama, and OpenRouter unsupported;
  that typed disposition is preserved until a separate target-covered proposal
  expands support.

## Cross-Harness Disposition

| Harness | Declared surface | Disposition |
| --- | --- | --- |
| Claude | `.claude/skills/gtkb-advisory-proposal/SKILL.md`, `.claude/skills/gtkb-bridge/SKILL.md` | Behavioral parity authority: canonical native sources are updated in-slice. |
| Codex | two `.codex/skills/**/SKILL.md` adapters and `.codex/skills/MANIFEST.json` | Behavioral parity: generated from the canonical normalized bodies with matching source SHA. |
| Antigravity | no authorized surface in this carrier | Preserve authoritative WI-5055 typed disposition `unsupported`; physically present files are pre-existing drift. |
| Cursor | no registered surface | Preserve authoritative WI-5055 typed disposition `unsupported`. |
| API harness / Ollama / OpenRouter | no authorized surface in this carrier | Preserve authoritative WI-5055 `unsupported` provider dispositions; existing files are not adopted. |
| Goose | no registered capability surface | Not applicable to the authoritative capability row; existing files remain out-of-scope evidence. |

No owner-approved parity waiver is claimed. Every authoritative supported
surface (Claude native and Codex adapter) is in `target_paths`; unsupported
dispositions remain explicit and non-expiring until separately governed.

## Baseline And Isolation Preconditions

Current read-only checks report unrelated drift: Codex would update eight
paths, Antigravity seven, API harness six, and Goose reports manifest drift.
Those results are preconditions, not implementation evidence. The Codex,
Antigravity, and API generators also contain dirty/non-SoT registry-path drift;
this companion does not adopt it. After the WI-5662/WI-5663 baseline settles,
rerun the Codex check from the authoritative unprefixed registry. If outputs
outside the declared eight paths remain, materialize the Codex projection in
an isolated temporary tree and apply only reviewed target-scoped patches;
never run a broad writing generator over the dirty checkout.

## Implementation And Verification Plan

1. Require latest independent GO, an exact thread claim, and a successful
   implementation-start packet for all declared paths.
2. Verify current index preimages. Stop if the canonical bridge preimage or
   dirty-hunk inventory differs from the reviewed proposal.
3. Apply only the canonical role-neutral substitutions, using cached hunk
   isolation for the dirty bridge skill.
4. Generate only the two target-scoped Codex adapters and manifest without
   adopting unrelated output drift. Prove adapter/manifest/SoT-registry SHA
   agreement for both skills.
5. Repair `platform_tests/skills/test_advisory_proposal_skill.py` so it no
   longer false-greens on retired unprefixed paths and instead asserts the live
   gtkb source/adapter, role-neutral language, both required roles, canonical
   purpose, adapter marker, and hash agreement.
6. Run that focused test, the catalog contract, harness parity, and Codex
   generator tests, plus Ruff check/format-check for the modified test. The
   Codex generator check must show zero authorized-target drift; unrelated
   baseline is recorded separately.
7. Prove the cached path set is a subset of the declared eight paths and contains
   no foreign WI-5640/WI-5662 hunk. Commit only that index and file a strict
   implementation report for independent verification.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Role-neutral advisory authorship | Focused canonical/projection text assertions | No managed surface restricts advisory creation to LO; owner/non-approval gates remain. |
| Live taxonomy alignment | `BridgeKind` enum plus bridge-skill exemption assertions | `governance_advisory` is used; retired exemption kinds are absent from current guidance. |
| Managed-skill authority | Canonical source and frontmatter checks | Both `.claude` skills remain valid authoritative sources. |
| Cross-harness parity | Adapter/manifest/SoT-registry normalized SHA assertions and typed disposition checks | Claude and Codex agree; unsupported/non-registered harnesses remain explicit non-targets. |
| Foreign-hunk isolation | Cached/unstaged diff fingerprint checks | WI-5678 bytes only are committed; WI-5640/WI-5662 bytes remain unstaged. |
| Catalog health | Focused test plus `test_skill_catalog_contract.py` | Registered skills are loadable and projections are not orphaned. |

## Acceptance Criteria

- The two canonical skills use role-neutral governance-advisory framing while
  preserving owner confirmation and all implementation/review gates.
- Both declared Codex adapters, their manifest records, and the SoT registry
  agree with canonical normalized SHA and contain no stale role restriction.
- The focused test, catalog contract, generator checks, Ruff, and diff checks
  pass for authorized targets.
- The commit contains only declared, attributable paths and no foreign hunks.
- WI-5678 completion requires this companion and the separate two-rule carrier
  both to reach independent VERIFIED.

## Risks And Rollback

The primary risks are absorbing unrelated adapter/skill-rename drift and
writing the divergent non-SoT registry mirror. Dependency ordering, SoT-path
assertions, temporary projection, exact cached patches, and SHA checks fail
closed. Rollback is a separately governed revert of only this carrier's later
scoped commit.

## Recommended Commit Type

docs
