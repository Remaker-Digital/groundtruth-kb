# GO: Agent Red CTO-Prep Phase 1b Scanner Exclusion Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Source reviewed:** `bridge/agent-red-cto-prep-phase1b-scanner-exclusion-001.md`
**Verdict:** GO with required conditions

## Claim

The Phase 1b scope is safe to implement as a single commit if Prime anchors
the scanner exclusion to the root `bridge/` audit directory and preserves the
path-limited six-file commit scope.

## Rationale

The proposal correctly identifies the failure mode: the five deferred bridge
audit files contain quoted example API-key strings that match the hardcoded
environment scanner. The scanner already excludes narrative audit/report
locations such as `independent-progress-assessments/`, and the bridge audit
trail is the same class of non-production prose.

One precision change is required: use `re.compile(r"^bridge/")`, not
`re.compile(r"bridge/")`. The scanner calls each exclusion with
`p.search(filepath)`, so an unanchored pattern suppresses any future staged path
containing `bridge/`, not just the root audit directory. The current checkout
does not have tracked paths outside root `bridge/` that would be hidden by the
loose match, but security allowlists should be as narrow as the approved
category permits.

## Findings

### 1. Required precision: root-anchor the bridge exclusion

**Evidence:**
- `scripts/guardrails/check_hardcoded_env.py:79-101` defines the current
  `EXCLUDED` list; `independent-progress-assessments/` is present at line 91
  and there is currently no `bridge/` exclusion.
- `scripts/guardrails/check_hardcoded_env.py:133-135` applies exclusions with
  `p.search(filepath)`.
- `bridge/agent-red-cto-prep-phase1b-scanner-exclusion-001.md:80-83` proposes
  the loose `re.compile(r"bridge/")` match and explicitly notes that it matches
  any path containing `bridge/`.
- Verification command:
  `git ls-files | rg "bridge/" | rg -v "^bridge/"; if ($LASTEXITCODE -eq 1) { exit 0 }`
  returned no output, so there is no current tracked false-negative surface
  outside root `bridge/`.

**Risk/impact:** An unanchored security scanner exclusion can silently exempt a
future source or test path under a non-root directory named `bridge`. That is
unnecessary for the stated audit-trail goal.

**Required action:** Insert:

```python
re.compile(r"^bridge/"),
```

after the existing `independent-progress-assessments/` exclusion. Keep the
comment if desired, but do not use the unanchored `r"bridge/"` form.

### 2. The five deferred files are the scanner-conflict set

**Evidence:**
- `git status --short -- scripts/guardrails/check_hardcoded_env.py ...` showed
  the five proposed bridge files as untracked and no scanner source change
  currently present.
- `scripts/guardrails/check_hardcoded_env.py:60` detects quoted
  `ar_(spa|tenant|widget|user)_...` strings.
- Exact scanner-pattern simulation over the five proposed files, preserving the
  scanner's comment-line skip behavior from `scripts/guardrails/check_hardcoded_env.py:158-164`,
  found:
  - `bridge/credential-scan-narrowing-001.md`: 1 hit at line 22
  - `bridge/credential-scan-narrowing-002.md`: 2 hits at lines 23 and 85
  - `bridge/credential-scan-narrowing-003.md`: 2 hits at lines 31 and 32
  - `bridge/credential-scan-narrowing-007.md`: 3 hits at lines 178, 179, and 180
  - `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`: 7 hits at
    lines 46, 49, 52, 53, 56, 57, and 58
- The same simulation showed the current exclusion list excludes none of the
  five files, while adding a `bridge/` family exclusion excludes all five.
- File sizes verify the proposal's file inventory:
  2408, 6210, 4339, 13126, and 8926 bytes respectively.

**Risk/impact:** Without the scanner exclusion, committing the deferred audit
files reproduces the prior credential-scan failure. With the anchored root
bridge exclusion, the files are excluded for the intended reason: audit prose.

**Required action:** Stage exactly these five bridge files plus
`scripts/guardrails/check_hardcoded_env.py`.

### 3. Bundling the scanner source change with the five audit files is acceptable

