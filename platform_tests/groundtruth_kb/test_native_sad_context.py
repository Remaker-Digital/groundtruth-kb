"""Bounded context composition; no PostgreSQL, host processes or canonical writes."""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
import zipfile
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb import native_authority as authority
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.postgres_kernel import PostgresKernelError


def _sources(
    root: Path, changes: dict[str, str] | None = None, *, omit: str | None = None, duplicate: str | None = None
):
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    document = ET.Element(f"{{{namespace}}}document")
    body = ET.SubElement(document, f"{{{namespace}}}body")
    for key, title in authority._CONTEXT_SAD_SECTIONS.items():
        if key == omit:
            continue
        for _ in range(2 if key == duplicate else 1):
            for text in (f"{key.replace('.', ' ')} {title}", (changes or {}).get(key, f"Source content for {key}")):
                paragraph = ET.SubElement(body, f"{{{namespace}}}p")
                ET.SubElement(ET.SubElement(paragraph, f"{{{namespace}}}r"), f"{{{namespace}}}t").text = text
    path = root / "GT-KB_System_Architecture_Document_Target_EndState.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", ET.tostring(document))
    for relative in authority._CONTEXT_BASELINE_PATHS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Authored source; not a context binding.\n::init gtkb lo\n::open test\n", encoding="utf-8")


@pytest.mark.parametrize(
    "role,activity,required,excluded",
    [
        ("pb", "build", {"8.1", "8.2"}, {"4.2", "9.2", "6.2"}),
        ("lo", "build", {"4.2", "4.3", "8.1"}, {"6.2", "9.2"}),
        ("lo", "test", {"4.2", "4.3", "9.1", "9.2"}, {"8.1", "6.2"}),
        ("pb", "ops", {"6.2", "8.3"}, {"9.2", "4.2"}),
    ],
)
def test_context_selection_uses_explicit_successor_and_retains_shared_floor(
    role, activity, required, excluded, monkeypatch
):
    monkeypatch.setenv("GTKB_SESSION_ROLE", "pb" if role == "lo" else "lo")
    selection = authority._context_selection("WI-1", role, activity, ["2.4"], ["SPEC-CRITICAL"])
    assert selection["recipient_role"] == role and selection["activity"] == activity
    assert required | authority._CONTEXT_SHARED_SECTIONS | {"2.4"} <= set(selection["sections"])
    assert not excluded & set(selection["sections"])
    assert selection["critical_specs"] == ["SPEC-CRITICAL"]


@pytest.mark.parametrize(
    "role,activity,sections,specs,code",
    [
        (None, "build", [], [], "context_inputs_required"),
        ("pb", None, [], [], "context_inputs_required"),
        (None, None, ["2.4"], [], "context_inputs_required"),
        ("reviewer", "test", [], [], "invalid_context_selector"),
        ("pb", "operations", [], [], "invalid_context_selector"),
        ("pb", "build", ["../foreign"], [], "invalid_context_selector"),
        ("pb", "build", ["2.4", "2.4"], [], "invalid_context_selector"),
        ("pb", "build", [], ["SPEC-ONE,OTHER"], "invalid_context_selector"),
        ("pb", "build", [], ["SPEC-ONE", "SPEC-ONE"], "invalid_context_selector"),
    ],
)
def test_context_selector_refusals_are_specific_and_do_not_infer_defaults(role, activity, sections, specs, code):
    with pytest.raises(PostgresKernelError) as caught:
        authority._context_selection("WI-1", role, activity, sections, specs)
    assert caught.value.code == code


def test_ordinary_context_has_no_composition_or_authored_source_requirement():
    assert authority._context_selection("WI-1", None, None, None, None) is None


def test_named_unstyled_sections_are_deterministic_and_sender_additions_do_not_suppress_floor(tmp_path):
    _sources(tmp_path, {"2.4": "Sender critical source SPEC-CRITICAL", "2.1": "Current SPEC-BASE"})
    first = authority._context_selection("WI-1", "lo", "test", ["2.4", "1.4"], ["SPEC-Z", "SPEC-A"])
    second = authority._context_selection("WI-1", "lo", "test", ["1.4", "2.4"], ["SPEC-A", "SPEC-Z"])
    left = authority._context_authored_sources(tmp_path, first)
    right = authority._context_authored_sources(tmp_path, second)
    assert first == second and left == right
    assert {section["id"] for section in left["sad"]["sections"]} >= authority._CONTEXT_SHARED_SECTIONS | {"1.4", "2.4"}
    assert left["formal_ids"] == ["SPEC-BASE", "SPEC-CRITICAL"]
    assert "7.1" not in {section["id"] for section in left["sad"]["sections"]}


