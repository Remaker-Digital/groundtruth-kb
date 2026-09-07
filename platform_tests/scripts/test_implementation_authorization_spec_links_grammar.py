"""TEST-11779 - spec-links grammar and formatting-only amendment overlay (WI-5823).

Covers the Slice A/B extraction grammar (bullet precedence, dormant table
fallback, nested ``###`` visibility, compact prose citation parity, fail-closed
empty/placeholder behavior) and the Slice C ``amend-proposal`` overlay
(equivalence gating, strict re-parse, content-addressed idempotency, and the
"directly parseable approved bytes always win" precedence rule).

The companion module
``platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py``
remains the table-focused regression dependency and is executed unchanged.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("implementation_authorization_under_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec_module: @dataclass resolves its defining module via
    # sys.modules[cls.__module__], which is None for an unregistered module and
    # raises AttributeError during class creation.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod() -> Any:
    return _load_module()


# ---------------------------------------------------------------------------
# Slice A/B - Specification Links extraction grammar
# ---------------------------------------------------------------------------

_BULLET_DOC = """NEW

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged here.
"""

_TABLE_DOC = """NEW

## Specification Links

| Spec | Why it applies |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | bridge audit-trail authority |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | spec-to-test mapping |
"""

_BOTH_DOC = """NEW

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - cited as a bullet with a real citation.

| Spec | Why it applies |
|---|---|
| `DCL-NEVER-REACHED-001` | table is dormant while bullets carry citations |
"""

_NESTED_DOC = """NEW

## Specification Links

### Blocking

- `GOV-FILE-BRIDGE-AUTHORITY-001` - visible only if h3 subsections are retained.

