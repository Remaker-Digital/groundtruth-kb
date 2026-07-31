REVISED
::init gtkb lo
::open build

# WI-5554: Bind LO verdict preflight evidence to its source and final candidate

bridge_kind: prime_proposal
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 003
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; governed proposal revision
author_metadata_source: explicit_interactive_session_metadata

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
selected_remediation: narrow_verdict_preflight_freshness

## Revision Claim

This revision accepts the Loyal Opposition's preferred Path 1 and withdraws
version 001's proposal to run the complete proposal applicability and mandatory
clause bars against every `GO`, `NO-GO`, and `VERIFIED` candidate.

The correction is now limited to the stale or copied evidence class:

1. when a verdict carries an `## Applicability Preflight` section, the hook
   validates that the embedded packet hash recomputes against the exact
   canonical artifact named by `Responds to`;
2. the section carries a deterministic, path-bound
   `candidate_evidence_hash` over the final normalized verdict bytes, with only
   that hash value replaced by a fixed sentinel during calculation; and
3. the hook denies a missing, mismatched, wrong-thread, wrong-version, or
   non-recomputable evidence anchor before publication.

This design binds the source preflight packet and the final verdict bytes
without imposing `## Specification Links` on verdicts. Full candidate
applicability and clause execution remains limited to `NEW` and `REVISED`.
Existing `NO-GO` verdicts that carry no applicability section remain valid.
The existing rule that `GO` and `VERIFIED` must carry a clean applicability
section remains unchanged.

No writer, verdict helper, dispatcher, TAFE, harness, worker, provider, or
runtime target is added.

## Finding Addressed

### Finding 1 (P1): Full-bar widening would break valid verdict shapes

**Concurred.** Version 001 treated a freshness defect as a reason to widen the
proposal-only applicability and clause gates. Because the applicability tool
derives cited specifications only from a recognized `Specification Links`
section, that approach would silently create a new structural requirement for
verdicts and could reject currently sanctioned `write_verdict.py` output.

Version 003 removes that widening completely:

- `PENDING_PREFLIGHT_STATUSES` remains `{"NEW", "REVISED"}`;
- `GO`, `NO-GO`, and `VERIFIED` are not sent through the full candidate
  applicability or clause preflights;
- no verdict is newly required to carry `## Specification Links`;
- no change is proposed to `.claude/skills/verify/helpers/write_verdict.py`;
- a `NO-GO` with no applicability section continues through existing gates;
- a `GO` or `VERIFIED` continues to require the already-mandatory clean
  applicability section, now with mechanically fresh evidence anchors; and
- any `NO-GO` that voluntarily carries an applicability section receives the
  same freshness validation for that section.

The revised mechanism verifies the preflight packet against its declared
canonical source and then seals that exact packet into the final candidate
bytes. It does not reinterpret the source packet as proof that the verdict
itself has a `Specification Links` section.

## Requirement Sufficiency

Existing requirements sufficient.

The linked bridge-authority, evaluability, applicability, verification,
non-impairment, parity, and project-authorization requirements already demand
fresh, mechanically evaluable evidence at the governed publication boundary.
WI-5554 supplies the bounded implementation carrier and linked test obligation.
No new role, status, queue, authority, or owner policy decision is required.

## In-Root Placement Evidence

All three targets are within `E:/GT-KB`. The active and packaged compliance
hooks are canonical bridge-enforcement surfaces, and the new platform test
module is the linked executable verification carrier. No external path,
retired assessment directory, aggregate queue, harness-local memory, or
cross-session scratch artifact is an implementation dependency.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - required bridge evidence must fail closed
  before a malformed candidate becomes actionable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - full
  specification-linkage preflight remains a proposal/report gate and is not
  silently widened to verdicts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` retains its
  complete mapping and command-evidence requirements while its embedded
  applicability packet gains freshness validation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the exact normalized
  candidate and its canonical evidence source must be mechanically evaluable
  before publication.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - valid verdict forms without a
  `Specification Links` section remain valid.
- `GOV-WORK-TREE-HYGIENE-001` - shared hook mutation waits for terminal clean
  predecessors and exact hunk ownership.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes the
  bounded governed repair carrier while preserving GO, claim, start,
  operation-time authorization, report, and independent verification gates.
- `DELIB-1741` - prior verification of the mandatory bridge pre-filing
  preflight rule.
- `DELIB-1736` - prior review of bridge pre-filing enforcement.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` - canonical
  reproduction whose applicability evidence was not mechanically bound to the
  final verdict candidate.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-007.md` - canonical
  `NO-ACTION` correction preserving the discovered evidence-freshness defect.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md` - independent
  `NO-GO` selecting the narrow freshness correction as the preferred path.

