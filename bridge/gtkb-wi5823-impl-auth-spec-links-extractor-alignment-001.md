NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); the parent interactive session's resolver fallback reports loyal-opposition; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5823-impl-auth-spec-links-extractor-alignment
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5823

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py", "platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py"]
implementation_scope: extractor_grammar_alignment_and_post_go_amendment_path
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5823 Implementation Proposal — Align Impl-Auth Spec-Links Extraction With the Preflight Grammar and Add a Post-GO Formatting-Only Amendment Path

## Summary

Close the grammar divergence between the two gates that read a proposal's `## Specification Links` section. The applicability preflight (`scripts/bridge_applicability_preflight.py`) harvests concrete artifact-ID tokens from any format — bullets, tables, or prose citation lines — so proposals in those formats pass preflight and earn Loyal Opposition GO. The implementation-authorization extractor (`extract_spec_links()` / `section_body()` in `scripts/implementation_authorization.py`) truncates the section at the first `###` subheading and accepts only bullet-form (with a table fallback), so the same GO'd proposal then fails `begin` with "Approved proposal has no concrete specification links". The only self-fix — refiling — flips the thread's latest status to `REVISED`, which `begin` also rejects, structurally forcing one full Loyal Opposition review cycle per formatting tweak. This proposal (a) aligns the extractor grammar so table-form, `###`-subheading-partitioned form, prose-citation form, and bullet-form are all accepted, and (b) adds a fail-closed post-GO amendment path that preserves a live GO for formatting-only corrections without mutating any bridge chain file.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

Self-application note: this proposal's own `## Specification Links` section is deliberately authored in bullet form directly under the h2 heading — the one shape both the current strict extractor and the preflight accept — so this thread cannot itself stall on the defect it fixes.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, the code of record, and fresh `gt backlog show WI-5823 --json` / bridge-chain reads. Line numbers are current-worktree references.

1. **Truncation at `###`.** `section_body()` (line 644) resolves sections through `_iter_sections` (line 621), which uses `SECTION_RE = ^#{2,3}` (line 50). Any `###` subheading is a section boundary, so the body of `## Specification Links` ends at the first `### Required (blocking)`-style subheading. Everything under the subheadings — typically the citation tables — is invisible to the extractor. (The h2/h3 widening was introduced for a different reason: HYG-046 needed `### Requirement Sufficiency` findable as its own section; the side effect is the truncation.)
2. **Bullets-only acceptance.** `extract_spec_links()` (line 820) accepts only lines starting with `-`/`*` (backticked spans preferred), with an additive table fallback (`_extract_spec_links_from_table`, line 773, per DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001) that runs only when the bullet branch yields zero links — and only over the already-truncated body. Compact prose citation lines ("Required (blocking): DCL-…, GOV-…") yield nothing.
3. **The preflight accepts more.** `extract_spec_links()` in `scripts/bridge_applicability_preflight.py` (line 306) harvests `SPEC_ID_RE` tokens (`SPEC|GOV|ADR|DCL|PB|REQ|DELIB` prefixes, line 106) plus `RULE_PATH_RE` rule paths from the section text regardless of bullet/table/prose format. A proposal whose citations sit in a compact prose line or in tables therefore passes preflight, earns GO — and then fails `begin` extraction.
4. **The live shape is the vulnerable shape.** The two gate-clean program templates on this same project — `bridge/gtkb-wi5811-cross-harness-append-only-enforcement-001.md` and `bridge/gtkb-wi5812-goose-governed-filing-attestation-001.md` — both use a compact prose citation line followed by `### Required (blocking)` / `### Advisory` tables. Under the current extractor, both would fail `begin` with "no concrete specification links" after their GOs.
5. **The treadmill on record.** `bridge/gtkb-wi5808-harness-probe-dsv4pro-r1-*`: statuses run NEW(-001) → NO-GO(-002) → REVISED(-003) → GO(-004) → REVISED(-005) → GO(-006) → REVISED(-007) → GO(-008) — three GOs on materially one proposal, ~42 minutes lost, the verification window destroyed (WI-5823 description; DELIB-202667730 synthesis). Each refile was a formatting-only correction chasing `begin` extraction; each flip to `REVISED` invalidated the live GO (`approved_files_for_go`, "found latest status …" rejections at lines 519-535). Recurrence: `gtkb-wi5808-harness-probe-dsv4pro-r2b` (REVISED -003 after GO -002, the "003 cycle") and `gtkb-wi5808-harness-probe-dsv4pro-r3` (msg 214: post-hoc mutation of a GO'd artifact — the ungoverned workaround this proposal's amendment path replaces with a governed, fail-closed one).
6. **Concurrent modification.** `scripts/implementation_authorization.py` is currently being modified in this worktree by the WI-5694 cycle-1 implementation worker (validate/list surfaces); `git --no-optional-locks status` shows the file modified. See the Coordination Note below for sequencing.

