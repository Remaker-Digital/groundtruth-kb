"""Fix SPEC-STARTHERE-* assertions that used ^ anchor.

Python's re.findall (used by the assertion engine) does not enable MULTILINE
by default, so ^ matches only the start of the file. Rewrite affected patterns
with the (?m) inline flag so ^ matches each line.

Affected specs:
- SPEC-STARTHERE-BLOCKDIAGRAM   (^```mermaid)
- SPEC-STARTHERE-PREREQ-ORDERING (^## Prerequisites, ^## Install)
- SPEC-STARTHERE-DAYINLIFE      (^### Activity \d)
"""

from __future__ import annotations

from groundtruth_kb.db import KnowledgeDB

CHANGED_BY = "prime-opus-4-7-s299c"
CHANGE_REASON = (
    "Switch ^ anchors to (?m)^ inline flag so re.findall matches per-line, "
    "not only at file start. Codex GO conditions unchanged."
)

UPDATES: dict[str, list[dict[str, object]]] = {
    "SPEC-STARTHERE-EVIDENCE": [
        {
            "type": "all_of",
            "description": "Evidence page exists with provenance footnotes per metric",
            "assertions": [
                {"type": "file_exists", "file": "docs/evidence.md"},
                {
                    "type": "count",
                    "pattern": r"(?m)^\[\^[^\]]+\]:",
                    "file": "docs/evidence.md",
                    "operator": ">=",
                    "expected": 3,
                    "description": "At least 3 footnote definitions (provenance markers)",
                },
                {
                    "type": "grep",
                    "pattern": r"(?i)commit\s*sha|commit\s*hash|commit\s*`",
                    "file": "docs/evidence.md",
                    "description": "Commit SHA reference appears in footnotes",
                },
            ],
        }
    ],
    "SPEC-STARTHERE-BLOCKDIAGRAM": [
        {
            "type": "grep",
            "pattern": r"(?m)^```mermaid",
            "file": "docs/start-here.md",
            "min_count": 1,
            "description": "Mermaid fence present in start-here.md",
        }
    ],
    "SPEC-STARTHERE-PREREQ-ORDERING": [
        {
            "type": "all_of",
            "description": "Both Prerequisites and Install headings exist",
            "assertions": [
                {
                    "type": "grep",
                    "pattern": r"(?m)^## Prerequisites",
                    "file": "docs/start-here.md",
                },
                {
                    "type": "grep",
                    "pattern": r"(?m)^## .*Install",
                    "file": "docs/start-here.md",
                },
            ],
        }
    ],
    "SPEC-STARTHERE-DAYINLIFE": [
        {
            "type": "all_of",
            "description": "Day in the Life wired into nav and covers six activities",
            "assertions": [
                {
                    "type": "grep",
                    "pattern": r"day-in-the-life\.md",
                    "file": "mkdocs.yml",
                },
                {
                    "type": "count",
                    "pattern": r"(?m)^### Activity \d",
                    "file": "docs/day-in-the-life.md",
                    "operator": ">=",
                    "expected": 6,
                },
            ],
        }
    ],
}


def main() -> None:
    db = KnowledgeDB()
    for spec_id, assertions in UPDATES.items():
        db.update_spec(
            spec_id,
            CHANGED_BY,
            CHANGE_REASON,
            assertions=assertions,
        )
        print(f"updated: {spec_id}")


if __name__ == "__main__":
    main()