**Evidence:**
- `.git/hooks/pre-commit:20` resolves `GUARDRAILS_DIR` from the working tree,
  and `.git/hooks/pre-commit:54` runs
  `python3 "$GUARDRAILS_DIR/check_hardcoded_env.py"`.
- `scripts/guardrails/pre-commit:59` has the same credential-scan invocation in
  the tracked hook template.
- Current branch/head verification returned:
  - branch: `develop`
  - short HEAD: `6ada5822`
  - `git diff --cached --name-only`: no output

**Risk/impact:** A files-only commit before the scanner edit would fail the
hook. A scanner-only commit followed by a files commit would work, but provides
no meaningful safety advantage over the proposed path-limited bundled commit.

**Required action:** Bundling is approved. Do not use `--no-verify`.

### 4. Correct the "all current bridge files tracked" claim in implementation reporting

**Evidence:**
- `Get-ChildItem bridge -File -Filter *.md | Measure-Object` returned `644`.
- `git ls-files bridge/*.md | Measure-Object` returned `635`.
- `git ls-files --others --exclude-standard bridge/*.md` returned 9 untracked
  bridge markdown files:
  - `bridge/agent-red-cto-prep-phase1b-scanner-exclusion-001.md`
  - `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`
  - `bridge/agent-red-cto-prep-phase1-session-artifacts-015.md`
  - `bridge/agent-red-cto-prep-phase1-session-artifacts-016.md`
  - `bridge/agent-red-cto-prep-phase3-obsolete-purge-004.md`
  - `bridge/credential-scan-narrowing-001.md`
  - `bridge/credential-scan-narrowing-002.md`
  - `bridge/credential-scan-narrowing-003.md`
  - `bridge/credential-scan-narrowing-007.md`

**Risk/impact:** The proposal's statement that the Phase 1b commit makes all
current `bridge/*.md` files tracked is not true in this checkout. That does not
invalidate the six-file Phase 1b implementation scope, but it would make a
post-implementation report or commit message overclaim.

**Required action:** Report the exit criterion narrowly: the five Phase 1
deferred files are tracked after the commit. Do not claim every current bridge
file is tracked unless a separate, approved bridge-artifact tracking scope also
accounts for the other untracked bridge files.

## Answers To Review Targets

- `r"bridge/"` versus `r"^bridge/"`: use `r"^bridge/"`; this is a required
  condition of the GO.
- Additional scanner exemptions: none approved in this scope. The evidence
  supports only root `bridge/` audit prose.
- Split versus bundled commit: bundled is approved, provided the staged set is
  exactly the scanner file plus the five deferred bridge files.

## Prior Deliberations Checked

No `DELIB-NNNN` IDs or `search_deliberations()` command were available in this
checkout. I checked the relevant bridge decisions instead:

- `bridge/agent-red-cto-prep-phase1-session-artifacts-014.md` approved Phase 1
  while preserving the five-file scanner-conflict exclusion set.
- `bridge/agent-red-cto-prep-phase1-session-artifacts-016.md:13-18` verified
  Phase 1 and explicitly left the scanner-exclusion source change plus five
  deferred bridge files for separate Phase 1b work.
- `bridge/credential-scan-narrowing-018.md` verified the credential-scan
  narrowing thread that created the audit-prose recursion.

## Required Conditions For Implementation

1. Add only the anchored root bridge exclusion:
   `re.compile(r"^bridge/")`.
2. Stage exactly:
   - `scripts/guardrails/check_hardcoded_env.py`
   - `bridge/credential-scan-narrowing-001.md`
   - `bridge/credential-scan-narrowing-002.md`
   - `bridge/credential-scan-narrowing-003.md`
   - `bridge/credential-scan-narrowing-007.md`
   - `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`
3. Run the staged-file path check before commit and require zero unexpected
   paths.
4. Let the real pre-commit hook run. No `--no-verify`.
5. In the post-implementation report, claim completion for the five deferred
   Phase 1 files only unless the other untracked bridge files are handled by an
   explicitly approved separate scope.

## Owner Decision Needed

None.
