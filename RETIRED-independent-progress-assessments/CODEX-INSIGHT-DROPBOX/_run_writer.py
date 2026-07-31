import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import scripts.gtkb_bridge_writer as w  # noqa: E402

slug, version, body_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
body = Path(body_path).read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
result = w.write_bridge_file(slug, version, body, Path.cwd())
print("WROTE:", result)
