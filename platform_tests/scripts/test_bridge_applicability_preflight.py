"""Tests for mechanical bridge applicability preflight.

Governing decisions: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001,
ADR-ISOLATION-APPLICATION-PLACEMENT-001.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from groundtruth_kb.governance.approval_packet import construct_approval_packet

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"

spec = importlib.util.spec_from_file_location("bridge_applicability_preflight", SCRIPT_PATH)
assert spec is not None
preflight = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["bridge_applicability_preflight"] = preflight
spec.loader.exec_module(preflight)


def _write_bridge(root: Path, bridge_id: str, content: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / f"{bridge_id}-001.md").write_text(f"NEW\n\n{content}", encoding="utf-8")


def _write_bridge_version(root: Path, bridge_id: str, version: int, status: str, content: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / f"{bridge_id}-{version:03d}.md").write_text(f"{status}\n\n{content}", encoding="utf-8")


def _write_config(path: Path) -> None:
    path.write_text(
        """
[[rules]]
spec_id = "ADR-ISOLATION-APPLICATION-PLACEMENT-001"
severity = "blocking"
rationale = "Application placement must honor the root boundary."
applies_when_paths_match = ["applications/**"]

[[rules]]
spec_id = "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"
severity = "advisory"
rationale = "Concrete requirements should be durable."
applies_when_content_matches = ["requirement"]
""",
        encoding="utf-8",
    )


def _write_pauth_db(root: Path) -> Path:
    db_path = root / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """CREATE TABLE current_project_authorizations (
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL, status TEXT NOT NULL,
                included_spec_ids TEXT, excluded_spec_ids TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO current_project_authorizations VALUES (?, ?, ?, ?, ?)",
            ("PAUTH-FIXTURE", "PROJECT-FIXTURE", "active", json.dumps(["SPEC-OLD"]), json.dumps([])),
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _pauth_amendment_content(change_reason: str) -> str:
    envelope = {
        "id": "PAUTH-FIXTURE",
        "project_id": "PROJECT-FIXTURE",
        "included_spec_ids": ["SPEC-OLD", "SPEC-NEW"],
        "excluded_spec_ids": [],
        "change_reason": change_reason,
    }
    return (
        "# Proposal\n\n"
        "Project: PROJECT-FIXTURE\n\n"
        'target_paths: ["groundtruth.db"]\n\n'
        "## Specification Links\n\n"
        "- DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001\n\n"
        f"```json\n{json.dumps(envelope)}\n```\n"
    )


def _approval_packet(
    *,
    approved_by: str = "owner",
    coverage: str = "SPEC-NEW",
    identity: str = "PROJECT-FIXTURE PAUTH-FIXTURE",
    artifact_id: str = "PAUTH-FIXTURE",
) -> dict[str, object]:
    full_content = f"{identity} {coverage}"
    return construct_approval_packet(
        artifact_type="governance",
        artifact_id=artifact_id,
        action="update",
        source_ref="test-fixture",
        full_content=full_content,
        approval_mode="approve",
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request=full_content,
        changed_by="test",
        change_reason=full_content,
        approved_by=approved_by,
    )


def test_preflight_reports_structured_pauth_amendment_blocking_error(tmp_path: Path) -> None:
    bridge_id = "pauth-amendment"
    _write_bridge(tmp_path, bridge_id, _pauth_amendment_content("missing owner evidence"))
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )

    assert packet["missing_required_specs"] == []
    assert packet["preflight_passed"] is False
    assert len(packet["blocking_errors"]) == 1
    assert "No packet path detected" in packet["blocking_errors"][0]
    assert "blocking_errors:" in preflight.format_markdown(packet)


def test_preflight_accepts_structured_pauth_amendment_with_exact_owner_evidence(tmp_path: Path) -> None:
    bridge_id = "pauth-amendment"
    rel_path = ".groundtruth/formal-artifact-approvals/pauth-amendment.json"
    packet_path = tmp_path / rel_path
    packet_path.parent.mkdir(parents=True)
    packet_path.write_text(json.dumps(_approval_packet()), encoding="utf-8")
    _write_bridge(tmp_path, bridge_id, _pauth_amendment_content(f"Owner evidence: {rel_path}"))
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )

    assert packet["blocking_errors"] == []
    assert packet["preflight_passed"] is True


def test_preflight_rejects_out_of_root_pauth_approval_path(tmp_path: Path) -> None:
    bridge_id = "pauth-amendment"
    rel_path = ".groundtruth/formal-artifact-approvals/../../../outside.json"
    _write_bridge(tmp_path, bridge_id, _pauth_amendment_content(f"Owner evidence: {rel_path}"))
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )

    assert packet["preflight_passed"] is False
    assert "outside the in-root approval directory" in packet["blocking_errors"][0]


def test_preflight_rejects_malformed_pauth_approval_json(tmp_path: Path) -> None:
    bridge_id = "pauth-amendment"
    rel_path = ".groundtruth/formal-artifact-approvals/pauth-amendment.json"
    packet_path = tmp_path / rel_path
    packet_path.parent.mkdir(parents=True)
    packet_path.write_text("{malformed", encoding="utf-8")
    _write_bridge(tmp_path, bridge_id, _pauth_amendment_content(f"Owner evidence: {rel_path}"))
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )

    assert packet["preflight_passed"] is False
    assert "not readable JSON" in packet["blocking_errors"][0]


