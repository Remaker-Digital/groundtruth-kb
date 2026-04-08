# Session Initialization: CI Lint Remediation

Copy everything below the line into a new Claude Code session.

---

Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Branch: develop

## Task: Fix all CI lint failures (ruff E/F rules)

The CI lint workflow (`Lint` on GitHub Actions) is failing on both `main` and `develop` due to 1,446 ruff lint errors across `src/` and `tests/`. These were previously hidden by a `--statistics` flag crash that was fixed in the previous session. Now the real lint errors are visible and blocking CI.

### Error Breakdown by Rule

| Rule | Count | Description | Fix Strategy |
|------|-------|-------------|-------------|
| F401 | 1,020 | Unused imports | `ruff check --fix --select F401` (auto-fixable) |
| F841 | 170 | Unused local variables | `ruff check --fix --select F841` (auto-fixable) |
| E501 | 139 | Line too long (>120 chars) | Manual line wrapping or `ruff format` |
| F811 | 34 | Redefined unused name | Manual review — may indicate real bugs |
| E741 | 23 | Ambiguous variable name (l, O, I) | Rename variables |
| E402 | 23 | Module-level import not at top | Move imports or add `# noqa: E402` if intentional |
| F541 | 20 | f-string without placeholders | Remove f-prefix |
| F821 | 14 | Undefined name | Manual review — these may be real bugs |
| E702 | 1 | Multiple statements on one line | Split line |

### Error Distribution by Directory

| Directory | Count | Priority |
|-----------|-------|----------|
| tests/multi_tenant | 493 | High (largest) |
| src/multi_tenant | 220 | High (production code) |
| tests/unit | 76 | Medium |
| tests/security | 62 | Medium |
| tests/integrations | 41 | Medium |
| src/integrations | 31 | Medium |
| src/multi_tenant/superadmin_api | 29 | Medium |
| src/chat | 23 | Medium |
| src/app | 19 | Medium |
| (remaining dirs) | ~452 | Lower |

### Approach

1. **Phase 1 — Auto-fix (F401 + F841 + F541):** Run `ruff check --fix --select F401,F841,F541 src/ tests/` to auto-fix 1,210 of 1,446 errors (~84%). Verify no test breakage with `python -m pytest tests/unit/ -x -q --timeout=30`.

2. **Phase 2 — E501 line length:** Run `ruff format src/ tests/` to auto-format. Review any remaining E501 manually.

3. **Phase 3 — Manual fixes (F811, E741, E402, F821, E702):** Review each manually. F821 (undefined name) may indicate real bugs — investigate carefully. E402 (import order) may be intentional for conditional imports — add `# noqa: E402` where appropriate.

4. **Phase 4 — Verify:** Run `ruff check src/ tests/ --select E,F` locally. Confirm zero errors. Commit, push, verify CI passes on develop.

5. **Phase 5 — Merge to main:** Merge the lint fix to `main` so both branches have green CI.

### Constraints

- Do NOT modify behavior — only remove unused code, fix formatting, and rename ambiguous variables.
- F821 (undefined name) errors need careful review — they may indicate code that was partially refactored.
- Do NOT add `# noqa` comments except for E402 where the import order is intentional (e.g., path setup before imports).
- Run unit tests after each phase to catch regressions.
- Codex (Loyal Opposition) is offline this session — skip bridge checks.

### Commit Convention

```
fix: resolve 1,446 ruff lint errors (F401/F841/E501/F811/E741/E402/F541/F821)
```

### Success Criteria

- `ruff check src/ tests/ --select E,F` returns 0 errors
- `Lint` GitHub Actions workflow passes on both `develop` and `main`
- All unit tests pass
- No behavioral changes