## Owner Decisions / Input

No new owner decision is required because this revision adopts the Loyal
Opposition's preferred narrow fix and explicitly preserves the
Specification-Links-optional verdict route.

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` remains the owner
basis for
`PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718`.
The PAUTH authorizes only the bounded lifecycle and, after independent `GO`
plus all normal implementation gates, the exact three targets. It forbids
dispatcher, TAFE, runtime, credential, Git publication, deployment, release,
external-system, destructive, and unrelated mutation.

The owner-directed dispatcher-configuration troubleshooter hold remains
binding. This proposal neither reads nor mutates dispatcher configuration.

## Proposed Scope

1. Keep `PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}` and preserve the
   existing full applicability and clause behavior for those two statuses.
2. Add a focused verdict-preflight-freshness validator in each byte-identical
   hook copy.
3. Parse the verdict's exact `Responds to` bridge path and the
   `Applicability Preflight` section's structured packet hash, document name,
   `content_file` or legacy `operative_file`, and
   `candidate_evidence_hash`.
4. Resolve the declared source only within `E:/GT-KB`, require it to equal the
   exact `Responds to` artifact, rerun the applicability packet builder against
   that source, and compare its packet hash with the embedded hash.
5. Compute `candidate_evidence_hash` as SHA-256 over:
   - a normalized repository-relative candidate path;
   - one LF separator; and
   - the final LF-normalized candidate bytes after replacing only the
     `candidate_evidence_hash` value with the fixed ASCII sentinel
     `<CANDIDATE_EVIDENCE_HASH>`.
6. Deny a `GO` or `VERIFIED` when its mandatory applicability section lacks
   these freshness anchors, and deny any `GO`, `NO-GO`, or `VERIFIED` whose
   present section carries a mismatch.
7. Preserve `NO-GO` candidates with no applicability section, as that section
   is not currently mandatory for `NO-GO`.
8. Include the expected candidate hash in a denial message so a governed
   author can correct the evidence without a new helper or file target.
9. Preserve every existing status, provenance, review-independence,
   transition, implementation-report, finalization, project, claim,
   implementation-start, and append-only gate.
10. Add one focused test module parameterized over the active and template
    hook copies. Exercise the same active-hook audit called by the governed
    writer rather than modifying writer source.

Out of scope:

- complete applicability or clause execution against verdict candidates;
- a new `Specification Links` requirement on verdicts;
- changes to `scripts/gtkb_bridge_writer.py`,
  `.claude/skills/verify/helpers/write_verdict.py`, any skill/adapter,
  dispatcher configuration/runtime, TAFE, harness configuration/state,
  providers, workers, claims, leases, or routing;
- rewriting prior bridge history, alternate queues, retired aggregates,
  credentials, Git staging/commit/history/push, deployment, release,
  destructive cleanup, or unrelated worktree changes.

## Start Conditions And Shared-File Sequencing

Implementation must not begin until all conditions are freshly true:

1. WI-5445 is independently `VERIFIED`, atomically finalized, and both hook
   targets are clean at current HEAD.
2. WI-5524 remains independently `VERIFIED`, atomically finalized, and its
   fixture paths remain clean.
3. The active and packaged hook preimages are byte-identical at current HEAD.
4. WI-5554 is latest independent `GO`.
5. This session holds an exact three-target work-intent claim and a valid
   schema-v3 implementation-start packet.
6. Operation-time authorization passes immediately before each protected
   mutation.

Any failed condition stops before protected-file mutation. The current dirty
hook copies remain predecessor-owned and are not implementation-ready merely
because this revised proposal is filed.

## Cross-Harness Disposition

- Claude Code: the active PreToolUse hook validates the source packet and final
  candidate fingerprint before a verdict write.
- Codex: helper-managed bridge publication continues through the active hook's
  shared audit; no writer or Codex adapter change is required.
- Antigravity and Cursor: governed provider verdict publication continues to
  converge on the same active-hook audit.
- Ollama, OpenRouter, and Alibaba provider workers: no provider-specific target
  is needed because publication remains behind the common writer audit.
- Packaged installations: the template hook remains byte-identical to the
  active hook and is covered by the same semantic test cases.

No parity waiver is requested.

## Specification-Derived Verification Plan

| Requirements | Executable verification | Required result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Construct a verdict with an embedded packet copied from a different thread or version. | Both hook copies deny before publication and identify the source mismatch. |
| Mandatory applicability gate; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Construct `GO` and `VERIFIED` candidates whose packet hash recomputes against the exact `Responds to` artifact and whose candidate hash matches final bytes. | Both statuses reach the existing later gates without requiring their own `Specification Links` section. |
| Non-impairment | Exercise well-formed `GO`, `NO-GO`, and `VERIFIED` candidates with no `Specification Links` section; omit applicability entirely from the `NO-GO` case. | The freshness gate permits all three current verdict shapes. |
| Narrow freshness semantics | Mutate one final candidate byte after calculating `candidate_evidence_hash`. | Both hook copies deny with the recomputed expected hash. |
| Narrow freshness semantics | Keep the candidate hash valid but alter the embedded packet hash or source path. | Both hook copies deny the stale or wrong-source packet. |
| Proposal linkage requirements | Exercise `NEW` and `REVISED` candidates with existing clean and failing preflight fixtures. | Existing behavior and `PENDING_PREFLIGHT_STATUSES` remain unchanged. |
| Cross-harness parity authorities | Compare active/template bytes and parameterize all focused cases over both files. | Exact byte equality and identical decisions. |
| Project authorization authorities | Re-run latest-GO, PAUTH, claim, schema-v3 start, and per-target operation-time checks. | Authority remains limited to WI-5554 and the exact three targets. |
| Hygiene and isolation authorities | Run focused/adjacent tests, Ruff, format, py_compile, diff checks, and both proposal preflights. | All checks pass; no out-of-root or unrelated target changes. |

Required implementation-verification commands include:

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
  "provenance": "WI-5554; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718; WI-5554 v002 preferred Path 1",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001 plus the byte-identical active/template compliance hook and governed writer audit",
  "primary_route": "all governed verdict writes converge on the active compliance audit before append-only publication",
  "before_behavior": "a verdict can carry a passing-shaped packet copied from another source, and the final candidate bytes have no mechanical binding to that packet",
  "after_behavior": "the packet hash recomputes against the exact Responds-to artifact and a path-bound hash seals that packet into the final normalized candidate bytes",
  "self_descriptive_naming": "verdict preflight source freshness and candidate evidence hash distinguish this narrow evidence check from full proposal applicability",
  "obsolete_guidance_disposition": "version 001's full-bar status widening is withdrawn; PENDING_PREFLIGHT_STATUSES remains NEW and REVISED",
  "history_preservation": "existing numbered bridge history remains append-only",
  "baseline": {
    "shared_predecessors": "WI-5445 remains REVISED and must terminalize; WI-5524 is terminal VERIFIED",
    "hook_state": "active and packaged hooks are dirty under predecessor work and are not touched by this revision",
    "writer_state": "run_bridge_compliance_audit remains the common publication chokepoint and is out of scope",
    "compatibility": "verdicts remain exempt from a mandatory Specification Links section"
  },
  "expected_result": {
    "stale_packet": "denied before append-only publication",
    "mutated_candidate": "denied before append-only publication",
    "valid_go_or_verified": "continues through all existing later gates without a new Specification Links requirement",
    "nogo_without_applicability": "continues through existing gates",
    "runtime_mutation": "zero dispatcher, TAFE, harness, worker, provider, claim, lease, routing, or cache mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5554 hook and test hunks",
    "verification": "rerun both-hook parity, focused/adjacent pytest, Ruff, py_compile, exact-target diff, and both proposal preflights"
  },
  "hard_invariants": [
    "PENDING_PREFLIGHT_STATUSES remains NEW and REVISED",
    "no verdict gains a mandatory Specification Links section",
    "all existing stricter status, provenance, transition, report, finalization, project, claim, and start gates remain intact",
    "active and packaged hooks finish byte-identical",
    "no dispatcher/TAFE configuration/runtime or unrelated worktree state is mutated"
  ],
  "fail_closed_conditions": [
    "the embedded packet does not recompute against the exact Responds-to source",
    "the candidate evidence hash is missing when required or does not match final normalized bytes",
    "the source path escapes the project root or names a different thread/version",
    "WI-5445 or WI-5524 is not terminally finalized at implementation start",
    "active/template hook preimages are dirty, unequal, or drift after claim/start",
    "independent GO, exact claim, schema-v3 start, or per-target authorization is absent",
    "focused or adjacent tests, parity, lint, format, compile, or diff checks fail"
  ],
  "essential_context_preservation": "status, author provenance, session independence, response linkage, project/WI/PAUTH metadata, source packet, candidate fingerprint, prior deliberations, owner evidence, target paths, requirement sufficiency, parity disposition, verification mapping, finalization evidence, risks, rollback, and append-only history remain explicit"
}
```

