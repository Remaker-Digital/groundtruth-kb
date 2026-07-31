"""Tests for bridge artifact author/model audit metadata helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import ollama_harness as oh
from scripts import openrouter_harness as orh
from scripts.bridge_author_metadata import (
    CODEX_TURN_METADATA_SOURCE,
    ENV_VAR_HARNESS_NAME,
    FIELD_ENV_NAMES,
    BridgeAuthorMetadataError,
    _dispatch_harness_id_from_run_id,
    _resolve_durable_identity_fields,
    author_metadata_gaps_for_content,
    ensure_author_metadata,
    is_synthetic_session_context_id,
    load_author_metadata,
)

# A complete record for a DIFFERENT harness (Codex / A) than the filing harness
# the registry fixtures resolve (Claude / B). Used as the stale/wrong
# ``current.json`` baseline that the WI-4522 fix must never read.
AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}

# Every environment variable the loader consults, plus the registry-path
# override, derived from the module's own field map so this set stays correct as
# the field/env mapping evolves. The autouse fixture clears all of them so a live
# harness session's env cannot leak into the tests (the dispatch worker that runs
# this suite has GTKB_* set for itself).
_AUTHOR_ENV_VARS = tuple(
    sorted(
        {name for names in FIELD_ENV_NAMES.values() for name in names}
        | {ENV_VAR_HARNESS_NAME, "GTKB_HARNESS_REGISTRY_PATH"}
    )
)

# A single ACTIVE Prime Builder (Claude / B) plus an active Loyal Opposition
# (Codex / A). ``_resolve_durable_identity_fields`` resolves the unambiguous
# active Prime Builder fallback when ``GTKB_HARNESS_NAME`` is unset.
_SINGLE_PB_REGISTRY = [
    {"id": "B", "harness_name": "claude", "role": ["prime-builder"], "status": "active"},
    {"id": "A", "harness_name": "codex", "role": ["loyal-opposition"], "status": "active"},
]

_PB_AND_LO_REGISTRY = [
    {"id": "A", "harness_name": "codex", "role": ["prime-builder"], "status": "active"},
    {"id": "B", "harness_name": "claude", "role": ["loyal-opposition"], "status": "active"},
]

# The four per-session runtime fields a filing harness supplies through its own
# runtime envelope (env). The two durable fields come from the registry, never
# from env, in these fixtures.
_RUNTIME_ENVELOPE = {
    "GTKB_AUTHOR_SESSION_CONTEXT_ID": "2026-06-14T15-26-14Z-prime-builder-B-27f08e",
    "GTKB_AUTHOR_MODEL": "claude-opus-4-8",
    "GTKB_AUTHOR_MODEL_VERSION": "4.8",
    "GTKB_AUTHOR_MODEL_CONFIGURATION": "headless bridge auto-dispatch worker",
}


@pytest.fixture(autouse=True)
def _clear_author_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every test hermetic against the live dispatch session's environment."""
    for name in _AUTHOR_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def _write_registry_projection(project_root: Path, harnesses: list[dict]) -> None:
    """Write a harness-registry projection at the path the loaders read for ``project_root``."""
    registry = project_root / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps({"schema_version": 1, "source_of_truth": "test", "harnesses": harnesses}),
        encoding="utf-8",
    )


def _write_stale_current_json(project_root: Path, metadata: dict) -> None:
    """Write a (deprecated, must-not-be-read) ``current.json`` baseline for another harness."""
    stale = project_root / ".gtkb-state" / "bridge-author-metadata" / "current.json"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text(json.dumps(metadata), encoding="utf-8")


def _write_attested_codex_session(
    project_root: Path,
    session_id: str,
    *,
    status: str = "open",
    model_id: str = "gpt-5.6-sol",
    model_version: str = "gpt-5.6-sol",
    model_configuration: str = "reasoning_effort=xhigh; thread_source=user",
    metadata_source: str = CODEX_TURN_METADATA_SOURCE,
    harness_id: str = "A",
) -> None:
    path = project_root / "harness-state" / "codex" / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "harness_id": harness_id,
                "harness_name": "codex",
                "status": status,
                "role": "prime-builder",
                "role_asserted": "prime-builder",
                "role_resolved": "prime-builder",
                "role_resolution": {
                    "interactive_resolved_role": "prime-builder",
                    "interactive_role_source": "transcript_init_keyword",
                    "authority_mode": "interactive_transcript",
                },
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": session_id,
                    "harness_id": "A",
                    "harness_name": "codex",
                    "role": "prime-builder",
                    "role_resolution_source": "transcript_init_keyword",
                    "dispatch_run_id": None,
                    "issued_at": "2026-07-18T00:00:00Z",
                },
                "model_id": model_id,
                "model_version": model_version,
                "model_configuration": model_configuration,
                "model_metadata_source": metadata_source,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_author_metadata_gaps_for_bridge_artifact() -> None:
    content = "NO-GO\n\n## Findings\n"
    assert author_metadata_gaps_for_content(content) == [
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    ]