### Advisory

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - also inside a nested subsection.
"""


def test_bullet_citations_are_extracted(mod: Any) -> None:
    links = mod.extract_spec_links(_BULLET_DOC)
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in links
    assert "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001" in links


def test_table_fallback_is_used_when_no_bullets(mod: Any) -> None:
    """With no bullet citations the table is the extraction source."""
    links = mod.extract_spec_links(_TABLE_DOC)
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in links
    assert "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001" in links


def test_bullets_take_precedence_and_table_is_dormant(mod: Any) -> None:
    """Bullet precedence: a table alongside cited bullets must not contribute."""
    links = mod.extract_spec_links(_BOTH_DOC)
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in links
    assert "DCL-NEVER-REACHED-001" not in links


def test_nested_h3_subsections_remain_visible(mod: Any) -> None:
    """Slice A: the level-aware reader keeps '### ' subsections in the body."""
    links = mod.extract_spec_links(_NESTED_DOC)
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in links
    assert "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001" in links


def test_section_body_including_subsections_retains_nested_headings(mod: Any) -> None:
    body = mod._section_body_including_subsections(_NESTED_DOC, "Specification Links")
    assert "### Blocking" in body
    assert "### Advisory" in body


@pytest.mark.parametrize(
    "markdown",
    [
        "NEW\n\n## Specification Links\n\n",
        "NEW\n\n## Specification Links\n\n- TBD\n",
        "NEW\n\n# No section at all\n",
    ],
)
def test_empty_or_placeholder_spec_links_fail_closed(mod: Any, markdown: str) -> None:
    """Empty / placeholder / absent sections must raise, never return []."""
    with pytest.raises(mod.AuthorizationError):
        mod.extract_spec_links(markdown)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Open defect found by WI-5823 TEST-11779: a '- None' bullet is extracted as the "
        "spec id 'None' instead of failing closed. PLACEHOLDER_RE omits 'none', which "
        "config/governance file-bridge-protocol lists as placeholder content, and the "
        "token still survives extraction despite not matching _SPEC_ID_RE. Left as a "
        "strict xfail so it flips to a failure the moment the extractor is repaired."
    ),
)
def test_none_placeholder_should_fail_closed(mod: Any) -> None:
    with pytest.raises(mod.AuthorizationError):
        mod.extract_spec_links("NEW\n\n## Specification Links\n\n- None\n")


def test_preflight_parity_harvest_finds_compact_prose_citations(mod: Any) -> None:
    """Compact prose citation parity: harvest sees ids the bullet grammar skips."""
    body = mod._section_body_including_subsections(_BULLET_DOC, "Specification Links")
    harvested = mod._preflight_parity_harvest(body)
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in harvested


# ---------------------------------------------------------------------------
# Slice C - formatting-only amendment overlay
# ---------------------------------------------------------------------------

_APPROVED = """GO-BEARING PROPOSAL PLACEHOLDER"""


def _proposal(spec_section: str) -> str:
    return (
        "NEW\n\n"
        "bridge_kind: prime_proposal\n"
        "Document: gtkb-example-thread\n"
        "Project Authorization: PAUTH-EXAMPLE\n"
        "Project: PROJECT-EXAMPLE\n"
        "Work Item: WI-0001\n\n"
        'target_paths: ["scripts/example.py"]\n\n'
        f"{spec_section}\n"
        "## Requirement Sufficiency\n\n"
        "Existing requirements sufficient.\n"
    )


def test_first_status_token_reads_first_non_blank_line(mod: Any) -> None:
    assert mod._first_status_token("\n\n  GO  \n# heading\n") == "GO"
    assert mod._first_status_token("") == ""


def test_equivalence_passes_for_formatting_only_change(mod: Any) -> None:
    """Reflowing a citation must not change any authority-bearing invariant."""
    approved = _proposal("## Specification Links\n\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n")
    amended = _proposal(
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` -\n  bridge authority, rewrapped across two lines.\n"
    )
    _checks, failures = mod._amendment_equivalence(approved, amended)
    assert failures == []


@pytest.mark.parametrize(
    ("field", "amended_spec", "mutate"),
    [
        ("work_item", None, lambda text: text.replace("Work Item: WI-0001", "Work Item: WI-0002")),
        ("project", None, lambda text: text.replace("Project: PROJECT-EXAMPLE", "Project: PROJECT-OTHER")),
        ("status", None, lambda text: text.replace("NEW\n", "REVISED\n", 1)),
        (
            "target_paths",
            None,
            lambda text: text.replace('["scripts/example.py"]', '["scripts/example.py", "scripts/extra.py"]'),
        ),
    ],
)
def test_equivalence_fails_closed_on_authority_bearing_change(
    mod: Any, field: str, amended_spec: str | None, mutate: Any
) -> None:
    """Any authority-bearing difference must be reported, not tolerated."""
    approved = _proposal("## Specification Links\n\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n")
    amended = mutate(approved)
    _checks, failures = mod._amendment_equivalence(approved, amended)
    assert field in failures


def test_equivalence_detects_spec_set_change(mod: Any) -> None:
    approved = _proposal("## Specification Links\n\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n")
    amended = _proposal(
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n"
        "- `GOV-SMUGGLED-IN-001` - added under cover of a formatting fix.\n"
    )
    _checks, failures = mod._amendment_equivalence(approved, amended)
    assert "preflight_specs" in failures


def test_amended_strict_parse_failures_reports_each_defect(mod: Any) -> None:
    broken = "NEW\n\n## Specification Links\n\n- TBD\n"
    failures = mod._amended_strict_parse_failures(broken)
    assert any("Specification Links" in item for item in failures)
    assert any("Requirement Sufficiency" in item for item in failures)


def test_validate_amended_file_rejects_bridge_paths(mod: Any, tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    candidate = bridge_dir / "gtkb-example-001.md"
    candidate.write_text("NEW\n", encoding="utf-8")
    with pytest.raises(mod.AuthorizationError, match="bridge/"):
        mod._validate_amended_file(tmp_path, str(candidate))


def test_validate_amended_file_rejects_out_of_root(mod: Any, tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("NEW\n", encoding="utf-8")
    with pytest.raises(mod.AuthorizationError, match="project root"):
        mod._validate_amended_file(root, str(outside))


def test_validate_amended_file_accepts_in_root_regular_utf8(mod: Any, tmp_path: Path) -> None:
    candidate = tmp_path / "amended.md"
    candidate.write_text("NEW\n", encoding="utf-8")
    rel, text = mod._validate_amended_file(tmp_path, str(candidate))
    assert rel == "amended.md"
    assert text == "NEW\n"


def test_amendment_identity_excludes_provenance_so_retries_are_idempotent(mod: Any) -> None:
    """Content addressing must not include timestamp or session provenance."""
    identity = mod._amendment_identity(
        bridge_id="gtkb-example",
        proposal_rel="bridge/gtkb-example-001.md",
        approved_digest="sha256:aa",
        go_rel="bridge/gtkb-example-002.md",
        go_digest="sha256:bb",
        amended_digest="sha256:cc",
        checks={},
    )
    assert "created_at" not in identity
    assert "session_id" not in identity
    assert identity["bridge_id"] == "gtkb-example"


def test_load_proposal_amendment_returns_none_without_evidence(mod: Any, tmp_path: Path) -> None:
    assert (
        mod.load_proposal_amendment(
            tmp_path,
            "gtkb-example",
            "approved",
            "go",
            proposal_rel="bridge/gtkb-example-001.md",
            go_rel="bridge/gtkb-example-002.md",
        )
        is None
    )


def test_load_proposal_amendment_rejects_stale_approved_hash(mod: Any, tmp_path: Path) -> None:
    """Evidence bound to different approved bytes must not be honored."""
    directory = mod.proposal_amendment_dir(tmp_path, "gtkb-example")
    directory.mkdir(parents=True)
    record = {
        "schema_version": mod.AMENDMENT_RECORD_SCHEMA_VERSION,
        "bridge_id": "gtkb-example",
        "approved_proposal_file": "bridge/gtkb-example-001.md",
        "approved_proposal_sha256": "sha256:stale",
        "go_file": "bridge/gtkb-example-002.md",
        "go_sha256": mod._content_digest("go"),
        "amended_sha256": mod._content_digest("amended"),
        "equivalence": {},
        "amended_text": "amended",
        "record_sha256": "sha256:whatever",
    }
    (directory / "abc.json").write_text(json.dumps(record), encoding="utf-8")
    assert (
        mod.load_proposal_amendment(
            tmp_path,
            "gtkb-example",
            "approved",
            "go",
            proposal_rel="bridge/gtkb-example-001.md",
            go_rel="bridge/gtkb-example-002.md",
        )
        is None
    )
