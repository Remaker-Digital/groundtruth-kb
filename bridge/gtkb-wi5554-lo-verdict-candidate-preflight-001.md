NEW
::init gtkb lo
::open build

# WI-5554: Validate LO verdict candidate applicability before governed publication

bridge_kind: prime_proposal
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 001
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; governed proposal authoring

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554
Related Work Items: WI-5348, WI-5445, WI-5524

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py"]

implementation_scope: configuration_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Claim

The governed writer already audits final normalized in-memory bridge bytes
through `scripts.gtkb_bridge_writer.run_bridge_compliance_audit` before any
append-only file write. The shared compliance gate currently executes
candidate applicability and mandatory clause preflights only when the first
status is `NEW` or `REVISED`. As a result, Loyal Opposition `GO`, `NO-GO`, and
`VERIFIED` candidates can pass the writer audit without evaluating their own
specification and clause evidence.

This proposal closes that status-classification gap in the byte-identical
active/template hook pair and proves the existing writer chokepoint consumes
the correction. It does not modify writer source, dispatcher configuration,
TAFE, harness configuration, or runtime state.

## Defect / Reproduction

Canonical reproduction is preserved in the WI-5348 chain:

1. `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` became
   operative `GO` while omitting its own `## Specification Links`.
2. Its prose reported applicability evidence calculated against the prior
   Prime artifact, not the final `GO` candidate bytes.
3. The governed writer accepted v006 because
   `PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}` excludes every Loyal
   Opposition verdict status from candidate applicability and clause checks.
4. Once v006 was operative, the live applicability preflight failed with three
   missing required and three missing advisory specifications.
5. Prime Builder filed canonical `NO-ACTION` correction
   `bridge/gtkb-wi5348-retired-g-phase1-operative-population-007.md`.

The correction must occur before append-only publication, not after a malformed
verdict has become operative.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` already require mechanically
evaluable, fail-closed bridge artifacts. WI-5554 supplies the concrete defect,
scope, and linked test obligation. No new role, status, queue, dispatcher,
TAFE, or artifact authority is needed.

## In-Root Placement Evidence

All three targets are inside `E:/GT-KB`. The active and packaged hooks are GT-KB
bridge-enforcement surfaces; the new test module is platform coverage. No
external path, adopter repository, retired assessment directory, or
harness-local scratch artifact is an implementation dependency.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - malformed or conflicting required bridge
  state must fail closed before actionability or mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - specification
  linkage is mechanically enforced, including on a final `GO` candidate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` candidate
  bytes must carry and satisfy the complete spec-derived evidence floor.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the exact candidate
  artifact must be evaluable before publication.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - all existing stricter bridge
  gates and valid publication routes must remain intact.
- `GOV-WORK-TREE-HYGIENE-001` - shared hook work requires terminal predecessors,
  clean preimages, exact targets, and unrelated-byte preservation.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - active and packaged hooks must
  implement and test one behavior.
- `ADR-CROSS-HARNESS-PARITY-001` - supported harness publication paths receive
  the same shared writer audit without a harness-specific bypass.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex helper-managed bridge writes
  receive the same compliance semantics as Claude hook writes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH is additive
  to independent GO, exact claim, start, report, and verification gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - mutation authority remains bounded
  to WI-5554 and the exact three targets.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - every protected
  mutation requires fresh operation-time authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  related work, and exact target metadata are explicit.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - the WI-5348 correction route remains
  valid, while future corrected `GO` candidates are evaluated before write.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - final candidate evaluation must not
  weaken trusted author metadata or review-independence checks.
- `SPEC-AUQ-POLICY-ENGINE-001` - the existing owner decision and active PAUTH
  are explicit; no approval is inferred from prose.
- `GOV-STANDING-BACKLOG-001` - WI-5554 and its test carrier preserve the
  discovered defect until terminal verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes
  bounded carriers for defects discovered while driving the black-box program,
  while preserving every bridge and implementation gate.
- `DELIB-1741` - prior verification of the mandatory bridge pre-filing
  preflight rule.
- `DELIB-1736` - prior review of the bridge pre-filing preflight hook.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` - accepted
  malformed `GO` that reproduced the candidate-content bypass.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-007.md` - canonical
  Prime correction and current WI-5554 source evidence.
- `bridge/gtkb-wi5445-active-template-hook-failclosed-parity-006.md` - current
  shared-hook predecessor whose NO-GO must be terminally resolved first.
- `bridge/gtkb-wi5524-bridge-compliance-fixture-envelope-refresh-003.md` -
  current implementation report for the fixture repair needed to resolve
  WI-5445 without weakening the hook.

## Owner Decisions / Input

No new owner decision is required.

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner basis
for active
`PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718`.
The PAUTH authorizes this bounded proposal and, only after independent GO plus
the normal claim/start gates and terminal shared-file predecessors, the exact
three-target implementation. It forbids dispatcher, TAFE, runtime, credential,
Git commit/history/push, deployment, release, external-system, destructive,
and unrelated mutation.

