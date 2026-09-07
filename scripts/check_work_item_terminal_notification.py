#!/usr/bin/env python3
"""Execute claim-release and terminal-notification coordination checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
for candidate in (PROJECT_ROOT, PACKAGE_SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from groundtruth_kb.git_lifecycle.commands import CommandResult  # noqa: E402
from groundtruth_kb.git_lifecycle.models import OperationDenied  # noqa: E402
from groundtruth_kb.git_lifecycle.service import GitLifecycleService  # noqa: E402

from scripts.bridge_work_intent_registry import acquire, claim_status, release  # noqa: E402

EVALUATOR_ID = "post-commit-notification-coordination-release"
EVALUATOR_VERSION = 2
SPEC_ID = "DCL-BRIDGE-CLAIM-LIFECYCLE-001"
PASS, FAIL, PARTIAL, UNASSESSED = "PASS", "FAIL", "PARTIAL", "UNASSESSED"
CRITERIA = {
    "CLAIM-LC-1": "Only the exact reviewed snapshot may proceed to publication.",
    "CLAIM-LC-2": "The work-product commit precedes and excludes notification.",
    "CLAIM-LC-3": "Activation and every control release precede final-visible notification.",
    "CLAIM-LC-4": "Success and duplicate delivery leave zero controls and no duplicate activation.",
    "CLAIM-LC-5": "Terminality is independent of notification retention.",
    "CLAIM-LC-6": "A notification alone cannot synthesize state or cleanup.",
    "CLAIM-LC-7": "Early release and in-flight ambiguity fail closed.",
    "CLAIM-LC-8": "Timing follows registered policy and has no private fallback.",
    "CLAIM-LC-9": "Grandfathering is exact and all later items use the current contract.",
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


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, shell=False)
    return result.stdout.strip()


def _repo(parent: Path) -> Path:
    repo = parent / "publication"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.email", "claim-evaluator@example.invalid")
    _git(repo, "config", "user.name", "Claim Evaluator")
    (repo / "scope.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "fixture base")
    return repo


def _service(repo: Path, boundary: Boundary) -> GitLifecycleService:
    return GitLifecycleService.for_testing(
        repo,
        state_dir=repo / ".state",
        dispatcher_state_dir=repo / ".dispatcher",
        clock=lambda: 1_800_000_000.0,
        sleep=lambda _seconds: None,
        command_boundary=boundary,
    )


def _publication_matrix(parent: Path, criteria: dict[str, Criterion]) -> GitLifecycleService:
    repo = _repo(parent)
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "scope.txt").write_text("reviewed\n", encoding="utf-8")
    _git(repo, "add", "scope.txt")
    _git(repo, "commit", "-m", "reviewed snapshot")
    head, tree = _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")
    (repo / ".git" / "FETCH_HEAD").write_text(f"{base}\t\tbranch 'main' of origin\n", encoding="utf-8")
    boundary = Boundary()
    service = _service(repo, boundary)
    result = service.publish_candidate_branch(
        source_commit=head,
        source_tree=tree,
        base_ref="main",
        target_ref="work-item/wi-claim-fixture",
        message="reviewed fixture",
        max_blob_bytes=1_000_000,
        push=False,
    )
    c1 = criteria["CLAIM-LC-1"]
    _add(
        c1,
        "GitLifecycleService.publish_candidate_branch",
        "exact reviewed snapshot",
        "positive",
        [result.code, "live_push=false"],
        PASS,
        "exact snapshot proceeded",
    )
    try:
        service.publish_candidate_branch(
            source_commit=head,
            source_tree="0" * 40,
            base_ref="main",
            target_ref="work-item/wi-claim-mismatch",
            message="changed fixture",
            max_blob_bytes=1_000_000,
            push=False,
        )
    except OperationDenied as exc:
        ok = exc.code == "source_tree_mismatch"
        _add(
            c1,
            "GitLifecycleService.publish_candidate_branch",
            "modified reviewed snapshot",
            "negative",
            [f"denial={exc.code}"],
            PASS if ok else FAIL,
            "modified snapshot rejected",
        )
    else:
        _add(
            c1,
            "GitLifecycleService.publish_candidate_branch",
            "modified reviewed snapshot",
            "negative",
            ["modified tree accepted"],
            FAIL,
            "modified snapshot proceeded",
        )
    c1.outcome = PASS if all(row.outcome == PASS for row in c1.attempts) else FAIL
    c1.reason = "exact and modified snapshots executed through canonical publication"

    c2 = criteria["CLAIM-LC-2"]
    c2.attempts.extend(c1.attempts)
    _missing(c2, service, "emit_verified_notification", "inspect candidate then emit notification after commit")
    c2.outcome, c2.reason = PARTIAL, "candidate publication executes; final notification boundary is unavailable"
    return service


def _bridge_fixture(root: Path, slug: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True)
    (bridge / f"{slug}-001.md").write_text(
        "NEW\n::init gtkb lo\n::open build\n\n"
        "# Claim evaluator fixture\n\n"
        "Project: PROJECT-EVALUATOR\nWork Item: WI-EVALUATOR-1\n",
        encoding="utf-8",
    )


def _claim_matrix(root: Path, criteria: dict[str, Criterion]) -> None:
    slug, session = "gtkb-semantic-claim-fixture", "semantic-session"
    _bridge_fixture(root, slug)
    acquired = acquire(slug, session, ttl_seconds=37, project_root=root)
    status = claim_status(slug, project_root=root)
    c4 = criteria["CLAIM-LC-4"]
    identity = bool(
        acquired and status and status.get("session_id") == session and status.get("work_item_id") == "WI-EVALUATOR-1"
    )
    _add(
        c4,
        "bridge_work_intent_registry.acquire/claim_status",
        "acquire isolated claim and read exact holder identity",
        "positive",
        [
            f"acquired={acquired}",
            f"holder={status and status.get('session_id')}",
            f"work_item={status and status.get('work_item_id')}",
        ],
        PASS if identity else FAIL,
        "claim identity read back",
    )
    reacquired = acquire(slug, session, ttl_seconds=37, project_root=root)
    _add(
        c4,
        "bridge_work_intent_registry.acquire",
        "same-session duplicate acquisition",
        "positive",
        [f"reacquired={reacquired}"],
        PASS if reacquired else FAIL,
        "same-session delivery is idempotent",
    )
    release(slug, "foreign-session", project_root=root)
    preserved = claim_status(slug, project_root=root)
    _add(
        c4,
        "bridge_work_intent_registry.release",
        "foreign release attempt",
        "negative",
        [f"holder={preserved and preserved.get('session_id')}"],
        PASS if preserved and preserved.get("session_id") == session else FAIL,
        "foreign caller could not release the claim",
    )
    release(slug, session, project_root=root)
    release(slug, session, project_root=root)
    empty = claim_status(slug, project_root=root)
    _add(
        c4,
        "bridge_work_intent_registry.release/claim_status",
        "holder release plus duplicate delivery",
        "negative",
        [f"remaining={empty}"],
        PASS if empty is None else FAIL,
        "release is idempotent and leaves the claim store empty",
    )
    c4.outcome, c4.reason = (
        PARTIAL,
        "claim-store idempotency executes; other locks, leases, holds, and activation stores have no unified readback",
    )

    c7 = criteria["CLAIM-LC-7"]
    c7.attempts.extend(c4.attempts[-2:])
    _missing(c7, None, "terminal_inflight_fence", "release during prepared, in-flight, and ambiguous terminal states")
    c7.outcome, c7.reason = UNASSESSED, "draft release executes, but the terminal in-flight fence is unavailable"

    c8 = criteria["CLAIM-LC-8"]
    acquire(slug, session, ttl_seconds=73, project_root=root)
    timed = claim_status(slug, project_root=root)
    duration = None
    if timed:
        start = datetime.fromisoformat(str(timed["acquired_at"]).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(timed["ttl_expires_at"]).replace("Z", "+00:00"))
        duration = round((end - start).total_seconds())
    _add(
        c8,
        "bridge_work_intent_registry.acquire/claim_status",
        "change supplied draft TTL from 37 to 73 seconds",
        "positive",
        [f"observed_ttl_seconds={duration}"],
        PASS if duration == 73 else FAIL,
        "runtime followed the supplied timing value",
    )
    release(slug, session, project_root=root)
    _missing(
        c8, None, "registered_claim_timing_policy", "remove registered timing authority and reject private fallback"
    )
    c8.outcome, c8.reason = (
        PARTIAL,
        "runtime timing input executes, but its registered policy authority is not exposed by this boundary",
    )


def _missing(
    criterion: Criterion,
    service: GitLifecycleService | None,
    name: str,
    scenario: str,
) -> None:
    target = getattr(service, name, None) if service is not None else None
    if target is None:
        effect = "getattr returned no callable production boundary"
    else:
        try:
            target()
        except Exception as exc:  # noqa: BLE001
            effect = f"call raised {type(exc).__name__}: {exc}"
        else:
            effect = "call returned without a criterion-specific effect contract"
    _add(
        criterion,
        f"production.{name}",
        scenario,
        "failure",
        [effect],
        UNASSESSED,
        f"required production boundary {name} is unavailable or incomplete",
    )


def _notification_matrix(service: GitLifecycleService, criteria: dict[str, Criterion]) -> None:
    scenarios = {
        "CLAIM-LC-3": ("complete_terminal_emission", "activate, release claim/lock/lease/hold, notify last"),
        "CLAIM-LC-5": ("resolve_terminal_work_item", "delete or omit retained notification after accepted commit"),
        "CLAIM-LC-6": ("consume_verified_notification", "notification without attributable terminal commit"),
        "CLAIM-LC-9": ("resolve_grandfathered_terminal_cohort", "cohort member, old nonmember, and later item"),
    }
    for criterion_id, (name, scenario) in scenarios.items():
        criterion = criteria[criterion_id]
        _missing(criterion, service, name, scenario)
        criterion.outcome = UNASSESSED
        criterion.reason = f"canonical {name} boundary is unavailable"


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
    with tempfile.TemporaryDirectory(prefix="wi6898-claim-", dir=scratch) as directory:
        isolated = Path(directory)
        service = _publication_matrix(isolated, criteria)
        _claim_matrix(isolated, criteria)
        _notification_matrix(service, criteria)
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
