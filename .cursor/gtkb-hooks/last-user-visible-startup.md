# GroundTruth-KB Fresh Session Startup

Generated: 2026-06-25T08:24:01Z
Dashboard: GroundTruth-KB Project Dashboard: http://localhost:3000/d/gtkb/groundtruth-kb-dashboard

## Startup Disclosure

### Role And Routing

- Role being assumed: Prime Builder
- Interactive resolved role: Prime Builder
- Interactive role source: durable registry fallback; no transcript-defined interactive role was provided to startup
- Durable registry role: Prime Builder
- Durable registry role authority: headless dispatch routing and interactive fallback only; non-overriding when a transcript-defined interactive role is present
- Role mapping source: harness-state/harness-registry.json
- Harness self-identification: E

### Session-Context Review Independence

- Formal GO / NO-GO / VERIFIED must come from a different model session context than the artifact author/implementer.
- Blocker: reviewer session context equals artifact `author_session_context_id`; fail closed when metadata is missing or unreadable.
- Not the boundary: harness ID, vendor, or durable registry role (routing labels only).
- `::init gtkb pb` grants Prime Builder authority regardless of durable registry role; it does not permit this session to GO/VERIFY its own authored or implemented work.

### Compact Project State

- GT-KB release blockers: 0
- GT-KB active backlog items: 0
- GT-KB open MemBase work items: 11 (subject-scoped; 255 across all subjects)
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 86
- GT-KB drift changed paths: 1
- GT-KB Testing/tool rollup: 0 failing, 2 manual, 15 ready/passing (queried repo: unknown)
- Active harness role slot: `prime-builder` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: fail (harness=all, role=prime-builder, MISSING=32, PASS=142, STALE=6)

### Init Scope

- This `::init` disclosure is minimized for routing, role authority, and compact project state.
- Operator-facing activity context is loaded with `::open <activity>` after startup.
- The `::open <activity>` path injects the activity disposition profile, dashboard pointer, active work subject, compact operator briefing, and top-priority surface.
- Startup report path: `docs/gtkb-dashboard/session-startup-report.md`