"""Tests for the no-index bridge file writer.

The writer only creates status-bearing numbered bridge files. Dispatcher/TAFE
state and helper-level latest-status validation live above this module.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import gtkb_bridge_writer as writer
from scripts.gtkb_bridge_writer import (
    PRIME_STATUSES,
    VALID_STATUSES,
    BridgeConflictError,
    BridgePublicationError,
    BridgeTransitionError,
    publish_lo_verdict,
    write_bridge_file,
)

AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}


def test_write_bridge_file_creates_numbered_file_with_metadata(tmp_path: Path) -> None:
    path = write_bridge_file("docthing", 1, "NEW\n\nhello\n", tmp_path, author_metadata=AUTHOR_METADATA)

    assert path == tmp_path / "bridge" / "docthing-001.md"
    assert path.read_text(encoding="utf-8") == (
        "NEW\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\nhello\n"
    )
    assert not (tmp_path / "bridge" / "INDEX.md").exists()


def test_write_bridge_file_rejects_existing_numbered_file(tmp_path: Path) -> None:
    target = tmp_path / "bridge" / "conflict-001.md"
    target.parent.mkdir()
    target.write_text("NEW\nexisting\n", encoding="utf-8")

    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file("conflict", 1, "NEW\nnew body\n", tmp_path, require_author_metadata=False)

    assert target.read_text(encoding="utf-8") == "NEW\nexisting\n"


def test_write_bridge_file_rejects_non_positive_version(tmp_path: Path) -> None:
    with pytest.raises(BridgeTransitionError, match="version must be positive"):
        write_bridge_file("bad", 0, "NEW\n", tmp_path, require_author_metadata=False)


def test_write_bridge_file_can_skip_author_metadata_for_test_fixtures(tmp_path: Path) -> None:
    path = write_bridge_file("fixture", 2, "GO\n\nfixture body\n", tmp_path, require_author_metadata=False)

    assert path.read_text(encoding="utf-8") == "GO\n\nfixture body\n"


def test_no_action_is_valid_prime_authored_status() -> None:
    assert "NO-ACTION" in VALID_STATUSES
    assert "NO-ACTION" in PRIME_STATUSES


def test_write_bridge_file_rejects_version_in_git_history(tmp_path: Path) -> None:
    """write_bridge_file raises BridgeConflictError when the target version exists in
    git history but is absent from disk (deleted-then-recreate attempt, WI-4740)."""
    try:
        subprocess.run(
            ["git", "init", "--quiet", str(tmp_path)],
            check=True,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=str(tmp_path),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test Runner"],
            cwd=str(tmp_path),
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("git not available in test environment")

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    committed = bridge_dir / "gtkb-history-guard-001.md"
    committed.write_text("GO\n\n# Original verdict\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial bridge file"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )

    # Delete from disk — now committed in history but absent on disk.
    committed.unlink()

    with pytest.raises(BridgeConflictError, match="git history"):
        write_bridge_file(
            "gtkb-history-guard",
            1,
            "NEW\n\n# Recreate attempt - should fail\n",
            project_root=tmp_path,
            require_author_metadata=False,
        )


PROVIDER_METADATA = {
    "author_identity": "Alibaba Cloud Studio H",
    "author_harness_id": "H",
    "author_session_context_id": "dispatch-H-1",
    "author_model": "deepseek-v4-pro",
    "author_model_version": "v4",
    "author_model_configuration": "provider fixture",
}


def _provider_thread(tmp_path: Path, *, bridge_kind: str = "prime_proposal") -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / "provider-thread-001.md").write_text(
        "NEW\n\nbridge_kind: " + bridge_kind + "\nDocument: provider-thread\n",
        encoding="utf-8",
    )


def _provider_go_content(**metadata_overrides: str) -> str:
    metadata = dict(PROVIDER_METADATA)
    metadata.update(metadata_overrides)
    metadata_lines = "".join(f"{key}: {value}\n" for key, value in metadata.items())
    return (
        "GO\n"
        f"{metadata_lines}\n"
        "bridge_kind: lo_verdict\n"
        "Document: provider-thread\n"
        "Version: 002\n"
        "Responds to: bridge/provider-thread-001.md\n\n"
        "## Applicability Preflight\n\n"
        "- missing_required_specs: []\n"
    )


def _prepare_provider_mocks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[tuple[str, str]]:
    released: list[tuple[str, str]] = []
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "loyal-opposition", "harness_id": "H"},
    )
    monkeypatch.setattr(
        writer,
        "_claim_holder",
        lambda *_args, **_kwargs: {"session_id": "dispatch-H-1"},
    )
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: None)
    monkeypatch.setattr(
        writer,
        "_release_claim",
        lambda _root, slug, session_id: released.append((slug, session_id)),
    )
    return released


def test_write_bridge_file_exclusive_create_closes_exists_check_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "bridge/race-002.md"

    def create_racing_target(_target: Path, _root: Path) -> bool:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("GO\n\nracing writer\n", encoding="utf-8")
        return False

    monkeypatch.setattr(writer, "_bridge_file_committed_in_git", create_racing_target)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file(
            "race",
            2,
            _provider_go_content(),
            tmp_path,
            require_author_metadata=False,
        )

    assert target.read_text(encoding="utf-8") == "GO\n\nracing writer\n"


def test_publish_lo_verdict_computes_next_path_and_releases_claim_after_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    released = _prepare_provider_mocks(monkeypatch, tmp_path)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    result = publish_lo_verdict(
        "provider-thread",
        "GO",
        _provider_go_content(),
        tmp_path,
        session_id="dispatch-H-1",
        harness_name="alibaba-cloud-studio",
        author_metadata=PROVIDER_METADATA,
    )

    assert result.verdict_path == "bridge/provider-thread-002.md"
    assert result.claim_released is True
    assert released == [("provider-thread", "dispatch-H-1")]
    assert (tmp_path / result.verdict_path).read_text(encoding="utf-8").startswith("GO\n")


def test_publish_lo_verdict_denies_wrong_role_before_mutation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _provider_thread(tmp_path)
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "prime-builder", "harness_id": "H"},
    )

    with pytest.raises(BridgePublicationError, match="loyal-opposition"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    assert not (tmp_path / "bridge/provider-thread-002.md").exists()


def test_publish_lo_verdict_denies_missing_or_other_session_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "loyal-opposition", "harness_id": "H"},
    )
    monkeypatch.setattr(writer, "_claim_holder", lambda *_args, **_kwargs: None)

    with pytest.raises(BridgePublicationError, match="active claim"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    monkeypatch.setattr(writer, "_claim_holder", lambda *_args, **_kwargs: {"session_id": "dispatch-H-2"})
    with pytest.raises(BridgePublicationError, match="another session"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )


def test_publish_lo_verdict_denies_metadata_conflict_and_post_impl_go(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    _prepare_provider_mocks(monkeypatch, tmp_path)

    with pytest.raises(BridgePublicationError, match="metadata conflict"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(author_model="untrusted-model"),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )


def test_publish_lo_verdict_denies_stale_response_version_and_guard_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    released = _prepare_provider_mocks(monkeypatch, tmp_path)

    stale = _provider_go_content().replace("bridge/provider-thread-001.md", "bridge/provider-thread-000.md")
    with pytest.raises(BridgePublicationError, match="respond to current latest"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            stale,
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    wrong_version = _provider_go_content().replace("Version: 002", "Version: 003")
    with pytest.raises(BridgePublicationError, match="Version must be 002"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            wrong_version,
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    def deny_guard(**_kwargs):
        raise BridgePublicationError("scanner-safe credential denial")

    monkeypatch.setattr(writer, "_run_provider_verdict_guards", deny_guard)
    with pytest.raises(BridgePublicationError, match="credential denial"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    assert not (tmp_path / "bridge/provider-thread-002.md").exists()
    assert released == []

    (tmp_path / "bridge/provider-thread-001.md").write_text(
        "NEW\n\nbridge_kind: implementation_report\nDocument: provider-thread\n",
        encoding="utf-8",
    )
    with pytest.raises(BridgeTransitionError, match="invalid after NEW"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )
