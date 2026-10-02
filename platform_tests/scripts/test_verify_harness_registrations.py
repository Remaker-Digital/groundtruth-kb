"""No registration names a role, and every GT-KB launcher template runs (c123; batch design WP2 2.1 to 2.3, G1).

The fixture is c121's nine installed rows (GET /v1/harnesses on that install). They select roles through
``--skill bridge-review`` and role-named dispatch tags, F and G name models routing.toml has no row for, F, D and H
carry neither the init line nor the bridge target, and B's headless Claude Code argv lacks the dispatched permission
posture (c123; batch design WP2 2.4, owner decisions B1 and B5). The corrected rows of the design's table yield no
finding, and each GT-KB template parses with its own launcher's parser. The same script reads the installed authority
in the installed-product qualification.
"""

from __future__ import annotations

import copy
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "platform_tests" / "fixtures" / "harness_registrations_c121.json"
PYTHON = "groundtruth-kb/.venv/Scripts/python.exe"
BRIDGE = ["--init", "{{INIT_LINE}}", "--bridge-document", "{{DOCUMENT}}", "--bridge-version", "{{VERSION}}"]
# c123 (owner decision B1): B's dispatched posture with B5's setting sources, as `claude --help` spells it on 2.1.281.
POSTURE = [
    "--permission-mode",
    "bypassPermissions",
    "--setting-sources",
    "project",
    "--strict-mcp-config",
    "--disallowedTools",
    "WebFetch,WebSearch",
]
CORRECTED_ARGV = {
    "B": ["claude", "--model", "claude-sonnet-5", "--effort", "max", *POSTURE, "-p", "{{PROMPT}}"]
    + ["--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"],
    "D": [PYTHON, "scripts/ollama_harness.py", *BRIDGE, "--report", "{{REPORT}}", "-p", "{{PROMPT}}"]
    + ["--model", "deepseek-v4-flash-cloud"],
    "E": [PYTHON, "scripts/cursor_harness.py", "-p", "{{PROMPT}}"],
    "F": [PYTHON, "scripts/openrouter_harness.py", *BRIDGE, "--report", "{{REPORT}}", "-p", "{{PROMPT}}"]
    + ["--model", "deepseek-v4-flash"],
    "G": [PYTHON, "scripts/goose_harness.py", "-p", "{{PROMPT}}", "--model", "goose-deepseek-v4-pro"],
    "H": [PYTHON, "scripts/alibaba_cloud_studio_harness.py", *BRIDGE, "--report", "{{REPORT}}"]
    + ["--prompt", "{{PROMPT}}", "--model", "alibaba-deepseek-v4-pro"],
}
CORRECTED_TAGS = {
    "A": ["event-source"],
    "B": [],
    "C": [],
    "D": ["low-cost"],
    "E": [],
    "F": ["low-cost"],
    "G": ["alibaba-deepseek"],
    "H": ["alibaba-cloud-studio"],
}


@pytest.fixture(scope="module")
def verifier():
    """The verifier module, imported with sys.path restored (it adds the project root)."""
    saved = list(sys.path)
    try:
        return importlib.import_module("scripts.verify_harness_registrations")
    finally:
        sys.path[:] = saved


def _c121_records() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]


def _corrected_records() -> list[dict]:
    records = copy.deepcopy(_c121_records())
    for record in records:
        surfaces = record["invocation_surfaces"]
        if record["id"] in CORRECTED_TAGS:
            surfaces["dispatch"]["dispatch_tags"] = CORRECTED_TAGS[record["id"]]
        if record["id"] in CORRECTED_ARGV:
            surfaces["headless"]["argv"] = CORRECTED_ARGV[record["id"]]
    return records


def _codes(result: dict) -> dict[str, set[str]]:
    return {row["id"]: {finding["code"] for finding in row["findings"]} for row in result["rows"]}


def test_the_c121_rows_select_roles_and_unrouted_models(verifier):
    codes = _codes(verifier.evaluate(_c121_records(), ROOT))
    assert all("skill_selector" in codes[host] for host in "DEFGH")
    assert all("role_value" in codes[host] for host in "ABCDEFGH")
    assert all("model_route_unresolved" in codes[host] for host in "FG")
    assert all({"init_placeholder_missing", "bridge_target_placeholders_missing"} <= codes[host] for host in "DFH")
    assert "permission_posture_unmet" in codes["B"]
    assert all("permission_posture_unmet" not in codes[host] for host in "ACDEFGHI")
    assert codes["I"] == set(), "I's manual surface already binds through --init and names no role"


