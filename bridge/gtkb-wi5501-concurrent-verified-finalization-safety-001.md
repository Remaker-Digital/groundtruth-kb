NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5501 Concurrent VERIFIED Finalization Safety

bridge_kind: prime_proposal
Document: gtkb-wi5501-concurrent-verified-finalization-safety
Version: 001 (NEW)
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5501
Related Work Items: WI-5511, WI-5513, WI-5514
target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]
Recommended commit type: fix:

## Claim

Repair `finalize_verified_commit` so two or more governed VERIFIED finalizers
cannot create sibling commits and then roll each other back through stale
real-index snapshots. The transaction must serialize helper finalizers,
preserve unrelated concurrent real-index updates, fail closed on same-path
collisions, and leave each successfully committed target clean in the real
index.

This is a finalization-transaction repair only. It does not change bridge
verdict eligibility, review independence, included-path coverage,
predecessor-chain validation, hunk-patch semantics, dispatcher behavior,
worker eligibility, harness routing, or the user's dispatcher
configuration/runtime hold.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-WORK-TREE-HYGIENE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the project-authorization
envelope requirements, and the existing disposable-index/hunk-finalization
contracts already define the required outcome and fail-closed boundaries. The
defect is an implementation gap in the current transaction, not a missing
requirement. No new or revised specification is required before
implementation.

## Defect / Reproduction

Canonical MemBase WI-5501 version 7 records the current reproduction:
multiple independent VERIFIED finalizers each created a valid commit from the
same parent, then `_realign_real_index_after_temp_commit` compared the live
index against a stale full-index `entries_before` snapshot, raised on peer
changes, and the exception path atomically moved `HEAD` back to the common
parent. The result was a succession of orphaned commits, missing verdict files,
and source/test bytes left dirty despite successful independent verification.

The live implementation explains that result:

1. `_prepare_real_index_realign` captures every real-index entry before the
   disposable-index commit.
2. `git commit` moves the shared branch ref while no transaction-wide
   finalizer lock is held.
3. `_realign_real_index_after_temp_commit` writes committed paths one process
   per path, then requires every non-committed index entry to equal the stale
   pre-commit snapshot.
4. Any peer finalizer or background index writer that changes an unrelated
   entry during that window makes the transaction report failure after its
   commit already exists.
5. The exception path uses `update-ref HEAD <old> <created>` to roll its commit
   back. Repeated sibling transactions can therefore leave every valid commit
   unreachable from the active branch.

The three managed helper projections are currently byte-identical at
SHA-256 `549e12e6b8cb2f998c36d06b51da8ac98a013ed2d6d5ee766abae66535af5ec2`,
and all four proposal targets are clean relative to current HEAD.

## In-Root Placement Evidence

All targets are inside `E:\GT-KB`:

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`

No external, adopter, dispatcher configuration, TAFE, runtime-state, or
harness-registry path is in scope.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Tree Stabilization project PAUTH.
  PAUTH version 3 has no included-work-item restriction and permits source,
  test, repository-metadata, metadata, configuration, documentation,
  runtime-state, governance-evidence, and bridge classes. It continues to
  forbid dispatcher mutation, Git commit/history/push, deployment, release,
  credentials, destructive cleanup, and external-system mutation.
- `DELIB-202666775` records the owner's sequencing decision: Claude was to
  file only WI-5511 and leave the already-owned WI-5501 proposal to this Codex
  session. This filing completes that existing assignment rather than
  creating a competing implementation vehicle.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remains
  controlling. No dispatcher configuration/runtime inspection or mutation is
  proposed.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` is honored. The
  reproduction above is carried from canonical MemBase WI-5501; no scratch or
  retired external report is cited.
- No new owner decision is required for proposal review.

## Prior Deliberations

- `DELIB-202666064` - independently VERIFIED disposable-index finalization
  baseline whose safeguards must be preserved.
- `DELIB-202666231` - independently VERIFIED binary hunk-patch finalizer
  support whose semantics must be preserved.
- `DELIB-202666173` - finalization-scoped NO-GO precedent.
- `DELIB-202666274` - owner authority for Tree Stabilization.
- `DELIB-202666775` - owner sequencing: this Codex session retains WI-5501;
  Claude files only WI-5511.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - successful exact finalization must not leave
  inverse staged residue or orphan verified work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - VERIFIED publication and finalization
  remain bound to the numbered bridge chain and role authority.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the concurrency
  transaction requires executed, race-focused verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  carries all relevant governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and exact targets are explicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - any implementation remains
  independently GO, claim, and implementation-start gated.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - operation-time authority must
  match this exact proposal and target set.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - the selected
  project-scope PAUTH has no restrictive included-work-item list.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - bridge behavior and normal
  Git workflows must remain intuitive and non-impaired.
- `ADR-CROSS-HARNESS-PARITY-001` - governed VERIFIED finalization must preserve
  equivalent behavior across supported local harness projections.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the canonical helper and its
  generated local projections must remain aligned and parity-tested.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and test
  paths remain in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Cross-Harness Disposition

