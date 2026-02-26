# Membase for Claude — Persistent Knowledge Database Pattern

**A pattern for giving Claude Code persistent, version-controlled, self-auditing project memory using an append-only SQLite database.**

> This pattern was developed across 100+ sessions on a commercial SaaS project (Agent Red Customer Experience). It evolved from markdown-only memory into a structured database after discovering that markdown backlogs drift, context windows forget, and session boundaries lose state. The approach below is extractable to any project.

---

## The Problem

Claude Code sessions have three persistent memory challenges:

1. **Context window saturation** — Long sessions accumulate stale context that biases decisions.
2. **Session boundary amnesia** — Each new session starts cold. CLAUDE.md and MEMORY.md help, but they're unstructured and drift over time.
3. **Undetected regression** — When code changes break previously-verified behavior, there's no automated signal unless you have tests that specifically check for it.

The markdown-only approach (CLAUDE.md + MEMORY.md + topic files) works well for the first ~20 sessions. After that, the files grow unwieldy, contradictions accumulate, and there's no machine-verifiable way to know if what Claude "remembers" is still true.

---

## Architecture Overview

```
project/
  CLAUDE.md                    # Rules, patterns, procedures (HOW to work)
  memory/MEMORY.md             # Current state, recent sessions (WHAT happened)
  tools/knowledge-db/
    db.py                      # Append-only SQLite API (~800 lines)
    knowledge.db               # The database (auto-created)
    seed.py                    # Initial data loader
    assertions.py              # Machine-verifiable checks (~280 lines)
    app.py                     # Read-only web UI (~230 lines)
  .claude/
    hooks/
      assertion-check.py       # SessionStart hook: run assertions + inject handoff
      scheduler.py             # UserPromptSubmit hook: process scheduled prompts
    settings.local.json        # Hook registration
    SCHEDULE.md                # Pre-planned prompts (FIFO queue)
```

### Core Principle: Append-Only

No rows are ever updated or deleted. Every change creates a new versioned record with `changed_by`, `changed_at`, and `change_reason`. Current state = latest version per ID (via SQL views). This gives you:

- **Full audit trail** — Every status change, every correction, every assertion result is preserved.
- **No accidental data loss** — Claude can't accidentally destroy information.
- **Blame tracking** — `changed_by` + `change_reason` tell you exactly why each change happened.

---

## Step 1: Create the Database Module

Create `tools/knowledge-db/db.py`. The core schema has 5 tables:

### Tables

| Table | Purpose |
|-------|---------|
| `specifications` | Work items / features with versioned status tracking |
| `test_procedures` | Test procedure definitions and execution history |
| `operational_procedures` | SOPs, deployment procedures, repeatable processes |
| `assertion_runs` | History of machine-verifiable assertion executions |
| `session_prompts` | Event-sourced session handoff prompts |

### Key Design Decisions

```sql
-- Every table uses the same versioning pattern:
CREATE TABLE specifications (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "245" or "245.1" for sub-specs
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,                 -- e.g. "P0", "P1", "P2"
    scope TEXT,                    -- grouping / module scope
    section TEXT,                  -- logical section within the project
    handle TEXT,                   -- short mnemonic (e.g. "max-turns-align")
    tags TEXT,                     -- JSON array of tags for filtering
    status TEXT NOT NULL,          -- specified | implemented | verified | retired
    assertions TEXT,               -- JSON array of machine-verifiable checks
    changed_by TEXT NOT NULL,      -- 'claude' or 'seed'
    changed_at TEXT NOT NULL,      -- ISO 8601 UTC
    change_reason TEXT NOT NULL,   -- Human-readable explanation
    UNIQUE(id, version)
);

-- Current state = latest version per ID (SQL view)
CREATE VIEW current_specifications AS
SELECT s.* FROM specifications s
INNER JOIN (
    SELECT id, MAX(version) AS max_v
    FROM specifications GROUP BY id
) m ON s.id = m.id AND s.version = m.max_v;
```

**Numbering:** Spec IDs support decimal notation for sub-specs (e.g., `245`, `245.1`, `245.1.3`). This allows hierarchical decomposition without losing traceability.

**Indexes:** Add indexes on frequently-queried columns for performance as the database grows:

```sql
CREATE INDEX IF NOT EXISTS idx_specs_id ON specifications(id);
CREATE INDEX IF NOT EXISTS idx_specs_status ON specifications(status);
CREATE INDEX IF NOT EXISTS idx_specs_version ON specifications(id, version);
CREATE INDEX IF NOT EXISTS idx_specs_changed_at ON specifications(changed_at);
CREATE INDEX IF NOT EXISTS idx_assertion_runs_spec ON assertion_runs(spec_id);
CREATE INDEX IF NOT EXISTS idx_test_procs_id ON test_procedures(id);
CREATE INDEX IF NOT EXISTS idx_session_prompts_session ON session_prompts(session_id);
```

