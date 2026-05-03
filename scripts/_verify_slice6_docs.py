"""One-shot Slice 6 docs verification per bridge -001 §"Test Plan"."""

from __future__ import annotations

import re
import pathlib
import sys

p = pathlib.Path("groundtruth-kb/docs/architecture/isolation.md")
text = p.read_text(encoding="utf-8")

required = [
    "## What is an application subject",
    "## Application root vs GT-KB product root",
    "## Starting a new project with .gt project init.",
    "## What .gt project doctor. checks",
    "## Upgrading an existing project with .gt project upgrade.",
    "## Migrating an existing mixed-root project",
    "## Clean-adopter smoke contract",
    "## Service-down behavior",
    "## Overlay fallback semantics",
]
missing = [s for s in required if not re.search(s, text)]
print("REQUIRED-SECTIONS missing:", missing if missing else "none")

checks = [
    "isolation:adopter-root-placement",
    "isolation:service-endpoint",
    "isolation:work-subject",
    "isolation:no-writable-product-paths",
    "isolation:hooks-point-to-wrappers",
    "isolation:workstream-focus-hook-absent",
    "isolation:work-list-no-product-entries",
    "isolation:release-readiness-app-subject-header",
    "isolation:chroma-regeneratable",
]
missing_checks = [c for c in checks if c not in text]
print("DOCTOR-CHECK missing:", missing_checks if missing_checks else "none")

c_drive = "C:" + chr(92)
e_drive = "E:" + chr(92)
banned_paths = [name for name, tok in [("C-drive", c_drive), ("E-drive", e_drive)] if tok in text]
print("BANNED-PATHS:", banned_paths if banned_paths else "none")

banned_words_re = re.compile(r"\b(incident|regression|defect)\b", re.IGNORECASE)
banned_words_hits = banned_words_re.findall(text)
print("BANNED-WORDS:", banned_words_hits if banned_words_hits else "none")

session_re = re.compile(r"\bS\d{3,}\b")
delib_re = re.compile(r"DELIB-S\d{3,}-[A-Z0-9-]+")
text_without_delib = delib_re.sub("DELIB-CITED", text)
session_hits = session_re.findall(text_without_delib)
print("SESSION-IDS (outside DELIB cites):", session_hits if session_hits else "none")

print("OVERLAY-DELIB cited:", "DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION" in text)
print("REHEARSAL-DRIVER cited:", "rehearse_isolation.py" in text)
print("RECIPE cited:", "upgrade-rehearsal-recipe.md" in text)
print("LOC:", len(text.splitlines()))

# Cross-link integrity: each ../reference/X.md must point to a file that exists
docs_root = p.parent.parent
links = re.findall(r"\(\.\./([\w\-/]+\.md)\)", text)
broken = [link for link in links if not (docs_root / link).exists()]
print("BROKEN-CROSS-LINKS:", broken if broken else "none")

# index.md cross-link
index_text = (docs_root / "index.md").read_text(encoding="utf-8")
print("INDEX cross-link present:", "architecture/isolation.md" in index_text)

if missing or missing_checks or banned_paths or banned_words_hits or session_hits or broken:
    sys.exit(1)
