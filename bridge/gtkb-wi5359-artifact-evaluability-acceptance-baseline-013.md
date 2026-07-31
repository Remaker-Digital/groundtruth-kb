REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5359-artifact-evaluability-acceptance-baseline
Version: 013
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5359-artifact-evaluability-acceptance-baseline-012.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5359
target_paths: ["scripts/check_artifact_evaluability.py", "platform_tests/scripts/test_check_artifact_evaluability.py"]
implementation_scope: current_head_zero_byte_acceptance_and_atomic_evidence_finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5359 Current-HEAD Acceptance And Atomic Evidence Finalization Revision

## Revision Claim

This revision resolves every v012 prerequisite without changing either
protected target. Owner-approved whole-project Assurance PAUTH v4 is active at
MemBase row 946 under `DELIB-202667713`; it preserves v3 and removes only
`git_commit` from registered forbidden operations. A fresh native-process check
also establishes that the future scoped arguments exit with code 2 exactly as
v009 required. The exit-1 statement in v011 was a shell/tool-transport
misclassification and is explicitly corrected here.

This proposal authorizes only a zero-byte acceptance transaction against the
exact current tracked baseline, a fresh report containing current evidence, and
governed atomic finalization of the complete uncommitted numbered evidence
cohort. GO-010, its claim, and its start packet remain historical and may not be
reused. A new independent GO must include both mandatory applicability and
Clause Applicability evidence before any fresh implementation claim/start.

## Findings Addressed

### V012-F1 - Whole-project terminal commit authority was absent

Resolved. The owner replied `Approve Assurance PAUTH v4`; the decision is
captured as `DELIB-202667713`, and active PAUTH version 4 is row 946. Version 4
retains the list-free whole-project scope, allowed mutation classes, included
specifications, no exclusions, no expiry, and all normal lifecycle gates. It
removes only `git_commit` from `forbidden_operations`.

Raw/manual staging or commit remains outside scope. Only the governed exact
atomic VERIFIED finalizer may stage and commit the reviewed bridge cohort after
its operation-time checks. Push, release, deployment, history rewrite,
credential action, destructive cleanup, external mutation, and dispatcher/TAFE
mutation remain forbidden.

### V012-F2 - The exact future-CLI exit criterion appeared to fail

Resolved by distinguishing the native checker code from the outer shell/tool
result. Running the bare native command as the last PowerShell process caused
the tool wrapper to summarize the shell as exit 1. Two direct native checks
prove the checker itself returns 2:

1. PowerShell immediately after the command reports `NATIVE_EXIT=2` from
   `$LASTEXITCODE`.
2. A Python `subprocess.run([...])` call reports `returncode: 2`, empty stdout,
   and argparse's expected unrecognized-argument diagnostic on stderr.

No checker or test byte changed. The intended criterion is native process
return code 2, not the enclosing harness transport's normalized exit status.
Future report and verification must capture the native return code explicitly.

### V012-F3 - GO-010 omitted mandatory Clause Applicability evidence

Accepted. V013 does not reuse GO-010. Its complete candidate must pass both
preflights before publication, and a later GO is executable only if it embeds
the applicability and mandatory Clause Applicability results, including clause
counts, exit 0, and zero blocking gaps.

## Exact Current Baseline

Repository HEAD is `8a35eabc8cae297cbd295223d6ec904aa15212b8`.

| Target | State | Bytes | SHA-256 | Git blob |
| --- | --- | ---: | --- | --- |
| `scripts/check_artifact_evaluability.py` | tracked, clean, unstaged | 14,451 | `2e02ad3911d419be4ea4a56c8aae8e0d4a5f25b829406664be9fd9673b61b862` | `bebfc1f0a98a15a96a519a417f1461cc76fab56f` |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | tracked, clean, unstaged | 7,933 | `69e4fac09572619dccd6c9fa526fbc14ba795ae1225949691e4574b612f15b67` | `3799fa92a02c6d22c63f7b59fa7ff88163cf0e16` |

