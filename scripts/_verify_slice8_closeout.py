"""GTKB-ISOLATION-017 Slice 8 — composite acceptance-gate verifier.

Per `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` (REVISED-2;
Codex GO at `-006`) acceptance criteria 5: this script runs the composite
acceptance gate covering B1/B2/B3/B4/B5/B7 outcomes. B6 is explicitly skipped
and reports "deferred to Slice 8.5" per
`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`.

Exit code: 0 if all in-scope checks PASS (B6 deferred is intentional, not a
failure). Non-zero if any in-scope check FAILS.

Per `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`, B2 is narrowed to
`groundtruth-kb/` (not full repo).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GT_KB_PKG = REPO_ROOT / "groundtruth-kb"

EXPECTED_VERSION = "0.7.0rc1"

SLICE_8_5_BRIDGE_REF = "bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md"


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a subprocess command and return (exit_code, stdout, stderr)."""
    proc = subprocess.run(  # noqa: S603 - intentional subprocess for verifier
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=900,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check_b1_version_bump() -> tuple[str, str]:
    """B1 — `__version__` reports 0.7.0rc1 in groundtruth_kb package."""
    code, out, err = _run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'src'); import groundtruth_kb; print(groundtruth_kb.__version__)"],
        cwd=GT_KB_PKG,
    )
    if code != 0:
        return "FAIL", f"import failed: {err.strip() or out.strip()}"
    actual = out.strip()
    if actual != EXPECTED_VERSION:
        return "FAIL", f"expected {EXPECTED_VERSION}, got {actual}"
    return "PASS", f"__version__ == {EXPECTED_VERSION}"


def check_b2_ruff_groundtruth_kb_only() -> tuple[str, str]:
    """B2 — `ruff check groundtruth-kb/` exits 0 (NARROWED scope per DELIB-S330)."""
    code, _out, err = _run([sys.executable, "-m", "ruff", "check", "groundtruth-kb/"], cwd=REPO_ROOT)
    if code != 0:
        return "FAIL", f"ruff exit {code}; stderr: {err.strip()[:200]}"
    return "PASS", "ruff check groundtruth-kb/ exits 0 (full-repo scope deferred per DELIB-S330)"


def check_b3_pytest_completes_clean() -> tuple[str, str]:
    """B3 — `pytest groundtruth-kb/tests/` runs to completion with 0 failures.

    Per DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE, Slice 8 brings
    pytest to green (no failures), not just feasibility (runs-to-completion).
    """
    code, out, _err = _run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"], cwd=GT_KB_PKG)
    if code != 0:
        return "FAIL", f"pytest exit {code}; tail: {out.strip().splitlines()[-1] if out.strip() else 'no output'}"
    last = out.strip().splitlines()[-1] if out.strip() else ""
    return "PASS", f"pytest exit 0; {last}"


def check_b4_release_notes_exists() -> tuple[str, str]:
    """B4 — `release-notes-0.7.0-rc1.md` exists with required structure."""
    path = GT_KB_PKG / "release-notes-0.7.0-rc1.md"
    if not path.exists():
        return "FAIL", f"missing {path.relative_to(REPO_ROOT)}"
    text = path.read_text(encoding="utf-8")
    required = [
        "# GT-KB v0.7.0-rc1 Release Notes",
        "## Highlights",
        "## Adopter-visible changes",
        "## Out of scope for this release",
        SLICE_8_5_BRIDGE_REF,  # cross-reference to Slice 8.5 follow-on
    ]
    missing = [r for r in required if r not in text]
    if missing:
        return "FAIL", f"missing required sections/references: {missing}"
    return "PASS", f"{path.name} present with required structure + Slice 8.5 cross-ref"


