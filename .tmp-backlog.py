from groundtruth_kb.db import KnowledgeDB

db = KnowledgeDB("groundtruth.db")
items = db.list_work_items()
for wi in items:
    stage = wi.get("stage", "?")
    if stage in ("complete", "resolved", "retired", "cancelled"):
        continue
    wid = wi["id"]
    prio = wi.get("priority", "?")
    proj = wi.get("project_name", "")
    title = wi["title"][:90]
    print(f"{wid} | {stage} | {prio} | {proj} | {title}")
