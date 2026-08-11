REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ff25c-fc0a-7181-825d-931e2a0440fa
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder subagent; read-only finalization-only proposal preparation; no claim, publication, implementation, index, database, registry, or TAFE mutation
author_metadata_source: live CODEX_THREAD_ID and explicit Prime Builder task assignment

bridge_kind: prime_proposal
Document: gtkb-adbr-t0-p6-githooks-taxonomy-classification
Version: 007
Date: 2026-08-11 UTC
Responds to NO-GO: bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-006.md
Original approved proposal: bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-001.md
Original GO: bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-002.md
Project Authorization: PAUTH-PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION-T0-T6
Project: PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION
Work Item: WI-6040
target_paths: ["config/governance/project-authorization-operation-taxonomy.toml", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]
implementation_scope: exact-byte adoption and finalization only; zero semantic or byte changes to the three implementation targets
kb_mutation_in_scope: false
database_mutation_in_scope: false
registry_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
requires_review: true
requires_verification: true
Recommended commit type: feat

# WI-6040 ADBR T0 P6 — Finalization-Only Authority Recovery

## Summary

Approve one append-only finalization-only lifecycle for the exact accepted
WI-6040 P6 implementation already present in the worktree. Independent v006
accepts the implementation substance and blocks terminal finalization because
the retained schema-v3 implementation-start packet was finalized under a
`draft` work-intent claim, not the `go_implementation` claim now required by
the protected-commit authorization checker. The retained packet is also
expired. Neither its recorded `implementation_start` object nor any retained
runtime sidecar can repair that claim-kind/currentness mismatch.

No source, test, or taxonomy reimplementation is proposed. After an
independent v008 `GO`, Prime Builder will acquire a fresh exact
`go_implementation` claim, mint and finalize a fresh schema-v3 packet bound to
v007/v008, PAUTH v6, the exact three targets, and their unchanged hashes, rerun
the approved evidence on those same bytes, and file v009 as a no-byte-change
implementation report. A different Loyal Opposition session may then issue
v010 `VERIFIED` only through one atomic scoped finalization transaction.

This proposal performs no KB, MemBase, or `groundtruth.db` mutation. It also
authorizes no PAUTH change, publication-receipt repair, registry change, real
index mutation during the Prime Builder phase, dispatcher action, legacy TAFE
action, push, deployment, release, or history rewrite.

## Response To V006 NO-GO

### F1 — Expired packet was finalized under the wrong claim kind

Accepted. The retained named packet
`sha256:6f8bb5542dfc542539d00ccb3c04087e6e7d3efe4ec4b6566ce4ae19656a9b23`
was created at `2026-08-11T04:08:22Z`, expired at
`2026-08-11T06:08:22Z`, and embeds work-intent `claim_kind: draft`. Its
`implementation_start` record proves an earlier start attempt; it does not
prove the current `go_implementation` authority required for a protected
terminal commit. Reusing, editing, extending, or treating that packet as
current is prohibited.

The correction is lifecycle-only:

1. independent v008 `GO` on this exact v007 proposal;
2. a new exact `go_implementation` claim held by the implementing Prime
   Builder session while v008 is latest;
3. a fresh schema-v3 `implementation_authorization.py begin` packet whose
   claim snapshot is exactly `go_implementation`, whose proposal/GO binding is
   v007/v008, and whose target set is exactly the three paths above;
4. no byte edit—only adoption of the already accepted candidate under that
   fresh authority;
5. receipt-complete v009 implementation report with fresh hashes and executed
   evidence; and
6. independent one-transaction v010 `VERIFIED` finalization, or a finding-
   specific `NO-GO` if any currentness or scope gate fails.

No stale packet, expired claim, retained sidecar, report statement, or owner
approval substitutes for those steps.

## Requirement Sufficiency

**Existing requirements sufficient.** The original owner decisions, v001
proposal, v002 independent GO, PAUTH v6, P6 implementation requirements, and
the current protected-commit claim-kind enforcement already define the needed
behavior. The three implementation targets satisfy that behavior and require
no new target, classifier behavior, taxonomy rule, packet schema, PAUTH class,
waiver, or bypass. This proposal supplies only a current proposal/GO/claim/
packet/report chain for exact-byte adoption and atomic finalization.

## Exact Immutable Lineage And Receipt Readback