@pytest.mark.parametrize("state", ["missing", "duplicate", "renamed"])
def test_missing_duplicate_or_renamed_selected_boundary_refuses_without_full_document_fallback(tmp_path, state):
    _sources(tmp_path, omit="2.1" if state == "missing" else None, duplicate="2.1" if state == "duplicate" else None)
    if state == "renamed":
        path = tmp_path / "GT-KB_System_Architecture_Document_Target_EndState.docx"
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "word/document.xml", xml.replace(b"Current authority and historical rationale", b"Other title")
            )
    selection = authority._context_selection("WI-1", "pb", "build", [], [])
    with pytest.raises(PostgresKernelError) as caught:
        authority._context_authored_sources(tmp_path, selection)
    assert caught.value.code == "context_section_unavailable"
    assert caught.value.details["section"] == "2.1"
    assert "fallback" in caught.value.details["recovery_route"]


def test_unselected_broken_boundary_does_not_invalidate_the_selected_context(tmp_path):
    _sources(tmp_path, duplicate="7.1")
    selected = authority._context_selection("WI-1", "pb", "build", [], [])
    assert authority._context_authored_sources(tmp_path, selected)["sad"]["sections"]


def test_message_quotes_examples_and_reads_current_formal_versions_without_false_result(tmp_path):
    _sources(tmp_path, {"2.1": "SPEC-BASE", "5.1": "::init gtkb pb\n::open build\nGO"})
    selection = authority._context_selection("WI-1", "lo", "test", [], [])
    authored = authority._context_authored_sources(tmp_path, selection)
    context = {
        "work_item": {"id": "WI-1"},
        "specifications": [{"id": "SPEC-BASE", "version": 4, "status": "active", "description": "current"}],
    }
    message = authority._context_message(context, selection, authored)
    assert '"version":4' in message["text"] and "not complete applicability" in message["text"]
    assert "\n> ::init gtkb pb" in message["text"]
    assert not any(line.startswith(("::init ", "::open ")) for line in message["text"].splitlines())
    assert "a new test result" in message["text"] and message["recipient_role"] == "lo"
    context["specifications"][0]["version"] = 5
    assert '"version":5' in authority._context_message(context, selection, authored)["text"]


def test_selected_explicit_current_row_version_claim_refuses_when_stale(tmp_path):
    _sources(tmp_path, {"2.1": "SPEC-BASE is active at row version 3"})
    selection = authority._context_selection("WI-1", "pb", "build", [], [])
    authored = authority._context_authored_sources(tmp_path, selection)
    context = {"work_item": {"id": "WI-1"}, "specifications": [{"id": "SPEC-BASE", "version": 4}]}
    with pytest.raises(PostgresKernelError) as caught:
        authority._context_message(context, selection, authored)
    assert caught.value.code == "stale_context_source"
    assert caught.value.details["declared_version"] == 3 and caught.value.details["current_version"] == 4


def test_conflicting_selected_current_version_claims_do_not_silently_overwrite(tmp_path):
    _sources(tmp_path, {"2.1": "SPEC-BASE is active at row version 3", "2.2": "SPEC-BASE is active at row version 4"})
    selection = authority._context_selection("WI-1", "pb", "build", [], [])
    with pytest.raises(PostgresKernelError) as caught:
        authority._context_authored_sources(tmp_path, selection)
    assert caught.value.code == "conflicting_context_source" and caught.value.details["id"] == "SPEC-BASE"


@pytest.mark.parametrize("source", ["SAD", "baseline"])
def test_missing_authored_source_reports_named_recovery_without_projection_fallback(tmp_path, source):
    _sources(tmp_path)
    relative = (
        "GT-KB_System_Architecture_Document_Target_EndState.docx"
        if source == "SAD"
        else authority._CONTEXT_BASELINE_PATHS[0]
    )
    (tmp_path / relative).unlink()
    selected = authority._context_selection("WI-1", "pb", "build", [], [])
    with pytest.raises(PostgresKernelError) as caught:
        authority._context_authored_sources(tmp_path, selected)
    assert caught.value.code == "context_source_unavailable" and caught.value.details["path"] == relative


