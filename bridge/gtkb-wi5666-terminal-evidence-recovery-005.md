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


# Terminal Evidence Recovery — WI-5666 exact continuation and atomic finalization

bridge_kind: prime_proposal
Document: gtkb-wi5666-terminal-evidence-recovery
Version: 005
Responds to: bridge/gtkb-wi5666-terminal-evidence-recovery-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666

target_paths: ["bridge/gtkb-wi5666-terminal-evidence-recovery-007.md"]

## Claim

The original WI-5666 chain is permanently non-terminal because v007 is a
malformed Prime Builder report. This separate recovery may create only one
current bridge-native evidence report for immutable source commit
ad19a3662baf1c8d206901e9a4bc83b7f3d7ecfd. Independent LO then either issues
NO-GO or atomically finalizes that report and a verdict. No history, source,
test, configuration, generated artifact, or fixture may be changed.

## Requirement Sufficiency

Existing requirements sufficient. The recovery introduces no source work. The
new explicit bridge-evidence PAUTH corrects only the prior authority-class gap.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- DELIB-202667193 — owner-directed autonomous sweep authority.

## Owner Decisions / Input

No new owner decision is required. PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724
implements DELIB-202667193 only for the append-only report and independent LO
atomic finalization; it does not widen the original source-sweep PAUTH.

## Authority Boundary

The prior PAUTH remains excluded for bridge audit artifacts and is not
reinterpreted. The new PAUTH permits only WI-5666 bridge and governance-evidence
mutations: the one PB report at v007 and independent LO finalization. It
forbids source, test, configuration, documentation, fixture, generated-adapter,
historical rewrite, dispatcher, deployment, external-system, credential,
history-rewrite, and push operations.

## Exact Continuation Schema

If this revision receives GO at v006, PB may file only
bridge/gtkb-wi5666-terminal-evidence-recovery-007.md through the canonical
bridge writer. Its nonblank schema must be:

NEW
bridge_kind: implementation_report
Document: gtkb-wi5666-terminal-evidence-recovery
Version: 007
Responds to: bridge/gtkb-wi5666-terminal-evidence-recovery-006.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666
target_paths: ["bridge/gtkb-wi5666-terminal-evidence-recovery-007.md"]

The writer must inject real current PB identity, harness, session-context,
model, and metadata-source lines. The report must not claim historical v007 is
current authority, use decorated Version metadata, use Responds-to-GO shorthand,
or use synthetic author provenance.

## Atomic Finalization Contract

PB does not commit the report. After independent review of v007, LO either
issues NO-GO or runs the live write_verdict.py helper with
--finalize-verified and sole include
bridge/gtkb-wi5666-terminal-evidence-recovery-007.md. The transaction must
create v008 VERIFIED and one local commit containing exactly v007 and v008. A
file-only terminal verdict is invalid.

## Evidence Report Content

The exact v007 report must prove without source mutation:

1. git show --name-only --format= for ad19a3662 lists only .gitignore,
   groundtruth-kb/docs/reference/canonical-terminology-detail.md,
   docs/procedures/per-thread-finalization-repair.md, and
   docs/harness-parity-phase-2-matrix.md.
2. Parent/tree identity and historical v006 GO are immutable evidence; v007-v010
   historical records are accurately described as non-terminal/corrective.
3. Eight git check-ignore scratch probes pass, the mapping-aware residual scan
   over exactly those four committed paths has zero violations, and
   git diff --check ad19a3662^ ad19a3662 passes.
4. Before filing the index is empty for every non-bridge path; after filing,
   only v007 is eligible for the LO finalizer transaction.

## Implementation And Verification Plan

1. After GO, PB acquires the claim and an implementation-start packet under the
   new bridge-evidence PAUTH; stop on denial.
2. PB files only v007 through the canonical writer with actual command results.
3. LO independently rechecks schema, evidence anchors, author metadata, and
   index scope, then either NO-GOs or finalizes atomically with v007 as sole
   include.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority | GO, claim, packet, exact v007 schema | Only the PAUTH-permitted report is written. |
| Historical source scope | git show --name-only --format= ad19a3662 | Exactly four immutable implementation paths. |
| Acceptance evidence | ignore probes, residual scan, commit diff check | All recorded checks pass. |
| Terminal durability | LO atomic finalizer with v007 sole include | One local commit contains only v007 and v008. |

## Acceptance Criteria

- PB creates only v007 with exact schema and real writer metadata.
- The historical commit is evidenced without restaging or modification.
- Terminal outcome is LO NO-GO or an atomic LO commit containing v007 and v008.
- No source, test, config, fixture, historical bridge artifact, or unrelated
  worktree change is included.

## Risks And Rollback

The risk is another malformed report or file-only terminal verdict. Exact
schema validation, the bridge-only PAUTH, and the LO finalizer transaction fail
closed. No source rollback exists because no source mutation is authorized.

## Recommended Commit Type

docs
