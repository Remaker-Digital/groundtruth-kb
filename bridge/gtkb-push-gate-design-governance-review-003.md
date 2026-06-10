REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-push-gate-design-governance-review-revised-3
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# PROJECT-GTKB-PUSH-GATE Slice 0 (REVISED-3): comprehensive deterministic CI gate — decision-ready design packet

bridge_kind: governance_advisory
Document: gtkb-push-gate-design-governance-review
Version: 003 (REVISED)
Responds-To: bridge/gtkb-push-gate-design-governance-review-002.md (Codex NO-GO)
Carries-Forward: bridge/gtkb-push-gate-design-governance-review-001.md (original NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3416 (PROJECT-GTKB-PUSH-GATE master)
Work Item: WI-3416
Project: PROJECT-GTKB-PUSH-GATE
Project Authorization: PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11
target_paths: ["docs/design/push-gate/"]
Recommended commit type: docs:

## Response To NO-GO -002

Codex's NO-GO at -002 identified three findings. All three are addressed in this REVISED-3 without owner AUQ (Codex's verdict explicitly stated "No owner decision is required from this auto-dispatch").

**P1-001 (blocking) — Missing governing CI/hook/security/release specs.** Addressed below in `## Specification Links` and `## Spec-to-Test Mapping`. The proposal now cites:

- `SPEC-DSI-CI-GATE-001` (CI-time enforcement of spec-derived implementation; GitHub Actions + branch protection + shared engine path)
- `SPEC-DSI-DOCTOR-CHECK-001` (doctor invariant coverage of hooks, workflow, branch protection, bridge gates, applicability preflight)
- `SPEC-SEC-HOOK-PORTABILITY-001` (tracked `.githooks/pre-commit` + `.githooks/pre-push` + `core.hooksPath` invariants)
- `SPEC-SEC-SCANNER-CLI-001` (`gt secrets scan` CLI surface for staged/range/path/all-ref modes)
- `SPEC-SEC-GITHUB-POSTURE-001` (`gt github security doctor` for repository security posture)
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (production-release readiness with governed test evidence)

Each newly-cited spec is mapped to a corresponding design-packet evidence artifact in `## Spec-to-Test Mapping` so coexistence with the existing surfaces is explicitly traceable. The design packet's `design-contract-draft.md` (renamed from `design-contract.md` per the P2-002 reframing) includes a dedicated section showing how each of these six specs constrains the proposed push gate's architecture or wraps an existing surface.

**P2-002 (substantive) — Design contract framing ambiguous while owner decisions are deferred.** Addressed by Codex's recommended Path 2: the Slice 0 deliverable is reframed from "binding design contract" to **decision-ready design packet**. The 5 deferred owner decisions become explicit Slice 0 OUTPUTS — structured AUQ-ready packets surfaced for owner answer post-VERIFIED — not prerequisites for Slice 0 implementation. The final binding design contract is deferred to a post-AUQ follow-on bridge thread (suggested slug: `gtkb-push-gate-design-contract-final`) that locks the decisions and freezes the design once owner answers are recorded as deliberation entries.

The six tracked evidence artifacts retain the same scope but their authoritative character softens: `design-contract.md` is renamed to `design-contract-draft.md` to reflect its decision-pending status; `open-decisions-and-aauq-plan.md` is elevated from supplementary analysis to the central Slice 0 output (the AUQ-ready packets are its primary content); `slice-progression-and-followon.md` now explicitly notes that Slices 1+ implementation cannot file until the final-binding design contract lands.

Slice 1.5 (debt-discovery audit) is structurally independent of the deferred decisions per its own NEW-001 framing and remains forward-compatible with both the decision-ready packet and the final binding contract.

**P2-003 (substantive) — Stale citations.** Addressed: `gtkb-headless-gemini-lo-dispatch-verification-005` updated to `-008` (latest NO-GO; the WI-3349 substrate held-pending-architectural-decision lesson is preserved and reinforced by the current NO-GO state); `gtkb-git-repo-broken-blob-investigation-009` updated to `-012` (latest VERIFIED; the byte-faithfulness + out-of-root scratch-path trap lesson is preserved and the VERIFIED status confirms the pre-filing-check gap is real and consequential).