def test_ensure_author_metadata_inserts_after_status_line(tmp_path: Path) -> None:
    content = "NEW\n\n# Proposal\n"

    updated = ensure_author_metadata(content, project_root=tmp_path, explicit=AUTHOR_METADATA)

    assert updated.startswith(
        "NEW\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\n# Proposal\n"
    )


def test_ensure_author_metadata_rejects_missing_runtime_source(tmp_path: Path) -> None:
    # No registry under tmp_path, env cleared by the autouse fixture: neither the
    # durable identity nor the runtime envelope resolves, so it fails closed.
    with pytest.raises(BridgeAuthorMetadataError, match="missing or invalid"):
        ensure_author_metadata("GO\n\n## Verdict\n", project_root=tmp_path)


def test_ensure_author_metadata_rejects_placeholder_existing_value(tmp_path: Path) -> None:
    content = (
        "NO-GO\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: unknown\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\n## Findings\n"
    )

    with pytest.raises(BridgeAuthorMetadataError, match="partial or invalid"):
        ensure_author_metadata(content, project_root=tmp_path, explicit=AUTHOR_METADATA)


def test_durable_identity_fields_resolve_from_registry(tmp_path: Path) -> None:
    """The two durable fields resolve per-call from the registry; NEVER the runtime fields."""
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)

    fields = _resolve_durable_identity_fields(tmp_path)

    assert fields == {"author_identity": "prime-builder/claude", "author_harness_id": "B"}
    for runtime_field in (
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    ):
        assert runtime_field not in fields


def test_durable_identity_fields_resolve_single_dispatchable_prime_builder(tmp_path: Path) -> None:
    """Multiple active Prime Builders resolve only when one can receive dispatch."""
    _write_registry_projection(
        tmp_path,
        [
            {
                "id": "A",
                "harness_name": "codex",
                "role": ["prime-builder"],
                "status": "active",
                "can_receive_dispatch": True,
            },
            {
                "id": "B",
                "harness_name": "claude",
                "role": ["prime-builder"],
                "status": "active",
                "can_receive_dispatch": False,
            },
        ],
    )

    fields = _resolve_durable_identity_fields(tmp_path)

    assert fields == {"author_identity": "prime-builder/codex", "author_harness_id": "A"}


def test_dispatch_run_id_parser_handles_realistic_role_tokens() -> None:
    assert _dispatch_harness_id_from_run_id("2026-07-05T07-50-27Z-loyal-opposition-B-54c749") == "B"
    assert _dispatch_harness_id_from_run_id("2026-07-05T22-13-00Z-prime-builder-A-7ad6c6") == "A"
    assert _dispatch_harness_id_from_run_id("2026-07-05T22-13-00Z-acting-prime-builder-E-7ad6c6") == "E"


def test_dispatch_run_id_resolves_durable_identity_when_harness_name_unset(tmp_path: Path) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)

    fields = _resolve_durable_identity_fields(
        tmp_path,
        env={"GTKB_BRIDGE_POLLER_RUN_ID": "2026-07-05T07-50-27Z-loyal-opposition-B-54c749"},
    )

    assert fields == {"author_identity": "loyal-opposition/claude", "author_harness_id": "B"}


def test_load_author_metadata_uses_dispatch_run_id_for_durable_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "2026-07-05T07-50-27Z-loyal-opposition-B-54c749")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "claude-opus-4-8")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "4.8")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "headless bridge auto-dispatch worker")

    result = load_author_metadata(tmp_path)

    assert result == {
        "author_identity": "loyal-opposition/claude",
        "author_harness_id": "B",
        "author_session_context_id": "2026-07-05T07-50-27Z-loyal-opposition-B-54c749",
        "author_model": "claude-opus-4-8",
        "author_model_version": "4.8",
        "author_model_configuration": "headless bridge auto-dispatch worker",
    }


def test_dispatch_run_id_token_role_does_not_override_registry_role(tmp_path: Path) -> None:
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)

    fields = _resolve_durable_identity_fields(
        tmp_path,
        env={"GTKB_BRIDGE_POLLER_RUN_ID": "2026-07-05T07-50-27Z-loyal-opposition-B-54c749"},
    )

    assert fields == {"author_identity": "prime-builder/claude", "author_harness_id": "B"}


