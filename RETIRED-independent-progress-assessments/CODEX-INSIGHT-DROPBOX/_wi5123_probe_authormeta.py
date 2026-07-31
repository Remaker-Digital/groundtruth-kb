import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.bridge_author_metadata import ensure_author_metadata, extract_author_metadata

explicit = {
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code headless bridge auto-dispatch; resolved role loyal-opposition",
}
sample = "NO-GO\n\nbridge_kind: lo_verdict\nDocument: probe\n"
resolved = ensure_author_metadata(sample, project_root=ROOT, explicit=explicit)
meta = extract_author_metadata(resolved)
for key in (
    "author_identity",
    "author_harness_id",
    "author_session_context_id",
    "author_model",
    "author_model_version",
    "author_model_configuration",
):
    print(f"{key} = {meta.get(key)!r}")
