NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled

# WI-5368 Implementation Report - Exact-Postimage Recovery Under PAUTH v3

bridge_kind: implementation_report
Document: gtkb-wi5368-codex-git-window-command-family
Version: 017
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-016.md
Approved proposal: bridge/gtkb-wi5368-codex-git-window-command-family-015.md
Date: 2026-07-30 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]

implementation_scope: exact_postimage_recovery_and_atomic_finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

## First-Line Role Eligibility Check

PASS. The resolved session role is Prime Builder and may author `NEW`.
Session `019fb1f2-2f91-7b82-ac15-acdd56e13d1e` holds the exact current
`go_implementation` claim and finalized schema-v3 implementation-start packet
for GO v016 and the two declared targets. This report requests independent
verification; it does not author a Loyal Opposition verdict.

## Implementation Claim

The marker-qualified Codex internal Git command-family implementation described
by the earlier v011/v012 chain remains complete in exactly two unstaged target
postimages. The v015 recovery proposal and independent GO v016 re-established
current project and operation-time authority after owner-approved Harness
Parity PAUTH v3 removed only the former `git_commit` prohibition.

This recovery transaction made no new source or test edit. It bound the exact
frozen postimages to a fresh claim and start packet, revalidated their bytes,
reran the full focused and quality cohort, and now files the current-evidence
implementation report required by v015/v016. The old v012 packet and v013
scratch/NO-ACTION evidence remain historical and are not reused as authority.

The implementation recognizes the observed internal Git command family only
when all strict qualifiers hold: `git.exe`, exactly one case-insensitive
`core.hooksPath=NUL`, exactly one empty `core.fsmonitor=`, a non-empty
non-option Git subcommand, the top-level window/conhost relationship, bounded
ChatGPT ancestry, and no nested Git ancestor. The only target-window/process
side effect remains `ShowWindowAsync(SW_HIDE)`. Ambiguity fails open; no
process termination, Git interception, routing, eligibility, or harness
suppression is introduced.

## Fresh Claim And Implementation-Start Evidence

- Claim row: `35025`, kind `go_implementation`, acquired
  `2026-07-30T16:02:23Z` by session
  `019fb1f2-2f91-7b82-ac15-acdd56e13d1e` for active member WI-5368.
- Authorizing GO:
  `bridge/gtkb-wi5368-codex-git-window-command-family-016.md`.
- Approved recovery proposal:
  `bridge/gtkb-wi5368-codex-git-window-command-family-015.md`.
- Finalized schema-v3 packet hash:
  `sha256:0e336fcb0b05723100f22c9164381066abb06176cea0ec87948dd9a864b5eabe`.
- Pre-start packet hash:
  `sha256:19ef6fb581b1847633f908be5daa92eaceb76a3d07296374a05c8192ccaa89cf`.
- Finalized at `2026-07-30T16:03:16Z`; expires
  `2026-07-30T17:03:16Z`.
- Operation-time evaluation selected active PAUTH v3, normalized-envelope hash
  `60C2A6525EE0234A0B739D4CE5A83DCFA9EE459C0D029DFA014DE032B5635FAC`,
  and allowed both exact source/test targets.
- Worker role provenance resolved this exact session as Prime Builder from the
  transcript init keyword.

## Exact Recovery Cohort

Both targets remain modified and unstaged; the index contains their clean HEAD
preimages and the cached target cohort is empty.

| Target | Index / clean blob | Current postimage blob | Current raw SHA-256 | Bytes | Numstat |
|---|---|---|---|---:|---:|
| `scripts/ops/codex_snapshot_window_hider.py` | `4b0ed05225b161bd582e53489c393a2b5a7693e9` | `cc1923054d9bb82c6cb6314093af7595385836d5` | `88BFFC35E4AB9A9A18B243CC35993C086276C3ADD8CCB22326B87FFEA0A18BC1` | 7,773 | `+42/-14` |
| `platform_tests/scripts/test_codex_snapshot_window_hider.py` | `309f56fa9f7f499815628281c27ccd2890cef13d` | `8b5ac667b48519d96e3c716dd83f78acae931c8b` | `BB93F56AA55689002C470080094C0213313F5F16359895F2E1D79800CAF7A20A` | 9,897 | `+151/-8` |

These values exactly match v015's frozen postimages and LO's v016 independent
re-observation. No third target, cached hunk, or new byte change was introduced.

## Files Changed

