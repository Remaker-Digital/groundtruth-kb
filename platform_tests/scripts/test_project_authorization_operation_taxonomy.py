"""Regression tests for the operation-taxonomy baseline path rules.

Landed by bridge/gtkb-operation-taxonomy-baseline-path-rules (GO at -002 with
binding conditions). The two ``[[path_rule]]`` entries registering the neutral
baseline (``.harness-baseline-configuration/**``) and the predecessor baseline
being retired (``.agents/**``) as ``configuration``-class targets exist so the
operation-time evaluator can authorize work inside those directories instead of
failing closed on the ``unclassified`` mutation class — the F1 blocking defect
of bridge/gtkb-baseline-correction-and-goose-projector-slice-1-002.md.

The fail-closed default for unregistered paths is itself load-bearing and is
asserted here alongside the new classifications.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.governance.project_authorization_operation_time import (  # noqa: E402
    classify_target,
    load_operation_taxonomy,
)


@pytest.fixture(scope="module")
def taxonomy():
    return load_operation_taxonomy(PROJECT_ROOT)


# Representative concrete paths cover every extension class present in the two
# trees at classification time (markdown, python, toml, json, extensionless),
# because the F1 alternative (extension-scoped globs) failed precisely on the
# extensions without classifier fallbacks (.md, .json).
BASELINE_PATHS = [
    ".harness-baseline-configuration/**",
    ".harness-baseline-configuration/rules/file-bridge-protocol.md",
    ".harness-baseline-configuration/hooks/assertion-check.py",
    ".harness-baseline-configuration/rules/canonical-terminology.toml",
    ".harness-baseline-configuration/commands/registry.json",
    ".harness-baseline-configuration/skills/gtkb-verify/SKILL.md",
    ".agents/**",
    ".agents/rules/bridge-essential.md",
    ".agents/hooks/credential-scan.py",
    ".agents/settings.json",
    ".agents/skills/gtkb-bridge/helpers/scan_bridge.py",
]


@pytest.mark.parametrize("path", BASELINE_PATHS)
def test_baseline_paths_classify_as_configuration(taxonomy, path):
    classified = classify_target(path, taxonomy)
    assert classified.mutation_class == "configuration", (
        f"{path} classified as {classified.mutation_class!r}; the baseline "
        "path rules must classify both baseline trees as configuration"
    )


def test_unknown_dot_directory_glob_still_unclassified(taxonomy):
    """The amendment must not loosen the fail-closed default for unknown trees.

    Scope note learned during red-first execution: classification operates on
    the PATTERN TEXT, and global extension fallbacks exist (``.md``/``.json``/
    ``.jsonl`` -> ``governance_evidence``; ``.py`` etc. -> ``source``;
    ``.toml``/``.yaml``/``.yml`` -> ``configuration``) regardless of tree. The
    genuinely fail-closed surface is therefore extensionless forms — ``**``
    globs and bare paths — which is exactly the form ``target_paths`` arrays
    use. These must stay unclassified for unregistered trees.
    """
    for path in (
        ".nonexistent-tree/**",
        ".some-future-dir/**",
        ".harness-baseline-configuration-backup/**",
        ".nonexistent-tree/subdir/extensionless-file",
    ):
        classified = classify_target(path, taxonomy)
        assert classified.mutation_class == "unclassified", (
            f"{path} classified as {classified.mutation_class!r}; unregistered "
            "extensionless dot-directory patterns must remain unclassified "
            "(fail-closed)"
        )


def test_path_rules_present_in_taxonomy(taxonomy):
    """The registration is data-side ([[path_rule]]), not a code change."""
    patterns = {rule.pattern for rule in taxonomy.path_rules}
    assert ".harness-baseline-configuration/**" in patterns
    assert ".agents/**" in patterns
    for rule in taxonomy.path_rules:
        if rule.pattern in {".harness-baseline-configuration/**", ".agents/**"}:
            assert rule.mutation_class == "configuration"
