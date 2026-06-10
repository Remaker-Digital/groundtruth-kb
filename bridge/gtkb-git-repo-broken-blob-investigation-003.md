REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-05-27-prime-builder-bridge-continuation
author_model: GPT-5
author_model_version: codex
author_model_configuration: reasoning=medium
author_metadata_source: session

# Revised Proposal - Git Repo Broken-Blob Read-Only Investigation

bridge_kind: prime_proposal
Document: gtkb-git-repo-broken-blob-investigation
Version: 003 (REVISED)
Date: 2026-05-27 UTC

Implements: WI-3394 (Investigate and repair local git repo broken-blob)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3394
target_paths: ["independent-progress-assessments/repo-integrity/broken-blob-investigation/"]
Recommended commit type: chore

## Revision Claim

This revision addresses the NO-GO findings in `bridge/gtkb-git-repo-broken-blob-investigation-002.md`. The investigation remains a separate pre-repair slice and remains read-only against git repository state. The mutating commands from the original proposal are removed: no non-dry-run `git fetch`, no `git fsck --lost-found`, no branch or tag movement, no object deletion, no history rewrite, and no commits.

The git fsck missing-blob defect remains preserved as follow-up reliability debt in WI-3394. This proposal only scopes a diagnostic report; repair execution is out of scope and must be proposed separately after the diagnostic report is reviewed.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-git-repo-broken-blob-investigation-003.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `NO-GO: bridge/gtkb-git-repo-broken-blob-investigation-002.md`
- `NEW: bridge/gtkb-git-repo-broken-blob-investigation-001.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - diagnostic evidence is written to in-root `independent-progress-assessments/repo-integrity/broken-blob-investigation/`; no out-of-root live GT-KB artifact paths are used.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specification surfaces and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to verification evidence.
- `GOV-STANDING-BACKLOG-001` - WI-3394 is the canonical backlog record for this reliability defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the diagnostic report is durable review evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3394, this thread, and diagnostic outputs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3394 remains tracked as reliability debt; repair lifecycle remains deferred.

## Requirement Sufficiency

Existing requirements are sufficient for a read-only diagnostic investigation. No new or revised specification is needed. A repair proposal may require additional owner approval depending on the selected repair option.

## KB Mutation Scope

This proposal performs no MemBase mutation and does not write to `groundtruth.db`. It writes only diagnostic evidence under `independent-progress-assessments/repo-integrity/broken-blob-investigation/<UTC-timestamp>/`. It does not mutate `.git`, `.groundtruth-chroma/`, or any project source file.

## WI Citation Disclosure

The proposal declares work for WI-3394 only. References to WI-3392 are originating-context citations because that work surfaced the broken-blob defect.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - reliability/defect work routes through PROJECT-GTKB-RELIABILITY-FIXES under standing authorization.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - diagnostic outputs should be deterministic reports that can later become reusable tooling if the pattern recurs.

## Owner Decisions / Input

Owner direction on 2026-05-27 authorized preserving the broken-blob repair as a separate proposal/debt item. No additional owner decision is required for this read-only diagnostic revision. Any mutating repair remains deferred to a follow-on bridge proposal.

## Implementation Plan

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

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revision is filed under `bridge/` and inserted in `bridge/INDEX.md`. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Diagnostic evidence directory is under `independent-progress-assessments/repo-integrity/broken-blob-investigation/` in `E:\GT-KB`. | PASS - all live artifacts remain in root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation`. | PASS before LO review. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table plus the post-implementation report's observed commands. | PASS - mapped evidence. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3394 --json`. | PASS - WI-3394 remains the tracked defect. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Diagnostic report and bridge thread preserve durable traceability while repair remains deferred. | PASS - durable debt and diagnostic evidence preserved. |

## Acceptance Criteria

- Loyal Opposition returns GO on this revised read-only investigation proposal.
- `independent-progress-assessments/repo-integrity/broken-blob-investigation/<UTC-timestamp>/` exists and contains `tree-references.json`, `tree-contents.json`, `recovery-search.json`, `operations-impact.json`, and `recommended-repair.md`.
- `tree-references.json` identifies commits or refs that reference tree `aec442890b8085c24f6d663e228521d21a3ec56e`, or states that the tree is unreachable with supporting evidence.
- `tree-contents.json` identifies the missing blob entry and path where possible.
- `recovery-search.json` records only read-only remote/local reference checks.
- `operations-impact.json` identifies which normal git operations are affected.
- `recommended-repair.md` recommends a follow-on repair path and explicitly marks mutating repair as out of scope for this slice.
- No non-dry-run fetch is run.
- `git fsck --lost-found` is not run.
- No git history rewrite, branch/tag movement, object deletion, or commit creation occurs.

## Risk And Rollback

Risk is low because the investigation avoids git-state mutations. The only created artifacts are diagnostic report files under `independent-progress-assessments/repo-integrity/broken-blob-investigation/`.

Rollback: delete the timestamped diagnostic report directory before commit if the investigation report is withdrawn. No git object-store rollback is required because this slice does not mutate `.git`.

## Required Revision Response

- Finding P1-001, read-only scope included mutating commands: addressed by removing non-dry-run fetch and `--lost-found`, and by constraining every diagnostic command to read-only usage.
- Finding P2-001, sibling clone outside root: addressed by requiring any fresh-clone recovery to be a future owner/external/manual input or an in-root scratch-only diagnostic, never an out-of-root live GT-KB dependency.

## Pre-Filing Preflights

Prime will file this revision with the bridge helper so candidate applicability and ADR/DCL clause preflights run before the live `bridge/INDEX.md` update.
