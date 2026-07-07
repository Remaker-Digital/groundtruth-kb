"""Render the WI-4754 command-surface roadmap disposition report.

This helper is intentionally read-only: it loads
``config/agent-control/command-surface.toml``, validates that every preserved
CS-2+ roadmap slice has a concrete disposition, and emits markdown or JSON
evidence for the implementation report.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_DISPOSITIONS = {"implement", "defer", "supersede", "retire", "needs_owner_decision"}
SURVIVING_DISPOSITIONS = {"implement", "defer", "needs_owner_decision"}
EXPECTED_SLICE_IDS = ("CS-2", "CS-2.5", "CS-3", "CS-4", "CS-5+", "CS-6", "CS-7")


@dataclass(frozen=True)
class SliceDisposition:
    id: str
    title: str
    disposition: str
    child_slice: str
    rationale: str
    harness_parity_disposition: str
    required_target_paths: tuple[str, ...]
    required_specs: tuple[str, ...]
    pauth_needed: bool
    bridge_proposal_needed: bool
    covered_by: tuple[str, ...] = ()
    covered_behaviors: tuple[str, ...] = ()
    owner_decision_needed: str = ""

    @property
    def survives_as_child_work(self) -> bool:
        return self.disposition in SURVIVING_DISPOSITIONS

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "disposition": self.disposition,
            "child_slice": self.child_slice,
            "rationale": self.rationale,
            "harness_parity_disposition": self.harness_parity_disposition,
            "required_target_paths": list(self.required_target_paths),
            "required_specs": list(self.required_specs),
            "pauth_needed": self.pauth_needed,
            "bridge_proposal_needed": self.bridge_proposal_needed,
            "covered_by": list(self.covered_by),
            "covered_behaviors": list(self.covered_behaviors),
            "owner_decision_needed": self.owner_decision_needed,
            "survives_as_child_work": self.survives_as_child_work,
        }


@dataclass(frozen=True)
class CommandSurfaceDisposition:
    schema_version: int
    roadmap_id: str
    source_bridge: str
    verified_architecture_bridge: str
    project: str
    work_item: str
    project_authorization: str
    slices: tuple[SliceDisposition, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "roadmap_id": self.roadmap_id,
            "source_bridge": self.source_bridge,
            "verified_architecture_bridge": self.verified_architecture_bridge,
            "project": self.project,
            "work_item": self.work_item,
            "project_authorization": self.project_authorization,
            "slices": [item.to_dict() for item in self.slices],
        }


class DispositionConfigError(ValueError):
    """Raised when the disposition config is incomplete or ambiguous."""


def _default_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_config_path(project_root: Path) -> Path:
    return project_root / "config" / "agent-control" / "command-surface.toml"


def _string_tuple(value: object, *, field: str, slice_id: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise DispositionConfigError(f"{slice_id}.{field} must be a list of strings")
    return tuple(value)


def _required_str(raw: dict[str, Any], field: str, *, context: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DispositionConfigError(f"{context}.{field} must be a non-empty string")
    return value.strip()


def _required_bool(raw: dict[str, Any], field: str, *, context: str) -> bool:
    value = raw.get(field)
    if not isinstance(value, bool):
        raise DispositionConfigError(f"{context}.{field} must be a boolean")
    return value


def _parse_slice(raw: dict[str, Any]) -> SliceDisposition:
    slice_id = _required_str(raw, "id", context="slice")
    disposition = _required_str(raw, "disposition", context=slice_id)
    if disposition not in ALLOWED_DISPOSITIONS:
        allowed = ", ".join(sorted(ALLOWED_DISPOSITIONS))
        raise DispositionConfigError(f"{slice_id}.disposition must be one of: {allowed}")

    item = SliceDisposition(
        id=slice_id,
        title=_required_str(raw, "title", context=slice_id),
        disposition=disposition,
        child_slice=str(raw.get("child_slice") or ""),
        rationale=_required_str(raw, "rationale", context=slice_id),
        harness_parity_disposition=_required_str(raw, "harness_parity_disposition", context=slice_id),
        required_target_paths=_string_tuple(
            raw.get("required_target_paths"), field="required_target_paths", slice_id=slice_id
        ),
        required_specs=_string_tuple(raw.get("required_specs"), field="required_specs", slice_id=slice_id),
        pauth_needed=_required_bool(raw, "pauth_needed", context=slice_id),
        bridge_proposal_needed=_required_bool(raw, "bridge_proposal_needed", context=slice_id),
        covered_by=_string_tuple(raw.get("covered_by"), field="covered_by", slice_id=slice_id),
        covered_behaviors=_string_tuple(raw.get("covered_behaviors"), field="covered_behaviors", slice_id=slice_id),
        owner_decision_needed=str(raw.get("owner_decision_needed") or ""),
    )
    if item.survives_as_child_work:
        if not item.child_slice:
            raise DispositionConfigError(f"{slice_id} survives as child work but has no child_slice")
        if not item.required_target_paths:
            raise DispositionConfigError(f"{slice_id} survives as child work but has no required_target_paths")
        if not item.required_specs:
            raise DispositionConfigError(f"{slice_id} survives as child work but has no required_specs")
        if not item.pauth_needed or not item.bridge_proposal_needed:
            raise DispositionConfigError(f"{slice_id} survives as child work but is not PAUTH and bridge gated")
    return item


def load_disposition(config_path: str | Path) -> CommandSurfaceDisposition:
    path = Path(config_path)
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    slices_raw = raw.get("slices")
    if not isinstance(slices_raw, list) or not slices_raw:
        raise DispositionConfigError("config must define at least one [[slices]] entry")
    slices = tuple(_parse_slice(item) for item in slices_raw)
    _validate_slice_set(slices)
    return CommandSurfaceDisposition(
        schema_version=int(raw.get("schema_version", 0)),
        roadmap_id=_required_str(raw, "roadmap_id", context="root"),
        source_bridge=_required_str(raw, "source_bridge", context="root"),
        verified_architecture_bridge=_required_str(raw, "verified_architecture_bridge", context="root"),
        project=_required_str(raw, "project", context="root"),
        work_item=_required_str(raw, "work_item", context="root"),
        project_authorization=_required_str(raw, "project_authorization", context="root"),
        slices=slices,
    )


def _validate_slice_set(slices: tuple[SliceDisposition, ...]) -> None:
    ids = tuple(item.id for item in slices)
    if len(set(ids)) != len(ids):
        raise DispositionConfigError("slice ids must be unique")
    missing = [item for item in EXPECTED_SLICE_IDS if item not in ids]
    if missing:
        raise DispositionConfigError(f"missing required command-surface slices: {', '.join(missing)}")
    extras = [item for item in ids if item not in EXPECTED_SLICE_IDS]
    if extras:
        raise DispositionConfigError(f"unknown command-surface slice ids: {', '.join(extras)}")

    cs3 = next(item for item in slices if item.id == "CS-3")
    covered_text = "\n".join(cs3.covered_behaviors)
    if "::init" not in covered_text or "::wrap" not in covered_text:
        raise DispositionConfigError("CS-3 must explicitly preserve ::init and ::wrap as covered behavior")


def _markdown_list(items: tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- `{item}`" for item in items)


def render_markdown(disposition: CommandSurfaceDisposition) -> str:
    lines = [
        "# Command-Surface Roadmap Disposition",
        "",
        f"- Roadmap: `{disposition.roadmap_id}`",
        f"- Source bridge: `{disposition.source_bridge}`",
        f"- Verified architecture closure: `{disposition.verified_architecture_bridge}`",
        f"- Project: `{disposition.project}`",
        f"- Work item: `{disposition.work_item}`",
        f"- Project authorization: `{disposition.project_authorization}`",
        "",
        "## Slice Disposition Table",
        "",
        "| Slice | Title | Disposition | Child slice |",
        "| --- | --- | --- | --- |",
    ]
    for item in disposition.slices:
        child = item.child_slice or "none"
        lines.append(f"| `{item.id}` | {item.title} | `{item.disposition}` | `{child}` |")

    lines.extend(["", "## Details", ""])
    for item in disposition.slices:
        lines.extend(
            [
                f"### {item.id} - {item.title}",
                "",
                f"- Disposition: `{item.disposition}`",
                f"- Child slice: `{item.child_slice or 'none'}`",
                f"- PAUTH needed: `{str(item.pauth_needed).lower()}`",
                f"- Bridge proposal needed: `{str(item.bridge_proposal_needed).lower()}`",
                f"- Rationale: {item.rationale}",
                f"- Harness parity disposition: {item.harness_parity_disposition}",
                "",
                "Required target paths:",
                "",
                _markdown_list(item.required_target_paths),
                "",
                "Required specs:",
                "",
                _markdown_list(item.required_specs),
                "",
            ]
        )
        if item.covered_by:
            lines.extend(["Covered by:", "", _markdown_list(item.covered_by), ""])
        if item.covered_behaviors:
            lines.extend(
                ["Covered behaviours:", "", "\n".join(f"- {behavior}" for behavior in item.covered_behaviors), ""]
            )
        if item.owner_decision_needed:
            lines.extend(["Owner decision needed:", "", f"- {item.owner_decision_needed}", ""])

    surviving = [item for item in disposition.slices if item.survives_as_child_work]
    lines.extend(
        [
            "## Surviving Child Work",
            "",
            "The following entries are not implementation approval. Each requires a fresh bridge proposal, PAUTH coverage, GO, implementation-start packet, report, and verification before mutation.",
            "",
        ]
    )
    for item in surviving:
        lines.extend(
            [
                f"### {item.child_slice}",
                "",
                f"- Parent slice: `{item.id}`",
                f"- Current disposition: `{item.disposition}`",
                "- Required target paths:",
                "",
                _markdown_list(item.required_target_paths),
                "",
                "- Required specs:",
                "",
                _markdown_list(item.required_specs),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_default_project_root())
    parser.add_argument("--config", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    config_path = args.config or _default_config_path(args.project_root)
    disposition = load_disposition(config_path)
    if args.format == "json":
        content = json.dumps(disposition.to_dict(), indent=2, sort_keys=True) + "\n"
    else:
        content = render_markdown(disposition)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
