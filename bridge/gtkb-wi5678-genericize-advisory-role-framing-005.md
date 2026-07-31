REVISED
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
Document: gtkb-wi5678-genericize-advisory-role-framing
Version: 005
Responds to: bridge/gtkb-wi5678-genericize-advisory-role-framing-004.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5678

target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/file-bridge-protocol.md"]

# WI-5678 Role-Neutral Governance-Advisory Rules Carrier

## Revision Claim

This revision resolves all three v004 findings while preserving the clean,
two-rule scope accepted as the correct carrier boundary. It replaces the
unresolvable taxonomy citation with a verified bridge chain plus live source,
adds executed enum/gate/legacy-migration evidence, and links the now-filed
managed-skill companion. It makes no source, hook, enum, test, template,
adapter, registry, or generated-file mutation.

Both targets are currently clean. Implementation still requires a fresh
independent GO, exact claim, and successful implementation-start packet.

## Findings Addressed

### P1 — Taxonomy authority was not concrete or resolvable

The absent `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` citation is removed. The durable
authority used by this documentation reconciliation is now:

- `bridge/gtkb-bridge-kind-taxonomy-stabilization-008.md`, the terminal VERIFIED
  eight-version taxonomy implementation chain; and
- `groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py:7-13`, where
  `BridgeKind.GOVERNANCE_ADVISORY = "governance_advisory"` is live.

These are concrete and directly inspectable. This proposal does not pretend
the verified bridge chain is a MemBase DCL.

### P1 — Verification covered prose but not enforcement

The verification plan now executes the live enum, the legacy migration
mapping, and the compliance-gate exemption for `governance_advisory`. The exact
focused command was executed against the current worktree and produced
4 passed, 1 pre-existing `asyncio_mode` warning:

`python -m pytest platform_tests/scripts/test_bridge_kind_taxonomy.py::test_bridge_kind_enum_values platform_tests/scripts/test_bridge_kind_taxonomy.py::test_map_bridge_kind platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py::test_bridge_kind_governance_advisory_no_metadata_passes -q --tb=short`

Compatibility is stated precisely: `loyal_opposition_advisory` is accepted as a
legacy migration input and maps to `governance_advisory`; it is not a valid
token for new entries. New-entry gate acceptance is proven only for the live
`governance_advisory` token.

### P2 — Managed-skill companion did not exist

`bridge/gtkb-wi5678-managed-skill-advisory-framing-001.md` is now a governed
NEW companion with explicit target paths, SoT registry handling, scaffold
source, Codex adapter/manifest coverage, focused false-green test repair,
cross-harness dispositions, dependency ordering, and completion criteria.
WI-5678 cannot be declared complete until both carriers independently reach
VERIFIED.

## Exact Proposed Changes

### `.claude/rules/canonical-terminology.md`

- Rename the `Loyal Opposition advisory` heading to `Governance advisory`.
- Define a governance advisory as an `ADVISORY` bridge entry that any operating
  role may author or that may be created on explicit owner direction.
- Replace the wrong `NO-GO` / `loyal_opposition_advisory` filing instruction
  with status `ADVISORY` and `bridge_kind: governance_advisory`.
- Retain `Loyal Opposition advisory` only as a historical alias so existing
  citations continue to resolve.
- Change “Loyal Opposition advisory creation” in the advisory-latency glossary
  entry to role-neutral “governance advisory creation.”
- Preserve “prior Loyal Opposition verdict” where it accurately describes
  NO-ACTION semantics; verdict authority is not advisory authorship.

### `.claude/rules/file-bridge-protocol.md`

- Change the `ADVISORY` status table's `Set by` cell from Loyal Opposition to
  `Any operating role / Owner direction`.
- Generalize Advisory Reports purpose and authority prose so Prime Builder,
  Loyal Opposition, another operating role, or explicit owner direction may
  originate a governance advisory.
- Preserve interactive Prime disposition, headless non-dispatchability, and
  GO/NO-GO/VERIFIED authority unchanged.

## Source Inventory And Exclusions

The bounded before-state inventory remains:

- `canonical-terminology.md:730-739` — LO-only name/author framing, wrong
  `NO-GO` status, and retired bridge kind.
- `canonical-terminology.md:1194-1200` — advisory latency attributes creation
  only to Loyal Opposition.
- `file-bridge-protocol.md:279` — ADVISORY set-by restricted to LO.
- `file-bridge-protocol.md:358-366` — purpose/authority restricted to LO.

