NEW

# GT-KB Bridge INDEX Phantom-VERIFIED References Reconciliation

**Status:** NEW (P2 bridge hygiene; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §3.1; reaffirmed in [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) (Codex VERIFIED). 7 INDEX VERIFIED references point to bridge files absent from disk and git history.

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-002.md](bridge/s317-working-tree-triage-002.md) F4 — first surfaced phantom INDEX class.
- [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §3 — named this follow-up.
- [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) — Codex VERIFIED + Q1 ("File the follow-up after this triage is GO/implemented or explicitly paused").
- **Existing INDEX reconciliation precedents** (HTML comments above thread entries):
  - `gtkb-slice2b-metrics-index-reconciliation` thread — VERIFIED at `-008` (similar class; INDEX entry has annotation).
  - `gtkb-membase-effective-use-umbrella` (annotation about S306-S307 parallel-poller phantom versions).
  - `gtkb-root-directory-migration-post-verify` (annotation about -001..-009 + -011 parallel-poller phantoms).

---

## §0. Scope

Annotate the 7 known phantom INDEX VERIFIED references in `bridge/INDEX.md` with HTML comment blocks per existing precedent. **Annotation only**; no per-thread state mutation, no file restoration, no thread reopens.

**In scope:**
- Edit `bridge/INDEX.md` to add HTML comment blocks above each affected `Document:` line for the 7 phantom-INDEX threads.
- Document the phantom-INDEX defect class explicitly in each comment.
- Optionally cite per-thread companion (e.g., `gtkb-root-directory-migration` ↔ `gtkb-root-directory-migration-post-verify`).

**Out of scope:**
- Per-thread "did the work actually ship?" investigation (deferred to per-thread follow-up bridges if owner desires).
- File restoration from any source (no source is known; git history confirms absence).
- INDEX entry restructure or thread reopening.
- Any code or test changes.

---

## §1. Inventory (verified 2026-04-27)

For each phantom INDEX entry, latest existing version on disk + companion thread (if any):

| INDEX phantom ref | Latest on-disk version | Git history of phantom | Companion thread (potentially related work) |
|---|---|---|---|
| `gtkb-root-directory-migration-018.md` | `-post-verify-019.md` (different thread name) | ABSENT | `gtkb-root-directory-migration-post-verify` (VERIFIED at `-019` on disk; likely the canonical close-out) |
| `gtkb-app-boundary-mechanism-audit-012.md` | `-003.md` | ABSENT | None known; thread appears to have stalled at -003 |
| `gtkb-membase-effective-use-umbrella-014.md` | `-001.md` | ABSENT | Existing INDEX annotation already references S306-S307 parallel-poller (versions 004-022 are listed but only -001 exists) |
| `gtkb-dashboard-industry-alignment-slice2a-visibility-008.md` | `-007.md` | ABSENT | Slice 2 work continued in `slice2b-metrics` (VERIFIED at -026 reconciled by `gtkb-slice2b-metrics-index-reconciliation`) |
| `gtkb-dora-telemetry-foundation-008.md` | `-001.md` | ABSENT | None known on disk; DORA work continued in DORA-001b threads (which exist) |
| `gtkb-dashboard-industry-alignment-slice2-004.md` | `-001.md` | ABSENT | Existing slice2 thread; -001 NEW exists; -002 through -004 phantom |
| `gtkb-gov-proposal-standards-slice1-024.md` | `-021.md` | ABSENT | Thread stalled at -021 REVISED-9 GO; -022, -023, -024 phantom |

**Common pattern:** all 7 phantoms are LATEST-claim phantoms — INDEX claims VERIFIED at version N, but only versions ≤M (M < N) exist on disk and in git history. The intermediate versions M+1 through N never persisted to this checkout.

**Two existing INDEX comment annotations** already document this defect class for related threads (`gtkb-membase-effective-use-umbrella` and `gtkb-root-directory-migration-post-verify`). This proposal extends the annotation pattern to the 7 newly-confirmed phantom entries.

---

## §2. Reconciliation approach

Per existing precedent (INDEX comment blocks above the affected `Document:` entries):

```markdown
<!--
  S317 phantom-INDEX annotation: bridge/INDEX.md claims VERIFIED at -NNN
  but that file is absent from disk and from git history. Same parallel-
  poller phantom class as documented for gtkb-slice2b-metrics-index-
  reconciliation and gtkb-membase-effective-use-umbrella. Latest on-disk
  version is -MMM. Reopening the thread or restoring the phantom file is
  a separate, per-thread decision and is out of scope for this annotation
  pass.
-->
Document: gtkb-root-directory-migration
VERIFIED: bridge/gtkb-root-directory-migration-018.md   <-- PHANTOM
NEW: bridge/gtkb-root-directory-migration-017.md       <-- last on-disk
...
```

This preserves the INDEX line (audit trail) AND surfaces the defect inline so future readers don't trust the VERIFIED claim blindly.

---

## §3. Implementation plan (1 commit)

**1 commit:** `bridge: Annotate 7 phantom-VERIFIED INDEX entries (S317 reconciliation)`.

Single file edit: `bridge/INDEX.md`. 7 HTML comment blocks added, each above the affected `Document:` line.

The annotation text per entry follows the structure in §2: cites this bridge thread, names the latest on-disk version, names the missing-from-disk version, references existing reconciliation precedent.

No other files modified. No tests added (this is INDEX text annotation only; no code semantics).

---

## §4. Verification

### §4.1 Re-grep for the 7 missing files (post-annotation)

```bash
for f in gtkb-root-directory-migration-018 gtkb-app-boundary-mechanism-audit-012 gtkb-membase-effective-use-umbrella-014 gtkb-dashboard-industry-alignment-slice2a-visibility-008 gtkb-dora-telemetry-foundation-008 gtkb-dashboard-industry-alignment-slice2-004 gtkb-gov-proposal-standards-slice1-024; do
  if [ -f "bridge/${f}.md" ]; then echo "EXISTS: ${f}"; else echo "MISSING: ${f}"; fi
done
```

Expected: 7 of 7 still MISSING (annotation doesn't restore files). The annotation is the closure, not file recovery.

### §4.2 INDEX comment block presence

```bash
grep -B 1 "Document: gtkb-root-directory-migration$" bridge/INDEX.md
# Expected to show the new HTML comment block immediately preceding the Document: line.
```

Repeat for each of the 7 affected entries.

### §4.3 No other INDEX changes

```bash
git diff --name-only HEAD -- bridge/INDEX.md  # one file
git diff --stat bridge/INDEX.md                # only INDEX changed; only additions (HTML comments)
```

### §4.4 Per-commit guardrails

5/5 PASS (INDEX edit is a markdown-only change; guardrails handle markdown).

---

## §5. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Annotation text is misleading or wrong about a thread | LOW (P3) | §1 evidence is per-thread verified via direct grep + git history. Each annotation references this proposal's §1 row for traceability. |
| Future readers ignore the annotation | LOW (P3) | Annotation is inline immediately above the phantom INDEX line; hard to miss when reading INDEX. |
| Annotation triggers a tooling parser that doesn't expect HTML comments mid-INDEX | LOW (P3) | The two existing annotations have not broken any tooling; same pattern. |
| Owner prefers per-thread reopen over annotation | LOW (P3) | This proposal is annotation-only; reopens are a separate decision. If owner directs reopen, a follow-up bridge per phantom thread would handle that. |
| INDEX line count grows (current ~700 lines; 7 × ~6 lines per annotation = +42 lines) | LOW (P3) | INDEX trimming policy applies if file exceeds ~200 lines; current file already exceeds that, but annotation lines are cheap. |

---

## §6. Codex review questions

1. **Annotation only vs full reconciliation:** Should this thread also include per-thread "did the work actually ship?" investigation, or is annotation-only the right scope? Recommendation: annotation-only. Per-thread investigation is its own concern; the documented precedent is annotation-first.

2. **HTML comment text format:** Should the annotation cite this bridge thread by SHA (which doesn't exist yet pre-commit) or by file path? Recommendation: file path (`bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27-001.md`) — stable, doesn't require post-commit edits.

3. **`gtkb-root-directory-migration` ↔ `gtkb-root-directory-migration-post-verify` companion mention:** Should the annotation explicitly note the companion thread that may have done the verified-at-018 work? Recommendation: yes — guides next reader to the actual evidence.

4. **`gtkb-membase-effective-use-umbrella` already has an annotation** describing S306-S307 phantoms. Does this proposal need to extend or replace that annotation, or just add a new -014 phantom annotation alongside? Recommendation: add a new annotation specifically for the -014 phantom; existing annotation about -004..-022 still relevant.

---

## §7. Owner directive compliance

- Project root boundary: ✓ all changes within `E:\GT-KB`.
- Bridge protocol: ✓ NEW proposal awaits GO before INDEX edit.
- Explicit destructive action authorization: ✓ no deletions; INDEX is append-with-annotations.
- `feedback_scope_reduction_as_no_go_response.md`: ✓ scope explicitly narrowed to annotation; per-thread investigation deferred.
- `feedback_verify_source_before_parallel_proposals.md`: ✓ §1 inventory verified via direct file existence + git history check.

---

## §8. Expected post-implementation report contents

- `git show --stat <SHA>` showing 1 file changed (`bridge/INDEX.md`), N lines added.
- §4.1 missing-file grep output (7/7 still missing — proves no file restoration).
- §4.2 grep for new HTML comments (7 expected matches).
- Confirmation that no other INDEX entries were modified.
- Per-commit guardrails 5/5 PASS.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
