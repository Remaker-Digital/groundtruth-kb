"""Focused tests for the WI-4301 session-envelope runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.session import topic_router
from groundtruth_kb.session.envelope import (
    TOPIC_TYPES,
    EnvelopeError,
    archive_dir,
    close_current_topic,
    close_topic,
    ensure_worker_session,
    load_current,
    open_session,
    open_topic,
    parse_canonical_init_keyword,
    resolve_worker_role_provenance,
    worker_session_envelope_path,
)
from groundtruth_kb.session.topic_router import (
    handle_topic_command,
    parse_topic_command,
    render_topic_context,
)
from groundtruth_kb.session.wrap import is_canonical_wrap_trigger, run_wrap

REPO_ROOT = Path(__file__).resolve().parents[2]


def _seed_harness(root: Path) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"codex": {"id": "A"}},
            }
        ),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]}],
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("keyword", "subject", "role"),
    [
        ("::init gtkb", "gtkb", None),
        ("::init gtkb pb", "gtkb", "prime-builder"),
        ("::init gtkb lo", "gtkb", "loyal-opposition"),
        ("::init application", "application", None),
        ("::init application pb", "application", "prime-builder"),
        ("::init application lo", "application", "loyal-opposition"),
    ],
)
def test_canonical_init_keyword_parser_accepts_exact_six_form_grammar(
    keyword: str,
    subject: str,
    role: str | None,
) -> None:
    assert parse_canonical_init_keyword(keyword) == {"subject": subject, "role": role}


@pytest.mark.parametrize(
    "keyword",
    [
        None,
        "",
        " ::init gtkb pb",
        "::init gtkb pb ",
        "::init  gtkb pb",
        "::init gtkb  pb",
        "::init GTKB pb",
        "::init gtkb prime-builder",
        "::init project pb",
        "::init gtkb pb extra",
        "::init gtkb pb\n",
        "::init gtkb pb\nnext",
    ],
)
def test_canonical_init_keyword_parser_rejects_noncanonical_forms(keyword: str | None) -> None:
    assert parse_canonical_init_keyword(keyword) is None


def test_role_dcl_a6_explicit_role_is_preserved_against_registry_fallback(tmp_path: Path) -> None:
    _seed_harness(tmp_path)

    envelope = open_session(
        tmp_path,
        harness_name="codex",
        init_keyword="::init gtkb pb",
        role="prime-builder",
        active_work_item_id="WI-4301",
    )

    # WI-6067: the envelope is read from the authoritative per-session document;
    # the shared per-harness pointer is no longer written.
    current = worker_session_envelope_path(tmp_path, "codex", envelope["session_id"])
    assert current.is_file()
    saved = json.loads(current.read_text(encoding="utf-8"))
    assert saved["session_id"] == envelope["session_id"]
    assert saved["harness_id"] == "A"
    assert saved["role_asserted"] == "prime-builder"
    assert saved["role_resolved"] == "prime-builder"
    assert saved["role_resolution"]["interactive_resolved_role"] == "prime-builder"
    assert saved["role_resolution"]["interactive_role_source"] == "transcript_init_keyword"
    assert saved["role_resolution"]["durable_registry_role"] == "loyal-opposition"
    assert saved["role_resolution"]["authority_mode"] == "interactive_transcript"
    assert "non-overriding" in saved["role_resolution"]["durable_registry_authority"]
    assert saved["active_work_item_id"] == "WI-4301"


def test_role_dcl_a7_subject_only_startup_uses_source_classified_fallback(tmp_path: Path) -> None:
    _seed_harness(tmp_path)

    envelope = open_session(tmp_path, harness_name="codex", init_keyword="::init gtkb", subject="gtkb")

    saved = json.loads(
        worker_session_envelope_path(tmp_path, "codex", envelope["session_id"]).read_text(encoding="utf-8")
    )
    assert saved["subject_asserted"] == "gtkb"
    assert saved["role_resolved"] == "loyal-opposition"
    assert saved["role_resolution"]["interactive_role_source"] is None
    assert saved["role_resolution"]["durable_registry_role"] == "loyal-opposition"
    assert saved["role_resolution"]["authority_mode"] == "durable_registry_fallback"


def test_role_dcl_a4_worker_bootstrap_precedes_marker_and_lifecycle_loading() -> None:
    """The explicit worker document is established before later startup work."""
    source = (REPO_ROOT / "scripts" / "session_self_initialization.py").read_text(encoding="utf-8")

    worker_bootstrap = source.index("            ensure_worker_session(")
    marker_persistence = source.index("    # Persist interactive role overrides")
    lifecycle_loading = source.index("    lifecycle_guard_path = (")

    assert worker_bootstrap < marker_persistence < lifecycle_loading


def test_topic_open_close_is_strict_and_single_active(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_harness(tmp_path)
    opened = open_session(tmp_path, harness_name="codex")
    monkeypatch.setenv("GTKB_SESSION_ID", opened["session_id"])

    assert set(TOPIC_TYPES) == {"ops", "deliberation", "build", "test", "spec", "project"}

    topic = open_topic(tmp_path, "spec", harness_name="codex")
    assert topic["route_target"] == "spec-governance-service"
    assert topic["preload_state"]["sources"]

    # Single-active (SPEC-TOPIC-ENVELOPE-ROUTER-001 v3 / WI-4685): re-opening
    # supplants the current envelope rather than raising "already open".
    second = open_topic(tmp_path, "spec", harness_name="codex")
    assert second["closed_at"] is None
    envelope = load_current(tmp_path, "codex")
    open_topics = [t for t in envelope["topics"] if t["closed_at"] is None]
    assert len(open_topics) == 1
    assert open_topics[0]["type"] == "spec"
    assert any(t["close_outcome"] == "auto_closed_by_open_supplant" for t in envelope["topics"])

    closed = close_topic(tmp_path, "spec", harness_name="codex")
    assert closed["closed_at"]
    assert closed["close_outcome"] == "closed"


def test_open_topic_closes_current_topic_of_other_type(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    open_topic(tmp_path, "spec", harness_name="codex")
    open_topic(tmp_path, "build", harness_name="codex")

    envelope = load_current(tmp_path, "codex")
    open_topics = [t for t in envelope["topics"] if t["closed_at"] is None]
    assert len(open_topics) == 1
    assert open_topics[0]["type"] == "build"
    spec_topic = next(t for t in envelope["topics"] if t["type"] == "spec")
    assert spec_topic["close_outcome"] == "auto_closed_by_open_supplant"


def test_bare_close_closes_current_topic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_harness(tmp_path)
    opened = open_session(tmp_path, harness_name="codex")
    monkeypatch.setenv("GTKB_SESSION_ID", opened["session_id"])

    open_topic(tmp_path, "build", harness_name="codex")
    closed = close_current_topic(tmp_path, harness_name="codex")
    assert closed is not None
    assert closed["type"] == "build"
    assert closed["close_outcome"] == "closed"

    envelope = load_current(tmp_path, "codex")
    assert [t for t in envelope["topics"] if t["closed_at"] is None] == []


def test_bare_close_is_idempotent_noop_when_nothing_open(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    assert close_current_topic(tmp_path, harness_name="codex") is None
    # Typed close with nothing open is also an idempotent no-op (not an error).
    assert close_topic(tmp_path, "spec", harness_name="codex") is None


def test_typed_close_type_mismatch_is_guidance_error(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    open_topic(tmp_path, "build", harness_name="codex")
    with pytest.raises(EnvelopeError, match="open topic envelope is"):
        close_topic(tmp_path, "spec", harness_name="codex")
    # The build topic remains open after the rejected mismatched close.
    envelope = load_current(tmp_path, "codex")
    assert [t["type"] for t in envelope["topics"] if t["closed_at"] is None] == ["build"]


def test_ops_topic_route_and_preload_are_available(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    topic = open_topic(tmp_path, "ops", harness_name="codex")

    assert topic["route_target"] == "operations-status-decision-service"
    assert topic["preload_state"]["sources"] == [
        "operations_status",
        "support_user_activity",
        "ops_feedback_inputs",
    ]
    # Single-active (WI-4685): re-opening supplants rather than raising.
    second = open_topic(tmp_path, "ops", harness_name="codex")
    assert second["closed_at"] is None
    envelope = load_current(tmp_path, "codex")
    assert len([t for t in envelope["topics"] if t["closed_at"] is None]) == 1


def test_run_wrap_archives_envelope_with_mandatory_step_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_harness(tmp_path)
    opened = open_session(tmp_path, harness_name="codex")
    monkeypatch.setenv("GTKB_SESSION_ID", opened["session_id"])
    open_topic(tmp_path, "test", harness_name="codex")

    result = run_wrap(tmp_path, harness_name="codex", wrap_outcome="canonical_wrap")

    archive_path = result["archive_path"]
    assert archive_path.parent == archive_dir(tmp_path, "codex")
    assert archive_path.is_file()
    assert not (tmp_path / "harness-state" / "codex" / "session-envelope.json").exists()
    archived = json.loads(archive_path.read_text(encoding="utf-8"))
    assert archived["status"] == "closed"
    assert archived["wrap_outcome"] == "canonical_wrap"
    assert {item["step"] for item in archived["wrap_step_results"]} >= {1, 4, 8, 11, 12}
    step_11 = next(item for item in archived["wrap_step_results"] if item["step"] == 11)
    assert step_11["closed_topic_count"] == 1
    assert archived["topics"][0]["close_outcome"] == "auto_closed_by_session_wrap"


def test_wrap_and_topic_command_parsers_are_strict() -> None:
    assert is_canonical_wrap_trigger("::wrap")
    assert is_canonical_wrap_trigger("\n::wrap\nlater text")
    assert not is_canonical_wrap_trigger("::wrap ")
    assert not is_canonical_wrap_trigger("::WRAP")

    assert parse_topic_command("::open spec").topic_type == "spec"  # type: ignore[union-attr]
    assert parse_topic_command("::open ops").topic_type == "ops"  # type: ignore[union-attr]
    assert parse_topic_command("::close ops").action == "close"  # type: ignore[union-attr]
    assert parse_topic_command("\n::close project\nnotes").action == "close"  # type: ignore[union-attr]
    # Bare ::close is recognized (single-active close-current; WI-4685).
    bare_close = parse_topic_command("::close")
    assert bare_close is not None
    assert bare_close.action == "close"
    assert bare_close.topic_type is None
    assert parse_topic_command("\n::close\nnotes").topic_type is None  # type: ignore[union-attr]
    assert parse_topic_command("::open") is None
    assert parse_topic_command("::open  spec") is None
    assert parse_topic_command("::close unknown") is None
    assert parse_topic_command("::close ") is None  # trailing space stays strict


def test_render_topic_context_injects_activity_profile_for_open(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    command = parse_topic_command("::open build")
    assert command is not None

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    assert result["project_root"] == str(tmp_path)
    context = render_topic_context(result)

    assert "## Activity Disposition Profile" in context
    assert "- name: build" in context
    assert "- headless_eligibility: headless_eligible" in context
    assert "- skills: bridge, bridge-propose, verify, kb-work-item, kb-spec" in context
    assert "- terminology: implementation proposal, implementation report, work item" in context
    assert "## Activity Terminology" in context
    assert "## Activity Skill Advisory" in context
    assert "- scenario: activity:build" in context
    assert "- history_state.sources: GO'd bridge proposals, active PAUTH authorizations" in context
    assert "- direction.stance: implement-within-scope" in context
    assert "- direction.guardrails: no implementation without a GO'd bridge proposal" in context
    assert "- direction.manipulates: source files, test files" in context
    assert "## Open Activity Operator Context" in context
    assert "## Ops Activity Status And AUQ Options" not in context


def test_render_topic_context_loads_only_open_activity_payload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TEST-11253: the opened activity shard is composed without unrelated shards."""
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    command = parse_topic_command("::open build")
    assert command is not None

    monkeypatch.setattr(topic_router, "_render_open_operator_context", lambda _result: "")
    monkeypatch.setattr(topic_router, "_render_activity_terminology", lambda _root, _profile: "")

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    context = render_topic_context(result)

    assert "- name: build" in context
    assert "- skills: bridge, bridge-propose, verify, kb-work-item, kb-spec" in context
    assert "- scenario: activity:build" in context
    assert "grill-me-for-clarification" not in context
    assert "decision-capture" not in context
    assert "gtkb-hygiene-investigation" not in context
    assert "activity:deliberation" not in context
    assert "activity:ops" not in context


