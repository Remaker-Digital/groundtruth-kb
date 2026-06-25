import os
import re
from collections import defaultdict
from datetime import datetime

bridge_dir = "bridge"
files = os.listdir(bridge_dir)
print(f"Files in bridge: {len(files)}")

prefixes = defaultdict(list)
for f in files:
    m = re.match(r"^(.*)-(\d{3})\.md$", f)
    if m:
        prefixes[m.group(1)].append((int(m.group(2)), f))

print(f"Unique prefixes: {len(prefixes)}")

actionable = []
for prefix, entries in prefixes.items():
    entries.sort()
    latest_num, latest_file = entries[-1]
    path = os.path.join(bridge_dir, latest_file)
    with open(path, encoding="utf-8", errors="replace") as fh:
        first_line = fh.readline().strip()
    if first_line in ("NEW", "REVISED"):
        mtime = os.path.getmtime(path)
        actionable.append((mtime, latest_file, prefix, latest_num, first_line))

print(f"Actionable count: {len(actionable)}")
actionable.sort()
for mtime, f, prefix, num, status in actionable[-20:]:
    dt = datetime.fromtimestamp(mtime)
    print(f"{dt.strftime('%Y-%m-%d %H:%M')}  {status}  {f}")
