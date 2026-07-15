"""Envelope integration tests for WI-5266 literal resource precedence."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.session.envelope import (
    ensure_worker_session,
    load_current,
    open_session,
    route_prompt_resources,
)


def _seed_harnesses(root: Path) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_name": "codex", "role": ["prime-builder"]}],
            }
        ),
        encoding="utf-8",
    )


def test_interactive_envelope_starts_without_an_inferred_resource(tmp_path: Path) -> None:
    _seed_harnesses(tmp_path)

    envelope = open_session(tmp_path, harness_name="codex", role="prime-builder")

    assert envelope["resource_selection"]["selected_resources"] == []
    assert envelope["resource_contract"]["resources"]["backlog"]["read_route"] == "gt backlog list"


def test_dispatch_provenance_is_the_only_worker_default(tmp_path: Path) -> None:
    _seed_harnesses(tmp_path)

    dispatched = ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="dispatch-5266",
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="run-5266",
    )

    assert dispatched["resource_selection"]["selected_resources"] == ["bridge_queue"]
    assert dispatched["resource_selection"]["selection_authority"] == "dispatch_provenance"
    assert dispatched["resource_selection"]["dispatch_run_id"] == "run-5266"


def test_current_owner_backlog_literal_replaces_dispatch_default(tmp_path: Path) -> None:
    _seed_harnesses(tmp_path)
    ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="dispatch-5266",
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="run-5266",
    )

    selection = route_prompt_resources(
        tmp_path,
        "Process P0/P1 backlog beginning with bridge/TAFE/harness-related items WI-5266",
        harness_name="codex",
    )
    envelope = load_current(tmp_path, "codex")

    assert selection["selected_resources"] == ["backlog"]
    assert envelope is not None
    assert envelope["resource_selection"]["selected_resources"] == ["backlog"]
    assert envelope["resource_selection"]["selection_authority"] == "current_owner_literal"
    assert envelope["work_item_ids"] == ["WI-5266"]
    assert envelope["active_work_item_id"] == "WI-5266"
    assert envelope["role"] == "prime-builder"


def test_topic_words_do_not_mutate_an_interactive_resource_selection(tmp_path: Path) -> None:
    _seed_harnesses(tmp_path)
    open_session(tmp_path, harness_name="codex", role="prime-builder")

    selection = route_prompt_resources(
        tmp_path,
        "Continue bridge work for the TAFE harness",
        harness_name="codex",
    )
    envelope = load_current(tmp_path, "codex")

    assert selection["selected_resources"] == []
    assert envelope is not None
    assert envelope["resource_selection"]["selected_resources"] == []


def test_multiple_prompt_work_items_do_not_invent_one_active_item(tmp_path: Path) -> None:
    _seed_harnesses(tmp_path)
    open_session(tmp_path, harness_name="codex", role="prime-builder")

    route_prompt_resources(
        tmp_path,
        "Compare backlog WI-5266 and WI-5267 with the bridge queue",
        harness_name="codex",
    )
    envelope = load_current(tmp_path, "codex")

    assert envelope is not None
    assert envelope["resource_selection"]["selected_resources"] == ["backlog", "bridge_queue"]
    assert envelope["resource_selection"]["primary_resource"] is None
    assert envelope["work_item_ids"] == ["WI-5266", "WI-5267"]
    assert envelope["active_work_item_id"] is None
