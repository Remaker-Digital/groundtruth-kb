# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for verdict-side Prior Deliberations seeding."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
PROPOSE_HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"


def _load_module(name: str, path: Path):
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def verify_helper():
    return _load_module("verify_write_verdict_under_test", VERIFY_HELPER_PATH)


@pytest.fixture()
def propose_helper():
    return _load_module("bridge_propose_helper_for_verify_seed_test", PROPOSE_HELPER_PATH)


class FakeKnowledgeDB:
    def __init__(self) -> None:
        self.queries: list[tuple[str, int]] = []

    def search_deliberations(self, query: str, *, limit: int):
        self.queries.append((query, limit))
        return [
            {"id": "DELIB-0001", "source_type": "bridge_thread", "title": "Duplicate glossary seed"},
            {"id": "DELIB-0002", "source_type": "owner_decision", "title": "Verdict seeding decision"},
        ]


def _glossary(tmp_path: Path) -> Path:
    path = tmp_path / "canonical-terminology.md"
    path.write_text(
        "### Sample Verdict\n\n**Source:** `DELIB-0001`; `GOV-SAMPLE-001`\n",
        encoding="utf-8",
    )
    return path


def _verdict_body() -> str:
    return (
        "VERIFIED\n\n"
        "# Loyal Opposition Verification\n\n"
        "## Applicability Preflight\n\n"
        "passed\n\n"
        "## Prior Deliberations\n\n"
        "## Specifications Carried Forward\n\n"
        "- `GOV-SAMPLE-001`\n"
    )


def test_verdict_helper_seeds_prior_deliberations_without_bleeding_into_next_section(
    verify_helper,
    tmp_path,
):
    log_path = tmp_path / ".gtkb-state" / "bridge-verify-helper" / "last-prepopulation.json"

    seeded = verify_helper.seed_prior_deliberations(
        "sample-verdict",
        _verdict_body(),
        db=FakeKnowledgeDB(),
        glossary_path=_glossary(tmp_path),
        log_path=log_path,
    )

    prior_section = seeded.split("## Specifications Carried Forward", 1)[0]
    following_section = seeded.split("## Specifications Carried Forward", 1)[1]
    assert "<!-- Pre-populated by helper; review and prune. -->" in prior_section
    assert "`DELIB-0001`" in prior_section
    assert "`GOV-SAMPLE-001`" in prior_section
    assert "`DELIB-0002`" in prior_section
    assert "<!-- Pre-populated by helper; review and prune. -->" not in following_section


def test_verdict_helper_uses_verify_log_namespace(verify_helper, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    verify_helper.seed_prior_deliberations(
        "sample-verdict",
        _verdict_body(),
        db=False,
        glossary_path=_glossary(tmp_path),
    )

    verify_log = tmp_path / ".gtkb-state" / "bridge-verify-helper" / "last-prepopulation.json"
    propose_log = tmp_path / ".gtkb-state" / "bridge-propose-helper" / "last-prepopulation.json"
    assert verify_log.exists()
    assert not propose_log.exists()
    log_data = json.loads(verify_log.read_text(encoding="utf-8"))
    assert log_data["topic_slug"] == "sample-verdict"
    assert log_data["semantic_search_attempted"] is False


def test_verdict_helper_preserves_body_when_opted_out(verify_helper):
    body = _verdict_body()

    assert verify_helper.seed_prior_deliberations("sample-verdict", body, pre_populate=False) == body


def test_propose_and_verdict_helpers_share_identical_seeding_output(
    verify_helper,
    propose_helper,
    tmp_path,
):
    body = _verdict_body()
    glossary = _glossary(tmp_path)
    db = FakeKnowledgeDB()

    verdict_seeded = verify_helper.seed_prior_deliberations(
        "sample-verdict",
        body,
        db=db,
        glossary_path=glossary,
        log_path=False,
    )
    propose_seeded = propose_helper.pre_populate_prior_deliberations(
        "sample-verdict",
        body,
        db=FakeKnowledgeDB(),
        glossary_path=glossary,
        log_path=False,
    )

    assert verdict_seeded == propose_seeded
    assert propose_helper.pre_populate_prior_deliberations is verify_helper.pre_populate_prior_deliberations


def test_novel_verdict_topic_gets_explicit_placeholder(verify_helper, tmp_path):
    seeded = verify_helper.seed_prior_deliberations(
        "novel-verdict-topic",
        _verdict_body(),
        db=False,
        glossary_path=_glossary(tmp_path),
        log_path=False,
    )

    assert verify_helper.pre_populate_prior_deliberations.__module__ == "groundtruth_kb.bridge.prior_deliberations"
    assert "_No prior deliberations: <fill in reason before filing>._" in seeded
