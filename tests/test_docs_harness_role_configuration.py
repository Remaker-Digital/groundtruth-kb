from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dual_agent_docs_capture_harness_role_configuration_comparison() -> None:
    doc = (ROOT / "docs" / "method" / "06-dual-agent.md").read_text(encoding="utf-8")

    assert "## Harness role configuration comparison" in doc
    assert "The current GroundTruth-KB dual-agent install is asymmetric" in doc
    assert "| Area | Prime Builder configuration | Loyal Opposition configuration |" in doc
    assert "`claude-code` provider" in doc
    assert "`codex` provider" in doc
    assert "Cursor support remains a candidate implementation item" in doc
    assert "No native Codex or Cursor hook-registration parity exists today" in doc
    assert "every installed capable harness should receive role-ready" in doc
