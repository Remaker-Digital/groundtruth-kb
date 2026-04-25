# Independent Progress Assessments — Archive

This directory holds one-shot session utilities that were active operational
artifacts at one point but have since been superseded, completed, or
explicitly retired by the owner.

## Why this directory exists

Per `bridge/gtkb-root-directory-migration-post-verify-009.md` Phase 1f
(owner Decision #5, ratified 2026-04-24), one-shot scripts that:

- ran exactly once for a specific session or migration step,
- produced their effect (KB inserts, file edits, doc generation), and
- have no remaining callers in active tooling

are moved here rather than retained in the active surface. The benefits:

1. **Verifier scope shrinks.** `scripts/migrate_root_to_gtkb.py` excludes
   `independent-progress-assessments/archive/**` from its walk, so the
   verifier no longer flags these inert files for residual workstation
   path literals.

2. **Active surface stays signal-rich.** New contributors looking at
   `independent-progress-assessments/` see only currently-meaningful
   artifacts (LO logs, runbooks, the bridge-automation directory),
   not a graveyard of session-dated utility scripts.

3. **History preserved.** Files are moved (`git mv` for tracked files,
   plain `mv` for untracked Cursor-generated files), so `git log --follow`
   against the archived path still shows the full pre-archive history
   for anything that was tracked.

## Adopter / Loyal Opposition rule

Do NOT delete files from this directory. Two reasons:

- They are reference material for understanding past sessions' decisions.
- The owner-directive default is to preserve audit trail; only explicit
  owner approval reverses that.

If a file in here turns out to still be referenced by active tooling
(missed by the GO condition #2 reference grep at archive time), restore
it to its original location and update this README. The reference grep
that gated the original archive was:

```bash
grep -RIn "_insert_s136_prompt|migrate_topic_files_to_kb|rewrite_memory_s140|create_corrected_proposal_template|create_gtkb_visual_docs|create_locked_remaker_docs|add_locked_doc_graphics|prime-bridge-cleanup-2026-04-08" .github/ scripts/ src/ tests/ tools/ docs/
```

Only hits at archive time were in `scripts/migration-{execute,verify}-output.txt`
and `scripts/verify-output.txt` — i.e. dry-run report entries, not
live tooling.

## Inventory at archive time (2026-04-24)

| File | Origin / purpose | Status |
|------|------------------|--------|
| `add_locked_doc_graphics.py` | One-shot doc graphics insertion utility | Retired |
| `create_corrected_proposal_template.py` | One-shot bridge proposal template generator | Retired |
| `create_gtkb_visual_docs.py` | One-shot visual-docs generator (v1) | Retired |
| `create_gtkb_visual_docs_v2.py` | One-shot visual-docs generator (v2) | Retired |
| `create_locked_remaker_docs.py` | One-shot locked-doc generator | Retired |
| `prime-bridge-cleanup-2026-04-08.ps1` | One-shot bridge cleanup for 2026-04-08 incident | Retired |
| `cursor-legacy/` | Pre-existing legacy archive sub-tree | Retained (see directory) |

## Companion archive

The matching archive for `scripts/`-rooted one-shots lives at
`scripts/archive/`. The same rules apply.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
