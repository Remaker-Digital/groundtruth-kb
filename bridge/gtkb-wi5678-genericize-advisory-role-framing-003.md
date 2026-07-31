REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5678-genericize-advisory-role-framing
Version: 003
Responds to: bridge/gtkb-wi5678-genericize-advisory-role-framing-002.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5678
target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/file-bridge-protocol.md"]

implementation_scope: rules-only role-neutral advisory terminology carrier
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5678 — role-neutral governance-advisory rules carrier

## Revision Disposition

Version 002 is correct. Version 001 mixed six declared targets with a
four-surface acceptance contract and left dirty generated-adapter ownership to
the reviewer. This revision selects one executable carrier: the two clean,
tracked canonical rule files above. Its acceptance is intentionally partial
for WI-5678 and does not claim a repository-wide purge.

Managed-skill source and adapter work is explicitly deferred to the separate
companion thread `gtkb-wi5678-managed-skill-advisory-framing`. That companion
must cover `.claude/skills/gtkb-advisory-proposal/SKILL.md`,
`.claude/skills/gtkb-bridge/SKILL.md`, their generated Codex adapters, and any
manifest/registry outputs actually emitted by the governed generator. This
rules carrier neither runs nor writes through the adapter generator.

Both declared targets are currently clean. No source mutation occurs through
this filing. Implementation requires fresh independent GO, this thread's exact
claim, and a successful implementation-start packet.

## Exact Proposed Changes

### `.claude/rules/canonical-terminology.md`

- Rename the `Loyal Opposition advisory` heading to `Governance advisory`.
- Define a governance advisory as an `ADVISORY` bridge entry that any operating
  role may author, or that may be created on explicit owner direction.
- Replace the incorrect `NO-GO` / `loyal_opposition_advisory` filing instruction
  with status `ADVISORY` and `bridge_kind: governance_advisory`.
- Retain `Loyal Opposition advisory` as a historical alias so existing citations
  continue to resolve.
- At the separate `advisory latency` definition, replace “Loyal Opposition
  advisory creation” with role-neutral “governance advisory creation.”
- Preserve “prior Loyal Opposition verdict” where it describes NO-ACTION
  semantics; verdict authority is not advisory authorship.

### `.claude/rules/file-bridge-protocol.md`

- Change the `ADVISORY` status table's `Set by` cell from `Loyal Opposition` to
  `Any operating role / Owner direction`.
- Generalize the Advisory Reports purpose and authority prose so PB, LO, or
  explicit owner direction may originate a governance advisory.
- Preserve existing interactive Prime disposition, headless non-dispatchability,
  and GO/NO-GO/VERIFIED role boundaries unchanged.

## Source Inventory And Exclusions

The exact before-state inventory is:

- `canonical-terminology.md:730-739` — LO-only name, Codex-only author framing,
  wrong `NO-GO` status, and retired `loyal_opposition_advisory` bridge kind.
- `canonical-terminology.md:1194-1200` — advisory-latency definition attributes
  all advisory creation to Loyal Opposition.
- `file-bridge-protocol.md:279` — ADVISORY set-by restricted to Loyal Opposition.
- `file-bridge-protocol.md:358-366` — purpose/authority restricted to owner asking
  LO or LO initiation.

Out of scope:

- No enum, dispatcher, router, checker, hook, source, test, template, or adapter
  mutation.
- No edit to either currently dirty `gtkb-bridge/SKILL.md` surface.
- No broad `python scripts/generate_codex_skill_adapters.py` write: its current
  check reports eight output paths, including foreign WI-5640 migration drift.
- No claim that WI-5678 is complete until the named managed-skill companion is
  independently GO'd, implemented, generated/proven, and VERIFIED.

## Managed-Skill Companion Boundary

The canonical managed-skill sources are `.claude/skills/<slug>/SKILL.md`; the
Codex files are generated adapters. The companion must:

1. name both canonical sources and both adapters plus every manifest/registry
   output the generator would actually change;
