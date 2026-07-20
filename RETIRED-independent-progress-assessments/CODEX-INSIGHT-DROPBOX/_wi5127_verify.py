"""WI-5127 formal-artifact integrity verification (LO read-check; transient scratch)."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "groundtruth-kb/src")
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

PKT = Path(".groundtruth/formal-artifact-approvals")
db = KnowledgeDB("groundtruth.db")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def staged_blob(path: str) -> bytes:
    return subprocess.run(["git", "show", f":{path}"], capture_output=True).stdout


print("=== DCL records: exist + packet self-consistent + inserted==approved ===")
dcls = [
    ("DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001", "2026-07-10-dcl-project-root-boundary-sandbox-output-exception-001.json"),
    ("DCL-PROJECT-ROOT-BOUNDARY-DB-SNAPSHOT-OUTPUT-EXCEPTION-001", "2026-07-10-dcl-project-root-boundary-db-snapshot-output-exception-001.json"),
    ("DCL-PROJECT-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXEC-EXCEPTION-001", "2026-07-10-dcl-project-root-boundary-external-harness-exec-exception-001.json"),
]
for spec_id, pkt_name in dcls:
    spec = db.get_spec(spec_id)
    exists = spec is not None
    pkt = json.loads((PKT / pkt_name).read_text(encoding="utf-8"))
    fc = pkt["full_content"]
    self_ok = sha(fc.encode("utf-8")) == pkt["full_content_sha256"]
    owner = pkt.get("approved_by")
    presented = pkt.get("presented_to_user")
    content = (spec.get("content") or spec.get("body") or spec.get("description") or "") if spec else ""
    inserted_matches = content.strip() == fc.strip() or content == fc
    print(f"  {spec_id}: exists={exists} status={spec.get('status') if spec else None} "
          f"packet_self_consistent={self_ok} approved_by={owner!r} presented={presented} inserted==approved={inserted_matches}")

print("=== narrative/template packets: hash == staged target blob ===")
narr = [
    ("2026-07-10-narrative-project-root-boundary-carriers-001.json", ".claude/rules/project-root-boundary.md"),
    ("2026-07-10-template-upgrade-rehearsal-carriers-001.json", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md"),
    ("2026-07-10-template-canonical-terminology-carriers-001.json", "groundtruth-kb/templates/rules/canonical-terminology.md"),
]
for pkt_name, target in narr:
    pkt = json.loads((PKT / pkt_name).read_text(encoding="utf-8"))
    claimed = pkt["full_content_sha256"]
    fc_sha = sha(pkt["full_content"].encode("utf-8"))
    blob = staged_blob(target)
    blob_sha = sha(blob)
    print(f"  {target}: approved_by={pkt.get('approved_by')!r} presented={pkt.get('presented_to_user')} "
          f"self_consistent={fc_sha == claimed} staged_blob==approved={blob_sha == claimed} (bytes staged={len(blob)})")

db.close()
