NEW
::init gtkb lo
::open build

# gtkb-wi5593-cli-content-file-help-text-foreign-hunk-revert — Revert foreign --content-file help-text hunk mis-attributed to WI-5326

bridge_kind: prime_proposal
Document: gtkb-wi5593-cli-content-file-help-text-foreign-hunk-revert
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-18 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (owner-declared session-stated role, transcript_init_keyword resolution source)

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5593

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

During Loyal Opposition verification/finalization of WI-5326 (bridge/gtkb-wi5326-atomic-work-item-test-linkage-004.md), `.claude/skills/verify/helpers/write_verdict.py --finalize-verified --include groundtruth-kb/src/groundtruth_kb/cli.py` staged the entire current working-tree state of cli.py — one of WI-5326's five declared `target_paths` — rather than a scoped hunk. cli.py's working tree at that moment also contained an uncommitted, unrelated ~9-line expansion of the `--content-file` option's help text on the `generate_approval_packet` command (lines ~3900-3908), which landed together with the legitimate WI-5326 change in commit `604eb240134913ef987a66cd71ff4f9ce725962f` ("fix(backlog): WI-5326 atomic work-item/test linkage and exact repair VERIFIED"). No bridge thread named cli.py as in-scope for this help-text change, and it has no connection to WI-5326's actual scope (atomic work-item/test linkage repair).

Investigation traced the hunk's origin precisely: it is the third fragment of the same in-flight "narrative approval-packet target/content separation" feature governed by WI-5574 (bridge/gtkb-wi5574-narrative-approval-packet-content-source-001.md, filed the same day, status NEW/backlogged). WI-5574 explicitly governs "two pre-existing foreign source hunks" in `cli_approval_packet.py` and `governance/narrative_artifact_packet.py` that implement exactly the target/content-separation semantic this cli.py help text describes — confirmed by matching design language between the cli.py help string ("--target still supplies the packet's real path identity... content-file supplies full_content in place of reading --target") and the new, still-uncommitted docstring on `narrative_artifact_packet.py`'s `build_narrative_packet` ("target_path supplies the packet's path identity... content_source, when given, supplies the packet's full_content instead of reading it from target_path"). WI-5574's `target_paths` do not include cli.py, most likely because by the time WI-5574 was filed, the cli.py fragment had already been swept into the WI-5326 commit and was no longer visible in the working tree as a foreign hunk to scan for.

Confirmed via full read of `generate_approval_packet`'s body: `content_file` flows through to `run_generate_approval_packet` completely unconditionally (no `--kind` branching in cli.py itself), so this help text is a pure documentation change with zero runtime effect. Reverting it does not touch the narrative-packet dispatch logic in `cli_approval_packet.py`/`governance/narrative_artifact_packet.py`, which remains correctly held under WI-5574's own "foreign and unverified" governance pending its independent review.

This proposal reverts cli.py's `--content-file` help text to its exact prior single-line form ("Formal artifact content file."), restoring WI-5326's commit scope to only what its VERIFIED verdict actually reviewed and tested. It does not rewrite git history (`604eb240` is untouched); this is a new, separate forward commit. The more complete help text should be reintroduced later as part of WI-5574's own properly-reviewed scope (a REVISED version of that thread could expand `target_paths` to include cli.py) rather than preserved now on the strength of this investigation's own unreviewed inference — WI-5574 itself does not extend that courtesy to its own two sibling hunks, and this one should not receive better treatment for having (accidentally) skipped review entirely.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal restores the bridge audit-trail integrity that a whole-file `--include` finalization silently broke: a VERIFIED commit must contain only what its linked specifications/report describe.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites its governing specs and WI-5593's own `source_spec_id` (`GOV-WORK-TREE-HYGIENE-001`).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization, Project, Work Item, and `target_paths` metadata are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11643 (linked to WI-5593) is the spec-derived test; see Spec-Derived Verification Plan below.
- `GOV-STANDING-BACKLOG-001` — WI-5593 is a single, ordinary work item tracked in MemBase's canonical `work_items` table under PROJECT-GTKB-TREE-STABILIZATION / worktree-finalization; this is not a bulk or batch backlog operation.
- `GOV-WORK-TREE-HYGIENE-001` — WI-5593's own governing spec; this is squarely a work-tree/finalization hygiene defect (foreign-hunk contamination via whole-file `--include`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this proposal follows the durable-artifact chain (work item → linked test → phase → bridge proposal) rather than treating the fix as a transient chat edit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the corrective work is represented as a versioned work item, test, and bridge thread rather than an unlogged direct edit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — discovering unreviewed content in a VERIFIED commit is exactly the kind of artifact-lifecycle trigger (defect discovered → work item → test → proposal) this DCL requires capturing.

