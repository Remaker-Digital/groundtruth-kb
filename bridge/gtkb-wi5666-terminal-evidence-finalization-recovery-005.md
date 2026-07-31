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
Document: gtkb-wi5666-terminal-evidence-finalization-recovery
Version: 005
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-004.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666

target_paths: ["platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py", "bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-007.md"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5666 REVISED Proposal — Specification-Derived Test Recovery

This proposal performs no KB or MemBase mutation.

## Summary

Replace the rejected evidence-only terminal plan with one focused executable
test module that cites and verifies all fifteen specifications carried by this
thread. Preserve the already-committed four-path WI-5666 implementation as
read-only historical evidence. After independent GO, create only the new test
file, execute the required focused and spec-derived runners, and file v007 as
the implementation report. Independent Loyal Opposition retains sole authority
for the v008 terminal verdict and atomic finalization.

## Response To V004

V004 found that static Git, ignore-pattern, residual-reference, worktree, and
preflight observations do not satisfy the mandatory specification-derived-test
contract. This revision accepts that finding in full:

- all fifteen linked specifications are retained; none is waived or declared
  inapplicable;
- one exact test path is now declared;
- every retained specification maps below to a named executable assertion;
- the owner approved the exact test expansion in
  `DELIB-20260730-WI5666-SPEC-DERIVED-TEST-EXPANSION`;
- the exact singleton PAUTH is current at v2 and adds only mutation class
  `test` to its existing `bridge` and `governance_evidence` authority.

## Requirement Sufficiency

Existing requirements are sufficient. V004 precisely defines the missing
terminal gate, and the owner decision supplies the previously absent test
authority. No source, configuration, documentation, fixture, generated
adapter, runtime, dispatcher, TAFE, repository-metadata, deployment,
credential, external-system, Git-history-rewrite, push, or destructive-cleanup
mutation is required or authorized.

## In-Root Placement Evidence

Both declared targets are beneath `E:/GT-KB`. The test target is under the
canonical platform test tree, and the report target is the next Prime-authored
implementation-report slot after the expected v006 LO verdict.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires role-correct, append-only,
  numbered bridge publication and independent review/finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — keeps the owner decision, PAUTH,
  executable test, report, and verdict as durable governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  revision to cite every applicable specification concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires created and
  executed tests derived from every retained specification before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires exact PAUTH,
  project, work-item, and target-path linkage.
- `SPEC-AUQ-POLICY-ENGINE-001` — binds the scope expansion to the owner's
  explicit approval rather than inferred authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — confines all artifacts to the
  GT-KB root and keeps adopter applications out of scope.
- `GOV-STANDING-BACKLOG-001` — keeps WI-5666 as the canonical work carrier and
  requires terminal reconciliation only after real evidence exists.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — requires the Claude and Codex scratch
  ignore probes to remain equivalent for their canonical renamed skills.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserves traceability from owner
  decision through PAUTH, proposal, test, report, and verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserves REVISED, GO, report, and
  VERIFIED as separate append-only lifecycle states.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — limits implementation to the
  exact WI-5666 singleton authorization.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires fresh
  claim/start evaluation before test or v007 mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — forbids treating the owner
  decision or PAUTH as a substitute for v006 GO and implementation start.
- `GOV-WORK-TREE-HYGIENE-001` — requires exact-path cleanliness and preserves
  unrelated staged or dirty work.

## Owner Decisions / Input

- `DELIB-20260730-WI5666-SPEC-DERIVED-TEST-EXPANSION` records the owner's exact
  approval for one test path and append-only v005-v008 continuation.
- `PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724` v2
  allows only `bridge`, `governance_evidence`, and `test` mutation classes for
  WI-5666. It forbids external-system, dispatcher, TAFE, runtime-state,
  credential, production-deployment, destructive-cleanup, Git-history-rewrite,
  and push operations.
- `DELIB-202667193`, `DELIB-202667194`, and `DELIB-202666273` remain the
  historical bounded-sweep and evidence-preservation decisions.
- `DELIB-202666552` and `DELIB-202666673` continue to require valid atomic
  terminal evidence rather than a file-only verdict.

## Proposed Implementation

Create exactly
`platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py`.
Its module docstring must cite all fifteen specifications verbatim so
`scripts/run_spec_derived_tests.py` can discover the mapping. The test module
must use deterministic in-root fixtures and read-only Git/bridge observations;
it must not mutate the four historical implementation paths, the live index,
MemBase, dispatcher/TAFE state, or any runtime carrier.

The module must provide these named checks (equivalent finer-grained names are
acceptable only if the v007 report preserves a one-to-one mapping):

1. `test_recovery_bridge_chain_is_append_only_role_separated_and_exactly_linked`
   verifies the v005 proposal metadata, the independent v006 role boundary,
   the expected v007 report slot, project/WI/PAUTH linkage, and no bridge
   bypass.
2. `test_owner_decision_and_exact_pauth_v2_cover_only_wi5666_test_recovery`
   verifies the owner-decision link, WI singleton, exact allowed mutation
   classes, and retained forbidden operations.
3. `test_historical_commit_has_exact_four_path_boundary_and_current_targets_are_clean`
   verifies commit `ad19a3662baf1c8d206901e9a4bc83b7f3d7ecfd` contains exactly
   `.gitignore`, `docs/harness-parity-phase-2-matrix.md`,
   `docs/procedures/per-thread-finalization-repair.md`, and
   `groundtruth-kb/docs/reference/canonical-terminology-detail.md`; all four
   current paths must equal HEAD and remain unstaged.
4. `test_all_eight_canonical_scratch_patterns_ignore_their_probe_paths`
   verifies these exact probes return ignored:
   `.claude/skills/gtkb-bridge/helpers/draft-x.md`,
   `.claude/skills/gtkb-verify/helpers/draft-x.md`,
   `.claude/skills/gtkb-verify/helpers/_temp_verdict_x`,
   `.claude/skills/gtkb-verify/helpers/x-draft-body.md`,
   `.claude/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md`,
   `.claude/skills/gtkb-verify/helpers/write_bridge_x.py`,
   `.codex/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md`, and
   `.codex/skills/gtkb-verify/helpers/gtkb-wi1-draft-body.md`.
5. `test_four_historical_targets_have_zero_residual_mapped_skill_paths`
   verifies zero matches for bare `bridge`, `verify`, `bridge-propose`, or
   `assertion-triage` skill directories across the exact four paths.
6. `test_module_declares_all_fifteen_specs_for_derived_test_discovery`
   locks the module-level spec citations and prevents silent mapping loss.

After the test passes, file only
`bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-007.md` as the
implementation report. It must identify every specification, the exact test
function that covers it, the command executed, and the observed result.

## Specification-Derived Verification Plan

| Specification | Required executable mapping |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | bridge-chain role separation and append-only transition test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | owner-decision/PAUTH/artifact-chain persistence test |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | exact fifteen-spec proposal-link test |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | module citation lock plus strict spec-derived runner |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | exact project/WI/PAUTH/target metadata test |
| `SPEC-AUQ-POLICY-ENGINE-001` | exact owner-decision provenance test |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | in-root target and four-path boundary test |
| `GOV-STANDING-BACKLOG-001` | WI-5666 canonical carrier and nonterminal-state test |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | eight Claude/Codex ignore-probe parity test |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | decision-to-test-to-report traceability test |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | REVISED-to-GO-to-report lifecycle test |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | exact singleton PAUTH v2 test |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | allowed classes and forbidden operations test |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | independent GO and implementation-start prerequisite test |
| `GOV-WORK-TREE-HYGIENE-001` | exact historical commit boundary and clean current targets test |

Required commands after v006 GO and implementation start:

```text
python -m pytest platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py -q --tb=short
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5666-terminal-evidence-finalization-recovery --dry-run --json
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5666-terminal-evidence-finalization-recovery --json --strict
ruff check platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py
ruff format --check platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py
git diff --check -- platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5666-terminal-evidence-finalization-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5666-terminal-evidence-finalization-recovery
```

## Acceptance Criteria

- The v005 candidate and live artifact pass applicability and mandatory clause
  preflights with all fifteen specifications and no gaps.
- Independent v006 GO precedes a fresh exact claim and schema-v3
  implementation-start packet for the test file and future v007 report only.
- The focused test file cites all fifteen specs and every named assertion
  passes.
- The spec-derived dry run reports all fifteen specifications covered; strict
  execution exits zero.
- The historical four implementation paths remain unchanged, clean, and
  unstaged; unrelated worktree/index state is preserved.
- V007 provides per-spec path, assertion, command, and observed-result
  evidence.
- Independent v008 uses the governed atomic finalizer over the complete
  v001-v008 chain and the one test file, creates no unrelated commit content,
  and performs no push.

## Cross-Harness Disposition

The only cross-harness behavior in scope is read-only verification that the
eight Claude/Codex scratch probes remain equivalent. No harness adapter, hook,
rule, registration, session envelope, or runtime state changes.

## Risks And Rollback

The primary risk is writing a brittle repository-state test. The test must use
exact immutable commit identity, exact bounded paths, and current-HEAD equality
without asserting that the entire shared worktree or real index is globally
clean. It must not adopt unrelated dirty or staged paths.

Rollback is a separately governed revert of the one test file if needed.
Bridge and deliberation artifacts remain append-only and are never deleted or
rewritten. The historical four-path source result is not a rollback target.

## Files Expected To Change

- `platform_tests/scripts/test_wi5666_terminal_evidence_finalization_recovery.py`
- `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-007.md`

## Recommended Commit Type

`test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
