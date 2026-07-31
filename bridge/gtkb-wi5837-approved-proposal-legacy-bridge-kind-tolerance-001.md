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
Document: gtkb-wi5837-approved-proposal-legacy-bridge-kind-tolerance
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5837

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight_legacy_proposal_kind.py"]
implementation_scope: approved_proposal_resolver_legacy_bridge_kind_tolerance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5837 Implementation Proposal — Legacy Bridge-Kind Tolerance in the Approved-Proposal Resolver

## Summary

Threads whose first version predates the `bridge_kind` convention are wedged from both directions with no lawful authoring choice between them. The applicability preflight's approved-proposal resolver recognizes a proposal only by its declared `bridge_kind` marker; a pre-convention proposal declares none, so on such a thread the resolver can never bind and every correctly-labeled implementation report fails the mandatory preflight closed. The only escape — mislabeling the report as a proposal — routes the project-authorization evaluation to the proposal phase and then fails the finalize-time protected-commit checker, which requires the linked Prime artifact to declare exactly `bridge_kind: implementation_report`. First versions are append-only and cannot be relabeled, so the wedge is not curable by authoring; the fix must be resolver-side.

This proposal adds a narrow, deterministic legacy-tolerance path to the preflight's approved-proposal resolver: a version that declares no `bridge_kind` marker at all may be recognized as proposal-kind only when it independently proves proposal shape and proposal role through structural signals the thread already carries. The strict marker path keeps precedence; the legacy branch fires only when the marker-based scan finds nothing. It also replaces the resolver's single generic failure sentence with a per-version diagnostic naming what was examined and why each candidate was rejected.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5837-approved-proposal-legacy-bridge-kind-tolerance-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, the code of record, `gt backlog show WI-5837 --json`, `gt projects show-authorization`, direct MemBase reads, and first-line status-token reads of the numbered bridge files. Line numbers are current-worktree references at index blob `c9de9bca` (see Coordination Note).

1. **File-side rejection.** In `scripts/bridge_applicability_preflight.py`, `_approved_proposal_for_report()` (line 804) accepts a candidate only when `_bridge_kind(candidate_content)` is in `PROPOSAL_BRIDGE_KINDS` (line 130) — the frozenset `{prime_proposal, implementation_proposal}` — in both its explicit-hatch arm (line 842) and its candidate-scan arm (line 860). A version that declares no marker yields `None` from `_bridge_kind()` (line 780) and is excluded by both arms. With zero candidates the resolver returns the blocking error `Implementation report has no readable earlier proposal-kind artifact with a matching GO verdict`, which `build_packet` converts into `PAUTH operation-time evaluation failed closed: …` and a false `preflight_passed`.

2. **Finalize-side requirement.** In `scripts/check_protected_commit_authorization.py`, `_approved_chain()` (line 1373) reads the linked Prime artifact and raises `linked Prime artifact is not an implementation report` unless `IMPLEMENTATION_REPORT_RE` (line 60, `^bridge_kind:\s*implementation_report\s*$`) matches at line 1384. Declaring that exact value is therefore mandatory to finalize — and is precisely the declaration that routes the file-side resolver into the failure above.

3. **The double wedge is real, and it is asymmetric in a way that localizes the fix.** `_approved_chain` resolves the proposal *structurally*: it walks `go.responds_to` and requires only `status in {NEW, REVISED}` and `author_role == "prime-builder"` (lines 1397-1399). It performs **no** `bridge_kind` check on the proposal. The preflight requires a marker the checker does not. That divergence is the root defect: the two gates hold different notions of "proposal-kind", and on a legacy thread the intersection of the two notions is empty. Converging the preflight onto the checker's structural notion (extended by the marker when present) makes the intersection non-empty and is sufficient — no finalize-side legacy tolerance is required.

4. **Live casualty, verified.** On `gtkb-wi5694-terminal-evidence-packet-validator` the current chain is: `-001` NEW / no marker, `-002` GO, `-003` NEW / no marker, `-004` NO-GO, `-005` REVISED / `implementation_report`, `-006` NO-GO, `-007` REVISED / `implementation_report`. `-001` declares `target_paths` and a `Project Authorization` line, and `-002` carries `Responds to: bridge/gtkb-wi5694-terminal-evidence-packet-validator-001.md`, which matches `OPERATIVE_REFERENCE_RE` (line 101) — so `-001` is a GO-approved proposal in every respect except the marker it could not have carried. Under the current resolver `-001` and `-003` are excluded for having no marker and `-005` for having a finalization marker, leaving zero candidates: exactly the recorded failure.