### Python API Pattern

```python
class KnowledgeDB:
    """Append-only knowledge database. Claude is the sole writer."""

    _UNSET = object()  # Sentinel: distinguishes "not provided" from "set to None"

    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).parent / "knowledge.db"
        self._conn = None
        self._ensure_schema()

    def _get_conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")  # Safe for concurrent reads
        return self._conn

    def get_spec(self, spec_id):
        """Get latest version of a spec."""
        row = self._get_conn().execute(
            "SELECT * FROM current_specifications WHERE id = ?", (spec_id,)
        ).fetchone()
        return dict(row) if row else None

    def update_spec(self, spec_id, changed_by, change_reason, **kwargs):
        """Create new version with changes. Append-only — never modifies existing rows.

        Uses _UNSET sentinel to distinguish "not provided" from "explicitly set to None":
            update_spec("245", ..., description=KnowledgeDB._UNSET)  # keeps current
            update_spec("245", ..., description=None)                # sets to NULL
        """
        current = self.get_spec(spec_id)
        if not current:
            raise ValueError(f"Spec {spec_id} not found")
        next_version = current["version"] + 1
        # Merge: use new value if provided, else keep current
        columns = [k for k in current if k != "rowid"]
        merged = {}
        for col in columns:
            if col in kwargs and kwargs[col] is not self._UNSET:
                merged[col] = kwargs[col]
            else:
                merged[col] = current[col]
        merged["version"] = next_version
        merged["changed_by"] = changed_by
        merged["changed_at"] = datetime.now(timezone.utc).isoformat()
        merged["change_reason"] = change_reason
        # Serialize assertions if provided as Python object (avoid double-encoding)
        if "assertions" in kwargs and not isinstance(merged["assertions"], str):
            merged["assertions"] = json.dumps(merged["assertions"])
        # Insert new version row
        cols = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        values = [merged[c] for c in columns]
        self._get_conn().execute(
            f"INSERT INTO specifications ({cols}) VALUES ({placeholders})", values
        )
        self._get_conn().commit()

    def export_json(self, output_path=None):
        """Full logical backup as JSON. Safe to run anytime."""
        # Exports all tables for archival / disaster recovery
        ...

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
```

### Usage in Claude Sessions

```python
import sys; sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()
db.get_spec("245")                       # Latest version of spec 245
db.list_specs(status="implemented")      # All implemented specs
db.get_summary()                         # Counts by status
db.update_spec("245", changed_by="claude",
               change_reason="Verified in S42",
               status="verified")
db.export_json()                         # Full logical backup
db.close()                               # Always close when done
```

---

## Step 2: Machine-Verifiable Assertions

This is the key innovation. Each specification can have JSON assertions that Claude can run automatically:

```python
# Three assertion types:
assertions = [
    # grep — pattern must be found in file (with min_count)
    {"type": "grep", "file": "src/config.py", "pattern": "MAX_TURNS",
     "min_count": 1, "description": "Max turns constant defined"},

    # grep_absent — pattern must NOT be found in file
    {"type": "grep_absent", "file": "src/wizard.py", "pattern": "DuplicateStepName",
     "description": "Wizard doesn't duplicate sidebar content"},

    # glob — file path pattern must match at least one file
    {"type": "glob", "pattern": "admin/shared/HelpTooltip.tsx",
     "description": "HelpTooltip component exists"},
]
```

### Assertion Runner

The assertion runner (`assertions.py`) iterates all specs with assertions, runs each check, and records results in `assertion_runs`. It returns a structured summary:

```python
def run_all_assertions(db, triggered_by="manual"):
    """Run all assertions across all specs. Returns summary dict."""
    specs = db.list_specs_with_assertions()  # Only specs that have assertions
    results = []
    for spec in specs:
        parsed = json.loads(spec["assertions"])
        checks = [run_single_assertion(a) for a in parsed]
        overall_passed = all(c["passed"] for c in checks)
        # Record in assertion_runs table
        db.record_assertion_run(spec["id"], spec["version"],
                                overall_passed, checks, triggered_by)
        results.append({"spec_id": spec["id"], "title": spec["title"],
                        "overall_passed": overall_passed, "checks": checks})
    return {"passed": sum(1 for r in results if r["overall_passed"]),
            "failed": sum(1 for r in results if not r["overall_passed"]),
            "details": results}
```

### Why This Matters

Without assertions, Claude "believes" specs are implemented based on session memory. With assertions, Claude **proves** specs are implemented by checking the actual codebase. When a future code change accidentally breaks a behavior, the assertion catches it at session start.

---

## Step 3: Session Hooks

### SessionStart Hook — Assertion Check + Handoff Injection

Register in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/assertion-check.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

