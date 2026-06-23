"""SPEC-1741 How It Works intent diagram coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
HOW_IT_WORKS = ROOT / "docs-site" / "docs" / "getting-started" / "how-it-works.md"
DOCS_INVENTORY = ROOT / "docs-site" / "docs-inventory.yml"

CUSTOMER_INTENTS = {
    "C1": "general_inquiry",
    "C2": "product_question",
    "C3": "order_status",
    "C4": "return_request",
    "C5": "exchange_request",
    "C6": "refund_request",
    "C7": "shipping_inquiry",
    "C8": "pricing_question",
    "C9": "availability_check",
    "C10": "complaint",
    "C11": "feedback",
    "C12": "account_issue",
    "C13": "payment_issue",
    "C14": "subscription_question",
    "C15": "technical_support",
    "C16": "greeting",
    "C17": "escalation",
}
ADMIN_INTENTS = {"A1": "admin_assistance"}
ORDER_BRANCH_NODES = {"C3", "C4", "C5", "C6", "C7"}
LEAF_NODE_IDS = set(CUSTOMER_INTENTS) | set(ADMIN_INTENTS)


def _intent_diagram(markdown: str) -> str:
    diagrams = re.findall(r"```mermaid\n(.*?)\n```", markdown, flags=re.DOTALL)
    for diagram in diagrams:
        if "18 Intent Classes" in diagram:
            return diagram
    raise AssertionError("Missing 18 Intent Classes Mermaid diagram")


def _class_defs(diagram: str) -> dict[str, dict[str, str]]:
    defs: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"^\s*classDef\s+(\w+)\s+(.+)$", diagram, flags=re.MULTILINE):
        properties = {}
        for part in match.group(2).split(","):
            key, value = part.split(":", 1)
            properties[key.strip()] = value.strip().rstrip(";")
        defs[match.group(1)] = properties
    return defs


def _class_assignments(diagram: str) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for match in re.finditer(r"^\s*class\s+([A-Z0-9,]+)\s+(\w+)\s*$", diagram, flags=re.MULTILINE):
        class_name = match.group(2)
        for node_id in match.group(1).split(","):
            assignments[node_id] = class_name
    return assignments


def _hex_luminance(hex_color: str) -> float:
    value = hex_color.removeprefix("#")
    red, green, blue = (int(value[index : index + 2], 16) for index in (0, 2, 4))
    return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)


def test_intent_categories_diagram_uses_styled_flowchart_nodes() -> None:
    diagram = _intent_diagram(HOW_IT_WORKS.read_text(encoding="utf-8"))
    assignments = _class_assignments(diagram)

    assert "flowchart TB" in diagram
    assert "mindmap" not in diagram.lower()
    assert len(CUSTOMER_INTENTS) == 17

    for node_id, label in CUSTOMER_INTENTS.items() | ADMIN_INTENTS.items():
        assert f"{node_id}[{label}]" in diagram
        assert node_id in assignments, f"{node_id} must have an explicit class"


def test_intent_category_leaf_classes_are_light_with_dark_text() -> None:
    diagram = _intent_diagram(HOW_IT_WORKS.read_text(encoding="utf-8"))
    class_defs = _class_defs(diagram)
    assignments = _class_assignments(diagram)

    assert set(assignments) == LEAF_NODE_IDS
    for node_id in LEAF_NODE_IDS:
        class_name = assignments[node_id]
        properties = class_defs[class_name]
        assert _hex_luminance(properties["fill"]) >= 200, f"{node_id} class {class_name} must use a light pastel fill"
        assert _hex_luminance(properties["color"]) <= 40, f"{node_id} class {class_name} must use dark text"

    assert {assignments[node_id] for node_id in ORDER_BRANCH_NODES} == {"orderIntent"}


def test_docs_inventory_no_longer_describes_intents_as_mindmap() -> None:
    inventory = DOCS_INVENTORY.read_text(encoding="utf-8")

    assert "mindmap diagram" not in inventory
    assert "styled flowchart diagram" in inventory
