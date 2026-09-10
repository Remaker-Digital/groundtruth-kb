"""The doctor uses exact projection conformance, without a waiver plane."""

import pytest
from groundtruth_kb.project.doctor import _check_harness_projection_conformance


def test_missing_checker_is_a_visible_failure(tmp_path):
    result = _check_harness_projection_conformance(tmp_path)
    assert result.status == "fail"
    assert not result.found


@pytest.mark.parametrize("status", ["pass", "fail"])
def test_doctor_preserves_checker_result_and_limits(tmp_path, status):
    script = tmp_path / "scripts/check_harness_parity.py"
    script.parent.mkdir()
    script.write_text(
        "def check_harness_parity(root, *, harness):\n"
        "    assert harness == 'all'\n"
        f"    return {{'status': '{status}', 'harnesses': {{'example': {{'status': '{status}'}}}}, 'issues': []}}\n",
        encoding="utf-8",
    )
    result = _check_harness_projection_conformance(tmp_path)
    assert result.status == status
    assert "actual hook invocation" in result.message


def test_local_checker_failure_never_becomes_pass(tmp_path):
    script = tmp_path / "scripts/check_harness_parity.py"
    script.parent.mkdir()
    script.write_text("raise ImportError('genuine local failure')\n")
    result = _check_harness_projection_conformance(tmp_path)
    assert result.status == "fail"
    assert "genuine local failure" in result.message
