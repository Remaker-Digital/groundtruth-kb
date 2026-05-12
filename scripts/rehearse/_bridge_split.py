"""Wave 2 lane 7 (Stage B): bridge thread classification by subject.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO).

Reads ``bridge/INDEX.md`` for the thread inventory + latest-version
status, then parses each thread's most recent NEW/REVISED file's
metadata block (key-value pairs between the **Status:** preamble and
the first ``---`` separator — NOT YAML frontmatter). Classifies each
thread as framework, adopter, or unclassified, and emits the split.

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001; Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import (
    build_split_summary,
    classify_by_id_prefix,
    emit_result,
    partition_items,
)

_INDEX_DOCUMENT_LINE = re.compile(r"^Document:\s*(?P<name>\S+)\s*$")
_INDEX_STATUS_LINE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY):\s*"
    r"bridge/(?P<filename>[A-Za-z0-9_.-]+)\s*$"
)
_VERSION_SUFFIX = re.compile(r"-(\d{3})\.md$")
_METADATA_BLOCK_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
_METADATA_BLOCK_TERMINATOR = re.compile(r"^---\s*$")


def _parse_index_threads(index_text: str) -> list[dict[str, Any]]:
    """Walk INDEX.md, returning per-thread thread records.

    Each record:
        {
            thread_name,
            latest_status,        # status from the top INDEX line
            latest_version,       # version from the top INDEX line
            latest_filename,      # filename from the top INDEX line
            metadata_filename,    # filename of the latest NEW or REVISED
                                  # (Prime metadata source); None if absent
        }

    Per Codex Slice 5 ``-008`` F1: the top-of-entry status line is often
    a Loyal Opposition response (GO/NO-GO/VERIFIED) without a Prime
    metadata block. Classification metadata lives in the latest NEW or
    REVISED file (Prime's most recent submission). Walking down the
    ordered status lines and selecting the first NEW/REVISED yields the
    correct metadata source while preserving latest_status from the top
    line.

    Per ``.claude/rules/file-bridge-protocol.md`` §"Index File": "The
    latest version is always at the top of the version list within each
    entry."
    """
    threads: list[dict[str, Any]] = []
    current_name: str | None = None
    current_lines: list[tuple[str, str]] = []

    def _flush() -> None:
        if current_name is None or not current_lines:
            return
        latest_status, latest_filename = current_lines[0]
        version_match = _VERSION_SUFFIX.search(latest_filename)
        version = int(version_match.group(1)) if version_match else 0

        # Find the most recent NEW/REVISED in the ordered list (top is
        # newest). Per Slice 5 -008 F1: this is the Prime metadata
        # source. None if no NEW/REVISED appears (e.g., a thread that
        # only has Codex responses, which would be malformed).
        metadata_filename: str | None = None
        for status, filename in current_lines:
            if status in ("NEW", "REVISED"):
                metadata_filename = filename
                break

        threads.append(
            {
                "thread_name": current_name,
                "latest_status": latest_status,
                "latest_version": version,
                "latest_filename": latest_filename,
                "metadata_filename": metadata_filename,
            }
        )

    for raw_line in index_text.splitlines():
        line = raw_line.strip()
        doc_match = _INDEX_DOCUMENT_LINE.match(line)
        if doc_match:
            _flush()
            current_name = doc_match.group("name")
            current_lines = []
            continue
        status_match = _INDEX_STATUS_LINE.match(line)
        if status_match and current_name is not None:
            current_lines.append((status_match.group("status"), status_match.group("filename")))
    _flush()
    return threads


def _parse_metadata_block(file_text: str) -> dict[str, str]:
    """Parse the key-value metadata block of a bridge file.

    The block sits between the ``**Status:** ...`` preamble and the
    first ``---`` content separator. Format is key-value pairs, NOT
    YAML frontmatter (no opening ``---`` delimiter).

    Per Codex Slice 5 ``-002`` non-blocking note 2: parser must accept
    the actual format used in current bridge files (verified on
    slice4-001).

    Returns ``{key: value}`` dict (string values only). Returns empty
    dict if no metadata block is found.
    """
    metadata: dict[str, str] = {}
    in_block = False
    for line in file_text.splitlines():
        stripped = line.strip()
        if _METADATA_BLOCK_TERMINATOR.match(stripped):
            if in_block:
                break
            continue
        kv_match = _METADATA_BLOCK_KEY.match(stripped)
        if kv_match:
            key = kv_match.group(1).lower()
            value = kv_match.group(2).strip()
            if key in (
                "bridge_kind",
                "work_item_ids",
                "spec_ids",
                "target_project",
                "implementation_scope",
            ):
                in_block = True
                metadata[key] = value
                continue
            if in_block:
                metadata[key] = value
        elif in_block and not stripped:
            continue
        elif in_block:
            break
    return metadata


def _classify_thread(thread: dict[str, Any]) -> tuple[str, str]:
    """Return (classification, signal) for a thread.

    Heuristic priority per ``-005`` §2.1:
    1. ``target_project:`` field (agent-red → adopter; groundtruth-kb →
       framework).
    2. ``work_item_ids:`` prefix as fallback.
    3. Thread-name pattern as last resort.
    4. No signal → unclassified.
    """
    metadata = thread.get("metadata", {})

    target_project = metadata.get("target_project", "").strip().strip("`'\"").lower()
    if target_project == "agent-red":
        return ("adopter", "target_project_agent_red")
    if target_project == "groundtruth-kb":
        return ("framework", "target_project_groundtruth_kb")

    wi_field = metadata.get("work_item_ids", "")
    wi_match = re.search(r"\[?\s*([A-Za-z0-9_-]+)", wi_field)
    if wi_match:
        wi_id = wi_match.group(1)
        prefix_class = classify_by_id_prefix(wi_id)
        if prefix_class == "adopter":
            return ("adopter", f"work_item_ids_prefix:{wi_id}")
        if prefix_class == "framework":
            return ("framework", f"work_item_ids_prefix:{wi_id}")

    thread_name = thread.get("thread_name", "").lower()
    if thread_name.startswith("gtkb-isolation-"):
        return ("adopter", "thread_name_gtkb_isolation")
    if thread_name.startswith(("gtkb-bridge-", "gtkb-db-backup-", "halt-os-pollers")):
        return ("framework", "thread_name_framework_infra")
    if thread_name.startswith("gtkb-dora-"):
        return ("adopter", "thread_name_dora_adopter")
    if thread_name.startswith("canonical-deploy-pipeline"):
        return ("adopter", "thread_name_canonical_deploy")

    return ("unclassified", "no_classification_signal")


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    bridge_root: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    ``bridge_root`` (default ``LEGACY_ROOT/bridge``) lets tests pass a
    fixture directory per Codex Slice 5 ``-002`` non-blocking note 4 —
    no monkeypatching of module constants needed.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    lane_dir = output_dir / "bridge_split"
    lane_dir.mkdir(parents=True, exist_ok=True)
    root = bridge_root if bridge_root is not None else LEGACY_ROOT / "bridge"
    index_path = root / "INDEX.md"

    if not index_path.exists():
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"bridge_index_missing: {index_path}"],
            },
        )

    try:
        index_text = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"bridge_index_unreadable: {exc}"],
            },
        )

    threads = _parse_index_threads(index_text)
    if not threads:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": ["bridge_index_no_threads_parsed"],
            },
        )

    warnings: list[str] = []
    for thread in threads:
        # Per Codex Slice 5 -008 F1: classification metadata comes from
        # the latest NEW/REVISED (Prime) file, not the top INDEX line
        # which may be a Codex GO/NO-GO/VERIFIED response without
        # metadata. ``metadata_filename`` is None only if the thread has
        # no NEW/REVISED entries — surface that as a warning.
        metadata_source = thread.get("metadata_filename")
        if metadata_source is None:
            thread["metadata"] = {}
            warnings.append(
                f"bridge_thread_no_prime_metadata_file: {thread['thread_name']} (no NEW/REVISED line in INDEX entry)"
            )
            continue
        bridge_file = root / metadata_source
        if not bridge_file.exists():
            thread["metadata"] = {}
            warnings.append(
                f"bridge_file_missing: {bridge_file.name} (Prime metadata source for {thread['thread_name']})"
            )
            continue
        try:
            file_text = bridge_file.read_text(encoding="utf-8")
        except OSError as exc:
            thread["metadata"] = {}
            warnings.append(f"bridge_file_unreadable: {bridge_file.name}: {exc}")
            continue
        thread["metadata"] = _parse_metadata_block(file_text)

    buckets = partition_items(threads, _classify_thread)

    if any(t["classification_signal"] == "no_classification_signal" for t in buckets["unclassified"]):
        warnings.append(
            f"unclassified_threads_present: "
            f"{sum(1 for t in buckets['unclassified'] if t['classification_signal'] == 'no_classification_signal')} "
            f"thread(s) with no classification signal — surface for owner decision at Wave 3"
        )

    bridge_split_doc = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_root": str(root).replace("\\", "/"),
        "summary": build_split_summary(buckets),
        "framework_threads": buckets["framework"],
        "adopter_threads": buckets["adopter"],
        "unclassified_threads": buckets["unclassified"],
    }

    bridge_split_path = lane_dir / "bridge_split.json"
    bridge_split_path.write_text(json.dumps(bridge_split_doc, indent=2), encoding="utf-8")

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(bridge_split_path)],
            "metrics": {
                "framework_count": bridge_split_doc["summary"]["framework_count"],
                "adopter_count": bridge_split_doc["summary"]["adopter_count"],
                "unclassified_count": bridge_split_doc["summary"]["unclassified_count"],
                "total_threads": bridge_split_doc["summary"]["total"],
            },
            "warnings": warnings,
        },
    )
