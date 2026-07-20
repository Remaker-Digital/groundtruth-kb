import sys, json, sqlite3
sys.path.insert(0, 'groundtruth-kb/src')
from groundtruth_kb.governance.project_authorization_operation_time import evaluate_envelope, load_operation_taxonomy

conn = sqlite3.connect('groundtruth.db')
conn.row_factory = sqlite3.Row
row = conn.execute(
    "SELECT * FROM project_authorizations WHERE id = ?",
    ("PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713",),
).fetchone()
auth = dict(row)
for k in ("allowed_mutation_classes", "forbidden_operations", "included_work_item_ids", "included_spec_ids"):
    if auth.get(k):
        auth[k] = json.loads(auth[k])

ops_to_check = [
    "implementation_packet_create",
    "implementation_start",
    "protected_mutation",
    "credential_lifecycle",
    "destructive_cleanup",
    "dispatcher_mutation",
    "external_system_mutation",
    "git_commit",
    "git_history_rewrite",
    "git_push",
    "production_deployment",
    "release",
]
tax = load_operation_taxonomy()
for op in ops_to_check:
    d = evaluate_envelope(auth, requested_operation=op, target_paths=["groundtruth.db"], taxonomy=tax)
    print(f"{op:30s} allowed={d.allowed!s:6s} reason_code={d.reason_code}")
