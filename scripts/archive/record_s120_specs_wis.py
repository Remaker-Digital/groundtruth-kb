import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "knowledge-db"))
import db as db_mod

kdb = db_mod.KnowledgeDB()
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s120_data.json")
data = json.loads(open(data_path, "r", encoding="utf-8").read())

for s in data["specs"]:
    kdb.insert_spec(**s)
    print(f"  Spec {s['id']}: {s['title']}")

for w in data["work_items"]:
    kdb.insert_work_item(**w)
    print(f"  WI {w['id']}: {w['title']}")

print(f"Done: {len(data['specs'])} specs, {len(data['work_items'])} work items recorded")
summary = kdb.get_summary()
print(f"KB totals: {summary['specifications']} specs, {summary['work_items']} WIs")
