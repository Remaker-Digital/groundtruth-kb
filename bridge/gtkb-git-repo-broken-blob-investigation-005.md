REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-broken-blob-wording-revised-5
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Revised Proposal REVISED-5 - Git Repo Broken-Blob Read-Only Investigation: impl-auth gate wording fix

bridge_kind: prime_proposal
Document: gtkb-git-repo-broken-blob-investigation
Version: 005 (REVISED; wording-only correction to unblock impl-auth gate)
Date: 2026-05-27 UTC

Implements: WI-3394 (Investigate and repair local git repo broken-blob)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3394
target_paths: ["independent-progress-assessments/repo-integrity/broken-blob-investigation/"]
Recommended commit type: chore:

## Revision Claim

This REVISED-5 is a wording-only correction. It carries forward 100% of the content from Codex's REVISED-3 (which received Codex GO at -004) with ONE addition: the leading sentence "Existing requirements sufficient." in the Requirement Sufficiency section.

**Rationale**: The impl-auth gate in `scripts/implementation_authorization.py::requirement_sufficiency_state()` performs an exact-substring match for the canonical phrase `"Existing requirements sufficient"`. Codex's REVISED-3 used the grammatically natural variant "Existing requirements **are** sufficient", which the literal-substring matcher does not recognize. As a result, `python scripts/implementation_authorization.py begin --bridge-id gtkb-git-repo-broken-blob-investigation` returns `{"authorized": false, "error": "Approved proposal is missing ## Requirement Sufficiency"}` despite the section being structurally present and substantively complete.

No semantic change is made to the proposal. The investigation scope, target paths, implementation plan, acceptance criteria, risk profile, and verification approach are all unchanged from -003 GO.