## Proposed Design

Three slices, all inside `scripts/implementation_authorization.py`, function-scoped to the extractor/amendment surface only.

### Slice A — Level-aware Specification Links body

Add a targeted helper `_section_body_including_subsections(markdown, heading)` built on the existing `_iter_section_spans()` (line 630), which already yields heading spans whose bodies include nested deeper subsections. `extract_spec_links()` switches from `section_body()` to this helper, so a `## Specification Links` section retains its `###`-subheaded content (tables and bullets under `### Required (blocking)` / `### Advisory` become visible). The two other `section_body()` callers — `Files Expected To Change` (line 870) and `Requirement Sufficiency` (line 1413) — are deliberately untouched: widening them is out of scope and HYG-046's h3-visibility behavior for `### Requirement Sufficiency` is preserved unchanged.

### Slice B — Format alignment: preflight-parity harvest as a third additive branch

`extract_spec_links()` precedence, preserved and extended:

1. **Bullet branch** (existing, unchanged): backticked spans from `-`/`*` lines; per-bullet placeholder check fails closed (`_bullet_has_citation` + `PLACEHOLDER_RE`).
2. **Table fallback** (existing, unchanged, per DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001): runs when the bullet branch yields zero links; dormant whenever bullets exist. Now operates over the level-aware body, so tables under `###` subheadings are reachable.
3. **Preflight-parity harvest** (new, additive): when both prior branches yield zero links, harvest concrete citation tokens from the full level-aware body — backtick spans, uppercase artifact-ID tokens (the existing `_SPEC_ID_RE` class, matching the preflight's `SPEC_ID_RE` acceptance), and `.claude/rules/` paths (mirroring the preflight's `RULE_PATH_RE`). This accepts compact prose citation lines and any format the preflight harvests. By construction the branch yields only concrete tokens: placeholder prose can never become a link, and a section with no concrete token anywhere still raises "Approved proposal has no concrete specification links" exactly as today.