No enum, dispatcher, router, checker, hook, source, test, template, skill,
adapter, manifest, registry, or migration-policy mutation is in scope. No
writing generator is run. Both scaffold-golden roots remain quarantined and
are never read, modified, captured, staged, or committed.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667454` expressly makes
governance-advisory authorship role-neutral. The verified taxonomy chain and
live `BridgeKind` source prove the current token and enforcement. This carrier
only reconciles two canonical rule documents to those durable facts.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
- ADR-CROSS-HARNESS-PARITY-001

## Prior Deliberations And Governed Evidence

- `DELIB-202667454` — owner decision that Advisory Proposals are role-agnostic
  and contrary guidance must be removed.
- `DELIB-202667470` — owner authorization for WI-5678 through normal proposal,
  review, implementation-start, report, and verification gates.
- `DELIB-20263636` — advisory report template authority.
- `DELIB-1500` and `DELIB-20263729` — ADVISORY status/message-type history.
- `bridge/gtkb-bridge-kind-taxonomy-stabilization-008.md` — terminal VERIFIED
  taxonomy chain.
- `bridge/gtkb-wi5678-managed-skill-advisory-framing-001.md` — governed owner
  of the remaining managed-skill/projection completion work.

## Owner Decisions / Input

No new owner decision is required. The owner already authorized the exact
role-neutral outcome in `DELIB-202667454` and WI-5678 implementation in
`DELIB-202667470`.

## Cross-Harness Disposition

These two rule files are shared canonical rule authority rather than
harness-specific adapters. Claude, Codex, and other rule consumers receive the
same text. Managed-skill and adapter parity is not waived or implied here; it
is owned by the separately governed companion.

## Pre-Filing Preflight Subsection

The completed candidate must pass both bridge applicability and mandatory
ADR/DCL clause preflights before filing. Any missing blocking specification,
target classification, or clause evidence stops the revision.

## Implementation And Verification Plan

1. After fresh GO, acquire the exact claim and require a successful
   implementation-start packet for only the two rule files.
2. Apply only the inventory substitutions above and prove the cached set equals
   the two declared targets.
3. Run exact residual scans for LO-only advisory-authorship wording and the
   retired new-entry kind; verify the historical alias remains exactly once.
4. Re-run the three exact taxonomy/gate node IDs above. Expect all selected
   tests to pass; the legacy token is migration-only, while
   `governance_advisory` is accepted by the live gate.
5. Run `gt project doctor` and scoped `git diff --check`; inspect the unchanged
   GO/NO-GO/VERIFIED and NO-ACTION sections for verdict-role non-impairment.
6. Commit only the authorized two-file index, file a strict implementation
   report with commit-finalization evidence, and request independent review.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Role-neutral authorship (`DELIB-202667454`) | Exact residual scan of both targets | No LO-only advisory-author restriction remains. |
| Live taxonomy | `test_bridge_kind_enum_values` plus live source inspection | `BridgeKind.GOVERNANCE_ADVISORY` equals `governance_advisory`. |
| New-entry gate | `test_bridge_kind_governance_advisory_no_metadata_passes` | Live compliance gate accepts the current non-implementation kind. |
| Legacy compatibility | `test_map_bridge_kind` | Retired `loyal_opposition_advisory` maps only as migration input to `governance_advisory`. |
| Historical continuity | Alias scan in canonical terminology | Prior term remains only as historical alias. |
| Verdict-role non-impairment | Unchanged protocol-section inspection | GO/NO-GO/VERIFIED and NO-ACTION authority remain unchanged. |
| Canonical rule health | `gt project doctor` and scoped diff check | Pass without out-of-scope mutation. |
| Completion ownership | Direct companion thread inspection | Remaining managed-skill/projection work has a governed explicit contract. |

## Acceptance Criteria

- Both rules use `governance advisory` and
  `bridge_kind: governance_advisory` consistently for current entries.
- Any operating role or explicit owner direction may originate an advisory,
  while verdict authority remains unchanged.
- `Loyal Opposition advisory` remains only as historical terminology; the raw
  legacy bridge kind is described only as migration compatibility.
- Exact taxonomy/gate tests, doctor, residual scans, and diff checks pass.
- The commit contains only the two declared rule paths.
- This carrier records partial WI-5678 progress; WI completion requires the
  managed-skill companion to reach independent VERIFIED too.

## Risks And Rollback

The risk is ambiguous prose or accidental weakening of verdict-role
boundaries. Exact substitutions, executable taxonomy/gate tests, and
non-impairment review constrain it. Rollback is a separately governed two-path
revert; it cannot alter the companion or taxonomy implementation.

## Recommended Commit Type

docs
