"""WI-7280: the resource contract must not cite a retired authority.

The session envelope is the contract agents read to resolve where bridge state
lives, so a retired citation there propagates into every session that consults
it. ``resource_contract.resources.bridge_queue.authority`` named
``TAFE/dispatcher bridge state ...`` while the governing spec
``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`` is already retired in MemBase, and
Compact Operating Guidance s10 forbids preserving TAFE as current authority or
fallback.

``topic_qualifiers`` carried the token too. That list is a live routing surface,
not prose, so leaving ``TAFE`` in it kept the retired name reachable from prompt
text.

These tests are written against the retired *substrate*, not against one exact
replacement string, so a future rewording of the authority does not fail them
while a reintroduced retired citation does.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from groundtruth_kb.context.resource_routing import (
    canonical_resource_contract,
    validate_resource_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATHS = (
    REPO_ROOT / "config" / "registry" / "context-manifests.toml",
    REPO_ROOT
    / "groundtruth-kb"
    / "src"
    / "groundtruth_kb"
    / "context"
    / "registries"
    / "v1"
    / "context-manifests.toml",
)

# Substrates whose governing records are retired. A contract that names any of
# these is citing a retired authority as current.
RETIRED_SUBSTRATES = ("TAFE",)


def test_generated_contract_names_no_retired_substrate() -> None:
    contract = canonical_resource_contract()
    rendered = repr(contract)
    for substrate in RETIRED_SUBSTRATES:
        assert substrate not in rendered, f"resource contract cites retired substrate {substrate!r}"


def test_bridge_queue_authority_names_the_current_authority() -> None:
    """Positive control: removing the retired name must not empty the field."""
    authority = canonical_resource_contract()["resources"]["bridge_queue"]["authority"]
    assert authority.strip(), "bridge_queue authority must not be blank"
    assert "bridge/" in authority, f"bridge_queue authority no longer names the bridge files: {authority!r}"


def test_topic_qualifiers_carry_no_retired_substrate() -> None:
    qualifiers = canonical_resource_contract()["topic_qualifiers"]
    for substrate in RETIRED_SUBSTRATES:
        assert substrate not in qualifiers, (
            f"{substrate!r} remains a live topic qualifier, keeping the retired name reachable from prompt text"
        )
    assert "bridge" in qualifiers, "removing the retired token must not empty the qualifier list"


def test_contract_still_validates_after_the_correction() -> None:
    """The validator compares against the canonical contract exactly.

    A correction applied to only one of the two must fail here, which is the
    point: this is what catches a partial edit.
    """
    assert validate_resource_contract(canonical_resource_contract()) is not None


@pytest.mark.parametrize("registry_path", REGISTRY_PATHS, ids=lambda p: p.parent.name)
def test_registry_manifests_name_no_retired_substrate(registry_path: Path) -> None:
    if not registry_path.is_file():
        pytest.skip(f"registry not present: {registry_path}")
    raw = registry_path.read_text(encoding="utf-8")
    for substrate in RETIRED_SUBSTRATES:
        assert substrate not in raw, f"{registry_path.name} cites retired substrate {substrate!r}"


def test_registry_manifests_agree_with_each_other() -> None:
    """The packaged copy and the config copy must not drift apart.

    They were byte-identical before this correction; a fix applied to one and
    not the other would leave the retired citation live on whichever path the
    runtime actually loads.
    """
    present = [path for path in REGISTRY_PATHS if path.is_file()]
    if len(present) < 2:
        pytest.skip("only one registry manifest present")
    first = present[0].read_text(encoding="utf-8")
    for other in present[1:]:
        assert other.read_text(encoding="utf-8") == first, f"{other} drifted from {present[0]}"


@pytest.mark.parametrize("registry_path", REGISTRY_PATHS, ids=lambda p: p.parent.name)
def test_registry_bridge_queue_authority_matches_the_generated_contract(registry_path: Path) -> None:
    """Registry data and the in-code contract must state the same authority."""
    if not registry_path.is_file():
        pytest.skip(f"registry not present: {registry_path}")
    data = tomllib.loads(registry_path.read_text(encoding="utf-8"))
    expected = canonical_resource_contract()["resources"]["bridge_queue"]["authority"]
    found = [
        value for value in _iter_authority_values(data) if "bridge" in value.lower() and "membase" not in value.lower()
    ]
    assert found, f"{registry_path.name} declares no bridge_queue authority"
    for value in found:
        assert value == expected, f"{registry_path.name} authority {value!r} != contract {expected!r}"


def _iter_authority_values(node: object):
    """Yield every ``authority`` string anywhere in the parsed TOML."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "authority" and isinstance(value, str):
                yield value
            else:
                yield from _iter_authority_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_authority_values(item)