- **Claude / harness B:** applicable. The canonical
  `.claude/skills/verify/helpers/write_verdict.py` helper owns the behavior.
- **Codex / harness A:** applicable. The byte-identical
  `.codex/skills/verify/helpers/write_verdict.py` projection must preserve the
  canonical helper's behavior.
- **Cursor / harness E:** applicable. The byte-identical
  `.cursor/skills/verify/helpers/write_verdict.py` projection must preserve the
  canonical helper's behavior.
- **Antigravity / harness C:** not an implementation target because no managed
  local `write_verdict.py` projection exists for this helper. Antigravity must
  continue through the existing governed finalization route; no parity waiver
  is requested.
- **Ollama / harness D, OpenRouter / harness F, and Alibaba / harness H:** not
  implementation targets because provider workers do not own these local
  helper projections. Their existing governed publisher/finalizer routes remain
  unchanged; no parity waiver is requested.

## Proposed Scope

### 1. Serialize governed finalizers

Add one repository-scoped, cross-process finalization lock held from before
the verdict write through disposable commit creation, real-index realignment,
postconditions, and failure cleanup. The lock must:

- serialize only governed `finalize_verified_commit` transactions;
- use a bounded wait and a diagnostic naming the contended repository;
- release in `finally`, including validation and Git failures;
- never terminate, disable, reroute, or de-eligibilize a worker;
- not claim to serialize unrelated raw Git commands that do not honor it.

### 2. Make real-index preservation path-local

Retain the pre-commit snapshot only for committed-path collision detection and
preserved-overlap reconstruction. Immediately before realignment, re-read the
live real index and:

- fail closed if any committed path differs from the accepted pre-commit
  entry unless that exact overlap was already captured by the existing
  preservation plan;
- treat the current non-target entries as foreign state to preserve;
- update only the exact committed paths;
- verify the committed paths equal the expected candidate/preserved-overlap
  entries;
- do not reject or overwrite unrelated index changes that appeared during the
  disposable commit window.

### 3. Batch committed-path realignment

Replace the one-`git update-index`-process-per-path loop with one exact
`update-index --index-info` transaction for the complete committed-path set.
The payload must support additions, replacements, and removals, validate every
entry before invocation, preserve path quoting safely, and never name a
non-committed path. This shrinks the interruption and index-lock window
without weakening validation.

### 4. Harden post-commit HEAD handling

Capture and validate the finalizer's created commit deterministically.
Before realignment and before returning success, prove current `HEAD` is that
commit or a state explicitly accepted by the transaction. On failure:

- roll back only with the existing compare-and-swap form when `HEAD` still
  equals the finalizer's own commit;
- never move a peer's later commit;
- retain the verdict and provide a recovery diagnostic when compare-and-swap
  cannot safely roll back.

WI-5513 separately owns broad retry classification for Git's
`cannot lock ref HEAD` diagnostic; this proposal does not duplicate or
supersede that work.

### 5. Preserve all existing gates and projections

Keep unchanged:

- review-independence and real session-context checks;
- predecessor-chain containment;
- report-claim/include-set coverage;
- hunk-patch path and hash validation;
- foreign staged-hunk preservation on committed paths;
- disposable-index staged-set validation;
- exact committed-path verification;
- failed-verdict cleanup rules;
- auto-retirement only after successful terminal commit.

