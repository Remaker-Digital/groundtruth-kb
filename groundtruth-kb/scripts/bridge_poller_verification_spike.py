#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge poller verification spike runner.

Per ``bridge/gtkb-bridge-poller-p2-5-verification-spike-003.md`` (REVISED-1
GO at -004) and ``bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-004.md``
(REVISED-1 GO), this script seeds a hermetic disposable repo with sentinel
+ minimized governance hooks, exercises Claude Code and Codex headless
modes, and produces a classified spike-report.md mapping each harness ×
mode combination to ``WRITE_CAPABLE`` / ``REVIEW_ONLY`` / ``OUT_OF_SCOPE``.

Default mode: mocked-subprocess. Safe for CI; zero token cost.
Live mode: ``--run-live-harnesses`` + ``--owner-approval-file <path>``,
where the approval file schema is validated BEFORE any real CLI invocation.

Disposable workspace: ``<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/``
resolved via the P1 ``paths.resolve_project_root()`` contract.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge.paths import (
    StateDirOutOfRootError,
    resolve_project_root,
)

SPIKES_SUBDIR = ("spikes",)
TOKEN_COST_FLOOR = 1_500_000  # acknowledged-cost smoke test against stale approvals
APPROVAL_REQUIRED_FIELDS = (
    "approval_text",
    "approval_source_ref",
    "approval_session",
    "approval_recorded_at",
    "estimated_token_cost",
    "estimated_token_cost_acknowledgment",
)
SPIKE_WORKSPACE_ENV_VAR = "GTKB_SPIKE_WORKSPACE"


@dataclass(frozen=True)
class TestResult:
    test_id: str
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    sentinel_hook_fired: bool
    sentinel_gov_hook_fired: bool
    protected_spec_unchanged: bool


@dataclass(frozen=True)
class Classification:
    harness: str
    mode: str
    verdict: str  # "WRITE_CAPABLE" | "REVIEW_ONLY" | "OUT_OF_SCOPE"
    detail: str