def test_preflight_rejects_invalid_nonowner_or_noncovering_pauth_packet(tmp_path: Path) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)
    rel_path = ".groundtruth/formal-artifact-approvals/pauth-amendment.json"
    packet_path = tmp_path / rel_path
    packet_path.parent.mkdir(parents=True)

    cases = [
        ({}, "fails schema validation"),
        (_approval_packet(approved_by="reviewer"), "not owner-approved"),
        (
            _approval_packet(identity="PROJECT-OTHER PAUTH-OTHER", artifact_id="GOV-OTHER"),
            "does not mention project",
        ),
        (_approval_packet(coverage="SPEC-OTHER"), "does not cover the amendment"),
    ]
    for index, (approval_packet, expected) in enumerate(cases, start=1):
        bridge_id = f"pauth-amendment-{index}"
        packet_path.write_text(json.dumps(approval_packet), encoding="utf-8")
        _write_bridge(tmp_path, bridge_id, _pauth_amendment_content(f"Owner evidence: {rel_path}"))

        packet = preflight.build_packet(
            bridge_id=bridge_id,
            bridge_dir=tmp_path / "bridge",
            config_path=config,
            db_path=db_path,
        )

        assert packet["preflight_passed"] is False
        assert expected in packet["blocking_errors"][0]


def test_preflight_treats_unrelated_json_with_amendment_constraint_as_non_applicable(
    tmp_path: Path,
) -> None:
    """Citing the PAUTH-amendment constraint with unrelated JSON is non-blocking.

    WI-5408 regression: the prior duplicate validator treated any JSON object
    alongside a literal mention of the governing amendment DCL as a structured
    replacement envelope, falsely requiring owner evidence and blocking the
    proposal. The canonical validator returns None for content with no actual
    structured replacement envelope, so the thin adapter must report no
    blocking error even when unrelated JSON evidence is present.
    """
    bridge_id = "pauth-amendment-unrelated-json"
    content = (
        "# Proposal\n\n"
        'target_paths: ["scripts/bridge_applicability_preflight.py"]\n\n'
        "## Specification Links\n\n"
        "- DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001\n\n"
        '```json\n{"unrelated": "evidence", "foo": 1}\n```\n'
    )
    _write_bridge(tmp_path, bridge_id, content)
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = _write_pauth_db(tmp_path)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )

    assert packet["blocking_errors"] == []
    assert packet["preflight_passed"] is True