Apply the canonical helper change identically to Claude, Codex, and Cursor
managed projections and prove byte parity.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5501; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Serialize governed VERIFIED finalizers and make real-index reconciliation path-local.",
  "before_behavior": "Valid peer finalizers can create sibling commits, reject one another's unrelated index updates, and roll their own commits out of the active branch.",
  "after_behavior": "Governed finalizers commit in one linear order; unrelated staged work survives; same-path collisions fail closed before overwrite.",
  "self_descriptive_naming": "Finalization lock, pre-realignment snapshot, committed-path entries, and preserved overlap remain explicit concepts.",
  "history_preservation": "No existing commit or bridge artifact is rewritten; recovery is forward-only through new serial finalizations.",
  "obsolete_guidance_disposition": "No governance guidance is retired. Existing disposable-index, hunk-patch, independence, and atomic-finalization contracts remain controlling.",
  "baseline": {
    "managed_helper_sha256": "549e12e6b8cb2f998c36d06b51da8ac98a013ed2d6d5ee766abae66535af5ec2",
    "projection_count": 3,
    "atomicity_test_module": "platform_tests/scripts/test_lo_verified_commit_atomicity.py",
    "known_failure": "Canonical MemBase WI-5501 v7 records valid sibling finalizer commits rolled out of active HEAD by stale real-index reconciliation."
  },
  "expected_result": {
    "concurrent_finalizers": "Two controlled finalizers produce two reachable parent-child commits with both verdicts retained.",
    "unrelated_index_change": "The foreign staged blob remains byte-identical and finalization succeeds.",
    "same_path_change": "Finalization fails closed without overwriting the foreign entry.",
    "projection_parity": "Claude, Codex, and Cursor helper bytes remain identical."
  },
  "rollback": {
    "instructions": "Governedly restore the four approved targets to their pre-change hashes without rewriting bridge or Git history.",
    "verification": "Re-run the complete pre-change atomicity module, projection hash parity, Ruff, format, compile, and diff checks."
  },
  "hard_invariants": [
    "No unrelated real-index entry is overwritten or adopted.",
    "No same-path concurrent mutation is silently accepted.",
    "No worker or dispatcher state is modified.",
    "No existing finalization eligibility or verification gate is weakened."
  ],
  "fail_closed_conditions": [
    "The repository finalization lock cannot be acquired within its bounded wait.",
    "A committed-path entry changes unexpectedly.",
    "HEAD cannot be proven to reference the finalizer's created commit at a required boundary.",
    "Any helper projection differs or any concurrency regression test fails."
  ],
  "essential_context_preservation": "The implementation report and terminal verdict must preserve the exact lock boundary, path-local realignment algorithm, before/after index blobs, HEAD ancestry, committed path set, projection hashes, and every existing finalization-gate regression result."
}
```

## Specification-Derived Verification Plan

| Specification / invariant | Required executed evidence |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001`; unrelated-work preservation | Inject an unrelated real-index mutation between disposable commit and realignment; finalization succeeds and the exact foreign staged blob remains |
| Same-path fail-closed behavior | Inject a committed-path real-index mutation at the same boundary; finalization refuses overwrite, performs only safe CAS rollback, and preserves the foreign staged state |
| Linear terminal history | Run two controlled finalizers for different bridge threads concurrently; prove the lock serializes them, both verdicts remain, commits form a parent-child chain, and HEAD contains both |
| Batched exact realignment | Instrument Git calls; prove one `update-index --index-info` operation covers all committed paths and no foreign path enters its payload |
| Lock lifecycle | Force validation, commit, and realignment failures; prove lock release and a later finalizer can proceed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Re-run existing predecessor, include-set, independence, failed-verdict cleanup, and atomic commit tests unchanged |
| Hunk-patch and binary preservation | Re-run existing hunk-patch, overlap, CRLF, binary MemBase, and real-index preservation tests unchanged |
| Projection parity | SHA-256 compare all three managed helpers after generation/copy; require byte identity |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete atomicity module plus focused concurrency nodes and report exact results |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Confirm ordinary single-finalizer behavior and diagnostics remain compatible; no dispatcher/harness/config path changed |

Required commands:

- `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short`
- Focused pytest nodes for concurrent finalizers, unrelated index mutation,
  same-path collision, batched update-index, and lock release.
- `python -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `python -m ruff format --check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `python -m py_compile .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `git diff --check -- .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py`

## Acceptance Criteria

- Two governed finalizers cannot execute the commit/realignment transaction
  concurrently for the same repository.
- A controlled two-finalizer test produces two reachable linear commits and
  retains both terminal verdict files.
- An unrelated concurrent index mutation is preserved byte-for-byte and does
  not make a valid finalization roll back.
- A same-path concurrent mutation fails closed without overwrite.
- Real-index committed-path updates use one bounded batched Git operation.
- All existing atomicity, hunk-patch, binary, CRLF, overlap, independence,
  include-set, predecessor, cleanup, and lock-retry tests continue to pass.
- Claude, Codex, and Cursor helper projections are byte-identical.
- No dispatcher, TAFE, harness registry, worker, configuration, credential,
  external system, deployment, release, push, or unrelated Git history is
  touched.
- Implementation is not authorized until fresh independent GO, an exact
  work-intent claim, and schema-v3 implementation-start authorization.
- Terminal closure still requires independent VERIFIED and an atomic local
  finalization after WI-5501 itself proves the race is fixed.

## Applicability Preflight

- Candidate canonical file:
  `bridge/gtkb-wi5501-concurrent-verified-finalization-safety-001.md`.
- content_source: `pending_content`.
- packet_hash before recording this result subsection:
  `sha256:b2992455b2307c5545b5523588c8fa019f6c4ea0939eb648792282c1b0a87b64`.
- preflight_passed: `true`.
- declared_target_paths:
  `[".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]`.
- missing_required_specs: `[]`.
- missing_advisory_specs: `[]`.
- blocking_errors: `[]`.

## Clause Applicability

- Candidate canonical file:
  `bridge/gtkb-wi5501-concurrent-verified-finalization-safety-001.md`.
- Clauses evaluated: 5.
- `must_apply`: 4.
- `may_apply`: 1.
- Evidence gaps in `must_apply` clauses: 0.
- Blocking gaps: 0.
- Mandatory result: PASS, exit 0.

## Risks / Rollback

The principal risk is deadlock or over-broad serialization. Bound the lock
wait, hold it only around one finalization transaction, release it in every
exit path, and test failure recovery. A second risk is accepting a same-path
foreign staged hunk as unrelated; compare exact committed-path entries before
realignment and retain the existing preserved-overlap preflight.

Rollback is a governed reversion of the four target files to their pre-change
bytes. Existing bridge files and commits remain append-only; no history
rewrite is a rollback mechanism.

## Files Expected To Change

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