| Version | Status | SHA-256 | Bytes | Typed receipt |
| --- | --- | --- | ---: | --- |
| v001 | NEW proposal | `DC1EB9EA1A5A883E174F7C2EECD34B1EF201DC10E61BA6339BF2C6648479F53B` | 18,446 | row 1858 consumed; result `sha256:f14e6ab6be4d810866363ced21014442dc01e8316091ee9157dd9abde6072d54`; revision `SOTREV-B12F33E4DA014A70AD004700FFA73635`; failure/compensation null |
| v002 | GO | `A4A1867CF620AE5F122BED37A5438C5AA5AB9B577E268D90A940F6AF245DA053` | 8,667 | row 1871 consumed; result `sha256:0eecc759192816a1d5dae711213a5cf5b92d58921ed4cc94540779ca1fca44e7`; revision `SOTREV-67F5BE460D8B4CA788F8A6A4E575E59B`; failure/compensation null |
| v003 | NEW implementation report | `4566ADF9CFCF2FE873A6AD026F289BBDF570FEB7972FA22A3F297396672666FE` | 12,780 | row 1912 consumed; result `sha256:7e96910d2c3fc8fda9cca5e16b675d5f287a0fdef63deb2d8b2f0356bbad5055`; revision `SOTREV-EBA68747BE6C4D2AB1FD10F18B69C8A9`; failure/compensation null |
| v004 | NO-GO | `7448E46EE56646E1D3D1C7EDF65090D1C569044BBE334029CCE3BADB200F916A` | 12,366 | row 2009 consumed; result `sha256:0907308ed18f93be4b743b2e307bf9cffc8d7162b19186fe9ed299f4e0466cf7`; revision `SOTREV-27E262F4A3EF483F9A43869A301014FF`; failure/compensation null |
| v005 | REVISED implementation report | `7FD7ABD7648DB00CCDD6D8E278B59613FB63E81438F4F7DDB00A3E29596E4DF9` | 12,708 | row 2139 consumed; result `sha256:0d17431e7a97a4d335bc58b733ebf9c1147f2119ecf75e2e0ea4db468330dda2`; revision `SOTREV-5846C75E6B1A4128902CB26D63107AA3`; failure/compensation null |
| v006 | NO-GO | `511076D347441D9B8E1620834A9F8AC1968D5ECFBE359D378B11242ABE76A77A` | 23,102 | row 2189 consumed; capability `sha256:325222722167b573c57645b2d932a7b4bc8816a82c8dcb4ef8db2dabc3d6d4c3`; result `sha256:1a7766471a75f6ef3e29c210b97e85080624d970d83778c5aead450a027502d2`; revision `SOTREV-42D91EB3FF854EDA94DB71E5DCAEE660`; failure/compensation null |

The one retained v004 publication sidecar names the same v004 content digest
and already-consumed row-2009 capability. It is disclosed as non-authoritative
runtime evidence only. V007 neither removes nor recovers it, and it cannot
supply a current claim or implementation-start packet. If a fresh finalizer
classifies that residue as blocking, it must fail closed and route a separate
governed recovery rather than deleting or bypassing it.

## Current PAUTH And Historical Packet Boundary

Fresh canonical `gt projects show-authorization` readback reports PAUTH
`PAUTH-PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION-T0-T6` version 6,
row 1035, active with no expiry, project
`PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION`, included work item
`WI-6040`, and included specification
`GOV-AGENT-DIRECTION-BASELINE-REMEDIATION-ACCEPTANCE-001`. Its allowed
mutation classes are source, test, config, configuration,
governance_evidence, metadata, repository_metadata, and bridge. Its forbidden
operation remains `dispatcher_mutation`. The owner-decision anchor is
`DELIB-20260809-ADBR-T0-P6-002`.

The expired historical packet remains immutable evidence:

- packet: `sha256:6f8bb5542dfc542539d00ccb3c04087e6e7d3efe4ec4b6566ce4ae19656a9b23`;
- pre-start: `sha256:a797cc421c0825f62576b293b282f4f69c96f3f290e8199a2af6b5b9d9ed879b`;
- created/expires: `2026-08-11T04:08:22Z` / `2026-08-11T06:08:22Z`;
- proposal/GO: v001/v002;
- recovery provenance: report v003 and NO-GO v004;
- session: `019fe0ce-9579-7112-8541-442ef77f18c0`;
- embedded claim: acquired `2026-08-11T04:00:18Z`, `claim_kind: draft`;
  v005 identifies the underlying work-intent row as 37998;