The hook does two things:
1. **Runs all assertions** and classifies failures as either "regressions" (implemented/verified specs now failing) or "expected" (specified but not yet implemented).
2. **Reads the session handoff prompt** stored by the previous session, so Claude automatically knows what to work on next.

```python
# Classification logic in the hook:
for failure in failures:
    spec = db.get_spec(failure["spec_id"])
    status = spec["status"]
    if status in ("implemented", "verified"):
        # REGRESSION — something broke
        regressions.append(failure)
    else:
        # Expected — not yet implemented
        expected.append(failure)
```

### UserPromptSubmit Hook — Session Scheduler

The scheduler hook (`.claude/hooks/scheduler.py`) processes pre-planned prompts from `.claude/SCHEDULE.md`. This enables deferred automation — Claude can schedule future tasks during a session that execute in subsequent sessions.

```markdown
<!-- .claude/SCHEDULE.md format -->
## Group: post-deploy-checks
trigger: always

Update staging deployment status in MEMORY.md after confirming revision is active.
```

**Trigger types:**
- `always` — inject with the next user prompt
- `session_end` — inject when wrap-up keywords are detected ("wrap up", "done", "end session")
- `after:N` — inject after N user prompts have been processed

The scheduler uses file locking to prevent race conditions when multiple hooks fire concurrently.

### Session Handoff Prompts

At the end of each session, Claude stores a structured prompt for the next session:

```python
db.insert_session_prompt("S42", "Continue work on Feature X. Group 3 complete, "
    "start Group 4 (Quick Actions). 4,539 tests, 0 failures.",
    context={
        "production_version": "1.58.3",
        "test_count": 4539,
        "test_failures": 0,
        "wis_implemented": [249, 251, 252],
        "next_tasks": ["WI #243", "WI #244"]
    })
```

The next session's hook automatically retrieves and displays this, then marks it as consumed.

---

## Step 4: Audit Cadence

Every Nth session (default: 5) is automatically flagged as an **audit session**. During wrap-up, the handoff generator checks and prepends audit instructions:

```python
AUDIT_INTERVAL = 5  # configurable

def is_audit_session(self, next_session_id, interval=None):
    n = self.parse_session_number(next_session_id)  # "S100" -> 100
    if n is None:
        return False
    return n % (interval or self.AUDIT_INTERVAL) == 0

def get_audit_directive(self):
    return (
        "AUDIT SESSION: Perform a fresh-context review before new work:\n"
        "1. Knowledge DB integrity - run assertions, check for status drift\n"
        "2. MEMORY.md and CLAUDE.md - accuracy, staleness, contradictions\n"
        "3. Repeatable Procedures - still accurate?\n"
        "4. Open design debt\n"
        "5. Hooks and scheduler - verify all hooks execute without errors\n"
        "Report findings before proceeding with regular work."
    )
```

This compensates for the inevitable context drift that accumulates across sessions.

---

## Step 5: CLAUDE.md + MEMORY.md Boundary

The database doesn't replace your markdown files — it complements them:

| File | Role | Content | Updates |
|------|------|---------|---------|
| **CLAUDE.md** | Rules & architecture | How to work: procedures, patterns, evaluation criteria | Rarely |
| **MEMORY.md** | State & history | What happened: versions, test counts, recent sessions | Every session |
| **Knowledge DB** | Specifications & assertions | Formal specs with machine-verifiable assertions | Every code change |

**Rule of thumb:** If it tells Claude *what to do*, it goes in CLAUDE.md. If it tells Claude *what has been done*, it goes in MEMORY.md. Formal specifications with machine-verifiable truth go in the database.

### CLAUDE.md Should Reference the DB

```markdown
### Knowledge Database
The Knowledge Database (`tools/knowledge-db/knowledge.db`) is the canonical
source of truth for all specifications. Claude is the sole writer. The owner
observes through the read-only web UI at localhost:8090.

Python API:
  db.get_spec("245")
  db.update_spec("245", changed_by="claude", change_reason="...", status="implemented")
  db.close()

When to update:
| Trigger | Action |
| Implement a WI | update_spec(id, status="implemented") |
| Verify a WI passes tests | update_spec(id, status="verified") |
| Discover a wrong status | update_spec(id, status=corrected) |
```

---

## Step 6: Read-Only Web UI

A simple Flask app provides the owner with visibility without giving them write access:

```python
# app.py — ~230 lines, runs at localhost:8090
from flask import Flask, render_template_string
from db import KnowledgeDB

app = Flask(__name__)

@app.route("/")
def index():
    db = KnowledgeDB()
    summary = db.get_summary()
    specs = db.list_specs()
    db.close()
    return render_template_string(TEMPLATE, summary=summary, specs=specs)
```

