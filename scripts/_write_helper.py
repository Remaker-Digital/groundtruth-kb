import sys, pathlib
target = sys.argv[1]
content = sys.stdin.read()
pathlib.Path(target).write_text(content, encoding="utf-8")
print(f"Wrote {target} ({len(content)} bytes)")