2. use `python scripts/generate_codex_skill_adapters.py --check` as parity proof;
3. avoid a writing generator run until the unrelated eight-output baseline is
   clean or an independently approved carrier isolates it;
4. bind the dirty canonical bridge skill's HEAD preimage
   `60a86337c93f394a9905a6e890d126d5f2ff74ef`, enumerate only WI-5678
   substitutions, and prove the cached patch excludes the foreign
   `config/agent-control/gtkb-*` migration hunks while retaining those hunks in
   the worktree.

## In-Root Placement Evidence

Both targets resolve under `E:/GT-KB/.claude/rules/`. The proposal is additive
under `E:/GT-KB/bridge/`. No out-of-root artifact, harness memory, or scratchpad
is an authority or dependency.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded documentation repair.
`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` already defines `governance_advisory`, and
`DELIB-202667454` expressly makes Advisory Proposals role-agnostic. This carrier
does not change executable behavior.

## Specification Links

- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`

## Prior Deliberations And Rejected Approaches

- `DELIB-202667454` — owner decision that Advisory Proposals are role-agnostic
  and contrary direction must be purged.
- `DELIB-202667470` — owner authorization for WI-5678 through the governed
  proposal, review, start, report, and verification lifecycle.
- `DELIB-20263636` — advisory report template authority.
- `DELIB-1500` and `DELIB-20263729` — ADVISORY status/message-type history.
- Version 001's six-target carrier is rejected because its target, placement,
  verification, and acceptance contracts disagreed.
- Broad adapter regeneration is rejected in this carrier because the read-only
  generator check reports eight outputs and would absorb unrelated drift.
- Hand-editing generated Codex adapters is rejected; the companion must follow
  the managed-skill generation lifecycle.

## Owner Decisions / Input

The owner explicitly authorized WI-5678 in `DELIB-202667470`. No additional
owner decision is needed for this corrected rules-only carrier.

## Cross-Harness Disposition

This carrier changes shared canonical rule prose, not harness-specific skill or
runtime behavior. Claude, Codex, and other consumers read the same rule
authority. Managed-skill parity is explicitly pending in the named companion;
no parity waiver is claimed here.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected |
| --- | --- | --- |
| Role-neutral authorship (`DELIB-202667454`) | Exact grep of the two targets for `Loyal Opposition advisory creation`, `Loyal Opposition (or owner-direction) authors`, and the ADVISORY LO-only table cell | no authorship restriction remains |
| Canonical taxonomy (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`) | Inspect the terminology entry for status/kind | `ADVISORY` and `bridge_kind: governance_advisory` |
| Historical citation continuity | Inspect the governance-advisory entry | `Loyal Opposition advisory` retained only as historical alias |
| Protocol non-impairment | Inspect GO/NO-GO/VERIFIED and NO-ACTION sections | verdict roles and NO-ACTION semantics unchanged |
| Canonical rule health | `gt project doctor` and `git diff --check -- .claude/rules/canonical-terminology.md .claude/rules/file-bridge-protocol.md` | pass |
| Scoped patch | `git diff --cached --name-only` and worktree audit | only the two declared targets attributable to this carrier |

## Acceptance Criteria

- The two declared rules use `governance advisory` and
  `bridge_kind: governance_advisory` consistently.
- They permit governance-advisory authorship by any operating role or explicit
  owner direction, while leaving verdict authority unchanged.
- The historical `Loyal Opposition advisory` alias remains.
- The line-1196 advisory-latency wording is role-neutral.
- `gt project doctor`, exact grep checks, and `git diff --check` pass.
- The scoped patch contains only the two declared targets.
- This carrier is recorded as partial WI-5678 progress; terminal WI completion
  remains blocked on the named managed-skill companion.

## Risks / Rollback

Risk is limited to ambiguous prose or accidental weakening of verdict-role
boundaries. Exact substitutions and non-impairment review constrain that risk.
Rollback is a governed two-path revert. The companion remains independently
reviewable and cannot inherit authority from this carrier.

## Recommended Commit Type

`docs`
