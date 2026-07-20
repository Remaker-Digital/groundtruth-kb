REVISED
::init gtkb lo
::open build

# WI-5554: Make verdict freshness evidence producible by sanctioned tooling

bridge_kind: prime_proposal
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 007
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-006.md
Date: 2026-07-19 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; governed proposal revision
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554
Related Work Items: WI-5348, WI-5445, WI-5524, WI-5600

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/bridge_applicability_preflight.py", "scripts/gtkb_bridge_writer.py", "platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: configuration_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
selected_remediation: shared_verdict_candidate_preparation

## Revision Claim

Version 005 proved that the version-003 freshness validator is internally
consistent, but version 006 correctly found that no sanctioned authoring path
can produce its mandatory `candidate_evidence_hash`. This revision keeps the
approved fail-closed freshness semantics and adds the missing production
preparation path.

One public candidate-preparation API in
`scripts/bridge_applicability_preflight.py` will:

1. accept the final intended root-contained candidate path and normalized
   verdict content;
2. when an applicability section exists, resolve the exact canonical same-
   thread artifact named by `Responds to`;
3. rebuild the applicability packet against that source immediately before
   publication;
4. replace the candidate's existing applicability section with the rebuilt
   packet plus one fixed hash sentinel;
5. compute the path-bound hash over those final bytes; and
6. return the prepared content with the sentinel replaced by the hash.

`scripts/gtkb_bridge_writer.py` will call this API after author metadata and
bridge-envelope normalization and immediately before the existing compliance
audit. The applicability CLI will expose the same API as a deterministic,
write-free final-preparation mode for direct `Write` users. The hook will
consume the public hash implementation when available and retain its local
equivalent only as a fail-closed partial-install fallback.

This preserves both sanctioned routes. It does not require authors or tests to
import hook-private functions, does not weaken the validator, and does not
declare direct `Write` unsupported.

## Findings Addressed

### Finding 1 (P0/P1): no sanctioned producer exists

**Concurred.** The version-005 focused tests manufactured valid candidates by
calling the hook's private `_candidate_evidence_hash`, while the real writer,
verdict finalizer, provider publisher, and direct-Write route had no equivalent
operation. Because existing `GO` and `VERIFIED` gates require an applicability
section, the new mandatory hash made those statuses unreachable through
documented tooling.

The correction is production-path preparation, not validator relaxation:

- `write_bridge_file()` prepares after all writer-owned byte normalization and
  before `run_bridge_compliance_audit()`;
- `publish_lo_verdict()` and the atomic `write_verdict.py` finalizer inherit
  the behavior through their existing `write_bridge_file()` call;
- a new CLI final-preparation mode emits exact prepared bytes for the direct
  `Write` route without writing a numbered bridge artifact;
- the focused hook tests use the public preparation API instead of hook-
  private internals;
- writer tests exercise the real integration point; and
- the stale hard-block fixture is rebuilt through the sanctioned preparation
  path rather than receiving a hand-computed hash.

The existing full applicability and clause candidate preflights remain limited
to `NEW` and `REVISED`. Verdicts do not gain a `Specification Links`
requirement.

### Finding 2 (P2): packet hash appeared fragile under concurrent MemBase state

**Concurred with investigation required.** The packet is intentionally a hash
of the complete deterministic applicability result, including the fixed source
content/path, applicable specification projection, and blocking diagnostics.
It must not contain timestamps, MemBase row versions, unrelated work items, or
other ambient revision counters.

The implementation will add executable stability coverage proving:

- repeated builds for a fixed source and fixed applicable-governance
  projection produce the same packet hash;
- an unrelated MemBase write does not change that hash;
- a change to governance that is actually applicable to the candidate does
  change the packet and intentionally invalidates prior evidence; and
- last-moment preparation rebuilds the packet and candidate hash in one
  operation immediately before audit, eliminating the minutes-long
  composition window observed by the reviewer.

If the tests expose unrelated-state sensitivity, implementation stops at
`NO-GO`; the packet hash must not be weakened or declared advisory.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision supplies the missing
operability implementation for the already-approved freshness requirement; it
does not create a new role, status, authority, queue, or provider contract.

## In-Root Placement Evidence