The owner-directed dispatcher-configuration troubleshooter hold remains
binding. This proposal neither reads nor mutates dispatcher configuration.

## Proposed Scope

1. Replace the proposal-only candidate-preflight status classification with
   self-descriptive semantics that include `NEW`, `REVISED`, `GO`, `NO-GO`,
   and `VERIFIED`.
2. Run applicability and mandatory clause preflights against final normalized
   in-memory candidate bytes immediately before the governed append-only write.
3. Deny publication when either preflight reports missing specifications,
   blocking errors, or mandatory clause gaps.
4. Preserve status-specific structural, author-provenance, review-independence,
   transition, evidence-anchor, implementation-report, finalization, project,
   claim, and implementation-start gates.
5. Keep `scripts/gtkb_bridge_writer.py` unchanged. Its existing
   `run_bridge_compliance_audit` invocation remains the common publication
   chokepoint.
6. Add one focused test module that covers both hook copies and the shared
   writer audit for clean and malformed `GO`, `NO-GO`, and `VERIFIED`
   candidates, including NO-ACTION-to-GO and implementation-report-to-VERIFIED
   transitions.
7. Re-run adjacent bridge-compliance suites to prove `NEW` and `REVISED`
   behavior remains unchanged and no valid LO publication path regresses.

Out of scope:

- changes to `scripts/gtkb_bridge_writer.py`, verdict helpers, adapters, harness
  configuration, dispatcher configuration/runtime, TAFE, workers, claims,
  leases, eligibility, routing, or providers;
- weakening any production gate to make a fixture pass;
- bridge-history rewrite, alternate queues, retired aggregates, MemBase
  implementation mutation, credentials, external systems, Git staging/commit/
  history/push, deployment, release, destructive cleanup, or unrelated files.

## Start Conditions And Shared-File Sequencing

Implementation must not begin until all conditions are freshly true:

1. WI-5445 is independently `VERIFIED`, atomically finalized, and its exact
   active/template hook paths are clean.
2. WI-5524 is independently `VERIFIED`, atomically finalized, and its fixture
   paths are clean.
3. The active and packaged hook preimages are byte-identical at current HEAD.
4. WI-5554 is latest independent `GO`.
5. An exact three-target work-intent claim and schema-v3 implementation-start
   packet are active for this session.
6. Operation-time authorization passes immediately before each mutation.

Any failed condition stops before protected-file mutation.

## Cross-Harness Disposition

- Claude Code: the active PreToolUse hook and packaged template remain
  byte-identical and evaluate final `GO`, `NO-GO`, and `VERIFIED` bytes.
- Codex: all helper-managed writes continue through
  `scripts.gtkb_bridge_writer.run_bridge_compliance_audit`; focused tests prove
  identical candidate denial without modifying writer source.
- Antigravity and Cursor: dispatched provider verdict publication continues
  through `publish_lo_verdict` / `write_bridge_file` and receives the same
  corrected shared audit; no adapter or harness configuration changes.
- Ollama, OpenRouter, and Alibaba provider workers: no harness-specific source
  target is required because their governed verdict publication also converges
  on the shared writer.

No parity waiver is requested.

## Specification-Derived Verification Plan

| Requirements | Executable verification | Required result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Exercise malformed final verdict candidates through both hooks and `run_bridge_compliance_audit`. | Denial occurs before any numbered file exists; both preflights receive exact final bytes. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Reproduce a WI-5348-v006-shaped `GO`: prior Prime proposal clean, candidate specification links absent. | Active hook, template hook, and writer audit all deny the candidate. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exercise complete and incomplete `VERIFIED` candidates after an implementation report. | Complete candidate reaches later finalization gates; incomplete candidate fails during candidate preflight/evidence evaluation. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Exercise a corrected `GO` after `NO-ACTION`. | Candidate preflights run on the corrected `GO`; valid transition semantics remain intact. |
| Cross-harness parity authorities | Parameterize all semantic cases over active and packaged hooks; compare bytes and SHA-256. | Identical decisions and exact byte equality. |
| Project-authorization authorities | Re-run latest-GO, PAUTH, claim, start, and per-target operation-time validators. | Exact WI-5554 three-target authority only. |
| Non-impairment and hygiene authorities | Run the new module plus disposition, envelope, requirement-sufficiency, project-metadata, and hard-block suites; run Ruff, format, py_compile, and diff checks. | All focused/adjacent checks pass; only three approved paths differ. |
| Artifact lifecycle and isolation authorities | Run both candidate preflights and verify every source/evidence path is in-root and canonical. | Zero missing specs/clause gaps and no noncanonical dependency. |