def test_render_topic_context_does_not_inject_profile_for_close(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    open_topic(tmp_path, "build", harness_name="codex")
    command = parse_topic_command("::close build")
    assert command is not None

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    context = render_topic_context(result)

    assert "`::close build` accepted." in context
    assert "## Activity Disposition Profile" not in context
    assert "## Open Activity Operator Context" not in context


def test_render_topic_context_injects_operator_context_for_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeStartup:
        GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"

        @staticmethod
        def build_startup_model(project_root: Path, *, role_profile: str, fast_hook: bool) -> dict:
            assert project_root == tmp_path.resolve()
            assert role_profile == "prime-builder"
            assert fast_hook is True
            return {
                "workstream_focus": {"current_label": "GT-KB Infrastructure Focus"},
                "session_overlay": {},
            }

        @staticmethod
        def render_active_work_subject(*args, **kwargs) -> str:
            return "- Current work subject is GT-KB Infrastructure Focus."

        @staticmethod
        def _render_session_startup_briefing(model: dict) -> str:
            return "- Operator briefing: compact."

        @staticmethod
        def _render_top_priority_actions_section(model: dict) -> str:
            return "### Top Priority Actions\n\n1. **WI-1**: Synthetic priority (priority: P1)"

    monkeypatch.setattr(topic_router, "_load_startup_module", lambda _root: FakeStartup)
    context = render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "project_root": str(tmp_path),
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )

    assert "## Open Activity Operator Context" in context
    assert (
        "- Dashboard: GroundTruth-KB Project Dashboard: http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
        in context
    )
    assert "### Active Work Subject" in context
    assert "- Current work subject is GT-KB Infrastructure Focus." in context
    assert "### Session Startup Briefing" in context
    assert "- Operator briefing: compact." in context
    assert "### Top Priority Actions" in context
    assert "**WI-1**" in context