All eight targets are within `E:/GT-KB`. The two hook copies, shared
applicability service, governed writer, and four focused test modules are
canonical in-root implementation or verification surfaces. Every dependency
named by this proposal is a canonical in-root surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - required verdict evidence must be
  mechanically producible and validated before append-only publication.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - full
  specification-linkage checks remain proposal/report gates and are not
  silently widened to verdicts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - atomic `VERIFIED`
  publication retains complete spec-derived evidence while inheriting
  last-moment candidate preparation from the shared writer.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the exact source packet,
  path, and final normalized candidate bytes are mechanically evaluable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - existing writer-mediated and
  direct-Write verdict routes remain functional.
- `GOV-WORK-TREE-HYGIENE-001` - exact WI-5554 hunks must be isolated from
  foreign dirty bytes and represented by a reviewable hunk patch.
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

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes this
  bounded repair carrier while preserving independent GO, claim, start,
  operation-time authorization, report, verification, and focused-finalization
  gates.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md` - rejected the
  original full-bar widening and selected narrow evidence freshness.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md` - independently
  approved the narrow validator design.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-006.md` - independently
  found the missing production producer, stale fixture, and packet-stability
  question addressed by this revision.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` and
  `bridge/gtkb-wi5348-retired-g-phase1-operative-population-007.md` - canonical
  reproduction and correction that established the original freshness defect.
- `bridge/gtkb-wi5600-provider-applicability-preflight-recovery-002.md` -
  preserves missing provider applicability-section enrichment as separate,
  serialized work after WI-5554 rather than duplicating it here.

## Owner Decisions / Input

No new owner decision is required. Preserving both writer-mediated and direct
`Write` routes is the non-impairing disposition; making either route
unsupported would require a separate owner decision and is not proposed.

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner basis
for active
`PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719`.
The obsolete three-file
`PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718`
is revoked. The V2 authorization names all eight targets and forbids
dispatcher, TAFE, runtime, live-worker, claim/lease, credential, unrelated,
Git commit/history/push, deployment, release, external-system, and destructive
mutation.

The owner-directed dispatcher-configuration troubleshooter hold remains
binding. This proposal does not mutate dispatcher configuration or runtime
state.

## Proposed Scope

1. Add public, deterministic verdict-candidate preparation primitives to
   `scripts/bridge_applicability_preflight.py`:
   - root-contained candidate-path normalization;
   - exact same-thread `Responds to` resolution;
   - one public candidate evidence hash implementation;
   - replacement of one existing applicability section with a freshly rebuilt
     packet and hash sentinel; and
   - a prepared-content return value with the final hash injected.
2. Add a CLI final-preparation mode requiring `--content-file` and the exact
   intended `--candidate-path`. It writes no bridge file, emits prepared
   candidate bytes on stdout, sends diagnostics to stderr, and rejects
   incompatible JSON/report modes.
3. In `write_bridge_file()`, run preparation after author metadata and envelope
   normalization but before the compliance audit. Audit and write the exact
   returned bytes.
4. Preserve a `NO-GO` with no applicability section unchanged. Do not
   synthesize a missing applicability section for `GO` or `VERIFIED`; the
   existing gate continues to deny it. WI-5600 remains responsible for any
   separately approved provider missing-section enrichment.
5. Make the active/template hook hash validator call the public hash function
   when importable, with its byte-equivalent local implementation retained only
   as a fail-closed partial-install fallback.
6. Replace private-hook fixture construction with the public preparation API.
7. Refresh the stale hard-block workspace fixture through the public API.
8. Add writer and CLI end-to-end tests, packet-hash stability tests, and
   unrelated-state/applicable-governance invalidation tests.
9. Run the unchanged atomic `VERIFIED` finalization suite to prove its existing
   writer call inherits preparation without modifying the finalizer.
10. Preserve all existing status, provenance, independence, transition,
    evidence-anchor, project, claim, implementation-start, finalization,
    credential, and append-only gates.

Out of scope:

- generating a missing applicability section for provider candidates;
- provider, harness, adapter, skill, or `write_verdict.py` changes;
- widening full candidate applicability or clause checks beyond `NEW` and
  `REVISED`;
- a new `Specification Links` requirement on verdicts;
- dispatcher configuration/runtime, TAFE, workers, claims, leases,
  eligibility, routing, credentials, external systems, deployment, release,
  Git staging/commit/history/push, destructive cleanup, bridge-history rewrite,
  alternate queues, retired aggregates, or unrelated changes.

## Start Conditions And Shared-File Sequencing

Implementation must not begin until all conditions are freshly true:

1. WI-5445 and WI-5524 remain independently terminal and finalized.
2. This v007 is latest independent `GO`.
3. V2 PAUTH is active and the obsolete PAUTH remains revoked.
4. The implementing session holds an exact eight-target work-intent claim and
   valid schema-v3 implementation-start packet.
5. No live worker or nonterminal peer claim owns any approved target hunk.
6. Current dirty target bytes are treated as quarantined evidence, not adopted
   wholesale. The implementing session reconstructs exact preimages, isolates
   only WI-5554 hunks, and produces a canonical hunk patch whose forward and
   reverse applicability and target list are verified.
7. The active and packaged hook copies finish byte-identical.
8. Operation-time authorization passes immediately before every protected
   mutation.
9. WI-5600 remains serialized and does not implement overlapping writer or
   preflight hunks until WI-5554 is terminal.

Any failed condition stops before protected mutation.

## Cross-Harness Disposition

- Claude Code direct `Write`: runs the deterministic final-preparation CLI as
  the literal last content-producing step, then submits those exact bytes to
  the active hook.
- Codex and helper-managed writes: inherit preparation from
  `write_bridge_file()`.
- Antigravity, Cursor, Ollama, OpenRouter, and Alibaba provider publication:
  inherit preparation through the existing common writer call; no
  provider-specific implementation is added.
- Atomic `VERIFIED` finalization: inherits preparation through its existing
  `write_bridge_file()` call.
- Packaged installations: the template hook remains byte-identical and the
  shared preflight/writer modules remain the one implementation.

No parity waiver is requested.

## Specification-Derived Verification Plan

| Requirements | Executable verification | Required result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; evaluability | Prepare `GO`, `NO-GO`, and `VERIFIED` candidates through the public API, then audit them through both hooks. | Exact-source packet and final candidate hash pass without private-hook calls. |
| Non-impairment | Exercise writer-mediated and direct-CLI preparation paths. | Both produce audit-passing exact bytes; neither route is disabled. |
| Existing status semantics | Exercise `NO-GO` without applicability and `GO`/`VERIFIED` without applicability. | `NO-GO` remains unchanged; existing mandatory-section gate still denies the other two. |
| Source freshness | Copy a packet from a different thread/version and mutate source governance. | Preparation rebuilds from exact `Responds to`; stale or wrong-thread evidence cannot survive. |
| Candidate freshness | Mutate one byte after preparation. | Both hooks deny with a candidate-hash mismatch. |
| Packet determinism | Rebuild against a fixed source before and after unrelated MemBase writes, then change applicable governance. | Unrelated writes preserve hash; applicable governance change intentionally changes it. |
| Writer integration | Call real `write_bridge_file()` after metadata/envelope injection. | Audit receives and disk receives the same prepared final bytes. |
| Atomic finalization | Run the existing LO `VERIFIED` atomicity suite unchanged. | Full suite passes and rollback behavior remains atomic. |
| Parity | Compare active/template bytes and decisions across focused cases. | Exact byte identity and identical outcomes. |
| Hygiene and authority | Re-run PAUTH, latest-GO, claim/start, hunk-patch, lint, format, compile, diff, and index checks. | Only approved WI-5554 hunks are attributed; foreign bytes and empty index are preserved. |