**Opportunity Radar item captured.** Codex's `Opportunity Radar` finding (add CI/security/release content triggers to `config/governance/spec-applicability.toml` so future proposals don't hit this same omission class) is captured as `WI-3422` under `PROJECT-GTKB-RELIABILITY-FIXES` (covered by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`). Related specs and bridge thread linked. Canonical project membership repaired post-capture per the known doubled-prefix bug (WI-3411).

The remainder of this proposal carries forward the substantive design from -001 with the framing change applied throughout.

## Summary

This is a `bridge_kind: governance_review` proposal. Its scope is the **decision-ready design packet** for PROJECT-GTKB-PUSH-GATE — a comprehensive deterministic CI gate that mechanically blocks pushes to GitHub when any artifact fails any tracked check. The proposal does not create production code; its deliverable is a tracked design document tree under `docs/design/push-gate/<UTC-timestamp>/` that Codex can critique before any binding-final design contract is filed.

The originating signal is owner directive S365: *"Please propose a comprehensive and deterministic testing solution which can be run on the project as a gate when we push to GitHub."* Followed by three locked decisions on design tensions:

1. **No amnesty** — all errors must be found and fixed. No baseline-snapshot. Full forward enforcement. Existing debt is cleaned in a dedicated slice BEFORE the gate becomes a push blocker.
2. **Time-irrelevant execution with caching welcomed** — gate runs as long as needed; nothing pushes uncleaned; a content-addressed result cache skips unchanged-and-previously-passed artifacts to keep normal-development cycles fast without quality compromise.
3. **Mechanical gate + mechanical blocker** — binary PASS/FAIL per check; any failure blocks push at both local pre-push hook and GitHub Actions branch protection.

Followed by: *"Please proceed in order. This is a very important enhancement of GT-KB."* authorizing the slice progression to begin.

This proposal lands the **decision-ready design packet** for Codex review and structures the 5 deferred owner decisions as Slice 0 OUTPUTS that get surfaced for AUQ post-VERIFIED. The binding-final design contract lives in a follow-on bridge thread that files only after the owner-decision packets are answered.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - design evidence is written to in-root `docs/design/push-gate/`; no out-of-root paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to a verification step appropriate for governance-review delivery.
- `GOV-STANDING-BACKLOG-001` - WI-3416 was captured via the gate-clean backlog-add CLI as the master backlog item for PROJECT-GTKB-PUSH-GATE; WI-3422 (opportunity-radar capture) was added under PROJECT-GTKB-RELIABILITY-FIXES this cycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the design packet produced by this review is a durable governed artifact under change control.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3416, this thread, the design packet, and any follow-on implementation proposals.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3416 advances from backlog candidate to lifecycle-tracked governance-review scope; implementation lifecycle remains deferred to Slice 1+ behind the final binding design contract.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the gate is itself a deterministic service per the principle; the cache substrate is the load-bearing technical novelty enabling time-irrelevant execution without per-cycle quality compromise.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - candidate requirements discovered by the review remain candidates until owner-approved spec intake promotes them.
- `SPEC-DSI-CI-GATE-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs CI-time enforcement of spec-derived implementation, the GitHub Actions job on every pull request and push, branch protection requiring the job, and the shared engine path between local hook and CI logic. The push gate's CI integration model directly implements this spec; the design packet's `design-contract-draft.md` includes a section showing the canonical CLI + GitHub Actions workflow shape that satisfies this spec.
- `SPEC-DSI-DOCTOR-CHECK-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs `gt project doctor` invariant coverage of hooks, GitHub Actions workflow, branch protection, bridge gates, and applicability preflight. The design packet's `design-contract-draft.md` includes a section showing how the push gate integrates with this doctor invariant (the gate's PASS state is one of the conditions doctor verifies for release-readiness).
- `SPEC-SEC-HOOK-PORTABILITY-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs tracked `.githooks/pre-commit` and `.githooks/pre-push` plus `core.hooksPath` invariants. The push gate's local pre-push integration uses tracked hooks per this spec; the design packet specifies that the push-gate hook is installed via `core.hooksPath` indirection to the tracked `.githooks/pre-push` and not via untracked `.git/hooks/` writes.
- `SPEC-SEC-SCANNER-CLI-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs `gt secrets scan` CLI surface with staged/range/path/all-ref modes serving hooks, CI, doctor checks, and incident response. The push gate's Layer 5 (security audit) wraps this CLI surface for both pre-push (staged + range mode) and CI (all-ref mode) invocations; the design packet specifies the mode selection per gate phase.
- `SPEC-SEC-GITHUB-POSTURE-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs `gt github security doctor` for repository security posture, branch protection, and workflow coverage checks. The push gate's branch-protection integration model coordinates with this spec; the design packet specifies that the gate's CI job is registered as a required check via this doctor's branch-protection invariants rather than via ad-hoc workflow installation.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - (NEWLY CITED per Codex NO-GO -002 P1-001) governs production-release readiness requiring governed test evidence and passing non-deploying release-candidate gate or owner-approved deferral. The push gate's Layer 7 wraps the existing `release-candidate-gate` skill per this spec; the design packet specifies that Layer 7 runs only on PRs to main + tagged release commits (not on every push) per the existing release-readiness scope, and that Layer 7 PASS contributes evidence toward the governance-required test evidence rather than replacing it.

## Requirement Sufficiency

Existing requirements sufficient for the governance-review deliverable. The proposal will surface candidate requirements for the gate's behavior (cache invariants, layer pass/fail criteria, override governance), but those remain candidates until promoted via the standard chat-derived spec approval workflow per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`. No new formal SPEC is created by this Slice 0. The reframing per P2-002 confirms that the binding design contract lands only after owner-decision packets are resolved; any spec promotion derived from owner decisions happens in the follow-on `gtkb-push-gate-design-contract-final` thread, not in this Slice 0.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to `groundtruth.db`. The governance-review work produces a tracked design packet at `docs/design/push-gate/<timestamp>/` plus supporting analysis files. The PROJECT-GTKB-PUSH-GATE project record and WI-3416 master backlog item were captured in MemBase before this proposal was filed, as separate inventory operations. WI-3422 (this cycle's opportunity-radar capture under PROJECT-GTKB-RELIABILITY-FIXES) is similarly a separate inventory operation, not implementation work scoped by this proposal.

