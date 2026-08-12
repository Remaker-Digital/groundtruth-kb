NEW
::init gtkb lo
::open build

# WI-6140 — bounded exact-source applicability-horizon cycle-breaker

bridge_kind: prime_proposal
Document: gtkb-wi6140-source-horizon-cycle-breaker
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-08-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; harness A; transcript-defined ::init gtkb pb; lead completion and bounded dependency-recovery lane
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6140

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch", "bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false

---

## Summary

This proposal performs no KB, MemBase, or groundtruth.db mutation.

Create one clean, separately governed five-target carrier for the retained
WI-6140 exact-source applicability-horizon repair. For an explicit canonical
numbered `content_file` at version `N`, the applicability packet must derive
its prospective finalization member from that declared source horizon, exactly
`N+1`; materializing that successor must not make the unchanged source packet
synthesize and hash `N+2`.

This carrier is the bounded ordering inversion authorized by
`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`. The
owner's explicit direction to “independently GO, implement, and atomically
VERIFY” this carrier is the narrow serialized release for this carrier only.
The prior global numbered-bridge writer hold remains closed for every other
lane.

This carrier may reach independent atomic VERIFIED before WI-5950
terminalization. It does not claim that the source-horizon patch repairs
WI-5950's separately reproduced missing-PAUTH-read-context defect. After this
clean carrier terminalizes, the controlling row-14277 sequence resumes:
WI-5950 terminalization, then narrow WI-5953 recovery, then disposition of the
original `gtkb-wi6140-verdict-packet-hash-source-horizon` chain.

## Proposal Claim

Repair only the exact-source finalization horizon:

1. When `build_packet()` receives an explicit canonical numbered
   `content_file`, `_pauth_phase_cohort()` derives the anticipated finalization
   member from the source's declared version, exactly `source_version + 1`.
2. Siblings newer than that explicit source are outside that source packet's
   observation horizon and cannot cause synthetic `N+2` drift.
3. Content without a canonical declared source version retains the existing
   observed-version fallback.
4. Source bytes, rules, target paths, current PAUTH state, and candidate bytes
   remain independently bound and fail closed on drift.
5. No writer, verdict-helper, packet-schema, approved-chain, candidate-restamp,
   receipt-recovery, registry, real-index, W0P, dispatcher, or TAFE behavior
   changes.

This is a regression repair of the exact-source binding contract. It is not a
freshness bypass, post-publication restamp, append-only exception, or
substitute for independent review and atomic finalization.

## Exact Five-Target Scope

1. `scripts/bridge_applicability_preflight.py`
   - adopt only the retained declared-source `N+1` horizon hunk;
   - preserve the noncanonical observed-version fallback;
   - leave proposal selection, phase classification, approved-chain
     resolution, PAUTH evaluation, and packet schema unchanged.

2. `platform_tests/scripts/test_bridge_applicability_preflight.py`
   - adopt only the retained exact-source sibling-invariance and
     noncanonical-fallback tests.

3. `platform_tests/scripts/test_check_protected_commit_authorization.py`
   - adopt only the retained protected-commit report/VERIFIED snapshot test;
   - prove unchanged source/candidate evidence passes before and after
     successor materialization;
   - prove source drift and candidate drift still fail independently;
   - absorb no WI-6183 or WI-5950 missing-read-context projection-ledger test
     or implementation byte.

4. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch`
   - retain the exact reviewed source patch unchanged.

5. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch`
   - retain the exact reviewed two-module test patch unchanged.

No sixth implementation target may be added under this proposal. Any target,
patch-content, or behavioral expansion requires a REVISED proposal and fresh
independent review.

## Retained Patch And Current-Preimage Evidence

Read-only preparation on 2026-08-11 established these current pre-patch Python
bytes:

| Path | SHA-256 | Bytes | Git state |
| --- | --- | ---: | --- |
| `scripts/bridge_applicability_preflight.py` | `44A2EC7CCBC4E86A7E04693AF1CC6048155C0364E4D725B606E5C2599ACED2AE` | 62582 | clean |
| `platform_tests/scripts/test_bridge_applicability_preflight.py` | `BFD745633D176FBA474B6C155D5F65F57ACC0AA20FFB142461E0D37CA143FF27` | 59373 | clean |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `EAC5B1A586514626E42805417B5A80B2DDC8440BD19469DF1CA421967C67E6DE` | 160292 | clean |

The retained, presently untracked cleanup-evidence patches are:

| Patch | Covered implementation paths | SHA-256 | Bytes | Retained delta |
| --- | --- | --- | ---: | --- |
| `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch` | `scripts/bridge_applicability_preflight.py` | `810D6CC9030A8E4B9427B62EF157FE13C1DF55BD792CBBC0100FACF59FB316B4` | 2593 | `+16/-5` |
| `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch` | both declared test modules | `FF5F00C8A0096FA96676E7B15B59875BA246B9F4224267A44CB55966E9FBE2BC` | 7668 | applicability `+109/-1`; protected-commit `+35/-6` |

Against the current three Python preimages, both exact retained patches pass:

```text
git apply --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch
git apply --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch
```

Both commands exited `0`. No patch was applied, no target was edited, and no
index was changed during preparation.

The earlier `gtkb-wi6140-verdict-packet-hash-source-horizon-005.md` report
recorded historical disposable-index checks, reverse-byte audits, `232 passed`,
and Ruff success for these same patch hashes. That evidence establishes patch
provenance only. It is not substituted for the fresh post-GO verification
required by this proposal.

If any current preimage or retained patch hash differs at implementation start,
or either forward check ceases to pass, implementation must stop before target
mutation and return for a REVISED proposal or corrected GO.

## Target-Overlap Disposition

The old `gtkb-wi6140-verdict-packet-hash-source-horizon` chain declared the
same five targets. Ordinarily that would make this carrier a duplicate.
Row 14282 expressly supersedes that duplicate-order objection by authorizing a
fresh clean carrier to run first. The old chain remains immutable non-closing
evidence and must receive its later row-14277 disposition; it is neither
withdrawn nor silently terminalized here.

WI-6042 historically overlapped
`scripts/bridge_applicability_preflight.py` and
`platform_tests/scripts/test_bridge_applicability_preflight.py`. The current
three Python preimages above are Git-clean, and this carrier absorbs no
WI-6042 byte or historical dirty-tree assumption.

The separate WI-6183/WI-5950 missing-read-context lane may overlap
`platform_tests/scripts/test_check_protected_commit_authorization.py`. Row
14282 gives this exact clean source-horizon carrier serialized priority. That
separate lane must wait, fresh-read the terminal WI-6140 result, and rebase or
revise its own test evidence afterward; this proposal absorbs none of it.

Immediately before claim acquisition and again before patch application, the
implementation owner must re-read all live claims, bridge target declarations,
the exact five paths, and the real-index hash. Any new foreign claim, dirty
target byte, staged overlap, or incompatible path declaration fails closed
before mutation. Owner sequencing authority does not waive fresh claim/path
collision checks.

## Authorized Dependency Sequence

`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`,
rowid `14282`, content hash
`d1357c38af43e1bf20e4007c19e348d29159369e44edcdd0d8da18258b44212c`,
authorizes exactly this bounded inversion:

1. independently review this clean carrier;
2. after GO, acquire its exact `go_implementation` claim and current schema-v3
   start packet;
3. implement and verify only the retained five-target patch;
4. reach independent atomic VERIFIED while preserving the real index and all
   foreign state;
5. resume WI-5950 terminalization;
6. perform the narrow WI-5953 recovery only after WI-5950 terminalizes; and
7. then dispose of the original WI-6140 chain as required by row 14277.

The controlling ordinary sequence remains
`DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`,
rowid `14277`, content hash
`fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`,
except for the single expressly authorized inversion above.

## Explicit Non-Scope

- No change to `scripts/check_protected_commit_authorization.py` or to the
  separately governed WI-6183 missing-PAUTH-read-context repair.
- No KB, MemBase, `groundtruth.db`, project-membership, PAUTH, registry, receipt
  row, or real-index mutation.
- No WI-5950 source/test byte, report, claim, packet, receipt, or finalization.
- No WI-5953 live receipt recovery, capability consumption, or row repair.
- No W0P mutation, release, ratification, terminalization, staging, or success
  claim. W0P remains quarantined non-closing evidence.
- No change to the original WI-6140 numbered chain.
- No candidate-evidence, proposal/GO selection, approved-chain, packet-schema,
  writer, verdict-helper, compliance-hook, or publication-currentness change.
- No real `.git/index` mutation by Prime Builder and no absorption of foreign
  staged bytes. Independent finalization must use the protected copied-index
  transaction and prove the real index byte-identical before and after.
