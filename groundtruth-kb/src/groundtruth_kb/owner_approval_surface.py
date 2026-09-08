"""Deterministic owner-approval surface generator for WI-4553 Slice 1.

Presentation-only adapter: renders mobile-friendly approval bundles for AUQ and
bridge review contexts without creating a parallel owner-decision authority.
"""

from __future__ import annotations

import html
import json
import mimetypes
import threading
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from groundtruth_kb.policy.registry import load_unified_policy_registry

SCHEMA_VERSION = 1
MAX_OPTIONS = 8
DEFAULT_PREVIEW_HOST = "127.0.0.1"
DEFAULT_PREVIEW_PORT = 8767

NON_AUTHORITATIVE_WARNING = (
    "Slice 1 presentation only. Browser selections and this page are "
    "non-authoritative. Record decisions through AskUserQuestion, the file "
    "bridge, or formal approval packets."
)

VALID_SOURCE_SURFACES = frozenset(
    {
        "auq",
        "bridge_go",
        "bridge_no_go",
        "bridge_verified",
        "formal_artifact_review",
    }
)


class OwnerApprovalSurfaceError(ValueError):
    """Raised when an approval packet fails validation."""


@dataclass(frozen=True)
class ApprovalOption:
    """One AskUserQuestion-style choice in an approval packet."""

    option_id: str
    label: str
    description: str = ""

    def to_json_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {"option_id": self.option_id, "label": self.label}
        if self.description:
            payload["description"] = self.description
        return payload


@dataclass(frozen=True)
class ApprovalPacket:
    """Deterministic owner-approval packet rendered by the presentation adapter."""

    packet_id: str
    title: str
    summary: str
    action_class: str
    source_surface: str
    options: tuple[ApprovalOption, ...]
    evidence_links: tuple[str, ...]
    evidence_text: str = ""
    display_status: str = "pending"
    expires_at: str = ""
    schema_version: int = SCHEMA_VERSION

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "packet_id": self.packet_id,
            "title": self.title,
            "summary": self.summary,
            "action_class": self.action_class,
            "source_surface": self.source_surface,
            "display_status": self.display_status,
            "non_authoritative": True,
            "non_authoritative_warning": NON_AUTHORITATIVE_WARNING,
            "options": [option.to_json_dict() for option in self.options],
            "evidence_links": list(self.evidence_links),
            "evidence_text": self.evidence_text,
            "expires_at": self.expires_at,
        }


def parse_approval_packet(raw: dict[str, Any]) -> ApprovalPacket:
    """Parse and validate an approval packet mapping."""
    if not isinstance(raw, dict):
        raise OwnerApprovalSurfaceError("approval packet must be a mapping")

    packet_id = _required_string(raw, field="packet_id")
    title = _required_string(raw, field="title")
    summary = _required_string(raw, field="summary")
    action_class = _required_string(raw, field="action_class")
    source_surface = _required_string(raw, field="source_surface")
    display_status = str(raw.get("display_status", "pending")).strip() or "pending"
    expires_at = str(raw.get("expires_at", "")).strip()
    evidence_text = str(raw.get("evidence_text", "")).strip()
    schema_version = int(raw.get("schema_version", SCHEMA_VERSION))
    if schema_version != SCHEMA_VERSION:
        raise OwnerApprovalSurfaceError(f"unsupported schema_version={schema_version!r}")

    options = _parse_options(raw.get("options"))
    evidence_links = _parse_evidence_links(raw.get("evidence_links"))

    return ApprovalPacket(
        packet_id=packet_id,
        title=title,
        summary=summary,
        action_class=action_class,
        source_surface=source_surface,
        options=options,
        evidence_links=evidence_links,
        evidence_text=evidence_text,
        display_status=display_status,
        expires_at=expires_at,
        schema_version=schema_version,
    )


