"""Shared partition helpers for the Wave 2 split-pattern lanes.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO with 5 implementation conditions).

Domain-neutral: knows nothing about bridge files, backlog rows, or KB
artifacts. Provides:

- ``classify_by_id_prefix()`` — common ``GTKB-*`` / ``AR-*`` / unknown
  classification (callers may apply additional content-based logic to
  override the default per-row).
- ``partition_items()`` — bucket items into framework / adopter /
  unclassified using a caller-supplied classifier.
- ``build_split_summary()`` — compose the standard summary block.
- ``emit_result()`` — write ``{lane_dir}/result.json`` per Wave 2 -003
  §4.2 contract + Slice 4 ``-006`` F2 lesson; appends the result.json
  path to ``output_files`` before serialization (self-referential).

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE``: shared partitioning
logic lives in this helper rather than being duplicated across the 3
split lanes. Each lane provides its own source-reader and
domain-specific classifier.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

_FRAMEWORK_PREFIX = "GTKB-"
_ADOPTER_PREFIX = "AR-"


def classify_by_id_prefix(item_id: str) -> str:
    """Return ``'framework'`` | ``'adopter'`` | ``'unknown'`` from the ID prefix.

    Callers may apply additional content-based logic to override this
    result. For example, ``_backlog_split.py`` reroutes ``GTKB-*`` rows
    with explicit Agent Red migration content to ``unknown`` (then
    ``unclassified``) rather than letting them silently land in
    framework — per Slice 5 ``-004`` F1 fix.
    """
    if item_id.startswith(_ADOPTER_PREFIX):
        return "adopter"
    if item_id.startswith(_FRAMEWORK_PREFIX):
        return "framework"
    return "unknown"


def partition_items(
    items: list[dict[str, Any]],
    classifier: Callable[[dict[str, Any]], tuple[str, str]],
) -> dict[str, list[dict[str, Any]]]:
    """Partition items into framework/adopter/unclassified buckets.

    ``classifier(item)`` returns ``(classification, signal)`` where:

    - ``classification ∈ {'framework', 'adopter', 'unclassified'}``
    - ``signal`` is a short string explaining which rule fired (added
      to each item's record as ``classification_signal`` so Wave 3 has
      actionable evidence per Slice 5 ``-006`` GO condition 2).

    Returns ``{'framework': [...], 'adopter': [...], 'unclassified': [...]}``.
    Each item dict has ``classification_signal`` appended; the original
    item is shallow-copied so the caller's input list is not mutated.
    """
    buckets: dict[str, list[dict[str, Any]]] = {
        "framework": [],
        "adopter": [],
        "unclassified": [],
    }
    for item in items:
        classification, signal = classifier(item)
        if classification not in buckets:
            classification = "unclassified"
            signal = signal or "unknown_classification_value"
        record = {**item, "classification_signal": signal}
        buckets[classification].append(record)
    return buckets


def build_split_summary(buckets: dict[str, list[Any]]) -> dict[str, int]:
    """Compose the ``summary`` block: per-bucket counts + total."""
    framework_count = len(buckets.get("framework", []))
    adopter_count = len(buckets.get("adopter", []))
    unclassified_count = len(buckets.get("unclassified", []))
    return {
        "framework_count": framework_count,
        "adopter_count": adopter_count,
        "unclassified_count": unclassified_count,
        "total": framework_count + adopter_count + unclassified_count,
    }


_DEFAULT_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "agent red",
    "agent_red",
    "adopter migration",
    "adopter rehearsal",
)


def classify_with_content_override(
    item_id: str,
    content_text: str,
    *,
    adopter_content_markers: tuple[str, ...] = _DEFAULT_ADOPTER_CONTENT_MARKERS,
) -> tuple[str, str]:
    """Classify by ID prefix with adopter-content conflict routing.

    Per Slice 5 ``-004`` F1 + Slice 6 ``-002`` F2: ``GTKB-*`` plus
    explicit adopter content is a *conflict signal*, not enough by
    itself to prove adopter ownership. Conflicts route to
    ``unclassified`` with signal ``gtkb_prefix_with_adopter_content``
    so Wave 3 has actionable evidence rather than silent
    auto-classification.

    Returns ``(classification, signal)``:

    - ``AR-*`` prefix → ``('adopter', 'ar_prefix')``
    - ``GTKB-*`` prefix + adopter content → ``('unclassified',
      'gtkb_prefix_with_adopter_content')``
    - ``GTKB-*`` prefix + no adopter content → ``('framework',
      'gtkb_prefix')``
    - Unknown prefix → ``('unclassified', 'unknown_prefix')``

    Per Slice 6 ``-004`` GO condition 3: this helper is for ID-prefixed
    artifacts (specs, work items, deliberations). DOC records do NOT
    follow the GTKB-/AR- prefix structure and need a separate
    domain-specific classifier in their consuming lane.
    """
    if item_id.startswith(_ADOPTER_PREFIX):
        return ("adopter", "ar_prefix")
    if item_id.startswith(_FRAMEWORK_PREFIX):
        blob = content_text.lower()
        if any(m in blob for m in adopter_content_markers):
            return ("unclassified", "gtkb_prefix_with_adopter_content")
        return ("framework", "gtkb_prefix")
    return ("unclassified", "unknown_prefix")


def emit_result(lane_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Write the structured result to ``{lane_dir}/result.json``.

    Per Wave 2 -003 §4.2 + Slice 4 ``-006`` F2 lesson: each sub-script
    writes ``result.json`` containing the structured result returned by
    ``run()``. Appends the result.json path to ``result["output_files"]``
    before serialization so the on-disk content correctly references
    itself.

    Same shape as the helper introduced in ``_path_rewrite.py:172`` for
    Slice 4; lifted into this shared helper so all 3 split lanes use
    the same implementation.
    """
    result_path = lane_dir / "result.json"
    result["output_files"] = [*result["output_files"], str(result_path)]
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