5. **Fresh-read corrections to the work-item narrative.** Two details in the WI-5837 `status_detail` did not survive verification and are corrected here: `-005` carries `implementation_report`, not `prime_proposal`; and `-007` is already present on disk (untracked) as REVISED / `implementation_report`, so the pending revision is filed rather than only drafted. The draft at `.gtkb-state/propose-drafts/wi5694-007-revised.md` also still exists. Neither correction changes the defect or its remedy; both are recorded so the reviewer is not reconciling a stale narrative.

6. **The negative discriminator is available in live data.** On the same thread `-003` is a legacy *report* with no marker. It declares no `target_paths`, and no GO verdict names it as operative (`-004` is NO-GO). It is therefore excluded by the proposed positive signals without relying on the marker at all — evidence that structural recognition separates legacy proposals from legacy reports on a real chain rather than only in fixtures.

7. **Independent corroboration.** Loyal Opposition recorded the same class independently at `bridge/gtkb-wi5757-advisory-router-dedup-starvation-004.md` finding F1 ("Report lacks a GO-linked proposal-kind ancestor"), observing the identical blocking error under operation-time PAUTH evaluation and prescribing a chain repair. F1's prescription is the authoring-side workaround; this proposal supplies the resolver-side remedy that F1's own thread would also need, since a chain whose first version predates the convention cannot be repaired by appending.

## Proposed Design

All changes are confined to `scripts/bridge_applicability_preflight.py` plus one new test module. Nothing in the finalize-time checker is modified — see the Coordination Note.

### Slice A — Deterministic legacy proposal-kind recognition

Add a helper alongside the resolver that answers one question: is this version a pre-convention proposal? It returns True only when **every** condition holds:

1. **Marker absent, never mismatched.** `_bridge_kind(content) is None`. A version declaring any other value (`lo_verdict`, `implementation_report`, `implementation_report_revision`, or any future kind) is never tolerated. Tolerance attaches to the absence of the convention, not to disagreement with it.
2. **A Loyal Opposition GO names it operative.** The existing `approved_by_go(version)` closure already requires a later GO verdict that references this exact slug and version through `OPERATIVE_REFERENCE_RE`. This is the strongest available positive signal: an LO reviewer treated this version as the operative proposal.
3. **Proposal shape.** `extract_declared_target_paths(content)` is non-empty. Proposals declare an authorized target scope; reports on these legacy threads do not.
4. **Prime-authored proposal status.** The first-line status token, via the existing `_status_from_content`, is `NEW` or `REVISED`.
5. **No report-only marker.** The content declares neither an `Approved proposal:` nor a `Controlling GO:` line. Defense in depth against a legacy artifact that is report-shaped in every other respect.

Conditions 2-4 are the positive signals the mandate requires; condition 1 bounds the tolerance to pre-convention artifacts and condition 5 is the negative guard. A version that is merely missing a marker is never promoted.

**Precedence.** The legacy branch is evaluated only after the strict marker-based scan yields zero candidates, so no thread whose proposal carries a marker changes behavior in any way. In the explicit `Approved proposal:` arm the same helper is consulted only when the named version fails the marker test, preserving the arm's existing same-thread, must-precede, and matching-GO checks unchanged.

**Version selection.** When multiple legacy candidates qualify, the resolver keeps the existing `max(...)` highest-version-wins rule, so a legacy REVISED proposal supersedes a legacy NEW proposal on the same chain. Restricting tolerance to version `001` was considered and rejected below.

### Slice B — Explicit resolution diagnostic

`TEST-11788`'s recorded expected outcome requires that resolution failure "emits an explicit diagnostic naming the unresolved version". The resolver currently emits one generic sentence naming nothing. Replace it with a message that enumerates each earlier version examined and the specific disqualifying reason per version — declared marker value, no matching GO, no declared target paths, non-proposal status token, or unreadable — so a reviewer reading a NO-GO can see which artifact to look at instead of re-deriving the scan by hand. The failure remains fail-closed; only its legibility changes.

### Slice C — Recognition provenance in the packet

Record how the proposal was resolved — by marker or by legacy tolerance — together with the resolved path, in the `project_authorization_operation_time` block, and surface it in the markdown table so a Loyal Opposition verdict states on its face that tolerance was exercised. Silent tolerance would be the failure mode of this change; the evidence field is what keeps it visible.

