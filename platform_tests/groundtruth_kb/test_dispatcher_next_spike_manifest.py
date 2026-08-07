"""Dispatcher Next spike pinned-dependency manifest drift guard (WI-5617).

Per ``bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-001.md``
(REVISED at ``-003``, Loyal Opposition GO at ``-004``).

``test_dispatcher_next_foundation.py::test_pinned_dependencies_import_under_python_314``
asserts exact installed versions via ``importlib.metadata``, but nothing declared
those pins, so the asserted environment could not be reconstructed. The manifest
closes that gap.

A manifest is only useful if it cannot drift from what the code asserts. A
manifest that disagrees with ``dependency_versions()`` would be worse than no
manifest, because it would be confidently wrong. These tests pin agreement in
BOTH directions -- an added, removed, or re-pinned dependency on either side
fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "config" / "dispatcher" / "requirements-dispatcher-next-spike.txt"

# name==version, exact pin only. A range specifier (>=, ~=, <) must not match:
# the foundation asserts one exact version, so a range cannot express it.
PIN_RE = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)==(?P<version>[^\s#]+)$")


def _parse_manifest() -> dict[str, str]:
    """Parse the manifest into {name: version}, ignoring comments and blanks."""
    pins: dict[str, str] = {}
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.match(line)
        assert match is not None, f"manifest line is not an exact `name==version` pin: {raw!r}"
        pins[match.group("name")] = match.group("version")
    return pins


@pytest.fixture(scope="module")
def declared_versions() -> dict[str, str]:
    from groundtruth_kb.dispatcher_next.foundation import dependency_versions

    return dict(dependency_versions())


# --------------------------------------------------------------------------
# T1 - the manifest exists and is non-empty
# --------------------------------------------------------------------------


def test_t1_manifest_exists_and_declares_pins():
    assert MANIFEST.is_file(), f"pinned-dependency manifest is absent: {MANIFEST}"
    assert _parse_manifest(), "manifest declares no pins"


# --------------------------------------------------------------------------
# T2 / T3 - manifest and code agree exactly, in both directions
# --------------------------------------------------------------------------


def test_t2_manifest_matches_dependency_versions_exactly(declared_versions):
    assert _parse_manifest() == declared_versions


def test_t3_no_pin_missing_from_manifest(declared_versions):
    missing = sorted(set(declared_versions) - set(_parse_manifest()))
    assert not missing, f"asserted by the foundation but absent from the manifest: {missing}"


def test_t3b_no_extra_pin_in_manifest(declared_versions):
    extra = sorted(set(_parse_manifest()) - set(declared_versions))
    assert not extra, f"declared in the manifest but not asserted by the foundation: {extra}"


def test_t3c_versions_agree_per_dependency(declared_versions):
    pins = _parse_manifest()
    mismatched = {
        name: (pins[name], declared_versions[name])
        for name in set(pins) & set(declared_versions)
        if pins[name] != declared_versions[name]
    }
    assert not mismatched, f"manifest/code version disagreement {{name: (manifest, code)}}: {mismatched}"


# --------------------------------------------------------------------------
# T4 - well-formedness: every pin is exact
# --------------------------------------------------------------------------


def test_t4_every_pin_is_an_exact_equality_pin():
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        assert PIN_RE.match(line), f"not an exact `==` pin: {raw!r}"
        assert not any(op in line for op in (">=", "<=", "~=", ">", "<", "!=")), (
            f"range specifier is not an exact pin: {raw!r}"
        )


@pytest.mark.parametrize("bad", ["dbos>=2.27.0", "dbos", "dbos~=2.27", "dbos<3"])
def test_t4b_parser_rejects_non_exact_pins(bad):
    """The guard is only meaningful if the parser would actually reject drift."""
    assert PIN_RE.match(bad) is None
