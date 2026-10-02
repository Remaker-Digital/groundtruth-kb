"""c123 (batch design WP5, G17): the bridge status vocabulary has one source.

SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001 v2 says consumers import the vocabulary module's sets instead of restating them.
The named subsets and the message-kind groups live in groundtruth_kb.bridge.vocabulary, and no other module of the
package or of scripts/ holds a literal of two or more status tokens. Tests are outside the guard: they state contracts
independently, as this module does.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from groundtruth_kb.bridge import vocabulary
from groundtruth_kb.bridge.taxonomy import BRIDGE_KIND_BY_STATUS, BridgeKind

ROOT = Path(__file__).resolve().parents[2]
TWELVE = frozenset(
    {
        "NEW",
        "REVISED",
        "READY",
        "VERDICT-REJECTED",
        "BLOCKED",
        "GO",
        "NO-GO",
        "NOT-READY",
        "SUPERSEDED",
        "VERIFIED",
        "WITHDRAWN",
        "ADVISORY",
    }
)
NAMED_SETS = {
    "PROPOSAL_STATUSES": {"NEW", "REVISED"},
    "WORK_ITEM_HEADER_STATUSES": {"NEW", "REVISED", "BLOCKED"},
    "ACCEPTED_SCOPE_STATUSES": {"GO", "READY", "VERIFIED"},
    "DEPENDENCY_GATED_STATUSES": {"NEW", "REVISED", "GO", "READY", "VERIFIED"},
    "POST_ACCEPTANCE_STATUSES": {"GO", "READY", "NOT-READY", "VERIFIED"},
    "TERMINAL_STATUSES": {"VERIFIED", "WITHDRAWN", "SUPERSEDED"},
    "VERDICT_STATUSES": {"GO", "NO-GO", "NOT-READY", "VERIFIED", "SUPERSEDED"},
    "REPORT_STATUSES": {"READY"},
    "ADVISORY_STATUSES": {"ADVISORY"},
    "REVIEW_STATUSES": {"VERDICT-REJECTED"},
    "OPERATIONAL_STATUSES": {"BLOCKED", "WITHDRAWN"},
}
KIND_OF_GROUP = {
    "PROPOSAL_STATUSES": BridgeKind.IMPLEMENTATION_PROPOSAL,
    "VERDICT_STATUSES": BridgeKind.LO_VERDICT,
    "REPORT_STATUSES": BridgeKind.IMPLEMENTATION_REPORT,
    "ADVISORY_STATUSES": BridgeKind.GOVERNANCE_ADVISORY,
    "REVIEW_STATUSES": BridgeKind.GOVERNANCE_REVIEW,
    "OPERATIONAL_STATUSES": BridgeKind.OPERATIONAL_STATE_CHANGE,
}


@pytest.mark.parametrize(("name", "members"), sorted(NAMED_SETS.items()))
def test_each_named_set_has_its_stated_members(name: str, members: set[str]) -> None:
    assert getattr(vocabulary, name) == frozenset(members)


def test_the_kind_groups_partition_the_twelve() -> None:
    groups = [getattr(vocabulary, name) for name in KIND_OF_GROUP]

    assert vocabulary.CANONICAL_STATUSES == TWELVE
    assert sum(len(group) for group in groups) == len(TWELVE)
    assert frozenset().union(*groups) == TWELVE


def test_the_kind_map_follows_the_groups() -> None:
    expected = {status: kind for name, kind in KIND_OF_GROUP.items() for status in NAMED_SETS[name]}

    assert expected == BRIDGE_KIND_BY_STATUS


def status_literals(path: Path, base: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Set, ast.Tuple, ast.List)):
            elements = node.elts
        elif isinstance(node, ast.Dict):
            elements = [key for key in node.keys if key is not None]
        else:
            continue
        tokens = [
            element.value for element in elements if isinstance(element, ast.Constant) and element.value in TWELVE
        ]
        if len(tokens) >= 2:
            found.append(f"{path.relative_to(base).as_posix()}:{node.lineno}")
    return found


def restated_sets(base: Path) -> list[str]:
    source = base / "groundtruth-kb" / "src" / "groundtruth_kb"
    single_source = source / "bridge" / "vocabulary.py"
    return [
        site
        for folder in (source, base / "scripts")
        for path in sorted(folder.rglob("*.py"))
        if "__pycache__" not in path.parts and path != single_source
        for site in status_literals(path, base)
    ]


def test_no_module_restates_a_status_set() -> None:
    assert restated_sets(ROOT) == []


def test_the_guard_finds_a_restated_set(tmp_path: Path) -> None:
    bridge = tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb" / "bridge"
    bridge.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (bridge / "vocabulary.py").write_text('STATUSES = frozenset({"GO", "READY"})\n', encoding="utf-8")
    (bridge / "consumer.py").write_text('def gated(s):\n    return s in {"GO", "READY"}\n', encoding="utf-8")
    (tmp_path / "scripts" / "tool.py").write_text('KIND = {"NEW": 1, "REVISED": 2}\nONE = ["GO"]\n', encoding="utf-8")

    assert restated_sets(tmp_path) == ["groundtruth-kb/src/groundtruth_kb/bridge/consumer.py:2", "scripts/tool.py:1"]