## WI Citation Disclosure

This proposal declares review work for WI-3416 only. References to WI-3411 (backlog-add doubled-prefix CLI bug, repaired during this session's capture sequence including WI-3422's membership row), WI-3410 (impl-auth literal-substring matcher bias-case), WI-3415 (verify-embedded-evidence CLI candidate), WI-3422 (this cycle's opportunity-radar capture), WI-3349 (Gemini substrate held-pending-architectural-decision), and WI-3394 (broken-blob investigation VERIFIED -012) are originating-context citations only — they exemplify the defect classes the push gate will mechanically detect. None of those WIs are implemented or modified by this proposal.

## Prior Deliberations

- Owner directive S365 (2026-05-28, originating session): *"Please propose a comprehensive and deterministic testing solution which can be run on the project as a gate when we push to GitHub."* — the originating request.
- Owner three-tension resolution S365 (2026-05-28): *"First: no amnesty — all errors must be found and fixed. Second: It takes as long as it takes — we will not knowingly push anything that has not been tested and fixed, so it isn't relevant how long it takes to test and fix (although I assume we can avoid re-testing artifacts that have not been changed since they passed the respective test). Third: the term 'gate' refers to a mechanical execution of the tests and a mechanical blocker that prevents pushing any artifacts which are not 100% PASS."* — locks the three primary design tensions.
- Owner authorization S365 (2026-05-28): *"Please proceed in order. This is a very important enhancement of GT-KB."* — authorizes filing Slice 0 + project capture + master WI + Slice 1.5 path forward.
- `DELIB-2499` (S365): owner decision authorizing standing PAUTH covering Slice 0-11 for PROJECT-GTKB-PUSH-GATE; cited by Slice 1.5 NEW-001 and indirectly anchoring this Slice 0 thread's project membership.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the foundational architectural principle the push gate operationalizes: convert repetitive AI quality plumbing into deterministic CLI work.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - the push gate becomes part of the lifecycle-independence boundary for the GT-KB platform (gate must be runnable from any clone, not coupled to a specific developer's workstation).
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - existing release-readiness framework that the push gate's Layer 7 wraps via the `release-candidate-gate` skill.
- Codex NO-GO at `bridge/gtkb-push-gate-design-governance-review-002.md` — surfaces P1-001 (missing CI/security/release spec citations), P2-002 (design-contract framing ambiguity while owner decisions are deferred), and P2-003 (stale citations); all three addressed in this REVISED-3.
- Prior session WI captures that exemplify the gate's value: WI-3410 (impl-auth literal-substring matcher) and WI-3415 (verify-embedded-evidence CLI) are both defect classes the push gate would catch deterministically rather than via post-hoc Codex review.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-008.md` (NO-GO; latest per Codex NO-GO -002 P2-003 stale-citation finding) - WI-3349 substrate verification illustrates a defect class (Windows PATHEXT subprocess resolution) that lint+unit tests would catch but currently rely on Codex review at filing time. Current NO-GO state at -008 reinforces the held-pending-architectural-decision posture (three substrate-resolution paths remain open).
- `bridge/gtkb-git-repo-broken-blob-investigation-012.md` (VERIFIED; latest per Codex NO-GO -002 P2-003 stale-citation finding) - WI-3394 broken-blob investigation closed VERIFIED at -012 after multi-round REVISED chain. The investigation's NO-GO rounds (gitignored evidence; byte-faithfulness + out-of-root scratch-path trap) are exactly the pre-filing-check gap the push gate's Layer 6 (governance integrity) plus Slice 1.5's audit mode would mechanically detect; the VERIFIED close confirms the gap is real and consequential.