- No whole-file staging of a shared path.
- No registry TOML, registry projection, dispatcher, scheduled task, legacy
  TAFE, credential, external-system, release, deployment, push,
  destructive-cleanup, or Git-history-rewrite operation.
- No numbered-bridge writer invocation by any other lane while this carrier's
  narrow serialized release is active.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision in
`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`, the
retained WI-6140 work-item requirement, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
version 2, the active whole-project PAUTH v2, and the linked bridge-authority,
exact-source freshness, operation-time authorization, non-impairment,
worktree-isolation, and specification-derived verification requirements fully
define this five-target repair.

No new target, behavior, KB mutation, receipt operation, registry condition,
W0P condition, or dispatcher behavior is required for this carrier. The
separate WI-6183 missing-read-context defect remains governed by its own
carrier and is not a missing requirement here.

## Acceptance Criteria

1. For an explicit canonical source `bridge/<slug>-NNN.md`, identical source,
   rules, targets, MemBase/PAUTH authority, and candidate state produce
   identical packet material and `packet_hash` before and after
   `bridge/<slug>-(NNN+1).md` materializes.
2. The explicit-source finalization cohort includes the source horizon and its
   anticipated immediate successor, never synthetic `NNN+2` solely because
   `NNN+1` now exists.
3. A real source-content mutation still changes the packet hash and is
   rejected as stale.
4. Rules, target-path, current-PAUTH mutation, expiration, or revocation still
   changes or blocks evidence as governed today.
5. Candidate-byte mutation still fails the independent
   `candidate_evidence_hash` check.
6. Noncanonical content with stale or plausible body-version metadata
   continues to use the observed-version fallback.
7. A protected-commit proposal → GO → implementation-report → prospective
   VERIFIED fixture passes before and after candidate materialization without
   bypass.
8. Both retained patches retain their exact hashes, apply cleanly to the
   implementation-start preimages, and touch exactly the three declared
   Python paths.
9. The complete focused and adjacent suites pass freshly after implementation;
   no historical count is reused as current evidence.
10. Ruff lint and format checks pass on all three Python paths.
11. Applicability, clause, claim, implementation-start, report, pre-verdict,
    and protected-commit gates remain fail-closed.
12. The real `.git/index`, database, registry state, W0P bytes, WI-5950 bytes,
    original WI-6140 chain, dispatcher state, and legacy TAFE state remain
    byte- and row-identical outside the independently finalized exact cohort.

## Implementation Plan

1. Use row 14282's narrow release only for this carrier. Keep every other
   numbered-bridge writer lane held.
2. Obtain independent Loyal Opposition review and GO on this exact
   five-target proposal.
3. In the sole designated Prime Builder implementation session, fresh-read the
   proposal, GO, current claims, path overlaps, PAUTH v2, all five targets,
   current HEAD, and real-index hash.
4. Acquire the exact `go_implementation` claim and mint/finalize one current
   schema-v3 implementation-start packet bound to the proposal, GO, PAUTH v2,
   five targets, and their fresh preimages.
5. Reconfirm both retained patch hashes and forward applicability. Fail closed
   on any divergence or overlap.
6. Apply the source patch and test patch unchanged. Do not regenerate, widen,
   or partially reinterpret either patch.
7. Prove touched paths and hunk counts match the retained evidence; record
   exact postimage hashes and confirm the real index remains unchanged.
8. Run the full specification-derived matrix below and record actual counts,
   timings, warnings, hashes, and exit codes.
9. Validate both patches in a disposable index seeded from clean `HEAD`;
   never stage the shared real index.
10. File a truthful implementation report under this new slug, with final
    candidate-aware applicability and clause evidence computed from the exact
    report bytes.
11. Release the Prime claim only through ordinary receipt-complete report
    publication.
12. Require a distinct Loyal Opposition session to rerun the mapped gates and
    perform atomic VERIFIED finalization through the exact hunk patches and
    governed numbered-chain cohort while preserving the real index, as
    required by `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` version 2.
13. Only after terminal receipt/commit/readback may coordination resume
    WI-5950, then WI-5953, then the original WI-6140 disposition.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires the append-only numbered bridge
  lifecycle, role-correct status authorship, and independent GO/VERIFIED.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — requires exact source and current
  authority evidence while prohibiting self-invalidating sibling observation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires current
  project-scoped implementation authorization in addition to bridge approval.
