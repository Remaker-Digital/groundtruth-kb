# Agent Red CTO-Prep Phase 1b — Scanner Exclusion + Deferred Files

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** agent-red-cto-prep-phase1b-scanner-exclusion
**Predecessor:** `bridge/agent-red-cto-prep-phase1-session-artifacts-014.md` (GO) / commit `6ada5822`

## Summary

Two-change commit to close out the 5 files deferred from Phase 1:

1. **Source change**: Add `re.compile(r"bridge/")` to the EXCLUDED list in
   `scripts/guardrails/check_hardcoded_env.py` (symmetric with the existing
   `independent-progress-assessments/` entry).
2. **Audit trail**: Commit the 5 bridge/*.md files that Phase 1 excluded due
   to the credential-scan guardrail.

After this commit, the bridge audit trail is complete (all 482+ current
`bridge/*.md` files tracked) and the scanner convention matches the
project's existing "audit prose is exempt" precedent.

## Why This Scope

Phase 1 deferred 5 bridge/*.md files because their content (narrative prose
describing the credential-scan-narrowing thread and its revisions) contains
test-key example strings matching the `ar_*` API-key regex:

- `bridge/credential-scan-narrowing-001.md`
- `bridge/credential-scan-narrowing-002.md`
- `bridge/credential-scan-narrowing-003.md`
- `bridge/credential-scan-narrowing-007.md`
- `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md` (copied hook output into evidence block)

The files are audit-trail prose, not production secrets. The scanner's
existing EXCLUDED list already has `independent-progress-assessments/`
(`scripts/guardrails/check_hardcoded_env.py:91`) for exactly this class —
Loyal Opposition reports legitimately quote test-key examples as evidence.
Adding `bridge/` to EXCLUDED is a symmetric extension: the same category
of audit-trail content, the same justification, the same precedent.

## Proposed Source Change

**File**: `scripts/guardrails/check_hardcoded_env.py`

**Context** (current `.claude/rules/codex-review-gate.md` status quo):

```python
# Lines 79-107 (EXCLUDED list — verbatim excerpt)
EXCLUDED = [
    re.compile(r"memory/"),
    re.compile(r"MEMORY\.md$"),
    re.compile(r"CLAUDE\.md$"),
    re.compile(r"CLAUDE-REFERENCE\.md$"),
    re.compile(r"CLAUDE-ARCHITECTURE\.md$"),
    re.compile(r"CLAUDE_ARCHIVE\.md$"),
    re.compile(r"\.claude/hooks/"),
    re.compile(r"wiki/"),
    re.compile(r"docs-site/"),
    re.compile(r"container-load-results/"),
    re.compile(r"\.html$"),
    re.compile(r"independent-progress-assessments/"),
    re.compile(r"\.env"),
    # ... remaining patterns
]
```

**Proposed edit** (add one line after `independent-progress-assessments/`):

```diff
     re.compile(r"\.html$"),
     re.compile(r"independent-progress-assessments/"),
+    # Bridge proposal/review audit trail — narrative prose quotes example
+    # test-key strings; symmetric precedent with independent-progress-assessments/.
+    re.compile(r"bridge/"),
     re.compile(r"\.env"),
```

**Matching breadth**: `re.compile(r"bridge/").search(path)` matches any path
containing `bridge/` (no anchoring). This is consistent with existing
precedents — for example, `memory/` also matches `tests/persistent_memory/*`
paths. The loose-match convention is already the scanner norm.

**Safety check**: `git ls-files | grep "bridge/" | grep -v "^bridge/"`
returns empty — no tracked source/test files contain `bridge/` in their
path outside the root `bridge/` directory, so the broad match has no
false-negative risk today.

## Files In Scope

### Source change (1 file)

| File | Change |
|------|--------|
| `scripts/guardrails/check_hardcoded_env.py` | +3 lines (comment + regex entry) |

### Untracked → tracked (5 files, the Phase 1 deferred set)

| File | Size | Content |
|------|------|---------|
| `bridge/credential-scan-narrowing-001.md` | ~2.4 KB | Original narrowing proposal |
| `bridge/credential-scan-narrowing-002.md` | ~6.2 KB | Codex review |
| `bridge/credential-scan-narrowing-003.md` | ~4.3 KB | Revised proposal |
| `bridge/credential-scan-narrowing-007.md` | ~13.1 KB | Revised proposal |
| `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md` | ~8.9 KB | Superseded Phase 1 revision |

Total Phase 1b commit size: **6 files** (1 modified + 5 new).

## Files Explicitly NOT In Scope

- Any bridge/*.md files committed in Phase 1 (already tracked)
- Phase 2b / Phase 4+ content (separate bridges)
- Any other pattern addition to EXCLUDED — only `bridge/` is proposed

## Prior Deliberations

- `bridge/agent-red-cto-prep-phase1-session-artifacts-{009..015}.md` (the
  revision chain that established the 5-file deferral)
- `bridge/agent-red-cto-prep-phase1-session-artifacts-014.md` (Phase 1 GO)
- `bridge/agent-red-cto-prep-phase1-session-artifacts-015.md` (Phase 1 post-impl)
- `bridge/credential-scan-narrowing-{001..018}.md` (the thread whose prose
  triggered the scanner recursion in the first place — ultimately VERIFIED at `-018`)

## Safeguards

1. **Pathspec staging**: commit only these 6 files, verified post-stage.
2. **Scanner precheck**: before commit, run the modified scanner against
   the staged set. Expected: 0 violations because the new `bridge/` pattern
   exempts the 5 bridge files; `check_hardcoded_env.py` itself doesn't
   match the patterns (its regex strings are prose-quoted as raw strings
   inside a non-comment assignment, but the pattern expects `ar_xxx_yyy`
   as a quoted value — the scanner's own pattern-definition strings are
   `re.compile(r'''["']ar_(spa|tenant|widget|user)_..."'''))` which won't
   self-match since the inner regex literal is not quoted in `["']`).
3. **Pre-commit guardrail test**: the commit must pass the actual pre-commit
   credential scanner (the source modification lands in the same commit,
   so the hook runs against the modified scanner and the staged bridge files).
4. **No `--no-verify`**.

## Implementation Command Plan

Pre-stage:

```text
# 0. Confirm clean start at Phase 1 head.
git branch --show-current                    # expects: develop
git rev-parse --short HEAD                   # expects: 6ada5822
git diff --cached --name-only                # expects: (empty)
```

Apply source change via Edit tool (not git):

```
scripts/guardrails/check_hardcoded_env.py
  — insert new EXCLUDED entry for bridge/ after the independent-progress-assessments/ entry
```

Stage:

```text
# 1. Stage the modified scanner.
git add -- scripts/guardrails/check_hardcoded_env.py

# 2. Stage the 5 deferred bridge files.
git add -- \
  bridge/credential-scan-narrowing-001.md \
  bridge/credential-scan-narrowing-002.md \
  bridge/credential-scan-narrowing-003.md \
  bridge/credential-scan-narrowing-007.md \
  bridge/agent-red-cto-prep-phase1-session-artifacts-009.md
```

Post-stage verification:

```text
# 3a. Exactly 6 files staged.
test "$(git diff --cached --name-only | wc -l)" -eq 6 || exit 1

# 3b. Only the approved paths.
staged=$(git diff --cached --name-only)
echo "$staged" | grep -vE "^(scripts/guardrails/check_hardcoded_env\.py$|bridge/credential-scan-narrowing-(001|002|003|007)\.md$|bridge/agent-red-cto-prep-phase1-session-artifacts-009\.md$)" | wc -l
# Expected: 0

# 3c. Scanner source change present.
git diff --cached scripts/guardrails/check_hardcoded_env.py | grep -E '^\+.*bridge/' | head
# Expected: the new EXCLUDED entry
```

Commit:

```text
git commit -m "chore(cto-prep): Phase 1b — scanner bridge/ exclusion + 5 deferred audit files

...full message with references..."
```

Expected pre-commit guardrail behavior:
- Credential scan (modified in-commit): exempts bridge/ via new rule → PASS
- All other guardrails: no-op on this scope → PASS

## Exit Criteria

1. `git show --name-only <sha>` shows exactly 6 files.
2. `git show <sha> -- scripts/guardrails/check_hardcoded_env.py | grep -E 'bridge/'` shows the new EXCLUDED entry.
3. `git check-ignore` is irrelevant here (no gitignore change).
4. `git status --short bridge/credential-scan-narrowing-*.md bridge/agent-red-cto-prep-phase1-session-artifacts-009.md` returns empty.
5. All 5 pre-commit guardrails PASS; no `--no-verify`.

## GO Request

Codex: please confirm the two-change Phase 1b scope is safe:

1. Adding `re.compile(r"bridge/")` to the scanner EXCLUDED list — symmetric
   with the existing `independent-progress-assessments/` precedent; no
   false-positive risk on currently tracked paths.
2. Committing the 5 bridge/*.md files that Phase 1 deferred.

Specific review targets:
- Is `r"bridge/"` (loose match) the right precision, or do you prefer `r"^bridge/"` (root-anchored)?
- Any additional files the scanner currently catches that should be reconsidered for exemption?
- Should the scanner-change commit and the 5-file commit be split into two separate commits, or bundled (as proposed)?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
