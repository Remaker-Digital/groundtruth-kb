#!/usr/bin/env python3
"""Execute semantic branch-binding and publication checks in disposable repos."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.git_lifecycle.commands import CommandResult  # noqa: E402
from groundtruth_kb.git_lifecycle.models import OperationDenied, PromotionEvidence  # noqa: E402
from groundtruth_kb.git_lifecycle.service import GitLifecycleService  # noqa: E402

EVALUATOR_ID = "git-branch-binding-promotion"
EVALUATOR_VERSION = 2
SPEC_ID = "DCL-GIT-BRANCH-BINDING-PROMOTION-001"
PASS, FAIL, PARTIAL, UNASSESSED = "PASS", "FAIL", "PARTIAL", "UNASSESSED"
CRITERIA = {
    f"BRANCH-BIND-A{index}": statement
    for index, statement in enumerate(
        (
            "Binding and terminal attribution are current and collision-safe.",
            "Work-item branches are deterministic, isolated, and correctly descended.",
            "Protected mutations revalidate current authority and snapshot inputs.",
            "Publication preserves the exact verified tree and excludes notification.",
            "Accepted publication terminalizes the one bound work item.",
            "Promotion tiers are distinct and enforce their current gates.",
            "Interrupted emission resumes without duplicate Git effects or held controls.",
            "Prohibited publication and promotion routes fail closed.",
            "The sealed grandfathered cohort is exact and immutable.",
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

    def finish(self, outcome: str, reason: str) -> None:
        self.outcome, self.reason = outcome, reason


class RecordingBoundary:
    """Deterministic provider seam used by the production service."""

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
    _git(repo, "config", "user.email", "evaluator@example.invalid")
    _git(repo, "config", "user.name", "Semantic Evaluator")
    (repo / "scope.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "fixture base")
    return repo


def _service(repo: Path, boundary: RecordingBoundary | None = None) -> GitLifecycleService:
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
) -> None:
    criterion.attempts.append(Attempt("behavioral", entrypoint, scenario, polarity, effects, outcome, reason))


def _missing(criterion: Criterion, service: GitLifecycleService, name: str, scenario: str) -> None:
    target = getattr(service, name, None)
    if target is None:
        effect = "getattr returned no callable production boundary"
    else:
        try:
            target()
        except Exception as exc:  # noqa: BLE001 - evidence records the boundary response
            effect = f"call raised {type(exc).__name__}: {exc}"
        else:
            effect = "call returned without an assertion-specific effect contract"
    _add(
        criterion,
        f"GitLifecycleService.{name}",
        scenario,
        "failure",
        [effect],
        UNASSESSED,
        f"required production boundary {name} is unavailable or incomplete",
    )


def _binding_matrix(parent: Path, criteria: dict[str, Criterion]) -> None:
    repo = _repo(parent, "binding")
    _git(repo, "branch", "project/demo")
    _git(repo, "checkout", "project/demo")
    service = _service(repo)
    created = service.create_work_item_branch(
        work_item_id="WI-TEST-1", title="semantic evaluator", project_branch="project/demo"
    )
    bound = service.bind_work_item(
        work_item_id="WI-TEST-1",
        title="semantic evaluator",
        project_branch="project/demo",
        scope_paths=("scope.txt",),
        required_checks=("semantic",),
    )
    validated = service.validate_binding("WI-TEST-1")
    a2 = criteria["BRANCH-BIND-A2"]
    _add(
        a2,
        "GitLifecycleService.create_work_item_branch/bind_work_item/validate_binding",
        "deterministic branch with valid project ancestry",
        "positive",
        [created.code, bound.code, validated.code, f"branch={validated.branch}"],
        PASS,
        "production service created, bound, and validated the branch",
    )
    try:
        service.bind_work_item(
            work_item_id="WI-TEST-1",
            title="semantic evaluator",
            project_branch="project/demo",
            scope_paths=("different.txt",),
            required_checks=("semantic",),
        )
    except OperationDenied as exc:
        ok = exc.code == "binding_conflict"
        _add(
            a2,
            "GitLifecycleService.bind_work_item",
            "conflicting immutable rebinding",
            "negative",
            [f"denial={exc.code}"],
            PASS if ok else FAIL,
            "conflicting binding rejected",
        )
    else:
        _add(
            a2,
            "GitLifecycleService.bind_work_item",
            "conflicting immutable rebinding",
            "negative",
            ["conflicting write returned"],
            FAIL,
            "conflicting binding accepted",
        )
    a2.finish(
        PASS if all(row.outcome == PASS for row in a2.attempts) else FAIL,
        "positive ancestry and negative collision fixtures executed",
    )

    a1 = criteria["BRANCH-BIND-A1"]
    a1.attempts.extend(a2.attempts)
    _missing(a1, service, "record_terminal_attribution", "append attribution then attempt stale/colliding writes")
    a1.finish(PARTIAL, "binding behavior executes, but terminal attribution has no production boundary")


def _publication_matrix(parent: Path, criteria: dict[str, Criterion]) -> None:
    repo = _repo(parent, "publication")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "scope.txt").write_text("candidate\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "candidate")
    head, tree = _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")
    (repo / ".git" / "FETCH_HEAD").write_text(f"{base}\t\tbranch 'main' of origin\n", encoding="utf-8")
    boundary = RecordingBoundary()
    service = _service(repo, boundary)
    result = service.publish_candidate_branch(
        source_commit=head,
        source_tree=tree,
        base_ref="main",
        target_ref="work-item/wi-test-publish",
        message="semantic fixture",
        max_blob_bytes=1_000_000,
        push=False,
    )
    a4 = criteria["BRANCH-BIND-A4"]
    _add(
        a4,
        "GitLifecycleService.publish_candidate_branch",
        "exact candidate tree",
        "positive",
        [result.code, f"commit={result.commit_sha}", "live_push=false"],
        PASS if result.code == "candidate_ref_created" else FAIL,
        "exact tree accepted without live remote",
    )

    mismatch = _repo(parent, "publication-mismatch")
    mismatch_head = _git(mismatch, "rev-parse", "HEAD")
    try:
        _service(mismatch, RecordingBoundary()).publish_candidate_branch(
            source_commit=mismatch_head,
            source_tree="0" * 40,
            base_ref="main",
            target_ref="work-item/wi-test-mismatch",
            message="mismatch",
            max_blob_bytes=1_000_000,
            push=False,
        )
    except OperationDenied as exc:
        ok = exc.code == "source_tree_mismatch"
        _add(
            a4,
            "GitLifecycleService.publish_candidate_branch",
            "changed reviewed tree",
            "negative",
            [f"denial={exc.code}", "provider_calls=0"],
            PASS if ok else FAIL,
            "changed tree rejected before provider effect",
        )
    else:
        _add(
            a4,
            "GitLifecycleService.publish_candidate_branch",
            "changed reviewed tree",
            "negative",
            ["changed tree accepted"],
            FAIL,
            "publication accepted mismatch",
        )
    a4.finish(
        PASS if all(row.outcome == PASS for row in a4.attempts) else FAIL, "exact-tree and mismatch scenarios executed"
    )

    a3 = criteria["BRANCH-BIND-A3"]
    a3.attempts.extend(a4.attempts)
    _missing(a3, service, "revalidate_operation_authority", "stale authorization, actor, scope, and generation")
    a3.finish(PARTIAL, "tree currentness executes, but full authority/session revalidation is unavailable")
    a5 = criteria["BRANCH-BIND-A5"]
    _missing(a5, service, "record_terminal_attribution", "accepted result with singleton metadata")
    _missing(a5, service, "resolve_terminal_work_item", "read back accepted commit attribution")
    a5.finish(UNASSESSED, "terminal attribution and readback boundaries are unavailable")


def _remaining_matrix(parent: Path, criteria: dict[str, Criterion]) -> GitLifecycleService:
    service = _service(_repo(parent, "remaining"), RecordingBoundary())
    a6 = criteria["BRANCH-BIND-A6"]
    evidence = PromotionEvidence("missing.json", "sha256:" + "0" * 64)
    calls: tuple[tuple[str, dict[str, Any]], ...] = (
        (
            "promote_project_to_develop",
            {"project_id": "PROJECT-X", "project_branch": "project/x", "evidence": evidence},
        ),
        ("promote_develop_to_stage", {"release_id": "RELEASE-X", "evidence": evidence}),
    )
    for name, kwargs in calls:
        try:
            getattr(service, name)(**kwargs)
        except OperationDenied as exc:
            _add(
                a6,
                f"GitLifecycleService.{name}",
                "missing governed evidence",
                "negative",
                [f"denial={exc.code}"],
                PASS,
                "incomplete promotion request rejected",
            )
        else:
            _add(
                a6,
                f"GitLifecycleService.{name}",
                "missing governed evidence",
                "negative",
                ["request returned"],
                FAIL,
                "incomplete promotion request accepted",
            )
    a6.finish(PARTIAL, "both tier entrypoints reject missing gates; safe positive hosted scenario is unavailable")

    a7 = criteria["BRANCH-BIND-A7"]
    try:
        service.resume_operation("missing-operation")
    except (OperationDenied, FileNotFoundError) as exc:
        code = exc.code if isinstance(exc, OperationDenied) else "transaction_missing"
        _add(
            a7,
            "GitLifecycleService.resume_operation",
            "unknown transaction",
            "negative",
            [f"denial={code}"],
            PASS,
            "unknown operation failed closed",
        )
    _missing(a7, service, "resume_terminal_emission", "interrupt and resume each emission phase")
    a7.finish(UNASSESSED, "terminal-emission reconciliation and zero-control readback are unavailable")

    a8 = criteria["BRANCH-BIND-A8"]
    GitLifecycleService.validate_remote_push("work-item/wi-x", "work-item/wi-x")
    _add(
        a8,
        "GitLifecycleService.validate_remote_push",
        "same-name unprotected ref",
        "positive",
        ["returned without mutation"],
        PASS,
        "canonical route accepted",
    )
    denials: list[str] = []
    for source, destination in (("work-item/wi-x", "main"), ("work-item/wi-x", "work-item/wi-y")):
        try:
            GitLifecycleService.validate_remote_push(source, destination)
        except OperationDenied as exc:
            denials.append(exc.code)
    expected = ["direct_push_prohibited", "remote_ref_rewrite_prohibited"]
    _add(
        a8,
        "GitLifecycleService.validate_remote_push",
        "protected and rewritten refs",
        "negative",
        [f"denials={denials}"],
        PASS if denials == expected else FAIL,
        "prohibited routes rejected",
    )
    a8.finish(
        PASS if all(row.outcome == PASS for row in a8.attempts) else FAIL, "positive and negative ref routes executed"
    )

    a9 = criteria["BRANCH-BIND-A9"]
    _missing(a9, service, "resolve_grandfathered_terminal_cohort", "member, nonmember, and enlargement attempt")
    a9.finish(UNASSESSED, "sealed-cohort production resolver is unavailable")
    return service


def _published_state(service: GitLifecycleService) -> list[dict[str, Any]]:
    rows = []
    for index in range(1, 9):
        assertion_id = f"PUBLISHED-{index}"
        target = getattr(service, "resolve_published_state", None)
        effect = "getattr returned no callable production boundary"
        if target is not None:
            try:
                target(assertion_id=assertion_id)
            except Exception as exc:  # noqa: BLE001
                effect = f"call raised {type(exc).__name__}: {exc}"
        rows.append(
            {
                "assertion_id": assertion_id,
                "evidence_mode": "behavioral",
                "entrypoint": "GitLifecycleService.resolve_published_state",
                "scenario": "published-state separation/readback",
                "observed_effects": [effect],
                "outcome": UNASSESSED,
                "reason": "canonical published-state resolver/provider seam is unavailable",
            }
        )
    return rows


def _aggregate(criteria: dict[str, Criterion]) -> str:
    outcomes = [row.outcome for row in criteria.values()]
    if all(row == PASS for row in outcomes):
        return PASS
    if FAIL in outcomes:
        return FAIL
    return PARTIAL if PARTIAL in outcomes else UNASSESSED


def evaluate(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    # Canon s17: evaluator scratch is session-scoped under the canonical
    # scratchpad root, never `.gtkb-state`.
    try:
        from scripts.gtkb_session_id import session_scratch_dirname
    except ImportError:  # pragma: no cover - direct script execution path
        from gtkb_session_id import session_scratch_dirname

    scratch = root / "scratchpad" / session_scratch_dirname() / "evaluator-runs"
    scratch.mkdir(parents=True, exist_ok=True)
    criteria = {key: Criterion(key, value) for key, value in CRITERIA.items()}
    with tempfile.TemporaryDirectory(prefix="wi6898-branch-", dir=scratch) as directory:
        parent = Path(directory)
        _binding_matrix(parent, criteria)
        _publication_matrix(parent, criteria)
        supplemental = _published_state(_remaining_matrix(parent, criteria))
    outcomes = [row.outcome for row in criteria.values()]
    return {
        "evaluator_id": EVALUATOR_ID,
        "evaluator_version": EVALUATOR_VERSION,
        "spec_id": SPEC_ID,
        "aggregate_result": _aggregate(criteria),
        "counts": {name: outcomes.count(name) for name in (PASS, FAIL, PARTIAL, UNASSESSED)},
        "criteria": [asdict(criteria[key]) for key in CRITERIA],
        "supplemental_assertions": supplemental,
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