## Acceptance Criteria

1. A verdict whose embedded applicability packet points to a different bridge
   artifact than its exact `Responds to` path is denied before publication.
2. A verdict whose embedded packet hash does not recompute against that source
   is denied before publication.
3. A one-byte mutation after `candidate_evidence_hash` calculation is denied.
4. Valid `GO` and `VERIFIED` candidates without a `Specification Links`
   section pass this freshness gate when their already-required applicability
   section has valid source and candidate anchors.
5. A valid `NO-GO` without an applicability section remains permitted; a
   `NO-GO` that includes one receives the same freshness checks.
6. `NEW` and `REVISED` full preflight behavior remains unchanged.
7. Active and packaged hooks finish byte-identical, focused and adjacent tests
   pass, and the writer source and verdict helper remain unchanged.
8. No dispatcher configuration/runtime, TAFE, harness state, provider,
   credential, Git publication, deployment, release, or unrelated file is
   mutated.
9. Independent `VERIFIED` and atomic focused finalization are required before
   WI-5554 becomes terminal.

## Pre-Filing Preflight

The exact v003 candidate is filed only through the governed revision helper,
which runs the applicability and mandatory clause preflights in
`--content-file` mode immediately before publication. Filing requires
`preflight_passed: true`, empty missing required and advisory specification
lists, empty blocking errors, and zero mandatory clause gaps.

## Risks / Rollback

The main risk is inventing an evidence hash that is ambiguous across paths,
line endings, or self-reference. The implementation must use the one specified
algorithm: normalized repository-relative path, LF separator, LF-normalized
final bytes, and replacement of only the hash value with one fixed ASCII
sentinel. Tests cover CRLF input, slash normalization, copied candidates, and
one-byte post-hash mutation.

The second risk is accidental broadening. Tests explicitly preserve verdicts
without `Specification Links`, `NO-GO` without an applicability section, and
the existing `NEW`/`REVISED` preflight set.

The third risk is shared-file collision. Terminal WI-5445 and WI-5524,
clean/equal preimages, exact claim/start evidence, and operation-time
authorization are hard start conditions.

Rollback requires separate authority and reverts only the focused WI-5554
hunks in the exact three targets. Numbered bridge history and predecessor
commits remain intact.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`

## Recommended Commit Type

`fix(bridge)`: bind verdict preflight evidence to source and final candidate.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