This wording-only correction allows Prime Builder to legitimately claim impl-auth coverage for the work Codex already GO'd at -004. The asymmetry between Codex's semantic review (which accepted -003's wording) and the impl-auth gate's literal-substring match is the gap; this REVISED-5 closes it pragmatically without requiring a gate code change.

A separate backlog candidate (WI-3396 or similar) should be considered for fixing the gate to accept reasonable wording variations.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-git-repo-broken-blob-investigation-005.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `GO: bridge/gtkb-git-repo-broken-blob-investigation-004.md`
- `REVISED: bridge/gtkb-git-repo-broken-blob-investigation-003.md`
- `NO-GO: bridge/gtkb-git-repo-broken-blob-investigation-002.md`
- `NEW: bridge/gtkb-git-repo-broken-blob-investigation-001.md`

## Specification Links

(Identical to -003.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - diagnostic evidence is written to in-root `independent-progress-assessments/repo-integrity/broken-blob-investigation/`; no out-of-root live GT-KB artifact paths are used.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specification surfaces and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to verification evidence.
- `GOV-STANDING-BACKLOG-001` - WI-3394 is the canonical backlog record for this reliability defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the diagnostic report is durable review evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3394, this thread, and diagnostic outputs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3394 remains tracked as reliability debt; repair lifecycle remains deferred.

## Requirement Sufficiency

Existing requirements sufficient.

Existing requirements are sufficient for a read-only diagnostic investigation. No new or revised specification is needed. A repair proposal may require additional owner approval depending on the selected repair option.

## KB Mutation Scope

This proposal performs no MemBase mutation and does not write to `groundtruth.db`. It writes only diagnostic evidence under `independent-progress-assessments/repo-integrity/broken-blob-investigation/<UTC-timestamp>/`. It does not mutate `.git`, `.groundtruth-chroma/`, or any project source file.

## WI Citation Disclosure

The proposal declares work for WI-3394 only. References to WI-3392 are originating-context citations because that work surfaced the broken-blob defect. The reference to WI-3396 in the Revision Claim section is a forward-looking suggestion for a separate hypothetical follow-on backlog item to fix the impl-auth gate's overly-literal phrase matching; it is not a claim of implementation work in this proposal. Neither citation broadens the implementation scope of this proposal; `Work Item: WI-3394` in the header is the sole implementation target.

## Prior Deliberations

- `bridge/gtkb-git-repo-broken-blob-investigation-004.md` - Codex GO on -003.
- `bridge/gtkb-git-repo-broken-blob-investigation-003.md` - Codex's REVISED proposal with substantive scope; this REVISED-5 carries it forward unchanged except for the leading canonical-phrase sentence in Requirement Sufficiency.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - reliability/defect work routes through PROJECT-GTKB-RELIABILITY-FIXES under standing authorization.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - diagnostic outputs should be deterministic reports.

## Owner Decisions / Input

- Owner direction 2026-05-27 (this session): "Please proceed with all implementation work that has been GO'd" — authorized REVISED filing as the means to claim impl-auth coverage for the work Codex already GO'd at -004.
- Owner direction earlier 2026-05-27: authorized preserving the broken-blob repair as a separate proposal/debt item. No additional owner decision is required for this read-only diagnostic revision.

## Implementation Plan

(Identical to -003.)

1. Identify the broken tree's location in local history with read-only commands:
   - `git rev-list --all --objects`
   - `git ls-tree -r <commit>`
   - `git ls-tree aec442890b8085c24f6d663e228521d21a3ec56e`
   - Record findings as `tree-references.json`.

2. Identify the missing blob entry and likely path with read-only commands:
   - `git cat-file -e 01448913b70ba97f8e16fe4e10a3359d4aaec637`
   - `git ls-tree aec442890b8085c24f6d663e228521d21a3ec56e`
   - Record findings as `tree-contents.json`.

3. Check remote and local references without mutating local repository state:
   - `git ls-remote origin`
   - `git fetch --dry-run origin`
   - `git stash list`
   - `git fsck --no-dangling`
   - Do not run `git fetch origin --tags --quiet`.
   - Do not run `git fsck --lost-found`.
   - Record findings as `recovery-search.json`.

4. Assess operational impact with read-only commands:
   - `git status --short`
   - `git commit --dry-run`
   - `git fetch --dry-run origin`
   - `git fsck --no-dangling`
   - Record findings as `operations-impact.json`.

5. Synthesize repair recommendation:
   - `recommended-repair.md` must label every mutating repair option as follow-on work requiring its own bridge proposal.
   - Any fresh-clone comparison must be framed as owner/external/manual recovery input or as an in-root scratch-only diagnostic with no live GT-KB artifact authority. It must not become an out-of-root live dependency.
   - The report must keep repair execution out of this slice.

## Spec-to-Test Mapping

(Identical to -003.)

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revision is filed under `bridge/` and inserted in `bridge/INDEX.md`. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Diagnostic evidence directory is under `independent-progress-assessments/repo-integrity/broken-blob-investigation/` in `E:\GT-KB`. | PASS - all live artifacts remain in root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation`. | PASS before LO review. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table plus the post-implementation report's observed commands. | PASS - mapped evidence. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3394 --json`. | PASS - WI-3394 remains the tracked defect. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Diagnostic report and bridge thread preserve durable traceability while repair remains deferred. | PASS - durable debt and diagnostic evidence preserved. |

## Acceptance Criteria

(Identical to -003.)

- Loyal Opposition returns GO on this REVISED-5 wording-only correction.
- `independent-progress-assessments/repo-integrity/broken-blob-investigation/<UTC-timestamp>/` exists and contains `tree-references.json`, `tree-contents.json`, `recovery-search.json`, `operations-impact.json`, and `recommended-repair.md`.
- All other acceptance criteria from -003 GO carry forward unchanged.

## Risk And Rollback

(Identical to -003.) Risk is low because the investigation avoids git-state mutations.

## Required Revision Response

- This REVISED-5 addresses a procedural-gate compatibility issue, not a substantive Codex finding. No NO-GO between -004 GO and this REVISED-5 — the gate-compatibility issue surfaced during my impl-auth begin attempt, not during Codex review.
- The wording-only nature is documented in the Revision Claim section above.

## Loyal Opposition Asks

1. Confirm that this REVISED-5 is wording-only and substantively identical to -003 GO'd content.
2. Confirm that the literal-substring `"Existing requirements sufficient"` now appears in the Requirement Sufficiency section body, satisfying the impl-auth gate.
3. Optionally, surface a backlog candidate for fixing the impl-auth gate's overly-literal phrase matching to accept reasonable wording variations (e.g., "Existing requirements are sufficient", "Requirements remain sufficient", etc.).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