- exact targets: the same three paths declared by this proposal;
- taxonomy: v2 SHA-256
  `C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450`;
- evaluator: SHA-256
  `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`.

It must not be overwritten by a draft-authority begin attempt. Only the
post-v008 Prime Builder session holding the exact current `go_implementation`
claim may create the replacement named packet.

## Exact No-Byte-Change Candidate Ledger

| Path | HEAD blob / bytes | Exact candidate blob / bytes | Candidate SHA-256 | Diff from HEAD |
| --- | --- | --- | --- | ---: |
| `config/governance/project-authorization-operation-taxonomy.toml` | `f2f34f23495e4d64ad8a535fd40da5ff78590666` / 3,816 | `3db0803a58c6f9a475d6a7d43ab7a6aa8894f825` / 3,889 | `C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450` | +5/-1 |
| `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py` | `95b0c0f93352a4cc5569c86bd7a66ef628b3312e` / 14,516 | `1aaf8c20423a2fef375e5865142ae44ab784457e` / 17,307 | `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42` | +59/-1 |
| `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py` | `e79c868d67da79e1ac0fe6258f70be4736eae52b` / 8,630 | `41000b68934eb146095c53c4b0f81f3f77fec2b9` / 11,385 | `14971314109C40F057BF832B583B28A7B7E6065FEF05301839A187EC6471A076` | +60/-0 |

The exact candidate delta is 124 insertions and 2 deletions across only these
three unstaged targets. It implements taxonomy version 2, the single
root-relative `.githooks/**` to `configuration` rule, governed path-rule
loading/validation, slash-normalized classification, and fail-closed
cross-class overlap behavior. V007 authorizes no normalization, formatting,
line-ending change, comment edit, test edit, or semantic revision.

Any candidate hash, blob, byte count, numstat, or hunk drift before the fresh
start packet or v009 report blocks adoption and requires a new Prime Builder
revision. The finalization-only route must never silently substitute an
equivalent reimplementation.

## Proposed Lifecycle And No-Byte Implementation

1. Publish v007 only after v006 is physical, receipt-complete, and fresh-read,
   and after replacing the two explicit v006 readback markers above.
2. Obtain independent v008 `GO` from a session context unrelated to this
   proposal author and the later implementing session.
3. With v008 latest, acquire a fresh exact `go_implementation` work-intent
   claim for this slug. Confirm its project is the ADBR project, its WI is
   WI-6040, it is unexpired, and its implementation deadline/grace are live.
4. Run exactly one current `implementation_authorization.py begin` sequence
   under that claim. Require a schema-v3 packet binding v007, v008, PAUTH v6,
   the exact three targets, the current taxonomy/evaluator hashes, the
   implementing session, and `claim_kind: go_implementation`.
5. Validate all three targets against that packet. Make no target edit.
   Exact-byte adoption under the fresh authority is the implementation action.
6. Rerun the full approved focused and static matrix with hashes stable before
   and after. File v009 `NEW` implementation report with the new packet,
   claim, hashes, tests, receipt lineage, current HEAD/index census, and exact
   finalization manifest.
7. Release the Prime implementation claim only through the ordinary
   receipt-complete report/finalization lifecycle. Do not self-review.
8. Route v009 to a fresh independent Loyal Opposition session. That session
   may create v010 `VERIFIED` only through the governed atomic finalizer over
   the exact cohort below. Any denial produces v010 `NO-GO`; no second
   finalizer call follows without fresh reconciliation and authority.

## Phase-Specific Real-Index Invariant

The real-index rule differs by lifecycle phase and must not be overstated:

### Prime Builder proposal, start, adoption, testing, and report phase

- The real index is immutable. Its pre-proposal SHA-256 is
  `B8E7BB45F3526EBBA4FF586879B4890706F95526A666F45F0083936110DC4791`
  at HEAD `de467cbc93bbad9f8d826ffd9fa96733f76c504a`.
- Exactly two foreign cached entries exist, both mode 100644, stage 0, blob
  `d4a1aca0e15172acad63f218f32c9814b2055677`:
  `config/registry/sot-artifacts.toml` and
  `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`.
- The three WI-6040 targets remain unstaged. Prime Builder may not stage,
  reset, realign, or otherwise mutate any index entry while acquiring the
  claim, minting the packet, adopting unchanged bytes, testing, or filing
  v009.
