REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata


# WI-5368 Codex Git Window Command Family - Single-Carrier Supersession Revision

bridge_kind: prime_proposal
Document: gtkb-wi5368-codex-git-window-command-family
Version: 011
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-010.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]
implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

This revision resolves the v010 cross-thread stop by selecting exactly one
active project carrier and one technical contract. WI-5368 under the active
Harness Parity project is the controlling carrier. This revision explicitly
supersedes and consolidates the unimplemented intent of
`gtkb-wi5298-codex-git-window-family-containment-repair` into WI-5368; it does
not adopt that sibling's argument-independent provenance, nested-Git ancestry,
or v2 mutex requirements.

The selected behavior remains the stricter marker-qualified WI-5368 design:
require the exact Codex Git-manager overrides `core.hooksPath=NUL` and an empty
`core.fsmonitor=`, preserve the existing direct ChatGPT/conhost ancestry bound,
and leave the existing mutex unchanged. This minimizes the risk of hiding
unrelated user or tool Git processes while extending the already-governed
hide-only fallback to the observed internal Git command family.

The sibling v002 GO is retained as historical reviewed evidence only. Its
project is retired, WI-5298 is resolved, the v002 verdict has no typed
publication capability, and no implementation report or terminal verdict
followed it. A canonical `WITHDRAWN` v003 publication was attempted with exact
session provenance after the v010 response, but the writer failed closed before
publication because `WITHDRAWN` has no formal responder-role envelope mapping.
No sibling v003 was written, no claim remains, and no manual bridge write or
writer bypass occurred. WI-5763 carries correction of that canonical filing
defect. This revision supplies the explicit supersession disposition that is
currently publishable through the governed typed path.

No source or test mutation is authorized by this revision. Implementation may
begin only after an independent GO on this exact v011 content, an exact live
claim, and a passing implementation-start packet against the frozen target
bytes and the active whole-project PAUTH.

## Findings Addressed

### F1 - P1 - Cross-thread target ownership remained unresolved

Resolved by an explicit single-carrier selection. The retired sibling's
unimplemented intent is superseded and consolidated here. WI-5368 is the only
active project member proposed to own the two targets, and its marker-qualified
contract is the only design presented for approval.

### F2 - P1 - Competing designs could hide materially different Git processes

Resolved by rejecting the broader sibling contract. The implementation must
not qualify Git solely from process provenance, must not accept nested Git
ancestry, and must not alter the monitor mutex. The two exact configuration
markers, direct ancestry, top-level event, executable identity, and fail-open
inspection behavior remain mandatory.

### F3 - P1 - A terminal sibling disposition could not be canonically filed

Disclosed and contained. The canonical writer rejected `WITHDRAWN` before
publication due to its missing responder-role envelope mapping. The failure was
not bypassed. This v011 revision uses the supported REVISED lifecycle to record
explicit supersession, while WI-5763 owns the writer/status-enum correction.

## Scope And Frozen Baseline

Implementation remains limited to:

1. parse Git `-c key=value` overrides and require a non-empty subcommand;
2. require `git.exe`, exactly one `core.hooksPath=NUL`, exactly one empty
   `core.fsmonitor=`, the existing top-level event, `conhost.exe` relationship,
   and direct bounded ancestry to `ChatGPT.exe`;
3. reject duplicate, missing, malformed, or near-miss markers, missing
   subcommands, non-Git executables, nested Git ancestry, and non-ChatGPT
   provenance;
4. preserve `ShowWindowAsync(SW_HIDE)` as the sole target-window/process side
   effect and fail open on all inspection ambiguity; and
5. extend only the declared focused test module for observed command shapes and
   rejection cases.

Frozen clean target blobs:

- `scripts/ops/codex_snapshot_window_hider.py`:
  `4b0ed05225b161bd582e53489c393a2b5a7693e9`.
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`:
  `309f56fa9f7f499815628281c27ccd2890cef13d`.

Any target drift, index entry, new peer ownership, PAUTH denial, or unrelated
path is a stop requiring another governed revision. Dispatcher, TAFE, routing,
eligibility, role, Git execution, process lifetime, credential, release,
deployment, staging, commit, push, and third-file changes remain out of scope.

## Project-Only Authorization

WI-5368 is an active member of
`PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY`. The project's active
version-2 PAUTH has no per-work-item inclusion list and covers source, test, and
governed bridge work for active project members. The legacy WI
`approval_state` value is compatibility metadata and does not grant or revoke
implementation authority. Project PAUTH does not replace independent GO,
work-intent claim, implementation-start, operation-time, verification, or
terminal-finalization gates. The PAUTH continues to forbid dispatcher mutation,
TAFE mutation, Git commit/history/push, release, deployment, credentials,
destructive cleanup, and external-system mutation.

## Requirement Sufficiency

**Existing requirements sufficient.** The active nonimpairment, harness-parity,
project-authorization, bridge-authority, specification-linkage, and
spec-derived-verification requirements completely determine this bounded
repair. No new or revised requirement is needed before implementation. The
remaining prerequisites are lifecycle evidence—a fresh independent GO, exact
claim, passing implementation-start packet, and clean target cohort—not a
requirements gap.

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
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666274` authorizes project-level Harness Parity implementation
  while preserving bridge, independent review, claim, start, verification, and
  operation-time gates.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` requires nonimpairing background
  window containment.
- The 2026-07-15 owner directive forbids resolving console visibility by
  disabling, suppressing, or excluding any harness.
- WI-5298's source owner directive is preserved as historical evidence, but its
  retired project and resolved work item cannot compete with the selected
  active WI-5368 carrier.

## Owner Decisions / Input

No new owner decision is required for review or implementation of this exact
source/test scope under the active whole-project PAUTH. A separate exact
authorization remains necessary before any local terminal commit because the
active PAUTH forbids `git_commit`.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5368 live-observer evidence plus the clean frozen target baseline","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact ChatGPT/conhost ancestry plus exact Codex internal Git-manager markers","before_behavior":"Only the historical add -u form is recognized; other marker-qualified internal Git commands may surface visible consoles.","after_behavior":"Observed marker-qualified Codex internal Git-manager consoles are hidden while every Git command continues and exits naturally.","self_descriptive_naming":"The matcher and tests describe qualifying Codex Git provenance rather than one historical subcommand.","obsolete_guidance_disposition":"The broader argument-independent sibling design is explicitly superseded and not adopted.","history_preservation":"The retired sibling files remain unchanged as historical evidence; v011 records one active carrier and contract.","baseline":{"source_blob":"4b0ed05225b161bd582e53489c393a2b5a7693e9","test_blob":"309f56fa9f7f499815628281c27ccd2890cef13d"},"expected_result":{"focused":"observed exact-marker command forms qualify and all near misses remain rejected","live":"zero visible qualifying windows while commands complete naturally"},"rollback":{"instructions":"use a separately governed exact two-file repair","verification":"focused near-miss suite plus live observation"},"hard_invariants":["hide only","no process-lifecycle action","no Git interception","no dispatcher or TAFE mutation","fail open on ambiguity"],"fail_closed_conditions":["required markers made optional","nested Git ancestry accepted","arbitrary Git consoles hidden","process or dispatcher state changed","target drift or competing owner detected"],"essential_context_preservation":"Retain exact event, process, marker, singleton, project-authorization, and nonimpairment evidence."}
```

## Specification-Derived Verification Plan

| Governing requirement | Verification after GO | Required result |
| --- | --- | --- |
| Project-only authorization and independent review | Fresh exact claim plus schema-v3 implementation-start against v011 and a new independent GO | Active project membership and PAUTH allow the exact two targets; proposal and GO author sessions differ. |
| Marker-qualified command coverage | Focused pytest parameterization over observed command shapes | `write-tree`, `read-tree`, `diff`, `status`, `ls-files`, and pathspec `add` qualify only with both exact markers. |
| Near-miss isolation | Missing, duplicate, malformed, value-near-miss, ancestry, executable, and event tests | Unrelated user/tool Git, nested Git ancestry, and every ambiguous form remain untouched. |
| Hide-only nonimpairment | Static source review and focused side-effect assertions | `ShowWindowAsync(SW_HIDE)` is the sole target-window/process effect; no termination, interception, routing, or mutex mutation exists. |
| Supersession integrity | Strict bridge-chain and target-ownership preflight | The retired sibling is treated only as historical superseded intent and no second executable owner is admitted. |
| Scope and quality | Scoped status/diff/numstat, pytest, Ruff check, Ruff format check, and `git diff --check` | Only the exact source/test hunks exist and every mechanical gate passes. |
| Terminal integrity | Independent review plus separately authorized exact atomic finalization | No file-only VERIFIED; without commit authority the implementation report remains nonterminal. |

## Acceptance Criteria

1. A fresh independent GO approves this v011 single-carrier contract and a
   matching implementation-start packet passes against the clean frozen blobs.
2. Both exact Codex Git markers and the direct ChatGPT/conhost provenance are
   required; the sibling's broader argument-independent and nested-Git rules
   are not implemented.
3. All observed internal command-family shapes qualify, while unrelated,
   malformed, marker-free, non-ChatGPT, nested-Git, non-top-level, and non-Git
   cases remain untouched.
4. Commands continue running and exit naturally, with hide-only behavior and
   no process, Git, dispatcher, TAFE, routing, role, or eligibility mutation.
5. Only the two declared target files may change after GO; any drift or peer
   ownership aborts the start.
6. Terminal verification remains independent and uses an exact atomic
   finalizer only after matching commit authority exists.

## Pre-Filing Preflight Subsection

Before typed publication, the completed candidate must pass the live bridge
applicability and mandatory ADR/DCL clause preflights with authoritative author
metadata, no missing required specifications, no unclassified targets, and no
must-apply evidence or blocking gaps. Any version race, target collision that
the explicit supersession does not resolve, claim loss, authorization denial,
or preflight failure aborts filing.

## Risk And Rollback

The main technical risk is hiding unrelated Git consoles; exact singleton
markers, direct process ancestry, event shape, executable identity, and
fail-open inspection contain it. The governance risk is treating prose
supersession as sufficient while a strict resolver still reports the retired
sibling as an executable owner; that condition explicitly aborts filing or
implementation. Before implementation, rollback is another append-only bridge
disposition. After authorized implementation, rollback is a governed exact
two-file repair. No broad reset, history rewrite, process termination,
dispatcher/TAFE mutation, or manual bridge write is permitted.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
