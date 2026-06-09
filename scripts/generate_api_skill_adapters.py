#!/usr/bin/env python3
"""Generate compact API harness skill adapters from canonical GT-KB skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_RELATIVE_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"
API_SKILLS_RELATIVE_PATH = Path(".api-harness") / "skills"
MANIFEST_NAME = "MANIFEST.json"
GENERATED_MARKER = "<!-- GTKB-API-SKILL-ADAPTER"
GENERATED_END_MARKER = "GTKB-API-SKILL-ADAPTER -->"
FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


class ApiSkillAdapterError(ValueError):
    """Raised when canonical skill metadata cannot produce an API adapter."""


@dataclass(frozen=True)
class ApiSkillAdapter:
    capability_id: str
    canonical_name: str
    description: str
    source_relative_path: str
    adapter_relative_path: str
    source_sha256: str


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _relative_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_generated_block(text: str) -> str:
    start = text.find(GENERATED_MARKER)
    if start == -1:
        return text
    end = text.find(GENERATED_END_MARKER, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(GENERATED_END_MARKER) :].lstrip("\r\n")


def _load_registry(project_root: Path) -> dict[str, Any]:
    registry_path = project_root / REGISTRY_RELATIVE_PATH
    return tomllib.loads(registry_path.read_text(encoding="utf-8"))


def _skill_capabilities(registry: dict[str, Any]) -> list[dict[str, Any]]:
    raw_capabilities = registry.get("capabilities")
    if not isinstance(raw_capabilities, list):
        return []
    return [
        capability
        for capability in raw_capabilities
        if isinstance(capability, dict)
        and capability.get("kind") == "skill"
        and str(capability.get("canonical_source") or "").endswith("/SKILL.md")
    ]


def _adapter_relative_path(source_relative_path: str) -> str:
    source_path = Path(source_relative_path)
    return (API_SKILLS_RELATIVE_PATH / source_path.parent.name / "SKILL.md").as_posix()


def validate_skill_frontmatter(text: str, path: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        raise ApiSkillAdapterError(f"{path}: missing opening YAML frontmatter delimiter")

    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        raise ApiSkillAdapterError(f"{path}: missing closing YAML frontmatter delimiter")

    fields: dict[str, str] = {}
    for offset, line in enumerate(lines[1:closing_index], start=2):
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "- ")):
            continue
        if ":" not in stripped:
            raise ApiSkillAdapterError(f"{path}:{offset}: malformed frontmatter line")
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not FRONTMATTER_KEY_RE.match(key):
            raise ApiSkillAdapterError(f"{path}:{offset}: invalid frontmatter key {key!r}")
        fields[key] = value.strip().strip("\"'")

    for required in ("name", "description"):
        if not fields.get(required):
            raise ApiSkillAdapterError(f"{path}: missing non-empty {required!r} frontmatter field")
    return fields


def _existing_generated_at(existing_text: str | None) -> str | None:
    if not existing_text:
        return None
    for line in existing_text.splitlines():
        if line.startswith("Generated at:"):
            return line.split(":", 1)[1].strip() or None
    return None


def build_adapters(project_root: Path) -> list[ApiSkillAdapter]:
    registry = _load_registry(project_root)
    adapters: list[ApiSkillAdapter] = []
    for capability in _skill_capabilities(registry):
        source_relative_path = str(capability.get("canonical_source") or "")
        source_path = project_root / source_relative_path
        source_text = _strip_generated_block(source_path.read_text(encoding="utf-8")).lstrip("\ufeff")
        frontmatter = validate_skill_frontmatter(source_text, source_relative_path)
        source_sha256 = _sha256_text(source_text.rstrip() + "\n")
        adapters.append(
            ApiSkillAdapter(
                capability_id=str(capability.get("id") or ""),
                canonical_name=str(capability.get("canonical_name") or frontmatter["name"]),
                description=frontmatter["description"],
                source_relative_path=source_relative_path,
                adapter_relative_path=_adapter_relative_path(source_relative_path),
                source_sha256=source_sha256,
            )
        )
    return adapters


def _generated_block(adapter: ApiSkillAdapter, generated_at: str) -> str:
    return "\n".join(
        [
            GENERATED_MARKER,
            "Generated: true",
            "Generated by: scripts/generate_api_skill_adapters.py",
            f"Canonical source: {adapter.source_relative_path}",
            f"Canonical source sha256: {adapter.source_sha256}",
            f"Generated at: {generated_at}",
            "Do not edit this adapter directly. Edit the canonical source and regenerate.",
            GENERATED_END_MARKER,
            "",
        ]
    )


def render_adapter(adapter: ApiSkillAdapter, *, generated_at: str) -> str:
    lines = [
        "---",
        f"name: {adapter.canonical_name}",
        f"description: {json.dumps(adapter.description)}",
        "---",
        _generated_block(adapter, generated_at),
        f"# API Harness Skill Adapter: {adapter.canonical_name}",
        "",
        f"- Capability ID: `{adapter.capability_id}`",
        f"- Canonical source: `{adapter.source_relative_path}`",
        f"- Canonical source sha256: `{adapter.source_sha256}`",
        "- Adapter role: compact discovery pointer for API-based shims.",
        "- Tool contract: use only the canonical tool subset exposed by API-based harnesses.",
        "",
        "## Summary",
        "",
        adapter.description,
        "",
        "## Use Contract",
        "",
        "Before applying this skill, read the canonical source file listed above. This adapter is not a full copy of "
        "the skill body; it preserves source-of-truth discipline and avoids duplicating broad canonical knowledge into "
        "generated API-based harness surfaces.",
        "",
    ]
    return "\n".join(lines)


def _write_if_changed(path: Path, content: str, *, check: bool) -> bool:
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    if existing == content:
        return False
    if check:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _manifest_content(adapters: list[ApiSkillAdapter]) -> str:
    payload = {
        "schema_version": 1,
        "generated_by": "scripts/generate_api_skill_adapters.py",
        "source_of_truth": ".claude/skills/*/SKILL.md",
        "adapter_contract": "compact pointer; read canonical source before applying skill",
        "adapters": [asdict(adapter) for adapter in adapters],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _remove_orphan_adapters(project_root: Path, adapters: list[ApiSkillAdapter], *, check: bool) -> list[str]:
    skills_root = project_root / API_SKILLS_RELATIVE_PATH
    if not skills_root.is_dir():
        return []
    expected = {project_root / adapter.adapter_relative_path for adapter in adapters}
    expected.add(skills_root / MANIFEST_NAME)
    orphans: list[str] = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        if skill_file in expected:
            continue
        text = skill_file.read_text(encoding="utf-8")
        if GENERATED_MARKER not in text:
            continue
        orphans.append(_relative_path(project_root, skill_file))
        if not check:
            skill_file.unlink()
            try:
                skill_file.parent.rmdir()
            except OSError:
                pass
    return orphans


def generate(project_root: Path, *, check: bool = False) -> tuple[list[str], list[str]]:
    project_root = project_root.resolve()
    adapters = build_adapters(project_root)
    changed: list[str] = []
    for adapter in adapters:
        adapter_path = project_root / adapter.adapter_relative_path
        existing_text = adapter_path.read_text(encoding="utf-8") if adapter_path.is_file() else None
        generated_at = _existing_generated_at(existing_text) or _now_iso()
        rendered = render_adapter(adapter, generated_at=generated_at)
        if _write_if_changed(adapter_path, rendered, check=check):
            changed.append(adapter.adapter_relative_path)

    manifest_path = project_root / API_SKILLS_RELATIVE_PATH / MANIFEST_NAME
    if _write_if_changed(manifest_path, _manifest_content(adapters), check=check):
        changed.append(_relative_path(project_root, manifest_path))
    changed.extend(_remove_orphan_adapters(project_root, adapters, check=check))
    return changed, [adapter.adapter_relative_path for adapter in adapters]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args(argv)

    try:
        changed, adapter_paths = generate(args.project_root, check=args.check)
    except (ApiSkillAdapterError, OSError, tomllib.TOMLDecodeError) as exc:
        print(f"API skill adapters: FAIL ({exc})", file=sys.stderr)
        return 1

    if changed:
        action = "would update" if args.check else "updated"
        print(f"API skill adapters: {action} {len(changed)} file(s)")
        for path in changed:
            print(f"- {path}")
        return 1 if args.check else 0

    print(f"API skill adapters: PASS ({len(adapter_paths)} adapters current)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