**Hash-material sequencing (LO decision requested).** The `stable_pauth` projection in `_packet_hash_material` enumerates its keys explicitly, so adding a recognition field changes the packet hash. That projection and `PACKET_HASH_SCHEMA_VERSION = 3` are themselves part of the uncommitted WI-5811 baseline this proposal layers on. The proposal's default is to add the field inside the same unlanded schema-3 envelope, since no committed packet hash can yet depend on schema 3. If, at implementation time, WI-5811 has landed and any recorded packet hash already depends on schema 3, the implementing session mints `PACKET_HASH_SCHEMA_VERSION = 4` instead and records the bump in the implementation report. Review question 2 asks Loyal Opposition to confirm this conditional.

### Slice D — Regression coverage

New module `platform_tests/scripts/test_bridge_applicability_preflight_legacy_proposal_kind.py`. The load-bearing test is a cross-gate agreement test: a temporary legacy chain (`-001` NEW with no marker and declared target paths, `-002` GO responding to `-001`, `-003` report declaring `implementation_report` and its controlling GO) must clear **both** the file-time preflight and the finalize-time chain resolution. The finalize half drives the checker's `_approved_chain` over a stub resolution mirroring the real audit-version shape; the checker is imported and exercised read-only and is not modified, so it is not a target path.

### Rejected alternatives

- **Relabel the legacy first version.** Impossible and prohibited: bridge files are append-only under GOV-FILE-BRIDGE-AUTHORITY-001, and rewriting a GO'd artifact is the recorded anti-pattern.
- **Add a legacy tolerance to the finalize-time checker too.** Unnecessary and higher-blast-radius. The checker's proposal recognition is already structural (Problem Statement item 3); its only marker requirement is on the report, which becomes satisfiable the moment the file side stops rejecting that declaration. Modifying the checker would also collide with two live claims on that file for no gain.
- **Restrict tolerance to version `001`.** Narrower but wrong: a legacy thread whose proposal was revised after a NO-GO carries its operative pre-convention proposal at `-003` or later, and this rule would leave those threads wedged while adding no safety the GO-approval and shape signals do not already provide.
- **Tolerate any version missing a marker whenever the thread has any GO.** Rejected as exactly the silent-promotion rule the mandate warns against: it would admit legacy reports and unrelated artifacts. The per-version GO-operative reference plus proposal shape is what makes recognition specific.
- **Widen `PROPOSAL_BRIDGE_KINDS` or treat `None` as a member.** Equivalent to the previous item with the guards removed, and it would corrupt `_pauth_phase`, which reads the same frozenset to classify the artifact under review.
- **Make the preflight skip the resolver on legacy threads.** Would silence the gate rather than satisfy it, removing finalization-phase authorization evaluation from exactly the threads that already lack it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — WI-5837's source spec; append-only numbered bridge chain authority. The append-only property is the reason the fix must be resolver-side, and no bridge file is written or rewritten by this implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-authorization chain whose operation-time evaluation this resolver gates; the header PAUTH triple proceeds under it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation, and the constraint carried by the preflight surface being repaired.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the mapping below is the derivation record the verifier executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under scripts and platform_tests; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the defect is a two-layer defense-in-depth incoherence between a write-time gate and a review-time gate; this restores their agreement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — every claim derives from fresh canonical reads made this session, including two corrections to the work-item narrative.
- `SPEC-1662` — advisory — assertion quality: the tests assert behavioral outcomes (resolution results, cross-gate agreement, diagnostic content), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the recognition-provenance evidence field makes tolerance a durable, reviewable artifact rather than invisible runtime behavior.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: packet evidence ties proposal, GO, report, and verification together across the legacy boundary.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5837 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5837 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — replaces a per-thread manual escape (mislabeling artifacts to satisfy one gate at the cost of the other) with deterministic resolver behavior.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667731`, `DELIB-202667730`, `DELIB-202667726`, `DELIB-202667723`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with role-transition plan: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667731** — Harness Test Corrections whole-project authorization decision: the list-free grant recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 under which this proposal is filed.
- **DELIB-202667730** — Harness Test final synthesis: the corrections program that carries WI-5837 as a member work item.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the program whose runs surfaced this defect class.
- **DELIB-202667723** — Terminal-evidence-sufficient decision on expired implementation-start packets: cited because its implementation is the concurrent WI-5824 change staged in the finalize-time checker, and this proposal's Coordination Note establishes disjointness from it.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase; the evidence bridge chains were verified by direct first-line status-token and metadata reads of the numbered files.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5837. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731** — the owner's list-free whole-project grant covers WI-5837 as a member of PROJECT-GTKB-HARNESS-TEST-CORRECTIONS. Verified fresh this session: status active, no expiry, no included or excluded work-item lists, allowed mutation classes include source, test, and test_addition. Per the grant's scope summary this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. One decision is requested of Loyal Opposition rather than the owner: the packet-hash sequencing conditional in Slice C. No new owner decision is required to review this proposal, and this proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5837 defect record (fresh-read verified), its source spec GOV-FILE-BRIDGE-AUTHORITY-001, its spec-derived test TEST-11788 with its recorded expected outcome, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, and the live code of record on both gates fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11788` ("Implementation reports on pre-bridge_kind legacy threads resolve their approved proposal", spec `GOV-FILE-BRIDGE-AUTHORITY-001`) is the spec-derived anchor. Its recorded expected outcome has two obligations — resolution succeeds and reaches finalization-phase evaluation, and resolution failure emits an explicit diagnostic naming the unresolved version — and both are asserted below.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11788 obligation 1 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_legacy_first_version_resolves_as_approved_proposal` | A report declaring implementation_report on a chain whose GO'd first version has no marker resolves that version as its approved proposal; the packet reaches finalization-phase evaluation with no approved-proposal blocking error |
| TEST-11788 obligation 2 | `test_unresolved_diagnostic_names_each_examined_version` | When no candidate qualifies, the blocking error names every earlier version examined with its per-version disqualifying reason |
| WI-5837 / GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | `test_cross_gate_agreement_on_legacy_chain` | The load-bearing regression: one temporary legacy chain clears the file-time preflight and the finalize-time `_approved_chain` resolution, proving both gates admit the same lawful authoring choice |
| WI-5837 (silent-promotion guard) | `test_legacy_report_without_target_paths_rejected`, `test_version_with_non_proposal_marker_never_tolerated`, `test_version_without_operative_go_rejected`, `test_report_only_marker_rejected`, `test_non_prime_status_token_rejected` | Each positive and negative signal is independently load-bearing: removing any one causes the candidate to be rejected |
| WI-5837 (precedence lock) | `test_marker_path_takes_precedence_over_legacy` | On a chain carrying both a marker-bearing proposal and a marker-less candidate, the marker-bearing version is resolved and the legacy branch does not fire |
| WI-5837 (legacy revision) | `test_highest_legacy_version_wins` | With two qualifying legacy candidates the highest version is resolved |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (no-regression) | existing `platform_tests/scripts/test_bridge_applicability_preflight.py` suite | Marker-based resolution, phase classification, spec-links harvesting, and blocking-error behavior are unchanged for all non-legacy threads |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `test_packet_records_recognition_provenance` | The packet and rendered markdown state whether resolution used the marker path or legacy tolerance, and name the resolved path |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight_legacy_proposal_kind.py platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short` passes green.
3. Live-chain check: running the applicability preflight against a report that declares implementation_report on `gtkb-wi5694-terminal-evidence-packet-validator` no longer reports the approved-proposal blocking error, and the packet names `bridge/gtkb-wi5694-terminal-evidence-packet-validator-001.md` as the resolved proposal under legacy recognition.
4. Cross-gate agreement holds: the same fixture chain that passes the preflight also resolves through the finalize-time chain resolution.
5. No thread whose proposal carries a `bridge_kind` marker changes resolution behavior; the marker path retains precedence.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals.
7. No file under `bridge/` and no MemBase record is written by the implementation; `scripts/check_protected_commit_authorization.py` is not modified.

## Risk And Rollback

- **Over-tolerance risk (the material risk).** A rule that promoted a non-proposal would let an unreviewed artifact stand in for a GO'd proposal. Mitigated by requiring all five signals conjunctively, by keeping the marker path in precedence, by the per-signal rejection tests, and by making recognition provenance visible in the packet so a reviewer can see tolerance was used. The live `-003` case demonstrates the guards excluding a real legacy report.
- **Under-tolerance risk.** Guards too strict would leave threads wedged. Mitigated by the highest-version rule for legacy revisions and by the Slice B diagnostic, which converts a silent stall into a legible one naming the artifact that failed to qualify.
- **Hash-material risk.** Adding a packet field changes the packet hash. Bounded by the Slice C sequencing conditional and the explicit LO decision request.
- **Concurrent-edit risk.** `scripts/bridge_applicability_preflight.py` carries staged WI-5811 work. See the Coordination Note; the change is function-scoped and sequenced.
- **Rollback** is the exact revert of the one source file's resolver functions and deletion of the new test module. No MemBase mutation, no dispatcher/TAFE state change, no bridge chain write, and nothing to migrate.