Any target byte, length, blob, index entry, tracked state, clean status, HEAD,
project membership, PAUTH, bridge frontier, claim, or peer-ownership drift is a
hard stop requiring another append-only revision.

## Project-Only Authorization

WI-5359 remains an active member of
`PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`. Active authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
is version 4, row 946, owner decision `DELIB-202667713`, with no work-item
inclusion or exclusion list. Legacy WI `approval_state` and the stale resolved
compatibility projection do not grant, revoke, or prove implementation
authority; the active project membership, PAUTH, numbered bridge frontier,
claim, start packet, and operation-time decisions control.

Remaining forbidden operations are `credential_lifecycle`,
`destructive_cleanup`, `dispatcher_mutation`, `external_system_mutation`,
`git_history_rewrite`, `git_push`, `production_deployment`, and `release`.

## Scope And Atomic Evidence Cohort

The post-GO acceptance transaction performs no source or test write. It:

1. acquires a fresh exact `go_implementation` claim and schema-v3 start packet
   bound to v013, its new GO, PAUTH v4, and the two baseline paths;
2. revalidates HEAD, target hashes, lengths, blobs, index entries, tracked/clean
   state, active project membership, PAUTH, and absence of target collisions;
3. executes the focused tests, Ruff checks, native exit-2 check, and post-check
   rehash/status checks;
4. files a new implementation report stating zero target-byte changes and
   preserving the historical sweep provenance without laundering it into this
   WI's implementation history; and
5. requests independent verification and the governed atomic finalizer.

Bridge versions 009 through 012 are currently untracked. Terminal finalization
must create one exact local commit containing the complete v009-through-v016
numbered recovery/evidence chain, including the independently authored future
GO, implementation report, and VERIFIED verdict. The already tracked source and
test bytes are evidence inputs, not new commit content. Any extra bridge or
nonbridge path in that exact finalizer cohort is a stop.

## Requirement Sufficiency

**Existing requirements sufficient.** The linked evaluability, worktree
hygiene, deterministic enforcement, nonimpairment, project authorization,
bridge authority, SoT freshness, and spec-derived testing requirements fully
determine this zero-byte acceptance and atomic evidence transaction. No new or
revised normative carrier is required.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202667713` records the exact owner approval for whole-project
  Assurance PAUTH v4 and removal of only `git_commit`.
- `DELIB-202666274` is the prior Assurance whole-project authorization source;
  v4 preserves its scope and gates.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establishes
  project-only authority for active member work items.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` makes per-WI approval
  metadata non-controlling.
- V008-v012 preserve the stale-baseline discovery, current-byte acceptance,
  incomplete GO, PB stop, and corrected NO-GO history.

## Owner Decisions / Input