Required implementation-verification commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/bridge_applicability_preflight.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/bridge_applicability_preflight.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/bridge_applicability_preflight.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_gtkb_bridge_writer.py
git diff --check -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/bridge_applicability_preflight.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight
```

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5554; WI-5554 v006; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001 plus the shared applicability service, governed writer, and byte-identical active/template compliance hooks",
  "primary_route": "prepare exact final verdict bytes immediately before the existing compliance audit and append-only write",
  "before_behavior": "the validator requires a final-candidate hash that sanctioned authors cannot produce, and a packet captured during composition may be stale before publication",
  "after_behavior": "the writer and direct-Write CLI rebuild existing applicability evidence against the exact Responds-to source and bind it to final normalized candidate bytes as one last-moment operation",
  "self_descriptive_naming": "prepare_verdict_candidate and candidate_evidence_hash distinguish production preparation from enforcement",
  "obsolete_guidance_disposition": "version 003's claim that no writer or direct-Write helper change is required is superseded; its narrow freshness semantics remain",
  "history_preservation": "all numbered bridge history remains append-only",
  "baseline": {
    "provider_missing_section": "separate WI-5600 work; not synthesized here",
    "hook_state": "current dirty bytes remain quarantined until exact hunk ownership and implementation-start checks pass",
    "writer_state": "all helper, provider, and atomic-finalizer routes already converge on write_bridge_file",
    "direct_write_state": "remains supported through deterministic final-preparation output"
  },
  "expected_result": {
    "valid_go_or_verified": "prepared and accepted without a private hook call",
    "nogo_without_applicability": "unchanged and still valid",
    "missing_go_or_verified_applicability": "still denied by the existing gate",
    "stale_packet_or_mutated_candidate": "rebuilt or denied before publication",
    "runtime_mutation": "candidate preparation is a pure content transformation and performs no dispatcher, TAFE, harness, worker, provider, claim, lease, eligibility, routing, or cache mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5554 hunks represented by the verified hunk patch",
    "verification": "rerun both publication paths, hook parity, focused and atomic pytest, lint, format, compile, diff, and bridge preflights"
  },
  "hard_invariants": [
    "PENDING_PREFLIGHT_STATUSES remains NEW and REVISED",
    "verdicts do not gain a Specification Links requirement",
    "NO-GO without applicability remains valid",
    "missing GO or VERIFIED applicability remains denied",
    "writer-mediated and direct-Write routes remain supported",
    "active and packaged hooks finish byte-identical",
    "no dispatcher, TAFE, provider, harness, runtime, claim, lease, or unrelated mutation occurs"
  ],
  "fail_closed_conditions": [
    "the Responds-to source is missing, out of root, or from another thread",
    "the rebuilt source packet does not pass",
    "candidate preparation cannot replace exactly one hash sentinel",
    "packet stability depends on unrelated MemBase state",
    "independent GO, V2 PAUTH, exact claim, schema-v3 start, per-target authority, or exact hunk ownership is absent",
    "focused, atomic, parity, lint, format, compile, diff, or preflight checks fail"
  ],
  "essential_context_preservation": "status, author/model provenance, session independence, response linkage, project/WI/PAUTH metadata, source packet, candidate fingerprint, prior deliberations, owner evidence, target paths, requirement sufficiency, parity disposition, verification mapping, finalization evidence, risks, rollback, and append-only history remain explicit"
}
```

## Acceptance Criteria

1. A valid `GO` or `VERIFIED` candidate can be prepared and published through
   both writer-mediated and direct-Write routes without importing a hook-
   private function or hand-computing a hash.
2. Writer preparation occurs after metadata/envelope normalization and before
   audit; the audited bytes exactly equal the written bytes.
3. The exact same-thread `Responds to` packet is rebuilt at preparation time,
   and the final path-bound candidate hash matches those final bytes.
4. `NO-GO` without applicability remains unchanged; missing `GO` or
   `VERIFIED` applicability remains denied.
5. Fixed-source packet hashes survive unrelated MemBase writes but change for
   applicable governance changes.
6. The focused, hard-block, applicability, writer, and unchanged atomicity
   suites all pass without private-hook fixture construction.
7. Active and packaged hooks finish byte-identical.
8. Only exact approved WI-5554 hunks are attributed; all foreign dirty bytes
   remain preserved and quarantined.
9. No dispatcher configuration/runtime, TAFE, live worker, provider, harness,
   claim/lease, credential, Git publication, deployment, release, external-
   system, destructive, or unrelated mutation occurs.
10. Independent `VERIFIED` and focused finalization are required before
    WI-5554 becomes terminal.

## Pre-Filing Preflight

The exact v007 candidate is filed only through the governed revision helper,
which runs applicability and mandatory clause preflights in `--content-file`
mode immediately before publication. Filing requires `preflight_passed: true`,
empty missing required and advisory specification lists, empty blocking
errors, and zero mandatory clause gaps.

## Risks / Rollback

The main risk is circular or ambiguous byte preparation. The implementation
must normalize metadata and envelope first, rebuild one existing applicability
section, insert one fixed ASCII sentinel, calculate the path-bound hash once,
and audit/write those exact returned bytes.

The second risk is accidental duplication with WI-5600. WI-5554 refreshes and
binds an existing applicability section. It does not generate a section that a
provider omitted; WI-5600 stays serialized for that separate behavior.

The third risk is commingled dirt. Implementation uses exact preimage
reconstruction and a canonical hunk patch; it never adopts whole-file dirty
state merely because a path is authorized.

Rollback requires separate authority and reverts only the exact focused
WI-5554 hunks after reverse-applicability verification. Numbered bridge history
and foreign worktree bytes remain untouched.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `scripts/bridge_applicability_preflight.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`fix(bridge)`: make verdict freshness evidence producible.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
