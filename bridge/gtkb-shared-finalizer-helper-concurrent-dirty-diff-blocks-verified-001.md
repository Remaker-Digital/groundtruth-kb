ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-17T13-56-37Z-loyal-opposition-B-c17535
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code headless bridge auto-dispatch; Loyal Opposition harness B; dispatcher id 2026-07-17T13-56-37Z-loyal-opposition-B-c17535

# Loyal Opposition Advisory - Shared VERIFIED-Finalizer Helpers Are Concurrently Dirty With Two Unreviewed Threads

bridge_kind: governance_advisory
Document: gtkb-shared-finalizer-helper-concurrent-dirty-diff-blocks-verified
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-17

## Source

Discovered as a side effect of reviewing `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-003.md`
(WI-5373, PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL). A peer LO
session (`B-2026-07-17T14-10-00Z-envelope-slice-a-safe-verify`) landed a
`NO-GO` on that thread at `-004.md` for an unrelated finding (a premature
`WI-5373` resolution) before I could file mine; standing down on a competing
verdict there is correct and separately handled. This finding is independent
of that thread's outcome and was not covered by the peer's `-004` verdict, so
per the standing "findings must not be left as a chat aside" directive it is
filed here as its own advisory rather than folded into a footnote.

## Claim

The three governed bridge-writing helper surfaces Loyal Opposition must use to
safely record any verdict - `.claude/skills/verify/helpers/write_verdict.py`
(+ `.codex`/`.cursor` projections), `scripts/gtkb_bridge_writer.py`, and
`.claude/skills/bridge-propose/helpers/write_bridge.py` (+ `.codex`
projection) - are currently all simultaneously dirty (uncommitted, modified
relative to `HEAD`) in the shared working tree, carrying two DIFFERENT open,
unreviewed Prime Builder implementation reports from the same authoring
session (`author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627`):

- `bridge/gtkb-wi5401-hunk-patch-integrity-gate-003.md` (status `NEW`,
  unreviewed) - `target_paths` includes
  `.claude/skills/verify/helpers/write_verdict.py` (+ 2 harness projections)
  and `scripts/gtkb_bridge_writer.py`. Diff size: `write_verdict.py` +159/-c
  lines (x3 projections), `gtkb_bridge_writer.py` +157/-c lines.
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-003.md` (status
  `NEW`, unreviewed) - `target_paths` includes
  `.claude/skills/bridge-propose/helpers/write_bridge.py` (+ 1 harness
  projection). Diff size: +26/-c lines (x2 projections).

`git log -3 --oneline -- .claude/skills/verify/helpers/write_verdict.py`
confirms the last commit touching that file is `42a252ab chore(gtkb): sweep
governable platform work`; the dirty diff postdates it and is not part of any
commit.

**Concrete risk:** `.claude/rules/file-bridge-protocol.md` § "Mandatory
VERIFIED Commit-Finalization Gate" requires `VERIFIED` to be recorded
exclusively through `write_verdict.py --finalize-verified`. Any Loyal
Opposition session (mine or a peer's) attempting to finalize `VERIFIED` on
*any* thread right now - not just `gtkb-envelope-protocol-slice-a-canonical-insertion`
- would execute the current on-disk, uncommitted, not-yet-independently-reviewed
WI-5401 code to perform a governance-terminal action (an atomic git commit
closing that thread). This inverts the review-before-execution principle the
GO/NO-GO/VERIFIED protocol exists to enforce, independent of whether the new
code is actually buggy. Given ~50 bridge threads were pending review across the
platform at this dispatch, the exposure is not limited to one thread.

**Mitigating detail (traced, not assumed):** the lower-level primitive
`scripts/gtkb_bridge_writer.py:write_bridge_file()` - used for plain
`GO`/`NO-GO` writes that do not go through `--finalize-verified` - is itself
byte-identical to `HEAD`. The WI-5401 diff only touches
`_patch_paths_from_bytes`/`_hunk_patch_metadata_from_report`/
`_hunk_patch_covered_paths` (hunk-patch artifact validation, reached via
`publish_lo_verdict`, not `write_bridge_file`), and `write_bridge_file()`'s
full dependency chain (`run_bridge_compliance_audit`,
`validate_verdict_evidence_anchors`, `ensure_author_metadata`,
`_reject_synthetic_session_context_id`, `.claude/hooks/bridge-compliance-gate.py`)
is entirely clean (verified via `git status --short` on each). This advisory
itself was filed through that clean path. So plain `NO-GO`/`GO` writes remain
safe; only `--finalize-verified` (and, by extension, the newer
`publish_lo_verdict`/hunk-patch coverage path) is exposed.

## Owner Decision Needed

None blocking. This is an operational-sequencing observation, not a policy
question - no owner decision is required to act on it. Flagging per the
"findings must not be left as a chat aside" standing directive
(`[[findings-always-become-advisory-proposals]]`) so it is durably tracked
rather than lost in this session's transcript.

## Recommended Prime Action

1. Prioritize independent LO review of `gtkb-wi5401-hunk-patch-integrity-gate`
   and `gtkb-wi5409-cross-harness-proposal-linkage-gate` ahead of other
   pending items, specifically because they are the two threads currently
   holding the shared `VERIFIED`-finalization machinery dirty for every other
   in-flight thread, not just their own.
2. Once both are independently reviewed and (if approved) committed, the
   finalizer helpers return to a clean `HEAD`-matching state and normal
   `VERIFIED` finalization resumes being safe platform-wide.
3. As a durable systemic improvement (separate follow-on, not required before
   item 1/2): consider a cheap self-check inside
   `write_verdict.py --finalize-verified` that runs `git status` on its own
   file (and `gtkb_bridge_writer.py`) before executing, and fails closed with
   a clear message when either is dirty relative to `HEAD`, rather than
   relying on each reviewer to independently discover and manually trace this
   class of exposure (as this advisory's author had to).
4. No action is required specifically on
   `gtkb-envelope-protocol-slice-a-canonical-insertion`; that thread already
   has an independent `NO-GO` from a different, unrelated finding
   (`bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-004.md`).

## Classification Slot

adopt

Rationale: this is a factual, verified observation of current repository
state (not a design proposal requiring alternatives analysis), and the
recommended action (review-priority resequencing) requires no new
specification, architecture decision, or design constraint - only routine
dispatch/review prioritization Prime Builder can act on directly. No owner
grilling gate applies (`adopt`/`adapt` implementation-implied gate is scoped
to peer-solution/external-system advisories per
`.claude/rules/peer-solution-advisory-loop.md`; this advisory recommends
sequencing, not an implementation itself).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
