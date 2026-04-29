# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Format smart-poller notification artifacts for harness session-start orient.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md`` (P3-notify GO at
-008), the runner writes::

    .gtkb-state/bridge-poller/notifications/pending-bridge-action-{recipient}.json
    .gtkb-state/bridge-poller/notifications/pending-bridge-action-{recipient}.md

via the canonical ``groundtruth_kb.bridge.notify.update_notification``. This
module is a thin formatting wrapper around the canonical reader. It does NOT
re-parse the schema and does NOT mutate notification files.

Authority: ``bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`` GO
(REVISED-1 at -003 §3.1).
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.bridge.notify import (
    NOTIFY_SCHEMA_VERSION,
    NOTIFY_SUBDIR,
    NotificationArtifact,
    read_notification,
)
from groundtruth_kb.bridge.routing import BridgeAgent

# State dir lives at <project_root>/.gtkb-state/bridge-poller/. The runner's
# get_state_dir() resolves the same path; the reader takes project_root from
# the harness so it does not depend on environment variables at startup time.
STATE_RELATIVE = (".gtkb-state", "bridge-poller")


def _state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*STATE_RELATIVE)


def read_for_recipient(project_root: Path, recipient: BridgeAgent | str) -> NotificationArtifact | None:
    """Delegate to the canonical reader. Returns ``None`` on absent or malformed.

    The canonical ``groundtruth_kb.bridge.notify.read_notification`` already
    handles missing-file and malformed-JSON cases by returning ``None``.
    """
    return read_notification(_state_dir(project_root), recipient)


def format_orient_section(artifact: NotificationArtifact | None) -> str:
    """Produce the markdown section for the session-start orient block.

    Returns empty string when:
      - ``artifact`` is ``None`` (absent / malformed)
      - ``artifact.pending_actions`` is empty
      - ``artifact.schema_version`` does not match ``NOTIFY_SCHEMA_VERSION``
        (defensive: future schema bump should not surface garbled rows;
        caller may emit a separate diagnostic line if desired)

    The empty-string return is intentional: the harness orient builder treats
    empty as "no section" and proceeds with the rest of the orient unchanged.
    """
    if artifact is None or not artifact.pending_actions:
        return ""
    if artifact.schema_version != NOTIFY_SCHEMA_VERSION:
        return ""
    lines = [
        f"### Smart-poller notification — {len(artifact.pending_actions)} pending action(s)",
        "",
        f"_Source: `.gtkb-state/bridge-poller/{NOTIFY_SUBDIR}/pending-bridge-action-{artifact.recipient}.json` "
        f"(schema v{artifact.schema_version}; written {artifact.written_at})_",
        "",
        "| Document | Status | File | INDEX line |",
        "|---|---|---|---|",
    ]
    for item in artifact.pending_actions:
        lines.append(
            f"| `{item.document_name}` | **{item.top_status}** | `{item.top_file}` | {item.index_line_number} |"
        )
    return "\n".join(lines)