- `GOV-ARTIFACT-APPROVAL-001` — preserves separate approval requirements for
  protected narrative and governance evidence.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires PAUTH
  evaluation at proposal, start, report, and finalization operations.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — requires
  the exact GO-backed claim and current schema-v3 start packet before mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete
  specification linkage in this implementation proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires exact project,
  work-item, and PAUTH linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent
  tests derived from each operative requirement before VERIFIED.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` version 2 — requires the governed
  proposal/GO/start/report/independent-VERIFIED lifecycle and exact atomic
  commit evidence without real-index contamination.
- `GOV-WORK-TREE-HYGIENE-001` — requires exact preimages, hunk isolation,
  copied-index validation, and foreign-byte preservation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — requires
  candidate-aware applicability and clause checks at each lifecycle boundary.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires preservation of
  essential exact-source, candidate, PAUTH, review, overlap, and historical
  context.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — requires truthful concrete
  session-context authorship for proposal, report, and verdict.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — forbids treating PAUTH,
  retained patches, or owner sequencing authority as a substitute for GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — require durable append-only capture
  of the dependency inversion and its implementation evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps all active work and
  evidence within the GT-KB project boundary.

## Specification-Derived Verification Plan

| Governing requirement | Required executable evidence | Expected result |
| --- | --- | --- |
| Exact canonical-source sibling invariance | `test_finalization_exact_source_horizon_is_invariant_after_successor_materializes` | PASS before and after successor materialization with identical packet material/hash |
| Noncanonical observed fallback | `test_finalization_noncanonical_source_ignores_stale_declared_version_for_observed_fallback` | PASS; body metadata is not canonical identity |
| Protected-commit source/candidate separation | `test_report_verdict_hash_passes_before_and_after_candidate_materialization` | PASS for unchanged evidence; source and candidate drift fail independently |
| Full adjacent verification | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | exit 0, zero failures; record fresh count and timing |
| Static lint | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py` | exit 0 |
| Static formatting | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py` | exit 0 |
| Patch integrity | SHA-256 readback plus `git apply --check --whitespace=error-all` for both retained patches | exact declared hashes and exit 0 |
| Isolated finalization cohort | disposable copied-index application, strict whitespace check, numstat, and touched-path census | exact three Python paths; source `+16/-5`; tests `+109/-1` and `+35/-6`; no foreign path |
| Governed Git lifecycle v2 | finalization evidence under `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` version 2 | one independent atomic VERIFIED commit; no history rewrite or real-index contamination |
| Real-index preservation | SHA-256 readback of `.git/index` before and after Prime implementation and independent finalization | byte-identical |
| Operation-time PAUTH and overlap boundary | current PAUTH evaluator plus fresh claim/path collision scan over the exact five targets | allowed under active PAUTH v2 and no foreign collision; otherwise fail closed |
| Bridge applicability | exact candidate run through `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file .gtkb-state/propose-drafts/gtkb-wi6140-source-horizon-cycle-breaker-001.md` | `preflight_passed=true`, no missing required/advisory specs, no blockers |
| Clause applicability | exact candidate run through `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file .gtkb-state/propose-drafts/gtkb-wi6140-source-horizon-cycle-breaker-001.md` | exit 0; zero must-apply evidence gaps and zero blocking gaps |
| Post-file executability | independent reviewer runs `scripts/pre_verdict_executability_check.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --json` against the live report | `executable=true`, `gaps=[]` |
| Non-scope preservation | pre/post hashes and database/index/registry/claim/sidecar census | no database, registry, real-index, W0P, WI-5950, original-WI-6140, dispatcher, or TAFE mutation |

Historical `232 passed` evidence from the original chain is not an expected
fixed count. The implementation report must record the fresh count produced by
the then-current two-module run.

## Project Authorization

`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
version 2 is active and list-free over active project members. WI-6140 is an
active P0 project member with `resolution_status=open` and
`stage=backlogged`.

PAUTH v2 permits the source, test, test-addition, governance-evidence, and
bridge classes required by these exact targets. It forbids dispatcher
mutation, external-system mutation, credential lifecycle, push, history
rewrite, deployment, release, and destructive cleanup. It does not replace
this proposal, independent GO, exact claim, schema-v3 implementation start,
report, or independent atomic VERIFIED finalization.

## Prior Deliberations

- `DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`,
  rowid `14282`, content hash
  `d1357c38af43e1bf20e4007c19e348d29159369e44edcdd0d8da18258b44212c`
  — exact owner authority for this clean five-target carrier to take priority
  before WI-5950 without conflating the separate missing-read-context defect.
