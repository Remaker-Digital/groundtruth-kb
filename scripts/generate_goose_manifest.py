"""Generate the Goose skills manifest indexing on-disk gtkb- skill adapters (WI-5641).

Goose resolves skill capability parity via .goose/skills/MANIFEST.json rather than
per-capability registry surface entries. This generator scans the on-disk
.goose/skills/gtkb-*/SKILL.md adapters and writes a deterministic manifest index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

GOOSE_SKILLS_RELATIVE_PATH = Path(".goose") / "skills"
MANIFEST_NAME = "MANIFEST.json"


@dataclass(frozen=True)
class GooseSkillAdapter:
    capability_id: str
    adapter_relative_path: str
    source_relative_path: str
    source_sha256: str


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _read_skill_name(skill_md: Path) -> str:
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
        if line.strip() == "---" and "name" not in line:
            continue
    return skill_md.parent.name


def _load_registry_ids(project_root: Path) -> dict[str, str]:
    import tomllib
    reg = project_root / "config" / "agent-control" / "harness-capability-registry.toml"
    ids: dict[str, str] = {}
    if reg.is_file():
        data = tomllib.loads(reg.read_text(encoding="utf-8"))
        for cap in data.get("capabilities", []):
            cn = cap.get("canonical_name")
            if cn:
                ids[str(cn)] = str(cap.get("id") or "")
    return ids


def _capability_id_for(canonical_name: str, registry_ids: dict[str, str]) -> str:
    return registry_ids.get(canonical_name) or f"skill.{canonical_name.removeprefix('gtkb-')}"


def build_manifest(project_root: Path) -> dict:
    registry_ids = _load_registry_ids(project_root)
    skills_root = project_root / GOOSE_SKILLS_RELATIVE_PATH
    adapters: list[GooseSkillAdapter] = []
    if skills_root.is_dir():
        for skill_md in sorted(skills_root.glob("gtkb-*/SKILL.md")):
            name = _read_skill_name(skill_md)
            rel = skill_md.relative_to(project_root).as_posix()
            src = project_root / ".claude" / "skills" / name / "SKILL.md"
            src_rel = src.relative_to(project_root).as_posix()
            sha = _sha256_text(src.read_text(encoding="utf-8").rstrip() + "\n") if src.is_file() else ""
            cap_id = _capability_id_for(name, registry_ids)
            adapters.append(
                GooseSkillAdapter(
                    capability_id=cap_id,
                    adapter_relative_path=rel,
                    source_relative_path=src_rel,
                    source_sha256=sha,
                )
            )
    return {
        "schema_version": 1,
        "generated_by": "scripts/generate_goose_manifest.py",
        "source_of_truth": ".goose/skills/gtkb-*/SKILL.md",
        "adapter_contract": "goose manifest index of on-disk gtkb- skill adapters",
        "adapters": [asdict(a) for a in adapters],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Goose skills manifest.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true", help="Report drift without writing.")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    payload = build_manifest(project_root)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    manifest_path = project_root / GOOSE_SKILLS_RELATIVE_PATH / MANIFEST_NAME

    existing = manifest_path.read_bytes().decode("utf-8") if manifest_path.is_file() else None
    count = len(payload["adapters"])
    if args.check:
        if existing == content:
            print(f"Goose skills manifest: PASS ({count} adapters current)")
            return 0
        print("Goose skills manifest: FAIL (drift)")
        return 1
    if existing != content:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_bytes(manifest_path, content.encode("utf-8"))
    print(f"Goose skills manifest: PASS ({count} adapters current)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
