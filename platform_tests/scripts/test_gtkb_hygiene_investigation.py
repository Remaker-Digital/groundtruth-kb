"""Spec-derived tests for the FAB-20 gtkb-hygiene-investigation slice (WI-4432).

One consolidated module covering all three GO acceptance surfaces:

1. Baseline registry loader (``scripts/hygiene/hygiene_baseline.py``) — GOV-08,
   GOV-STANDING-BACKLOG-001: the HYG-001..068 baseline loads and enumerates.
2. Chunked report generator (``scripts/hygiene/hygiene_report.py``) —
   SPEC-DSI-DOCTOR-CHECK-001: renders size-bounded chunks and a work-item-routable
   form, with no bulk MemBase mutation and no FAB-19/delta consumer.
3. Orchestration skill + Codex adapter parity — GOV-ARTIFACT-ORIENTED-GOVERNANCE-001:
   the SKILL.md packages the structured schema + 4-round workflow + loop-until-dry
   decay disclosure, and the Codex adapter is generated with green parity.

Modules are loaded by file location per the platform_tests convention.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HYGIENE_DIR = REPO_ROOT / "scripts" / "hygiene"
BASELINE_MODULE_PATH = HYGIENE_DIR / "hygiene_baseline.py"
REPORT_MODULE_PATH = HYGIENE_DIR / "hygiene_report.py"
REGISTRY_PATH = REPO_ROOT / "config" / "governance" / "hygiene-baseline-registry.toml"
SKILL_PATH = REPO_ROOT / ".claude" / "skills" / "gtkb-hygiene-investigation" / "SKILL.md"
CODEX_ADAPTER_PATH = REPO_ROOT / ".codex" / "skills" / "gtkb-hygiene-investigation" / "SKILL.md"
CAPABILITY_REGISTRY_PATH = REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"

EXPECTED_IDS = [f"HYG-{n:03d}" for n in range(1, 69)]
VALID_CLASSES = {"defect", "debt", "decision-needed", "drift"}
VALID_RATINGS = {"High", "Medium", "Low"}


def _load(name: str, path: Path):
    # Ensure the hygiene dir is importable so hygiene_report's sibling import resolves.
    if str(HYGIENE_DIR) not in sys.path:
        sys.path.insert(0, str(HYGIENE_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _compact(text: str) -> str:
    """Lowercase + collapse whitespace so markdown line-wraps do not break substring checks."""
    return " ".join(text.lower().split())


hb = _load("hygiene_baseline", BASELINE_MODULE_PATH)
hr = _load("hygiene_report", REPORT_MODULE_PATH)


# ---------------------------------------------------------------------------
# 1. Baseline registry loader
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def registry():
    return hb.load_baseline()


def test_registry_file_exists() -> None:
    assert REGISTRY_PATH.is_file()


def test_loads_sixty_eight_findings(registry) -> None:
    assert len(registry) == 68


def test_ids_are_contiguous_hyg_001_to_068(registry) -> None:
    assert registry.ids() == EXPECTED_IDS


def test_every_finding_has_valid_class_and_title(registry) -> None:
    for finding in registry.findings:
        assert finding.finding_class in VALID_CLASSES, finding.id
        assert finding.title and finding.title.strip(), finding.id


def test_ratings_use_allowed_vocabulary(registry) -> None:
    for finding in registry.findings:
        for rating in (finding.impact, finding.effort, finding.confidence):
            if rating is not None:
                assert rating in VALID_RATINGS, (finding.id, rating)


def test_embedded_quotes_survive_toml_escaping(registry) -> None:
    by_id = {f.id: f for f in registry.findings}
    assert '"claude", "codex"' in by_id["HYG-063"].title


def test_empty_string_fields_load_as_none(registry) -> None:
    by_id = {f.id: f for f in registry.findings}
    assert by_id["HYG-007"].fab_cluster is None
    assert by_id["HYG-061"].decision_complexity is None


def test_owner_touchpoint_flag_round_trips(registry) -> None:
    by_id = {f.id: f for f in registry.findings}
    assert by_id["HYG-001"].owner_touchpoint_required is True
    assert by_id["HYG-061"].owner_touchpoint_required is False


def test_registry_metadata(registry) -> None:
    assert registry.schema_version == 1
    assert registry.baseline_id == "HYG-BASELINE-2026-06-10"
    assert len(registry.source_reports) == 2


def test_to_dict_is_json_serializable(registry) -> None:
    payload = registry.to_dict()
    encoded = json.dumps(payload)
    assert payload["finding_count"] == 68
    assert json.loads(encoded)["findings"][0]["id"] == "HYG-001"


def test_missing_registry_raises(tmp_path: Path) -> None:
    with pytest.raises(hb.BaselineRegistryError):
        hb.load_baseline(tmp_path / "missing.toml")


# ---------------------------------------------------------------------------
# 2. Chunked report generator
# ---------------------------------------------------------------------------


def _finding(**kwargs):
    base = {"id": "HYG-900", "title": "synthetic finding", "finding_class": "drift"}
    base.update(kwargs)
    return hb.HygieneFinding(**base)


def test_render_finding_emits_present_fields() -> None:
    finding = _finding(
        id="HYG-901",
        title="example title",
        finding_class="defect",
        locations=("path/to/file.py:10",),
        verification="ran the command",
        impact="High",
        effort="Low",
        confidence="High",
        owner_touchpoint_required=True,
        owner_question="Option 1 vs 2?",
        proposed_approach="do the minimal fix",
    )
    rendered = hr.render_finding(finding)
    assert "HYG-901" in rendered
    assert "example title" in rendered
    assert "Class: defect" in rendered
    assert "path/to/file.py:10" in rendered
    assert "ran the command" in rendered
    assert "Option 1 vs 2?" in rendered


def test_chunks_respect_size_bound_and_cover_all_findings() -> None:
    findings = [_finding(id=f"HYG-{n:03d}", title=f"finding number {n}") for n in range(1, 41)]
    max_chars = 800
    chunks = hr.generate_report_chunks(findings, max_chars=max_chars)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= max_chars
    joined = "\n".join(chunks)
    for finding in findings:
        assert finding.id in joined


def test_empty_corpus_returns_single_chunk() -> None:
    chunks = hr.generate_report_chunks([])
    assert len(chunks) == 1
    assert "No findings" in chunks[0]


def test_max_chars_below_header_reserve_raises() -> None:
    with pytest.raises(ValueError):
        hr.generate_report_chunks([_finding()], max_chars=10)


def test_finding_to_work_item_is_backlog_routable() -> None:
    finding = _finding(
        id="HYG-902",
        title="routable finding",
        finding_class="debt",
        fab_cluster="FAB-19",
        problem_statement="something is wrong",
    )
    wi = hr.finding_to_work_item(finding)
    assert set(wi) >= {"title", "origin", "component", "change_reason", "description"}
    assert wi["origin"] == "hygiene"
    assert wi["component"] == "FAB-19"
    assert wi["source_finding_id"] == "HYG-902"
    assert wi["title"] == "routable finding"


def test_finding_to_work_item_defaults_component_without_cluster() -> None:
    wi = hr.finding_to_work_item(_finding(fab_cluster=None))
    assert wi["component"] == "gtkb-platform"


def test_report_module_performs_no_bulk_mutation_or_fab19_consumer() -> None:
    # AST-based so docstring/comment prose (which legitimately MENTIONS these to
    # say it does NOT do them) cannot trip the check; only real code counts.
    tree = ast.parse(REPORT_MODULE_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for forbidden in ("subprocess", "sqlite3", "groundtruth_kb"):
        assert forbidden not in imported, forbidden
    func_names = [n.name.lower() for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert not any("delta" in name or "evidence_pack" in name for name in func_names)


def test_baseline_renders_through_generator(registry) -> None:
    chunks = hr.generate_report_chunks(registry.findings)
    joined = "\n".join(chunks)
    for finding in registry.findings:
        assert finding.id in joined


# ---------------------------------------------------------------------------
# 3. Orchestration skill + Codex adapter parity
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_skill_frontmatter(skill_text: str) -> None:
    assert skill_text.lstrip().startswith("---")
    assert "name: gtkb-hygiene-investigation" in skill_text
    assert "description:" in skill_text


def test_skill_documents_structured_findings_schema(skill_text: str) -> None:
    for field_name in ("finding_class", "locations", "verification", "owner_touchpoint_required"):
        assert field_name in skill_text, field_name


def test_skill_documents_four_round_workflow(skill_text: str) -> None:
    compact = _compact(skill_text)
    assert "parallel focus-area probe" in compact
    assert "gap probe" in compact
    assert "completeness critic" in compact
    assert "adversarial skeptic" in compact


def test_skill_documents_loop_until_dry_with_decay_disclosure(skill_text: str) -> None:
    compact = _compact(skill_text)
    assert "loop-until-dry" in compact
    assert "decay disclosure" in compact


def test_skill_defers_delta_mode(skill_text: str) -> None:
    compact = _compact(skill_text)
    assert "deferred follow-on" in compact
    assert "delta mode" in compact
    assert "does not implement" in compact


def test_skill_uses_canonical_role_registry_not_retired_mirror(skill_text: str) -> None:
    assert "harness_projection" in skill_text
    # The retired role-assignments.json mirror must not be referenced.
    assert "role-assignments.json" not in skill_text


def test_codex_adapter_generated_with_marker(skill_text: str) -> None:
    assert CODEX_ADAPTER_PATH.is_file()
    adapter = CODEX_ADAPTER_PATH.read_text(encoding="utf-8")
    assert "GTKB-CODEX-SKILL-ADAPTER" in adapter
    assert "Canonical source: .claude/skills/gtkb-hygiene-investigation/SKILL.md" in adapter


def test_capability_registry_entry_and_codex_parity() -> None:
    data = tomllib.loads(CAPABILITY_REGISTRY_PATH.read_text(encoding="utf-8"))
    entry = next(
        (cap for cap in data.get("capabilities", []) if cap.get("id") == "skill.gtkb-hygiene-investigation"),
        None,
    )
    assert entry is not None, "capability registry entry missing"
    assert entry["canonical_source"] == ".claude/skills/gtkb-hygiene-investigation/SKILL.md"
    assert "prime-builder" in entry["required_for_roles"]
    codex = entry["codex"]
    assert codex["adapter_source"] == ".claude/skills/gtkb-hygiene-investigation/SKILL.md"
    sha = codex["source_sha256"]
    assert sha != "pending-generation"
    assert len(sha) == 64 and all(c in "0123456789abcdef" for c in sha)
