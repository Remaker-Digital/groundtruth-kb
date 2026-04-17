# GT-KB Skill `/gtkb-bridge-propose` — Implementation Bridge (v001)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (currently `37a88cc` — Tier A #2 landed with `-010` fix)
**Depends on:** Tier A #4 (`gtkb-skill-decision-capture-009` REVISED, pending Codex review) for skill-scaffold infrastructure

## Purpose

Ship the `/gtkb-bridge-propose` skill as Tier A deliverable #3 per the scope
GO's six-bridge sequencing. This is the first skill in the catalog whose
*primary* contract is to write bridge files — so its pre-flight scanner
check is the behavioral anchor for the "catch credentials before the hook
has to" UX pattern referenced throughout the scope proposal.

## Dependency on Tier A #4 — Explicit Sequencing Note

The scope GO's intended order placed #3 before #4. In practice #4 was
started first and is now carrying the G2 review gate (skill scaffold +
adopter installation). This bridge is therefore drafted **additive** to
#4: it assumes `upgrade.py`'s `_MANAGED_SKILLS`, `_filter_skills_for_profile`,
`_plan_managed_skills`, and `plan_upgrade` wire-in from
`gtkb-skill-decision-capture-009` have landed before this bridge executes.

If #4 receives another NO-GO and defers, this bridge must be revised to
either (a) wait for #4, or (b) introduce the skill-scaffold infrastructure
itself. Option (a) is preferred to avoid two competing pattern
implementations. This is called out here so Codex can flag any implicit
assumption drift.

## Skill Contract

### Invocation

```
/gtkb-bridge-propose <topic-slug> [--parent <existing-doc>] [--scope <short-phrase>]
```

- `topic-slug` — kebab-case, becomes the bridge filename stem
  (`bridge/<topic-slug>-001.md`).
- `--parent` — optional. Names an existing bridge document this proposal
  supersedes or continues (e.g. `gtkb-operational-skills-tier-a`). Adds a
  **Parent:** header to the output file.
- `--scope` — optional. One-sentence scope summary embedded in the
  generated file's **Summary** section.

### Inputs (from the owner turn)

- Topic slug (required)
- Proposal body (freeform markdown, typed by the owner or drafted by the
  agent and confirmed)
- Optional parent, scope phrase
- Optional "Invariants" list (if absent, the skill auto-generates an
  empty `## Invariants` block with a TODO note for the author)

### Outputs

- `bridge/<topic-slug>-001.md` with standardized structure:
  - Frontmatter-style header: Status: NEW, Author, Date (UTC),
    Session (from environment if present), Parent, Branch, Parent SHA
  - `## Summary`, `## Rationale`, `## Invariants`, `## Test Plan`,
    `## Prior Deliberations`, `## Scanner Safety`, `## GO Request`
- `bridge/INDEX.md` updated with a NEW entry inserted at the top:
  ```
  Document: <topic-slug>
  NEW: bridge/<topic-slug>-001.md
  ```

### Ordering guarantee (file-first write)

1. **Write file first.** `bridge/<topic-slug>-001.md` is committed to disk
   before `bridge/INDEX.md` is touched. A crash between the two writes
   leaves an unindexed bridge file — visible on next scan, recoverable
   by the author — never an index entry pointing at a missing file.
2. **Idempotent rewrite detection.** If `bridge/<topic-slug>-001.md`
   already exists, the skill aborts with an explicit error and offers
   to bump to `-002` (REVISED). No silent overwrite.
3. **Index append is atomic.** The INDEX mutation is a single file
   write of the full file contents (read → modify → write), not an
   append-mode append. Matches the pattern used by existing bridge
   housekeeping.

### Auto-computed fields

- **Branch**: `git rev-parse --abbrev-ref HEAD`. If detached HEAD, emit
  `(detached)` plus the SHA.
- **Parent SHA**: `git rev-parse HEAD`. Included verbatim in the file
  header for traceability.
- **Taxonomy counts** (optional, for scope/umbrella proposals): the skill
  offers to compute current INDEX statistics (count of NEW, REVISED, GO,
  NO-GO, VERIFIED across all open entries) and insert a table. Off by
  default — enabled with `--taxonomy-counts`.
- **Session ID**: read from `$CLAUDE_SESSION_ID` if set, otherwise
  `$GIT_COMMIT_SHORT` as a weak fallback, otherwise `"unknown"`.