def load_approval_packet(path: Path) -> ApprovalPacket:
    """Load an approval packet JSON fixture from disk."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise OwnerApprovalSurfaceError(f"{path} must contain a JSON object")
    return parse_approval_packet(data)


def validate_approval_packet(
    packet: ApprovalPacket,
    *,
    workspace_root: Path,
    valid_action_classes: frozenset[str] | None = None,
) -> None:
    """Validate packet semantics against AUQ action classes and root boundary."""
    root = workspace_root.resolve()
    _reject_archive_path(root)
    action_classes = valid_action_classes or _load_action_classes(root)
    if packet.action_class not in action_classes:
        raise OwnerApprovalSurfaceError(f"unknown action_class {packet.action_class!r}")

    if packet.source_surface not in VALID_SOURCE_SURFACES:
        raise OwnerApprovalSurfaceError(f"unknown source_surface {packet.source_surface!r}")

    if not packet.options:
        raise OwnerApprovalSurfaceError("approval packet requires at least one option")
    if len(packet.options) > MAX_OPTIONS:
        raise OwnerApprovalSurfaceError(f"approval packet exceeds max option count ({MAX_OPTIONS})")

    seen_option_ids: set[str] = set()
    for option in packet.options:
        if option.option_id in seen_option_ids:
            raise OwnerApprovalSurfaceError(f"duplicate option_id {option.option_id!r}")
        seen_option_ids.add(option.option_id)

    for link in packet.evidence_links:
        _validate_evidence_path(link, workspace_root=root)


def render_approval_bundle(
    packet: ApprovalPacket,
    output_dir: Path,
    *,
    workspace_root: Path,
    valid_action_classes: frozenset[str] | None = None,
) -> dict[str, Path]:
    """Validate and write HTML + JSON bundle files to ``output_dir``."""
    validate_approval_packet(packet, workspace_root=workspace_root, valid_action_classes=valid_action_classes)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "packet.json"
    html_path = output_dir / "index.html"
    json_path.write_text(
        json.dumps(packet.to_json_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    html_path.write_text(render_html_page(packet), encoding="utf-8")
    return {"json": json_path, "html": html_path}


def render_html_page(packet: ApprovalPacket) -> str:
    """Render a mobile-friendly static HTML page for one approval packet."""
    options_html = "\n".join(_render_option(option) for option in packet.options)
    evidence_links_html = "\n".join(_render_evidence_link(link) for link in packet.evidence_links)
    evidence_block = ""
    if packet.evidence_text:
        escaped_text = html.escape(packet.evidence_text)
        evidence_block = f"""
  <section>
    <h2>Copyable evidence</h2>
    <pre class="evidence-text">{escaped_text}</pre>
  </section>"""

    expires_block = ""
    if packet.expires_at:
        expires_block = f"<p><strong>Expires:</strong> {html.escape(packet.expires_at)}</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(packet.title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      line-height: 1.45;
    }}
    body {{
      margin: 0 auto;
      max-width: 42rem;
      padding: 1rem 1.1rem 2rem;
    }}
    .banner {{
      background: #fff3cd;
      border: 1px solid #ffecb5;
      border-radius: 0.5rem;
      color: #664d03;
      margin: 0 0 1rem;
      padding: 0.75rem 0.9rem;
    }}
    .meta, .summary {{
      color: #495057;
    }}
    .option {{
      border: 1px solid #ced4da;
      border-radius: 0.5rem;
      margin: 0.75rem 0;
      padding: 0.75rem 0.9rem;
    }}
    .option-id {{
      color: #6c757d;
      font-size: 0.85rem;
    }}
    .evidence-text {{
      background: #f8f9fa;
      border-radius: 0.35rem;
      overflow-x: auto;
      padding: 0.75rem;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    ul {{
      padding-left: 1.2rem;
    }}
  </style>
</head>
<body>
  <div class="banner" role="note">{html.escape(NON_AUTHORITATIVE_WARNING)}</div>
  <header>
    <h1>{html.escape(packet.title)}</h1>
    <p class="meta"><strong>Status:</strong> {html.escape(packet.display_status)} (non-authoritative)</p>
    <p class="meta"><strong>Packet:</strong> {html.escape(packet.packet_id)}</p>
    <p class="meta"><strong>Action class:</strong> {html.escape(packet.action_class)}</p>
    <p class="meta"><strong>Source surface:</strong> {html.escape(packet.source_surface)}</p>
    {expires_block}
  </header>
  <section>
    <h2>Summary</h2>
    <p class="summary">{html.escape(packet.summary)}</p>
  </section>
  <section>
    <h2>Options</h2>
    {options_html}
  </section>
  <section>
    <h2>Evidence links</h2>
    <ul>
      {evidence_links_html}
    </ul>
  </section>{evidence_block}
</body>
</html>
"""


