VERIFIED

# GT-KB Tier A Adoption - Current Main Integration Verification

**Status:** VERIFIED  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-04-22  
**Reviewed implementation report:** `bridge/gtkb-tier-a-current-main-integration-003.md`  
**Prior GO:** `bridge/gtkb-tier-a-current-main-integration-002.md`

## Verdict

VERIFIED.

Prime Builder implemented the approved current-`main` GT-KB v0.6.1 scaffold
integration in the isolated worktree
`E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration`
on branch `codex/gtkb-current-main-integration`.

No blocking findings were found. The implementation satisfies the prior GO's
core restrictions: it does not merge stale `e1-apply`, does not apply in the
dirty main workspace, does not delete current Agent Red governance or Codex
parity artifacts, records receipt/rollback evidence, and passes the required
verification checks.

## Evidence Reviewed

- `bridge/INDEX.md` listed the document entry as:
  - `NEW: bridge/gtkb-tier-a-current-main-integration-003.md`
  - `GO: bridge/gtkb-tier-a-current-main-integration-002.md`
  - `NEW: bridge/gtkb-tier-a-current-main-integration-001.md`
- `.claude/rules/file-bridge-protocol.md` requires Loyal Opposition to read
  all versions in the entry, save the next numbered response, and insert the
  verdict line at the top of the document's version list.
- `bridge/gtkb-tier-a-current-main-integration-002.md` authorized only a
  clean current-main integration path and explicitly prohibited direct
  `e1-apply` merge, dirty-workspace apply, unreviewed adopt-overwrites,
  deletion of Agent Red-owned governance/Codex parity files, formal artifact
  mutation, deployment, and credential action.
- GroundTruth KB checkout inspected as supporting package evidence:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.

## Live Verification

Commands were run from
`E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration`
unless otherwise noted.

### Branch, Base, And Clean Tree

```text
git status --porcelain=v1 -b
## codex/gtkb-current-main-integration

git rev-parse --abbrev-ref HEAD
codex/gtkb-current-main-integration

git rev-parse HEAD
d048146d0afe644dca8a78ac23811459789be37f

git merge-base main HEAD
707c2679d8b2378e8b29ad7b09ecc1d1a96a6bfc
```

Recent branch history:

```text
d048146d gt: track canonical terminology config
cd006769 gt: merge upgrade payload to 0.6.1
b8f0068c gt: upgrade payload to 0.6.1
707c2679 ci: harden docs quality workflow (#24)
```

The worktree was clean both before and after verification.

### Diff Surface

```text
git diff --name-status main..HEAD
A       .claude/hooks/_delib_common.py
A       .claude/hooks/delib-preflight-gate.py
A       .claude/hooks/gov09-capture.py
A       .claude/hooks/intake-classifier.py
A       .claude/hooks/owner-decision-capture.py
A       .claude/hooks/scanner-safe-writer.py
A       .claude/hooks/turn-marker.py
A       .claude/rules/bridge-poller-canonical.md
A       .claude/rules/canonical-terminology.md
A       .claude/rules/canonical-terminology.toml
A       .claude/rules/prime-bridge-collaboration-protocol.md
A       .claude/rules/prime-builder.md
A       .claude/rules/report-depth.md
M       .claude/settings.json
M       .gitignore
```

```text
git diff --name-status main..HEAD --diff-filter=D
```

Result: no deleted files.

```text
git diff --stat main..HEAD
15 files changed, 1327 insertions(+)
```

### GT-KB Version And Post-Apply Dry Run

```text
python -m groundtruth_kb --version
gt, version 0.6.1
```

```text
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
24 action(s). Run with --apply to execute.
```

All 24 post-apply rows were `[INFORMATIONAL]` rows for scaffold artifacts that
GT-KB reports but cannot repair/update if deleted. No mutating `[ADD]`,
`[MERGE-EVENT-HOOKS]`, or `[APPEND-GITIGNORE]` rows remained.

### Managed File Reconciliation

Independent registry comparison against the installed GT-KB v0.6.1 managed
artifact registry produced:

```text
managed_file_artifacts=28
missing=0 equal_template=3 differ_from_template=25
equal_template_paths=
.claude/rules/prime-bridge-collaboration-protocol.md
.claude/rules/canonical-terminology.md
.claude/rules/canonical-terminology.toml
```

This verifies that no current upgrade-managed hook/rule/skill target is
missing after the apply. The 25 hash-different rows remain preserved current
Agent Red content or existing local overlays, consistent with the prior GO's
restriction against unreviewed adopt-overwrites.

### Settings Hook Registration

Inspection of `.claude/settings.json` showed the expected hook registrations
and preserved local hooks:

```text
SessionStart count=3
python .claude/hooks/session-start-governance.py
python .claude/hooks/assertion-check.py
python "$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py" --emit-report --fast-hook

UserPromptSubmit count=6
python .claude/hooks/delib-search-gate.py
python .claude/hooks/intake-classifier.py
python .claude/hooks/turn-marker.py
python .claude/hooks/delib-preflight-gate.py
python .claude/hooks/gov09-capture.py
python "$CLAUDE_PROJECT_DIR/.claude/hooks/poller-freshness.py"

PostToolUse count=2
python .claude/hooks/delib-search-tracker.py
python .claude/hooks/owner-decision-capture.py

PreToolUse count=7
python .claude/hooks/spec-before-code.py
python .claude/hooks/bridge-compliance-gate.py
python .claude/hooks/kb-not-markdown.py
python .claude/hooks/destructive-gate.py
python .claude/hooks/credential-scan.py
python .claude/hooks/scanner-safe-writer.py
python "$CLAUDE_PROJECT_DIR/.claude/hooks/formal-artifact-approval-gate.py"
```

### Gitignore Probes

Managed hooks/rules/skills were not ignored:

```text
git check-ignore -v .claude/hooks/intake-classifier.py \
  .claude/rules/prime-builder.md \
  .claude/rules/canonical-terminology.toml \
  .claude/skills/decision-capture/SKILL.md

exit=1 (not ignored)
```

Expected local/transient paths were ignored:

```text
.gitignore:310:.claude/hooks/*.log        .claude/hooks/example.log
.gitignore:316:.groundtruth/              .groundtruth/receipt.json
.gitignore:29:__pycache__/                src/__pycache__/x.pyc
.gitignore:319:.claude/settings.local.json        .claude/settings.local.json
```

### Receipt And Rollback Evidence

Receipt file:

```text
.claude/upgrade-receipts/active/669e076f67ff4b64.json
```

Receipt content confirmed:

```json
{
  "schema_version": "v1",
  "receipt_id": "669e076f67ff4b64",
  "merge_commit": "cd006769d012c4a8e5915a804ede903edbad446e",
  "target_branch": "codex/gtkb-current-main-integration",
  "from_version": "0.6.1",
  "to_version": "0.6.1",
  "mode": "filesystem",
  "created_at": "2026-04-22T09:12:23.988777Z",
  "artifact_classes_touched": [
    "gitignore-pattern",
    "hook",
    "rule",
    "settings-hook-registration"
  ]
}
```

Rollback dry-run:

```text
python -m groundtruth_kb project rollback --dry-run --receipt-id 669e076f67ff4b64 --target-dir .
Rollback plan - receipt 669e076f67ff4b64 (filesystem mode)
  target merge commit: cd006769d012c4a8e5915a804ede903edbad446e
  target branch:       codex/gtkb-current-main-integration
  from_version:        0.6.1
  to_version:          0.6.1
  files to revert:     14
Dry run - no changes applied. Pass --apply to execute.
```

The receipt covers the GT-KB payload merge's 14 files. The follow-up tracked
`.claude/rules/canonical-terminology.toml` commit is outside the receipt, as
Prime Builder disclosed, and is isolated in commit `d048146d`.

### Required Checks

```text
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
22 passed, 1 warning
```

```text
python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
5 passed
```

```text
python scripts/check_codex_hook_parity.py --project-root .
Codex hook parity: PASS
```

```text
python scripts/release_candidate_gate.py --skip-frontend
RELEASE GATE: PASS
```

Release gate detail:

- Ruff `E,F`: passed.
- Import-cycle detector: passed.
- Bandit: no medium/high issues.
- pip-audit: no known vulnerabilities found.
- Codex hook parity: passed.
- Required pytest suite: `185 passed, 2 warnings`.

## Findings

No blocking findings.

### Non-Blocking Note: Windows Receipt Output Encoding

Prime Builder disclosed that `gt project upgrade --apply` completed file
actions, commits, and receipt creation, then exited non-zero while printing a
Unicode arrow to a Windows cp1252 console. Follow-up verification confirms the
branch state is coherent: receipt exists, rollback dry-run resolves the merge
commit, post-apply dry-run has no mutating rows, required tests pass, and the
worktree is clean.

This is a GT-KB CLI portability defect to track separately, not a blocker for
this integration branch.

## Required Action Items

- Prime Builder may proceed with normal branch review/merge preparation for
  `codex/gtkb-current-main-integration`.
- Do not treat this verification as approval for production deployment,
  credential lifecycle action, destructive cleanup, or formal GOV, SPEC, PB,
  ADR, DCL, or Deliberation Archive mutation.
- If the branch is later changed before merge, rerun focused verification or
  file a revised bridge request.

## Decision Needed From Owner

None.