### Mutation contract

The skill writes:
- `bridge/<topic-slug>-001.md` — the proposal file
- `bridge/INDEX.md` — one new entry appended at the top

The skill does **NOT** write:
- KB specs, WIs, ADRs, DCLs, documents, or tests (never — that's
  `/gtkb-spec-intake`'s contract, and even there it's confirmation-gated)
- Git commits, stashes, or any non-bridge files
- Any file under `.claude/` or `src/`

## Pre-Flight Scanner Check

The skill runs the canonical credential scanner against the proposal body
**before writing to disk**. This is the behavioral anchor that gives the
skill its name — the scanner-safe-writer hook will catch the same
violations at Write time, but by then the owner has already typed the
offending content and has to redo it. The pre-flight check catches it one
step earlier.

### Catalog source

```python
from groundtruth_kb.governance.credential_patterns import (
    CREDENTIAL_PATTERNS,
    BASH_EXTRAS,
    scan,
)
```

PII patterns are **excluded** from the pre-flight check, matching
`scanner-safe-writer.py`'s hook-level scope (policy: credential-class only,
redacted PII samples are allowed in bridge prose).

### Behavior on match

1. Print the list of hits (pattern_name, line number, column range, first
   20 chars of matched text with surrounding context redacted).
2. Do **not** write the file.
3. Offer two owner options:
   - **Redact**: the skill runs `credential_patterns.redact()` over the
     body and offers the redacted form for confirmation.
   - **Abort**: no file written, no INDEX change, skill exits with a
     non-zero status and a short message.

### Behavior on no match

The skill proceeds silently to the file-first write sequence.

### Catalog import failure handling

If `groundtruth_kb.governance.credential_patterns` cannot be imported
(e.g., adopter environment does not have the wheel installed), the skill
refuses to run and prints a one-line remediation: `"canonical scanner
unavailable — run gt project doctor"`. Unlike the hook, the skill does
**not** fall back to an inline catalog. The rationale: skill users are
Claude Code sessions that have the GT-KB wheel present by contract. A
falling-back skill would give the illusion of safety without the canonical
guarantee. A refusing skill forces the adopter to fix the install.

## Scaffold / Upgrade / Doctor Integration (Additive to #4)

### Scaffold copy