Alignment guarantee (the operative property, tested below): for any proposal content whose Specification Links section produces a non-empty preflight harvest, `extract_spec_links()` succeeds — `begin` can no longer fail on a format the preflight accepted at GO time. For pure-form fixtures (bullet-only, table-only, subheading-only, prose-only) the extracted set also contains every preflight-harvested spec ID. The existing dormant-fallback precedence for mixed documents is deliberately preserved (no amendment to DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001's recorded semantics).

### Slice C — Post-GO amendment path preserving a live GO (formatting-only)

New subcommand:

```text
python scripts/implementation_authorization.py amend-proposal --bridge-id <slug> --amended-file <path>
```

Fail-closed preconditions (ALL required):

1. The thread's post-GO chain state is `latest_is_go` or `resumable` — the same states `begin` accepts. A latest `REVISED`, `NEW`, `NO-ACTION`, `VERIFIED`, or `DEFERRED` state rejects: the amendment path never substitutes for review, revision, or terminal handling.
2. `approved_files_for_go()` resolves the GO'd proposal `-NNN` and its GO verdict.
3. Substance-equivalence gates between the GO'd proposal and the amended content — the amendment is accepted only when it is formatting-only by these checks:
   - preflight-grammar spec-links harvest set equality (the exact substance the Loyal Opposition GO validated);
   - declared `target_paths` set equality;
   - `Requirement Sufficiency` operative-state equality;
   - first-line status token equality and PAUTH triple metadata equality (`Project Authorization` / `Project` / `Work Item` lines);
   - the amended content passes strict extraction (`extract_spec_links` + `extract_target_paths`) — the amendment must actually cure the failure.
4. Effect: a durable amendment record is written to `.gtkb-state/impl-auth-amendments/<bridge-id>.json` carrying the sha256 of the GO'd proposal bytes, the sha256 and full text of the amended content, the equivalence evidence, a UTC timestamp, and the acting session id / author metadata. **No file under `bridge/` is written, rewritten, or deleted.** The numbered chain stays append-only and the GO'd artifact is never mutated — the governed inverse of the r3 post-hoc-mutation anti-pattern.
5. `begin` integration: only when strict extraction on the GO'd proposal raises `AuthorizationError` does `begin` consult the amendment record. It re-verifies the record fresh (stored GO'd-proposal hash must equal the current file bytes — detecting any chain drift after the amendment — and the equivalence gates are re-checked), then extracts from the amended content. The minted packet records `amendment_applied` evidence (record path + both hashes) so the implementation report and the Loyal Opposition verifier see the amendment explicitly. When the GO'd proposal extracts cleanly, any amendment record is ignored: the grammar-aligned direct path always wins.
6. Disclosure obligation: an implementation report for a thread whose packet carries `amendment_applied` evidence must cite the amendment record; the packet evidence fields make that mechanically checkable at verification.

### Rejected alternatives