- `DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`,
  rowid `14277`, content hash
  `fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`
  — controlling ordinary sequence that resumes after this bounded inversion.
- `DELIB-20260808-WI6077-WI6081-LEAD-PRIME-COMPLETION-DIRECTIVE` — owner
  direction to drive the publication-recovery tranche to genuine completion.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-001.md` — original
  exact-source-horizon proposal and acceptance criteria.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-005.md` — retained
  patch hashes, historical tests, and isolation evidence.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-008.md` — current
  NO-GO routing evidence for the original chain; preserved for later
  disposition.
- `bridge/gtkb-wi5950-strict-terminal-recovery-016.md` — durable NO-GO evidence
  of the cycle requiring this separately governed carrier before WI-5950
  retries.
- `WI-6183` — separate protected-commit missing-PAUTH-read-context defect.
  This proposal neither implements nor claims to resolve it.

The unrelated scaffold-seeded intake records are pruned because they do not
authorize or constrain this exact five-target repair.

## Owner Decisions / Input

The owner expressly authorized this single dependency-order inversion in
`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`. The
directive to “independently GO, implement, and atomically VERIFY” is the narrow
serialized release for this carrier only. No additional owner decision is
required to present, review, implement, report, and independently verify this
exact carrier through ordinary governed gates.

The prior global numbered-bridge writer hold remains closed for all other
lanes. Independent Loyal Opposition GO remains mandatory before any
implementation mutation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-6140 source-horizon cycle-breaker v001 under DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION row 14282",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, and REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001 version 2",
  "primary_route": "row-14282 narrow serialized release, fresh proposal, independent GO, exact go_implementation claim and schema-v3 start, retained five-target patch, truthful report, and independent atomic VERIFIED",
  "before_behavior": "An explicit source at version N hashes an observed sibling cohort that anticipates N+1 before publication but N+2 after N+1 materializes, making unchanged source evidence self-invalidating.",
  "after_behavior": "An explicit canonical source at version N deterministically binds its prospective cohort to N and N+1 while real source, rules, target, PAUTH, and candidate drift remain independently detectable and fail closed.",
  "self_descriptive_naming": "source horizon, canonical content_file, source_version + 1, packet_hash, and candidate_evidence_hash directly identify the behavior and evidence boundary.",
  "obsolete_guidance_disposition": "The original WI-6140 chain remains immutable non-closing evidence for later row-14277 disposition; stale terminality claims, historical-test substitution, post-publication restamping, and observed-sibling N+2 synthesis are not carried forward.",
  "history_preservation": "All original WI-6140, WI-5950, WI-5953, and W0P numbered artifacts remain append-only and unchanged; row 14282 expressly authorizes this separate clean carrier despite the old-chain target duplicate.",
  "essential_context_preservation": "Preserve the exact five-target scope; both retained patch hashes and current preimages; canonical-source, rules, target, PAUTH, and candidate evidence binding; the old WI-6140 chain and all other target overlaps; the separate WI-6183 and WI-5950 missing-read-context defect; row-14277 sequencing after this carrier; W0P quarantine; database, registry, and real-index state; independent review; and governed atomic finalization while changing only the exact source-horizon implementation hunks.",
  "baseline": {
    "python_targets": {
      "scripts/bridge_applicability_preflight.py": "sha256:44a2ec7ccbc4e86a7e04693af1cc6048155c0364e4d725b606e5c2599aced2ae",
      "platform_tests/scripts/test_bridge_applicability_preflight.py": "sha256:bfd745633d176fba474b6c155d5f65f57acc0aa20ffb142461e0d37ca143ff27",
      "platform_tests/scripts/test_check_protected_commit_authorization.py": "sha256:eac5b1a586514626e42805417b5a80b2ddc8440bd19469df1ca421967c67e6de"
    },
    "retained_patches": {
      "source": "sha256:810d6cc9030a8e4b9427b62ef157fe13c1df55bd792cbbc0100facf59fb316b4",
      "tests": "sha256:ff5f00c8a0096fa96676e7b15b59875ba246b9f4224267a44cb55966e9fbe2bc"
    },
    "forward_apply_check": "PASS for both retained patches",
    "original_chain_status": "NO-GO v008",
    "writer_serialization": "released for this carrier only; held for every other numbered-bridge lane"
  },
  "expected_result": {
    "summary": "Terminalize one clean exact-source applicability-horizon cycle-breaker without absorbing the separate missing-read-context repair or any foreign state.",
    "scope": [
      "one applicability-preflight source module",
      "two focused test modules",
      "two retained cleanup-evidence patch files"
    ],
    "acceptance": [
      "explicit source N remains packet-hash invariant after N+1 materializes",
      "no synthetic N+2 sibling observation",
      "noncanonical fallback preserved",
      "source and candidate drift still fail independently",
      "fresh claim and target-overlap rechecks pass",
      "database, registry, real index, and all foreign state remain unchanged",
      "fresh independent atomic VERIFIED under governed Git lifecycle version 2"
    ]
  },
  "rollback": {
    "instructions": "Before terminal verification, reverse only the two exact retained implementation patches under the active governed claim and restore all five targets to their recorded preimages; do not alter the real index or delete historical evidence.",
    "verification": "Recompute all five hashes, rerun the focused matrix, and prove database, registry, real-index, W0P, WI-5950, original-WI-6140, dispatcher, and TAFE state unchanged."
  },
  "hard_invariants": [
    "exactly five implementation targets",
    "no KB, MemBase, or groundtruth.db mutation",
    "no registry or real-index mutation",
    "no conflation with WI-6183 or WI-5950 missing-read-context work",
    "row 14282 gives this clean carrier priority but does not waive fresh claim or path-collision checks",
    "independent GO and implementation-start gates remain mandatory",
    "no Prime Builder staging or self-review",
    "W0P remains quarantined non-closing evidence",
    "row-14277 sequence resumes only after this carrier terminalizes",
    "no dispatcher or legacy TAFE mutation",
    "all other numbered-bridge writer lanes remain held",
    "atomic independent VERIFIED only"
  ],
  "fail_closed_conditions": [
    "a numbered-bridge writer outside this carrier starts",
    "target or active-claim conflict",
    "proposal, GO, PAUTH, claim, packet, target, preimage, or patch-hash drift",
    "either retained patch no longer applies exactly",
    "old-chain or other target overlap is not preserved and freshly rechecked",
    "touched-path or hunk-count expansion",
    "source, candidate, or operation-time freshness failure",
    "database, real-index, registry, W0P, WI-5950, original-WI-6140, dispatcher, or TAFE drift",
    "test, Ruff, applicability, clause, executability, receipt, or finalization failure"
  ]
}
```