## Prior Deliberations

No prior deliberation directly addresses this exact defect. I ran `gt deliberations search` for both "foreign hunk whole-file include finalization helper contamination" and "narrative approval packet content source separation cli help text" before drafting this proposal; the nearest semantic-similarity results were generic LO verdict records (NO-GO/GO/VERIFIED entries on unrelated WIs), none on-point.

Sibling/related bridge threads carried forward for context:

- `bridge/gtkb-wi5574-narrative-approval-packet-content-source-001.md` (NEW, status=backlogged) — the in-flight feature this hunk is the third fragment of; does not currently cover cli.py in its `target_paths`.
- `bridge/gtkb-generate-approval-packet-cli-012.md` (VERIFIED 2026-05-27) — the original base CLI command this option belongs to; predates and is unrelated to this specific hunk.
- `bridge/gtkb-wi5401-hunk-patch-integrity-gate-004.md` (VERIFIED, resolved) — a related but distinct concern (hunk-*patch byte/hash* integrity of already-filed `.patch` artifacts), not the same defect as this whole-file `--include` contamination.

## Owner Decisions / Input

This proposal does not depend on a fresh owner approval. It proceeds under the active `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` project authorization (which covers corrective/hygiene work within `PROJECT-GTKB-TREE-STABILIZATION`, the same project WI-5326 and WI-5574 are grouped under) plus the standard Prime Builder → Loyal Opposition GO/NO-GO bridge cycle. No AskUserQuestion-gated decision class (approval, waiver, priority choice, formal artifact approval, requirement clarification, destructive action, deployment) applies to a single-file, zero-behavior-change documentation-string revert.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`'s bridge audit-trail discipline and the file-bridge-protocol.md "Mandatory VERIFIED Commit-Finalization Gate" already establish that a VERIFIED commit's content must match what was reviewed; this proposal restores compliance with that existing requirement rather than introducing a new one.

## Spec-Derived Verification Plan

| Specification | Verification | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `git show HEAD -- groundtruth-kb/src/groundtruth_kb/cli.py` after the revert commit | Shows only the `--content-file` help-string reverted to its single-line form; no other change to cli.py in that commit. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run TEST-11643 (add/execute a focused CLI test, e.g. via Click's `CliRunner` invoking `--help` on `generate_approval_packet`, or introspecting the command's `params`, asserting the `--content-file` help string equals exactly `"Formal artifact content file."`) | PASS; this test does not exist in the repo yet and must be added as part of this implementation per GOV-12. |
| all linked specs | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py` and `ruff format --check` on the same file | All checks pass. |
| all linked specs | `git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py` | Exit 0, no output. |
| all linked specs | `git diff -- groundtruth-kb/src/groundtruth_kb/cli.py` (working tree) immediately before implementing | No other uncommitted change to cli.py exists that would conflict with this revert (confirmed at proposal time; re-verify at implementation time since other sessions may be concurrently active on this shared file). |

## Risk / Rollback

Risk is very low: a single Click option's help string in one file, no behavior change (confirmed `content_file` flows through to `cli_approval_packet.py` unconditionally regardless of `--kind`), no existing test depends on the expanded string (repo-wide grep confirmed zero matches for the literal expanded text outside cli.py itself). Rollback is a trivial single-commit revert of this commit; re-applying the expanded text would in any case be necessary once WI-5574 lands with its own properly-reviewed scope covering cli.py.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5593-cli-content-file-help-text-foreign-hunk-revert`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — this is a scope-correction revert of unreviewed content that rode along on a prior fix commit (604eb240), restoring that commit's actual reviewed/tested scope.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
