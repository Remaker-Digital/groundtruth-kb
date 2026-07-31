"""Doc-code consistency test for the bridge post-verdict transition table.

WI-5827 / TEST-11783 (spec GOV-FILE-BRIDGE-AUTHORITY-001). Asserts the
canonical file-bridge-protocol prose, its generated ``.claude/rules/``
projection, and the ``gtkb-verify`` Loyal Opposition verdict skill agree with
the code of record (``ORDINARY_TRANSITIONS`` / ``POST_GO_REPORT_AUGMENTATIONS``
in ``scripts/bridge_lifecycle_resolver.py``) on lawful post-verdict Prime
statuses, and regression-pins the exact r2b wedge class (``NO-GO -> NEW``).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.bridge_lifecycle_resolver import (  # noqa: E402
    ORDINARY_TRANSITIONS,
    POST_GO_REPORT_AUGMENTATIONS,
)

CANONICAL_DOC = PROJECT_ROOT / "config" / "agent-control" / "gtkb-file-bridge-protocol.md"
PROJECTION_DOC = PROJECT_ROOT / ".claude" / "rules" / "file-bridge-protocol.md"
VERIFY_SKILL = PROJECT_ROOT / ".claude" / "skills" / "gtkb-verify" / "SKILL.md"

TABLE_HEADING = "## Post-Verdict Transition Table"
POST_IMPL_HEADING = "## Post-Implementation Verification"

_ROW_RE = re.compile(r"^\|\s*([A-Z][A-Z -]*?(?:\(post-GO\))?)\s*\|\s*([A-Z, -]+?)\s*\|\s*$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:end] if end != -1 else text[start:]


def _parse_tables(section: str) -> list[dict[str, frozenset[str]]]:
    tables: list[dict[str, frozenset[str]]] = []
    current: dict[str, frozenset[str]] = {}
    in_table = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if line.startswith("|"):
            if line.replace("|", "").replace("-", "").strip() == "":
                continue  # separator row
            match = _ROW_RE.match(line)
            if match is None:
                continue  # header row like "| Previous status | ... |"
            key = match.group(1).replace("(post-GO)", "").strip()
            values = frozenset(v.strip() for v in match.group(2).split(",") if v.strip())
            current[key] = values
            in_table = True
        elif in_table:
            tables.append(current)
            current = {}
            in_table = False
    if current:
        tables.append(current)
    return tables


def _doc_tables(path: Path) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    section = _section(_read(path), TABLE_HEADING)
    tables = _parse_tables(section)
    assert len(tables) == 2, (
        f"{path.name}: expected base + post-GO augmentation tables in '{TABLE_HEADING}', found {len(tables)}"
    )
    return tables[0], tables[1]


def test_canonical_prose_table_matches_resolver() -> None:
    base, augmentations = _doc_tables(CANONICAL_DOC)
    assert base == dict(ORDINARY_TRANSITIONS)
    assert augmentations == dict(POST_GO_REPORT_AUGMENTATIONS)


def test_projection_table_matches_resolver() -> None:
    base, augmentations = _doc_tables(PROJECTION_DOC)
    assert base == dict(ORDINARY_TRANSITIONS)
    assert augmentations == dict(POST_GO_REPORT_AUGMENTATIONS)


def test_no_go_row_never_allows_new() -> None:
    assert "NEW" not in ORDINARY_TRANSITIONS["NO-GO"]
    assert "NO-GO" not in POST_GO_REPORT_AUGMENTATIONS
    for doc in (CANONICAL_DOC, PROJECTION_DOC):
        base, _ = _doc_tables(doc)
        assert "NEW" not in base["NO-GO"], f"{doc.name}: NO-GO row must not allow NEW"


def test_post_implementation_section_names_revised() -> None:
    for doc in (CANONICAL_DOC, PROJECTION_DOC):
        section = _section(_read(doc), POST_IMPL_HEADING)
        assert "corrected report publishes as REVISED" in section
        assert "never NEW" in section
        assert "`NEW` is never a lawful successor to `NO-GO`" in section
        assert "The FIRST post-implementation report after a GO publishes as a NEW" in section
        assert "2. Prime uses the governed writer to publish a NEW verification-request entry" not in section


def test_verify_skill_remedy_names_revised() -> None:
    skill = _read(VERIFY_SKILL)
    assert "MUST instruct Prime Builder to refile the corrected proposal or report as" in skill
    assert "`REVISED`, per the authoritative post-verdict transition table" in skill
    assert "MUST NOT instruct a refile as" in skill
    assert not re.search(r"refile[^.]*with status token `NEW`", skill, flags=re.IGNORECASE | re.DOTALL)
    assert not re.search(r"[Rr]efile the same implementation report as `NEW`", skill)


def test_table_documents_no_action_branch() -> None:
    assert "NO-ACTION" in ORDINARY_TRANSITIONS["NO-GO"]
    for doc in (CANONICAL_DOC, PROJECTION_DOC):
        section = _section(_read(doc), TABLE_HEADING)
        base, _ = _doc_tables(doc)
        assert "NO-ACTION" in base["NO-GO"]
        assert "DCL-NO-ACTION-STATUS-SEMANTICS-001" in section