The owner sees all specs, their statuses, assertion results, and version history. They tell Claude what to fix; Claude creates a corrected version.

---

## Step 7: Seed Script

Bootstrap the database from your existing project artifacts:

```python
# seed.py — Run once to populate initial data
# IMPORTANT: Guard against accidental re-seeding
def main():
    db = KnowledgeDB()
    existing = db.get_summary()
    if existing["total"] > 0 and "--force" not in sys.argv:
        print(f"Database already has {existing['total']} specs. Use --force to re-seed.")
        sys.exit(1)

    # Load from whatever source you have (markdown backlog, JIRA export, etc.)
    for item in your_backlog:
        db.insert_spec(
            id=item["id"],
            title=item["title"],
            status="specified",
            changed_by="seed",
            change_reason="Initial import from backlog"
        )
    db.close()
```

---

## Recurring Instructions for CLAUDE.md

Add these to your project's CLAUDE.md so Claude maintains the database correctly across sessions:

```markdown
### Knowledge Database Maintenance

**Claude is the sole writer.** The owner observes through the read-only web UI.

**When to update the database:**

| Trigger | Action |
|---------|--------|
| Implement a work item | `update_spec(id, status="implemented", change_reason="...")` |
| Verify a WI passes tests | `update_spec(id, status="verified", change_reason="...")` |
| Discover a wrong status | `update_spec(id, status=corrected, change_reason="...")` |
| Complete a test procedure | Create new version via `insert_test_procedure()` |

**Assertion rules:**
- Valid assertion types: `grep`, `grep_absent`, `glob`
- Pass assertions as raw Python lists to `update_spec()` — it handles JSON serialization internally
- After adding new fields to schemas, update count assertions (test drift)
- Run assertions after every batch of changes

**Session wrap-up:** Store a handoff prompt via `db.insert_session_prompt()` so the next session starts with context.

**Audit cadence:** Every 5th session performs a fresh-context integrity review before new work.
```

---

## Lessons Learned (100+ Sessions)

1. **The assertion runner is the single most valuable piece.** It turns "Claude remembers" into "Claude proves." Regressions caught at session start save hours of debugging.

2. **Append-only is not a limitation, it's a feature.** We never need to worry about lost data. At ~20 KB/session, storage is a non-issue for any realistic project lifetime.

3. **The double-serialization trap is real.** `update_spec(assertions=json.dumps([...]))` will double-encode because the method already calls `json.dumps()`. Always pass raw Python objects.

4. **Test drift is the #1 recurring failure mode.** When you add fields, enums, or schema entries, count-based assertions break. The fix is mechanical but easy to forget. The assertion runner catches it immediately.

5. **Session handoff prompts eliminate cold-start friction.** Instead of the human crafting "Continue work on X..." prompts, the previous session stores exactly what the next one needs.

6. **The 5-session audit cadence catches accumulated drift.** Individual sessions maintain the DB well, but small errors compound. Periodic fresh-context reviews are essential.

7. **MEMORY.md and CLAUDE.md still matter.** The database stores formal specs and assertions. The markdown files store patterns, preferences, and operational knowledge that don't fit a relational model.

8. **The read-only web UI builds trust.** The owner sees everything Claude knows without needing to read code or run scripts. This transparency is crucial for long-running commercial projects.

9. **Use a sentinel for "not provided" vs "set to None."** A bare `None` check cannot distinguish "caller omitted this argument" from "caller explicitly set it to None." A module-level `_UNSET = object()` sentinel resolves the ambiguity in merge logic.

10. **Index early.** As the database grows past ~100 specs, queries on `status`, `id`, and `changed_at` benefit noticeably from indexes. Add them in the schema creation, not as an afterthought.

---

## Quick Start Checklist

- [ ] Create `tools/knowledge-db/db.py` with append-only schema
- [ ] Create `tools/knowledge-db/assertions.py` with grep/glob/grep_absent types
- [ ] Create `tools/knowledge-db/seed.py` to bootstrap from existing artifacts
- [ ] Create `tools/knowledge-db/app.py` for read-only web UI
- [ ] Create `.claude/hooks/assertion-check.py` (SessionStart hook)
- [ ] Optionally create `.claude/hooks/scheduler.py` + `.claude/SCHEDULE.md` (session scheduler)
- [ ] Register hooks in `.claude/settings.local.json`
- [ ] Add Knowledge Database section to CLAUDE.md
- [ ] Add session handoff instructions to CLAUDE.md
- [ ] Run `python tools/knowledge-db/seed.py` to populate initial data
- [ ] Verify assertions run at session start

---

*This pattern was developed on the Agent Red Customer Experience project by Remaker Digital. The implementation approach is freely reusable under the MIT license. Adapt the schema to your project's needs — the core principles (append-only, machine-verifiable assertions, session handoff, audit cadence) are universal.*

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