def test_preflight_flags_missing_required_cross_cutting_spec(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
    assert packet["missing_advisory_specs"] == []
    assert packet["packet_hash"].startswith("sha256:")


def test_preflight_passes_when_required_spec_is_cited(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["missing_advisory_specs"] == []


def test_preflight_resolves_versioned_bridge_files_when_index_is_absent(tmp_path: Path) -> None:
    bridge_id = "application-move"
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / f"{bridge_id}-001.md").write_text(
        """
NEW

# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=bridge,
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["content_source"]["mode"] == "bridge_file_operative"
    assert packet["operative_version"]["path"] == f"bridge/{bridge_id}-001.md"
    assert packet["preflight_passed"] is True


def test_preflight_content_file_uses_pending_content(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    pending = tmp_path / "pending.md"
    pending.write_text(
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=pending,
    )

    assert packet["content_source"]["mode"] == "pending_content"
    assert packet["operative_version"]["path"] == f"bridge/{bridge_id}-001.md"
    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]


def test_preflight_content_file_passes_for_pending_compliant_content(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
    )
    pending = tmp_path / "pending.md"
    pending.write_text(
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=pending,
    )

    assert packet["content_source"]["mode"] == "pending_content"
    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["missing_advisory_specs"] == []


def test_preflight_cli_derives_bridge_id_from_content_file_document(tmp_path: Path, capsys) -> None:
    pending = tmp_path / "pending.md"
    pending.write_text(
        """
NEW

Document: application-move

# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    rc = preflight.main(
        [
            "--content-file",
            str(pending),
            "--bridge-dir",
            str(tmp_path / "missing-bridge"),
            "--config",
            str(config),
            "--db",
            str(tmp_path / "missing.db"),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    packet = json.loads(captured.out)
    assert rc == 0
    assert packet["bridge_document_name"] == "application-move"
    assert packet["content_source"]["mode"] == "pending_content"
    assert packet["operative_version"] is None


def test_withdrawn_status_is_parsed_as_terminal_operative_version(tmp_path: Path) -> None:
    bridge_id = "retired-thread"
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / f"{bridge_id}-001.md").write_text(
        """
NEW

# Old Review

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    (bridge / f"{bridge_id}-002.md").write_text(
        """
WITHDRAWN

# Supersession Notice

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    (bridge / "INDEX.md").write_text(
        "\n".join(
            [
                "# Bridge Index",
                "",
                f"Document: {bridge_id}",
                f"WITHDRAWN: bridge/{bridge_id}-002.md",
                f"NEW: bridge/{bridge_id}-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=bridge,
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["operative_version"]["status"] == "WITHDRAWN"
    assert packet["operative_version"]["path"] == f"bridge/{bridge_id}-002.md"
    assert packet["preflight_passed"] is True


def test_corrected_go_after_no_action_is_operative_and_packet_hash_is_stable(tmp_path: Path) -> None:
    bridge_id = "corrected-go"
    _write_bridge_version(
        tmp_path,
        bridge_id,
        1,
        "NEW",
        'target_paths: ["applications/Agent_Red/src/app.py"]\n\n'
        "## Specification Links\n\n- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n",
    )
    _write_bridge_version(tmp_path, bridge_id, 2, "NO-ACTION", "# Dependency hold\n")
    _write_bridge_version(
        tmp_path,
        bridge_id,
        3,
        "GO",
        f"Responds to: bridge/{bridge_id}-002.md\n"
        f"Approved proposal: bridge/{bridge_id}-001.md\n\n"
        'target_paths: ["applications/Agent_Red/src/app.py"]\n\n'
        "## Specification Links\n\n- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    first = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    second = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert first["operative_version"]["path"] == f"bridge/{bridge_id}-003.md"
    assert first["preflight_passed"] is True
    assert first["packet_hash"] == second["packet_hash"]


def test_latest_verified_after_no_action_is_operative_when_metadata_links_chain(tmp_path: Path) -> None:
    bridge_id = "verified-correction"
    _write_bridge_version(tmp_path, bridge_id, 1, "NEW", "# Proposal\n")
    _write_bridge_version(tmp_path, bridge_id, 2, "NO-ACTION", "# Failed start\n")
    _write_bridge_version(
        tmp_path,
        bridge_id,
        3,
        "VERIFIED",
        f"Verified: bridge/{bridge_id}-001.md\n\n## Specification Links\n",
    )

    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", bridge_id)

    assert preflight.choose_operative_version(versions).version_number == 3


def test_latest_standalone_no_action_remains_operative(tmp_path: Path) -> None:
    bridge_id = "standalone-no-action"
    _write_bridge_version(tmp_path, bridge_id, 1, "NEW", "# Proposal\n")
    _write_bridge_version(tmp_path, bridge_id, 2, "NO-ACTION", "# Dependency hold\n")

    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", bridge_id)

    operative = preflight.choose_operative_version(versions)
    assert operative.status == "NO-ACTION"
    assert operative.version_number == 2


def test_markdown_output_contains_hook_readable_clean_fields(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    markdown = preflight.format_markdown(packet)

    assert "## Applicability Preflight" in markdown
    assert "packet_hash: `sha256:" in markdown
    assert "missing_required_specs: []" in markdown


# W4 IP-1 (gtkb-s358-w4-enforcement-calibration, WI-3368): the content-scan
# pass of extract_target_paths is anchored to an enumerated repo-directory set
# so prose word/word tokens are not harvested as repository paths.


def test_preflight_prose_slash_not_harvested() -> None:
    """W4 IP-1 (false-positive removed): prose ``word/word`` tokens (GO/NO-GO,
    and/or, read/write) are not harvested as repository paths -- the anchored
    PATH_TOKEN_RE requires an enumerated repo-directory prefix.
    """
    content = (
        "# Proposal\n\n"
        "This proposal discusses GO/NO-GO discipline, prime-builder/loyal-opposition\n"
        "roles, read/write semantics, and and/or phrasing.\n"
    )
    harvested = preflight.extract_target_paths(content)
    assert harvested == set(), f"prose word/word tokens were harvested as paths: {sorted(harvested)}"


def test_preflight_declared_and_rooted_paths_still_harvested() -> None:
    """W4 IP-1 (genuine-positive preserved): declared ``target_paths`` entries
    and repo-rooted path mentions in prose are still harvested, so every
    genuine path-keyed applicability rule still triggers (relevance closure
    preserved per DCL-SPEC-RELEVANCE-CLOSURE-001).
    """
    content = (
        "# Proposal\n\n"
        'target_paths: ["scripts/foo.py"]\n\n'
        "The change also touches config/governance/sample.toml as described.\n"
    )
    harvested = preflight.extract_target_paths(content)
    assert "scripts/foo.py" in harvested, f"declared target_paths entry not harvested: {sorted(harvested)}"
    assert "config/governance/sample.toml" in harvested, f"repo-rooted path mention not harvested: {sorted(harvested)}"


def test_declared_target_paths_exclude_incidental_applicability_evidence() -> None:
    content = (
        "# Proposal\n\n"
        'target_paths: ["scripts/foo.py"]\n\n'
        "The review cites config/governance/sample.toml as applicability evidence only.\n"
    )

    assert preflight.extract_declared_target_paths(content) == {"scripts/foo.py"}
    assert preflight.extract_target_paths(content) == {
        "config/governance/sample.toml",
        "scripts/foo.py",
    }


def test_packet_separates_declared_scope_from_applicability_path_evidence(tmp_path: Path) -> None:
    bridge_id = "declared-scope"
    (tmp_path / "scripts").mkdir()
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["scripts/foo.py"]

The review cites config/governance/sample.toml as applicability evidence only.

## Specification Links

- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    config.write_text(
        """
[[rules]]
spec_id = "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"
severity = "blocking"
rationale = "Config path evidence must still trigger applicability."
applies_when_paths_match = ["config/**"]
""",
        encoding="utf-8",
    )

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    markdown = preflight.format_markdown(packet)

    assert packet["preflight_passed"] is True
    assert packet["target_paths"] == ["scripts/foo.py"]
    assert packet["declared_target_paths"] == ["scripts/foo.py"]
    assert packet["applicability_path_evidence"] == [
        "config/governance/sample.toml",
        "scripts/foo.py",
    ]
    assert "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001" in packet["applicable_specs"]
    assert packet["warnings"]["missing_parent_dirs"] == []
    assert 'declared_target_paths: ["scripts/foo.py"]' in markdown
    assert "applicability_path_evidence:" in markdown
    assert "config/governance/sample.toml" in markdown


# WI-4542: SPEC_LINK_HEADING_RE was `$`-anchored immediately after the optional
# ` links?`/` references?` suffix, so a trailing qualifier (e.g.
# `## Specification Links (carried forward)`) failed to match and
# extract_spec_links returned an empty set -- the pre-filing gate then
# hard-blocked the Write with a misleading missing_required_specs list. The fix
# tolerates separator-introduced qualifiers and adds an advisory diagnostic that
# distinguishes an unrecognized heading from a genuinely-empty section, WITHOUT
# changing preflight_passed.


def test_extract_spec_links_tolerates_trailing_qualifier_headings() -> None:
    """WI-4542: separator-introduced trailing qualifiers (parenthetical, colon,
    en-dash, em-dash, hyphen) on the spec-links heading are tolerated and the
    cited spec id is harvested (the unfixed regex returned an empty set).
    """
    for heading in (
        "## Specification Links (carried forward)",
        "## Specification References (updated)",
        "## Specification Links: carried forward",
        "## Specification Links — inherited",  # em-dash
        "## Specification Links – inherited",  # en-dash
        "## Specification Links - inherited",  # hyphen
    ):
        content = f"# Proposal\n\n{heading}\n\n- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n"
        harvested = preflight.extract_spec_links(content)
        assert "ADR-ISOLATION-APPLICATION-PLACEMENT-001" in harvested, (
            f"qualifier heading not harvested: {heading!r} -> {sorted(harvested)}"
        )


def test_extract_spec_links_preserves_canonical_and_bare_headings() -> None:
    """WI-4542: the widening preserves prior behavior -- canonical, bare, and
    prefixed `specification` headings still match exactly as before.
    """
    for heading in (
        "## Specification Links",
        "## Specification",
        "## Relevant Specification Links",
        "## Governing Specification References",
    ):
        content = f"# Proposal\n\n{heading}\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        assert "GOV-FILE-BRIDGE-AUTHORITY-001" in preflight.extract_spec_links(content), heading


def test_extract_spec_links_does_not_over_harvest_unrelated_heading() -> None:
    """WI-4542 no-over-harvest guard: a heading that starts with 'Specification'
    but is not a links section (bare trailing words, no separator) is NOT
    treated as the spec-links section, so spec-shaped tokens under it are not
    harvested.
    """
    content = "# Proposal\n\n## Specification Format Guide\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    assert preflight.extract_spec_links(content) == set()


def test_spec_link_heading_rejects_bare_hyphen_compound_headings() -> None:
    """WI-5330: a compound heading is not a spec-links qualifier heading."""
    for heading in (
        "## Specification-Derived Verification Plan",
        "## Specification-Driven Design Notes",
    ):
        assert preflight.SPEC_LINK_HEADING_RE.match(heading) is None


def test_extract_spec_links_skips_compound_heading_before_real_section() -> None:
    """WI-5330: harvesting reaches the real section after a compound heading."""
    content = """# Proposal

## Specification-Derived Verification Plan

- SPEC-WRONG-SECTION

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
"""

    assert preflight.extract_spec_links(content) == {"GOV-FILE-BRIDGE-AUTHORITY-001"}


def test_classify_spec_links_section_distinguishes_statuses() -> None:
    """WI-4542 advisory diagnostic: classify distinguishes harvested /
    section_empty / heading_unrecognized (with the offending heading) /
    no_section.
    """
    harvested = preflight.classify_spec_links_section(
        "# P\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    assert harvested["status"] == "harvested"
    assert harvested["candidate_heading"] is None

    empty = preflight.classify_spec_links_section("# P\n\n## Specification Links\n\n(none yet)\n")
    assert empty["status"] == "section_empty"

    unrecognized = preflight.classify_spec_links_section(
        "# P\n\n## Carried-Forward Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    assert unrecognized["status"] == "heading_unrecognized"
    assert unrecognized["candidate_heading"] == "## Carried-Forward Specification Links"


def test_strip_code_fences_ignores_prose_marker_line():
    """WI-4838 prose-wrap: a line that is a fence marker followed by multiple prose
    words is NOT treated as a fence opener; following prose is preserved for scanning."""
    lines = [
        "before prose",
        "``` describes the fence format and more words",
        "SPEC-TRIGGER prose that must remain scannable",
    ]
    out = preflight._strip_code_fences(lines)
    assert out[0] == "before prose"
    assert out[1] == "``` describes the fence format and more words"
    assert out[2] == "SPEC-TRIGGER prose that must remain scannable"


def test_strip_code_fences_inner_marker_does_not_close():
    """WI-4838 inner-marker: inside a fence, a marker-plus-language line does NOT close
    the fence; only a bare matched closer ends it."""
    lines = [
        "intro prose",
        "```",
        "code line one",
        "```python",
        "code line two",
        "```",
        "outro prose",
    ]
    out = preflight._strip_code_fences(lines)
    assert out[0] == "intro prose"
    assert out[1] == ""  # opener blanked
    assert out[2] == ""  # interior
    assert out[3] == ""  # inner ```python is interior, not a closer
    assert out[4] == ""  # interior
    assert out[5] == ""  # bare closer blanked
    assert out[6] == "outro prose"


def test_strip_code_fences_strips_paired_block():
    """No regression: a normal opener/interior/bare-closer block is blanked and the
    surrounding prose is preserved."""
    lines = ["alpha", "```", "secret code", "```", "omega"]
    out = preflight._strip_code_fences(lines)
    assert out == ["alpha", "", "", "", "omega"]


def test_strip_code_fences_opener_with_single_info_token():
    """A marker run plus a single language token is a valid opener."""
    lines = ["pre", "```python", "x = 1", "```", "post"]
    out = preflight._strip_code_fences(lines)
    assert out == ["pre", "", "", "", "post"]


def test_strip_code_fences_closer_must_match_char_and_length():
    """A closer must be the same fence char and at least the opener length; a shorter run
    or a different fence char does not close the fence."""
    lines = ["pre", "````", "inside", "```", "still inside", "~~~", "still", "````", "after"]
    out = preflight._strip_code_fences(lines)
    assert out[0] == "pre"
    assert out[1] == ""  # 4-backtick opener
    assert out[2] == ""  # inside
    assert out[3] == ""  # 3-backtick line is shorter than opener -> interior, not a closer
    assert out[4] == ""  # still inside
    assert out[5] == ""  # ~~~ is a different fence char -> interior, not a closer
    assert out[6] == ""  # still
    assert out[7] == ""  # 4-backtick bare closer -> closes
    assert out[8] == "after"

    absent = preflight.classify_spec_links_section("# P\n\nNo spec links section here.\n")
    assert absent["status"] == "no_section"


def test_preflight_passes_with_carried_forward_qualifier_heading(tmp_path: Path) -> None:
    """WI-4542 end-to-end: a required cross-cutting spec cited under
    `## Specification Links (carried forward)` now passes the gate (the bug
    previously hard-blocked it with a misleading missing_required_specs).
    """
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links (carried forward)

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["warnings"]["spec_links_section"]["status"] == "harvested"


def test_preflight_unrecognized_heading_surfaces_diagnostic_without_relaxing_gate(tmp_path: Path) -> None:
    """WI-4542: a prefix-form spec-links heading the STRICT regex rejects keeps
    the gate FAILING (harvesting stays strict) AND surfaces the advisory
    heading_unrecognized diagnostic -- proving the diagnostic does not weaken
    enforcement.
    """
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Carried-Forward Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    packet = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
    diag = packet["warnings"]["spec_links_section"]
    assert diag["status"] == "heading_unrecognized"
    assert diag["candidate_heading"] == "## Carried-Forward Specification Links"


def test_schema_v3_hash_is_stable_across_db_invocation_and_filesystem(tmp_path: Path) -> None:
    bridge_id = "stable-packet"
    target_path = "applications/missing/src/app.py"
    _write_bridge(
        tmp_path,
        bridge_id,
        f"""
# Proposal

WI-5441

target_paths: ["{target_path}"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
    )
    source = tmp_path / "bridge" / f"{bridge_id}-001.md"
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE current_specifications (id TEXT PRIMARY KEY, title TEXT, status TEXT, type TEXT)")
        conn.execute(
            "INSERT INTO current_specifications VALUES (?, ?, ?, ?)",
            (
                "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
                "Environment-only title",
                "specified",
                "architecture_decision",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    live = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
    )
    explicit = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=db_path,
        content_file=source,
    )
    no_db = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )

    assert live["packet_hash_schema_version"] == 3
    assert set(live["packet_hash_material"]) == preflight.PACKET_HASH_MATERIAL_KEYS
    assert live["source_identity"] == {
        "path": f"bridge/{bridge_id}-001.md",
        "status": "NEW",
        "version_number": 1,
    }
    assert live["packet_hash"] == explicit["packet_hash"] == no_db["packet_hash"]
    assert live["content_source"]["mode"] != explicit["content_source"]["mode"]
    assert live["applicable_specs"]["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]["exists_in_membase"] is True
    assert no_db["applicable_specs"]["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]["exists_in_membase"] is None
    assert set(live["packet_hash_material"]["applicable_specs"]["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]) == {
        "spec_id",
        "severity",
        "rationale",
        "matched_by",
    }
    assert live["warnings"]["missing_parent_dirs"]

    (tmp_path / "applications" / "missing" / "src").mkdir(parents=True)
    parent_present = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )

    assert parent_present["warnings"]["missing_parent_dirs"] == []
    assert parent_present["packet_hash"] == live["packet_hash"]


def test_schema_v3_hash_excludes_blocking_diagnostics_but_preserves_rejection(
    tmp_path: Path,
    monkeypatch,
) -> None:
    bridge_id = "diagnostic-boundary"
    _write_bridge(tmp_path, bridge_id, "# Proposal\n")
    source = tmp_path / "bridge" / f"{bridge_id}-001.md"
    config = tmp_path / "spec-applicability.toml"
    config.write_text("rules = []\n", encoding="utf-8")

    monkeypatch.setattr(preflight, "_pauth_amendment_blocking_errors", lambda *args: [])
    accepted = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    monkeypatch.setattr(
        preflight,
        "_pauth_amendment_blocking_errors",
        lambda *args: ["environment-dependent PAUTH denial"],
    )
    rejected = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )

    assert accepted["preflight_passed"] is True
    assert rejected["preflight_passed"] is False
    assert rejected["blocking_errors"] == ["environment-dependent PAUTH denial"]
    assert rejected["packet_hash"] == accepted["packet_hash"]


def test_explicit_canonical_source_ignores_newer_siblings_and_rejects_mismatch(
    tmp_path: Path,
) -> None:
    bridge_id = "canonical-source"
    _write_bridge(tmp_path, bridge_id, "# Proposal\n")
    source = tmp_path / "bridge" / f"{bridge_id}-001.md"
    config = tmp_path / "spec-applicability.toml"
    config.write_text("rules = []\n", encoding="utf-8")

    default = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
    )
    explicit = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    assert explicit["packet_hash"] == default["packet_hash"]

    _write_bridge_version(tmp_path, bridge_id, 2, "REVISED", "# Later revision\n")
    explicit_after_sibling = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    latest_default = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
    )
    assert explicit_after_sibling["source_identity"]["version_number"] == 1
    assert explicit_after_sibling["packet_hash"] == explicit["packet_hash"]
    assert latest_default["source_identity"]["version_number"] == 2
    assert latest_default["packet_hash"] != explicit["packet_hash"]

    wrong_thread = tmp_path / "bridge" / "different-source-001.md"
    wrong_thread.write_text("NEW\n# Wrong thread\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="belongs to another bridge thread"):
        preflight.build_packet(
            bridge_id=bridge_id,
            bridge_dir=tmp_path / "bridge",
            config_path=config,
            db_path=tmp_path / "absent.db",
            content_file=wrong_thread,
        )

    bom_source = tmp_path / "bridge" / f"{bridge_id}-003.md"
    bom_source.write_bytes(b"\xef\xbb\xbfNEW\n# BOM source\n")
    with pytest.raises(SystemExit, match="recognized first-line status"):
        preflight.build_packet(
            bridge_id=bridge_id,
            bridge_dir=tmp_path / "bridge",
            config_path=config,
            db_path=tmp_path / "absent.db",
            content_file=bom_source,
        )


def test_schema_v3_hash_tracks_source_and_rules_bytes_with_lf_normalization(tmp_path: Path) -> None:
    bridge_id = "mutation-sensitive"
    _write_bridge(tmp_path, bridge_id, "# Proposal\n\nWI-5441\n")
    source = tmp_path / "bridge" / f"{bridge_id}-001.md"
    config = tmp_path / "spec-applicability.toml"
    config.write_text("rules = []\n", encoding="utf-8")
    original = source.read_text(encoding="utf-8")

    baseline = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    source.write_bytes(original.replace("\n", "\r\n").encode("utf-8"))
    crlf = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    assert crlf["source_content_hash"] == baseline["source_content_hash"]
    assert crlf["packet_hash"] == baseline["packet_hash"]

    source.write_text(original + "\nSource mutation.\n", encoding="utf-8")
    source_changed = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    assert source_changed["source_content_hash"] != baseline["source_content_hash"]
    assert source_changed["packet_hash"] != baseline["packet_hash"]

    source.write_text(original, encoding="utf-8")
    config.write_text("rules = []\n# tracked rules mutation\n", encoding="utf-8")
    rules_changed = preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "absent.db",
        content_file=source,
    )
    assert rules_changed["rules_content_hash"] != baseline["rules_content_hash"]
    assert rules_changed["packet_hash"] != baseline["packet_hash"]


def _verdict_preparation_fixture(tmp_path: Path) -> tuple[Path, Path, Path, str]:
    bridge = tmp_path / "bridge"
    config = tmp_path / "config" / "governance" / "spec-applicability.toml"
    bridge.mkdir(parents=True)
    config.parent.mkdir(parents=True)
    config.write_text("rules = []\n", encoding="utf-8")
    source = bridge / "prepare-topic-001.md"
    source.write_text(
        "NEW\nbridge_kind: prime_proposal\nDocument: prepare-topic\nVersion: 001\n"
        'target_paths: ["scripts/example.py"]\n',
        encoding="utf-8",
    )
    draft = tmp_path / "candidate.md"
    content = (
        "GO\nbridge_kind: lo_verdict\nDocument: prepare-topic\nVersion: 002\n"
        "Responds to: bridge/prepare-topic-001.md\n\n"
        "## Applicability Preflight\n\n"
        "- packet_hash: `sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`\n"
        "- missing_required_specs: []\n\n"
        "## Findings\n\nFresh review.\n"
    )
    draft.write_text(content, encoding="utf-8")
    return source, config, draft, content


def test_prepare_verdict_candidate_rebuilds_exact_source_and_final_byte_hash(tmp_path: Path) -> None:
    _source, config, _draft, content = _verdict_preparation_fixture(tmp_path)

    prepared = preflight.prepare_verdict_candidate(
        candidate_path="bridge/prepare-topic-002.md",
        content=content,
        project_root=tmp_path,
        config_path=config,
        db_path=tmp_path / "absent.db",
    )

    assert "sha256:aaaaaaaa" not in prepared
    assert "- content_file: `bridge/prepare-topic-001.md`" in prepared
    assert "## Findings\n\nFresh review." in prepared
    assert prepared.count("## Applicability Preflight") == 1
    assert preflight.CANDIDATE_EVIDENCE_HASH_SENTINEL not in prepared
    embedded = preflight.CANDIDATE_EVIDENCE_HASH_LINE_RE.search(prepared)
    assert embedded is not None
    assert embedded.group("value") == preflight.candidate_evidence_hash(
        "bridge/prepare-topic-002.md",
        prepared,
        tmp_path,
    )
    assert preflight.candidate_evidence_hash(
        "bridge/prepare-topic-002.md",
        prepared + "x",
        tmp_path,
    ) != embedded.group("value")


def test_prepare_verdict_candidate_fails_closed_on_wrong_thread_or_duplicate_section(tmp_path: Path) -> None:
    _source, config, _draft, content = _verdict_preparation_fixture(tmp_path)

    with pytest.raises(preflight.VerdictCandidatePreparationError, match="must belong to the candidate bridge thread"):
        preflight.prepare_verdict_candidate(
            candidate_path="bridge/other-topic-002.md",
            content=content,
            project_root=tmp_path,
            config_path=config,
            db_path=tmp_path / "absent.db",
        )

    with pytest.raises(preflight.VerdictCandidatePreparationError, match="exactly one Applicability"):
        preflight.prepare_verdict_candidate(
            candidate_path="bridge/prepare-topic-002.md",
            content=content + "\n## Applicability Preflight\n",
            project_root=tmp_path,
            config_path=config,
            db_path=tmp_path / "absent.db",
        )


def test_prepare_verdict_candidate_cli_writes_only_final_bytes_to_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _source, config, draft, _content = _verdict_preparation_fixture(tmp_path)

    result = preflight.main(
        [
            "--prepare-verdict-candidate",
            "--content-file",
            str(draft),
            "--candidate-path",
            "bridge/prepare-topic-002.md",
            "--bridge-dir",
            str(tmp_path / "bridge"),
            "--config",
            str(config),
            "--db",
            str(tmp_path / "absent.db"),
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert captured.out.startswith("GO\n")
    assert "candidate_evidence_hash" in captured.out
    assert "prepared verdict candidate bytes" in captured.err
    assert not (tmp_path / "bridge" / "prepare-topic-002.md").exists()


def _operation_time_envelope(*, allow_bridge: bool = True, forbidden: list[str] | None = None) -> dict[str, object]:
    allowed = ["source", "test_addition"]
    if allow_bridge:
        allowed.append("bridge")
    return {
        "id": "PAUTH-FIXTURE",
        "version": 3,
        "project_id": "PROJECT-FIXTURE",
        "status": "active",
        "allowed_mutation_classes": allowed,
        "forbidden_operations": list(forbidden or []),
        "included_work_item_ids": [],
        "excluded_work_item_ids": [],
        "included_spec_ids": [],
        "excluded_spec_ids": [],
    }


def _install_operation_time_fixture(monkeypatch, envelope: dict[str, object]) -> None:
    taxonomy = preflight._load_operation_taxonomy(REPO_ROOT)
    monkeypatch.setattr(preflight, "_load_operation_taxonomy", lambda _root: taxonomy)
    monkeypatch.setattr(
        preflight,
        "extract_and_validate_project_authorization",
        lambda *_args, **_kwargs: dict(envelope),
    )


def _implementation_content(*, kind: str, version: int, targets: list[str], approved: int | None = None) -> str:
    approved_line = f"Approved proposal: bridge/pauth-phase-{approved:03d}.md\n" if approved is not None else ""
    return (
        "NEW\n"
        f"bridge_kind: {kind}\n"
        "Document: pauth-phase\n"
        f"Version: {version:03d}\n"
        f"{approved_line}"
        "Project Authorization: PAUTH-FIXTURE\n"
        "Project: PROJECT-FIXTURE\n"
        "Work Item: WI-FIXTURE\n"
        f"target_paths: {json.dumps(targets)}\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )


def test_pauth_proposal_allowed_finalization_denied_when_bridge_class_missing(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    (tmp_path / "bridge").mkdir()
    proposal = tmp_path / "proposal.md"
    proposal.write_text(
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/tool.py"]),
        encoding="utf-8",
    )
    _install_operation_time_fixture(monkeypatch, _operation_time_envelope(allow_bridge=False))

    proposal_packet = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=proposal,
    )
    proposal_pauth = proposal_packet["project_authorization_operation_time"]
    assert proposal_pauth["status"] == "allowed"
    assert proposal_pauth["requested_operations"] == ["implementation_packet_create", "implementation_start"]
    assert proposal_pauth["cohort"] == ["scripts/tool.py"]

    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        1,
        "REVISED",
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/tool.py"]),
    )
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        2,
        "GO",
        "Responds to: bridge/pauth-phase-001.md\n\n# Reviewed proposal\n",
    )
    report = tmp_path / "report.md"
    report.write_text(
        _implementation_content(
            kind="implementation_report",
            version=3,
            targets=["platform_tests/test_tool.py"],
            approved=1,
        ),
        encoding="utf-8",
    )
    report_packet = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=report,
    )
    report_pauth = report_packet["project_authorization_operation_time"]
    assert report_pauth["status"] == "denied"
    assert report_pauth["reason_code"] == "target_mutation_class_not_allowed"
    assert report_pauth["cohort"] == [
        "bridge/pauth-phase-001.md",
        "bridge/pauth-phase-002.md",
        "bridge/pauth-phase-003.md",
        "bridge/pauth-phase-004.md",
        "platform_tests/test_tool.py",
        "scripts/tool.py",
    ]
    assert {decision["reason_code"] for decision in report_pauth["decisions"]} == {"target_mutation_class_not_allowed"}
    assert report_packet["preflight_passed"] is False


def test_pauth_phase_cohort_allowed_and_reported(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        1,
        "REVISED",
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/tool.py"]),
    )
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        2,
        "GO",
        "Responds to: bridge/pauth-phase-001.md\n\n# Reviewed proposal\n",
    )
    report = tmp_path / "report.md"
    report.write_text(
        _implementation_content(
            kind="implementation_report",
            version=3,
            targets=["platform_tests/test_tool.py"],
            approved=1,
        ),
        encoding="utf-8",
    )
    _install_operation_time_fixture(monkeypatch, _operation_time_envelope())

    first = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=report,
    )
    second = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=report,
    )
    pauth = first["project_authorization_operation_time"]
    assert pauth["status"] == "allowed"
    assert pauth["authorization_source"] == "bridge/pauth-phase-001.md"
    assert pauth["evaluator_id"]
    assert pauth["taxonomy_sha256"]
    assert first["packet_hash"] == second["packet_hash"]
    assert "Project Authorization Operation-Time Evaluation" in preflight.format_markdown(first)


def test_finalization_binds_cohort_to_go_approved_proposal(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        1,
        "REVISED",
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/approved.py"]),
    )
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        2,
        "GO",
        "Responds to: bridge/pauth-phase-001.md\n\n# Approved v001\n",
    )
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        3,
        "REVISED",
        _implementation_content(kind="prime_proposal", version=3, targets=["config/unapproved.toml"]),
    )
    report = tmp_path / "report.md"
    report.write_text(
        _implementation_content(
            kind="implementation_report",
            version=4,
            targets=["platform_tests/test_approved.py"],
            approved=1,
        ),
        encoding="utf-8",
    )
    _install_operation_time_fixture(monkeypatch, _operation_time_envelope())

    packet = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=report,
    )

    pauth = packet["project_authorization_operation_time"]
    assert pauth["status"] == "allowed"
    assert pauth["authorization_source"] == "bridge/pauth-phase-001.md"
    assert "scripts/approved.py" in pauth["cohort"]
    assert "platform_tests/test_approved.py" in pauth["cohort"]
    assert "config/unapproved.toml" not in pauth["cohort"]


def test_finalization_rejects_proposal_without_matching_go(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    _write_bridge_version(
        tmp_path,
        "pauth-phase",
        1,
        "REVISED",
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/tool.py"]),
    )
    _write_bridge_version(tmp_path, "pauth-phase", 2, "NO-GO", "# Rejected proposal\n")
    report = tmp_path / "report.md"
    report.write_text(
        _implementation_content(
            kind="implementation_report",
            version=3,
            targets=["platform_tests/test_tool.py"],
            approved=1,
        ),
        encoding="utf-8",
    )
    _install_operation_time_fixture(monkeypatch, _operation_time_envelope())

    packet = preflight.build_packet(
        bridge_id="pauth-phase",
        bridge_dir=tmp_path / "bridge",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=report,
    )

    pauth = packet["project_authorization_operation_time"]
    assert pauth["status"] == "error"
    assert pauth["reason_code"] == "approved_proposal_resolution_failed"
    assert "no matching earlier GO verdict" in pauth["error"]
    assert packet["preflight_passed"] is False


def test_pauth_load_or_evaluator_failure_is_distinct_cli_error(tmp_path: Path, monkeypatch, capsys) -> None:
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    (tmp_path / "bridge").mkdir()
    proposal = tmp_path / "proposal.md"
    proposal.write_text(
        _implementation_content(kind="prime_proposal", version=1, targets=["scripts/tool.py"]),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        preflight,
        "extract_and_validate_project_authorization",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(preflight.AuthorizationError("malformed PAUTH fixture")),
    )

    result = preflight.main(
        [
            "--bridge-id",
            "pauth-phase",
            "--content-file",
            str(proposal),
            "--bridge-dir",
            str(tmp_path / "bridge"),
            "--config",
            str(config),
            "--db",
            str(tmp_path / "missing.db"),
            "--json",
        ]
    )
    packet = json.loads(capsys.readouterr().out)
    assert result == 6
    assert packet["project_authorization_operation_time"]["status"] == "error"
    assert "malformed PAUTH fixture" in packet["blocking_errors"][0]


def test_pauth_preflight_matches_canonical_evaluator(tmp_path: Path, monkeypatch) -> None:
    envelope = _operation_time_envelope()
    _install_operation_time_fixture(monkeypatch, envelope)
    cohort = ["bridge/parity-001.md", "scripts/tool.py"]
    decision_time = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)

    projected, errors = preflight._evaluate_pauth_phase(
        content="Project Authorization: PAUTH-FIXTURE\n",
        project_root=tmp_path,
        phase="finalization",
        cohort=cohort,
        cited_specs=set(),
        decision_time=decision_time,
    )
    taxonomy = preflight._load_operation_taxonomy(REPO_ROOT)
    canonical = [
        preflight._evaluate_envelope(
            envelope,
            requested_operation=operation,
            target_paths=cohort,
            decision_time=decision_time,
            taxonomy=taxonomy,
        ).as_dict()
        for operation in preflight.PAUTH_PHASE_OPERATIONS["finalization"]
    ]

    assert errors == []
    assert projected["decisions"] == canonical
    assert projected["allowed"] is all(decision["allowed"] for decision in canonical)