## Coordination Note (sequencing constraint, not scope)

**Baseline.** Both files involved are staged-modified with clean worktrees at HEAD `8a35eabc8`. The rebase baseline for this work is the **index** content of `scripts/bridge_applicability_preflight.py`, blob `c9de9bca` — not HEAD. This matters: the entire approved-proposal resolver this proposal repairs (`_approved_proposal_for_report`, `PROPOSAL_BRIDGE_KINDS`, `_pauth_phase`, the operation-time PAUTH block, and the schema-3 hash bump) exists **only in that staged content** and is absent from HEAD. This proposal must be implemented on top of the staged WI-5811 work, never against HEAD.

**Relationship to the concurrent preflight work.** `scripts/bridge_applicability_preflight.py` is GO'd WI-5811's target and is currently staged. This change **composes with** that work: it layers legacy tolerance onto the resolver WI-5811 introduced. It does not supersede it and does not duplicate it. Verified this session by reading the staged diff in full: the staged `_approved_proposal_for_report` contains no legacy-tolerance path, and both of its arms test `PROPOSAL_BRIDGE_KINDS` strictly. An independent session may have been working this same area under the label "Fix preflight resolver blind to pre-bridge_kind proposals"; as of this filing no such fix is present in the index or the worktree. If one lands before implementation, the implementing session must re-read the resolver first and, if the tolerance is already present, file a REVISED entry reducing this thread to the residual gap (most likely Slices B-D) rather than re-implementing Slice A.

**Relationship to the finalize-time checker.** `scripts/check_protected_commit_authorization.py` is staged with WI-5824's changes (the DELIB-202667723 terminal-evidence fix in `_load_finalized_packet` and the null-safe capability timestamp guard) and is also GO'd WI-5742's target. This proposal **does not modify that file at all** and does not list it as a target path. Disjointness is total, not merely function-level: the finalize side needs no legacy tolerance because its proposal recognition is already structural, and its new test coverage exercises `_approved_chain` read-only. No sequencing dependency runs in either direction.

**Sibling defect family (named, not absorbed).** The finalize-time checker also enforces a `Controlling GO:` header requirement that no authoring-time gate surfaces: a report responding to a NO-GO must declare its controlling GO explicitly or `_approved_chain` raises `implementation report is not linked to its approving GO`. The live `-007` on the WI-5694 thread responds to `-006` (NO-GO) and declares no `Controlling GO:` line, so it will meet that precondition after this fix lands. This is the same defect **family** — finalize-time preconditions invisible to authoring gates — but a distinct defect with a distinct remedy, and it is deliberately out of scope here. The distinction that matters for scoping: the `Controlling GO:` precondition is curable by authoring (a report can declare the header), whereas the legacy `bridge_kind` wedge is not, because first versions are append-only. This proposal fixes only the incurable half; unwedging the WI-5694 thread end to end requires both.

## DISARM — KB Mechanics

This work performs no MemBase mutation. The implementation creates and modifies source and test files only. Citations of DELIB, spec, work-item, and test IDs in this proposal are read-only references.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5837-approved-proposal-legacy-bridge-kind-tolerance`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect that renders a governance gate unsatisfiable on a class of threads, with regression coverage. No new capability surface is added.

## Loyal Opposition Review Questions

1. Are the five conjunctive signals the right recognition rule, or should tolerance additionally require that no later version on the chain declares a proposal-kind marker (a stricter "the thread is wholly pre-convention" test)?
2. Slice C sequencing: is adding the recognition-provenance field inside the unlanded schema-3 envelope correct, or should the implementation mint schema 4 unconditionally?
3. Is confining the change to the preflight — on the finding that the finalize-time checker's proposal recognition is already structural — the correct scope, or does Loyal Opposition want a matching explicit predicate in the checker so the two notions of proposal-kind cannot silently diverge again?
4. Does the cross-gate agreement test, driving `_approved_chain` over a stub resolution, satisfy the spec-derived testing requirement for the finalize half, or is a heavier end-to-end fixture required?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