## Owner Decisions / Input

This proposal depends on the following durable owner decisions:

- **S365 design tension resolutions** (verbatim above): no amnesty + time-irrelevant + mechanical-blocker locked.
- **S365 proceed authorization**: *"Please proceed in order. This is a very important enhancement of GT-KB."* authorizes Slice 0 filing + project capture + master WI capture.
- **`DELIB-2499` (S365 AUQ)**: selected "Standing Slice 0-11 (Recommended)" PAUTH scope, which covers this Slice 0 governance-review work via `PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11`.

The 5 deferred owner decisions are now framed as Slice 0 OUTPUTS (per Codex NO-GO -002 P2-002 Path 2 reframing) — they are surfaced as structured AUQ-ready packets in `open-decisions-and-aauq-plan.md` for owner answer post-VERIFIED. They do NOT block Slice 0 implementation; they block the follow-on `gtkb-push-gate-design-contract-final` thread that locks the binding contract.

The 5 deferred decisions remain:

1. **Cleanup-sequencing**: Option A (clean-then-enable; recommended) or Option B (enable-then-freeze-until-clean)?
2. **Override path scope**: should a `bridge_kind: gate_bypass_authorization` exist for emergency bypasses, or are bypasses fully forbidden?
3. **Multi-platform CI**: Windows-only (parity with `E:\GT-KB` convention) or Windows + ubuntu-latest (broader coverage)?
4. **PR-vs-push gating scope**: gate on both `push` and `pull_request` events to develop/main, or PR-only?
5. **Test impact analysis dependency**: adopt `pytest-testmon` (coverage-traced test selection) or implement pure-stdlib per-file SHA cache?

These remain Slice 0 surfaces (not Slice 0 prerequisites). The decision-ready packet produces structured trade-off analyses for each so owner can answer the AUQs from evidence rather than from cold context.

## Implementation Plan

The governance-review work produces six tracked evidence artifacts under `docs/design/push-gate/<UTC-timestamp>/`:

1. **`README.md`** — Document tree overview, reading order, provenance trail. Notes the "decision-ready packet" framing and points to `open-decisions-and-aauq-plan.md` as the post-VERIFIED owner-input target.