`src/groundtruth_kb/project/scaffold.py` — extend `_copy_skill_templates()`
(introduced by #4) to copy the `bridge-propose/` subtree when the profile
includes bridge support. One-line addition to the skill list, or the
helper iterates `templates/skills/*/` automatically — to be confirmed
against the #4 implementation.

### Upgrade tracking

`src/groundtruth_kb/project/upgrade.py` — append to the `_MANAGED_SKILLS`
list (introduced by #4):

```python
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
    ".claude/skills/bridge-propose/SKILL.md",            # NEW
    ".claude/skills/bridge-propose/helpers/write_bridge.py",  # NEW (if helper created)
]
```

No other `upgrade.py` changes are required: the `_filter_skills_for_profile`,
`_plan_missing_managed_files`, and `_plan_managed_skills` helpers from #4
iterate this list automatically.

### Doctor check

`src/groundtruth_kb/project/doctor.py` — extend the skill check
introduced by #4 to cover `bridge-propose/` as well. The per-skill check
pattern from #4 (keyword `ToolCheck` construction, `status="warning"` for
missing file, remediation pointing to `gt project upgrade --apply`) is
reused.

### Non-disruptive upgrade

Because #4 wires skills into `_plan_missing_managed_files` unconditionally,
same-version adopters missing `.claude/skills/bridge-propose/` will
receive an `add` action on their next `gt project upgrade --apply`. No
version bump required by this bridge.

## File List

### New files

- `templates/skills/bridge-propose/SKILL.md` (~80 lines — the skill
  contract, invocation, and owner-facing docs)
- `templates/skills/bridge-propose/helpers/write_bridge.py` (~150 lines —
  the Python helper the skill invokes: scanner check, file write, INDEX
  update, git-rev-parse)
- `tests/test_bridge_propose_helper.py` (~8 tests — pre-flight matches,
  file-first ordering, idempotent rewrite detection, git-rev-parse
  success + detached HEAD, catalog-import-failure abort, redact-offer
  path, taxonomy-count computation, INDEX insertion shape)
- `tests/test_scaffold_skills_bridge_propose.py` (~2 tests — adopter
  receives `bridge-propose/` files after `gt project init`; missing-file
  repair restores them)
- `tests/test_upgrade_skills_bridge_propose.py` (~2 tests — append to
  `_MANAGED_SKILLS` reflected in plan; same-version missing → `add`
  action)
- `tests/test_doctor_skills_bridge_propose.py` (~2 tests — present + OK,
  missing + warning with correct remediation text)

### Modified files

- `src/groundtruth_kb/project/upgrade.py` — append 2 entries to
  `_MANAGED_SKILLS` (single change; no other edits)
- `src/groundtruth_kb/project/doctor.py` — extend skill check to include
  `bridge-propose` (pattern identical to #4's decision-capture check)

### NOT modified

- `pyproject.toml` — templates tree already force-included (per #2)
- `scaffold.py` — #4's `_copy_skill_templates` handles the copy via the
  `_MANAGED_SKILLS` list (verify in post-impl)

### Expected deltas

- Code: ~230 new lines source (SKILL.md + helper) + ~250 new lines tests
- Tests: +16 (8 helper + 2 scaffold + 2 upgrade + 2 doctor + 2 integration)
- Full suite: ~1134 (post-#4) → ~1150

## Test Plan — Detail

### Helper unit tests (`tests/test_bridge_propose_helper.py`)

1. **`test_preflight_detects_ar_live_key`** — body containing an
   `ar_live_*` string → helper returns deny dict with `pattern_name` =
   `ar_live_key`; no file written.
2. **`test_preflight_allows_descriptive_prose`** — body with phrases like
   "AR-family live keys are redacted" → helper returns allow.
3. **`test_file_first_write_order`** — mock disk; assert
   `bridge/<slug>-001.md` write happens before `bridge/INDEX.md` write.
4. **`test_idempotent_rewrite_refused`** — `bridge/foo-001.md` already
   exists → helper aborts with explicit error; no INDEX change.
5. **`test_git_rev_parse_detached_head`** — simulated detached HEAD →
   emits `(detached) <sha>` in header; does not raise.
6. **`test_canonical_import_failure_refuses`** — monkeypatch
   `ImportError` on `credential_patterns` import → helper exits non-zero
   with remediation message; no file written.
7. **`test_redact_offer_path`** — match present + owner chooses redact →
   helper calls `credential_patterns.redact()` and presents redacted form.
8. **`test_taxonomy_counts_computed`** — synthetic INDEX.md with known
   counts → `--taxonomy-counts` emits expected table.

### Scaffold + upgrade integration tests

9. **`test_scaffold_installs_bridge_propose_skill`** — `gt project init
   --profile dual-agent` → `.claude/skills/bridge-propose/SKILL.md` +
   `helpers/write_bridge.py` present with non-empty content.
10. **`test_plan_upgrade_adds_missing_bridge_propose_at_same_version`**
    — adopter at current scaffold version missing the skill → `add`
    action emitted.
11. **`test_base_profile_no_bridge_propose`** — `local-only` profile:
    skill files neither `add` nor `skip` (consistent with #4).

### Doctor tests

12. **`test_doctor_bridge_propose_present`** — `status` = `ok`,
    `required=False`.
13. **`test_doctor_bridge_propose_missing_warning`** — `status` =
    `warning`, `message` contains `gt project upgrade --apply`.

### Cross-skill parity tests

14. **`test_managed_skills_list_includes_both_skills`** — assert
    `_MANAGED_SKILLS` contains both `decision-capture` and
    `bridge-propose` paths.
15. **`test_map_managed_to_template_preserves_nesting`** — reuse of
    `_map_managed_to_template` from #4; parametric test with both
    skill prefixes.

## Response to Scope GO Conditions (G1–G5)

- **G1 (source-derived patterns)** — N/A here; canonical module from #1
  is the source. Pre-flight imports from the module, never enumerates.
- **G2 (skill scaffold + adopter installation)** — #4 establishes the
  pattern. This bridge is additive: two new skill-file paths appended to
  the `_MANAGED_SKILLS` list #4 introduces. Scaffold, upgrade, and
  doctor coverage all inherit from #4. Two dedicated integration tests
  (`test_scaffold_installs_bridge_propose_skill`,
  `test_plan_upgrade_adds_missing_bridge_propose_at_same_version`) prove
  the adopter path.
- **G3 (six-bridge authorization)** — honored: this is bridge #3 of six,
  consistent with the sequencing table in `-004` GO Condition 3.
- **G4 (deliberation outcome)** — N/A here; this skill does not write
  deliberations. (`/gtkb-spec-intake` carries that concern — bridge #5.)
- **G5 (deny-record schema)** — the skill's pre-flight is advisory, not
  the authoritative deny gate. It does **not** write deny records; the
  scanner-safe-writer hook does (schema v1 defined by #2). The skill and
  hook share the catalog via
  `groundtruth_kb.governance.credential_patterns`; schema divergence is
  therefore impossible by construction.

## Prior Deliberations

No prior deliberations found for `/gtkb-bridge-propose` beyond this bridge
thread. Verification:

```text
python -m groundtruth_kb deliberations search \
    "bridge propose skill preflight scanner file first write order"
```

Related threads already archived:

- `bridge/gtkb-operational-skills-tier-a-004.md` — parent scope GO
- `bridge/gtkb-credential-patterns-canonical-010.md` — canonical catalog
  VERIFIED (Tier A #1)
- `bridge/gtkb-hook-scanner-safe-writer-012.md` — scanner-safe-writer
  hook + deny schema v1 VERIFIED (Tier A #2)
- `bridge/gtkb-skill-decision-capture-009.md` — skill-scaffold
  infrastructure REVISED, awaiting Codex review (Tier A #4)
- `.claude/rules/bridge-essential.md` — bridge visibility mandate
- `.claude/rules/file-bridge-protocol.md` — file naming + INDEX convention
  this skill encodes

## Exit Criteria

1. `templates/skills/bridge-propose/SKILL.md` + `helpers/write_bridge.py`
   land in `groundtruth-kb` main with content matching this spec.
2. `_MANAGED_SKILLS` in `upgrade.py` includes both new paths; no other
   `upgrade.py` changes.
3. Doctor covers the new skill via the #4 pattern; missing-file message
   points to `gt project upgrade --apply`.
4. 16 new tests pass; full suite clean; ruff + mypy --strict clean on
   full repo.
5. Scanner-safe-writer hook raises deny on a fixture body containing a
   canonical pattern when invoked with target `bridge/foo.md` —
   interchangeability with the skill's pre-flight is empirically
   demonstrated.
6. `gt project upgrade --apply` on a same-version adopter missing the
   skill adds both files; adopter can invoke `/gtkb-bridge-propose`
   successfully on a trivial body.
7. No version bump required by this bridge (skills land via unconditional
   missing-file repair per #4's semantics).

## Scanner Safety — This Proposal

Pre-flight scan of this file:

```text
python -c "
import re
from pathlib import Path
pat = re.compile(r'[\"\\\']ar_(spa|tenant|widget|user|live)_[A-Za-z0-9_]{16,}[\"\\\']')
c = Path('bridge/gtkb-skill-bridge-propose-001.md').read_text()
print('hits:', len(pat.findall(c)))
"
```

Expected: `hits: 0`.

Authoring pattern: credential families referenced descriptively
("AR-family live keys", "canonical pattern") rather than by literal
example strings. Regex snippets shown are Python import lines or
pattern-name references only, never live keys.

## GO Request

Codex: please review with particular attention to:

1. **Sequencing note**: is drafting #3 additive to #4 acceptable, or
   should we wait for #4 VERIFIED before even opening this bridge?
2. **Catalog refusal vs fallback**: the skill refuses when the canonical
   import fails, unlike the hook which falls back. Is that the right
   trade-off? (Argument: skill caller always has wheel installed by
   contract; falling back would hide install drift.)
3. **File-first write order**: explicit unit test covers this. Sufficient
   to rely on Python's sequential write order, or should there be a
   fsync between the two writes?
4. **Idempotent rewrite detection**: aborting on existing `-001.md` is
   conservative; should the skill instead auto-bump to `-002` (REVISED)?
   Current design errs toward explicitness (owner makes the decision).
5. **Taxonomy counts default off**: defensible for routine proposals;
   for scope/umbrella proposals they are useful. Comfortable with
   `--taxonomy-counts` as opt-in?

If GO: single GT-KB commit. ~230 net source insertions + ~250 test
insertions across ~8 files. Full suite + ruff + mypy --strict clean.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
