#!/usr/bin/env python3
"""Execute terminal-state checks without inferring behavior from source text."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.git_lifecycle.commands import CommandResult  # noqa: E402
from groundtruth_kb.git_lifecycle.models import OperationDenied  # noqa: E402
from groundtruth_kb.git_lifecycle.service import GitLifecycleService  # noqa: E402

EVALUATOR_ID = "work-item-terminal-state-and-metadata"
EVALUATOR_VERSION = 2
SPEC_ID = "GOV-WORK-ITEM-TERMINAL-STATE-001"
PASS, FAIL, PARTIAL, UNASSESSED = "PASS", "FAIL", "PARTIAL", "UNASSESSED"
CRITERIA = {
    f"WI-TERM-A{index}": statement
    for index, statement in enumerate(
        (
            "Terminality arises only from accepted registered-provider publication.",
            "The terminal tree and scope exactly match the verified snapshot.",
            "The terminal commit carries one canonical ID and exact rendering.",
            "The ID agrees across binding, snapshot, publication, and attribution.",
            "Every malformed or mismatched metadata carrier fails before publication.",
            "Independent acceptance rejects a nonconforming published commit.",
            "Exact replay is idempotent and conflicting replay fails closed.",
            "The terminal commit precedes and excludes its notification.",
            "Emission activates, releases controls, then publishes notification.",
            "Interrupted emission resumes the same commit and ends with zero controls.",
            "Only sealed-cohort members bypass the current terminal contract.",
            "Terminality is monotonic and one work item is retired per commit.",
        ),
        1,
    )
}


@dataclass
class Attempt:
    evidence_mode: str
    entrypoint: str
    scenario: str
    polarity: str
    observed_effects: list[str]
    outcome: str
    reason: str


@dataclass
class Criterion:
    criterion_id: str
    statement: str
    outcome: str = UNASSESSED
    reason: str = "not evaluated"
    attempts: list[Attempt] = field(default_factory=list)


class Boundary:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv: Sequence[str], *, cwd: Path) -> CommandResult:
        exact = tuple(str(item) for item in argv)
        self.calls.append(exact)
        return CommandResult(argv=exact, returncode=2 if "ls-remote" in exact else 0)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, shell=False)
    return result.stdout.strip()


def _repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.email", "terminal-evaluator@example.invalid")
    _git(repo, "config", "user.name", "Terminal Evaluator")
    (repo / "scope.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "fixture base")
    return repo


def _service(repo: Path, boundary: Boundary | None = None) -> GitLifecycleService:
    return GitLifecycleService.for_testing(
        repo,
        state_dir=repo / ".state",
        dispatcher_state_dir=repo / ".dispatcher",
        clock=lambda: 1_800_000_000.0,
        sleep=lambda _seconds: None,
        command_boundary=boundary,
    )


def _add(
    criterion: Criterion,
    entrypoint: str,
    scenario: str,
    polarity: str,
    effects: list[str],
    outcome: str,
    reason: str,
    mode: str = "behavioral",
) -> None:
    criterion.attempts.append(Attempt(mode, entrypoint, scenario, polarity, effects, outcome, reason))


def _attempt_missing(
    criterion: Criterion,
    service: GitLifecycleService,
    name: str,
    scenario: str,
    *,
    polarity: str = "failure",
) -> None:
    target = getattr(service, name, None)
    if target is None:
        effect = "getattr returned no callable production boundary"
    else:
        try:
            target()
        except Exception as exc:  # noqa: BLE001 - the attempt ledger records the actual response
            effect = f"call raised {type(exc).__name__}: {exc}"
        else:
            effect = "call returned without a criterion-specific effect contract"
    _add(
        criterion,
        f"GitLifecycleService.{name}",
        scenario,
        polarity,
        [effect],
        UNASSESSED,
        f"required terminal boundary {name} is unavailable or incomplete",
    )


def _publication_snapshot(parent: Path, criteria: dict[str, Criterion]) -> GitLifecycleService:
    repo = _repo(parent, "snapshot")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "scope.txt").write_text("verified\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "verified snapshot")
    head, tree = _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")
    (repo / ".git" / "FETCH_HEAD").write_text(f"{base}\t\tbranch 'main' of origin\n", encoding="utf-8")
    boundary = Boundary()
    service = _service(repo, boundary)
    result = service.publish_candidate_branch(
        source_commit=head,
        source_tree=tree,
        base_ref="main",
        target_ref="work-item/wi-terminal-fixture",
        message="verified fixture",
        max_blob_bytes=1_000_000,
        push=False,
    )
    a2 = criteria["WI-TERM-A2"]
    _add(
        a2,
        "GitLifecycleService.publish_candidate_branch",
        "exact verified tree and scope",
        "positive",
        [result.code, f"commit={result.commit_sha}", "live_push=false"],
        PASS,
        "exact snapshot accepted",
    )

    mismatch = _repo(parent, "snapshot-mismatch")
    mismatch_head = _git(mismatch, "rev-parse", "HEAD")
    mismatch_boundary = Boundary()
    try:
        _service(mismatch, mismatch_boundary).publish_candidate_branch(
            source_commit=mismatch_head,
            source_tree="0" * 40,
            base_ref="main",
            target_ref="work-item/wi-terminal-mismatch",
            message="mismatch fixture",
            max_blob_bytes=1_000_000,
            push=False,
        )
    except OperationDenied as exc:
        ok = exc.code == "source_tree_mismatch" and not mismatch_boundary.calls
        _add(
            a2,
            "GitLifecycleService.publish_candidate_branch",
            "reviewer-edited or mismatched tree",
            "negative",
            [f"denial={exc.code}", f"provider_calls={len(mismatch_boundary.calls)}"],
            PASS if ok else FAIL,
            "mismatch rejected before provider effect",
        )
    else:
        _add(
            a2,
            "GitLifecycleService.publish_candidate_branch",
            "reviewer-edited or mismatched tree",
            "negative",
            ["mismatch accepted"],
            FAIL,
            "mismatched snapshot was accepted",
        )
    a2.outcome = PASS if all(row.outcome == PASS for row in a2.attempts) else FAIL
    a2.reason = "positive and negative snapshot scenarios executed through publication"
    return service


def _binding(parent: Path, criteria: dict[str, Criterion]) -> GitLifecycleService:
    repo = _repo(parent, "binding")
    _git(repo, "branch", "project/demo")
    _git(repo, "checkout", "project/demo")
    service = _service(repo)
    service.create_work_item_branch(work_item_id="WI-TEST-2", title="terminal binding", project_branch="project/demo")
    service.bind_work_item(
        work_item_id="WI-TEST-2",
        title="terminal binding",
        project_branch="project/demo",
        scope_paths=("scope.txt",),
        required_checks=("terminal",),
    )
    result = service.validate_binding("WI-TEST-2")
    a4 = criteria["WI-TERM-A4"]
    _add(
        a4,
        "GitLifecycleService.validate_binding",
        "work-item branch identity and scope binding",
        "positive",
        [result.code, f"work_item={result.work_item_id}"],
        PASS,
        "binding equality was observed",
    )
    _attempt_missing(
        a4,
        service,
        "record_terminal_attribution",
        "mismatched binding, snapshot, scope, target, and attribution",
        polarity="negative",
    )
    a4.outcome, a4.reason = PARTIAL, "binding equality executes; cross-boundary terminal attribution does not"
    return service


def _terminal_matrix(service: GitLifecycleService, criteria: dict[str, Criterion]) -> None:
    scenarios: dict[str, tuple[str, str]] = {
        "WI-TERM-A1": (
            "resolve_terminal_work_item",
            "accepted/rejected registered-provider publication then terminal resolution",
        ),
        "WI-TERM-A3": (
            "build_terminal_metadata",
            "singleton carrier plus zero, multiple, duplicate, and rendering mismatch",
        ),
        "WI-TERM-A5": (
            "validate_terminal_metadata",
            "missing, malformed, unknown, unrelated, and cross-boundary mismatches",
        ),
        "WI-TERM-A6": ("record_terminal_attribution", "provider transport accepts a nonconforming commit"),
        "WI-TERM-A7": ("replay_terminal_publication", "exact replay then one changed immutable input"),
        "WI-TERM-A8": ("emit_verified_notification", "commit first, then omit, delete, and replay notification"),
        "WI-TERM-A9": ("complete_terminal_emission", "activate, project, release controls, read back, notify last"),
        "WI-TERM-A10": ("resume_terminal_emission", "interrupt each phase and reconcile to zero controls"),
        "WI-TERM-A11": ("resolve_grandfathered_terminal_cohort", "member, pre-cutover nonmember, post-cutover item"),
        "WI-TERM-A12": ("resolve_terminal_work_item", "replay terminal result then attempt reopen and work-item reuse"),
    }
    for criterion_id, (name, scenario) in scenarios.items():
        criterion = criteria[criterion_id]
        _attempt_missing(criterion, service, name, scenario)
        criterion.outcome = UNASSESSED
        criterion.reason = f"canonical {name} production boundary is unavailable or incomplete"


def _aggregate(criteria: dict[str, Criterion]) -> str:
    outcomes = [row.outcome for row in criteria.values()]
    if all(row == PASS for row in outcomes):
        return PASS
    if FAIL in outcomes:
        return FAIL
    return PARTIAL if PARTIAL in outcomes else UNASSESSED


def evaluate(root: Path = PROJECT_ROOT) -> dict:
    # Canon s17: evaluator scratch is session-scoped under the canonical
    # scratchpad root, never `.gtkb-state`.
    try:
        from scripts.gtkb_session_id import session_scratch_dirname
    except ImportError:  # pragma: no cover - direct script execution path
        from gtkb_session_id import session_scratch_dirname

    scratch = root / "scratchpad" / session_scratch_dirname() / "evaluator-runs"
    scratch.mkdir(parents=True, exist_ok=True)
    criteria = {key: Criterion(key, value) for key, value in CRITERIA.items()}
    with tempfile.TemporaryDirectory(prefix="wi6898-terminal-", dir=scratch) as directory:
        parent = Path(directory)
        publication = _publication_snapshot(parent, criteria)
        _binding(parent, criteria)
        _terminal_matrix(publication, criteria)
    outcomes = [row.outcome for row in criteria.values()]
    return {
        "evaluator_id": EVALUATOR_ID,
        "evaluator_version": EVALUATOR_VERSION,
        "spec_id": SPEC_ID,
        "aggregate_result": _aggregate(criteria),
        "counts": {name: outcomes.count(name) for name in (PASS, FAIL, PARTIAL, UNASSESSED)},
        "criteria": [asdict(criteria[key]) for key in CRITERIA],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = evaluate(args.project_root)
    print(
        json.dumps(report, indent=2, sort_keys=True)
        if args.json
        else f"{EVALUATOR_ID}: {report['aggregate_result']} ({SPEC_ID})"
    )
    return 0 if report["aggregate_result"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
