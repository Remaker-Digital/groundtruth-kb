NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 8

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Subject: Release operations + program closeout for GTKB-ISOLATION-017. Authors v0.7.0-rc1 release notes (CHANGELOG entry + standalone announcement), updates `memory/release-readiness.md` with the composite acceptance gate, ships a verification script, files an umbrella post-impl report citing Slices 1-7's IPRs/CVRs, and tags the v0.7.0-rc1 release.

**All 3 Slice 8 owner decisions resolved at S329 proposal-draft time** via AskUserQuestion:

- **Decision 2 (release version):** `v0.7.0-rc1` — release candidate, not GA. Per work_list TOP "Clean-adopter productization → v0.7.0-rc1" wording.
- **Decision 4 (publicity surfaces + scheduling):** all 4 — release notes + docs chapter cite + example repos cite + standalone announcement, all released together at the v0.7.0-rc1 tag moment.
- **Decision 5 (post-Phase-9 acceptance gate):** composite — (a) `memory/release-readiness.md` contains an `ISOLATION-017-CLOSEOUT` field naming all 7 VERIFIED bridge IDs; (b) `tests/test_examples_pass_doctor.py` 5/5 PASS in CI on the v0.7.0-rc1 tag; (c) `gt project doctor` passes on all 4 examples + the migration example reaches clean post-state.

## Context

