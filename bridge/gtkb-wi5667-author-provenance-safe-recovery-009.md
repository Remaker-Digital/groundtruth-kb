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
Document: gtkb-wi5667-author-provenance-safe-recovery
Version: 009
Responds to: bridge/gtkb-wi5667-author-provenance-safe-recovery-008.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667
target_paths: ["bridge/gtkb-wi5667-author-provenance-safe-recovery-011.md"]
observed_paths: ["bridge/gtkb-wi5667-author-provenance-safe-recovery-007.md", "bridge/gtkb-wi5667-author-provenance-safe-recovery-008.md", "groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]
implementation_scope: governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation and authorizes no source, test, template, configuration, or Git-history mutation.

# WI-5667 GO-lineage repair for post-facto provenance reconciliation

## Revision Disposition

Version 008 accepts version 007's factual reconciliation and identifies one
blocking lifecycle defect: this chain has never had a `GO`, so an
implementation report cannot proceed directly to terminal verification.

This version is the required normal reconciliation proposal. It adopts only
the narrow non-mutating historical-disposition scope, requests an independent
GO, and authorizes exactly one future GO-linked bridge report at version 011.
It does not re-propose, mutate, stage, or verify any of the 17 observed
source/test/template/configuration paths.

## Claim

After an independent GO at version 010, a fresh exact claim, and a schema-v3
implementation-start packet, Prime Builder may file only
`bridge/gtkb-wi5667-author-provenance-safe-recovery-011.md`. That report will
preserve and freshly recheck the version-007 provenance inventory, explicitly
declare the version-010 controlling GO, and request terminal review of the
historical-disposition evidence only.

No observed path is a mutation target. The broad owner commit remains
immutable historical provenance, not a retroactively authorized isolated
WI-5667 implementation.

## Requirement Sufficiency

Existing requirements are sufficient. Version 008 identifies a missing
lifecycle step, not a missing product requirement. The file-bridge authority,
project linkage, specification-derived evidence, and artifact-lifecycle rules
fully govern the one-report transaction. No new owner decision is needed.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202667193` — owner-directed gtkb-prefixed managed-template outcome.
- `DELIB-202667194` — exact foreign-hunk isolation requirement.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — bounded recovery precedent
  retaining independent review.
- `DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER` — hunk-scoped
  disposition precedent; no waiver is invoked by this proposal.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-007.md` — accepted
  factual target-to-commit and retain-disposition inventory.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-008.md` — immediate
  NO-GO requiring this proposal/GO/report sequence.

## Owner Decisions / Input

The retain disposition continues to follow `DELIB-202667193`, while the
historical lifecycle violation remains explicit. No retain-versus-reverse
choice is reopened and no owner waiver supplies the missing GO. Independent
review is the required next decision.

## Exact Authorized Output

The version-011 report must:

1. identify version 010 as `Controlling GO` and respond to that verdict;
2. retain `target_paths` as only the version-011 report itself;
3. restate that it performs no MemBase or observed-path mutation;
4. map all 17 originally declared paths to
   `db07f9dcfe7e7de8addc850729209278472cb0fe` or the accepted no-change
   disposition for `groundtruth-kb/tests/test_doctor.py`;
5. associate only the six managed-skill substitutions in `doctor.py` with
   WI-5667 and exclude the evaluator/decoding work;
6. retain the current gtkb-prefixed outcome without retroactive GO or isolated
   commit claims;
7. re-run the exact 17 focused tests, Ruff check, Ruff format-check, scoped
   status/hash checks, and both bridge preflights;
8. request terminal review of the report's accuracy only.

Any source/test/template/configuration drift that changes the accepted factual
inventory is a stop condition requiring a new proposal rather than silent
adoption.

## Specification-Derived Verification Plan

| Specification | Required verification | Expected result |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Full v001-v010 chain and commit provenance | Authors/commits remain readable; no history rewritten. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | v009 proposal → independent v010 GO → claim/start → v011 report | Canonical GO-linked lifecycle exists before terminal review. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact one-report target and active PAUTH | Only governance-evidence report creation is allowed. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh schema-v3 packet for the version-011 path | `allowed=true`; no observed path classified for mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight/header inspection | PAUTH, project, WI, and exact target are complete. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | Zero missing required/advisory specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact 17-test suite, complete per-spec mapping, and clause preflight | Tests/quality pass and every linked spec has evidence. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Durable 17-path provenance inventory and retain disposition | Historical state is preserved without lifecycle laundering. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Version-011 governed report | Reconciliation exists as a durable reviewable artifact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v008 NO-GO → v009 proposal → v010 GO → v011 report | Every dependent action follows its governing trigger. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Root-boundary inspection | All cited live paths remain inside `E:\GT-KB`. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact scoped status/hash checks and one-report finalization cohort | Foreign `doctor.py` dirt remains observation-only and unstaged. |

## Implementation Procedure After GO

1. Confirm latest status is independent `GO` v010 and all accepted provenance
   facts remain unchanged.
2. Acquire the exact claim and run `implementation_authorization.py begin
   --no-write`, then normal `begin`, for only the version-011 report path.
3. File the version-011 GO-linked report through the governed writer. Do not
   edit or stage any observed path.
4. Independent LO re-runs the declared evidence and uses the governed atomic
   finalizer only if every criterion passes.

## Terminal Finalization Boundary

At terminal review, the helper must include every then-untracked numbered file
in this thread plus the new verdict, and no observed source/test/template/config
path. Under current state that cohort is expected to be:

- v007 and v008;
- this v009;
- the independent v010 GO;
- the GO-linked v011 report;
- the generated v012 verdict.

Versions 001 through 006 are already tracked and clean. The intended local
subject is `docs(bridge): reconcile WI-5667 landed rename provenance`. No push
is authorized.

## Acceptance Criteria

- Version 009 receives an independent GO before any version-011 report is
  filed.
- The fresh claim/start packet authorizes only the version-011 report path.
- Version 011 explicitly links to the controlling GO and changes no observed
  path.
- The accepted 17-path mapping and foreign-doctor exclusion remain exact.
- The exact focused tests and quality gates pass.
- Terminal verification uses the governed helper over only the full untracked
  bridge cohort and records commit-finalization evidence.

## Risk And Rollback

The risk is mistaking a factually sound post-facto report for a GO-authorized
implementation lifecycle. The explicit proposal/GO/report sequence and
single-report target repair that lineage without rewriting history or approving
the broad commit. Rollback is append-only bridge disposition only.

## Pre-Filing Preflight

Applicability preflight against the completed candidate passed:

- packet hash:
  `sha256:ef07e7e839293147d541edbde22bff26369d64be931536de366f781fa2b733da`;
- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `warnings.unclassified_target_paths: []`;
- `blocking_errors: []`.

Mandatory clause preflight also passed: five clauses evaluated, four
`must_apply`, one `may_apply`, zero evidence gaps in must-apply clauses, zero
blocking gaps, exit zero.

## Recommended Commit Type

`docs:` — evidence-only provenance reconciliation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
