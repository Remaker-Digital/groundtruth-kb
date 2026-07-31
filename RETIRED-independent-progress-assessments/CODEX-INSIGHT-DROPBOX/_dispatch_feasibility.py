"""Read-only: Ollama/Alibaba dispatch-feasibility context."""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()

print("=== goose / alibaba / deepseek / ollama-dispatch backlog items ===")
rows = db.list_work_items() if hasattr(db, "list_work_items") else []
keys = ["goose", "alibaba", "deepseek", "ollama"]
for w in rows:
    blob = f"{w.get('id','')} {w.get('title','')} {w.get('description','')}".lower()
    if any(k in blob for k in keys):
        wid = w.get("id") or w.get("work_item_id")
        state = w.get("lifecycle_state") or w.get("stage") or w.get("status")
        print(f"  {wid} [{state}] {(w.get('title') or '')[:88]}")

print()
print("=== deliberation search: ollama/alibaba dispatchable ===")
try:
    for q in ["ollama harness dispatchable prime builder", "alibaba deepseek goose harness dispatch readiness"]:
        print(f"-- {q}")
        for r in db.search_deliberations(q, limit=4):
            did = r.get("deliberation_id") or r.get("id")
            print(f"   {did}  {(r.get('title') or r.get('summary') or '')[:74]}")
except Exception as e:
    print("  ERR", e)