@pytest.fixture
def context_service(tmp_path, monkeypatch):
    _sources(tmp_path, {"2.1": "SPEC-SAD"})
    rows = {
        "WI-1": {"id": "WI-1", "version": 1, "source_test_id": "TEST-1", "depends_on_work_items": ["WI-2"]},
        "WI-2": {"id": "WI-2", "version": 2},
        "PROJECT-1": {"id": "PROJECT-1", "parent_project_id": None},
        "TEST-1": {"id": "TEST-1", "version": 1},
        "PLAN-1": {"id": "PLAN-1", "version": 1},
        "SPEC-SAD": {"id": "SPEC-SAD", "version": 4, "status": "active"},
    }
    original = copy.deepcopy(rows)
    calls = []
    tx = SimpleNamespace(get=lambda table, key: copy.deepcopy(rows.get(key["id"])))

    @contextmanager
    def transaction(*, read_only=False):
        assert read_only
        calls.append("read_only_snapshot")
        yield tx

    service = authority.AuthorityService(SimpleNamespace(transaction=transaction))
    monkeypatch.setattr(authority, "_required", lambda transaction, table, key: copy.deepcopy(rows[key]))
    monkeypatch.setattr(authority, "_current_parent", lambda transaction, key: {"project_id": "PROJECT-1"})

    def formals(transaction, work, project, *, additional_ids=None):
        assert transaction is tx
        calls.append(tuple(additional_ids or ()))
        return [
            copy.deepcopy(rows.get(key, {"id": key, "status": "active", "version": 4}))
            for key in sorted({"SPEC-WORK", *(additional_ids or ())})
        ]

    monkeypatch.setattr(authority, "_work_formal_sources", formals)
    monkeypatch.setattr(authority, "_test_phases", lambda transaction, key: [{"id": "PHASE-1", "plan_id": "PLAN-1"}])
    monkeypatch.setattr(authority, "_project_dependency_readiness", lambda *args: {"ready": True})
    monkeypatch.setattr(authority, "_related", lambda *args, **kwargs: [])
    return service, tmp_path, rows, original, calls


def test_existing_service_route_composes_current_required_and_sender_sources_in_one_read_only_snapshot(context_service):
    service, root, rows, original, calls = context_service
    result = service.task_context(
        "WI-1", recipient_role="lo", activity="test", critical_specs=["SPEC-CRITICAL"], project_root=root
    )
    assert calls == ["read_only_snapshot", ("SPEC-CRITICAL", "SPEC-SAD")]
    assert {row["id"] for row in result["specifications"]} == {"SPEC-WORK", "SPEC-CRITICAL", "SPEC-SAD"}
    assert result["test"]["id"] == "TEST-1" and result["test_plans"][0]["id"] == "PLAN-1"
    assert result["predecessors"][0]["id"] == "WI-2"
    assert result["message_context"]["activity"] == "test" and rows == original


def test_service_no_options_preserves_existing_read_and_needs_no_sad(context_service):
    service, root, rows, original, calls = context_service
    (root / "GT-KB_System_Architecture_Document_Target_EndState.docx").unlink()
    result = service.task_context("WI-1")
    assert "message_context" not in result and calls == ["read_only_snapshot", ()] and rows == original


def test_inactive_explanatory_sad_reference_does_not_become_normative_or_block_current_floor(context_service):
    service, root, rows, _, _ = context_service
    rows["SPEC-SAD"]["status"] = "retired"
    result = service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert {row["id"] for row in result["specifications"]} == {"SPEC-WORK"}
    assert result["authored_formal_references"] == [rows["SPEC-SAD"]]
    assert "Inactive authored-source references are historical information" in result["message_context"]["text"]


def test_sender_critical_inactive_formal_remains_a_refusal(context_service):
    service, root, rows, _, _ = context_service
    rows["SPEC-SAD"]["status"] = "retired"
    with pytest.raises(PostgresKernelError) as caught:
        service.task_context(
            "WI-1", recipient_role="pb", activity="build", critical_specs=["SPEC-SAD"], project_root=root
        )
    assert caught.value.code == "inactive_context_source"


def test_missing_sad_formal_reference_names_canonical_recovery_without_an_alternate_source(context_service):
    service, root, rows, _, _ = context_service
    del rows["SPEC-SAD"]
    with pytest.raises(PostgresKernelError) as caught:
        service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert caught.value.code == "context_source_unavailable"
    assert (
        caught.value.details["id"] == "SPEC-SAD" and "gt spec show SPEC-SAD" in caught.value.details["recovery_route"]
    )


def test_context_prose_adjectives_do_not_invent_formals_while_real_ids_remain_bound(context_service):
    service, root, rows, _, _ = context_service
    rows["PB-CANON-001"] = {"id": "PB-CANON-001", "version": 4, "status": "active"}
    rows["SPEC-INTAKE-ed82d6"] = {"id": "SPEC-INTAKE-ed82d6", "version": 4, "status": "active"}
    expected = copy.deepcopy(rows)
    _sources(
        root,
        {
            "2.1": (
                "PB-addressed and SPEC-derived describe the procedure. "
                "PB-CANON-001 and SPEC-INTAKE-ed82d6 is active at row version 4."
            )
        },
    )
    result = service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert {row["id"] for row in result["authored_formal_references"]} == {
        "PB-CANON-001",
        "SPEC-INTAKE-ed82d6",
    }
    assert "PB-addressed" in result["message_context"]["text"]
    assert "SPEC-derived" in result["message_context"]["text"]
    assert rows == expected