@dataclass
class SpikeRunner:
    """Bridge poller verification spike runner.

    All paths resolve in-root via the P1 path contract. Live execution
    requires owner-approval-file validation BEFORE any subprocess invocation.
    """

    run_id: str = field(default="")
    project_root: Path = field(default_factory=resolve_project_root)

    def __post_init__(self) -> None:
        if not self.run_id:
            ts = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
            self.run_id = f"{ts}-{uuid.uuid4().hex[:6]}"

    @property
    def spike_root(self) -> Path:
        override = os.environ.get(SPIKE_WORKSPACE_ENV_VAR)
        if override:
            path = Path(override).resolve()
            if not path.is_relative_to(self.project_root):
                raise StateDirOutOfRootError(
                    f"{SPIKE_WORKSPACE_ENV_VAR}={override} resolves to {path}, "
                    f"which is outside project root {self.project_root}."
                )
            return path
        return self.project_root / ".gtkb-state" / "bridge-poller" / SPIKES_SUBDIR[0] / self.run_id

    @property
    def disposable_repo(self) -> Path:
        return self.spike_root / "disposable-repo"

    @property
    def evidence_dir(self) -> Path:
        return self.spike_root / "evidence"

    @property
    def report_path(self) -> Path:
        return self.spike_root / "spike-report.md"

    def setup_disposable_repo(self) -> Path:
        """Seed the disposable repo with sentinel + minimized governance hooks."""
        repo = self.disposable_repo
        repo.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        (repo / "groundtruth.toml").write_text("# disposable spike repo\n", encoding="utf-8")
        (repo / "CLAUDE.md").write_text("# SPIKE-SENTINEL-CLAUDE-XYZ123\n", encoding="utf-8")
        (repo / "AGENTS.md").write_text("# SPIKE-SENTINEL-AGENTS-XYZ123\n", encoding="utf-8")
        (repo / "protected-spec.json").write_text(
            json.dumps({"sentinel": "do-not-modify", "evil": False}, indent=2),
            encoding="utf-8",
        )

        # Seed hooks under .claude/hooks/ from the fixture directory
        fixture_src = (
            self.project_root / "groundtruth-kb" / "tests" / "fixtures" / "bridge_spike_minimized_governance_hooks"
        )
        if not fixture_src.is_dir():
            # Phase 2 isolation may move tests to root tests/; check that path too
            fallback = self.project_root / "tests" / "fixtures" / "bridge_spike_minimized_governance_hooks"
            if fallback.is_dir():
                fixture_src = fallback

        claude_hooks = repo / ".claude" / "hooks"
        claude_hooks.mkdir(parents=True, exist_ok=True)
        for hook_name in (
            "sentinel_marker.py",
            "formal_artifact_approval_gate.py",
            "credential_scan.py",
        ):
            src = fixture_src / hook_name
            if src.is_file():
                shutil.copy2(src, claude_hooks / hook_name)

        # Minimal Claude Code settings registering the sentinel + governance hooks
        (repo / ".claude" / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "type": "command",
                                "command": f"python {claude_hooks / 'sentinel_marker.py'}",
                            }
                        ],
                        "PreToolUse": [
                            {
                                "type": "command",
                                "command": (f"python {claude_hooks / 'formal_artifact_approval_gate.py'}"),
                            },
                            {
                                "type": "command",
                                "command": (f"python {claude_hooks / 'credential_scan.py'}"),
                            },
                        ],
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        # Codex sample (intent only; per ADR-CODEX-HOOK-PARITY-FALLBACK-001
        # not active on Windows)
        codex_dir = repo / ".codex"
        codex_dir.mkdir(parents=True, exist_ok=True)
        (codex_dir / "config.toml").write_text("# disposable codex config\n", encoding="utf-8")
        (codex_dir / "hooks.json").write_text(
            json.dumps(
                {
                    "_verification_warning": ("ADR-CODEX-HOOK-PARITY-FALLBACK-001: not active on Windows"),
                    "hooks": {
                        "SessionStart": [
                            {
                                "type": "command",
                                "command": f"python {claude_hooks / 'sentinel_marker.py'}",
                            }
                        ]
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return repo


def _validate_approval_file(path: Path, run_id: str) -> dict[str, Any]:
    """Validate the owner-approval JSON file and return its parsed content.

    Raises ValueError on any validation failure. Called BEFORE any live
    subprocess invocation per design -003 §1.2.
    """
    if not path.is_file():
        raise ValueError(f"Approval file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Approval file is not valid JSON: {exc}") from exc

    missing = [f for f in APPROVAL_REQUIRED_FIELDS if f not in payload]
    if missing:
        raise ValueError(
            f"Approval file missing required fields: {missing}. Required: {list(APPROVAL_REQUIRED_FIELDS)}"
        )

    cost = payload.get("estimated_token_cost", 0)
    if not isinstance(cost, int) or cost < TOKEN_COST_FLOOR:
        raise ValueError(
            f"Approval file estimated_token_cost={cost!r} below minimum "
            f"acknowledgment threshold {TOKEN_COST_FLOOR}; owner approval "
            f"likely stale or wrong run."
        )

    constraint = payload.get("run_id_constraint")
    if constraint is not None and constraint != run_id:
        raise ValueError(f"Approval file is bound to run_id={constraint!r}; this run_id={run_id!r}.")

    return payload


def _write_approval_receipt(evidence_dir: Path, approval: dict[str, Any], run_id: str) -> Path:
    """Write a receipt copy of the validated approval into the evidence dir."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    receipt = evidence_dir / "live-run-approval.json"
    receipt.write_text(
        json.dumps(
            {
                "validated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "validated_for_run_id": run_id,
                "approval_payload": approval,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return receipt


def _claude_modes() -> list[tuple[str, list[str]]]:
    return [
        ("default", ["claude", "-p", "spike-prompt"]),
        ("bare", ["claude", "-p", "spike-prompt", "--bare"]),
        ("add-dir", ["claude", "-p", "spike-prompt", "--add-dir", "{repo}"]),
        ("bare+add-dir", ["claude", "-p", "spike-prompt", "--bare", "--add-dir", "{repo}"]),
    ]


def _codex_modes() -> list[tuple[str, list[str]]]:
    return [
        ("default", ["codex", "exec", "spike-prompt"]),
        ("cd", ["codex", "exec", "spike-prompt", "--cd", "{repo}"]),
        (
            "sandbox+approval",
            ["codex", "exec", "spike-prompt", "--sandbox", "workspace-write", "--approval", "never"],
        ),
        ("profile", ["codex", "exec", "spike-prompt", "--profile", "default"]),
    ]


def _run_command_mocked(cmd: list[str], evidence_dir: Path, sentinel_pre: set[Path], gov_pre: set[Path]) -> TestResult:
    """Mocked subprocess: synthesize a plausible response without invoking real CLI."""
    cmd_tuple = tuple(cmd)
    return TestResult(
        test_id="MOCK",
        command=cmd_tuple,
        exit_code=0,
        stdout=f"[mocked subprocess; would invoke: {' '.join(cmd_tuple)}]\n",
        stderr="",
        duration_s=0.0,
        sentinel_hook_fired=False,  # mocked mode never fires real hooks
        sentinel_gov_hook_fired=False,
        protected_spec_unchanged=True,
    )


# Type alias for the subprocess.run-shaped callable that ``_run_command_live``
# uses. Tests inject a substitute via ``run_spike(subprocess_runner=fake)`` so
# the live code path is exercised without invoking real ``claude``/``codex``.
SubprocessRunner = Callable[..., subprocess.CompletedProcess[str]]


def _run_command_live(
    cmd: list[str],
    evidence_dir: Path,
    disposable_repo: Path,
    sentinel_pre: set[Path],
    gov_pre: set[Path],
    *,
    runner: SubprocessRunner = subprocess.run,
    timeout_s: int = 120,
) -> TestResult:
    """Invoke a real subprocess for one test combination and capture full evidence.

    Reads ``protected-spec.json`` content before and after the subprocess, then
    diffs the sentinel-marker globs in ``evidence_dir`` to detect whether the
    generic SessionStart sentinel and the governance marker fired. The
    populated ``TestResult`` feeds ``_classify()`` directly.

    The ``runner`` parameter defaults to ``subprocess.run``. Tests substitute it
    via ``run_spike(subprocess_runner=...)`` to exercise this code path
    without invoking real CLIs (saves the ~2.1M-token live cost in CI).
    """
    cmd_tuple = tuple(cmd)
    protected = disposable_repo / "protected-spec.json"
    pre_content = protected.read_text(encoding="utf-8") if protected.is_file() else ""

    env = {**os.environ, "SPIKE_EVIDENCE_DIR": str(evidence_dir)}
    start = time.monotonic()
    try:
        completed = runner(
            cmd,
            cwd=str(disposable_repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except FileNotFoundError as exc:
        # Real CLI not installed on this host; record as exit 127 + stderr.
        exit_code = 127
        stdout = ""
        stderr = f"FileNotFoundError: {exc}"
    except subprocess.TimeoutExpired as exc:
        exit_code = 124  # GNU timeout convention
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = f"TimeoutExpired after {timeout_s}s: {exc}"
    duration_s = time.monotonic() - start

    sentinel_post = set(evidence_dir.glob("SENTINEL_HOOK_FIRED-*"))
    gov_post = set(evidence_dir.glob("SENTINEL_GOV_HOOK_FIRED-*"))
    sentinel_fired = bool(sentinel_post - sentinel_pre)
    gov_fired = bool(gov_post - gov_pre)

    post_content = protected.read_text(encoding="utf-8") if protected.is_file() else ""
    protected_unchanged = pre_content == post_content

    return TestResult(
        test_id="LIVE",
        command=cmd_tuple,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_s=duration_s,
        sentinel_hook_fired=sentinel_fired,
        sentinel_gov_hook_fired=gov_fired,
        protected_spec_unchanged=protected_unchanged,
    )


def _classify(harness: str, mode: str, results: list[TestResult]) -> Classification:
    """Classify per design -003 §2.8."""
    sentinel_fired = any(r.sentinel_hook_fired for r in results)
    gov_fired = any(r.sentinel_gov_hook_fired for r in results)
    blocked = all(r.protected_spec_unchanged for r in results) and gov_fired

    if sentinel_fired and gov_fired and blocked:
        verdict = "WRITE_CAPABLE"
        detail = "Both generic and governance hooks fired; protected-write blocked."
    elif sentinel_fired and not gov_fired:
        verdict = "REVIEW_ONLY"
        detail = (
            "Generic hook fired but governance hook did not block protected-write. "
            "Mode safe ONLY for read-only/review-only spawns."
        )
    elif sentinel_fired and gov_fired and not blocked:
        verdict = "REVIEW_ONLY"
        detail = (
            "Governance hook fired but did not actually block the protected-write "
            "(sentinel marker present but file content changed). Mode safe ONLY for "
            "read-only spawns until governance enforcement is verified."
        )
    else:
        verdict = "OUT_OF_SCOPE"
        detail = (
            "Neither sentinel nor governance hook fired in this mode. Mode unsafe "
            "for any autonomous spawning until separate design lands."
        )
    return Classification(harness=harness, mode=mode, verdict=verdict, detail=detail)


def _write_spike_report(
    report_path: Path,
    *,
    run_id: str,
    live: bool,
    classifications: list[Classification],
    results_by_pair: dict[tuple[str, str], list[TestResult]],
    approval_receipt: Path | None,
) -> None:
    """Write the human-readable spike-report.md per design -003 §2.4."""
    lines: list[str] = []
    lines.append(f"# Bridge Poller Verification Spike — Report ({run_id})\n")
    if live:
        lines.append(
            "- mode: **LIVE** (--run-live-harnesses) — captured from real subprocess "
            "invocations; per-test evidence below contains real stdout/stderr/exit-code/"
            "duration plus sentinel-marker and protected-spec deltas."
        )
    else:
        lines.append(
            "- mode: **MOCKED** (default; CI-safe) — per-test results are synthesized; "
            "this report MUST NOT be used as P3 invoker classification evidence. "
            "Re-run with --run-live-harnesses + validated --owner-approval-file."
        )
    lines.append(f"- generated_at: {dt.datetime.now(dt.UTC).isoformat(timespec='seconds')}")
    if approval_receipt is not None:
        lines.append(f"- approval_receipt: `{approval_receipt}`")
    lines.append("")
    lines.append("## Classification matrix\n")
    lines.append("| Harness | Mode | Verdict | Detail |")
    lines.append("|---|---|---|---|")
    for c in classifications:
        lines.append(f"| {c.harness} | {c.mode} | **{c.verdict}** | {c.detail} |")
    lines.append("")
    lines.append("## Per-test evidence\n")
    for (harness, mode), results in results_by_pair.items():
        lines.append(f"### {harness} / {mode}\n")
        for r in results:
            lines.append(f"- command: `{' '.join(r.command)}`")
            lines.append(f"  - exit_code: {r.exit_code}")
            lines.append(f"  - duration_s: {r.duration_s:.3f}")
            lines.append(f"  - sentinel_hook_fired: {r.sentinel_hook_fired}")
            lines.append(f"  - sentinel_gov_hook_fired: {r.sentinel_gov_hook_fired}")
            lines.append(f"  - protected_spec_unchanged: {r.protected_spec_unchanged}")
            lines.append(f"  - stdout: ```\n{r.stdout}\n```")
            if r.stderr:
                lines.append(f"  - stderr: ```\n{r.stderr}\n```")
            lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_spike(
    *,
    run_id: str | None = None,
    live: bool = False,
    owner_approval_file: Path | None = None,
    subprocess_runner: SubprocessRunner | None = None,
    timeout_s: int = 120,
) -> Path:
    """Execute the verification spike. Returns the path to spike-report.md.

    Mocked default; live mode requires validated owner-approval-file.

    The ``subprocess_runner`` parameter is the test-injection point for the
    live code path. When set (non-None), live mode calls it instead of
    ``subprocess.run`` so tests can exercise the live adapter without
    invoking real ``claude``/``codex`` binaries. Production live runs leave
    it ``None`` and the live adapter calls ``subprocess.run`` directly.
    """
    runner = SpikeRunner(run_id=run_id or "")
    runner.setup_disposable_repo()

    approval_receipt: Path | None = None
    if live:
        if owner_approval_file is None:
            raise ValueError("--run-live-harnesses requires --owner-approval-file.")
        approval_path = Path(owner_approval_file).resolve()
        if not approval_path.is_relative_to(runner.project_root):
            raise ValueError(
                f"Approval file at {approval_path} is outside project root {runner.project_root}; refusing live run."
            )
        payload = _validate_approval_file(approval_path, runner.run_id)
        approval_receipt = _write_approval_receipt(runner.evidence_dir, payload, runner.run_id)

    results_by_pair: dict[tuple[str, str], list[TestResult]] = {}
    classifications: list[Classification] = []

    for harness, modes in (("claude", _claude_modes()), ("codex", _codex_modes())):
        for mode_name, cmd_template in modes:
            cmd = [c.replace("{repo}", str(runner.disposable_repo)) for c in cmd_template]
            sentinel_pre = set(runner.evidence_dir.glob("SENTINEL_HOOK_FIRED-*"))
            gov_pre = set(runner.evidence_dir.glob("SENTINEL_GOV_HOOK_FIRED-*"))
            if live:
                result = _run_command_live(
                    cmd,
                    runner.evidence_dir,
                    runner.disposable_repo,
                    sentinel_pre,
                    gov_pre,
                    runner=subprocess_runner if subprocess_runner is not None else subprocess.run,
                    timeout_s=timeout_s,
                )
            else:
                result = _run_command_mocked(cmd, runner.evidence_dir, sentinel_pre, gov_pre)
            results_by_pair[(harness, mode_name)] = [result]
            classifications.append(_classify(harness, mode_name, [result]))

    _write_spike_report(
        runner.report_path,
        run_id=runner.run_id,
        live=live,
        classifications=classifications,
        results_by_pair=results_by_pair,
        approval_receipt=approval_receipt,
    )
    return runner.report_path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bridge_poller_verification_spike.py",
        description="Bridge poller verification spike (mocked default; live opt-in).",
    )
    parser.add_argument("--run-id", default=None, help="Override the auto-generated run_id.")
    parser.add_argument(
        "--run-live-harnesses",
        action="store_true",
        help=(
            "Enable real claude/codex subprocess invocation. "
            "Requires --owner-approval-file. Default mode is mocked-subprocess."
        ),
    )
    parser.add_argument(
        "--owner-approval-file",
        type=Path,
        default=None,
        help=(
            "JSON file under <project_root>/.gtkb-state/... containing schema-validated "
            "owner approval. REQUIRED with --run-live-harnesses; validated BEFORE "
            "any live subprocess call."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.run_live_harnesses and args.owner_approval_file is None:
        parser.error("--run-live-harnesses requires --owner-approval-file")

    try:
        report_path = run_spike(
            run_id=args.run_id,
            live=args.run_live_harnesses,
            owner_approval_file=args.owner_approval_file,
        )
    except (ValueError, StateDirOutOfRootError) as exc:
        sys.stderr.write(f"spike runner refused: {exc}\n")
        return 2
    sys.stdout.write(f"spike-report: {report_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