## Risk / Rollback

The primary behavioral risk is under-binding content that merely carries
plausible version metadata. Mitigation: the bounded horizon applies only when
the source is an explicit canonical numbered path; noncanonical content
retains the observed fallback, and dedicated tests cover both branches.

The primary overlap risk is allowing the old WI-6140 chain, historical WI-6042
work, or the later WI-6183/WI-5950 carrier to mutate a shared target
concurrently. Mitigation: row 14282 establishes this carrier's serialized
priority, all other writer lanes remain held, and fresh claim/path/index checks
must pass immediately before implementation.

The primary integration risk is that the retained patches were created against
an earlier tree. Both currently apply cleanly, but applicability alone does not
prove semantic compatibility. Mitigation: exact implementation-start
preimages, unchanged patch hashes, touched-path census, fresh full adjacent
tests, Ruff, candidate-aware gates, and independent review.

Before terminal verification, rollback is limited to reversing the two exact
implementation patches and restoring the five declared targets to their
recorded preimages. After atomic VERIFIED, any regression requires a new
governed append-only repair and ordinary revert commit under
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` version 2; history rewrite is forbidden.

## Bridge Filing

This proposal is the first status-bearing numbered file for
`gtkb-wi6140-source-horizon-cycle-breaker`. No original WI-6140, WI-5950,
WI-5953, or W0P artifact is deleted, rewritten, or treated as terminal.

The owner's row-14282 direction to “independently GO, implement, and atomically
VERIFY” is the narrow serialized numbered-writer release for this carrier only.
The prior global hold remains closed for all other numbered-bridge writer
lanes until a later explicit coordination release.

The numbered file chain, typed publication receipt, exact claim, and
implementation-start packet are the governed workflow evidence. The legacy
TAFE dispatcher remains disabled and is not invoked, enabled, repaired, or
used by this carrier.

## Recommended Commit Type

`fix` — the exact five-target delta repairs a reproduced self-invalidating
applicability-packet freshness defect while preserving existing authority,
candidate, review, overlap, and finalization semantics.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
