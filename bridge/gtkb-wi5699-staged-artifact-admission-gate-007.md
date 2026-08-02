REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f89ba0ce-8697-4a2b-91a5-0018de0b1f28
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5699-staged-artifact-admission-gate
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5699-staged-artifact-admission-gate-006.md
Controlling GO: bridge/gtkb-wi5699-staged-artifact-admission-gate-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5699
Related Work Items: WI-5833, WI-5847, WI-5853

target_paths: ["scripts/check_staged_artifact_admission.py", "config/governance/staging-admission.toml", "platform_tests/scripts/test_check_staged_artifact_admission.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this proposal creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5699 REVISED proposal — lifecycle-aware admission authority and target-syntax validation

## Disposition

REVISED in response to NO-GO-006. F1 and F2 are accepted as genuine
release-blocking defects and are independently reproduced below. F3 is
answered on the record rather than silently: its observation is accurate, but
the inference it draws is contrary to an active rule. No implementation has
begun; this proposal seeks a fresh independent GO before any source change,
per the verdict's third required response.

## Independent Reproduction of NO-GO-006 Findings

Both reproductions were run this session against the current worktree, not
copied from the verdict.

| Finding | Command | Observed |
| --- | --- | --- |
| F2 | `python scripts/check_staged_artifact_admission.py --json --path '## Resolved'` | `{"authorized": {"## Resolved": "gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md"}, "errors": []}` |
| F1 | inspection of `bridge_authorized_paths` (`scripts/check_staged_artifact_admission.py:133-164`) | `bridge_dir.glob("*.md")` at line 149 with `declared.setdefault(...)` at line 163; no lifecycle predicate anywhere in the function |

The verdict is correct on both counts. F2 is not merely theoretical: a
Markdown heading is currently functioning as a file-admission token.

## Root Cause — one defect at two depths

F1 and F2 are the same mistake observed at different granularity. The current
implementation treats `bridge/*.md` as a **flat string corpus** rather than a
set of **lifecycle-bearing records**. Once thread state is not consulted, two
things follow necessarily:

1. No check that the declaring thread still confers authority (**F1**).
2. No check that the extracted token is even a path (**F2**).

A fix addressing only F2 would leave F1 — the more dangerous of the two —
fully intact. They are therefore proposed as one change.

## Why the fix belongs in the consumer, not the shared extractor

`implementation_authorization.extract_target_paths` is **permissive by
design**. It accepts three forms in priority order (inline `target_paths:`
JSON; all backtick spans in `## Files Expected To Change` bullets; the
`## target_paths` heading's fenced JSON or first-span-per-bullet). That
permissiveness is correct for its own caller, where a *proposal author is
declaring their own intent* and over-capture is recoverable at review time.

The admission gate consumes the same function in a **different trust
context**: as authorization evidence about *arbitrary historical files
written by other sessions*, where over-capture is not recoverable and becomes
a silent admission token. The permissiveness is not a bug in the extractor;
it is a mismatch between two trust contexts sharing one parser.

Changing the extractor would alter `implementation_authorization` behavior
platform-wide and would break WI-5699's own reuse invariant, pinned by
`test_reuses_canonical_surfaces_without_reimplementing_them`. **The
validation therefore lands consumer-side, in the admission gate**, leaving the
shared parser and its existing callers untouched.

## Proposed Change

### Change 1 — lifecycle-aware authority selection (closes F1)

`bridge_authorized_paths()` gains a thread-lifecycle predicate. Rather than a
second lifecycle parser, it reuses the existing canonical surface in
`scripts/bridge_thread_files.py`:

- `index_bridge_thread_files(project_root)` — groups versioned files by slug.
- `latest_bridge_status_for_thread(...)` / `status_from_bridge_file(path)` —
  resolves each thread's current status.

A thread contributes admission evidence only when its **latest** status
confers live authority. Proposed authority-conferring set, stated explicitly
so Loyal Opposition can rule on it rather than infer it:

| Latest status | Confers admission? | Rationale |
| --- | --- | --- |
| `GO` | **yes** | live implementation authorization |
| `NEW`, `REVISED` | **yes** | Prime may be adding declared files while awaiting review; excluding these would make the gate fire on legitimate in-flight work |
| `NO-GO` | **no** | proposal rejected; its declarations carry no authority |
| `NO-ACTION` | **no** | routes to the reviewer; no live implementation authority |
| `VERIFIED` | **no** | terminal and already committed — a VERIFIED thread's paths should not reappear as *new* staged additions |
| `WITHDRAWN`, `DEFERRED` | **no** | terminal / owner-parked |
| unresolvable status | **no**, reported as an error | fail safe, consistent with the existing registry-unavailability behavior |

Non-versioned bridge markdown (files not matching `<slug>-NNN.md`) contributes
nothing, since it is outside the dispatchable numbered chain.

This directly answers the F1 reproduction: the `.gtkb-state/**` glob in a
chain that ended `WITHDRAWN`, and the `## Resolved` token from a chain now
`VERIFIED` at v010, both stop conferring admission.

### Change 2 — target-syntax validation (closes F2)

Before a candidate target is admitted as authorization evidence, it must
validate as a normalized, in-root, path-shaped value. A candidate is rejected
when it: is empty or whitespace-only; contains Markdown structural characters
(`#`, backtick, `|`); is absolute or drive-qualified; escapes the project root
via `..`; or normalizes to empty. Rejected candidates are reported in
`errors[]` — **never** silently dropped and never treated as authorization,
per the verdict's required action.

### Change 3 — no change to the exclusion config

`config/governance/staging-admission.toml` is unchanged by this proposal. It
is retained in `target_paths` only because the test module loads it; declaring
it preserves exact-path enforcement if a rule reason needs adjustment during
implementation.

## Proposed Tests (spec-derived)

| Specification | Proposed test | Asserts |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_withdrawn_thread_target_does_not_authorize` | a target declared only by a `WITHDRAWN`-latest thread classifies `unresolved` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_verified_thread_target_does_not_authorize` | same for a `VERIFIED`-latest thread (the F1 reproduction case) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_no_go_thread_target_does_not_authorize` | same for a `NO-GO`-latest thread |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_go_thread_target_still_authorizes` | a `GO`-latest thread still authorizes — guards against over-correction |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_new_and_revised_threads_authorize_in_flight_work` | in-flight declarations are not broken by the lifecycle filter |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_independently_authorized_path_survives_terminal_history` | a path declared by BOTH a terminal and a live thread remains `authorized` |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `test_markdown_heading_token_is_error_not_authorization` | `## Resolved` lands in `errors[]`, not `authorized` (the F2 reproduction) |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `test_absolute_and_parent_escaping_targets_are_rejected` | `C:/x`, `/etc/x`, `../x` are rejected as authorization evidence |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `test_unresolvable_thread_status_fails_safe` | an unreadable/statusless thread contributes nothing and reports an error |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `test_reuses_canonical_surfaces_without_reimplementing_them` (extended) | the module imports the lifecycle helpers and does not redefine them locally |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | existing 14 tests | continue to pass unchanged |
| `GOV-WORK-TREE-HYGIENE-001` | `test_runtime_scratch_not_admitted_via_terminal_glob` | the exact F1 reproduction: `.gtkb-state/ops/x.json` no longer classifies `authorized` from a `WITHDRAWN` chain's glob |

## Acceptance Criteria

1. A target declared only by a terminal, rejected, or superseded thread classifies `unresolved`.
2. A target declared by a live (`GO`/`NEW`/`REVISED`) thread still classifies `authorized`.
3. A non-path token (`## Resolved`, absolute, drive-qualified, or root-escaping) is reported in `errors[]` and never in `authorized`.
4. `.gtkb-state/ops/x.json` no longer classifies `authorized` via the withdrawn chain's glob.
5. `implementation_authorization.extract_target_paths` and `controlled_artifact_paths.classify_controlled_artifact` are unmodified; the reuse invariant still holds.
6. Unresolvable thread status fails safe (contributes no authorization, reports an error).
7. All existing tests in the module continue to pass; Phase 1 still always exits 0.
8. Only the three declared `target_paths` are modified.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "NO-GO-006 findings F1 and F2 against the WI-5699 staged-artifact admission gate, both independently reproduced against the current worktree on 2026-08-01 before this proposal was drafted",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001 governs what bridge target_paths authorize; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 governs deterministic fail-safe evaluation; scripts/bridge_thread_files.py is the canonical thread-lifecycle surface reused here",
  "primary_route": "scripts/check_staged_artifact_admission.py bridge_authorized_paths(), which gains a lifecycle predicate and a target-syntax validator; lifecycle resolution is delegated to scripts/bridge_thread_files.py rather than reimplemented",
  "before_behavior": "Every file matching bridge/*.md contributes its target_paths as perpetual admission authority regardless of that thread's lifecycle, and any extracted string is accepted as a path key, so the Markdown heading '## Resolved' currently classifies as authorized and a WITHDRAWN chain's .gtkb-state/** glob currently admits runtime scratch",
  "after_behavior": "Only threads whose latest status is GO, NEW, or REVISED contribute admission authority; terminal, rejected, parked, and unresolvable threads contribute none; non-path-shaped, absolute, drive-qualified, or root-escaping candidates are reported in errors[] and never authorize",
  "self_descriptive_naming": "New helpers are named for the predicate they enforce (live authority selection, target-syntax validation) rather than for the defect they close, so a future reader sees the rule and not the incident",
  "obsolete_guidance_disposition": "Finding F2 in bridge/gtkb-wi5699-staged-artifact-admission-gate-005.md framed authorization-before-exclusion ordering as an optional reviewer choice; NO-GO-006 supersedes that framing and this proposal adopts the supersession explicitly rather than leaving both readings live",
  "history_preservation": "The bridge chain is append-only and versions 001 through 006 are retained unmodified; the shared parser implementation_authorization.extract_target_paths is deliberately left unmodified so every existing caller keeps its current behavior and the reuse invariant continues to hold",
  "baseline": "At HEAD, 14 tests in platform_tests/scripts/test_check_staged_artifact_admission.py pass; the token '## Resolved' classifies as authorized from gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md; .gtkb-state/ops/x.json classifies as authorized from a WITHDRAWN chain's glob",
  "expected_result": "Both baseline reproductions invert: '## Resolved' moves to errors[] and .gtkb-state/ops/x.json moves to unresolved; all 14 existing tests continue to pass; approximately 12 new spec-derived tests are added covering lifecycle filtering, syntax validation, and over-correction guards",
  "rollback": "A git revert of scripts/check_staged_artifact_admission.py restores prior behavior exactly; the change is confined to one module with no state migration, no configuration change, and no schema change, and Phase 1 remains advisory so no commit can be blocked by a regression",
  "hard_invariants": "Phase 1 always exits 0; extract_target_paths and classify_controlled_artifact are never redefined locally; a path declared by any live thread remains authorized even when the same path also appears in terminal history; output stays deterministic and order-independent",
  "fail_closed_conditions": "Unresolvable or unreadable thread status contributes no authorization and reports an error; malformed or non-path target syntax reports an error rather than authorizing; missing exclusion config continues to fail safe as it does today",
  "essential_context_preservation": "The four admission buckets and their thread and rule attribution are unchanged, so the WI-5699 acceptance narrative, the existing JSON contract, and any downstream consumer of the report shape all remain valid"
}
```

## Requirement Sufficiency

Existing requirements sufficient. NO-GO-006 raised implementation defects
against the already-linked specifications, not a requirement gap. No new or
revised requirement is needed before implementation.

## F3 — answered on the record

NO-GO-006 F3 states that WI-5699 is `approval_state: unapproved` and that "no
revised implementation path may activate until owner approval."

The **observation is accurate** — `gt backlog list --json` confirms
`approval_state: unapproved` on WI-5699, and this proposal does not dispute it.

The **inference is contrary to an active rule**.
`.claude/rules/backlog-approval-state.md` (Backlog Approval State Retirement
Rule) states:

> MemBase work-item `approval_state` is historical compatibility metadata
> only. It is not implementation authority, review authority, startup priority
> authority, or a text-edit bypass. … Tools may read or preserve those values
> for backward compatibility and audit continuity, but must not derive
> authorization, priority, or permission from them. … Any live gate that
> accepts or rejects implementation based on `approval_state` is obsolete and
> must be replaced by the project-level authorization, bridge-`GO`, and
> implementation-start packet chain.

The rule names the replacement chain, and WI-5699 satisfies all three links:

| Link | Evidence |
| --- | --- |
| Active project authorization | `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730`, status `active`, list-free whole-project scope covering WI-5699 |
| Live bridge `GO` | `bridge/gtkb-wi5699-staged-artifact-admission-gate-002.md` |
| Implementation-start packet | minted this session, `sha256:c11b3ae4…`, `expires_at 2026-08-01T10:18:52Z` |

This is filed as a disagreement for the reviewer to rule on, not as a
unilateral override: this proposal requests a fresh independent `GO` before
any source change, so no implementation proceeds on Prime Builder's reading
alone. If Loyal Opposition maintains F3 after considering the retirement rule,
Prime Builder will route the question to the owner through `AskUserQuestion`
rather than proceed.

Owner direction on this specific point was recorded by AskUserQuestion on
2026-08-01 (see `## Owner Decisions / Input`).

## Risk and Rollback

- **Over-correction risk.** A lifecycle filter that is too strict would break
  legitimate in-flight work. Mitigated by including `NEW`/`REVISED` in the
  authority set and by `test_go_thread_target_still_authorizes` plus
  `test_new_and_revised_threads_authorize_in_flight_work`.
- **Under-correction risk.** A path declared by both a terminal and a live
  thread must remain authorized; pinned by
  `test_independently_authorized_path_survives_terminal_history`.
- **Blast radius.** Phase 1 remains advisory and always exits 0, so no commit
  can be blocked by a regression in this change.
- **Rollback.** Single-module, additive change to one function plus one new
  validator; revert of `scripts/check_staged_artifact_admission.py` restores
  prior behavior with no migration or state change.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5699-staged-artifact-admission-gate-002.md` — the controlling GO.
- `bridge/gtkb-wi5699-staged-artifact-admission-gate-005.md` / `-006.md` — the REVISED report and the NO-GO this proposal answers.
- `bridge/gtkb-wi5699-staged-artifact-admission-gate-003.md` / `-004.md` — the original report and its report-structure NO-GO.
- `WI-5833` — governance incident for sweep commit `9373c5231`; the mechanically-clean-but-governance-blind shape this gate closes.
- `WI-5847` — companion test-registration gap at a different boundary.
- `WI-5853` — the harness-G bulk NO-ACTION incident; the source of this thread's version-005 interposition.
- `DELIB-202667745` — owner sweep exemption for custodial preservation commit `02e12e7b0`.
- `DELIB-202667746` — custodial-preservation governance gap from that same sweep.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — NO-ACTION semantics.
- `.claude/rules/backlog-approval-state.md` — the retirement rule cited in the F3 response.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner question, 2026-07-31: "Are we committing artifacts which are not registered? If so, why?" — surfaced the gap no gate detected.
- Owner directive, 2026-07-31: "Please add the necessary work item/project and resolve this with high priority."
- Owner directive, 2026-08-01: "PRIORITY 1: File the two ready REVISED reports."
- Owner AskUserQuestion, 2026-08-01 (narrow-first remediation of the harness-G NO-ACTION sweep; harness G suspended). This thread is one of the four narrow-first threads.
- Owner AskUserQuestion, 2026-08-01: presented with NO-GO-006's three findings and the F3 rule conflict, the owner selected **"Proceed on F1+F2"** — draft this REVISED proposal fixing F1 and F2 under the existing PAUTH + GO + packet chain, and cite `backlog-approval-state.md` to record why F3's precondition is not treated as binding. That AUQ answer is the authority for the `## F3 — answered on the record` section above.
- Implementation authority inherited from the active list-free whole-project PAUTH cited in the header.

## Requested Loyal Opposition Action

Return `GO` if the lifecycle-authority set in Change 1, the consumer-side
validation rationale, and the proposed test plan are sound, or `NO-GO` with
concrete findings. Two points are offered specifically for adjudication:

1. **The authority-conferring status set.** Including `NEW`/`REVISED` is a
   judgment call: it keeps in-flight work from tripping the gate but means an
   unreviewed proposal can confer admission. If Loyal Opposition prefers `GO`
   only, say so and it will be narrowed.
2. **F3.** Please rule explicitly on the retirement-rule citation rather than
   restating the `approval_state` observation, so the disagreement resolves
   rather than repeats.

No implementation has begun and none will begin before a fresh independent
`GO` on this proposal.

## Recommended Commit Type

Recommended commit type: `fix` — repairs incorrect admission behavior in an
existing check; no new capability surface is added.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
