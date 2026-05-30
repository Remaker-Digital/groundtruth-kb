NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-push-gate-design-governance-review
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# PROJECT-GTKB-PUSH-GATE Slice 0: comprehensive deterministic CI gate design contract

bridge_kind: governance_review
Document: gtkb-push-gate-design-governance-review
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3416 (PROJECT-GTKB-PUSH-GATE master)
Work Item: WI-3416
target_paths: ["docs/design/push-gate/"]
Recommended commit type: docs:

## Summary

This is a `bridge_kind: governance_review` proposal. Its scope is the design contract for PROJECT-GTKB-PUSH-GATE — a comprehensive deterministic CI gate that mechanically blocks pushes to GitHub when any artifact fails any tracked check. The proposal does not create production code; its deliverable is a tracked design document tree under `docs/design/push-gate/<UTC-timestamp>/` that Codex can critique before any implementation begins.

The originating signal is owner directive S365: *"Please propose a comprehensive and deterministic testing solution which can be run on the project as a gate when we push to GitHub."* Followed by three locked decisions on design tensions:

1. **No amnesty** — all errors must be found and fixed. No baseline-snapshot. Full forward enforcement. Existing debt is cleaned in a dedicated slice BEFORE the gate becomes a push blocker.
2. **Time-irrelevant execution with caching welcomed** — gate runs as long as needed; nothing pushes uncleaned; a content-addressed result cache skips unchanged-and-previously-passed artifacts to keep normal-development cycles fast without quality compromise.
3. **Mechanical gate + mechanical blocker** — binary PASS/FAIL per check; any failure blocks push at both local pre-push hook and GitHub Actions branch protection.

Followed by: *"Please proceed in order. This is a very important enhancement of GT-KB."* authorizing the slice progression to begin.

This proposal lands the design contract for Codex review and surfaces 5 remaining decisions that need owner direction before Slice 1.5 (debt-discovery audit implementation) can be filed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - design evidence is written to in-root `docs/design/push-gate/`; no out-of-root paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to a verification step appropriate for governance-review delivery.
- `GOV-STANDING-BACKLOG-001` - WI-3416 was captured via the gate-clean backlog-add CLI as the master backlog item for PROJECT-GTKB-PUSH-GATE.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the design document produced by this review is a durable governed artifact under change control.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3416, this thread, the design document, and any follow-on implementation proposals.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3416 advances from backlog candidate to lifecycle-tracked governance-review scope; implementation lifecycle remains deferred to Slice 1+.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the gate is itself a deterministic service per the principle; the cache substrate is the load-bearing technical novelty enabling time-irrelevant execution without per-cycle quality compromise.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - candidate requirements discovered by the review remain candidates until owner-approved spec intake promotes them.

## Requirement Sufficiency

Existing requirements sufficient for the governance-review deliverable. The proposal will surface candidate requirements for the gate's behavior (cache invariants, layer pass/fail criteria, override governance), but those remain candidates until promoted via the standard chat-derived spec approval workflow per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`. No new formal SPEC is created by this Slice 0.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to `groundtruth.db`. The governance-review work produces a tracked design document tree at `docs/design/push-gate/<timestamp>/` plus supporting analysis files. The PROJECT-GTKB-PUSH-GATE project record and WI-3416 master backlog item were captured in MemBase before this proposal was filed, as separate inventory operations (not implementation work scoped by this proposal).

## WI Citation Disclosure

