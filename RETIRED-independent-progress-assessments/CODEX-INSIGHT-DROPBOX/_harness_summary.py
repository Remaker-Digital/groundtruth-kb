"""Read-only: compact per-harness dispatch summary."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
reg = ROOT / "harness-state" / "harness-registry.json"
data = json.loads(reg.read_text(encoding="utf-8"))
harnesses = data.get("harnesses", data if isinstance(data, list) else [])

print(f"{'ID':<3} {'name':<12} {'type':<12} {'status':<12} {'roles/tags':<28} {'recv_disp':<9} {'fire_ev'}")
print("-" * 92)
for h in harnesses:
    hid = h.get("id", "?")
    name = h.get("harness_name", "?")
    htype = h.get("harness_type", "?")
    status = h.get("lifecycle_status") or h.get("status") or h.get("lifecycle_state") or "?"
    tags = h.get("dispatch_tags") or h.get("role") or h.get("roles") or []
    if isinstance(tags, str):
        tags = [tags]
    recv = h.get("can_receive_dispatch")
    fire = h.get("can_fire_events")
    print(f"{hid:<3} {name:<12} {htype:<12} {str(status):<12} {','.join(tags):<28} {str(recv):<9} {fire}")
