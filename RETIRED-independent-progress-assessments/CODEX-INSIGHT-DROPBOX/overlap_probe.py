# Read-only LO analysis probe: open GO'd bridge threads and target_paths overlaps.
import json
import re
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]
bridge = root / "bridge"
name_re = re.compile(r"^(?P<slug>.+)-(?P<v>[0-9]{3})[.]md$")
tp_re = re.compile(r"target_paths\s*[:=]\s*(\[[^\n]+\])")

threads = defaultdict(list)
for f in bridge.glob("*.md"):
    m = name_re.match(f.name)
    if m:
        threads[m.group("slug")].append((int(m.group("v")), f))


def first_token(f):
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s:
            return s.split()[0]
    return ""


go_threads = {}
for slug, vs in threads.items():
    vs.sort()
    _, latest_f = vs[-1]
    if first_token(latest_f) == "GO":
        tps = []
        for v, f in reversed(vs):
            txt = f.read_text(encoding="utf-8", errors="replace")
            if txt.lstrip().split("\n", 1)[0].strip() in ("NEW", "REVISED"):
                mm = tp_re.search(txt)
                if mm:
                    try:
                        tps = json.loads(mm.group(1))
                    except Exception:
                        tps = []
                break
        go_threads[slug] = tps

print("OPEN GO-LATEST THREADS:", len(go_threads))
for slug, tps in sorted(go_threads.items()):
    print(f"  {slug}")
    for p in tps:
        print(f"      - {p}")

print()
print("=== target_paths OVERLAPS among open GO threads ===")
slugs = list(go_threads)
found = False
for i in range(len(slugs)):
    for j in range(i + 1, len(slugs)):
        ov = set(go_threads[slugs[i]]) & set(go_threads[slugs[j]])
        if ov:
            found = True
            print(f"  OVERLAP: {slugs[i]}")
            print(f"        <> {slugs[j]}")
            for p in sorted(ov):
                print(f"           shared: {p}")
if not found:
    print("  (none)")
