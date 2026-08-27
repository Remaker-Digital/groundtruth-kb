"""Tests for the WI-5895 backward-walk target_paths resolver in the auto-finalization sweep.

Covers:
- report-only declaration resolves (report-first behaviour preserved).
- proposal-only declaration resolves via the backward chain walk.
- no-declaration chain yields the distinct skip reason and does not raise.
- the resolver never reaches outside its own slug's chain.

Fixtures bind to ``tmp_path`` bridge chains; canonical bridge state is never touched.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "auto_finalize_sweep.py"

_PROPOSAL_BODY = """NEW
# Proposal
target_paths: ["scripts/a.py", "platform_tests/scripts/test_a.py"]
"""

_REPORT_BODY = """NEW
# Report
## Files Changed
- scripts/a.py
"""

_VERDICT_BODY = """VERIFIED
# Verdict
"""


def _load_module():
    spec = importlib.util.spec_from_file_location("auto_finalize_sweep", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["auto_finalize_sweep"] = module
    spec.loader.exec_module(module)
    return module


def _write_bridge(tmp_path: Path, slug: str, version: int, body: str) -> None:
    path = tmp_path / "bridge" / f"{slug}-{version:03d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _bind_tmp_read(module, tmp_path: Path) -> None:
    def _read(rel: str) -> str | None:
        try:
            return (tmp_path / rel).read_text(encoding="utf-8")
        except OSError:
            return None

    module._read = _read


def test_report_only_declaration_resolves(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    _bind_tmp_read(module, tmp_path)
    slug = "gtkb-test-report-only"
    # report carries a parseable target_paths declaration (report-first step).
    _write_bridge(tmp_path, slug, 2, 'NEW\n# Report\ntarget_paths: ["scripts/a.py"]\n')
    _write_bridge(tmp_path, slug, 3, _VERDICT_BODY)
    verdict_rel = f"bridge/{slug}-003.md"
    report_rel = f"bridge/{slug}-002.md"

    targets, why = module._target_paths_from_chain(slug, verdict_rel, report_rel)

    assert targets == ["scripts/a.py"]
    assert why == "report"


def test_proposal_only_declaration_resolves_via_backward_walk(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    _bind_tmp_read(module, tmp_path)
    slug = "gtkb-test-backward-walk"
    # proposal (v001) declares target_paths; report (v002) and verdict (v003) do not.
    _write_bridge(tmp_path, slug, 1, _PROPOSAL_BODY)
    _write_bridge(tmp_path, slug, 2, _REPORT_BODY)
    _write_bridge(tmp_path, slug, 3, _VERDICT_BODY)
    verdict_rel = f"bridge/{slug}-003.md"
    report_rel = f"bridge/{slug}-002.md"

    targets, why = module._target_paths_from_chain(slug, verdict_rel, report_rel)

    assert targets == ["scripts/a.py", "platform_tests/scripts/test_a.py"]
    assert why == "backward-walk v001"


def test_no_declaration_chain_yields_distinct_skip_reason(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    _bind_tmp_read(module, tmp_path)
    slug = "gtkb-test-no-decl"
    _write_bridge(tmp_path, slug, 1, "NEW\n# Proposal\n## Files Changed\n- scripts/x.py\n")
    _write_bridge(tmp_path, slug, 2, _REPORT_BODY)
    _write_bridge(tmp_path, slug, 3, _VERDICT_BODY)
    verdict_rel = f"bridge/{slug}-003.md"
    report_rel = f"bridge/{slug}-002.md"

    targets, why = module._target_paths_from_chain(slug, verdict_rel, report_rel)

    assert targets is None
    assert why == "no target_paths anywhere in chain"


def test_resolver_never_reaches_outside_its_own_slug_chain(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    _bind_tmp_read(module, tmp_path)
    slug = "gtkb-test-isolated"
    other_slug = "gtkb-test-other"
    # A different slug's chain carries a parseable target_paths declaration.
    _write_bridge(tmp_path, other_slug, 1, _PROPOSAL_BODY)
    _write_bridge(tmp_path, slug, 1, "NEW\n# Proposal\n## Files Changed\n- scripts/y.py\n")
    _write_bridge(tmp_path, slug, 2, _REPORT_BODY)
    _write_bridge(tmp_path, slug, 3, _VERDICT_BODY)
    verdict_rel = f"bridge/{slug}-003.md"
    report_rel = f"bridge/{slug}-002.md"

    targets, why = module._target_paths_from_chain(slug, verdict_rel, report_rel)

    assert targets is None
    assert why == "no target_paths anywhere in chain"
