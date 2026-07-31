from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "generate_rule_compatibility_projections.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("test_rule_projection_generator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fixture(root: Path, *, missing_canonical: bool = False) -> Path:
    policy = root / "policy.toml"
    csv_path = root / "moves.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Current home directory:", "Current file name:", "New home directory:", "New file name:"])
        for index in range(38):
            writer.writerow(
                [
                    f"{root}/.claude/rules",
                    f"rule-{index}.md",
                    f"{root}/config/agent-control",
                    f"gtkb-rule-{index}.md",
                ]
            )
    lines = [
        "schema_version = 1",
        'manifest_path = "moves.csv"',
        "",
    ]
    for index in range(38):
        canonical = root / "config" / "agent-control" / f"gtkb-rule-{index}.md"
        if not missing_canonical or index != 0:
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_bytes(f"rule {index}\r\n".encode())
        lines.extend(
            [
                "[[rule_projections]]",
                f'source = ".claude/rules/rule-{index}.md"',
                f'canonical = "config/agent-control/gtkb-rule-{index}.md"',
                'class = "projection"',
                'load_policy = "explicit_query"',
                "",
            ]
        )
    policy.write_text("\n".join(lines), encoding="utf-8")
    return policy


def test_live_policy_covers_exactly_38_casefold_unique_pairs() -> None:
    module = _load_module()
    policy = module.load_policy(ROOT)
    rows = module.projection_rows(policy)
    module.validate_policy_against_manifest(ROOT, policy, rows)
    assert len(rows) == 38
    assert len({row.source.casefold() for row in rows}) == 38
    assert len({row.canonical.casefold() for row in rows}) == 38


def test_generate_is_one_way_byte_preserving_and_idempotent(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    first = module.generate(tmp_path, policy_path=policy)
    assert all(item.changed for item in first)
    assert (tmp_path / ".claude/rules/rule-0.md").read_bytes() == b"rule 0\r\n"
    second = module.generate(tmp_path, policy_path=policy)
    assert not any(item.changed for item in second)


def test_check_reports_drift_without_writing(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    target = tmp_path / ".claude/rules/rule-0.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"manual\n")
    results = module.generate(tmp_path, policy_path=policy, check=True)
    assert next(item for item in results if item.source.endswith("rule-0.md")).changed
    assert target.read_bytes() == b"manual\n"


def test_render_outputs_is_side_effect_free_and_uses_canonical_override(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    canonical = "config/agent-control/gtkb-rule-0.md"
    projection = tmp_path / ".claude/rules/rule-0.md"
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    _rows, outputs = module.render_outputs(
        tmp_path,
        policy_path=policy,
        canonical_overrides={canonical: b"planned replacement\n"},
    )
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert outputs[".claude/rules/rule-0.md"] == b"planned replacement\n"
    assert not projection.exists()
    assert before == after


def test_missing_canonical_fails_without_deleting_projection(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path, missing_canonical=True)
    target = tmp_path / ".claude/rules/rule-0.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"retained\n")
    with pytest.raises(module.RuleProjectionError, match="Canonical rule is missing"):
        module.generate(tmp_path, policy_path=policy)
    assert target.read_bytes() == b"retained\n"


def test_explicit_link_rewrite_skips_code_and_preserves_fragment() -> None:
    module = _load_module()
    rewrite = module.LinkRewrite("config/agent-control/gtkb-a.md", "gtkb-b.md", "config/agent-control/gtkb-b.md", 1)
    text = "[live](gtkb-b.md#x) ` [inline](gtkb-b.md)`\n```md\n[code](gtkb-b.md)\n```\n"
    rendered = module.stabilize_relative_links(text, "config/agent-control/gtkb-a.md", [rewrite])
    assert "[live](config/agent-control/gtkb-b.md#x)" in rendered
    assert "` [inline](gtkb-b.md)`" in rendered
    assert "[code](gtkb-b.md)" in rendered
