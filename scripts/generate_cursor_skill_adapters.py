#!/usr/bin/env python3
"""Generate side-effect-free Cursor skill adapters from canonical GT-KB skills.

Unlike ``_bootstrap_cursor_harness.py``, this command never registers a harness,
changes a role, writes database state, or regenerates harness projections.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_RELATIVE_PATH = Path("config/agent-control/gtkb-harness-capability-registry.toml")
CURSOR_SKILLS_RELATIVE_PATH = Path(".cursor/skills")
MANIFEST_NAME = "MANIFEST.json"
GENERATED_MARKER = "<!-- GTKB-CURSOR-SKILL-ADAPTER"
GENERATED_END_MARKER = "GTKB-CURSOR-SKILL-ADAPTER -->"
RESOURCE_DIRECTORY_NAMES = ("references", "helpers")
_CANONICAL_RESOURCE_RE = re.compile(
    r"(?P<prefix>\.agents/skills/)(?P<skill>[A-Za-z0-9._-]+)/(?P<resource>helpers|references)/"
)
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from _wrap_io import _atomic_write_bytes  # noqa: E402


class CursorSkillAdapterError(ValueError):
    """Raised when Cursor adapters cannot be generated deterministically."""


@dataclass(frozen=True, slots=True)
class CursorSkillAdapter:
    capability_id: str
    canonical_name: str
    source_relative_path: str
    adapter_relative_path: str
    source_sha256: str


def _codex_generator() -> Any:
    path = _SCRIPT_DIR / "generate_codex_skill_adapters.py"
    spec = importlib.util.spec_from_file_location("_gtkb_codex_skill_generator", path)
    if spec is None or spec.loader is None:
        raise CursorSkillAdapterError(f"Cannot load canonical adapter renderer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative(value: str, *, prefix: str, suffix: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        path.is_absolute()
        or ".." in path.parts
        or normalized != path.as_posix()
        or not normalized.startswith(prefix)
        or not normalized.endswith(suffix)
    ):
        raise CursorSkillAdapterError(f"Unsafe projection path: {value!r}")
    return normalized


def _load_registry(project_root: Path) -> dict[str, Any]:
    path = project_root / REGISTRY_RELATIVE_PATH
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise CursorSkillAdapterError(f"Cannot load harness capability registry {path}: {exc}") from exc


def build_adapters(project_root: Path) -> list[CursorSkillAdapter]:
    renderer = _codex_generator()
    raw_capabilities = _load_registry(project_root).get("capabilities")
    if not isinstance(raw_capabilities, list):
        raise CursorSkillAdapterError("Harness capability registry has no capabilities array")
    adapters: list[CursorSkillAdapter] = []
    seen: set[str] = set()
    for capability in raw_capabilities:
        if not isinstance(capability, dict) or capability.get("kind") != "skill":
            continue
        cursor = capability.get("cursor")
        if not isinstance(cursor, dict) or cursor.get("status") == "unsupported":
            continue
        raw_surface = str(cursor.get("surface") or "")
        if not raw_surface.replace("\\", "/").startswith(".cursor/skills/"):
            continue
        surface = _safe_relative(raw_surface, prefix=".cursor/skills/", suffix="/SKILL.md")
        source = _safe_relative(
            str(capability.get("canonical_source") or ""),
            prefix=".agents/skills/",
            suffix="/SKILL.md",
        )
        if surface in seen:
            raise CursorSkillAdapterError(f"Duplicate Cursor adapter surface: {surface}")
        seen.add(surface)
        source_path = project_root / source
        try:
            source_text = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise CursorSkillAdapterError(f"Cannot read canonical skill {source}: {exc}") from exc
        stripped = renderer._strip_generated_block(source_text).lstrip("\ufeff").rstrip() + "\n"
        renderer.validate_skill_frontmatter(stripped, source)
        adapters.append(
            CursorSkillAdapter(
                capability_id=str(capability.get("id") or ""),
                canonical_name=str(capability.get("canonical_name") or Path(source).parent.name),
                source_relative_path=source,
                adapter_relative_path=surface,
                source_sha256=_sha256(stripped.encode("utf-8")),
            )
        )
    return sorted(adapters, key=lambda item: item.adapter_relative_path.casefold())


def render_adapter(source_text: str, adapter: CursorSkillAdapter, *, generated_at: str) -> str:
    renderer = _codex_generator()
    renderer_adapter = renderer.SkillAdapter(
        capability_id=adapter.capability_id,
        canonical_name=adapter.canonical_name,
        source_relative_path=adapter.source_relative_path,
        adapter_relative_path=adapter.adapter_relative_path,
        source_sha256=adapter.source_sha256,
    )
    rendered = renderer.render_adapter(source_text, renderer_adapter, generated_at=generated_at)
    rendered = rendered.replace(renderer.GENERATED_MARKER, GENERATED_MARKER)
    rendered = rendered.replace(renderer.GENERATED_END_MARKER, GENERATED_END_MARKER)
    rendered = rendered.replace(
        "Generated by: scripts/generate_codex_skill_adapters.py",
        "Generated by: scripts/generate_cursor_skill_adapters.py",
    )
    rendered = rendered.replace(f"Generated at: {generated_at}\n", "")
    # Rewrite Codex surface paths to Cursor's, except helper invocations: those
    # must keep pointing at the Codex copies, which are Cursor's registered
    # execution route. A blanket replace here silently destroyed that routing on
    # every regeneration.
    rendered = re.sub(r"\.codex(/skills/[A-Za-z0-9._-]+/)(?!helpers/)", r".cursor\1", rendered)
    rendered = re.sub(r"\.codex(\\skills\\[A-Za-z0-9._-]+\\)(?!helpers\\)", r".cursor\1", rendered)
    # Resource-aware rewrite. ``helpers/`` are executables and must keep pointing
    # at the Codex copies, which are Cursor's registered execution route; its local
    # copies exist but are not invoked. ``references/`` are documentation and are
    # correctly local. Rewriting both to .cursor destroyed the helper routing on
    # every regeneration.
    rendered = _CANONICAL_RESOURCE_RE.sub(
        lambda match: (
            f".codex/skills/{match.group('skill')}/helpers/"
            if match.group("resource") == "helpers"
            else f".cursor/skills/{match.group('skill')}/references/"
        ),
        rendered,
    )
    return rendered


def _write_if_changed(path: Path, content: bytes, *, check: bool) -> bool:
    existing = path.read_bytes() if path.is_file() else None
    if existing == content:
        return False
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_bytes(path, content)
    return True


def _relative(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _resource_files(source_dir: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in source_dir.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix.casefold() not in {".pyc", ".pyo"}
            and not path.name.startswith(("_temp_", "tmp_", "draft-", "draft_"))
        ),
        key=lambda path: path.as_posix().casefold(),
    )


def _sync_resources(project_root: Path, adapter: CursorSkillAdapter, *, check: bool) -> list[str]:
    source_skill_dir = (project_root / adapter.source_relative_path).parent
    target_skill_dir = (project_root / adapter.adapter_relative_path).parent
    changed: list[str] = []
    for resource_name in RESOURCE_DIRECTORY_NAMES:
        source_root = source_skill_dir / resource_name
        target_root = target_skill_dir / resource_name
        expected: set[Path] = set()
        if source_root.is_dir():
            for source in _resource_files(source_root):
                target = target_root / source.relative_to(source_root)
                expected.add(target)
                if _write_if_changed(target, source.read_bytes(), check=check):
                    changed.append(_relative(project_root, target))
        if target_root.is_dir():
            for target in _resource_files(target_root):
                if target in expected:
                    continue
                changed.append(_relative(project_root, target))
                if not check:
                    target.unlink()
    return changed


def _manifest_content(adapters: list[CursorSkillAdapter]) -> bytes:
    payload = {
        "schema_version": 1,
        "generated_by": "scripts/generate_cursor_skill_adapters.py",
        "source_of_truth": ".agents/skills/*/SKILL.md",
        "adapter_contract": "full behavioral adapter; no harness-state side effects",
        "adapters": [asdict(adapter) for adapter in adapters],
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _observe_owned_orphans(project_root: Path, adapters: list[CursorSkillAdapter]) -> list[str]:
    root = project_root / CURSOR_SKILLS_RELATIVE_PATH
    if not root.is_dir():
        return []
    expected = {project_root / adapter.adapter_relative_path for adapter in adapters}
    changed: list[str] = []
    for path in sorted(root.glob("*/SKILL.md"), key=lambda item: item.as_posix().casefold()):
        if path in expected:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if GENERATED_MARKER not in text:
            continue
        changed.append(_relative(project_root, path))
    return changed


def render_outputs(
    project_root: Path,
    *,
    source_overrides: dict[str, bytes] | None = None,
) -> tuple[dict[str, bytes], list[CursorSkillAdapter], list[str]]:
    """Render the complete owned output set without touching the live tree."""

    root = project_root.resolve()
    adapters = build_adapters(root)
    overrides = source_overrides or {}
    outputs: dict[str, bytes] = {}
    expected_resources: set[str] = set()
    for adapter in adapters:
        source_bytes = (
            overrides[adapter.source_relative_path]
            if adapter.source_relative_path in overrides
            else (root / adapter.source_relative_path).read_bytes()
        )
        source_text = source_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        outputs[adapter.adapter_relative_path] = render_adapter(
            source_text, adapter, generated_at="deterministic"
        ).encode("utf-8")
        source_skill_dir = (root / adapter.source_relative_path).parent
        target_skill_dir = PurePosixPath(adapter.adapter_relative_path).parent
        for resource_name in RESOURCE_DIRECTORY_NAMES:
            source_root = source_skill_dir / resource_name
            if not source_root.is_dir():
                continue
            for source in _resource_files(source_root):
                target = (
                    target_skill_dir / resource_name / PurePosixPath(source.relative_to(source_root).as_posix())
                ).as_posix()
                source_relative = source.relative_to(root).as_posix()
                outputs[target] = overrides[source_relative] if source_relative in overrides else source.read_bytes()
                expected_resources.add(target)
    manifest = (CURSOR_SKILLS_RELATIVE_PATH / MANIFEST_NAME).as_posix()
    outputs[manifest] = _manifest_content(adapters)
    orphans = _observe_owned_orphans(root, adapters)
    for adapter in adapters:
        target_skill_dir = (root / adapter.adapter_relative_path).parent
        for resource_name in RESOURCE_DIRECTORY_NAMES:
            target_root = target_skill_dir / resource_name
            if not target_root.is_dir():
                continue
            for target in _resource_files(target_root):
                relative = _relative(root, target)
                if relative not in expected_resources:
                    orphans.append(relative)
    return outputs, adapters, sorted(set(orphans), key=str.casefold)


def generate(project_root: Path, *, check: bool = False) -> tuple[list[str], list[str], list[str]]:
    root = project_root.resolve()
    outputs, adapters, orphans = render_outputs(root)
    changed: list[str] = []
    for relative, content in sorted(outputs.items(), key=lambda item: item[0].casefold()):
        if _write_if_changed(root / relative, content, check=check):
            changed.append(relative)
    return (
        sorted(set(changed), key=str.casefold),
        [adapter.adapter_relative_path for adapter in adapters],
        orphans,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args(argv)
    try:
        changed, adapters, orphans = generate(args.project_root, check=args.check)
    except (CursorSkillAdapterError, OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        print(f"Cursor skill adapters: FAIL ({exc})", file=sys.stderr)
        return 2
    if orphans:
        print(
            "Cursor skill adapters: FAIL (owned orphan adapters require an explicit governed cleanup)", file=sys.stderr
        )
        for path in orphans:
            print(f"- {path}", file=sys.stderr)
        return 2
    if changed:
        action = "would update" if args.check else "updated"
        print(f"Cursor skill adapters: {action} {len(changed)} file(s)")
        for path in changed:
            print(f"- {path}")
        return 1 if args.check else 0
    print(f"Cursor skill adapters: PASS ({len(adapters)} adapters current)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