- `scripts/ops/codex_snapshot_window_hider.py`
  - parses leading Git `-c key=value` overrides;
  - requires `git.exe`, the two singleton exact Codex markers, and a valid
    subcommand;
  - preserves conhost ancestry, bounded ChatGPT ancestry, top-level event,
    singleton mutex, hide-only effect, and fail-open exception boundaries; and
  - rejects nested Git ancestry and marker/executable/subcommand near misses.
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`
  - covers observed `write-tree`, `read-tree`, `diff`, `status`, `ls-files`,
    and pathspec `add` families;
  - exercises outer/inner Git paths, case-insensitive keys, benign extra
    configuration, duplicate/malformed/missing marker rejection, invalid
    subcommands, non-Git forms, nested Git, ancestry bounds, and fail-open
    behavior; and
  - preserves static no-termination/no-dispatch and hide-only assertions.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667709` - owner-approved whole-project Harness Parity PAUTH v3;
  preserves v2 scope and gates while removing only `git_commit` from forbidden
  operations.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` - active project
  members inherit controlling whole-project implementation authority.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - no-visible-console requirement
  without harness suppression or loss of dispatchability.
- `DELIB-202666274` - modernization program's independent bridge, start,
  verification, and non-impairment gates.

## Owner Decisions / Input

No new owner decision is required. Active PAUTH v3 is list-free and applies to
active member WI-5368. It now permits governed local `git_commit` after normal
report and independent-verification gates. It continues to forbid push,
history rewrite, dispatcher mutation, external-system mutation, credential
lifecycle, production deployment, release, and destructive cleanup. The owner
contract also continues to forbid dispatcher/TAFE configuration or activation,
harness/role/eligibility mutation, manual routing, direct harness contact, raw
database mutation, and Git staging outside the governed finalizer.

## Requirement Sufficiency

Existing requirements sufficient. V015/v016 changed only recovery authority
and current-evidence binding; the strict marker-qualified containment behavior,
non-impairment boundary, and spec-derived test obligations remain complete.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Observed result |
|---|---|---|
| Strict command-family qualification and near-miss isolation | `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short --timeout=180` | 42 collected; 42 passed in 0.61s. |
| Hide-only non-impairment and no lifecycle/dispatch suppression | Focused behavioral/static tests plus source inspection | Only `ShowWindowAsync(SW_HIDE)` remains; no termination, dispatcher, TAFE, routing, role, or eligibility action exists. |
| Code quality | `python -m ruff check` and `python -m ruff format --check` on both targets | Ruff check passed; both files already formatted. |
| Exact target isolation | Raw SHA-256, `git hash-object`, index blob, scoped status/numstat/cached cohort, and `git diff --check` | Frozen v015 values match; exactly two unstaged paths; cached cohort empty; diff check passed. |
| Project/start authority | Current PAUTH v3 readback, claim row 35025, and finalized schema-v3 packet | Exact project, active member, GO, session, role, and target cohort are allowed at operation time. |
| Append-only terminal integrity | v015/v016 plus this report and requested independent review | Old v012/v013 evidence remains historical; only a future independent VERIFIED may authorize governed finalization. |

## Commands Run And Observed Results

- `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short --timeout=180` - exit 0; `42 passed in 0.61s`.
- `python -m ruff check scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py` - exit 0; all checks passed.
- `python -m ruff format --check scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py` - exit 0; two files already formatted.
- `git diff --check -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py` - exit 0; only an informational Windows LF/CRLF warning was emitted for the test worktree file.
- Scoped hash, blob, status, numstat, and cached-diff observations produced the exact table above; the cached cohort was empty.

## Acceptance Criteria Status

1. PASS - fresh claim and schema-v3 packet bind v015/v016, PAUTH v3, this
   session, and the exact two postimages.
2. PASS - both singleton Codex Git markers, `git.exe`, valid subcommand,
   conhost/top-level event, bounded ChatGPT ancestry, and nested-Git rejection
   are enforced.
3. PASS - all observed internal command families qualify; malformed and
   unrelated forms remain visible and untouched.
4. PASS - commands continue naturally; there is no process, Git-interception,
   dispatcher/TAFE, routing, role, eligibility, or harness mutation.
5. PASS - only the two declared postimages differ from their frozen index
   blobs, and they match v015/v016 exactly.
6. PASS - PAUTH v3 removes the former local-commit prohibition while retaining
   independent VERIFIED and governed finalizer gates.
7. PENDING INDEPENDENT VERIFICATION - this report requests Loyal Opposition
   re-execution and verdict; no terminal claim is made here.

## Risk And Rollback

The main residual risk is a future Codex command shape lacking both markers;
fail-open behavior leaves that console visible rather than hiding an unrelated
process. Rollback is a separately governed two-path correction after current
review/finalization. Broad checkout/reset, manual staging/commit, process
termination, dispatcher/TAFE action, push, history rewrite, credential action,
external mutation, deployment, release, and destructive cleanup remain out of
scope.

## Loyal Opposition Asks

1. Independently verify singleton-marker parsing, observed family coverage,
   nested-Git rejection, bounded ChatGPT ancestry, and hide-only behavior.
2. Re-run the focused tests, Ruff gates, and exact two-path hash/diff checks.
3. Return VERIFIED only if the report, fresh start evidence, and frozen
   postimages satisfy v015/v016; otherwise return NO-GO with concrete findings.

## Recommended Commit Type

`fix` - complete the exact two-path Codex window-containment correction through
the governed local finalizer after independent VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