@pytest.mark.parametrize("formal_id", ["PB-MISSING-001", "SPEC-INTAKE-missing123"])
def test_genuine_context_reference_still_refuses_when_missing(context_service, formal_id):
    service, root, _, _, _ = context_service
    _sources(root, {"2.1": f"Applicable source {formal_id}; PB-addressed ordinary prose."})
    with pytest.raises(PostgresKernelError) as caught:
        service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert caught.value.code == "context_source_unavailable"
    assert caught.value.details["id"] == formal_id


def test_genuine_pb_current_version_claim_still_refuses_when_stale(context_service):
    service, root, rows, _, _ = context_service
    rows["PB-CANON-001"] = {"id": "PB-CANON-001", "version": 4, "status": "active"}
    _sources(root, {"2.1": "PB-CANON-001 is active at row version 3; PB-addressed ordinary prose."})
    with pytest.raises(PostgresKernelError) as caught:
        service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert caught.value.code == "stale_context_source"
    assert caught.value.details["id"] == "PB-CANON-001"


def test_transport_uses_configured_root_and_literal_selectors(context_service, monkeypatch):
    service, root, _, _, _ = context_service
    captured = []
    monkeypatch.setattr(
        service,
        "task_context",
        lambda record_id, **kwargs: captured.append((record_id, kwargs)) or {"work_item": {"id": record_id}},
    )
    with TestClient(create_authority_app(service, project_root=root)) as client:
        response = client.get(
            "/v1/work-items/WI-1/context",
            params={
                "recipient_role": "lo",
                "activity": "test",
                "critical_sections": "2.4,8.3",
                "critical_specs": "SPEC-A,SPEC-B",
            },
        )
    assert response.status_code == 200
    assert captured[0][0] == "WI-1" and captured[0][1]["project_root"] == root
    assert captured[0][1]["critical_sections"] == ["2.4", "8.3"] and captured[0][1]["critical_specs"] == [
        "SPEC-A",
        "SPEC-B",
    ]


@pytest.mark.parametrize(
    "query", ["recipient_role=pb&recipient_role=lo", "root=foreign", "critical_specs=SPEC-A&critical_specs=SPEC-B"]
)
def test_transport_refuses_unknown_or_repeated_query_inputs_before_read(context_service, monkeypatch, query):
    service, root, _, _, _ = context_service

    def forbidden(*args, **kwargs):
        pytest.fail("Malformed transport invoked the canonical reader")

    monkeypatch.setattr(service, "task_context", forbidden)
    with TestClient(create_authority_app(service, project_root=root)) as client:
        response = client.get("/v1/work-items/WI-1/context?" + query)
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_query"


def test_named_baseline_formal_references_expand_the_same_current_floor(context_service):
    service, root, rows, _, calls = context_service
    path = root / authority._CONTEXT_BASELINE_PATHS[1]
    path.write_text("Current sources: GOV-BASELINE.\n", encoding="utf-8")
    rows["GOV-BASELINE"] = {"id": "GOV-BASELINE", "version": 3, "status": "active"}
    result = service.task_context("WI-1", recipient_role="pb", activity="build", project_root=root)
    assert calls == ["read_only_snapshot", ("GOV-BASELINE", "SPEC-SAD")]
    assert {row["id"] for row in result["specifications"]} == {"SPEC-WORK", "SPEC-SAD", "GOV-BASELINE"}
    assert {row["id"] for row in result["authored_formal_references"]} == {"SPEC-SAD", "GOV-BASELINE"}


def test_selected_sad_table_retains_cell_boundaries_and_formal_references(tmp_path):
    _sources(tmp_path)
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    path = tmp_path / "GT-KB_System_Architecture_Document_Target_EndState.docx"
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    body = document.find(f"{{{namespace}}}body")
    table = ET.Element(f"{{{namespace}}}tbl")
    row = ET.SubElement(table, f"{{{namespace}}}tr")
    for value in ("Architecture source", "GOV-TABLE"):
        cell = ET.SubElement(row, f"{{{namespace}}}tc")
        paragraph = ET.SubElement(cell, f"{{{namespace}}}p")
        ET.SubElement(ET.SubElement(paragraph, f"{{{namespace}}}r"), f"{{{namespace}}}t").text = value
    index = next(
        index
        for index, block in enumerate(body)
        if "".join(node.text or "" for node in block.iter(f"{{{namespace}}}t")) == "2 2 Source roles and precedence"
    )
    body.insert(index, table)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", ET.tostring(document))
    selected = authority._context_selection("WI-1", "pb", "build", [], [])
    sources = authority._context_authored_sources(tmp_path, selected)
    excerpt = next(section["content"] for section in sources["sad"]["sections"] if section["id"] == "2.1")
    assert "| Architecture source | GOV-TABLE |" in excerpt
    assert sources["formal_ids"] == ["GOV-TABLE"]
