"""WI-6305 Slice 1: regression tests for the projection-authority reference inventory.

Derived from the proposal's Specification-Derived Verification Plan:

- `GOV-HARNESS-NEUTRAL-BASELINE-001` -- the inventory must actually cover the
  neutral source. A run reporting zero baseline-side references means the
  extended search domain was not searched.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -- two runs over an unchanged tree produce
  identical classifications.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` -- references from more than one harness
  surface are each classified.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- a fixture reference of each of the
  four classes lands in its expected bucket.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _ROOT / "scripts" / "inventory_projection_authority_references.py"

_spec = importlib.util.spec_from_file_location("inventory_projection_authority_references", _SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
inventory = importlib.util.module_from_spec(_spec)
sys.modules["inventory_projection_authority_references"] = inventory
_spec.loader.exec_module(inventory)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001: one fixture per class ---------------


@pytest.mark.parametrize(
    ("source_path", "line", "expected"),
    [
        pytest.param(
            "scripts/harness_projection/project_harness.py",
            'target = ".claude/hooks/bridge-compliance-gate.py"',
            inventory.REQUIRED,
            id="required-projector-names-its-own-output",
        ),
        pytest.param(
            ".harness-baseline-configuration/.projection-manifest.json",
            '"target": ".goose/hooks/bridge-compliance-gate.py"',
            inventory.REQUIRED,
            id="required-typed-target-profile",
        ),
        pytest.param(
            "docs/reference/some-doc.md",
            "The projection at `.claude/rules/loyal-opposition.md` is generated from "
            "`.harness-baseline-configuration/rules/loyal-opposition.md`.",
            inventory.ROUTED,
            id="routed-paired-with-canonical-carrier",
        ),
        pytest.param(
            "docs/reference/some-doc.md",
            "Harness configuration for the Claude surface lives at `.claude/settings.json` in the generated tree.",
            inventory.NARRATIVE,
            id="narrative-prose-describes-path",
        ),
        pytest.param(
            ".harness-baseline-configuration/rules/file-bridge-protocol.md",
            "python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug <doc>",
            inventory.RESIDUAL_CONSUMER,
            id="residual-prose-that-executes-a-generated-target",
        ),
        pytest.param(
            "scripts/some_tool.py",
            'helper = Path(".codex/gtkb-hooks/adapter.py")',
            inventory.RESIDUAL_CONSUMER,
            id="residual-code-depends-on-generated-target",
        ),
    ],
)
def test_fixture_reference_of_each_class_lands_in_expected_bucket(source_path: str, line: str, expected: str) -> None:
    target = inventory._TARGET_RE.search(line)
    assert target is not None, "fixture line must contain a generated-target reference"
    assert inventory.classify_reference(source_path=source_path, line=line, target=target.group(0)) == expected


def test_classification_vocabulary_is_closed() -> None:
    assert set(inventory.CLASSIFICATIONS) == {
        inventory.REQUIRED,
        inventory.RESIDUAL_CONSUMER,
        inventory.ROUTED,
        inventory.NARRATIVE,
    }


# --- DCL-CROSS-HARNESS-ENFORCEMENT-001: multiple harness surfaces --------------


def test_references_from_more_than_one_harness_surface_are_each_classified(tmp_path: Path) -> None:
    _write(tmp_path, "docs/multi.md", "python .claude/hooks/a.py\npython .goose/hooks/b.py\n")

    references = inventory.scan(tmp_path)

    harnesses = {ref.harness for ref in references}
    assert {"claude", "goose"} <= harnesses
    assert all(ref.classification in inventory.CLASSIFICATIONS for ref in references)


def test_projection_directories_are_not_scanned_as_consumers(tmp_path: Path) -> None:
    """A generated target referencing a sibling generated target is not a consumer."""
    _write(tmp_path, ".claude/hooks/gate.py", 'other = ".claude/hooks/other.py"\n')
    _write(tmp_path, "docs/real.md", "python .claude/hooks/gate.py\n")

    sources = {ref.source_path for ref in inventory.scan(tmp_path)}

    assert sources == {"docs/real.md"}


# --- GOV-SOURCE-OF-TRUTH-FRESHNESS-001: determinism ---------------------------


def test_two_runs_over_an_unchanged_tree_produce_identical_classifications(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", "see `.claude/rules/x.md` for detail\n")
    _write(tmp_path, "scripts/b.py", 'p = Path(".codex/gtkb-hooks/y.py")\n')
    _write(tmp_path, "docs/c.md", "python .goose/hooks/z.py --run\n")

    first = inventory.build_report(inventory.scan(tmp_path))
    second = inventory.build_report(inventory.scan(tmp_path))

    assert first == second


def test_report_carries_no_timestamp_so_runs_are_comparable(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", "see `.claude/rules/x.md`\n")

    report = inventory.build_report(inventory.scan(tmp_path))

    assert "generated_at" not in report
    assert "timestamp" not in report


# --- GOV-HARNESS-NEUTRAL-BASELINE-001: the extended domain is really searched ---


def test_live_inventory_covers_the_neutral_baseline_domain() -> None:
    """The neutral source is searched, and it names no generated target.

    Coverage is proven by the files walked inside `.harness-baseline-configuration/`, not by references found there:
    under GOV-HARNESS-NEUTRAL-BASELINE-001 the baseline carries no harness directory name, so its reference count is
    zero on a correct tree while a zero file count would mean the domain was silently skipped.
    """
    if not (_ROOT / ".harness-baseline-configuration").is_dir():
        pytest.skip("neutral baseline not present in this checkout")

    coverage = inventory.domain_coverage(_ROOT)
    report = inventory.build_report(inventory.scan(_ROOT))

    assert coverage["neutral_baseline_files"] > 0, "neutral-baseline domain was not searched"
    assert coverage["other_files"] > 0
    assert report["baseline_side_references"] == 0, "the neutral baseline names a generated harness target"
    assert report["total_references"] > 0


def test_live_inventory_is_read_only_for_source(tmp_path: Path) -> None:
    """`scan` opens files for reading only; it must not create or modify anything."""
    _write(tmp_path, "docs/a.md", "see `.claude/rules/x.md`\n")
    before = {p: p.stat().st_mtime_ns for p in sorted(tmp_path.rglob("*")) if p.is_file()}

    inventory.scan(tmp_path)

    after = {p: p.stat().st_mtime_ns for p in sorted(tmp_path.rglob("*")) if p.is_file()}
    assert before == after