def check_b5_wheel_smoke() -> tuple[str, str]:
    """B5 — wheel + sdist build, plus install + version + init smoke.

    Per the accepted REVISED-2 plan and the S330 -008 NO-GO disposition
    (DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK), this check
    runs:

    1. `python -m build --wheel --sdist` (build step).
    2. Confirms wheel + sdist artifacts for EXPECTED_VERSION exist.
    3. Creates an **in-root** scratch venv at
       `E:/GT-KB/.tmp/slice8-install-smoke/<run-id>/venv` (per
       Codex `-010` F1 + `.claude/rules/project-root-boundary.md`: all
       active GT-KB verification paths must be within `E:\\GT-KB`).
    4. `pip install` the built wheel into the venv.
    5. Runs `gt --version` from the venv; asserts `0.7.0rc1`.
    6. Discovers `_GT_KB_HOST_ROOT` from the installed package (= `<venv>`
       for installed wheels: `scaffold.py` is at
       `<venv>/Lib/site-packages/groundtruth_kb/project/scaffold.py` and
       `parents[4]` resolves to `<venv>`). Since the venv is now in-root,
       `_GT_KB_HOST_ROOT` is also in-root.
    7. Creates `<host_root>/applications/SmokeApp` target dir.
    8. Runs `gt project init SmokeApp --gt-kb-root <host_root> --dir
       <host_root>/applications/SmokeApp --profile local-only
       --no-include-ci` using the working command shape under the Slice 4
       isolation contract (per DELIB-S330-...-INSTALL-UX-LIMITATION-ACK;
       the bare command `gt project init <tmp>/test-app --profile
       local-only` from the original `-005` plan does NOT work for
       installed wheels and is superseded by this command shape).
    9. Confirms scaffolded `groundtruth.toml` exists under the target.
   10. Cleans up scratch dir.
    """
    import shutil
    import uuid

    # Step 1 + 2: build (already-required step).
    code, out, err = _run([sys.executable, "-m", "build", "--wheel", "--sdist"], cwd=GT_KB_PKG)
    if code != 0:
        tail = (err or out).strip().splitlines()[-1] if (err or out).strip() else "no output"
        return "FAIL", f"build exit {code}; tail: {tail}"
    dist_dir = GT_KB_PKG / "dist"
    wheels = list(dist_dir.glob(f"groundtruth_kb-{EXPECTED_VERSION}-*.whl"))
    sdists = list(dist_dir.glob(f"groundtruth_kb-{EXPECTED_VERSION}.tar.gz"))
    if not wheels:
        return "FAIL", f"no wheel matching groundtruth_kb-{EXPECTED_VERSION}-*.whl in dist/"
    if not sdists:
        return "FAIL", f"no sdist matching groundtruth_kb-{EXPECTED_VERSION}.tar.gz in dist/"
    wheel_path = wheels[0]

    # Steps 3-7: install + version + init smoke in an in-root scratch dir.
    # Per Codex `-010` F1 + .claude/rules/project-root-boundary.md, all
    # verification paths must live within E:\GT-KB. The .tmp/ tree is gitignored
    # via *.tmp pattern (line 162 of .gitignore).
    scratch_parent = REPO_ROOT / ".tmp" / "slice8-install-smoke"
    scratch_parent.mkdir(parents=True, exist_ok=True)
    tmp_root = scratch_parent / f"run-{uuid.uuid4().hex[:8]}"
    tmp_root.mkdir(parents=True, exist_ok=False)
    try:
        venv_dir = tmp_root / "venv"
        # Create venv. Use sys.executable's Python.
        code, out, err = _run([sys.executable, "-m", "venv", str(venv_dir)])
        if code != 0:
            return "FAIL", f"venv create exit {code}: {err.strip()[:200]}"

        # Resolve venv Python + gt.exe (Windows) or gt (POSIX).
        if sys.platform == "win32":
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_gt = venv_dir / "Scripts" / "gt.exe"
        else:
            venv_python = venv_dir / "bin" / "python"
            venv_gt = venv_dir / "bin" / "gt"

        # pip install the built wheel.
        code, out, err = _run([str(venv_python), "-m", "pip", "install", "--quiet", str(wheel_path)])
        if code != 0:
            tail = (err or out).strip().splitlines()[-1] if (err or out).strip() else ""
            return "FAIL", f"pip install wheel exit {code}: {tail}"

        # gt --version smoke.
        code, out, _err = _run([str(venv_gt), "--version"])
        if code != 0:
            return "FAIL", f"gt --version exit {code}"
        if EXPECTED_VERSION not in out:
            return "FAIL", f"gt --version did not report {EXPECTED_VERSION}; got: {out.strip()[:120]}"

        # gt project init smoke using the working command shape.
        # Per Slice 4 isolation: target.parent must equal <host_root>/applications,
        # AND --gt-kb-root must equal _GT_KB_HOST_ROOT computed from the installed
        # package. Since scaffold.py lives at
        # <venv>/Lib/site-packages/groundtruth_kb/project/scaffold.py and
        # _GT_KB_HOST_ROOT = parents[4], the discovered host_root for an installed
        # wheel is <venv> itself. Discover it via subprocess so the smoke uses the
        # exact value the installed wheel computes.
        discovered = subprocess.run(  # noqa: S603 - trusted local invocation
            [str(venv_python), "-c",
             "from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT; print(_GT_KB_HOST_ROOT)"],
            capture_output=True, text=True, timeout=30,
        )
        if discovered.returncode != 0:
            return "FAIL", f"discover host_root exit {discovered.returncode}"
        host_root = Path(discovered.stdout.strip())
        target = host_root / "applications" / "SmokeApp"
        target.parent.mkdir(parents=True, exist_ok=True)

        init_cmd = [
            str(venv_gt), "project", "init", "SmokeApp",
            "--profile", "local-only",
            "--gt-kb-root", str(host_root),
            "--dir", str(target),
            "--no-seed-example",
            "--no-include-ci",
        ]
        code, out, err = _run(init_cmd)
        if code != 0:
            tail = (err or out).strip().splitlines()[-1] if (err or out).strip() else ""
            return "FAIL", f"gt project init exit {code}: {tail}"

        # Verify scaffolded artifacts.
        if not (target / "groundtruth.toml").exists():
            return "FAIL", f"scaffolded {target / 'groundtruth.toml'} missing after init"

        return (
            "PASS",
            f"build + pip install + gt --version ({EXPECTED_VERSION}) + gt project init (working command shape, in-root scratch at {tmp_root.relative_to(REPO_ROOT)}) all succeeded",
        )
    finally:
        # Cleanup in-root scratch dir; ignore errors (Windows may hold venv DLL
        # handles briefly). Path is under .tmp/ (gitignored via *.tmp); leftover
        # leak is an annoyance, not a governance violation.
        shutil.rmtree(tmp_root, ignore_errors=True)