def test_malformed_dispatch_run_id_does_not_resolve_harness_suffix(tmp_path: Path) -> None:
    _write_registry_projection(
        tmp_path,
        [{"id": "ABCDEF", "harness_name": "fake", "role": ["loyal-opposition"], "status": "active"}],
    )

    fields = _resolve_durable_identity_fields(
        tmp_path,
        env={"GTKB_BRIDGE_POLLER_RUN_ID": "2026-07-05T07-50-27Z-loyal-opposition-ABCDEF"},
    )

    assert fields == {}


def test_stale_current_json_is_not_read_as_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """S389 regression: a stale shared current.json for another harness is never inherited.

    Replaces the retired ``test_load_author_metadata_uses_project_session_file``,
    which asserted the exact (hazardous) behavior this fix removes — trusting
    ``current.json`` as a complete baseline. This is the spec-first (GOV-06)
    correction of that test's expectation.
    """
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)
    _write_stale_current_json(tmp_path, AUTHOR_METADATA)  # Codex / A — the wrong harness
    for key, value in _RUNTIME_ENVELOPE.items():
        monkeypatch.setenv(key, value)

    result = load_author_metadata(tmp_path)

    assert result["author_identity"] == "prime-builder/claude"
    assert result["author_harness_id"] == "B"
    assert result["author_session_context_id"] == _RUNTIME_ENVELOPE["GTKB_AUTHOR_SESSION_CONTEXT_ID"]
    # None of the stale Codex/A values leak through.
    assert result["author_harness_id"] != "A"
    assert "Codex" not in result["author_identity"]
    assert "session-123" not in result.values()