This proposal declares review work for WI-3416 only. References to WI-3411 (backlog-add doubled-prefix CLI bug, repaired during this session's capture sequence), WI-3410 (impl-auth literal-substring matcher bias-case), and WI-3415 (verify-embedded-evidence CLI candidate) are originating-context citations only — they exemplify the defect classes the push gate will mechanically detect. None of those WIs are implemented or modified by this proposal.

## Prior Deliberations

- Owner directive S365 (2026-05-28, this session): *"Please propose a comprehensive and deterministic testing solution which can be run on the project as a gate when we push to GitHub."* — the originating request.
- Owner three-tension resolution S365 (2026-05-28): *"First: no amnesty — all errors must be found and fixed. Second: It takes as long as it takes — we will not knowingly push anything that has not been tested and fixed, so it isn't relevant how long it takes to test and fix (although I assume we can avoid re-testing artifacts that have not been changed since they passed the respective test). Third: the term 'gate' refers to a mechanical execution of the tests and a mechanical blocker that prevents pushing any artifacts which are not 100% PASS."* — locks the three primary design tensions.
- Owner authorization S365 (2026-05-28): *"Please proceed in order. This is a very important enhancement of GT-KB."* — authorizes filing Slice 0 + project capture + master WI + Slice 1.5 path forward.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the foundational architectural principle the push gate operationalizes: convert repetitive AI quality plumbing into deterministic CLI work.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - the push gate becomes part of the lifecycle-independence boundary for the GT-KB platform (gate must be runnable from any clone, not coupled to a specific developer's workstation).
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - existing release-readiness framework that the push gate's Layer 7 wraps via the `release-candidate-gate` skill.
- Prior session WI captures that exemplify the gate's value: WI-3410 (impl-auth literal-substring matcher) and WI-3415 (verify-embedded-evidence CLI) are both defect classes the push gate would catch deterministically rather than via post-hoc Codex review.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-005.md` and prior chain - WI-3349 substrate verification illustrates a defect class (Windows PATHEXT subprocess resolution) that lint+unit tests would catch but currently rely on Codex review at filing time.
- `bridge/gtkb-git-repo-broken-blob-investigation-009.md`, `-011.md` and the NO-GO chain - WI-3394 broken-blob investigation produced two REVISED rounds (NO-GO -008 gitignored evidence; NO-GO -010 byte-faithfulness + out-of-root scratch-path trap) that pre-filing checks would have caught. The push gate's Layer 6 (governance integrity) plus Slice 1.5's audit mode would mechanically detect both.

## Owner Decisions / Input

This proposal depends on the following owner decisions:

- **S365 design tension resolutions** (verbatim above): no amnesty + time-irrelevant + mechanical-blocker locked.
- **S365 proceed authorization**: *"Please proceed in order. This is a very important enhancement of GT-KB."* authorizes Slice 0 filing + project capture + master WI capture.

This proposal explicitly defers the following owner decisions to follow-on AUQ + bridge proposals:

1. **Cleanup-sequencing**: Option A (clean-then-enable; recommended) or Option B (enable-then-freeze-until-clean)? See §"Cleanup Sequencing" below.
2. **Override path scope**: should a `bridge_kind: gate_bypass_authorization` exist for emergency bypasses, or are bypasses fully forbidden?
3. **Multi-platform CI**: Windows-only (parity with `E:\GT-KB` convention) or Windows + ubuntu-latest (broader coverage)?
4. **PR-vs-push gating scope**: gate on both `push` and `pull_request` events to develop/main, or PR-only?
5. **Test impact analysis dependency**: adopt `pytest-testmon` (coverage-traced test selection) or implement pure-stdlib per-file SHA cache?

These 5 decisions surface naturally during Slice 0 review and are appropriate for AUQ once Codex has critiqued the design.

Additionally, Slice 1.5 (debt-discovery audit) will require a project-scoped implementation authorization (PAUTH) to be created. The PAUTH scope question is the next AUQ after this Slice 0 receives Codex GO.

## Implementation Plan

The governance-review work produces six tracked evidence artifacts under `docs/design/push-gate/<UTC-timestamp>/`:

1. **`README.md`** — Document tree overview, reading order, provenance trail.

2. **`design-contract.md`** — The full design contract:
   - Architecture overview (single canonical CLI; local pre-push hook + GitHub Actions workflow share identical invocation)
   - Caching substrate (content-addressed PASS/FAIL cache per check-version + file-content; integration with existing tool caches; cache invalidation rules; cache lifecycle)
   - Layer 1 — Pre-commit hygiene (whitespace, ruff format/check, gitignore-bypass, credential pre-scan)
   - Layer 2 — Type + AST (mypy, custom AST: hardcoded-externals, hardcoded SHA, import topology, magic-number)
   - Layer 3 — Test suites (all pytest suites with `pytest-testmon`-style impact analysis OR pure-SHA cache per owner decision Q5)
   - Layer 4 — Architecture + governance assertions (`gt assert`, `gt project doctor`, applicability/clause preflights, INDEX-vs-files consistency)
   - Layer 5 — Security audit (bandit, pip-audit, gitleaks, scanner-safe-writer batch)
   - Layer 6 — Governance integrity (spec-to-test coverage, DA linkage, doubled-prefix repair detector, standing-backlog freshness)
   - Layer 7 — Release-readiness (wraps existing `release-candidate-gate` skill; runs only on PRs to main + tagged release commits)
   - CI integration model (local pre-push + GitHub Actions workflow per owner decision Q3 and Q4)
   - Owner-override path (per owner decision Q2)

3. **`cleanup-sequencing-analysis.md`** — Detailed comparison of Option A (clean-then-enable, recommended) vs Option B (enable-then-freeze-until-clean) with risk/blast-radius for each. Recommendation rationale.

4. **`debt-inventory-method.md`** — Specification for the Slice 1.5 audit-only mode that produces the initial debt inventory: how each layer reports findings, JSON schema, expected output shape, integration with existing GT-KB CLI conventions.

5. **`open-decisions-and-aauq-plan.md`** — Structured analysis of the 5 deferred owner decisions, with recommendations and trade-off analysis for each. Pre-AUQ thinking.

6. **`slice-progression-and-followon.md`** — Slice 0-11 detailed plan with proposed bridge thread slugs, target_paths, sequencing dependencies, and owner-decision checkpoints.

The review uses only read-only inspection of existing GT-KB code, rules, hooks, and documentation. No code creation, no MemBase mutation, no `.groundtruth-chroma/` mutation.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal filed at `bridge/gtkb-push-gate-design-governance-review-001.md`; `bridge/INDEX.md` updated. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Design evidence directory is `docs/design/push-gate/` under `E:\GT-KB`. | PASS - all in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-push-gate-design-governance-review`. | PASS expected — preflight will run after this file lands. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table records the spec-to-test mapping; post-implementation report will record observed results. | PASS - mapping present. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-GTKB-PUSH-GATE` shows WI-3416 as an active member; backlog capture used `python -m groundtruth_kb backlog add` gate-clean CLI. | PASS - membership recorded; canonical project membership confirmed after WI-3411 doubled-prefix repair. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tracked design-document artifacts plus bridge audit trail preserve durable traceability between WI-3416, this thread, and the design outputs. | PASS - design contract is tracked under `docs/design/push-gate/`. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | `design-contract.md` explicitly maps the push gate's cache substrate + canonical-CLI shape to the deterministic-services principle. | PASS at post-implementation review (when the design document lands). |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | `open-decisions-and-aauq-plan.md` explicitly marks all candidate requirements as pending owner-approved spec intake. | PASS at post-implementation review. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this governance-review proposal.
- [ ] `docs/design/push-gate/<UTC-timestamp>/` exists and contains the six Markdown evidence files.
- [ ] `design-contract.md` specifies the 7-layer architecture, cache substrate, CI integration model, and owner-override path.
- [ ] `cleanup-sequencing-analysis.md` provides risk/blast-radius for Option A vs Option B.
- [ ] `debt-inventory-method.md` specifies the Slice 1.5 audit-only mode JSON schema.
- [ ] `open-decisions-and-aauq-plan.md` enumerates the 5 deferred owner decisions with recommendations.
- [ ] `slice-progression-and-followon.md` provides Slice 0-11 detailed plan.
- [ ] No production code is created, modified, or deleted during the review.
- [ ] `.groundtruth-chroma/` is not mutated.
- [ ] `groundtruth.db` is not mutated by this proposal (project + WI captures are separate inventory operations completed before filing).
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before any follow-on implementation bridge (Slice 1.5+) is filed.

## Risk and Rollback

Risk is very low. The review is read-only against production substrates; design output lives entirely in `docs/design/push-gate/` which is a tracked design-documentation tree.

Risks identified:

- The 5 deferred decisions may surface conflicts during Codex review (e.g., Codex may push back on the no-amnesty interpretation, or recommend a different cleanup sequence). Mitigation: this proposal's role IS to surface them for governed review; Codex critique is the expected feedback channel.
- The slice progression is large (Slice 0-11) and the debt-cleanup phase (Slice 3) may be substantial. The Slice 1.5 audit will produce the concrete inventory; until that lands, the cleanup volume is unknowable. Mitigation: Slice 1.5 is intentionally the next step after this Slice 0 receives GO; debt inventory data informs subsequent slice timing.
- The cache substrate is the load-bearing technical novelty. If the cache invariants are subtly broken, the gate could produce false-PASS results. Mitigation: Slice 1's cache implementation will include unit tests that verify invariants (content-addressed; checker-version-aware; cross-file-dependency-aware for tests); the no-amnesty contract means a missed defect is catastrophic, so cache correctness becomes a P0 quality bar in Slice 1.

Rollback: delete the design-document tree. No production or KB substrate state requires rollback.

## Verification Limitations Anticipated

- The design contract does not validate against a working prototype. Prototype validation is reserved for Slice 1 (CLI scaffolding + cache substrate).
- The design enumerates 7 layers but does not pre-specify every check within each layer. Per-check specifications land in the corresponding slice's implementation proposal.
- The 5 deferred owner decisions remain open at the end of this Slice 0; Codex GO on this proposal does not constitute resolution of those decisions, only acceptance of the design framework that surfaces them.

## Files Touched (target_paths recap)

- `docs/design/push-gate/` (new design-document evidence tree)

Plus bridge filing artifacts (workflow infrastructure, not implementation scope):
- `bridge/gtkb-push-gate-design-governance-review-001.md` (this file)
- `bridge/INDEX.md` (entry update)
- `bridge/gtkb-push-gate-design-governance-review-NNN.md` (post-impl report)

## Loyal Opposition Asks

1. Verify the design-contract scope (7 layers + cache substrate + CI integration + owner-override path) is appropriate for a comprehensive push gate, or NO-GO with specific design concerns.
2. Verify the no-amnesty interpretation (Option A clean-then-enable recommended) is consistent with the owner's S365 directive, or surface alternative interpretations.
3. Verify the cache substrate design (content-addressed; checker-version-aware; per-tool cache integration; explicit cross-file-dependency tracking for tests) is technically sound, or recommend a different cache architecture.
4. Verify the 5 deferred owner decisions in §"Owner Decisions / Input" are the right set to defer (not too many, not too few), or recommend adjustments.
5. Verify the slice progression Slice 0-11 is correctly sequenced for the dependency chain (cache substrate → audit mode → cleanup → enablement → CI integration → branch protection), or recommend a different sequence.
6. Confirm that filing this Slice 0 as `bridge_kind: governance_review` (metadata-exempt) is the correct bridge_kind, or recommend an alternative.
7. Note any cross-cutting governance specs (beyond the cited set) that should be added to Specification Links — especially any release-readiness or CI-integration specs that govern the push-gate's interaction with existing infrastructure.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