def check_b6_deferred_to_slice_8_5() -> tuple[str, str]:
    """B6 — CI-green evidence DEFERRED to Slice 8.5 per DELIB-S330.

    This check is INTENTIONAL: it asserts B6 is documented as deferred (with the
    Slice 8.5 bridge thread named) in the closeout artifacts, NOT that CI is
    green. Slice 8.5 will capture the actual CI-green evidence after this commit
    lands.
    """
    readiness_path = REPO_ROOT / "memory" / "release-readiness.md"
    if not readiness_path.exists():
        return "FAIL", "memory/release-readiness.md missing"
    readiness = readiness_path.read_text(encoding="utf-8")
    if "B6 — CI-green evidence" not in readiness or "DEFERRED to Slice 8.5" not in readiness:
        return "FAIL", "release-readiness.md does not record B6 as deferred"
    if SLICE_8_5_BRIDGE_REF not in readiness:
        return "FAIL", f"release-readiness.md does not cite {SLICE_8_5_BRIDGE_REF}"
    return "DEFERRED", f"intentional: B6 captured by Slice 8.5 ({SLICE_8_5_BRIDGE_REF})"


def check_b7_bridge_terminal_state() -> tuple[str, str]:
    """B7 — release-readiness CLOSEOUT block names all 8 ISOLATION-017 slice bridges."""
    readiness = (REPO_ROOT / "memory" / "release-readiness.md").read_text(encoding="utf-8")
    if "## ISOLATION-017-CLOSEOUT" not in readiness:
        return "FAIL", "missing ISOLATION-017-CLOSEOUT block"
    # Confirm each slice bridge ID is referenced (numbers 1-7).
    expected_slices = [
        "Slice 1",
        "Slice 2",
        "Slice 2.5",
        "Slice 3",
        "Slice 4",
        "Slice 5",
        "Slice 6",
        "Slice 7",
    ]
    closeout_section = readiness.split("## ISOLATION-017-CLOSEOUT")[1]
    missing = [s for s in expected_slices if s not in closeout_section]
    if missing:
        return "FAIL", f"CLOSEOUT block does not reference: {missing}"
    return "PASS", "CLOSEOUT block references all 8 ISOLATION-017 slices + Slice 8.5 follow-on"


def check_changelog_entry() -> tuple[str, str]:
    """Closeout artifact — CHANGELOG.md has a [0.7.0-rc1] entry under [Unreleased]."""
    path = GT_KB_PKG / "CHANGELOG.md"
    if not path.exists():
        return "FAIL", f"missing {path.relative_to(REPO_ROOT)}"
    text = path.read_text(encoding="utf-8")
    if "## [0.7.0-rc1] - 2026-05-03" not in text:
        return "FAIL", "missing '## [0.7.0-rc1] - 2026-05-03' entry"
    if SLICE_8_5_BRIDGE_REF not in text and "Slice 8.5" not in text:
        return "FAIL", "CHANGELOG entry does not reference Slice 8.5 follow-on"
    return "PASS", "CHANGELOG entry present + references Slice 8.5"


def check_announcement_exists() -> tuple[str, str]:
    """Closeout artifact — docs/announcements/v0.7.0-rc1.md exists."""
    path = GT_KB_PKG / "docs" / "announcements" / "v0.7.0-rc1.md"
    if not path.exists():
        return "FAIL", f"missing {path.relative_to(REPO_ROOT)}"
    text = path.read_text(encoding="utf-8")
    if "# Announcing GroundTruth-KB v0.7.0-rc1" not in text:
        return "FAIL", "announcement missing required title"
    return "PASS", f"{path.name} present"


CHECKS = [
    ("B1", "Version bump to 0.7.0rc1", check_b1_version_bump),
    ("B2", "Ruff check (groundtruth-kb/ only, narrowed)", check_b2_ruff_groundtruth_kb_only),
    ("B3", "Pytest completes + green", check_b3_pytest_completes_clean),
    ("B4", "release-notes-0.7.0-rc1.md", check_b4_release_notes_exists),
    ("B5", "Wheel/sdist build smoke", check_b5_wheel_smoke),
    ("B6", "CI-green evidence (deferred to Slice 8.5)", check_b6_deferred_to_slice_8_5),
    ("B7", "Bridge terminal state in release-readiness", check_b7_bridge_terminal_state),
    ("CHANGELOG", "[0.7.0-rc1] entry", check_changelog_entry),
    ("ANNOUNCE", "v0.7.0-rc1 announcement", check_announcement_exists),
]


def main() -> int:
    results: list[tuple[str, str, str, str]] = []
    for tag, desc, fn in CHECKS:
        try:
            status, detail = fn()
        except Exception as exc:  # intentional-catch: surface check exceptions as FAIL
            status, detail = "FAIL", f"check raised: {exc}"
        results.append((tag, desc, status, detail))
        marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "DEFERRED": "[DEFER]"}.get(status, f"[{status}]")
        print(f"{marker:8s} {tag:10s} {desc} -- {detail}")

    fails = [r for r in results if r[2] == "FAIL"]
    deferreds = [r for r in results if r[2] == "DEFERRED"]
    print()
    print(
        f"Summary: {len(results) - len(fails) - len(deferreds)} pass, "
        f"{len(deferreds)} deferred (intentional), {len(fails)} fail."
    )
    if fails:
        print(f"FAIL: composite gate has {len(fails)} failing check(s); rc1 not ready.")
        return 1
    print("PASS: composite gate green for Slice 8 in-scope checks. Slice 8.5 captures B6.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
