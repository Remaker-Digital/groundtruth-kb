REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; owner-directed manual newest-first bridge processing; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5823-impl-auth-spec-links-extractor-alignment
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5823
Related Test: TEST-11779
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py", "scripts/implementation_authorization.py.wi5823-backup"]
implementation_scope: complete_missing_slice_c_and_spec_derived_tests_then_remove_exact_tracked_backup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix:

# WI-5823 Recovery Revision — Complete the Approved Work and Its Missing Tests

## Claim

Version 006 correctly rejects version 005's attempted `NO-ACTION` closure, but
version 003 cannot truthfully be refiled as a verification-ready report. The
approved proposal and GO cover Slices A, B, and C. The committed source contains
Slices A and B only; the report expressly deferred Slice C; the dedicated
TEST-11779 module promised by proposal 001 is absent; and a tracked
`implementation_authorization.py.wi5823-backup` artifact remains from the
custodial landing. This revision returns the thread to proposal state so that
the missing behavior, tests, and exact backup disposition receive a fresh
independent review, claim, and schema-v3 implementation start.

This proposal does not retroactively bless the custodial commit or the expired
packet. It makes no source, test, MemBase, registry, dispatcher, TAFE, Git,
credential, deployment, release, or external-system mutation.

## Findings Addressed

### Version 004 / 006 — implementation-start and executed evidence

Accepted. The historical named packet exists at
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment.json`.
It records packet hash
`sha256:f488d7bc3252200438710a38962a73af4a0afe0597003e6f06e06b6003fd0f76`,
created `2026-07-31T16:22:59Z`, expired `2026-07-31T18:22:59Z`, finalized
`2026-07-31T16:22:59Z`, session `G-2026-07-31T07-41-38Z`, the active project
authorization decision, and the exact original three-target set. Those facts
must appear in any later implementation report, but the expired packet is not
authority for new edits. A fresh packet is mandatory after a new GO.

The six extant implementation-authorization modules were executed fresh on
2026-08-01 with a diagnostic outer envelope of 600 seconds: 202 passed, one
pre-existing pytest configuration warning, in 268.69 seconds. Ruff lint passed,
Ruff format check passed, and `git diff --check` passed for the current source
and table-regression module. An attempted exact seven-module command collected
zero tests because the approved
`platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py`
path does not exist. That is evidence of incomplete implementation, not a test
success.

### Newly exposed completion gap

Proposal 001 and GO 002 approved all three slices, including the fail-closed
`amend-proposal` formatting-only overlay. Current source retains
`_section_body_including_subsections`, `_preflight_parity_harvest`, and the
three-branch `extract_spec_links` flow, but has no `amend-proposal` command or
equivalent durable overlay implementation. Version 003's unilateral deferral
did not change the approved acceptance contract.

## Current Baseline And Ownership

Repository HEAD is `75decbfa704fe50288aecbc5669def329a0825df`. All existing
paths below are tracked and Git-clean; no current target has a worktree or index
delta.

| Path | Current identity | Disposition |
| --- | --- | --- |
| `scripts/implementation_authorization.py` | SHA-256 `BB9F5C731D8920793D17305CD5D78F8B8F038CED8189C0D1E4ED9E953BBD3891` | Preserve Slices A+B and all later unrelated work; add only missing Slice C integration. |
| `platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py` | absent | Create the dedicated TEST-11779 grammar/amendment module promised by proposal 001. |
| `scripts/implementation_authorization.py.wi5823-backup` | SHA-256 `C080796D566AB5E4265B1CB0AE27DC8EC5B3FB81D970A0CD28C0175966F9364E` | Remove only this exact tracked custodial backup through the reviewed patch. |
| `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` | SHA-256 `40B5657DA8AEDED53AEEF41B53F1E38FF838AB2EDCB9AF72320A2579CAE18C51` | Verification dependency only; execute unchanged. |

The partial implementation and backup were preserved by custodial commit
`02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`. Later source changes, including
WI-5742, must not be rolled back or absorbed. Deleting the exact tracked backup
is proposed as a reversible source-file deletion, not a recursive or untracked
cleanup operation. If operation-time enforcement classifies it as forbidden
`destructive_cleanup`, implementation must stop before mutation and return for
narrower owner authority.

## Requirement Sufficiency

Existing requirements sufficient. WI-5823, TEST-11779, proposal 001, GO 002,
and corrective verdicts 004 and 006 already define the complete behavior and
evidence floor. This revision completes and narrows previously approved work;
it creates no formal requirement or MemBase mutation.

## Proposed Implementation

### Preserve and regression-lock Slices A+B

Keep the level-aware subsection reader and bullet, table, then preflight-parity
extraction order. The new dedicated module must prove bullet precedence,
dormant table fallback, nested `###` visibility, compact prose citation parity,
and fail-closed empty/placeholder behavior. The existing table module remains
unchanged and executes as a regression dependency.

