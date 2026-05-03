# existing-adopter-migration

A **pre-isolation adopter shape** plus a documented upgrade walkthrough that
ends in a clean post-migration state. This example exists for adopters who
predate the GTKB-ISOLATION-017 contract and need a reference for what the
migration looks like end-to-end.

The tree shape in this example deliberately FAILS several `isolation:*`
doctor checks — that's the starting state. Run [WALKTHROUGH.md](WALKTHROUGH.md)
to see the migration in action.

## What this example demonstrates

| Surface | Pre-isolation state | Post-migration state |
|---|---|---|
| `[service].endpoint` | `groundtruth.db` (raw DB path) | `configure-me://placeholder/v1` |
| `.claude/hooks/.workstream-focus-state.json` | `current_subject=platform` | `current_subject=application` (file rewritten) |
| `.claude/hooks/workstream-focus.py` | Present (legacy hook) | Removed by auto-fixer |
| `memory/release-readiness.md` | "Platform release readiness" header | Application-subject header |

The migration runs once; afterwards the adopter is isolation-compliant and
no longer triggers the auto-fixable subset of `isolation:*` checks.

## Dashboard rendering

The dashboard rendering walkthrough is meaningful **after** the migration
completes. Before the migration, the dashboard would show every isolation
surface in a non-clean state. After the migration:

```bash
gt dashboard render --adopter-root ~/projects/legacy-app/
```

surfaces:

- **Service health** from `[service].endpoint` — placeholder after the
  auto-fixer rewrites the raw-DB endpoint.
- **Overlay state** from `.groundtruth-chroma/` — empty until first
  index build (no orphan cache).

Both surfaces appear in the same render. See [WALKTHROUGH.md](WALKTHROUGH.md)
for the full migration sequence that produces this clean post-migration state.

## See also

- [WALKTHROUGH.md](WALKTHROUGH.md) — step-by-step upgrade walkthrough.
- [Application/Platform Isolation](../../docs/architecture/isolation.md)
- [cli.md](../../docs/reference/cli.md)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
