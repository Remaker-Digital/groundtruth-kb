"""A harness registration names no role and uses only the contract's placeholders (c123; batch design WP2 2.1, G1).

Roles bind to contexts through the init line (session-bootstrap: a harness, model, queue or environment default cannot
supply a missing role). c121's installed rows still selected roles through ``--skill bridge-review`` and role-named
dispatch tags, inside the free-form ``invocation_surfaces`` that no writer inspected. The writer now refuses each such
form with a 422 before anything is written, and ``harness_invocation.render`` refuses an unknown or unfilled
placeholder.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.harness_invocation import (
    FINDING_INIT_MARKER,
    FINDING_ROLE_KEY,
    FINDING_ROLE_VALUE,
    FINDING_SKILL_SELECTOR,
    FINDING_UNKNOWN_PLACEHOLDER,
    PLACEHOLDERS,
    SAMPLE_VALUES,
    InvocationError,
    render,
    sample_values,
    surface_findings,
)

from platform_tests.groundtruth_kb.native_fixtures import database_contents, files, harness_fields, put
from platform_tests.groundtruth_kb.native_fixtures import native as native

# F's corrected headless template (batch design WP2 2.1 step 3, with 2.2's model and 2.3's bridge target).
CORRECTED_F = {
    "dispatch": {"can_receive_dispatch": True, "dispatch_tags": ["low-cost"], "dispatch_max_items": 1},
    "headless": {
        "argv": [
            "groundtruth-kb/.venv/Scripts/python.exe",
            "scripts/openrouter_harness.py",
            "--init",
            "{{INIT_LINE}}",
            "--bridge-document",
            "{{DOCUMENT}}",
            "--bridge-version",
            "{{VERSION}}",
            "--report",
            "{{REPORT}}",
            "-p",
            "{{PROMPT}}",
            "--model",
            "deepseek-v4-flash",
        ],
        "max_items": 1,
    },
}

ROLE_BEARING = [
    ({"dispatch": {"dispatch_tags": ["low-cost", "loyal-opposition"]}}, FINDING_ROLE_VALUE),
    ({"dispatch": {"dispatch_tags": ["Prime-Builder"]}}, FINDING_ROLE_VALUE),
    ({"headless": {"argv": ["runner", "-p", "{{PROMPT}}", "--skill", "bridge-review"]}}, FINDING_SKILL_SELECTOR),
    ({"headless": {"argv": ["runner", "--skill=verification"]}}, FINDING_SKILL_SELECTOR),
    ({"headless": {"argv": ["runner", "::init gtkb lo"]}}, FINDING_INIT_MARKER),
    ({"private": {"role": "anything"}}, FINDING_ROLE_KEY),
    ({"surfaces": [{"roles": ["x"]}]}, FINDING_ROLE_KEY),
]


def test_render_fills_every_placeholder_in_place():
    argv = ["run", "--init", "{{INIT_LINE}}", "--doc={{DOCUMENT}}@{{VERSION}}", "-p", "{{PROMPT}}"]
    values = {"INIT_LINE": "::init gtkb lo", "DOCUMENT": "item", "VERSION": "3", "PROMPT": "Review"}
    assert render(argv, values) == ["run", "--init", "::init gtkb lo", "--doc=item@3", "-p", "Review"]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["run", "{{ROLE}}"], "unknown invocation placeholder: ROLE"),
        (["run", "{{PROMPT}}"], "unfilled invocation placeholder: PROMPT"),
    ],
)
def test_render_refuses_an_unknown_or_unfilled_placeholder(argv, message):
    with pytest.raises(InvocationError, match=message):
        render(argv, {})


def test_the_placeholders_are_exactly_the_registered_set():
    registered = {"PROMPT", "PROJECT_ROOT", "INIT_LINE", "DOCUMENT", "VERSION", "TASK_FILE", "REPORT"}
    assert registered == PLACEHOLDERS


def test_sample_values_fill_every_placeholder_and_render_the_corrected_d_template():
    """c123 (batch design WP2 2.1): readiness checks render a template as the dispatcher would, with sample values."""
    corrected_d = [
        "groundtruth-kb/.venv/Scripts/python.exe",
        "scripts/ollama_harness.py",
        "--init",
        "{{INIT_LINE}}",
        "--bridge-document",
        "{{DOCUMENT}}",
        "--bridge-version",
        "{{VERSION}}",
        "--report",
        "{{REPORT}}",
        "-p",
        "{{PROMPT}}",
        "--model",
        "deepseek-v4-flash-cloud",
    ]
    values = sample_values("fixture-root")
    assert set(values) == PLACEHOLDERS
    assert values["PROJECT_ROOT"] == "fixture-root" and "PROJECT_ROOT" not in SAMPLE_VALUES
    assert all(isinstance(value, str) and value for value in values.values())
    rendered = render(corrected_d, values)
    assert rendered == [
        "groundtruth-kb/.venv/Scripts/python.exe",
        "scripts/ollama_harness.py",
        "--init",
        SAMPLE_VALUES["INIT_LINE"],
        "--bridge-document",
        SAMPLE_VALUES["DOCUMENT"],
        "--bridge-version",
        SAMPLE_VALUES["VERSION"],
        "--report",
        SAMPLE_VALUES["REPORT"],
        "-p",
        SAMPLE_VALUES["PROMPT"],
        "--model",
        "deepseek-v4-flash-cloud",
    ]
    assert surface_findings({"headless": {"argv": corrected_d}}) == []


@pytest.mark.parametrize(("surfaces", "code"), ROLE_BEARING)
def test_each_role_bearing_form_is_a_finding(surfaces, code):
    assert code in {finding.code for finding in surface_findings(surfaces)}


def test_an_unknown_placeholder_is_a_finding():
    findings = surface_findings({"headless": {"argv": ["runner", "{{ROLE}}"]}})
    assert [(finding.code, finding.path, finding.value) for finding in findings] == [
        (FINDING_UNKNOWN_PLACEHOLDER, "headless.argv[1]", "{{ROLE}}")
    ]


def test_role_free_surfaces_have_no_findings():
    """A note that explains the rule is prose, not a tag or an argument, and is allowed."""
    note = {
        "manual_dispatch": {
            "argv": ["harness.py", "--init", "{{INIT_LINE}}"],
            "note": "the installation carries no role",
        }
    }
    assert surface_findings(CORRECTED_F) == []
    assert surface_findings(note) == []
    assert surface_findings(None) == []


@pytest.fixture
def authority(native, tmp_path):
    service, *_ = native
    with TestClient(create_authority_app(service, project_root=tmp_path)) as client:
        yield service, client, tmp_path


@pytest.mark.integration
@pytest.mark.timeout(120)
@pytest.mark.parametrize(("surfaces", "code"), ROLE_BEARING)
def test_the_writer_refuses_a_role_bearing_registration_before_writing(authority, surfaces, code):
    service, client, root = authority
    before, disk = database_contents(service), files(root)
    response = put(client, "harnesses", "F", harness_fields(invocation_surfaces=surfaces))
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "harness_surface_names_role"
    assert code in {finding["code"] for finding in error["details"]["findings"]}
    assert database_contents(service) == before and files(root) == disk


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_the_writer_refuses_an_unknown_placeholder(authority):
    service, client, root = authority
    before = database_contents(service)
    surfaces = {"headless": {"argv": ["runner", "-p", "{{TASK}}"]}}
    response = put(client, "harnesses", "F", harness_fields(invocation_surfaces=surfaces))
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "unknown_invocation_placeholder"
    assert database_contents(service) == before


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_a_corrected_row_is_accepted_and_a_status_only_amendment_is_unaffected(authority):
    _service, client, _root = authority
    created = put(client, "harnesses", "F", harness_fields(invocation_surfaces=CORRECTED_F))
    assert created.status_code == 200, created.text
    assert created.json()["invocation_surfaces"] == CORRECTED_F
    activated = put(client, "harnesses", "F", {"status": "active"}, expected_version=1)
    assert activated.status_code == 200, activated.text
    refused = put(
        client,
        "harnesses",
        "F",
        {"invocation_surfaces": {**CORRECTED_F, "dispatch": {"dispatch_tags": ["loyal-opposition"]}}},
        expected_version=2,
    )
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "harness_surface_names_role"