def run_preview_server(bundle_dir: Path, *, host: str = DEFAULT_PREVIEW_HOST, port: int = DEFAULT_PREVIEW_PORT) -> None:
    """Serve a rendered bundle directory over HTTP (GET-only, no write-back)."""
    directory = bundle_dir.resolve()
    if not directory.is_dir():
        raise OwnerApprovalSurfaceError(f"bundle directory not found: {directory}")

    handler = _make_static_handler(directory)
    server = ThreadingHTTPServer((host, port), handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def start_preview_server_background(
    bundle_dir: Path,
    *,
    host: str = DEFAULT_PREVIEW_HOST,
    port: int = DEFAULT_PREVIEW_PORT,
) -> ThreadingHTTPServer:
    """Start a background preview server and return the server handle."""
    directory = bundle_dir.resolve()
    if not directory.is_dir():
        raise OwnerApprovalSurfaceError(f"bundle directory not found: {directory}")
    handler = _make_static_handler(directory)
    server = ThreadingHTTPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _make_static_handler(directory: Path) -> type[SimpleHTTPRequestHandler]:
    class BundleHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(directory), **kwargs)

        def do_POST(self) -> None:  # noqa: N802 - stdlib API
            self.send_error(405, "Write-back is not supported in Slice 1")

        def do_PUT(self) -> None:  # noqa: N802 - stdlib API
            self.send_error(405, "Write-back is not supported in Slice 1")

        def do_DELETE(self) -> None:  # noqa: N802 - stdlib API
            self.send_error(405, "Write-back is not supported in Slice 1")

        def log_message(self, format: str, *args: object) -> None:
            return

        def guess_type(self, path: str) -> str:
            guessed, _ = mimetypes.guess_type(path)
            return guessed or "application/octet-stream"

    return BundleHandler


def _render_option(option: ApprovalOption) -> str:
    description = ""
    if option.description:
        description = f"<p>{html.escape(option.description)}</p>"
    return (
        f'<article class="option" aria-label="{html.escape(option.label)}">'
        f"<h3>{html.escape(option.label)}</h3>"
        f'<p class="option-id">option_id: {html.escape(option.option_id)}</p>'
        f"{description}"
        f"<p><em>Selection is non-authoritative in Slice 1.</em></p>"
        f"</article>"
    )


def _render_evidence_link(link: str) -> str:
    escaped = html.escape(link)
    return f"<li><code>{escaped}</code></li>"


def _parse_options(raw_options: object) -> tuple[ApprovalOption, ...]:
    if not isinstance(raw_options, list) or not raw_options:
        raise OwnerApprovalSurfaceError("approval packet requires non-empty options list")
    options: list[ApprovalOption] = []
    for raw_option in raw_options:
        if not isinstance(raw_option, dict):
            raise OwnerApprovalSurfaceError("option entries must be mappings")
        option_id = _required_string(raw_option, field="option_id")
        label = _required_string(raw_option, field="label")
        description = str(raw_option.get("description", "")).strip()
        options.append(ApprovalOption(option_id=option_id, label=label, description=description))
    return tuple(options)


def _parse_evidence_links(raw_links: object) -> tuple[str, ...]:
    if raw_links is None:
        return ()
    if not isinstance(raw_links, list):
        raise OwnerApprovalSurfaceError("evidence_links must be a list when provided")
    links = tuple(str(item).strip() for item in raw_links)
    if any(not link for link in links):
        raise OwnerApprovalSurfaceError("evidence_links must not contain empty entries")
    return links


def _required_string(data: dict[str, Any], *, field: str) -> str:
    value = str(data.get(field, "")).strip()
    if not value:
        raise OwnerApprovalSurfaceError(f"approval packet requires {field}")
    return value


def _validate_evidence_path(link: str, *, workspace_root: Path) -> None:
    normalized = link.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("\\\\"):
        raise OwnerApprovalSurfaceError(f"evidence link must be relative: {link!r}")
    path = Path(normalized)
    if path.is_absolute():
        raise OwnerApprovalSurfaceError(f"evidence link must be relative: {link!r}")
    if ".." in path.parts:
        raise OwnerApprovalSurfaceError(f"evidence link must not contain .. segments: {link!r}")
    resolved = (workspace_root / path).resolve()
    try:
        resolved.relative_to(workspace_root)
    except ValueError as exc:
        raise OwnerApprovalSurfaceError(f"evidence link escapes workspace root: {link!r}") from exc


def _load_action_classes(workspace_root: Path) -> frozenset[str]:
    registry = load_unified_policy_registry(start=workspace_root)
    return frozenset(registry.actions_by_class)


def _reject_archive_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if "\\claude-playground" in normalized:
        raise OwnerApprovalSurfaceError(f"{path} is an archive path and must not be used")
