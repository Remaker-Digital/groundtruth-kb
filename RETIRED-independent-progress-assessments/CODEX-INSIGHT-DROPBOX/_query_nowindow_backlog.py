"""Read-only: find codex-no-window / dispatch-readiness backlog items."""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
rows = db.list_work_items() if hasattr(db, "list_work_items") else []
keys = ["no-window", "no window", "codex dispatch", "dispatch readiness", "5080", "no_window", "codex-no-window", "kill-loop", "kill loop"]
hits = []
for w in rows:
    blob = f"{w.get('id','')} {w.get('title','')} {w.get('description','')}".lower()
    if any(k in blob for k in keys):
        hits.append(w)

print(f"matches: {len(hits)}")
for w in hits:
    wid = w.get("id") or w.get("work_item_id")
    state = w.get("lifecycle_state") or w.get("stage") or w.get("state") or w.get("status")
    title = (w.get("title") or "")[:95]
    print(f"  {wid} [{state}] {title}")