### Complete Slice C without rewriting bridge history

Add:

```text
python scripts/implementation_authorization.py amend-proposal --bridge-id <slug> --amended-file <in-root-path>
```

The command must:

1. Resolve an unambiguous GO-usable numbered chain and the exact approved
   proposal/GO pair; reject `NEW`, `REVISED`, `NO-ACTION`, `VERIFIED`,
   `DEFERRED`, malformed, or superseded state.
2. Accept only an in-root, non-bridge, regular UTF-8 amended file.
3. Require equality of status, document, bridge kind, PAUTH/project/WI triple,
   exact target set, Requirement Sufficiency state, and preflight-harvested
   specification set between approved and amended bytes.
4. Require the amended bytes to pass strict spec-link, target, sufficiency,
   metadata, and spec-derived-plan parsing.
5. Write no numbered bridge file. Persist append-only, content-addressed JSON
   evidence under `.gtkb-state/impl-auth-amendments/<bridge-id>/` with both
   hashes, full amended text, equivalence results, UTC/session provenance, and
   record hash. Identical retries are idempotent; conflicts never overwrite.
6. Let `begin` consult the overlay only when direct strict parsing of the GO'd
   proposal fails. Re-hash and revalidate proposal, GO, chain, record, and all
   equivalence gates before use. Directly parseable approved bytes always win.
7. Bind any use into schema-v3 `amendment_applied` packet evidence and recheck
   that binding during packet validation.

No timer, wait, retry, backoff, threshold, throttle, fan-out, or concurrency
literal is added. Any such control discovered as necessary must resolve through
the centralized typed configuration program owned by WI-5806/WI-5807 and return
for a target-covered review rather than creating a local fallback.

### Remove only the tracked backup

Delete only `scripts/implementation_authorization.py.wi5823-backup`. Do not run
a recursive cleanup, prune, history rewrite, or untracked-file deletion. The
exact blob remains recoverable from custodial commit `02e12e7b0`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `SPEC-1662`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Specification-Derived Verification Plan

| Requirement | Executed evidence required after implementation |
| --- | --- |
| TEST-11779; Slices A+B | Dedicated bullet, table, nested-subheading, compact-prose, parity-matrix, empty, and placeholder cases; existing table suite unchanged and green. |
| Slice C; append-only bridge authority | Formatting-only overlay succeeds while every numbered bridge byte remains identical. |
| Substance boundary | Changes to spec set, targets, sufficiency, metadata, status, document, or bridge kind fail closed and write no record. |
| Lifecycle boundary | Only the explicitly permitted unique-GO/resumable state succeeds; all other statuses, newer GO, ambiguity, and malformed chains fail. |
| Root boundary | Out-of-root, bridge-path, escaping-symlink, unreadable, and non-UTF-8 inputs fail closed. |
| Concurrency/append-only evidence | Identical concurrent writers converge idempotently; conflicting records cannot overwrite and ambiguous evidence blocks `begin`. |
| Packet integrity | Direct clean proposal wins; a valid overlay is freshly revalidated and disclosed; stale proposal, GO, or record hashes fail. |
| Nonimpairment | Current direct `begin`, packet history/integrity, lifecycle, table, and terminal-evidence suites remain green. |
| Timer/configuration directive | Deterministic scan proves changed production code adds no hard-coded timer, retry, interval, backoff, throttle, threshold, fan-out, or concurrency value. |

Required commands include the dedicated and existing table modules plus the
full touched implementation-authorization suite, separate Ruff lint and format
checks, `py_compile`, `git diff --check`, exact target status, and pre/post
SHA-256 inventory of bridge versions 001-007. The implementation report must
record exact commands, exit codes, counts, elapsed times, every mapping row as
executed yes/no, and the fresh packet path/hash/timestamps/session/claim/PAUTH
decision. Planned evidence is not executed evidence.

## Acceptance Criteria

1. Slices A+B remain behaviorally unchanged and gain their missing dedicated
   spec-derived coverage.
2. `amend-proposal` implements every fail-closed equivalence and lifecycle gate
   while writing zero numbered bridge bytes.
3. Direct parsing stays primary; any accepted overlay is append-only,
   content-addressed, freshly revalidated, and disclosed in the packet.
4. Concurrent identical writes are idempotent; conflicts never overwrite and
   ambiguity blocks authorization.
5. The exact tracked backup is removed and no other path is deleted.
6. All mapped tests and separate quality gates pass under a generous diagnostic
   envelope; no short timer is interpreted as process failure.
7. The implementation report contains complete start-packet and executed
   spec-to-test evidence suitable for independent terminal review.
