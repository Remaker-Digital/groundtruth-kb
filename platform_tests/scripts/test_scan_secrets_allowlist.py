"""The pre-commit secret scan's synthetic allowlist (``scripts/scan_secrets.py``).

The gate refused the program's central commit on 2026-09-17 with candidate findings that
were all synthetic (CI dummy values, redaction test fixtures, runtime-generated tokens).
``config/governance/secret-scan-allowlist.toml`` attests such lines by exact identity: path
plus SHA-256 of the line's exact text. These cases pin the contract that keeps the
allowlist from weakening detection:

- a real-looking secret is refused whether or not an allowlist exists;
- an attested line is accepted and reported as "allowlisted (synthetic)" with its identity
  and rationale, and only that exact line in that exact path is covered;
- an entry whose line changed is stale, is reported, and fails the gate;
- ``--staged`` reads the allowlist from the index, never from an unstaged working copy;
- a malformed allowlist fails closed;
- every entry in the tracked allowlist matches a live line of this tree.

Sample values are assembled at runtime so no provider-shaped contiguous text is committed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.governance.commit_preflight import preflight_exit_code, run_commit_preflight
from groundtruth_kb.secrets import scan_paths
from groundtruth_kb.secrets.patterns import PatternEntry, Severity

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "scan_secrets.py"
ALLOWLIST = "config/governance/secret-scan-allowlist.toml"
TOKEN = "AK" + "IA" + "R" * 16  # candidate-high shape, assembled at runtime
FIXTURE = "tests/test_redaction_fixture.py"
FIXTURE_LINE = f'    report = build(notes="uses key {TOKEN}")  # redaction fixture'
FIXTURE_TEXT = f"def test_report_strips_the_key():\n{FIXTURE_LINE}\n    assert report.clean\n"


def _load_gate():
    spec = importlib.util.spec_from_file_location("scan_secrets_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


gate = _load_gate()


def identity(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def allowlist_text(*entries: tuple[str, str, str]) -> str:
    lines = ["schema_version = 1"]
    for path, digest, rationale in entries:
        lines += ["", "[[entries]]", f'path = "{path}"', f'line_sha256 = "{digest}"', f'rationale = "{rationale}"']
    return "\n".join(lines) + "\n"


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=check, timeout=60)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "config", "user.email", "test@invalid.example")
    git(tmp_path, "config", "user.name", "Allowlist Test")
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    return tmp_path


def write(root: Path, name: str, content: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def stage(root: Path, name: str, content: str) -> None:
    write(root, name, content)
    git(root, "add", "--", name)


def scan(root: Path, *args: str) -> tuple[int, dict, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    combined = result.stdout + result.stderr
    assert TOKEN not in combined, "raw sample value leaked into scanner output"
    payload = json.loads(result.stdout) if result.stdout.strip() else json.loads(result.stderr)
    return result.returncode, payload, combined


def test_real_looking_secret_is_refused_with_and_without_an_allowlist(repo: Path) -> None:
    stage(repo, "src/config.py", f'token = "{TOKEN}"\n')
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["allowlist_source"]) == (1, "fail", "index")
    assert [f["severity"] for f in payload["findings"]] == ["candidate-high"]
    assert (payload["allowlisted_count"], payload["stale_allowlist_count"]) == (0, 0)

    stage(repo, FIXTURE, FIXTURE_TEXT)
    stage(repo, ALLOWLIST, allowlist_text((FIXTURE, identity(FIXTURE_LINE), "redaction fixture")))
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"]) == (1, "fail")
    assert [(f["path"], f["severity"]) for f in payload["findings"]] == [("src/config.py", "candidate-high")]
    assert [f["path"] for f in payload["allowlisted"]] == [FIXTURE]


def test_allowlisted_synthetic_line_is_accepted_and_reported_with_its_identity(repo: Path) -> None:
    stage(repo, FIXTURE, FIXTURE_TEXT)
    stage(repo, ALLOWLIST, allowlist_text((FIXTURE, identity(FIXTURE_LINE), "synthetic AKIA-shaped fixture")))
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["mode"]) == (0, "pass", "staged")
    assert (payload["finding_count"], payload["findings"], payload["stale_allowlist"]) == (0, [], [])
    assert payload["allowlist_path"] == ALLOWLIST
    assert payload["allowlisted_count"] == 1
    assert payload["allowlisted"] == [
        {
            "provider_class": "AWS Access Key",
            "severity": "candidate-high",
            "path": FIXTURE,
            "line": 2,
            "fingerprint_prefix": "sha256:" + hashlib.sha256(TOKEN.encode()).hexdigest()[:8],
            "description": "AWS Access Key",
            "disposition": "allowlisted (synthetic)",
            "line_sha256": identity(FIXTURE_LINE),
            "rationale": "synthetic AKIA-shaped fixture",
        }
    ]


def test_an_entry_covers_only_its_exact_line_in_its_exact_path(repo: Path) -> None:
    entry = (FIXTURE, identity(FIXTURE_LINE), "synthetic fixture")
    stage(repo, ALLOWLIST, allowlist_text(entry))
    # Same line text under another path: refused.
    stage(repo, "tests/test_copy.py", FIXTURE_TEXT)
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["allowlisted_count"]) == (1, "fail", 0)
    assert [f["path"] for f in payload["findings"]] == ["tests/test_copy.py"]
    git(repo, "rm", "-q", "--cached", "--", "tests/test_copy.py")
    # The attested line plus a second secret-shaped line in the same file: only the attested line is allowlisted.
    stage(repo, FIXTURE, FIXTURE_TEXT + f'other = "{TOKEN}"\n')
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"]) == (1, "fail")
    assert [(f["path"], f["line"]) for f in payload["findings"]] == [(FIXTURE, 4)]
    assert [(f["path"], f["line"]) for f in payload["allowlisted"]] == [(FIXTURE, 2)]
    assert payload["stale_allowlist"] == []


@pytest.mark.parametrize("still_matches", [True, False])
def test_stale_entry_is_reported_and_refused_when_the_attested_line_changes(repo: Path, still_matches: bool) -> None:
    entry = (FIXTURE, identity(FIXTURE_LINE), "synthetic fixture")
    stage(repo, ALLOWLIST, allowlist_text(entry))
    changed = FIXTURE_LINE + "  # edited" if still_matches else "    report = build(notes=notes)"
    stage(repo, FIXTURE, FIXTURE_TEXT.replace(FIXTURE_LINE, changed))
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"]) == (1, "fail")
    assert payload["allowlisted"] == []
    assert [(f["path"], f["line"], f["severity"]) for f in payload["findings"]] == (
        [(FIXTURE, 2, "candidate-high")] if still_matches else []
    )
    assert payload["stale_allowlist_count"] == 1
    stale = payload["stale_allowlist"][0]
    assert (stale["path"], stale["line_sha256"], stale["rationale"]) == entry
    assert "no finding on this path carries the attested line identity" in stale["reason"]


def test_staged_mode_reads_the_allowlist_from_the_index_not_the_working_tree(repo: Path) -> None:
    stage(repo, FIXTURE, FIXTURE_TEXT)
    write(repo, ALLOWLIST, allowlist_text((FIXTURE, identity(FIXTURE_LINE), "unstaged attestation")))
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["allowlist_source"], payload["allowlisted_count"]) == (
        1,
        "fail",
        "index",
        0,
    )
    git(repo, "add", "--", ALLOWLIST)
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["allowlisted_count"]) == (0, "pass", 1)
    # A staged allowlist governs even when the working copy is later edited away.
    write(repo, ALLOWLIST, allowlist_text())
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["allowlisted_count"]) == (0, "pass", 1)


def test_entry_scope_in_staged_and_tracked_modes(repo: Path) -> None:
    other = ("tests/test_elsewhere.py", identity('x = "' + TOKEN + '"'), "attested line of an unstaged path")
    stage(repo, FIXTURE, FIXTURE_TEXT)
    stage(repo, ALLOWLIST, allowlist_text((FIXTURE, identity(FIXTURE_LINE), "synthetic fixture"), other))
    code, payload, _ = scan(repo, "--staged")
    assert (code, payload["status"], payload["stale_allowlist_count"]) == (0, "pass", 0)
    # The tracked scan evaluates every entry: the path without a matching tracked line is stale.
    code, payload, _ = scan(repo)
    assert (code, payload["status"], payload["mode"], payload["allowlist_source"]) == (
        1,
        "fail",
        "tracked",
        "working-tree",
    )
    assert [(s["path"], s["reason"]) for s in payload["stale_allowlist"]] == [
        (other[0], "the path is not a scanned tracked text file; remove the entry")
    ]
    assert [f["path"] for f in payload["allowlisted"]] == [FIXTURE]


@pytest.mark.parametrize(
    ("text", "detail"),
    [
        ("schema_version = 1\n[[entries]]\npath = 'x'\n", "'line_sha256' must be 64 lowercase hex"),
        ("schema_version = 1\n[[entries]]\npath = 'x'\nline_sha256 = '" + "a" * 64 + "'\n", "'rationale' must say why"),
        (
            "schema_version = 1\n[[entries]]\npath = '../x'\nline_sha256 = '" + "a" * 64 + "'\nrationale = 'r'\n",
            "'path'",
        ),
        ("schema_version = 2\n", "schema_version must be 1"),
        ("entries = [\n", "not valid TOML"),
        (
            "schema_version = 1\n[[entries]]\npath = 'x'\nline_sha256 = '"
            + "a" * 64
            + "'\nrationale = 'r'\nline = 3\n",
            "unknown keys ['line']",
        ),
    ],
)
def test_malformed_allowlist_fails_closed_without_scanning(repo: Path, text: str, detail: str) -> None:
    stage(repo, "src/clean.py", "value = 1\n")
    stage(repo, ALLOWLIST, text)
    code, payload, combined = scan(repo, "--staged")
    assert code == 2
    assert payload["status"] == "error"
    assert payload["reason"] == "secret_scan_allowlist_invalid"
    assert detail in payload["detail"]
    assert '"findings"' not in combined


def test_duplicate_entries_are_rejected() -> None:
    entry = (FIXTURE, identity(FIXTURE_LINE), "r")
    with pytest.raises(gate.AllowlistError, match="duplicates an earlier entry"):
        gate.parse_allowlist(allowlist_text(entry, entry))


def test_commit_preflight_accepts_an_allowlisted_synthetic_fixture(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        ".githooks/pre-commit",
        ".githooks/pre-commit-ps1-parse.ps1",
        "scripts/scan_secrets.py",
        "scripts/check_ruff_format.py",
        "scripts/check_commit_pathspec_safety.py",
        "scripts/check_projection_drift.py",
    ):
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    git(repo, "config", "core.hooksPath", ".githooks")
    monkeypatch.setenv("PYTHON", sys.executable)
    monkeypatch.setenv("PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    stage(repo, FIXTURE, FIXTURE_TEXT)
    stage(repo, ALLOWLIST, allowlist_text((FIXTURE, identity(FIXTURE_LINE), "synthetic fixture")))
    evidence = run_commit_preflight(repo, python_bin=sys.executable)
    secret_scan = next(check for check in evidence.checks if check.name == "secret-scan")
    assert secret_scan.outcome.value == "passed", secret_scan
    assert '"allowlisted_count": 1' in secret_scan.summary
    assert preflight_exit_code(evidence) == 0, evidence
    result = git(repo, "commit", "-qm", "synthetic fixture", check=False)
    assert result.returncode == 0, result.stderr.decode(errors="replace")


def test_tracked_allowlist_entries_are_current_in_this_tree() -> None:
    """Every entry attests an existing line that still carries a candidate-high finding; no dead weight.

    Candidate-medium findings never refuse a commit, so the allowlist does not carry them (builder decision,
    2026-09-17): an entry whose line only matches medium patterns is dead weight and fails here.
    """
    entries = gate.parse_allowlist((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
    assert entries, "the tracked allowlist must carry the attested synthetic lines"
    patterns = tuple(
        PatternEntry(
            name=name,
            pattern=pattern,
            severity=Severity.CANDIDATE_HIGH if severity == "high" else Severity.CANDIDATE_MEDIUM,
            description=name,
        )
        for name, pattern, severity in gate.PATTERNS
    )
    for (path, digest), entry in entries.items():
        target = ROOT / path
        assert target.is_file(), f"{path}: attested path is not in the tree"
        assert path != "config/governance/timer-inventory.toml", (
            "generated outputs leave the tree; they are not attested"
        )
        result = scan_paths([target], repo_root=ROOT, patterns=patterns)
        identities = {finding.line_sha256 for finding in result.findings}
        assert digest in identities, f"{path}: no live finding carries the attested line identity ({entry.rationale})"
        severities = {finding.severity for finding in result.findings if finding.line_sha256 == digest}
        assert Severity.CANDIDATE_HIGH in severities, f"{path}: the attested line is only a candidate-medium finding"