GTKB-ISOLATION-017 Slices 1-7 are VERIFIED. Per the scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` lines 186-202 + GO at `-004`, Slice 8 is the release-ops + closeout slice. Per sequencing constraint at scoping `-003.md` line 209, Slice 8 unblocks after Slices 1-7 VERIFIED — all complete (commits `dc8e58f8` Slice 5, `9efd29bf` Slice 6, `05774d6a` Slice 7 on develop).

This is the **final slice on the v0.7.0-rc1 critical path**. Closing this slice closes the ISOLATION-017 program.

## Specification Links

1. **Phase 9 plan §"Deliverables From The Implementation Bridge"** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 415-430. Names release notes, version gating, and program closure as Slice 8 deliverables.
2. **Phase 9 plan §"Open Decisions"** at the same plan lines 369-396, specifically Decision 2 (release version), Decision 4 (publicity), Decision 5 (acceptance gate) — all resolved per S329 owner directives.
3. **Phase 9 plan §"Required Coverage"** at the same plan lines 89-303 — closeout summarizes which areas reached production state.
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — the binding ADR; Slice 8 documents that it is now fully implemented across Slices 1-7.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 186-202 + `-004` GO.
7. **GOV-09**, **GOV-19**, **GOV-20** (umbrella IPR + CVR drafts in post-impl REPORT).
8. **Prior Slice GOs (the closeout cites all 7):**
    - Slice 1 `-012` VERIFIED — 9 isolation doctor checks
    - Slice 2 `-008` VERIFIED — managed-artifact registry
    - Slice 2.5 `-008` VERIFIED — `OwnershipMeta.notes`
    - Slice 3 `-014` VERIFIED — `gt project init` defaults
    - Slice 4 `-012` VERIFIED — `gt project upgrade --accept-migration`
    - Slice 5 `-006` VERIFIED — clean-adopter test suite
    - Slice 6 `-004` VERIFIED — docs/architecture/isolation.md
    - Slice 7 `-004` VERIFIED — 4 example trees + migration walkthrough
9. **Existing surfaces modified or read-only-cited:**
    - `groundtruth-kb/CHANGELOG.md` — add v0.7.0-rc1 entry under `[Unreleased]`
    - `memory/release-readiness.md` — current state at S327 wrap; updated by Slice 8 with composite gate evidence
    - `groundtruth-kb/docs/architecture/isolation.md` — Slice 6's chapter (cited)
    - `groundtruth-kb/examples/*` — Slice 7's 4 examples (cited)
    - `groundtruth-kb/tests/test_examples_pass_doctor.py` — Slice 7's verification (cited as gate input)
10. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as the release target.
    - S329 owner directives resolving Decisions 2/4/5 (cited inline; to be archived at session-wrap).
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — Slice 5.5 deferred behind v0.7.0-rc1; the closeout notes the deferred scope.
    - `python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 release closeout"` — to be re-run by Codex review.

## Scope

### In-scope

Files created (new):

- **`groundtruth-kb/docs/announcements/v0.7.0-rc1.md`** — standalone release announcement (~150 LOC). Narrative covering: what changed (the isolation contract end-to-end), why (ADR-ISOLATION-APPLICATION-PLACEMENT-001), how to migrate (cite WALKTHROUGH.md from Slice 7), what's deferred (Slice 5.5 overlay refresh + disposability).
- **`scripts/_verify_slice8_closeout.py`** — composite acceptance-gate verification (~80 LOC). Three checks:
  1. `memory/release-readiness.md` contains an `ISOLATION-017-CLOSEOUT` block naming all 7 VERIFIED bridge IDs.
  2. `python -m pytest groundtruth-kb/tests/test_examples_pass_doctor.py -q` exits 0 (5/5 PASS).
  3. `python -m pytest groundtruth-kb/tests/adopter/ -q` exits 0 (45/45 PASS — Slice 5's clean-adopter contract still holds).

Files modified:

- **`groundtruth-kb/CHANGELOG.md`** — `[Unreleased]` section retitled to `[0.7.0-rc1] - 2026-05-03` with the full release-notes entry (~80 LOC). Cites Slice 6's docs chapter + Slice 7's examples + the migration walkthrough.
- **`memory/release-readiness.md`** — append an `ISOLATION-017-CLOSEOUT` block listing all 7 VERIFIED bridge IDs + the 3 gate-verification commands + the 5/5 + 45/45 + 4/4 expected pass counts (~30 LOC change).

Documents (per GOV-20 advisory pilot):

- **`IPR-SLICE8-RELEASE-OPS-001`** — pre-implementation review citing this proposal, the 3 resolved decisions, and the composite gate. Embedded in post-impl REPORT.
- **`CVR-SLICE8-RELEASE-OPS-001`** — post-implementation proof; embedded in post-impl REPORT.
- **`UMBRELLA-IPR-ISOLATION-017-PROGRAM`** — program-level umbrella citing all 7 prior IPRs + this slice's IPR. Embedded in post-impl REPORT per scoping line 199.
- **`UMBRELLA-CVR-ISOLATION-017-PROGRAM`** — program-level umbrella citing all 7 prior CVRs + this slice's CVR. Embedded in post-impl REPORT.

**Total estimated:** 2 new files + 2 modified files + 4 GOV-20 document drafts inline.

### Version tag (separate operator step, NOT in this commit)

Tagging the v0.7.0-rc1 release via `git tag -a v0.7.0-rc1 -m "..."` is a separate operator step **after** Codex VERIFIED on this slice. Per CLAUDE.md, the tag is a release-deploy moment requiring explicit owner authorization beyond a normal commit. Slice 8 prepares everything for the tag; the tag itself is owner-driven.

### Out-of-scope (explicitly deferred)

- **GA tagging (v0.7.0).** This slice ships the rc only. GA follows after rehearsal evidence on at least one real adopter.
- **Slice 5.5 (overlay refresh + disposability).** Deferred per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE`. The closeout notes the deferral.
- **PyPI publication.** A release tag enables, but does not perform, package publication. Publication is operator-driven.
- **Modifying Slices 1-7 surfaces.** This slice cites them; it does not modify them. Future doc/test fixes file as separate work items.
- **Customer email / blog post.** Decision 4 selected only release notes + docs cite + examples cite + standalone announcement (not customer email or blog post).

## Implementation Plan

1. **Author the standalone announcement** at `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (~150 LOC). Sections: Overview / What changed / Why / How to migrate (link to WALKTHROUGH.md) / What's deferred (Slice 5.5) / See also.

2. **Author the CHANGELOG entry** in `groundtruth-kb/CHANGELOG.md` under a new `## [0.7.0-rc1] - 2026-05-03` heading, before the `[Unreleased]` line. Sections: Added (isolation contract artifacts) / Changed (upgrade flow with `--accept-migration`) / Deprecated (workstream-focus.py legacy hook) / Cross-references (docs chapter, examples, announcement).

3. **Append `ISOLATION-017-CLOSEOUT` block to `memory/release-readiness.md`** — the composite gate evidence. Lists all 7 VERIFIED bridge IDs, the 3 gate-verification commands, and the expected outcomes (5/5 + 45/45 + 4/4).

4. **Author `scripts/_verify_slice8_closeout.py`** — composite gate verifier (~80 LOC). Reads release-readiness.md, runs the 2 pytest commands, reports composite PASS/FAIL.

5. **Author umbrella IPR + CVR documents** per GOV-20. Embedded in the post-impl REPORT.

## Test Plan (spec-to-content mapping)

| Specification clause | Verification |
|---|---|
| Phase 9 plan §"Deliverables" line 425-426 (release notes) | `groundtruth-kb/CHANGELOG.md` contains `## [0.7.0-rc1] - 2026-05-03` heading; entry covers Added/Changed/Deprecated sections |
| Phase 9 plan §"Deliverables" line 427-428 (release version gating) | release-readiness.md `ISOLATION-017-CLOSEOUT` block names v0.7.0-rc1 + `scaffold_version` updates flow through to scaffold output |
| Phase 9 plan §"Deliverables" line 429-430 (program closure summary) | post-impl REPORT umbrella IPR + CVR cite all 7 prior IPRs/CVRs |
| Decision 2 (v0.7.0-rc1 tag) | CHANGELOG header + announcement + release-readiness all cite v0.7.0-rc1 |
| Decision 4 (4 publicity surfaces, together) | Slice 8 produces all 4: CHANGELOG entry + announcement doc + cross-references to docs chapter + cross-references to examples |
| Decision 5 (composite acceptance gate) | `scripts/_verify_slice8_closeout.py` runs 3 checks; all PASS for v0.7.0-rc1 |

Verification commands:

```bash
# From E:\GT-KB
python scripts/_verify_slice8_closeout.py
```

Expected output: 3 PASS lines (release-readiness field present + clean-adopter 45/45 + examples 5/5).

Plus a content-presence check on CHANGELOG + announcement (header anchors, cross-link integrity).

## Acceptance Criteria

This NEW is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the resolved Decisions 2/4/5.
2. The 4 Slice 8 deliverables (CHANGELOG entry, announcement doc, release-readiness field, verification script) match the §"In-scope" file list.
3. The CHANGELOG entry cites Slice 6's docs chapter + Slice 7's examples + the migration walkthrough.
4. The standalone announcement narrates the v0.7.0-rc1 release without claiming GA semantics or publishing-channel commitments not in Decision 4.
5. The release-readiness `ISOLATION-017-CLOSEOUT` block names all 7 VERIFIED bridge IDs.
6. `scripts/_verify_slice8_closeout.py` runs the 3 composite-gate checks.
7. The version tag is documented as a separate operator step, NOT performed in the implementation commit.
8. Estimated envelope: 2 new files + 2 modified files + ~340 LOC across all artifacts.

## Risk / Rollback

**Risk 1 — Closeout claim drift (medium).** The umbrella IPR/CVR cite all 7 prior IPRs/CVRs as "complete". If any prior IPR/CVR was actually incomplete, the umbrella overclaims. Mitigation: each prior IPR/CVR is embedded in its slice's VERIFIED post-impl REPORT (Slice 5: -005, Slice 6: -003, Slice 7: -003); the umbrella cites the bridge IDs not the claim text, so each cite is mechanically verifiable.

**Risk 2 — Slice 5.5 deferral leak in announcement (low).** The standalone announcement must accurately describe the scope shipped in v0.7.0-rc1 — including what's deferred (overlay refresh + disposability). Mitigation: announcement has a §"What's deferred" section citing `DELIB-S328-...-OVERLAY-SCOPE-REVISION` + work_list row 31.

**Risk 3 — Tag-vs-commit ordering (low).** Tagging v0.7.0-rc1 must happen on a commit that includes the Slice 8 closeout artifacts. Mitigation: §"Implementation Plan" makes the tag a separate post-VERIFIED operator step, ensuring it lands on the right commit.

**Risk 4 — CI lane drift between slice commits and tag (low).** If Slice 8's closeout commit lands but CI hasn't re-run on a fresh state, the gate verification might pass locally but fail on a fresh CI run. Mitigation: gate runs in `_verify_slice8_closeout.py` exercise the same pytest commands CI uses; local PASS implies CI PASS.

**Rollback path:** Slice 8 ships docs + a verification script + 1 release-readiness field + 1 CHANGELOG entry. No source code or test changes (the verification test from Slice 7 is cited, not modified). Reversible via `git revert` of the implementation commit.

## Decision Needed From Owner

**None at NEW time.** Decisions 2, 4, 5 all resolved at S329 proposal-draft time. The version tag is a separate post-VERIFIED step; that authorization is not part of this NEW.

## Open Items

- The `python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 release closeout"` probe will run as part of Codex review's Prior Deliberations check.
- Decisions 2/4/5 deliberation archive insertion is owner-gated; for now answers cited inline.
- The version tag (`git tag -a v0.7.0-rc1 -m "..."`) is a separate operator step after Codex VERIFIED. Recommend asking the owner for the tag-commit authorization at that time.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