def test_b_rows_posture_finding_names_what_the_c121_argv_lacks(verifier):
    """c123 (batch design WP2 2.4): the operator's verifier applies the Claude verifier's posture rule to B's row."""
    rows = {row["id"]: row for row in verifier.evaluate(_c121_records(), ROOT)["rows"]}
    posture = [finding for finding in rows["B"]["findings"] if finding["code"] == "permission_posture_unmet"]
    assert len(posture) == 1 and posture[0]["path"] == "headless.argv"
    assert posture[0]["detail"].split("; ") == [
        "no --permission-mode bypassPermissions",
        "no --strict-mcp-config",
        "WebFetch and WebSearch are not disallowed (--disallowedTools WebFetch,WebSearch)",
        "no --setting-sources project",
    ]


@pytest.mark.parametrize(
    ("surface", "argv", "finding"),
    [
        ("headless", ["claude", *POSTURE, "-p", "{{PROMPT}}"], False),
        ("headless", ["C:/Users/owner/.local/bin/claude.exe", *POSTURE[:-2], "-p", "{{PROMPT}}"], True),
        ("headless", ["claude", *POSTURE, "--bare", "-p", "{{PROMPT}}"], True),
        ("headless", ["claude", *POSTURE, "--dangerously-skip-permissions", "-p", "{{PROMPT}}"], True),
        ("interactive", ["claude"], False),
    ],
    ids=["posture", "path_form_without_web_denials", "bare", "second_spelling", "not_the_headless_surface"],
)
def test_the_posture_rule_follows_the_claude_cli_in_the_headless_surface(verifier, surface, argv, finding):
    """H registers as harness_type claude but runs a GT-KB launcher; the rule follows the program the argv runs."""
    record = {"id": "B", "harness_type": "claude", "invocation_surfaces": {surface: {"argv": argv}}}
    codes = _codes(verifier.evaluate([record], ROOT))["B"]
    assert ("permission_posture_unmet" in codes) is finding, codes


def test_the_corrected_rows_yield_no_finding_and_every_template_parses(verifier):
    result = verifier.evaluate(_corrected_records(), ROOT)
    assert result["passed"], json.dumps([row for row in result["rows"] if row["findings"]], indent=1)
    assert result["authority_writes"] == 0


@pytest.mark.parametrize("host", ["D", "F", "H"])
def test_the_bridge_target_reaches_each_api_launcher_parser(verifier, host):
    argv = CORRECTED_ARGV[host]
    launcher = verifier.LAUNCHERS[argv[1]]
    arguments = verifier.render(argv[2:], verifier.sample_values(str(ROOT)))
    parsed = launcher.parser().parse_args(arguments)
    assert (parsed.bridge_document, parsed.bridge_version) == ("readiness-probe", 1)
    assert parsed.init == "::init gtkb lo"


def test_a_goose_row_without_a_model_is_a_finding(verifier):
    records = _corrected_records()
    goose = next(record for record in records if record["id"] == "G")
    goose["invocation_surfaces"]["headless"]["argv"] = [PYTHON, "scripts/goose_harness.py", "-p", "{{PROMPT}}"]
    assert "model_route_unresolved" in _codes(verifier.evaluate(records, ROOT))["G"]


def test_the_cli_reads_a_rows_file_and_exits_by_the_findings(verifier, tmp_path, capsys):
    c121, corrected = tmp_path / "c121.json", tmp_path / "corrected.json"
    c121.write_text(json.dumps({"records": _c121_records()}), encoding="utf-8")
    corrected.write_text(json.dumps(_corrected_records()), encoding="utf-8")
    assert verifier.main(["--rows", str(c121), "--project-root", str(ROOT)]) == 1
    assert verifier.main(["--rows", str(corrected), "--project-root", str(ROOT)]) == 0
    capsys.readouterr()
    assert verifier.main(["--rows", str(tmp_path / "absent.json"), "--project-root", str(ROOT)]) == 2
    assert json.loads(capsys.readouterr().out)["passed"] is False