The owner replied exactly `Approve Assurance PAUTH v4`. The decision is
captured as `DELIB-202667713` and materialized as active PAUTH v4 row 946. No
further owner decision is required for this exact acceptance transaction.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"v008-v013 current-state correction plus exact HEAD and native-process verification","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"focused 14-test suite plus exact tracked-byte and native-exit checks","before_behavior":"The recovery chain contains an incomplete GO and a shell-normalized exit result that obscures the checker's native code.","after_behavior":"The chain independently accepts the exact current tracked baseline, records native exit code 2 explicitly, changes no target byte, and commits the complete evidence chain atomically.","self_descriptive_naming":"The two-path baseline table, native-exit distinction, and exact bridge cohort state the acceptance boundary directly.","obsolete_guidance_disposition":"GO-010 is not reused; v011's exit-1 interpretation is corrected append-only while all prior files remain audit history.","history_preservation":"The historical sweep, stale premise, corrected baseline, stop, owner PAUTH decision, and fresh evidence remain queryable.","baseline":{"head":"8a35eabc8cae297cbd295223d6ec904aa15212b8","target_count":2,"tracked_target_count":2,"focused_tests":14,"native_future_cli_exit":2},"expected_result":{"target_byte_changes":0,"focused_tests_passed":14,"native_future_cli_exit":2,"atomic_bridge_versions":"009-016"},"rollback":{"instructions":"supersede the acceptance chain through a separately governed append-only correction","verification":"recheck exact target identities, native exit, and committed evidence cohort"},"hard_invariants":["no target-byte change","both targets tracked and clean","native exit code captured directly","no WI-5153 behavior added","only exact bridge cohort committed","no dispatcher or TAFE mutation"],"fail_closed_conditions":["target or HEAD drift","native exit differs from 2","focused test or Ruff failure","missing applicability or clause evidence","PAUTH/claim/start denial","extra finalizer path"],"essential_context_preservation":"Retain current checker behavior, unsupported future CLI boundary, historical sweep provenance, project authority, and complete numbered recovery evidence."}
```

## Specification-Derived Verification Plan

| Governing requirement | Verification after fresh GO | Required result |
| --- | --- | --- |
| Current project authority | Read active membership and PAUTH v4, then mint fresh exact claim/start | PAUTH row 946; exact two targets allowed; no WI-local approval consulted. |
| Exact current baseline | HEAD, lengths, SHA-256, Git blobs, index entries, tracked state, scoped status | All values equal the v013 table; both targets clean and unstaged. |
| Executable baseline | `python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180` | Exactly 14 tests pass. |
| Future interface boundary | Python subprocess invokes the exact unsupported `--spec-id`, `--work-item`, `--gate`, `--json` command | Native `returncode == 2`; argparse rejects the future arguments. |
| Code quality | Ruff check and Ruff format check over both targets | Both exit 0 without mutation. |
| Nonimpairment | Rehash, reblob, and recheck status after every command | Zero target changes and no third target. |
| Review completeness | Fresh GO embeds applicability and mandatory clause evidence | Both pass; clause exit 0 and zero blocking gaps. |
| Terminal integrity | Independent report review plus exact atomic finalizer | One local commit contains only bridge v009-v016; no push/release/deployment. |

Fresh read-only evidence before v013 filing: both target hashes/blobs/status and
HEAD matched; 14 focused tests passed; Ruff check and format passed; direct
PowerShell and Python-subprocess checks reported native exit 2.

## Acceptance Criteria

1. A new independent GO approves v013 and includes both mandatory preflight
   sections with no omissions or blocking gaps.
2. A fresh claim and schema-v3 start packet bind v013, its GO, PAUTH v4, active
   project membership, and the exact two clean tracked targets.
3. The acceptance transaction changes no source or test byte and reports the
   native child-process return code rather than an enclosing transport code.
4. All 14 focused tests and both Ruff gates pass; exact identities remain stable
   before and after.
5. A new report preserves zero-byte scope and historical sweep provenance.
6. Independent VERIFIED and the governed finalizer create one exact local
   commit containing only bridge versions 009 through 016.
7. Any target, authority, claim, packet, frontier, test, native-exit, or commit-
   cohort drift fails closed and requires another append-only revision.

## Pre-Filing Preflight Subsection

The complete v013 candidate must pass the applicability and mandatory ADR/DCL
clause preflights before governed publication. Require no missing required or
advisory specifications, no blocking error, clause exit 0, zero evidence gaps,
and zero blocking gaps. The later LO GO must independently embed both results.

## Risk And Rollback

The principal evidence risk is confusing an outer shell/tool exit status with
the native checker return code; direct subprocess capture eliminates that
ambiguity. The lifecycle risk is laundering the historical sweep or producing a
file-only terminal state; zero-byte scope, explicit provenance, PAUTH v4, and
the exact v009-v016 atomic cohort contain it. Rollback is a separately governed
append-only correction; no source rollback is needed because this transaction
changes no target byte. Broad reset, checkout, raw staging, manual commit,
history rewrite, push, release, deployment, credentials, destructive cleanup,
external mutation, and dispatcher/TAFE mutation are prohibited.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