def test_runtime_envelope_supplies_session_model_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Durable identity (registry) + runtime envelope (env) compose a complete, correct stamp."""
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)
    _write_stale_current_json(tmp_path, AUTHOR_METADATA)  # present-but-ignored
    for key, value in _RUNTIME_ENVELOPE.items():
        monkeypatch.setenv(key, value)

    result = load_author_metadata(tmp_path)

    assert result == {
        "author_identity": "prime-builder/claude",
        "author_harness_id": "B",
        "author_session_context_id": _RUNTIME_ENVELOPE["GTKB_AUTHOR_SESSION_CONTEXT_ID"],
        "author_model": "claude-opus-4-8",
        "author_model_version": "4.8",
        "author_model_configuration": "headless bridge auto-dispatch worker",
    }


def test_exact_session_envelope_supplies_attested_codex_model_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)
    _write_attested_codex_session(tmp_path, "codex-thread-123")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")

    result = load_author_metadata(tmp_path)

    assert result == {
        "author_identity": "codex",
        "author_harness_id": "A",
        "author_session_context_id": "codex-thread-123",
        "author_model": "gpt-5.6-sol",
        "author_model_version": "gpt-5.6-sol",
        "author_model_configuration": "reasoning_effort=xhigh; thread_source=user",
        "author_metadata_source": CODEX_TURN_METADATA_SOURCE,
    }


def test_exact_session_loader_never_uses_shared_current_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)
    _write_attested_codex_session(tmp_path, "other-session")
    shared = tmp_path / "harness-state" / "codex" / "session-envelope.json"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        json.dumps(
            {
                "session_id": "requested-session",
                "harness_id": "A",
                "harness_name": "codex",
                "status": "open",
                "model_id": "shared-wrong-model",
                "model_version": "shared-wrong-model",
                "model_configuration": "shared-wrong-config",
                "model_metadata_source": CODEX_TURN_METADATA_SOURCE,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("CODEX_THREAD_ID", "requested-session")

    with pytest.raises(BridgeAuthorMetadataError, match="missing or invalid"):
        load_author_metadata(tmp_path)


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"status": "closed"}, "requires an open session envelope"),
        ({"model_id": "unknown"}, "missing or invalid"),
        ({"metadata_source": "untrusted-source"}, "not attested"),
        ({"harness_id": "B"}, "mismatched harness identity"),
    ],
)
def test_exact_session_loader_rejects_closed_placeholder_or_untrusted_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, str],
    error: str,
) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)
    _write_attested_codex_session(tmp_path, "codex-thread-123", **overrides)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")

    with pytest.raises(BridgeAuthorMetadataError, match=error):
        load_author_metadata(tmp_path)


def test_environment_model_metadata_precedes_exact_session_envelope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_registry_projection(tmp_path, _PB_AND_LO_REGISTRY)
    _write_attested_codex_session(tmp_path, "codex-thread-123")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "environment-model")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "environment-version")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "environment-config")

    result = load_author_metadata(tmp_path)

    assert result["author_model"] == "environment-model"
    assert result["author_model_version"] == "environment-version"
    assert result["author_model_configuration"] == "environment-config"


def test_dispatch_run_id_wins_for_runtime_session_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run-123")
    monkeypatch.setenv("GTKB_INHERITED_SESSION_ID", "inherited-session-456")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-789")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "runtime-model")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "runtime-version")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "runtime-config")

    result = load_author_metadata(tmp_path)

    assert result["author_session_context_id"] == "dispatch-run-123"


def test_ensure_author_metadata_overrides_static_slug_when_dispatch_env_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = (
        "GO\n"
        "author_identity: OpenRouter Loyal Opposition\n"
        "author_harness_id: F\n"
        "author_session_context_id: openrouter-harness-f\n"
        "author_model: deepseek/fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: OpenRouter harness shim\n"
        "\n## Verdict\n"
    )
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run-123")

    updated = ensure_author_metadata(content, project_root=tmp_path)

    assert "author_session_context_id: dispatch-run-123\n" in updated
    assert "openrouter-harness-f" not in updated


def test_ensure_author_metadata_preserves_complete_real_session_when_dispatch_env_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = (
        "GO\n"
        "author_identity: loyal-opposition/test\n"
        "author_harness_id: T\n"
        "author_session_context_id: real-session-123\n"
        "author_model: model\n"
        "author_model_version: version\n"
        "author_model_configuration: config\n"
        "\n## Verdict\n"
    )
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run-123")

    assert ensure_author_metadata(content, project_root=tmp_path) == content


def test_static_headless_harness_slugs_are_synthetic_session_context_ids() -> None:
    assert is_synthetic_session_context_id("openrouter-harness-f")
    assert is_synthetic_session_context_id("ollama-harness-d")
    assert not is_synthetic_session_context_id("2026-06-30T22-35-51Z-prime-builder-A-e54574")


def test_headless_harness_env_injects_resolved_session_context() -> None:
    openrouter_env = orh.set_author_metadata_env(
        {"GTKB_BRIDGE_POLLER_RUN_ID": "openrouter-dispatch"},
        "deepseek/fixture-model",
        "fixture-model",
        "https://openrouter.test",
    )
    ollama_env = oh.set_author_metadata_env(
        {"GTKB_INHERITED_SESSION_ID": "ollama-inherited"},
        "fixture-model:fixture-version",
        "fixture-version",
        "http://ollama.test",
    )

    assert openrouter_env["GTKB_AUTHOR_SESSION_CONTEXT_ID"] == "openrouter-dispatch"
    assert ollama_env["GTKB_AUTHOR_SESSION_CONTEXT_ID"] == "ollama-inherited"


def test_incomplete_sources_fail_closed_not_wrong_stamp(tmp_path: Path) -> None:
    """Env unset + only durable identity resolvable + stale current.json -> raise, never wrong-stamp."""
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)
    _write_stale_current_json(tmp_path, AUTHOR_METADATA)  # Codex / A

    # The durable resolver supplies only 2 of 6 fields; the four runtime fields
    # have no source (env cleared, no self-authored header), so validation raises
    # rather than inheriting the stale Codex/A baseline.
    with pytest.raises(BridgeAuthorMetadataError, match="missing or invalid"):
        load_author_metadata(tmp_path)

    # The same fail-closed behavior holds at the bridge-write call site.
    with pytest.raises(BridgeAuthorMetadataError, match="missing or invalid"):
        ensure_author_metadata("GO\n\n## Verdict\n", project_root=tmp_path)


def test_explicit_overrides_env_and_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Precedence is explicit > env runtime envelope > durable identity."""
    _write_registry_projection(tmp_path, _SINGLE_PB_REGISTRY)
    for key, value in _RUNTIME_ENVELOPE.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("GTKB_AUTHOR_IDENTITY", "env-identity")  # beats durable "prime-builder/claude"

    result = load_author_metadata(tmp_path, explicit={"author_identity": "explicit-identity"})

    assert result["author_identity"] == "explicit-identity"  # explicit beats env and durable
    assert result["author_harness_id"] == "B"  # durable still fills the field explicit/env omit


def test_embedded_metadata_short_circuit_preserved(tmp_path: Path) -> None:
    """A complete self-authored header is returned unchanged with no identity/env resolution.

    No registry, no env, no current.json: if the short-circuit performed
    resolution it would fail closed; returning the content unchanged proves the
    already-embedded path is preserved (interactive / self-authoring sessions
    are unaffected by the WI-4522 fix).
    """
    content = (
        "GO\n"
        "author_identity: loyal-opposition/codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: ctx-xyz\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: high\n"
        "\n## Verdict\n"
    )

    assert ensure_author_metadata(content, project_root=tmp_path) == content
