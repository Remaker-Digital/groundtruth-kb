REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex desktop; owner-designated Prime Builder; manual physical-bridge processing with dispatcher disabled
author_metadata_source: explicit_interactive_session_metadata

# WI-5291 By-Reference Finalization Recovery v2 — Evidence-Only Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5291-by-reference-finalization-recovery-v2
Version: 003
Date: 2026-08-01 UTC

Responds to: bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-002.md
Approved proposal: bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5291

target_paths: ["bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_activation_in_scope: false
source_or_test_mutation_in_scope: false

## Implementation Claim

The evidence-only implementation authorized by strict GO v002 has been
re-derived against current HEAD `75decbfa704fe50288aecbc5669def329a0825df`.
No source, test, configuration, MemBase, dispatcher/TAFE, Git/index, release,
deployment, credential, external-system, history, or cleanup mutation was
performed. The only prospective live artifact in this report's implementation
scope is this numbered v003 bridge report.

The two immutable implementation subjects remain clean, tracked, byte-identical
to their historical independently reviewed post-normalization content, and
explicitly outside both `target_paths` and every prospective finalization
include set:

- `platform_tests/scripts/test_check_artifact_evaluability.py`
- `platform_tests/scripts/test_modernization_authority_foundations.py`

Current evidence does **not** support an all-green verification claim. The
focused 17-test command reports 14 passed and 3 failures caused by later
governance-state changes, while the broad release Ruff command reports ten
findings in four unrelated platform-test files. This report preserves those
results for independent fail-closed review.

## Live Filing Authority Evidence

Immediately before this final candidate was prepared for governed publication,
the acting Prime Builder revalidated exact v002 `GO` and its SHA-256, acquired
the exact `go_implementation` claim, and created the schema-v3
implementation-start packet for only
`bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md`.

- Claim row: `36126`; session
  `019fb19b-7814-73c1-8707-204e432cbf00`; acting role `prime-builder`;
  project `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`.
- Claim acquired: `2026-08-01T16:58:34Z`; implementation deadline
  `2026-08-01T17:28:34Z`; grace/TTL expiry `2026-08-01T17:38:34Z`.
- Schema-v3 packet created/finalized: `2026-08-01T17:01:58Z`; expires
  `2026-08-01T19:01:58Z`.
- Packet hash:
  `sha256:bb499ec9fa06ff78733a976e69890701f920966e5339e74b0715ce02974ba6ce`.
- Pre-start packet hash:
  `sha256:0ab462107d36c97e63ad4ee4473f1dc6b3d44bd1a2d8b35f8dba7c06df50ae2f`.
- Operation-time evaluator: version 1, SHA-256
  `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`;
  taxonomy version 1, SHA-256
  `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`.
- Decision: `allowed=true` for normalized operation `implementation_start`;
  the sole classified target is mutation class `bridge` at the exact v003
  path above.

No subject-file or historical-chain mutation was performed under this packet.
The governed writer must release the exact claim only after receipt-complete
publication; a failed publication remains subject to its typed compensation
and recovery contract.

## Current GO, Project, PAUTH, And Work-Item Evidence

- `gt bridge show gtkb-wi5291-by-reference-finalization-recovery-v2 --json --compact`
  resolved exactly two versions with latest status `GO` at
  `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-002.md`.
- Strict `resolve_bridge_lifecycle(...)` classified v001 as Prime Builder
  `NEW`, v002 as Loyal Opposition `GO`, found no quarantined path or blocking
  diagnostic, and selected v002 as the implementation verdict.
- Physical SHA-256:
  - v001: `09991B9C2F7A80AEDFCCCB6652C748111EE6FC4544FA96DD4B70A1437D78D2ED`
  - v002 GO: `21CF99CC407EDB2268CB5D4911085C4E556AA078494FB316D523BED515A67282`
- The GO reviewer session
  `f6fdf2cc-a0b3-4796-9689-3aa63e9514c0` is distinct from the v001 author
  session `019fb353-983b-7383-b57e-3b9fc6410af5`.
- Canonical project read: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` is
  active at version 2 with no `completed_at` value.
- Canonical membership read: WI-5291 has active member relationship
  `PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5291`; the work item is
  open/backlogged at priority P0.
- Canonical PAUTH read:
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  is active, version 5, unexpired, list-free for active project members, and
  allows bridge/governance-evidence work. It continues to forbid credential
  lifecycle, destructive cleanup, dispatcher mutation, external mutation, Git
  history rewrite, Git push, production deployment, and release.
- The legacy work-item `approval_state: unapproved` is compatibility metadata,
  not operation-time authority. Current authority is the active project
  membership plus active project PAUTH, exact GO, exact claim, and schema-v3
  start packet recorded above.

## Owner Decisions / Input

`DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL` is a live version-1 owner
decision linked to WI-5291. It expressly approves the bounded by-reference
bridge-only finalization path, preserves all normal gates, excludes both subject
tests from mutation/staging/commit, and excludes direct legacy approval-state
mutation, broad Git operations, dispatcher/TAFE action, push, release,
deployment, credentials, external mutation, history rewrite, and destructive
cleanup.

The decision's literal instruction to leave the subjects `untracked` was
already stale when recovery-v2 v001 reconciled current state: broad custodial
commit `42a252ab...` had tracked them on 2026-07-16. Current strict GO v002
approved the conservative interpretation used here: preserve the current clean
tracked blobs, perform no destructive untracking or history rewrite, and keep
both subjects outside this recovery transaction.

No broader owner authority is claimed.

## By-Reference Finalization Waiver

The owner expressly authorizes the **by-reference finalization waiver** in
`DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL`.

The following immutable implementation subjects are evidence by reference and
MUST NOT be modified, restored, staged, recommitted, or included in the recovery
transaction:

- `platform_tests/scripts/test_check_artifact_evaluability.py`
- `platform_tests/scripts/test_modernization_authority_foundations.py`

The waiver changes only finalization mechanics. It does not waive current
evidence collection, specification linkage, specification-derived testing,
review independence, exact include-set checks, commit-first ordering, or
fail-closed treatment of current test and broad-lint drift.

## Historical-Chain Quarantine And Recovery-Chain Currentness

The historical slug
`gtkb-wi5291-modernization-candidate-lint-normalization` remains unchanged.
Strict lifecycle resolution still fails at its physical v003 because metadata
`Version: 003 (NEW; post-implementation report)` does not exactly equal `003`.
Physical v006 remains untracked with SHA-256
`DC76F42F4AA3607315FDC54A69062BCE63633A52A2CB4D212BE187FA7B882C28`.
No historical version was edited, deleted, renamed, hidden, or reinterpreted.

The recovery-v2 controller resolves strictly through current GO v002. This
report does not absorb the historical parser defect or depend on unapproved
parser-relaxation work.

## Immutable Subject Identity And Ancestry

At current HEAD `75decbfa704fe50288aecbc5669def329a0825df`:

| Subject | Index/HEAD blob | Raw SHA-256 | Normalized AST SHA-256 | State |
| --- | --- | --- | --- | --- |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | `3799fa92a02c6d22c63f7b59fa7ff88163cf0e16` | `69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67` | `3F04D3D21F2088A3FE0D9501E168991B6DD02A61D902B71499F60E86E156FCED` | tracked, clean, unstaged |
| `platform_tests/scripts/test_modernization_authority_foundations.py` | `0e81f08b37bfce991f28ae9d32bbb68e0b52fc08` | `40DA822E7B7E2F4EFDE6BDEB42907F0F7103B3C2A5087C21881EEFDD2363A807` | `562D9405BD86FA2E7C1E97037BF796EECFF59D59938993E45D9B7B23F37E58DD` | tracked, clean, unstaged |

Both blob/raw/AST identities exactly match v001 and the independently reviewed
historical v003-v004 evidence. Commit
`42a252ab57b5a203e9406b626c741d897e8fb196` (`chore(gtkb): sweep governable
platform work`, 2026-07-16T16:07:12-07:00) is an ancestor of current HEAD,
changed 916 paths, contains both subjects, and carries the same two blob IDs.
It remains broad custodial provenance, not a scoped WI-5291 terminal commit.

## Commands Run And Observed Results

1. `gt bridge show gtkb-wi5291-by-reference-finalization-recovery-v2 --json --compact`
   - PASS: version count 2; latest v002 `GO`.
2. Strict `resolve_bridge_lifecycle(Path('.'), 'gtkb-wi5291-by-reference-finalization-recovery-v2')`
   - PASS: strict NEW v001 to strict GO v002; correct roles and adjacent
     `Responds to`; no quarantine or blocking diagnostic.
3. `gt backlog show WI-5291 --json`; canonical project/PAUTH reads via
   `gt projects show PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE --json`
   - PASS: active project, active WI membership, active/unexpired v5 PAUTH.
4. `gt deliberations show DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL --json`
   - PASS: version 1, owner_decision, linked to WI-5291, clean redaction state.
5. `git ls-files --stage -- <both subjects>` plus worktree/index diff probes
   - PASS: exact blobs above; no worktree diff; no staged diff; scoped status
     empty.
6. `Get-FileHash -Algorithm SHA256 <both subjects>` and normalized
   `ast.dump(..., include_attributes=False)` SHA-256 script
   - PASS: all four identities exactly match the table above.
7. `git merge-base --is-ancestor 42a252ab... HEAD`; `git diff-tree
   --no-commit-id --name-only -r 42a252ab...`; `git ls-tree 42a252ab... --
   <both subjects>`
   - PASS: ancestor exit 0; 916 changed paths; both subject entries present at
     the exact current blobs.
8. `python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py
   platform_tests/scripts/test_modernization_authority_foundations.py -q
   --tb=short` with pytest's cacheprovider plugin disabled
   - CURRENT DRIFT: 17 collected, 14 passed, 3 failed in 12.57s.
   - Failure 1: `GOV-SESSION-ROLE-AUTHORITY-001` has retired/non-current status
     and an outer assertion without an id.
   - Failure 2: the same retired carrier has no enforcement-source paths.
   - Failure 3: `GOV-SESSION-ROLE-AUTHORITY-001` evaluates
     `UNASSESSED (zero-executable)` and `DCL-SESSION-ROLE-RESOLUTION-001`
     evaluates `FAIL (never-pass)`.
   - All 14 tests in `test_check_artifact_evaluability.py` passed; the three
     failures are current authority-state assertions in the second immutable
     subject, not a subject-byte change.
9. `python -m ruff check <both subjects> --select E,F --ignore E501,E741`
   - PASS: `All checks passed!`
10. `python -m ruff format --check <both subjects>`
    - PASS: `2 files already formatted`.
11. `git diff --check -- <both subjects>`
    - PASS: exit 0, no output.
12. `python -m ruff check applications/Agent_Red/src/
    applications/Agent_Red/tests/ platform_tests/ --select E,F --ignore
    E501,E741`
    - CURRENT BROAD DRIFT: exit 1 with ten non-target findings:
      - one F401 in
        `platform_tests/scripts/test_bridge_applicability_preflight_gfr_slice_a.py`;
      - four F401 and three F841 findings in
        `platform_tests/scripts/test_dispatcher_generation_admission.py`;
      - one F401 in
        `platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py`;
      - one F401 in
        `platform_tests/scripts/test_parity_strict_on_rename.py`.
    - Neither immutable WI-5291 subject appears in the findings.
13. Strict resolver on the quarantined historical slug
    - EXPECTED FAIL-CLOSED: exact malformed v003 Version metadata diagnostic;
      no recovery-v2 authority is derived from that chain.
14. Exact work-intent acquisition for this recovery slug and PB session
    - PASS: `go_implementation` row 36126; active project/role/session binding;
      implementation deadline and grace recorded in `Live Filing Authority
      Evidence`.
15. `python scripts/implementation_authorization.py begin --bridge-id
    gtkb-wi5291-by-reference-finalization-recovery-v2 --session-id
    019fb19b-7814-73c1-8707-204e432cbf00`
    - PASS: schema v3; packet and pre-start hashes recorded above;
      operation-time `implementation_start` allowed for the sole v003 bridge
      target.

## Specification Links

- `GOV-CODE-QUALITY-BASELINE-001`
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

spec_to_test_evidence: Executed=yes

| Specification | Executed | Test / evidence | Observed result |
| --- | --- | --- | --- |
| `GOV-CODE-QUALITY-BASELINE-001` | yes | Target Ruff E/F, target Ruff format, scoped `git diff --check`, broad release Ruff | Target gates pass; broad gate truthfully reports ten non-target findings. |
| `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` | yes | Same target and broad Ruff commands | Default quality floor was executed without suppressing current broad drift. |
| `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` | yes | Target Ruff/format plus waiver inspection | No code-quality waiver is used; by-reference waiver affects finalization mechanics only. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | yes | Blob/raw/AST identity, scoped Git state, focused pytest | Subject identities and clean state match reviewed evidence; later authority-state failures are disclosed. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | yes | Focused 17-test command | 14 pass/3 current authority-state failures; independent verification must fail closed unless those outcomes satisfy the governing floor. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | yes | Candidate applicability and clause preflights on this exact draft | Recorded in `Pre-Filing Gate Evidence`; no omitted required/advisory specification or blocking clause gap is accepted. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | yes | Full links above plus project read | Active project/WI membership and full proposal-carried links are present. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | yes | Canonical project/PAUTH read | PAUTH v5 is active/unexpired and admits bridge/governance-evidence scope; claim/start remain publication prerequisites. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | yes | Candidate applicability PAUTH evaluator | Operation-time report-phase result recorded below; no legacy WI label is used as authority. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | yes | Exact PAUTH/project/WI/target metadata and canonical read | Envelope is exact and list-free project membership applies without broadening the sole target. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | yes | Strict GO resolver and draft-state gate | No live report, source/test edit, or terminal action occurred without GO/claim/start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | yes | Strict recovery resolver; historical resolver; physical hashes | Recovery chain is strict/current; old malformed chain remains append-only quarantine evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | yes | Machine-readable PAUTH/Project/WI lines | Exact linkage is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | yes | Full carried-forward links and candidate applicability | All required and advisory links are present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | yes | This mapping plus commands 1-15 | Every linked spec has executed evidence and observed results; no failed result is concealed. |
| `GOV-WORK-TREE-HYGIENE-001` | yes | Scoped target status/diff and prospective include census | Subjects remain clean/unstaged; only the exact bridge cohort is eligible for later terminal finalization. |
| `GOV-STANDING-BACKLOG-001` | yes | `gt backlog show WI-5291 --json` | Canonical WI remains open/backlogged; no KB lifecycle mutation occurred. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | yes | Owner DELIB read; old/new bridge inventories | Decision and recovery evidence remain durable, explicit artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | yes | Same deliberation/bridge evidence | No transient assertion replaces governed evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | yes | GO -> evidence report -> independent verification sequence | This report requests independent verification and does not self-assert terminal status. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | yes | Resolved subject, bridge, draft, project, and evidence paths | Every active dependency is under `E:/GT-KB`; no Agent Red lifecycle source is silently substituted. |

## Pre-Filing Gate Evidence

Candidate applicability and mandatory clause preflights are rerun against the
exact final candidate after insertion of the live claim/start evidence and
immediately before governed publication. The exact final command outputs and
file digest are preserved by the filing session; no self-referential packet
hash is inserted into these bytes.

- Applicability command:
  `python scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-wi5291-by-reference-finalization-recovery-v2 --content-file
  .gtkb-state/bridge-revisions/drafts/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md`
  - Required final result: PASS; `missing_required_specs: []`,
    `missing_advisory_specs: []`,
    `blocking_errors: []`, no target/path/author warnings.
  - The applicability packet hash is intentionally not self-embedded: changing a packet-hash
    line changes the candidate bytes. The filer must preserve the final command
    output alongside the exact filed digest during governed publication.
  - Operation-time finalization evaluation: allowed under active PAUTH v5 for
    `git_commit` and `protected_mutation`; four recovery-chain paths in the
    evaluator cohort. The separately required historical v006 include remains
    an exact finalizer-time cohort assertion rather than a declared report
    implementation target.
- Clause command:
  `python scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-wi5291-by-reference-finalization-recovery-v2 --content-file
  .gtkb-state/bridge-revisions/drafts/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md`
  - Required final result: PASS; 5 clauses evaluated, 4 `must_apply`, 1
    `may_apply`, 0 evidence gaps, 0 blocking gaps, exit 0.

## Prospective Terminal Include Set

Immediately before any terminal action, independent Loyal Opposition must
revalidate an exact five-path include set:

- `bridge/gtkb-wi5291-modernization-candidate-lint-normalization-006.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-001.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-002.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md`
- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-004.md`

The two subject tests are explicitly excluded. No unrelated path may enter the
terminal transaction. The reviewer must use the governed commit-first
finalizer; a file-only terminal verdict is invalid.

## Acceptance Criteria Status

1. PASS: recovery-v2 resolves strictly through current independent GO v002.
2. PASS: durable owner approval and active v5 project PAUTH are cited without
   treating the legacy WI approval label as authority.
3. PASS: neither immutable subject was modified, staged, restored, or
   recommitted.
4. PASS: current blob/raw/AST identities and custodial-sweep ancestry were
   re-derived exactly.
5. PASS WITH DISCLOSED DRIFT: target Ruff/format/diff gates pass; focused tests
   are 14 passed/3 later-state failures; broad Ruff has ten non-target findings.
6. PASS: historical malformed chain remains unchanged and fail-closed.
7. PASS: exact claim row 36126 and schema-v3 start packet
   `sha256:bb499ec9fa06ff78733a976e69890701f920966e5339e74b0715ce02974ba6ce`
   authorize only this v003 bridge report.
8. PENDING INDEPENDENT REVIEW: determine whether immutable subject evidence and
   disclosed later-state failures satisfy terminal verification requirements.
9. PENDING TERMINALIZATION: exact five-path commit-first include set.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260801-WI5291-BYREF-FINALIZATION-APPROVAL; strict recovery-v2 GO v002; independently reviewed historical v003-v004 subject evidence",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001; GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "Report immutable by-reference subject identity and current verification drift through the strict recovery-v2 controller without modifying either subject or the quarantined historical chain.",
  "before_behavior": "The historical controller is append-blocked by malformed v003 metadata; the reviewed subject bytes are clean tracked blobs from a broad custodial sweep; current authority-state drift makes three focused tests fail.",
  "after_behavior": "The subjects and historical chain are unchanged; the strict controller carries exact subject identity, ancestry, current test and broad-lint outcomes, and the bounded terminal cohort to independent review.",
  "self_descriptive_naming": "The recovery-v2 slug identifies WI-5291, by-reference finalization, and recovery from the malformed historical controller.",
  "obsolete_guidance_disposition": "The old chain is preserved as audit evidence but supplies no current authority; no parser relaxation or historical rewrite is performed.",
  "history_preservation": "All historical controller files and both implementation subjects remain unchanged; this report is append-only when later filed through the governed writer.",
  "baseline": {
    "recovery_versions_before_report": 2,
    "subject_files": 2,
    "subject_mutations": 0,
    "focused_tests_collected": 17,
    "focused_tests_passed": 14,
    "focused_tests_failed_from_current_authority_state": 3,
    "broad_ruff_non_target_findings": 10
  },
  "expected_result": {
    "subject_mutations": 0,
    "historical_controller_mutations": 0,
    "report_target_count": 1,
    "independent_terminal_review_required": true,
    "terminal_commit_path_ceiling": 5
  },
  "rollback": {
    "instructions": "If independent review rejects this recovery, retain the append-only report/verdict evidence, release only the exact claim through the governed path, and perform no source/test or historical-chain mutation.",
    "test": "Strict old-chain failure remains unchanged, recovery chain remains readable, both subject blob/raw/AST identities remain exact, and scoped Git state remains clean."
  },
  "hard_invariants": [
    "No mutation or staging of either WI-5291 implementation subject",
    "No rewrite of any historical controller file",
    "No live report before current GO, exact claim, and schema-v3 start authority",
    "No terminal publication before exact commit-first independent review",
    "No dispatcher or TAFE activation or configuration"
  ],
  "fail_closed_conditions": [
    "The recovery controller no longer resolves strictly to v002 GO before filing",
    "Either subject identity differs from reviewed blob, raw, or normalized-AST evidence",
    "Exact claim or operation-time project authorization is absent",
    "The terminal cohort exceeds old v006 plus recovery v001-v004",
    "Independent review cannot substantiate the disclosed focused-test or broad-Ruff drift"
  ],
  "essential_context_preservation": "Owner decision, old-chain parser defect, custodial-sweep ancestry, exact subject identities, current 14-pass/3-fail focused result, ten non-target broad-Ruff findings, five-path terminal ceiling, and disabled-dispatcher boundary remain explicit."
}
```

## Risk / Rollback

The primary risk is laundering a historically green test result into a false
current claim. This report instead records the current 14/3 focused outcome and
the exact authority-state diagnostics. A second risk is treating broad Ruff
drift as a WI-5291 subject defect; all ten findings are named and remain outside
the two immutable subjects.

Before terminal commit, rollback is a no-op or an append-only report revision.
A failed finalizer must leave no terminal file. After valid terminalization,
correction requires a separately governed append or revert; neither subject nor
historical bridge content is rewritten.

## Files Changed

- `bridge/gtkb-wi5291-by-reference-finalization-recovery-v2-003.md` — this
  evidence-only report is the sole authorized live target.

Excluded by-reference evidence only; not changed and not eligible for include:

- `platform_tests/scripts/test_check_artifact_evaluability.py`
- `platform_tests/scripts/test_modernization_authority_foundations.py`

## Recommended Commit Type

`chore(bridge)` for the separately authorized exact terminal-finalization
transaction, because this recovery changes governance evidence only and adds no
runtime capability.

## Loyal Opposition Asks

Independently re-read the owner decision, strict current GO, active project and
PAUTH, exact claim/start evidence, blob/raw/AST identities, custodial ancestry,
current 14-pass/3-fail focused tests, target quality gates, ten-finding broad
Ruff drift, and exact terminal cohort. Issue `NO-GO` unless every governing
terminal requirement is satisfied. If and only if all gates pass, use the
governed commit-first finalizer with the exact five-path ceiling and exclude the
two subject tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