def test_render_topic_context_profile_loader_failure_is_non_blocking(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_loader():
        raise topic_router.ActivityProfileError("profile config unavailable")

    monkeypatch.setattr(topic_router, "load_activity_profiles", fail_loader)
    context = render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )

    assert "`::open build` accepted." in context
    assert "## Activity Disposition Profile" in context
    assert "- status: unavailable" in context
    assert "- reason: profile config unavailable" in context


def test_render_topic_context_injects_activity_terminology_definitions(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    glossary_dir = tmp_path / ".claude" / "rules"
    glossary_dir.mkdir(parents=True)
    (glossary_dir / "canonical-terminology.md").write_text(
        "\n".join(
            [
                "### implementation proposal",
                "",
                "**Definition:** Pre-implementation bridge artifact requesting LO review.",
                "",
                "### work item",
                "",
                "**Definition:** A tracked unit of implementation work in MemBase.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    open_session(tmp_path, harness_name="codex")
    command = parse_topic_command("::open build")
    assert command is not None

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    context = render_topic_context(result)

    assert "## Activity Terminology" in context
    assert "**implementation proposal**: Pre-implementation bridge artifact requesting LO review." in context
    assert "**work item**: A tracked unit of implementation work in MemBase." in context
    assert "**deliberation**" not in context


def test_ensure_worker_session_writes_the_document_role_authority(tmp_path: Path) -> None:
    _seed_harness(tmp_path)

    envelope = ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="session-5171",
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="run-5171",
    )
    provenance = resolve_worker_role_provenance(
        tmp_path,
        current_session_id="session-5171",
        harness_name="codex",
    )

    assert envelope["worker_role_provenance"]["role"] == "prime-builder"
    assert provenance["harness_name"] == "codex"
    assert provenance["dispatch_run_id"] == "run-5171"


def test_worker_sessions_keep_distinct_document_role_authority(tmp_path: Path) -> None:
    """A later worker cannot replace an earlier session's authority document."""
    _seed_harness(tmp_path)

    ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="session-one",
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="run-one",
    )
    ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id="session-two",
        role="loyal-opposition",
        role_source="dispatcher_composition",
        dispatch_run_id="run-two",
    )

    assert worker_session_envelope_path(tmp_path, "codex", "session-one").is_file()
    assert worker_session_envelope_path(tmp_path, "codex", "session-two").is_file()
    assert (
        resolve_worker_role_provenance(
            tmp_path,
            current_session_id="session-one",
            harness_name="codex",
        )["role"]
        == "prime-builder"
    )
    assert (
        resolve_worker_role_provenance(
            tmp_path,
            current_session_id="session-two",
            harness_name="codex",
        )["role"]
        == "loyal-opposition"
    )
    # WI-6067: there is no shared "current" designation for a last writer to win.
    # Without an invoking session id no envelope can be proven to belong to the
    # caller, so nothing resolves.
    assert load_current(tmp_path, "codex") is None


def test_wrap_cannot_reach_another_context_envelope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-6067 (supersedes WI-5935 Slice C): cross-context closure is structurally
    impossible rather than merely refused.

    Before the shared-pointer purge, a second context reached the first context's
    envelope through the pointer and ``_assert_fail_closed_single_context`` refused
    the close. The pointer is gone, so context-b cannot observe context-a's envelope
    at all. The guard is retained in code as defense against any future path that
    reintroduces a shared read; this test asserts the structure that now makes it
    unreachable, and additionally that a context with no envelope of its own does not
    silently succeed — per DELIB-20260808-WI6067-GUARD-CONTRACT-READING.
    """
    _seed_harness(tmp_path)
    monkeypatch.setenv("GTKB_SESSION_ID", "context-a")
    open_session(tmp_path, harness_name="codex", session_id="context-a")

    monkeypatch.setenv("GTKB_SESSION_ID", "context-b")
    # context-b cannot observe context-a's envelope through any shared designation
    assert load_current(tmp_path, "codex") is None

    # context-a's document is untouched and still open
    a_doc = json.loads(worker_session_envelope_path(tmp_path, "codex", "context-a").read_text(encoding="utf-8"))
    assert a_doc["session_id"] == "context-a"
    assert a_doc["status"] == "open"

    before = worker_session_envelope_path(tmp_path, "codex", "context-a").read_bytes()
    archives_before = list(archive_dir(tmp_path, "codex").glob("*.json"))
    with pytest.raises(EnvelopeError, match="no open session envelope exists"):
        run_wrap(tmp_path, harness_name="codex")
    assert not worker_session_envelope_path(tmp_path, "codex", "context-b").exists()
    assert list(archive_dir(tmp_path, "codex").glob("*.json")) == archives_before
    assert worker_session_envelope_path(tmp_path, "codex", "context-a").read_bytes() == before


def test_run_wrap_operates_on_per_session_authoritative_document(tmp_path: Path) -> None:
    """WI-5935 Slice C: wrap mutates the per-session document, not the projection."""
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex", session_id="ctx-wrapped")
    result = run_wrap(tmp_path, harness_name="codex", session_id="ctx-wrapped")
    sid = result["session_id"]
    worker_doc = worker_session_envelope_path(tmp_path, "codex", sid)
    assert worker_doc.is_file()
    assert json.loads(worker_doc.read_text(encoding="utf-8"))["status"] == "closed"
    assert not (tmp_path / "harness-state" / "codex" / "session-envelope.json").exists()


def test_gt_session_wrap_cli_fails_closed_on_cross_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5935 Slice D: `gt session wrap` auto-resolves the invoking session-context id
    and fails closed (non-zero exit + diagnostic) on a cross-context wrap."""
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    root = tmp_path / "project"
    root.mkdir()
    (root / "groundtruth.toml").write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}),
        encoding="utf-8",
    )

    runner = CliRunner()
    cfg = ["--config", str(root / "groundtruth.toml")]

    monkeypatch.setenv("CODEX_THREAD_ID", "context-a")
    opened = runner.invoke(
        main,
        [*cfg, "session", "envelope", "open", "--harness-name", "codex", "--init-keyword", "::init gtkb pb"],
    )
    assert opened.exit_code == 0
    assert opened.output.strip() == "context-a"

    monkeypatch.setenv("GTKB_SESSION_ID", "context-b")
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    wrapped = runner.invoke(main, [*cfg, "session", "wrap", "--harness-name", "codex"])
    assert wrapped.exit_code != 0
    assert "no open session envelope exists" in wrapped.output


def test_render_wrap_summary_includes_closing_instruction(tmp_path: Path) -> None:
    """WI-5935 Slice E: the wrap summary carries the closing-instruction footer."""
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex", session_id="wrap-footer")
    result = run_wrap(tmp_path, harness_name="codex", session_id="wrap-footer")
    assert "When you are finished working, close your session envelope by invoking ::wrap." in result["summary"]


def test_startup_disclosure_surfaces_carry_closing_instruction() -> None:
    """WI-5935 Slice E: startup disclosure templates carry the closing instruction."""
    closing = "When you are finished working, close your session envelope by invoking ::wrap."
    surfaces = [
        REPO_ROOT / "config" / "agent-control" / "PRIME-BUILDER-STARTUP-OVERLAY.md",
        REPO_ROOT / "config" / "agent-control" / "LOYAL-OPPOSITION-STARTUP-OVERLAY.md",
        REPO_ROOT / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md",
    ]
    for surface in surfaces:
        assert surface.is_file(), surface
        content = surface.read_text(encoding="utf-8").replace("`", "")
        assert closing in content, surface
