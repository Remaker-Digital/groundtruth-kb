"""S154 session handoff prompt."""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db", "knowledge.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

prompt_text = """Continue work on Agent Red Customer Experience commercial project.
Location: E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Previous session: S154 (documentation + GitHub hygiene).

S154 completed:
- Updated 6 wiki pages (Home, Project-Status, Test-Coverage, Changelog, Defect-Log, Testing-Strategy)
- Added 9 GitHub repo topics and updated description
- Closed 3 stale GitHub issues (#103, #104, #64)
- Committed S153 remaining files (15 scripts + 12 test files)
- All pushed to remote (commit 0a9eafca)

Current state:
- Tests: 5,908 passed, 1 known fail (SPEC-1620: 4 manual tests remain)
- 6 open GitHub issues (all genuine)
- 16 open WIs (all reviewed as legitimate)
- All quality gates at ceiling (assertion 99.7%, pass 100%, traceability 100%)
- S155 is an audit session (every 5th)

Next: [describe task]"""

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

c.execute(
    """INSERT INTO session_prompts (session_id, version, event_type, created_at, prompt_text, context)
       VALUES (?, 1, 'created', ?, ?, ?)""",
    ("S154", now, prompt_text, "S154 documentation + GitHub hygiene session"),
)
conn.commit()
print(f"Inserted S154 session prompt")
conn.close()