2. **`design-contract-draft.md`** — The full design contract draft (renamed from `design-contract.md` per P2-002 reframing; "draft" reflects that it becomes binding only after the 5 deferred decisions are resolved in the follow-on `gtkb-push-gate-design-contract-final` thread):
   - Architecture overview (single canonical CLI; local pre-push hook + GitHub Actions workflow share identical invocation per `SPEC-DSI-CI-GATE-001`)
   - Caching substrate (content-addressed PASS/FAIL cache per check-version + file-content; integration with existing tool caches; cache invalidation rules; cache lifecycle)
   - Layer 1 — Pre-commit hygiene (whitespace, ruff format/check, gitignore-bypass, credential pre-scan)
   - Layer 2 — Type + AST (mypy, custom AST: hardcoded-externals, hardcoded SHA, import topology, magic-number)
   - Layer 3 — Test suites (all pytest suites with `pytest-testmon`-style impact analysis OR pure-SHA cache per owner decision Q5)
   - Layer 4 — Architecture + governance assertions (`gt assert`, `gt project doctor` per `SPEC-DSI-DOCTOR-CHECK-001`, applicability/clause preflights, INDEX-vs-files consistency)
   - Layer 5 — Security audit (bandit, pip-audit, gitleaks, `gt secrets scan` via `SPEC-SEC-SCANNER-CLI-001`, scanner-safe-writer batch)
   - Layer 6 — Governance integrity (spec-to-test coverage, DA linkage, doubled-prefix repair detector, standing-backlog freshness)
   - Layer 7 — Release-readiness (wraps existing `release-candidate-gate` skill per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`; runs only on PRs to main + tagged release commits)
   - Hook portability model (tracked `.githooks/pre-push` + `core.hooksPath` indirection per `SPEC-SEC-HOOK-PORTABILITY-001`)
   - CI integration model (per owner decisions Q3 and Q4; baseline draft per `SPEC-DSI-CI-GATE-001` + `SPEC-SEC-GITHUB-POSTURE-001` branch-protection invariants)
   - Owner-override path (per owner decision Q2)
   - Coexistence section (P1-001 traceability): for each of `SPEC-DSI-CI-GATE-001`, `SPEC-DSI-DOCTOR-CHECK-001`, `SPEC-SEC-HOOK-PORTABILITY-001`, `SPEC-SEC-SCANNER-CLI-001`, `SPEC-SEC-GITHUB-POSTURE-001`, and `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, explicitly state whether the push gate WRAPS the spec's surface (Layer 5/7), EXTENDS the spec's invariants (Layer 4 doctor integration), or COEXISTS independently (governance integrity Layer 6).

3. **`cleanup-sequencing-analysis.md`** — Detailed comparison of Option A (clean-then-enable, recommended; Codex agreed at NO-GO -002 final note) vs Option B (enable-then-freeze-until-clean) with risk/blast-radius for each. Recommendation rationale. Becomes input to deferred decision Q1.

4. **`debt-inventory-method.md`** — Specification for the Slice 1.5 audit-only mode that produces the initial debt inventory: how each layer reports findings, JSON schema, expected output shape, integration with existing GT-KB CLI conventions. Slice 1.5's NEW-001 already implements a minimum-viable version of this; the design-packet document harmonizes the schema for the canonical Slice 1 CLI.

5. **`open-decisions-and-aauq-plan.md`** — Central Slice 0 deliverable per the P2-002 reframing. Structured AUQ-ready packets for the 5 deferred owner decisions, each with:
   - Decision statement
   - 2-4 option labels suitable for AskUserQuestion
   - Trade-off analysis per option (cost/correctness/parity-with-existing-surfaces)
   - Spec-coherence check (does the option preserve `SPEC-DSI-CI-GATE-001`, `SPEC-SEC-HOOK-PORTABILITY-001`, etc. or require revision?)
   - Recommendation + rationale

6. **`slice-progression-and-followon.md`** — Slice 0-11 detailed plan with proposed bridge thread slugs, target_paths, sequencing dependencies, and owner-decision checkpoints. Explicitly notes that Slices 1+ implementation cannot file until `gtkb-push-gate-design-contract-final` lands VERIFIED.

The review uses only read-only inspection of existing GT-KB code, rules, hooks, and documentation. No code creation, no MemBase mutation, no `.groundtruth-chroma/` mutation.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal filed at `bridge/gtkb-push-gate-design-governance-review-003.md`; `bridge/INDEX.md` updated. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Design evidence directory is `docs/design/push-gate/` under `E:\GT-KB`. | PASS - all in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-push-gate-design-governance-review`. | PASS expected - preflight re-run after Write. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table records the spec-to-test mapping; post-implementation report will record observed results. | PASS - mapping present. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-GTKB-PUSH-GATE` shows WI-3416 as an active member; `gt projects show PROJECT-GTKB-RELIABILITY-FIXES` shows WI-3422 as active member (post doubled-prefix repair); backlog capture used `python -m groundtruth_kb backlog add` gate-clean CLI. | PASS - both memberships recorded. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tracked design-packet artifacts plus bridge audit trail preserve durable traceability between WI-3416, this thread, and the design outputs. | PASS - design packet is tracked under `docs/design/push-gate/`. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | `design-contract-draft.md` explicitly maps the push gate's cache substrate + canonical-CLI shape to the deterministic-services principle. | PASS at post-implementation review (when the design packet lands). |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | `open-decisions-and-aauq-plan.md` explicitly marks all candidate requirements as pending owner-approved spec intake. | PASS at post-implementation review. |
| `SPEC-DSI-CI-GATE-001` | `design-contract-draft.md` § Architecture overview specifies single canonical CLI + GitHub Actions workflow sharing identical invocation; § Coexistence section confirms the push gate IMPLEMENTS this spec's CI-time enforcement invariant. | PASS at post-implementation review. |
| `SPEC-DSI-DOCTOR-CHECK-001` | `design-contract-draft.md` § Layer 4 + § Coexistence section confirm push gate EXTENDS this doctor invariant by adding push-gate-PASS as one of the conditions doctor verifies for release-readiness. | PASS at post-implementation review. |
| `SPEC-SEC-HOOK-PORTABILITY-001` | `design-contract-draft.md` § Hook portability model + § Coexistence section confirm push gate WRAPS this spec via tracked `.githooks/pre-push` + `core.hooksPath` indirection; no untracked `.git/hooks/` writes. | PASS at post-implementation review. |
| `SPEC-SEC-SCANNER-CLI-001` | `design-contract-draft.md` § Layer 5 + § Coexistence section confirm push gate WRAPS `gt secrets scan` for both pre-push (staged + range mode) and CI (all-ref mode). | PASS at post-implementation review. |
| `SPEC-SEC-GITHUB-POSTURE-001` | `design-contract-draft.md` § CI integration model + § Coexistence section confirm push gate's CI job is registered as required check via this doctor's branch-protection invariants. | PASS at post-implementation review. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `design-contract-draft.md` § Layer 7 + § Coexistence section confirm Layer 7 WRAPS `release-candidate-gate` skill, runs only on PRs to main + tagged release commits, and contributes evidence toward governance-required test evidence rather than replacing it. | PASS at post-implementation review. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED-3 governance-review proposal.
- [ ] `docs/design/push-gate/<UTC-timestamp>/` exists and contains the six Markdown evidence files (note: `design-contract.md` renamed to `design-contract-draft.md` per P2-002 reframing).
- [ ] `design-contract-draft.md` specifies the 7-layer architecture, cache substrate, CI integration model, owner-override path, hook portability model, and dedicated § Coexistence section per P1-001.
- [ ] `cleanup-sequencing-analysis.md` provides risk/blast-radius for Option A vs Option B.
- [ ] `debt-inventory-method.md` specifies the Slice 1.5 audit-only mode JSON schema.
- [ ] `open-decisions-and-aauq-plan.md` enumerates the 5 deferred owner decisions with structured AUQ-ready packets (option labels, trade-off analyses, spec-coherence checks, recommendations).
- [ ] `slice-progression-and-followon.md` provides Slice 0-11 detailed plan and explicitly notes the `gtkb-push-gate-design-contract-final` follow-on thread gates Slices 1+ implementation.
- [ ] No production code is created, modified, or deleted during the review.
- [ ] `.groundtruth-chroma/` is not mutated.
- [ ] `groundtruth.db` is not mutated by this proposal (project + WI captures are separate inventory operations completed before filing).
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before any follow-on implementation bridge (`gtkb-push-gate-design-contract-final` or Slice 1.5+) is filed.

## Risk and Rollback

Risk is very low. The review is read-only against production substrates; design output lives entirely in `docs/design/push-gate/` which is a tracked design-documentation tree.

Risks identified:

- The 5 deferred decisions may surface conflicts during Codex review (e.g., Codex may push back on the no-amnesty interpretation, or recommend a different cleanup sequence). Mitigation: this proposal's role IS to surface them for governed review; Codex critique is the expected feedback channel; the decision-ready packet framing means Slice 0 VERIFIED does not commit to specific answers.
- The slice progression is large (Slice 0-11) and the debt-cleanup phase (Slice 3) may be substantial. The Slice 1.5 audit will produce the concrete inventory; until that lands, the cleanup volume is unknowable. Mitigation: Slice 1.5 is intentionally a parallel sub-slice that produces inventory data independent of the design contract.
- The cache substrate is the load-bearing technical novelty. If the cache invariants are subtly broken, the gate could produce false-PASS results. Mitigation: Slice 1's cache implementation (post final-contract VERIFIED) will include unit tests that verify invariants (content-addressed; checker-version-aware; cross-file-dependency-aware for tests); the no-amnesty contract means a missed defect is catastrophic, so cache correctness becomes a P0 quality bar in Slice 1.
- Coexistence drift relative to the newly-cited specs (P1-001 risk): if the push gate's CI integration drifts from `SPEC-DSI-CI-GATE-001`, or its hook portability drifts from `SPEC-SEC-HOOK-PORTABILITY-001`, the gate would silently re-introduce the governance drift it's supposed to reduce. Mitigation: the design packet's § Coexistence section in `design-contract-draft.md` explicitly maps the push gate to each spec's invariants; Codex verifies the mapping at post-implementation review.

Rollback: delete the design-packet tree. No production or KB substrate state requires rollback.

## Verification Limitations Anticipated

- The design packet does not validate against a working prototype. Prototype validation is reserved for Slice 1 (CLI scaffolding + cache substrate, post final-contract VERIFIED).
- The design enumerates 7 layers but does not pre-specify every check within each layer. Per-check specifications land in the corresponding slice's implementation proposal.
- The 5 deferred owner decisions remain open at the end of this Slice 0; Codex GO on this REVISED-3 does not constitute resolution of those decisions, only acceptance of the decision-ready-packet framework that surfaces them.

## Files Touched (target_paths recap)

- `docs/design/push-gate/` (new design-packet evidence tree)

Plus bridge filing artifacts (workflow infrastructure, not implementation scope):
- `bridge/gtkb-push-gate-design-governance-review-003.md` (this file)
- `bridge/INDEX.md` (entry update)
- `bridge/gtkb-push-gate-design-governance-review-NNN.md` (post-impl report after design packet lands)

## Loyal Opposition Asks

1. Verify the response to NO-GO -002 P1-001 (six newly-cited specs in `## Specification Links` and `## Spec-to-Test Mapping`, with each new spec mapped to a Coexistence section in `design-contract-draft.md`) closes the missing-spec finding, or NO-GO with specific gaps.
2. Verify the response to NO-GO -002 P2-002 (reframing from "design contract" to "decision-ready design packet"; renaming `design-contract.md` to `design-contract-draft.md`; elevating `open-decisions-and-aauq-plan.md` as Slice 0's central output; deferring binding contract to follow-on `gtkb-push-gate-design-contract-final` thread) is consistent with Codex's recommended Path 2, or recommend an alternative.
3. Verify the response to NO-GO -002 P2-003 (citations updated to `-008` for `gtkb-headless-gemini-lo-dispatch-verification` and `-012` for `gtkb-git-repo-broken-blob-investigation`) is correct, or surface remaining stale citations.
4. Verify the Coexistence section requirement for `design-contract-draft.md` correctly captures the relationship between the push gate and each newly-cited spec (WRAPS vs EXTENDS vs COEXISTS-INDEPENDENTLY), or recommend a clearer taxonomy.
5. Confirm that filing this REVISED-3 with the decision-ready-packet framing is the right structural answer to P2-002, or recommend collapsing back to Path 1 (resolve owner decisions before Slice 0 implementation).
6. Note any cross-cutting governance specs (beyond the 6 newly cited + 10 original) that should still be added to Specification Links.

## Mechanical Preflight Evidence (post-Write re-run intended)

The mandatory preflights will be re-run after this file lands and the INDEX REVISED entry is added. Expected outcomes:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-push-gate-design-governance-review`: PASS (`preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`).
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-push-gate-design-governance-review`: PASS (no blocking gaps; `must_apply` clauses each carry evidence).
- `python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-push-gate-design-governance-review`: 0 findings expected.
- `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-push-gate-design-governance-review`: 0 stale citations expected (both prior stale citations refreshed in this REVISED-3).
- `python scripts/bridge_proposal_wi_id_collision_check.py --content-file bridge/gtkb-push-gate-design-governance-review-003.md --declared-wi WI-3416`: advisory collisions for cited context WIs expected (`WI-3411`, `WI-3410`, `WI-3415`, `WI-3422`, `WI-3349`, `WI-3394`); non-blocking because the `## WI Citation Disclosure` section above explicitly enumerates these as context-only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
