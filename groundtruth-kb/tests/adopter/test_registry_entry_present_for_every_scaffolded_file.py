"""Every created application path is classified: application-owned by profile/option, or projector-owned."""

from __future__ import annotations

import json

from groundtruth_kb.project.scaffold import application_files, enumerate_scaffold_outputs

OPTIONAL_OWNED = {
    ".github/workflows/test.yml",
    ".github/workflows/build.yml",
    ".github/workflows/deploy.yml",
    ".github/dependabot.yml",
    ".coderabbitai.yaml",
    "src/tasks.py",
    "tests/test_tasks.py",
    "src/__init__.py",
    "tests/__init__.py",
}


def test_every_scaffolded_file_is_owned_or_projected(native_application) -> None:
    native_application.stage_baseline()
    target = native_application.scaffold(
        "Alpha",
        profile="dual-agent-webapp",
        include_ci=True,
        seed_example=True,
        integrations=True,
        harnesses=("claude",),
    )
    owned = set(enumerate_scaffold_outputs("dual-agent-webapp")) | OPTIONAL_OWNED | {"application.toml"}
    manifest = json.loads((target / ".claude/.projection-manifest.json").read_text(encoding="utf-8"))
    projected = set(manifest["paths"])
    unclassified = sorted(path for path in application_files(target) if path not in owned and path not in projected)
    assert not unclassified, unclassified
    assert projected <= application_files(target)
    assert not (owned & projected), "a path is either application-owned or projector-owned, never both"