8. No MemBase, registry, dispatcher/TAFE, credential, external system, release,
   deployment, push, or history rewrite occurs.

## Project Authority And Owner Decisions

`PROJECT-GTKB-HARNESS-TEST-CORRECTIONS` is active and WI-5823 is an active
member. The list-free whole-project PAUTH above is active and permits source,
test, test-addition, and bridge work while preserving all normal GO, claim,
packet, report, and independent-verification gates. Under the owner's project
inheritance rule, the WI row's legacy `approval_state` is not a separate veto.

- `DELIB-202667730` — Harness Test synthesis and defect evidence.
- `DELIB-202667731` — owner approval of the whole-project PAUTH.
- `DELIB-202667735` — delegated correction-proposal authoring while preserving
  the full governed implementation cycle.
- `DELIB-202667726` — originating Harness Test correction directive.

No additional owner decision is required to review this revision. If the exact
tracked-backup deletion is classified as forbidden at operation time, stop and
request that single narrower decision; do not bypass the gate.

## Cross-Harness / Nonimpairment Disposition

The implementation-authorization CLI is a shared repository service, so its
behavior applies uniformly to every harness. No harness-specific projection,
role, eligibility, routing, dispatcher, or TAFE path is changed. The direct
GO-approved proposal remains the intuitive primary input; the overlay is used
only for strict-format recovery and is explicit in packet evidence.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5823; TEST-11779; bridge versions 001-006; DELIB-202667730; DELIB-202667731",
  "canonical_authority": "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Parse the immutable GO-approved proposal directly; use an append-only formatting overlay only when strict direct parsing fails.",
  "before_behavior": "Slices A and B are committed without the dedicated test module; Slice C is absent; a tracked custodial backup remains.",
  "after_behavior": "The approved grammar behavior is regression-locked, formatting-only recovery preserves numbered bridge bytes, packets disclose overlays, and the exact backup is removed.",
  "baseline": "HEAD 75decbfa704fe50288aecbc5669def329a0825df; source SHA-256 BB9F5C731D8920793D17305CD5D78F8B8F038CED8189C0D1E4ED9E953BBD3891; dedicated grammar test absent; tracked backup SHA-256 C080796D566AB5E4265B1CB0AE27DC8EC5B3FB81D970A0CD28C0175966F9364E; six extant modules 202 passed in 268.69 seconds.",
  "self_descriptive_naming": "amend-proposal and amendment_applied identify the recovery action and its packet evidence.",
  "history_preservation": "Versions 001-006 and custodial commit 02e12e7b0 remain immutable; amendment evidence is append-only and content-addressed.",
  "obsolete_guidance_disposition": "Version 003's verification-ready implication and version 005's terminal NO-ACTION claim remain historical but noncontrolling.",
  "configuration_authority": "Any timer, retry, throttle, threshold, fan-out, or concurrency control resolves through the centralized typed configuration program; this slice adds no local literal.",
  "expected_result": "Complete Slice C and TEST-11779 without rewriting bridge history or impairing direct implementation authorization.",
  "essential_context_preservation": "Preserve the PAUTH, full numbered chain, GO-reviewed substance, exact target set, custodial provenance, later source changes, timer/configuration boundary, fresh packet obligation, and executed spec-to-test evidence.",
  "hard_invariants": [
    "No numbered bridge byte is rewritten or deleted.",
    "No amendment record is overwritten.",
    "No dispatcher, TAFE, harness-role, or routing state is changed.",
    "No new target mutation begins without fresh GO, claim, and schema-v3 packet."
  ],
  "fail_closed_conditions": [
    "Proposal or GO identity is ambiguous or stale.",
    "The amended content changes any reviewed substance.",
    "The input escapes the project root or names a bridge file.",
    "A conflicting amendment record exists.",
    "The exact backup deletion is classified as forbidden destructive cleanup."
  ],
  "rollback": "Governedly revert only the source/new-test patch and restore the exact backup blob from commit 02e12e7b0; retain append-only evidence."
}
```

## Risks And Rollback

The principal risk is disguising a substantive proposal rewrite as formatting.
Exact equality gates, original-first parsing, append-only records, fresh
revalidation, and packet disclosure contain it. Same-file source contention is
contained by the clean current baseline, exact claim/start target enforcement,
and preservation of later unrelated changes. Evidence growth is bounded to one
small content-addressed record per accepted amendment and exact lookup by bridge
and hashes, never a scan of unrelated history.

Rollback is a separately governed exact revert of the source/new-test patch and
restoration of the backup blob from `02e12e7b0`. Existing numbered bridge files
and amendment evidence remain append-only; history rewrite and evidence deletion
are not rollback mechanisms.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