- **Refile as REVISED (status quo).** Destroys the live GO and forces a full Loyal Opposition cycle per formatting tweak — the exact treadmill on record in dsv4pro-r1/r2b. Rejected as the standing remedy.
- **In-place edit of the GO'd proposal.** Append-only violation; the r3 incident is the recorded anti-pattern. Rejected outright; Slice C is designed so it is never necessary.
- **New bridge status token (e.g. `AMENDED`).** Widens the closed status vocabulary and every routing/dispatch surface for a narrow `begin`-time concern; disproportionate. Rejected.
- **Preflight enforces strict extractability pre-GO (the WI's alternative arm).** Hard-couples the preflight to impl-auth internals and would retroactively NO-GO currently-acceptable formats, moving the breakage earlier instead of removing it. Grammar alignment (impl-auth accepts what the preflight accepts) is the lower-blast-radius direction. A pre-GO extractability advisory could be a follow-on work item if residual gaps appear.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — WI-5823's `source_spec_id`; the constraint whose enforcement surface (`extract_spec_links`) this proposal repairs, and this proposal's own linkage obligation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain (`implementation_authorization.py`) whose `begin` path this proposal aligns; the PAUTH triple in the header proceeds under it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — append-only numbered bridge file chain authority; the amendment path is designed to never write under `bridge/` and to preserve the chain audit trail.
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` — required (blocking) — the existing table-fallback constraint this proposal extends; its recorded bullet-precedence/dormant-fallback semantics are preserved unchanged.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated by this implementation; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under `E:\GT-KB` (`scripts/`, `platform_tests/`); no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — both gates involved here are write-time/review-time mechanical enforcement layers; this proposal restores their two-layer coherence (review-time preflight and implementation-time extractor accepting the same grammar).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence in this proposal derives from fresh canonical reads (live worktree code, `gt backlog show`, `gt projects authorizations`, bridge chain files) made this session.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — the amendment path converts an ungoverned manual workaround (post-hoc mutation) into a deterministic, fail-closed service surface.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (extraction results, packet evidence, chain-byte identity), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the amendment record is a durable, evidence-carrying artifact rather than transient session state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: packet `amendment_applied` evidence ties proposal, amendment, report, and verification together.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin WI lifecycle transitions for WI-5823 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5823 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667730`, `DELIB-202667731`, `DELIB-202667726`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667730** — Harness Test final synthesis: consolidates the evaluation evidence, including the dsv4pro-r1 three-GO treadmill (-004/-006/-008 on materially one proposal, ~42 minutes lost, verification window destroyed), the r2b recurrence (REVISED -003 after GO -002), and the r3 post-hoc mutation of a GO'd artifact (msg 214) that motivate WI-5823.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): the list-free whole-project authorization recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the Harness Test program whose evaluation runs produced this defect record.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`); the evidence bridge chains were verified by direct first-line status-token reads of the numbered files.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5823. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730) covers WI-5823 as a member work item. Per the PAUTH scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5823 defect description (fresh-read verified via `gt backlog show WI-5823 --json`), DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-FILE-BRIDGE-AUTHORITY-001, and the DELIB-202667730 diagnosis evidence fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11779` ("Impl-auth extractor accepts every spec-links format the applicability preflight accepts") is the spec-derived test anchor created with WI-5823 per GOV-12. All new tests land in `platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py` (new module, following the `test_implementation_authorization_extract_spec_links_table.py` convention); the existing table-format module remains green as the precedence regression lock.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001 / TEST-11779 | `test_bullet_form_accepted` | Bullet-form citations directly under `## Specification Links` extract fully (regression; both grammars) |
| WI-5823 / TEST-11779 | `test_table_form_accepted` | Table-form citations directly under the h2 heading extract fully via the table fallback over the level-aware body |
| WI-5823 / TEST-11779 | `test_subheading_form_accepted` | The live wi5811/wi5812 shape — compact prose citation line + `### Required (blocking)` / `### Advisory` tables — extracts fully; a subheading-only variant (tables under `###`, no compact line) also extracts fully |
| WI-5823 / TEST-11779 | `test_prose_citation_form_accepted` | A compact prose citation line alone (no bullets, no tables) extracts its concrete IDs via the preflight-parity branch |
| WI-5823 / DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `test_preflight_parity_property` | Property test over a format-permutation matrix plus live-file fixtures (including `bridge/gtkb-wi5811-cross-harness-append-only-enforcement-001.md` and this proposal's own filed `-001`): wherever the preflight harvest is non-empty, `extract_spec_links()` succeeds; for pure-form fixtures the extracted set contains every preflight-harvested spec ID |
| WI-5823 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_amendment_path_preserves_go` | Tmp fixture chain (NEW → GO over a preflight-passing, strict-extraction-failing proposal): `begin` fails pre-amendment; `amend-proposal` with a formatting-only correction succeeds; `begin` then mints a packet carrying `amendment_applied` evidence; every `bridge/` fixture byte is identical before/after (live GO preserved, zero bridge writes) |
| WI-5823 (fail-closed amendment) | `test_amendment_rejects_substance_change`, `test_amendment_rejects_target_paths_change`, `test_amendment_rejects_requirement_sufficiency_change`, `test_amendment_rejects_non_go_latest_status`, `test_amendment_stale_record_rejected_at_begin` | Changed spec-link substance, changed target_paths, changed Requirement Sufficiency state, latest status not `latest_is_go`/`resumable`, and post-record chain drift each fail closed |
| DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001 (precedence lock) | existing `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` suite | Bullet precedence and dormant table fallback unchanged; empty/placeholder sections still raise |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | `test_placeholder_and_empty_still_fail_closed` | `## Specification Links` with only placeholder prose or no concrete token still raises "no concrete specification links"; per-bullet/table placeholder rejection preserved |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_implementation_authorization_spec_links_grammar.py platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py -q --tb=short` passes green, and the touched selections of `platform_tests/scripts/test_implementation_authorization.py` remain green.
3. Live-shape check: `extract_spec_links()` over `bridge/gtkb-wi5811-cross-harness-append-only-enforcement-001.md` succeeds and includes its required blocking IDs (currently it raises "no concrete specification links").
4. Begin-viability property holds: for every fixture whose applicability-preflight harvest is non-empty, `extract_spec_links()` does not raise.
5. `amend-proposal` writes nothing under `bridge/`; in every amendment test the chain files are byte-identical before and after, and the packet minted post-amendment carries the `amendment_applied` evidence fields.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals.
7. `section_body()` behavior for `Files Expected To Change` and `Requirement Sufficiency` callers is unchanged (existing suite green).

## Risk And Rollback

- **Grammar-widening risk.** The preflight-parity branch could harvest an ID from incidental prose. Mitigated: it fires only when bullet and table branches both yield zero links; it harvests only concrete citation tokens from the same classes the preflight already accepts at GO time (so review saw exactly those tokens); the fail-closed empty/placeholder behavior is unchanged and tested.
- **Amendment-abuse risk.** Mitigated: live-GO precondition, five substance-equivalence gates, zero bridge writes, fresh re-verification at `begin`, packet disclosure evidence, and rejection-path tests for every gate. The path can only cure formatting; any substantive change still requires REVISED + review.
- **Concurrent-edit risk.** `scripts/implementation_authorization.py` is being modified by the WI-5694 cycle-1 worker right now; see the Coordination Note — implementation is sequenced strictly after that lands, and this proposal's edits are function-scoped to a disjoint surface.
- **Rollback** is the exact revert of the one source file and the test modules. Amendment records under `.gtkb-state/` are inert runtime evidence without the consuming code; no MemBase mutation, no dispatcher/TAFE state, and no bridge chain file is touched.

## Coordination Note (sequencing constraint, not scope)

The WI-5694 cycle-1 implementation worker is concurrently modifying `scripts/implementation_authorization.py` (validate/list surfaces); the worktree already shows the file modified. WI-5823 implementation MUST be sequenced AFTER WI-5694 cycle-1 lands (its implementation is committed through its own governed cycle). To keep the diffs disjoint, this proposal targets only the extractor/amendment function surface: the new level-aware body helper, `extract_spec_links()`, the new `amend-proposal` subcommand, and the narrow `begin` extraction-failure consult. No validate/list surface, no other `section_body()` caller, and no shared constant used by the WI-5694 diff is modified. If, at implementation time, the landed WI-5694 diff has moved or renamed a touched function, the implementing session re-baselines line references before editing and notes the re-baseline in the implementation report.

## DISARM — KB Mechanics

This proposal creates and modifies source and test files only. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change; citations of DELIB, spec, WI, and TEST IDs in this proposal are read-only references, not mutations.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5823-impl-auth-spec-links-extractor-alignment`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect (grammar divergence between two enforcement gates that structurally forces redundant review cycles) with regression coverage; the amendment path is remediation plumbing for the same defect class, not a new capability surface.

## Loyal Opposition Review Questions

1. Is the three-branch precedence (bullets → table fallback → preflight-parity harvest, each firing only on zero links from the prior) the right compatibility posture, or should the branches union with the DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001 precedence semantics amended?
2. Are the five substance-equivalence gates sufficient to make `amend-proposal` formatting-only in every practical case, or should additional invariants (e.g., verification-plan section hash) be added?
3. Is consuming the amendment overlay inside `begin` (extraction only, with packet disclosure) acceptable, or should LO require an explicit acknowledgment artifact before a packet may use an amendment?
4. Does the parity property test plus the live wi5811-shape fixture satisfy the spec-derived testing requirement for every linked specification?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
