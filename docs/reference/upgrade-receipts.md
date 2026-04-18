# Upgrade Receipts

`gt project upgrade --apply` records a **rollback receipt** for every
upgrade that lands a payload merge commit. The receipt captures the
information needed to roll back the upgrade cleanly later via
`git revert -m 1 <merge_commit>`.

This page explains how receipts are stored, when they are tracked versus
filesystem-only, and how to opt in to tracked receipts on a legacy project.

## Two modes

Receipts can live in one of two modes depending on your adopter project's
`.gitignore` state:

### Tracked mode (default for fresh scaffolds)

The receipt JSON file is written to
`.claude/upgrade-receipts/active/<id>.json` and committed to your current
branch in a **separate post-merge commit**. This commit is NOT part of the
payload merge tree, so `git revert -m 1 <merge_commit>` reverts only the
payload.

Fresh projects created via `gt project init` start in tracked mode because
the scaffolded `.gitignore` does not broadly ignore `.claude/`.

### Filesystem mode (default for legacy projects that ignore `.claude/`)

The receipt JSON is written to the same path but NOT committed. It lives
only in your working tree. You can still use it to roll back an upgrade,
but the receipt itself is not preserved across branch switches or repo
clones.

Legacy projects with a broad `.claude/` ignore in `.gitignore` default to
this mode because the receipt path is inside the ignored subtree.

## How mode is determined

Before any upgrade work, `gt project upgrade --apply` runs:

```bash
git check-ignore --no-index -- .claude/upgrade-receipts/active/<tentative-id>.json
```

- Exit **0** (path is ignored) → **filesystem** mode.
- Exit **1** (path is not ignored) → **tracked** mode.
- Any other exit → the upgrade fails pre-flight with a diagnostic message.

`gt project upgrade --apply` does NOT modify your `.gitignore`. The
adopter's current gitignore state is authoritative.

## Opting in to tracked mode on a legacy project

If your project has a broad `.claude/` ignore AND you want tracked
receipts, manually add this 4-line block to your `.gitignore`. The block
MUST appear AFTER the broad `.claude/` ignore rule so it wins last-match:

```gitignore
# gt-upgrade tracked receipts — re-include ONLY the upgrade-receipts
# subtree when .claude/ is otherwise ignored. MUST appear AFTER any
# .claude/ ignore rule (last-match-wins).
!/.claude/
/.claude/*
!/.claude/upgrade-receipts/
!/.claude/upgrade-receipts/**
```

**What this block does:**

- Line 1 (`!/.claude/`) re-includes the `.claude/` directory itself so git
  will descend into it.
- Line 2 (`/.claude/*`) re-ignores every direct child of `.claude/` at the
  top level. This is why the block is safe only when your project was not
  tracking any other `.claude/` artifacts to begin with.
- Lines 3–4 re-include the `upgrade-receipts/` subtree (and everything
  beneath it recursively).

**If you want both tracked receipts AND tracked managed artifacts
(hooks, rules, skills, settings.json)**, the cleanest path is to REMOVE
the broad `.claude/` ignore entirely rather than add the re-inclusion
block. Fresh GT-KB projects scaffold without a broad `.claude/` ignore
precisely so all managed artifacts stay trackable.

## Opting out of tracked receipts

If you want receipts to stay filesystem-only (not in git), append an
explicit ignore AFTER any re-inclusion block:

```gitignore
.claude/upgrade-receipts/
```

The last-match-wins rule means this re-ignores the receipt subtree even
if earlier lines re-included it.

## Why `gt project upgrade --apply` does not modify `.gitignore`

Earlier design iterations had `upgrade --apply` append the re-inclusion
block when absent. This created an ambiguity: a legacy adopter's absent
block could mean "never had it" (wanted receipts) or "deliberately
removed it" (opt-out). With a single source of truth — the current
`.gitignore` state — there is no ambiguity. Adopter intent is explicit
and preserved.

## Receipt JSON schema (v1)

See the `ReceiptJSON` TypedDict in
`src/groundtruth_kb/project/rollback.py` for the authoritative field list:

- `schema_version: "v1"`
- `receipt_id`: opaque unique identifier
- `merge_commit`: full SHA of the payload merge commit
- `target_branch`: branch the merge landed on
- `from_version` / `to_version`: GT-KB scaffold versions
- `mode`: `"tracked"` or `"filesystem"`
- `created_at`: ISO-8601 UTC timestamp
- `artifact_classes_touched`: which artifact classes the upgrade changed

## Authorizing bridge

`bridge/gtkb-rollback-receipts-014.md` (Codex GO, 2026-04-18). Full
design trail in `bridge/gtkb-rollback-receipts-001.md` through `-014.md`
(7 versions total).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