Required commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py
git diff --check -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight
```

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5554; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718; WI-5348 v006/v007",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001 plus the canonical active/template bridge compliance hook and governed writer audit",
  "primary_route": "all governed numbered bridge writes converge on scripts.gtkb_bridge_writer.run_bridge_compliance_audit before append-only publication",
  "before_behavior": "NEW and REVISED candidate bytes execute applicability and clause preflights, while GO, NO-GO, and VERIFIED candidates can bypass those candidate-content checks and become operative before their own gaps are discovered",
  "after_behavior": "every Prime proposal/report and Loyal Opposition verdict candidate executes the same applicability and mandatory clause floor on its final normalized bytes before publication",
  "self_descriptive_naming": "candidate-preflight status names distinguish the shared final-byte gate from proposal-only structural gates",
  "obsolete_guidance_disposition": "proposal-only PENDING_PREFLIGHT_STATUSES naming and documentation are replaced in the active/template hooks; no alternate writer, queue, or authority is created",
  "history_preservation": "existing numbered bridge files remain append-only, including WI-5348 v006 and the canonical v007 correction",
  "baseline": {
    "shared_predecessors": "WI-5445 latest NO-GO v006 and WI-5524 implementation report v003 awaiting independent verification",
    "hook_state": "active and packaged hooks are currently byte-identical but dirty under the predecessor implementation",
    "writer_state": "run_bridge_compliance_audit already evaluates final in-memory content before write and remains out of implementation scope",
    "reproduction": "WI-5348 v006 accepted without its own Specification Links; operative applicability then failed"
  },
  "expected_result": {
    "malformed_verdict": "denied before append-only file creation",
    "valid_verdict": "continues to all existing status-specific and finalization gates",
    "parity": "active and packaged hooks remain byte-identical and semantically equivalent",
    "runtime_mutation": "zero dispatcher, TAFE, harness, worker, claim, lease, routing, provider, or cache mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5554 hook and test hunks",
    "verification": "rerun both-hook parity, focused/adjacent pytest, Ruff, py_compile, exact-target diff, and both bridge preflights"
  },
  "hard_invariants": [
    "no existing bridge gate or valid publication requirement is weakened",
    "final normalized candidate bytes are the bytes evaluated immediately before write",
    "all governed writer and provider paths continue to use one shared audit",
    "WI-5445 and WI-5524 terminal clean baselines precede shared-hook mutation",
    "no dispatcher/TAFE configuration/runtime, harness state, credentials, deployment, release, push, or unrelated worktree state is mutated"
  ],
  "fail_closed_conditions": [
    "WI-5445 or WI-5524 is not independently VERIFIED and atomically finalized",
    "active/template hook preimages are dirty, unequal, or drift after claim/start",
    "independent GO, exact claim, schema-v3 start, or per-target authorization is absent",
    "applicability or clause preflight returns a candidate gap",
    "focused or adjacent tests, parity, lint, format, compile, or diff checks fail",
    "implementation would require writer, adapter, dispatcher, TAFE, harness, or unrelated mutation"
  ],
  "essential_context_preservation": "candidate evaluation preserves status, author/model provenance, session-context independence, response linkage, project/WI/PAUTH metadata, specification links, prior deliberations, owner evidence, target paths, requirement sufficiency, cross-harness disposition, verification mapping, finalization evidence, risks, rollback, and append-only history"
}
```

## Acceptance Criteria

1. A WI-5348-v006-shaped `GO` candidate lacking its own complete specification
   links is denied before any numbered file is written, even when the prior
   Prime artifact passes.
2. `GO`, `NO-GO`, and `VERIFIED` candidates each execute applicability and
   mandatory clause preflights through both hook copies and the shared writer
   audit; every reported candidate gap blocks publication.
3. Valid LO verdict candidates continue through all existing provenance,
   independence, transition, evidence, and finalization gates.
4. `NEW` and `REVISED` candidate behavior remains unchanged.
5. Active and packaged hooks finish byte-identical; the focused and adjacent
   suites, Ruff, format, compile, diff, applicability, and clause checks pass.
6. No dispatcher configuration/runtime, TAFE, harness state, writer source,
   provider, credential, Git publication, deployment, release, or unrelated
   file is mutated.
7. Independent `VERIFIED` and atomic focused finalization are required before
   WI-5554 becomes terminal.

## Pre-Filing Preflight

The exact candidate body is subject to both mandatory content-file preflights
immediately before helper-mediated filing. Filing is prohibited unless
applicability reports `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, and
`blocking_errors: []`, and the mandatory clause preflight reports zero
blocking gaps.

## Risks / Rollback

The primary risk is over-broadening proposal-only structural checks when only
candidate applicability/clause execution should broaden. The implementation
must separate the shared final-byte preflight status set from status-specific
proposal metadata and requirement-sufficiency sets, and tests must prove clean
LO verdicts remain valid.

The second risk is shared-file collision. Terminal WI-5445 and WI-5524,
clean/equal hook preimages, exact claim/start evidence, and operation-time
authorization are hard start conditions.

Rollback requires separate authority and reverts only the focused WI-5554
hunks in the exact three targets. Numbered bridge history and predecessor
commits remain intact.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`

## Recommended Commit Type

`fix(bridge)`: enforce applicability and clause preflights on final Loyal
Opposition verdict candidate bytes.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
