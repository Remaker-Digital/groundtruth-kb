# Membase for Claude — Persistent Knowledge Database Pattern

**A pattern for giving Claude Code persistent, version-controlled, self-auditing project memory using an append-only SQLite database.**

> This pattern was developed across 128 sessions on a commercial SaaS project (Agent Red Customer Experience). It evolved from markdown-only memory into a structured database with 8 managed artifact types after discovering that markdown backlogs drift, context windows forget, and session boundaries lose state. The approach below is extractable to any project.

---

## The Problem

Claude Code sessions have three persistent memory challenges:

1. **Context window saturation** — Long sessions accumulate stale context that biases decisions.
2. **Session boundary amnesia** — Each new session starts cold. CLAUDE.md and MEMORY.md help, but they are unstructured and drift over time.
3. **Undetected regression** — When code changes break previously-verified behavior, there is no automated signal unless you have tests that specifically check for it.

The markdown-only approach (CLAUDE.md + MEMORY.md + topic files) works well for the first ~20 sessions. After that, the files grow unwieldy, contradictions accumulate, and there is no machine-verifiable way to know if what Claude "remembers" is still true.

---

## Architecture Overview

```
project/
  CLAUDE.md                    # Rules & behavior (HOW to work)
  memory/MEMORY.md             # State & bootstrap (WHAT has been done)
  tools/knowledge-db/
    db.py                      # Append-only SQLite API (~1,900 lines)
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

### Foundational Principles

1. **Append-only change control** — No rows are ever updated or deleted. Every change creates a new versioned record with `changed_by`, `changed_at`, and `change_reason`. Current state = latest version per ID (via SQL views).
2. **No phantom artifacts** — If Claude references something, it must exist. If it exists, it must be under change control. If it is under change control, its history must be retrievable.
3. **Machine-verifiable assertions** — Specifications can carry grep/glob assertions. "Claude remembers" becomes "Claude proves."
4. **Never-delete retention** — At ~20 KB/session, storage supports ~57,000 years at 1 session/day. Never purge data.

---

## Step 1: Artifact System Design

The database stores **8 managed artifact types** and **2 supporting record types**. Start with the core 3 (specifications, operational procedures, assertion runs) and add more as your project grows.

### Core Tables (Start Here)

| Table | Purpose |
|-------|---------|
| `specifications` | Requirements — testable descriptions of system behavior |
| `operational_procedures` | SOPs, deployment procedures, repeatable processes |
| `assertion_runs` | History of machine-verifiable assertion executions |
| `session_prompts` | Event-sourced session handoff prompts |

### Extended Tables (Add When Needed)

| Table | Purpose |
|-------|---------|
| `tests` | Individual test artifacts linked to specifications |
| `test_plans` + `test_plan_phases` | Orchestrating artifact: ordered test phases with gate criteria |
| `work_items` | Units of work: regression, defect, or new capability |
| `backlog_snapshots` | Point-in-time snapshots of active work items |
| `documents` | General-purpose project knowledge (migrated topic files, guides) |
| `environment_config` | Environment-specific values under change control |
| `test_coverage` | Many-to-many test-to-spec mapping |

### Key Design Decisions

#### Versioning Pattern (All Tables Follow This)

```sql
CREATE TABLE specifications (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "SPEC-0245" or "245.1" for sub-specs
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,                 -- e.g. "P0", "P1", "P2"
    scope TEXT,                    -- grouping / module scope
    section TEXT,                  -- logical section within the project
    handle TEXT,                   -- short mnemonic (e.g. "max-turns-align")
    tags TEXT,                     -- JSON array of tags for filtering
    type TEXT NOT NULL DEFAULT 'requirement',  -- requirement | governance | protected_behavior
    status TEXT NOT NULL,          -- specified | implemented | verified | retired
    assertions TEXT,               -- JSON array of machine-verifiable checks
    changed_by TEXT NOT NULL,      -- 'claude', 'seed', or session ID
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

#### Specification Types

| Type | Purpose |
|------|---------|
| `requirement` | Business requirement — "would a different choice affect the customer or the business?" |
| `governance` | Process rules — GOV-01 through GOV-12 (how the human-AI team works) |
| `protected_behavior` | Machine-verifiable assertions that must always pass |

#### Tests Table (Spec-Linked)

```sql
CREATE TABLE tests (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "TEST-0001"
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    spec_id TEXT NOT NULL,         -- links to specifications.id
    test_type TEXT NOT NULL,       -- unit | integration | e2e | security | regression | performance
    test_file TEXT,                -- file path
    test_class TEXT,
    test_function TEXT,
    description TEXT,
    expected_outcome TEXT NOT NULL,
    last_result TEXT,              -- PASS | FAIL | null
    last_executed_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);
```

#### Test Plans (Orchestrating Artifact)

An orchestrating artifact contains ordering, criteria, and execution context. It references other artifacts by ID **without duplicating their content**. Each referenced artifact is independently managed and versioned.

```sql
CREATE TABLE test_plans (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "PLAN-001"
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,          -- active | completed | retired
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE test_plan_phases (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "PHASE-001"
    version INTEGER NOT NULL,
    plan_id TEXT NOT NULL,         -- links to test_plans.id
    phase_order INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    gate_criteria TEXT NOT NULL,   -- what must pass to proceed
    test_ids TEXT,                 -- JSON array of test IDs in this phase
    last_result TEXT,
    last_executed_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);
```

#### Work Items (Origin + Component Taxonomy)

```sql
CREATE TABLE work_items (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,              -- e.g. "WI-001"
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    origin TEXT NOT NULL,          -- regression | defect | new | hygiene
    component TEXT NOT NULL,       -- e.g. infrastructure, database, customer_interface
    stage TEXT NOT NULL DEFAULT 'created', -- created | tested | backlogged | implementing | resolved
    source_spec_id TEXT,           -- what spec is this about?
    source_test_id TEXT,           -- what test revealed it?
    failure_description TEXT,
    resolution_status TEXT NOT NULL, -- open | in_progress | resolved | wont_fix
    priority TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);
```

#### Documents (General Knowledge)

```sql
CREATE TABLE documents (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    category TEXT,                 -- e.g. "architecture", "operational", "reference"
    content TEXT NOT NULL,
    source_file TEXT,              -- original file path if migrated from markdown
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);
```

### Indexes

Add indexes on frequently-queried columns for performance as the database grows:

```sql
CREATE INDEX IF NOT EXISTS idx_specs_id ON specifications(id);
CREATE INDEX IF NOT EXISTS idx_specs_status ON specifications(status);
CREATE INDEX IF NOT EXISTS idx_specs_version ON specifications(id, version);
CREATE INDEX IF NOT EXISTS idx_specs_changed_at ON specifications(changed_at);
CREATE INDEX IF NOT EXISTS idx_assertion_runs_spec ON assertion_runs(spec_id);
CREATE INDEX IF NOT EXISTS idx_tests_id ON tests(id);
CREATE INDEX IF NOT EXISTS idx_tests_spec ON tests(spec_id);
CREATE INDEX IF NOT EXISTS idx_test_plans_id ON test_plans(id);
CREATE INDEX IF NOT EXISTS idx_work_items_id ON work_items(id);
CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(resolution_status);
CREATE INDEX IF NOT EXISTS idx_session_prompts_session ON session_prompts(session_id);
CREATE INDEX IF NOT EXISTS idx_documents_id ON documents(id);
```

### Python API Pattern

```python
class KnowledgeDB:
    """Append-only knowledge database. Claude is the sole writer."""

    AUDIT_INTERVAL = 5  # every Nth session is an audit

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

    def insert_spec(self, id, title, status, changed_by, change_reason,
                    type="requirement", **kwargs):
        """Insert a new spec (version 1)."""
        ...

    def update_spec(self, spec_id, changed_by, change_reason, **kwargs):
        """Create new version with changes. Append-only -- never modifies existing rows."""
        current = self.get_spec(spec_id)
        if not current:
            raise ValueError(f"Spec {spec_id} not found")
        next_version = current["version"] + 1
        # Merge: use new value if provided (via _UNSET sentinel), else keep current
        ...

    def insert_test(self, id, title, spec_id, test_type, expected_outcome,
                    changed_by, change_reason, **kwargs):
        """Insert a new test artifact linked to a specification."""
        ...

    def insert_test_plan(self, id, title, status, changed_by, change_reason, **kwargs):
        """Insert a new test plan."""
        ...

    def insert_work_item(self, id, title, origin, component, resolution_status,
                         changed_by, change_reason, **kwargs):
        """Insert a new work item."""
        ...

    def insert_document(self, id, title, content, changed_by, change_reason, **kwargs):
        """Insert a project knowledge document."""
        ...

    def get_summary(self):
        """Counts by status for all artifact types."""
        ...

    def get_open_work_items(self):
        """All work items with resolution_status = open."""
        ...

    def get_untested_specs(self):
        """Specs with no linked test artifacts."""
        ...

    def get_active_test_plan(self):
        """The currently active test plan and its phases."""
        ...

    def create_backlog_snapshot_from_current(self, changed_by, change_reason):
        """Snapshot all open work items into a backlog record."""
        ...

    def export_json(self, output_path=None):
        """Full logical backup as JSON. Safe to run anytime."""
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
db.get_spec("SPEC-0245")                  # Latest version of spec
db.get_summary()                           # Counts by status across all types
db.get_open_work_items()                   # Active work
db.get_untested_specs()                    # Coverage gaps
db.update_spec("SPEC-0245", changed_by="claude",
               change_reason="Verified in S42",
               status="verified")
db.insert_work_item("WI-001", title="Fix rate limiter",
                    origin="defect", component="infrastructure",
                    resolution_status="open",
                    changed_by="claude", change_reason="Found during S42 testing")
db.export_json()                           # Full logical backup
db.close()
```

---

## Step 2: Machine-Verifiable Assertions

This is the key innovation. Each specification can have JSON assertions that Claude can run automatically:

```python
# Three assertion types:
assertions = [
    # grep -- pattern must be found in file (with min_count)
    {"type": "grep", "file": "src/config.py", "pattern": "MAX_TURNS",
     "min_count": 1, "description": "Max turns constant defined"},

    # grep_absent -- pattern must NOT be found in file
    {"type": "grep_absent", "file": "src/wizard.py", "pattern": "DuplicateStepName",
     "description": "Wizard does not duplicate sidebar content"},

    # glob -- file path pattern must match at least one file
    {"type": "glob", "pattern": "admin/shared/HelpTooltip.tsx",
     "description": "HelpTooltip component exists"},
]
```

### Assertion Runner

The assertion runner (`assertions.py`) iterates all specs with assertions, runs each check, and records results in `assertion_runs`. It returns a structured summary:

```python
def run_all_assertions(db, triggered_by="manual"):
    """Run all assertions across all specs. Returns summary dict."""
    specs = db.list_specs_with_assertions()
    results = []
    for spec in specs:
        parsed = json.loads(spec["assertions"])
        checks = [run_single_assertion(a) for a in parsed]
        overall_passed = all(c["passed"] for c in checks)
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

## Step 3: Governance Principles

These governance principles evolved over 128 sessions. They are not mandatory — adopt the ones that fit your project.

### GOV-01: Specs Are the Negotiation Artifact

When the human requests a change or identifies a flaw, Claude's first priority is creating/updating a specification. Testing and implementation proceed only after mutual understanding is established.

### GOV-02: Specs Are Immutable Without Owner Consent

Claude proposes; the human decides. Specifications are the shared contract between human and AI.

### GOV-03: Spec Granularity Is Driven by Test Unambiguity

Every spec should produce an unambiguous PASS/FAIL when tested. If a spec cannot be tested unambiguously, it needs to be decomposed.

### GOV-04: Specs Mature Through Use

Iterative refinement is normal maturation, not a defect. Specs start as `specified`, get `implemented`, then `verified`. Each transition creates a new version.

### GOV-05: Fix the Spec First, Not the Code

When a test fails, first verify the specification is correct. Then verify the test is correct. Only then fix the implementation. Correct the requirement before changing code.

### GOV-06: Specify on Contact

When Claude touches unspecified code, it becomes controlled. Any existing behavior that is modified should first be recorded as a specification.

### GOV-07: No Bug Fixes During Testing

Record defects as work items during test phases; fix them in separate sessions. This keeps testing phases clean and prevents scope creep.

### GOV-08: Knowledge Database Is the Single Source of Truth

All project knowledge lives in the KB. Markdown files store rules (CLAUDE.md) and operational state (MEMORY.md), but specifications, tests, procedures, and documents belong in the database.

### GOV-09: Owner Input Classification

When the owner describes what the system **must do**, **should do**, **must include**, or states numbered criteria, classify the input as **specification language**. Before writing any code: (1) record or verify specifications, (2) identify work items for gaps, (3) add work items to the backlog, (4) present the backlog for prioritization. A `UserPromptSubmit` hook mechanically enforces this, but Claude must also self-enforce.

### GOV-10: Tests Must Exercise Exposed Production Interfaces

Source inspection tests (reading TypeScript files, checking for string literals) are useful as regression supplements but are not Test artifacts. Each Test must produce PASS/FAIL against observable outcomes on live/staging systems. Tests are written and linked to specifications **before** implementation.

### GOV-11: Design Decision Checkpoint Discipline

At each work item or phase completion boundary, Claude must review implementation decisions for specification coverage before proceeding. This is a batched checkpoint, not a real-time pause — review decisions at natural boundaries rather than after every line of code.

### GOV-12: Work Item Creation Triggers Test Creation

Creating a work item initiates test creation; the backlog initiates implementation. This ensures no work proceeds without a testable definition of "done." Tests may be logical assertions, user story descriptions, or abstract descriptions.

### The Specification Litmus Test

"Would a different choice affect the customer or the business?" If yes, it is a specification. If no, it is an implementation detail.

**IS a specification:** Intent taxonomy, tier pricing, conversation handling rules, privacy commitments, UI field inventory, integration choices, quality criteria.

**NOT a specification:** Database schema, middleware ordering, startup sequence, API response shapes, env vars, internal module structure.

---

## Step 4: Session Hooks

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
        # REGRESSION -- something broke
        regressions.append(failure)
    else:
        # Expected -- not yet implemented
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
- `session_end` — inject when wrap-up keywords are detected
- `after:N` — inject after N user prompts have been processed

The scheduler uses file locking to prevent race conditions when multiple hooks fire concurrently.

### Session Handoff Prompts

At the end of each session, Claude stores a structured prompt for the next session:

```python
db.insert_session_prompt("S42",
    prompt_text="Continue work on Feature X. Group 3 complete, "
        "start Group 4. 4,539 tests, 0 failures.",
    context={
        "production_version": "1.58.3",
        "test_count": 4539,
        "next_tasks": ["WI-243", "WI-244"]
    })
```

The next session's hook automatically retrieves and displays this, then marks it as consumed.

---

## Step 5: Audit Cadence

Every Nth session (default: 5) is automatically flagged as an **audit session**. During wrap-up, the handoff generator checks and prepends audit instructions:

```python
def is_audit_session(self, next_session_id, interval=None):
    n = self.parse_session_number(next_session_id)  # "S100" -> 100
    if n is None:
        return False
    return n % (interval or self.AUDIT_INTERVAL) == 0

def get_audit_directive(self):
    return (
        "AUDIT SESSION: Perform a fresh-context review before new work:\n"
        "1. Knowledge DB integrity -- run assertions, check for status drift\n"
        "2. MEMORY.md and CLAUDE.md -- accuracy, staleness, contradictions\n"
        "3. Repeatable Procedures -- still accurate?\n"
        "4. Open design debt -- TODOs, type safety, large files\n"
        "5. Hooks and scheduler -- verify all hooks execute without errors\n"
        "Report findings before proceeding with regular work."
    )
```

This compensates for the inevitable context drift that accumulates across sessions.

---

## Step 6: CLAUDE.md + MEMORY.md Boundary

The database does not replace your markdown files — it complements them:

| File | Role | Content | Updates |
|------|------|---------|---------|
| **CLAUDE.md** | Rules & behavior | How to work: procedures, mandates, evaluation criteria | Rarely — only when rules change |
| **MEMORY.md** | State & bootstrap | What has been done: versions, sessions, quick reference | Every session |
| **Knowledge DB** | Artifacts & assertions | Specifications, tests, work items, documents, procedures | Every code change |

**Rule of thumb:** If it tells Claude *what to do*, it goes in CLAUDE.md. If it tells Claude *what has been done* or *how to access something*, it goes in MEMORY.md. Formal artifacts with machine-verifiable truth go in the database.

**Anti-drift rules for CLAUDE.md:**
- All project knowledge lives in the KB — do not create new markdown files for project knowledge
- Permitted markdown: CLAUDE.md (rules), MEMORY.md + topic files (operational state), external-facing docs
- Topic files are Claude's operational memory, not the canonical source of truth

### CLAUDE.md Should Reference the DB

```markdown
### Knowledge Database
The Knowledge Database (`tools/knowledge-db/knowledge.db`) is the canonical
source of truth for all project artifacts. Claude is the sole writer. The owner
observes through the read-only web UI at localhost:8090.

Python API: `tools/knowledge-db/db.py`
  db.get_spec("SPEC-0245")
  db.insert_work_item(...)
  db.get_open_work_items()
  db.get_untested_specs()
  db.get_summary()
```

---

## Step 7: Read-Only Web UI

A simple Flask app provides the owner with visibility without giving them write access:

```python
# app.py -- ~230 lines, runs at localhost:8090
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

The owner sees all artifacts, their statuses, assertion results, and version history. They tell Claude what to fix; Claude creates a corrected version.

---

## Step 8: Seed Script

Bootstrap the database from your existing project artifacts:

```python
# seed.py -- Run once to populate initial data
# IMPORTANT: Guard against accidental re-seeding
def main():
    db = KnowledgeDB()
    existing = db.get_summary()
    if existing["spec_total"] > 0 and "--force" not in sys.argv:
        print(f"Database already has {existing['spec_total']} specs. "
              "Use --force to re-seed.")
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

Add these to your CLAUDE.md so Claude maintains the database correctly across sessions:

```markdown
### Knowledge Database Maintenance

**Claude is the sole writer.** The owner observes through the read-only web UI.

**When to update the database:**

| Trigger | Action |
|---------|--------|
| Implement a feature | `update_spec(id, status="implemented", change_reason="...")` |
| Verify via tests | `update_spec(id, status="verified", change_reason="...")` |
| Discover a wrong status | `update_spec(id, status=corrected, change_reason="...")` |
| Find a defect | `insert_work_item(origin="defect", ...)` |
| Test reveals regression | `insert_work_item(origin="regression", ...)` |
| Complete a procedure | Create new version via `insert_op_procedure()` |

**Assertion rules:**
- Valid types: `grep`, `grep_absent`, `glob`
- Pass assertions as raw Python lists -- the API handles JSON serialization
- After adding new fields to schemas, update count assertions (test drift)
- Run assertions after every batch of changes

**Session wrap-up:** Store a handoff prompt via `db.insert_session_prompt()`
so the next session starts with context.

**Audit cadence:** Every 5th session performs a fresh-context integrity review
before new work.
```

---

## Lessons Learned (128 Sessions)

1. **The assertion runner is the single most valuable piece.** It turns "Claude remembers" into "Claude proves." Regressions caught at session start save hours of debugging.

2. **Append-only is not a limitation, it is a feature.** We never need to worry about lost data. At ~20 KB/session, storage is a non-issue for any realistic project lifetime.

3. **The double-serialization trap is real.** `update_spec(assertions=json.dumps([...]))` will double-encode because the method already calls `json.dumps()`. Always pass raw Python objects.

4. **Test drift is the #1 recurring failure mode.** When you add fields, enums, or schema entries, count-based assertions break. The fix is mechanical but easy to forget. The assertion runner catches it immediately.

5. **Session handoff prompts eliminate cold-start friction.** Instead of the human crafting "Continue work on X..." prompts, the previous session stores exactly what the next one needs.

6. **The 5-session audit cadence catches accumulated drift.** Individual sessions maintain the DB well, but small errors compound. Periodic fresh-context reviews are essential.

7. **MEMORY.md and CLAUDE.md still matter.** The database stores formal artifacts and assertions. The markdown files store rules, preferences, and operational patterns that do not fit a relational model.

8. **The read-only web UI builds trust.** The owner sees everything Claude knows without needing to read code or run scripts. This transparency is crucial for long-running commercial projects.

9. **Use a sentinel for "not provided" vs "set to None."** A bare `None` check cannot distinguish "caller omitted this argument" from "caller explicitly set it to None." A module-level `_UNSET = object()` sentinel resolves the ambiguity in merge logic.

10. **Index early.** As the database grows past ~100 specs, queries on `status`, `id`, and `changed_at` benefit noticeably from indexes. Add them in the schema creation, not as an afterthought.

11. **Python method name shadowing is silent.** When a class defines two methods with the same name, the second silently replaces the first. No error raised. Always use unique helper names per table (e.g., `_next_test_proc_version` vs `_next_test_version`).

12. **Governance principles emerge from use.** Do not try to design all the rules upfront. Let them crystallize through real sessions. Our 8 governance principles were all discovered through actual failures, not anticipated.

13. **The orchestrating artifact principle prevents content duplication.** Test plans reference test IDs, backlogs reference work item IDs. Never duplicate artifact content inside another artifact — reference by ID and keep each artifact independently versioned.

14. **Specification types enable different behaviors.** Requirements, governance rules, and protected behaviors have different change frequencies and verification patterns. A `type` column lets you filter and handle them differently.

15. **Migrate topic files to the database.** Markdown topic files inevitably drift from reality. Migrating project knowledge into documents under change control catches contradictions and enables search across all knowledge.

16. **Detect specification language mechanically.** When the owner says "must include" or "should do," that is a specification, not an implementation instruction. A `UserPromptSubmit` hook can detect these patterns and inject a reminder to follow the spec-first workflow before Claude starts writing code.

17. **Work item stages prevent premature implementation.** Adding a `stage` column (created → tested → backlogged → implementing → resolved) with transition enforcement prevents work items from reaching implementation without first having tests and backlog placement. The database enforces the workflow, not human vigilance.

18. **Route interception in E2E tests has blast radius.** Browser-level request interception (e.g., Playwright `page.route()`) can inadvertently capture requests beyond the intended scope. Glob patterns like `**/api/team/*` match more URLs than expected, including safe GET endpoints. Design tests to avoid overlapping route handlers rather than relying on method-based filtering.

19. **Governance principles compound.** Each governance principle builds on the others. GOV-12 (work item → test) only works because GOV-10 (tests must exercise production interfaces) defines what a valid test is, which only works because GOV-03 (test unambiguity) defines the quality bar. Adopt them incrementally, but expect later principles to reference earlier ones.

20. **The glossary is the pattern, not the code.** The most important thing Membase establishes is shared vocabulary. When the human says "backlog" and Claude says "backlog," both must refer to the same real, versioned, queryable artifact. Without this agreement, every other benefit (assertions, versioning, governance) is undermined.

---

## Glossary

These terms have specific meanings in the Membase pattern. Each corresponds to a real database table or a documented process — there are no abstract concepts without backing implementation.

### Artifact Types

| Term | Table | Definition |
|------|-------|-----------|
| **Specification** | `specifications` | A requirement — a business decision that affects customers or the business. Litmus test: "Would a different choice affect the customer or the business?" If yes, it is a specification. If no, it is an implementation detail. Functions as a decision log (what was agreed and why), not a build specification (how to construct). Status lifecycle: `specified` → `implemented` → `verified` → `retired`. |
| **Test** | `tests` | An individual testable assertion derived from a specification. Three valid forms: (1) logical assertion — exists/doesn't exist, comparisons, if-then; (2) user story — a verifiable process a user performs; (3) abstract description — measurements, pseudocode, or information describing the desired behavior. Must produce an unambiguous PASS/FAIL. |
| **Test Plan** | `test_plans` | An orchestrating artifact: ordered test phases with gate criteria. References test IDs without duplicating content. Each phase defines what must pass before proceeding to the next. |
| **Work Item** | `work_items` | A unit of work classified by origin (`regression`, `defect`, `new`, `hygiene`) and component. Stage lifecycle: `created` → `tested` → `backlogged` → `implementing` → `resolved`. Links to a source specification and optionally to a test that revealed it. |
| **Backlog Snapshot** | `backlog_snapshots` | A point-in-time snapshot of active work items. Not a living document — a frozen record of what was open at a specific moment. Ordering within the snapshot determines implementation priority. |
| **Operational Procedure** | `operational_procedures` | A step-by-step repeatable process: deployment, verification, audit, recovery. Versioned like all artifacts. |
| **Document** | `documents` | General-purpose project knowledge under change control. Replaces drifting markdown topic files. Anything that is "project knowledge" but not a specification, test, or procedure belongs here. |
| **Environment Config** | `environment_config` | Environment-specific values (URLs, connection strings, thresholds) under change control. Tracks what each environment is configured to use. |

### Supporting Records

| Term | Table | Definition |
|------|-------|-----------|
| **Assertion Run** | `assertion_runs` | A historical record of a machine-verifiable assertion execution. Records which spec was checked, whether it passed, the detailed results, and what triggered the run. |
| **Session Prompt** | `session_prompts` | A structured handoff message stored by one session for the next. Contains what was done, what's next, and key context. Marked as consumed after the receiving session reads it. |

### Concepts (Not Tables)

| Term | Definition |
|------|-----------|
| **Assertion** | A machine-verifiable check attached to a specification. Three types: `grep` (pattern must exist in file), `grep_absent` (pattern must NOT exist in file), `glob` (file path must exist). Stored as JSON in the specification's `assertions` column. Runs automatically at session start via the SessionStart hook. |
| **Phantom Artifact** | A concept referenced as if it were a tracked entity, but with no backing storage, change control, or queryable history. Example: saying "the backlog contains WI-42" when no backlog table exists. The anti-pattern this entire system was designed to eliminate. |
| **Orchestrating Artifact** | An artifact that composes other artifacts by reference (ID only), never by content duplication. Test plans reference test IDs; backlog snapshots reference work item IDs. Each referenced artifact is independently managed and versioned. Prevents content duplication and the drift that accompanies it. |
| **Governance Principle** | A process rule (GOV-\*) governing how the human-AI team works together. Discovered through real project failures, not designed upfront. Currently 14 principles: 12 numbered rules (GOV-01 through GOV-12) plus 2 architectural principles (SPEC-1493: Artifact Inventory, SPEC-1499: Orchestrating Artifact). |
| **Protected Behavior** | A specification with `type = 'protected_behavior'` carrying machine-verifiable assertions that must always pass. Checked in build gates before every deployment. |
| **Append-Only Change Control** | The versioning discipline: no UPDATE in place, no DELETE. Every mutation creates a new versioned row with mandatory `changed_by`, `changed_at`, and `change_reason`. Current state = latest version per ID (via SQL views). Full audit trail preserved indefinitely. |
| **Session Handoff** | The mechanism by which one session stores context for the next. The previous session calls `db.insert_session_prompt()` with a structured prompt; the SessionStart hook retrieves and displays it, then marks it consumed. Eliminates the human needing to craft "Continue work on X..." prompts. |
| **Specify on Contact** | Governance principle (GOV-06): when Claude touches unspecified code, it becomes controlled. Any existing behavior that is modified should first be recorded as a specification before changes are made. |
| **Audit Session** | Every Nth session (default: 5) is automatically flagged for a fresh-context integrity review. The audit covers KB assertions, MEMORY.md accuracy, procedure correctness, and design debt. Compensates for drift that accumulates incrementally across sessions. |

---

## Benefits & Milestones

Membase was not designed upfront — it evolved through real project needs. Each capability below was added in response to a specific problem encountered during production use.

### Evolution Timeline

| Session | Problem Encountered | Capability Added |
|---------|-------------------|-----------------|
| S1–S95 | Markdown backlogs drift; concepts referenced but not tracked | — (markdown-only era) |
| S96 | No machine-verifiable truth about what is implemented | **Knowledge Database** — append-only SQLite, 161 initial specs, assertions, web UI |
| S104–S106 | Requirements scattered across 90 session transcripts | **Specification Discipline** — 871 specs extracted, governance principles crystallized, specification litmus test defined |
| S109 | No way to measure which specs have tests | **Test Coverage** — `test_coverage` table, 1,230 test-to-spec mappings, 26% initial coverage |
| S110 | Topic files contradict each other and the database | **GOV-08** — 30 topic files migrated to KB documents under change control |
| S112 | Low spec coverage despite many tests | **Test Coverage Sprint** — 1,053 new tests, coverage 26% → 59% |
| S113–S114 | "Backlog" and "test plan" referenced but not actually tracked | **Artifact System Redesign** — 5 new tables, phantom artifacts eliminated, orchestrating artifact principle |
| S116–S117 | Claude implements before recording specs from owner requirements | **GOV-09 + GOV-10** — spec-language detection hook (S116), tests must exercise production interfaces (S117) |
| S128 | Work items created without tests; no lifecycle tracking | **GOV-12** — work item creation triggers test creation; `stage` column with transition enforcement |

### Current State (Session 128)

| Category | Metric | Count |
|----------|--------|-------|
| **Specifications** | Total | 1,803 |
| | Verified | 309 |
| | Implemented | 795 |
| | Specified (not yet implemented) | 695 |
| **Tests** | Test artifacts (spec-linked) | 2,797 |
| | Test-to-spec coverage mappings | 1,988 |
| | Automated tests passing | 5,962 |
| **Work Items** | Total | 917 |
| | Resolved | 854 |
| | Open | 27 |
| **Assertions** | Machine-verifiable assertions | 180 |
| | Currently passing | 127 |
| | Expected failures (specified, not implemented) | 53 |
| | Total assertion run records | 19,092 |
| **Knowledge** | Documents under change control | 138 |
| | Operational procedures | 13 |
| | Governance principles | 14 |
| **Database** | Versioned artifact rows | 8,443 |
| | Database size | 14.6 MB |
| | Data loss incidents | 0 |

### What the System Catches

The following failure modes are detected automatically, without human intervention:

- **Regressions at session start** — assertions run before work begins, flagging any spec whose implementation has drifted since the last session
- **Phantom artifact references** — the database enforces that every referenced concept has backing storage and change control
- **Specification drift** — append-only versioning preserves the full decision history; nothing is silently overwritten
- **Cold-start amnesia** — session handoff prompts give each new session the context it needs without human re-explanation
- **Accumulated process drift** — every 5th session is an audit, catching errors that compound across sessions
- **Untested specifications** — `get_untested_specs()` identifies coverage gaps on demand
- **Premature implementation** — GOV-09 hook detects spec language and enforces spec-first workflow; GOV-12 stage gates prevent implementation without tests

### What the System Does Not Measure

Honesty about limitations: Membase does not track session duration, so there are no "time saved" claims. There is no control group (a parallel project without Membase), so there are no comparative productivity metrics. The benefits above are factual — what exists, what was built, what is caught — not extrapolations.

---

## Quick Start Checklist

- [ ] Create `tools/knowledge-db/db.py` with append-only schema (start with specifications + operational_procedures)
- [ ] Create `tools/knowledge-db/assertions.py` with grep/glob/grep_absent types
- [ ] Create `tools/knowledge-db/seed.py` to bootstrap from existing artifacts
- [ ] Create `tools/knowledge-db/app.py` for read-only web UI
- [ ] Create `.claude/hooks/assertion-check.py` (SessionStart hook)
- [ ] Register hooks in `.claude/settings.local.json`
- [ ] Add Knowledge Database section to CLAUDE.md
- [ ] Add session handoff instructions to CLAUDE.md
- [ ] Run `python tools/knowledge-db/seed.py` to populate initial data
- [ ] Verify assertions run at session start
- [ ] Optionally create `.claude/hooks/scheduler.py` + `.claude/SCHEDULE.md` (session scheduler)
- [ ] Add extended tables (tests, test_plans, work_items, documents) when your project grows

---

*This pattern was developed across 128 sessions on the Agent Red Customer Experience project by Remaker Digital. The implementation approach is freely reusable under the MIT license. Adapt the schema to your project's needs — the core principles (append-only, machine-verifiable assertions, governance discipline, session handoff, audit cadence) are universal.*

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