- Any real-index SHA or cached-entry drift during this phase fails closed.

### Independent atomic VERIFIED finalization phase

- The finalizer may use a disposable/copy index and may perform the narrowly
  governed committed-cohort realignment needed after a successful commit.
- A successful commit can legitimately change the whole real-index SHA because
  the three now-committed WI-6040 entries are realigned to new HEAD. Therefore
  whole-index SHA equality is not a post-commit invariant.
- Every non-cohort entry must remain entry-identical. In particular, both
  foreign registry entries must remain mode 100644, stage 0, blob
  `d4a1aca0e15172acad63f218f32c9814b2055677`, and must remain the only cached
  diff paths after successful finalization.
- Failed finalization must restore the real index exactly to its pre-attempt
  bytes and preserve every foreign entry. No broad add, reset, checkout,
  commit, or index replacement is allowed.

## Specification Links

- `GOV-AGENT-DIRECTION-BASELINE-REMEDIATION-ACCEPTANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Plan

| Requirement / specification group | Executed evidence required after v008 GO | Expected result |
| --- | --- | --- |
| P6 owner decision and `GOV-AGENT-DIRECTION-BASELINE-REMEDIATION-ACCEPTANCE-001` | Complete focused operation-time test module and direct classifier assertions | 20/20 pass; `.githooks/pre-commit` and backslash form classify as exactly `configuration`; nested lookalike remains `unclassified` |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` and envelope/no-bypass requirements | Fresh claim status, fresh schema-v3 begin packet, three exact target validations, malformed/duplicate/unknown/non-root/overlap tests | packet embeds current `go_implementation` claim and PAUTH v6; all targets allowed; invalid or ambiguous rules fail closed |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Direct canonical PAUTH CLI read plus packet taxonomy/evaluator hashes | current PAUTH v6, taxonomy v2 and exact accepted evaluator; no cached authority substitute |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Hash/blob/size/numstat census before and after tests; complete focused module | zero candidate drift; all prior classifications remain green |
| Bridge/linkage/lifecycle requirements | Pending-content applicability and clause checks on final v007/v009; live executability after each receipt-complete file | no missing required/advisory specs, no blocking clause gaps, executable lifecycle |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` and `GOV-WORK-TREE-HYGIENE-001` | phase-specific HEAD/index/stage census plus finalizer exact include set | Prime phase leaves real index byte-identical; terminal phase changes only cohort alignment and preserves every foreign entry |
| Python quality | Ruff check, Ruff format check, in-memory compile, and `git diff --check` | all pass on unchanged targets |

Required commands after v008 GO and fresh packet:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification --target-path config/governance/project-authorization-operation-taxonomy.toml
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification --target-path groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification --target-path groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification
python scripts/pre_verdict_executability_check.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification --json
git diff --check -- config/governance/project-authorization-operation-taxonomy.toml groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
```

The implementation report must also execute in-memory `compile(..., "exec")`
for the two Python targets without creating bytecode and report exact stable
SHA-256/blob/size results. It must not replace the complete focused module with
selected-node or direct-classifier evidence.

## Current Read-Only Baseline

The finalization-only proposal preparation reran the complete focused module
against the exact candidate: `20 passed in 0.41s`. Ruff lint returned
`All checks passed!`; Ruff format reported `2 files already formatted`;
in-memory compilation passed; `git diff --check` exited 0. The target hashes,
HEAD, real-index SHA, and foreign stage entries remained unchanged. These are
proposal-baseline observations only. V009 must rerun and bind fresh post-v008
evidence; v010 verification must independently rerun the specification-derived
matrix.

## Finalization Manifest

Before the independent verdict, the exact pre-v010 include set is twelve
paths:

1. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-001.md`
2. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-002.md`
3. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-003.md`
4. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-004.md`
5. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-005.md`
6. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-006.md`
7. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-007.md`
8. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-008.md`
9. `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-009.md`
10. `config/governance/project-authorization-operation-taxonomy.toml`
11. `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
12. `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`

The atomic finalizer creates v010 and commits exactly thirteen paths. No hunk
patch is required because the exact three target worktree bytes are the
candidate to adopt. The finalizer must exclude the retained runtime packet and
sidecar, `groundtruth.db`, both registry worktree/index entries, WI-6183,
WI-6140, WI-5950, W0P, every other bridge thread, dispatcher state, and legacy
TAFE state.

## Acceptance Criteria

1. V006 is receipt-complete and its exact physical SHA/receipt replace the two
   explicit markers before v007 filing; all earlier numbered files remain
   immutable.
2. Independent v008 GO accepts this finalization-only route before any new
   packet or implementation action.
3. The implementing session holds an unexpired exact `go_implementation`
   claim and the fresh schema-v3 packet embeds that exact claim kind, session,
   v007/v008 authority, PAUTH v6, and exactly three targets.
4. The three target blobs, SHA-256 hashes, byte counts, numstat, and hunks do
   not change during the entire Prime Builder cycle.
5. The complete 20-test module, Ruff lint, Ruff format, in-memory compile,
   `git diff --check`, target validations, applicability, clause, and live
   executability gates pass with fresh evidence.
6. V009 is a receipt-complete no-byte-change implementation report and carries
   exact claim/packet/target/index/receipt evidence before independent review.
7. Prime Builder leaves the real index byte-identical. Independent terminal
   finalization preserves every non-cohort entry exactly; whole-index SHA may
   change only after successful exact-cohort commit realignment.
8. V010 VERIFIED exists only in the same successful transaction as the exact
   thirteen-path commit. A failed finalizer leaves no terminal verdict and
   restores the pre-attempt index/HEAD boundary.
9. No PAUTH, receipt, database, registry, foreign index, WI-6183, WI-6140,
   WI-5950, W0P, dispatcher, legacy TAFE, credential, push, deployment,
   release, or history-rewrite action occurs.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260809-ADBR-T0-P6-001; DELIB-20260809-ADBR-T0-P6-002; WI-6040; bridge v001-v006",
  "canonical_authority": "The numbered bridge chain, current PAUTH v6 canonical readback, current claim registry, and a fresh schema-v3 implementation-start packet jointly authorize finalization; no stale packet or sidecar is authority.",
  "primary_route": "REVISED finalization-only proposal, independent GO, fresh go_implementation claim, fresh schema-v3 packet, no-byte adoption report, independent atomic VERIFIED.",
  "before_behavior": "The accepted P6 bytes are green, but the retained expired packet embeds claim_kind draft and therefore cannot authorize protected finalization.",
  "after_behavior": "The same exact P6 bytes are adopted under a current GO plus go_implementation claim and packet, then independently committed with the complete numbered chain.",
  "self_descriptive_naming": "Finalization-only authority recovery, exact candidate ledger, phase-specific index invariant, and no-byte adoption describe the bounded operation directly.",
  "obsolete_guidance_disposition": "The earlier report/resumption route and expired draft-claim packet remain immutable historical evidence and are not reused as current authority.",
  "history_preservation": "V001-v006, their typed receipts, the old packet, and retained sidecar remain disclosed and unmodified; v007-v010 append the corrected lifecycle.",
  "baseline": {
    "target_hashes": "C0DA3311...EE450, F67A2F9...BF42, 14971314...1A076",
    "focused_tests": "20 passed",
    "old_packet": "sha256:6f8bb554...a9b23; expired; claim_kind draft",
    "head": "de467cbc93bbad9f8d826ffd9fa96733f76c504a",
    "real_index": "sha256:B8E7BB45F3526EBBA4FF586879B4890706F95526A666F45F0083936110DC4791"
  },
  "expected_result": {
    "candidate": "byte-identical",
    "authority": "fresh v007/v008-bound schema-v3 packet with claim_kind go_implementation",
    "terminal_state": "independent v010 VERIFIED and exact thirteen-path commit in one transaction"
  },
  "rollback": {
    "before_verified": "Make no target edit; if any gate fails, preserve the exact candidate and issue a finding-specific bridge response.",
    "after_verified": "Use a separate governed inverse commit; never rewrite the numbered chain or receipt history."
  },
  "hard_invariants": [
    "Zero semantic or byte change to the exact three P6 targets during this cycle.",
    "Fresh independent GO, go_implementation claim, and schema-v3 packet precede adoption/report.",
    "Prime Builder leaves the real index byte-identical.",
    "Atomic finalization preserves every non-cohort index entry exactly.",
    "No PAUTH, receipt, database, registry, dispatcher, or legacy TAFE bypass or mutation."
  ],
  "fail_closed_conditions": [
    "V006 is absent, unconsumed, or differs from the exact prefile readback.",
    "Candidate hash, blob, bytes, hunks, or target set drift.",
    "Claim kind is not exactly go_implementation or is expired/lapsed/mismatched.",
    "Packet does not bind v007/v008, PAUTH v6, exact session, and exact three targets.",
    "Any mapped test, applicability, clause, executability, receipt, aggregate-currentness, or finalizer gate fails.",
    "Any foreign index entry, database, registry, WI-6183, WI-6140, WI-5950, W0P, dispatcher, or TAFE path enters the cohort."
  ],
  "essential_context_preservation": "The proposal preserves the owner-approved P6 behavior, exact three-target bytes and tests, immutable v001-v006 chain and receipts, PAUTH v6 scope and dispatcher prohibition, expired draft-claim packet as non-authority, fresh GO-to-go_implementation lifecycle, corrected phase-specific index semantics, foreign registry staging, independent review, and atomic terminal commit requirement."
}
```

