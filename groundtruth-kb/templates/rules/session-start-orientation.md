# Session Start: ORIENT Block (Mandatory)

Load this rule at session start alongside `CLAUDE.md` / `AGENTS.md`.

## Purpose

Produce a **7-item ORIENT block** once per session after memory read and bridge scan, before first substantive work. ORIENT mirrors the retired POLLER block discipline: fixed header, numbered lines, live sources only.

## Output format (verbatim)

```
ORIENT S{N} @ HH:MMZ
  1 bridge:     <status>                                  # TAFE/dispatcher + versioned bridge scan
  2 branch:     <repo>@<sha-short>  (<ahead/behind N>)    # git rev-parse + git status -sb
  3 worktree:   <N modified, M untracked>  [relevant: <scoped subset>]
  4 wrap:       DELIB-<id> / INSIGHTS-<date>-<topic>.md   # DA search + LO dropbox latest
  5 blockers:   <list or 'none'>                          # active NO-GO + GO-unverified + release-blocking
  6 refresh:    <list or 'none'>                          # evidence that must be refreshed
  7 next:       <action>                                  # synthesis of 1-6
```

**Count is exactly 7.** Skipped or miscounted items are visible in grep and doctor checks.

## Live-source requirement

Every answer must come from a live command or read in the **current** session's first turn. Acceptable sources include `git`, bridge scan helpers, Deliberation Archive search, `gh run list`, and governed project CLI output.

When a live source cannot be obtained, use a structured unknown tag:

```
UNKNOWN:<category>
```

Allowed categories (extend only via governed bridge change):

| Category | When to use |
|----------|-------------|
| `no-remote-access` | Network or remote API unavailable |
| `first-session` | No prior artifacts exist yet |
| `transcript-unavailable` | Prior transcript path unavailable |
| `permission-denied` | Filesystem or harness permission blocked read |
| `source-missing` | Expected artifact absent on disk |
| `harness-unavailable` | Harness-specific tool unavailable |
| `ci-unavailable` | CI status cannot be queried |
| `dashboard-unavailable` | Dashboard or Grafana unreachable |

Bare `UNKNOWN` without a category is **invalid**.

## Session wrap

End Prime Builder sessions with a well-formed ORIENT block in the final owner-visible turn so the next session's `gt project doctor` check can validate prior-session orientation evidence.

## Extended baseline audit

When the owner uses a documented trigger phrase, run `/baseline-audit` (`.claude/skills/baseline-audit/SKILL.md`). Prime Builder **and** Loyal Opposition may execute that skill for independent verification.

Trigger phrases (case-insensitive substring match):

- `baseline status`
- `release readiness`
- `production readiness`
- `project handoff`
- `baseline audit`
- `where do we stand`
- `full status`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