## Owner Decisions / Input

- `DELIB-20260809-ADBR-T0-P6-001`, row 14090, content hash
  `213d1759bac7f2f99c09d412dcb2b8615861192b7fe96bf6a672600b3172a4ed`
  — approves the bounded `.githooks/**` taxonomy classification slice while
  preserving ordinary GO, exact target, claim, and implementation-start gates.
- `DELIB-20260809-ADBR-T0-P6-002` — approves only the PAUTH v6 addition of
  canonical `bridge` for lawful P6 cohort finalization while preserving the
  project, WI, spec, active/no-expiry state, earlier classes, plan guard, and
  dispatcher-mutation prohibition.

No additional owner decision, waiver, or scope expansion is required. The
owner has separately required legacy TAFE to remain disabled and untouched;
this proposal preserves that boundary.

## Prior Deliberations

- `DELIB-20260809-ADBR-T0-P6-001` — original bounded P6 owner approval.
- `DELIB-20260809-ADBR-T0-P6-002` — narrow PAUTH v6 correction.
- `DELIB-20260808012149` — v004 independent NO-GO that required restoration of
  the exact accepted P6 bytes; v005 satisfied it.
- `bridge/gtkb-adbr-t0-p6-githooks-taxonomy-classification-001.md` through
  `-006.md` — complete immutable proposal, GO, reports, and independent
  findings preceding this finalization-only carrier.
- `bridge/gtkb-adbr-t0-mechanism-repair-003.md` through `-006.md` — parent T0
  sequencing and P6 dependency evidence.

The fresh bounded deliberation search found no later owner decision that
widens P6 or authorizes reuse of a draft-claim packet.

## Risk And Rollback

The implementation behavior risk is already bounded by the complete 20-test
module and exact accepted hashes. The remaining risk is authority/currentness:
a stale claim, wrong claim kind, packet drift, receipt residue, aggregate drift,
or index collision could make an otherwise correct terminal commit unlawful.
The lifecycle deliberately fails closed at each boundary and permits no retry
or cleanup by inference.

Before VERIFIED, rollback is no action: preserve the exact three candidate
bytes and append a finding-specific bridge response. After VERIFIED, any
behavioral rollback requires a separate governed inverse commit over the three
implementation paths and fresh verification. No rollback rewrites bridge
history, edits typed receipts, mutates PAUTH/database/registry state, resets
foreign index entries, or invokes legacy TAFE.

## Pre-Filing Preflight

This is a non-live read-only draft. Before governed filing, the owning Prime
Builder session must fresh-read physical and typed v006, replace exactly the
two explicit v006 markers, then run path-bound LF-normalized applicability and
clause checks against the final candidate bytes using `--content-file`. It
must confirm no placeholder remains, direct bridge compliance passes, the
latest live status is v006 `NO-GO`, v007 is absent, the matching draft claim
belongs to the publishing session, all numbered writers are serialized, no
minted publication is pending, and bridge aggregate currentness is stable.

No pre-publication live executability claim is made for v007 because that
checker resolves the live numbered file. Independent Loyal Opposition must
run it after v007 is receipt-complete and before authoring v008.

## Loyal Opposition Request

Fresh-read v001-v007, every typed receipt, PAUTH v6, the expired historical
packet, current claim state, exact target bytes, current HEAD/index/stage
census, and final v007 pending-content gates. If this lifecycle-only proposal
is complete and executable, issue v008 `GO`. Do not treat GO as terminal
authority: Prime Builder must still obtain the fresh `go_implementation`
claim and schema-v3 packet, file v009, and route that report to a different
independent terminal reviewer.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
