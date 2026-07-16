#!/usr/bin/env python3
"""Run the frozen modernization Git lifecycle acceptance contract."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier, Event
from typing import Any
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.bridge_dispatch_reset import is_drain_marker_active  # noqa: E402
from groundtruth_kb.git_lifecycle import (  # noqa: E402
    CommandResult,
    GitLifecycleService,
    OperationDenied,
    PromotionEvidence,
)
from groundtruth_kb.git_lifecycle import quiescence as quiescence_module  # noqa: E402
from groundtruth_kb.git_lifecycle.__main__ import main as lifecycle_cli_main  # noqa: E402
from groundtruth_kb.git_lifecycle.quiescence import (  # noqa: E402
    acquire_dispatcher_quiescence,
    active_dispatcher_workers,
    recover_dispatcher_quiescence,
)
from groundtruth_kb.git_lifecycle.state import LifecycleState, canonical_json, sha256_json  # noqa: E402

WORK_ITEM = "WI-1001"
TITLE = "Change Core"
WORK_BRANCH = "work-item/wi-1001-change-core"
PROJECT_BRANCH = "project/modernization"
CHECKS = ("unit", "policy")
PROJECT_ID = "PROJECT-MODERNIZATION"
PAUTH_ID = "PAUTH-PROJECT-MODERNIZATION-WI-1001"
BRIDGE_ID = "gtkb-modernization-wi-1001"
AUTHOR_SESSION = "pb-author-session"
VERIFIER_SESSION = "lo-verifier-session"


class ManualClock:
    def __init__(self, value: float = 1_700_000_000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


class SimulatedProcessExit(BaseException):
    """Represents process loss after Git succeeds but before state finalizes."""


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")
    return result


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class Fixture:
    def __init__(self, root: Path, *, worker_probe: Callable[[], int] | None = None) -> None:
        self.root = root
        self.clock = ManualClock()
        root.mkdir(parents=True)
        _git(root, "init", "-b", "main")
        _git(root, "config", "user.email", "acceptance@example.invalid")
        _git(root, "config", "user.name", "GT-KB Acceptance")
        _write(root, ".gitignore", ".gtkb-state/\nbridge/\nharness-state/\ngroundtruth.db\nevidence/\n*.log\n")
        _write(root, "app.py", "VALUE = 'base'\n")
        _write(root, "unrelated.txt", "unrelated base\n")
        _git(root, "add", ".gitignore", "app.py", "unrelated.txt")
        _git(root, "commit", "-m", "initial")
        _git(root, "branch", PROJECT_BRANCH)
        _git(root, "checkout", "-b", WORK_BRANCH, PROJECT_BRANCH)
        self.worker_probe = worker_probe or (lambda: 0)
        self.evidence_counter = 0
        self.bridge_version = 2
        self._install_authority()
        self.service = self.new_service()

    @property
    def state_dir(self) -> Path:
        return self.root / ".gtkb-state" / "git-lifecycle"

    @property
    def dispatcher_dir(self) -> Path:
        return self.root / ".gtkb-state" / "bridge-poller"

    @staticmethod
    def _packet_hash(packet: dict[str, Any]) -> str:
        material = {key: value for key, value in packet.items() if key != "packet_hash"}
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def _install_authority(self) -> None:
        acquired_at = datetime.fromtimestamp(self.clock(), tz=UTC).isoformat().replace("+00:00", "Z")
        expires_at = "2099-01-01T00:00:00Z"
        claim = {
            "thread_slug": BRIDGE_ID,
            "session_id": AUTHOR_SESSION,
            "acquired_at": acquired_at,
            "ttl_expires_at": expires_at,
            "claim_kind": "go_implementation",
            "implementation_deadline": expires_at,
            "implementation_grace_expires_at": expires_at,
            "extensions_used": 0,
            "extension_cap_seconds": 7200,
            "acting_role": "prime-builder",
            "project_id": PROJECT_ID,
        }
        connection = sqlite3.connect(self.root / "groundtruth.db")
        connection.executescript(
            """
            CREATE TABLE project_authorizations (
                id TEXT NOT NULL, version INTEGER NOT NULL, project_id TEXT NOT NULL,
                status TEXT NOT NULL, expires_at TEXT, included_work_item_ids TEXT,
                excluded_work_item_ids TEXT, forbidden_operations TEXT,
                PRIMARY KEY (id, version)
            );
            CREATE VIEW current_project_authorizations AS
            SELECT a.* FROM project_authorizations a
            INNER JOIN (
                SELECT id, MAX(version) AS max_version FROM project_authorizations GROUP BY id
            ) latest ON a.id = latest.id AND a.version = latest.max_version;
            CREATE TABLE work_intent_claims (
                thread_slug TEXT PRIMARY KEY, session_id TEXT NOT NULL, acquired_at TEXT NOT NULL,
                ttl_expires_at TEXT NOT NULL, claim_kind TEXT, implementation_deadline TEXT,
                implementation_grace_expires_at TEXT, extensions_used INTEGER,
                extension_cap_seconds INTEGER, acting_role TEXT, project_id TEXT
            );
            """
        )
        connection.execute(
            "INSERT INTO project_authorizations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (PAUTH_ID, 1, PROJECT_ID, "active", None, json.dumps([WORK_ITEM]), json.dumps([]), json.dumps([])),
        )
        connection.execute(
            "INSERT INTO work_intent_claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(
                claim[key]
                for key in (
                    "thread_slug",
                    "session_id",
                    "acquired_at",
                    "ttl_expires_at",
                    "claim_kind",
                    "implementation_deadline",
                    "implementation_grace_expires_at",
                    "extensions_used",
                    "extension_cap_seconds",
                    "acting_role",
                    "project_id",
                )
            ),
        )
        connection.commit()
        connection.close()
        _write(self.root, f"bridge/{BRIDGE_ID}-001.md", "NEW\n\nCanonical acceptance proposal.\n")
        _write(self.root, f"bridge/{BRIDGE_ID}-002.md", "GO\n\nIndependent implementation approval.\n")
        worker_provenance = {
            "schema_version": 1,
            "role": "prime-builder",
            "session_id": AUTHOR_SESSION,
            "harness_id": "A",
            "harness_name": "codex",
            "role_resolution_source": "acceptance-fixture",
            "issued_at": acquired_at,
            "dispatch_run_id": AUTHOR_SESSION,
        }
        _write(
            self.root,
            f"harness-state/codex/session-envelopes/{AUTHOR_SESSION}.json",
            json.dumps(
                {
                    "status": "open",
                    "session_id": AUTHOR_SESSION,
                    "harness_id": "A",
                    "harness_name": "codex",
                    "worker_role_provenance": worker_provenance,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
            + "\n",
        )
        verifier_provenance = {
            "schema_version": 1,
            "role": "loyal-opposition",
            "session_id": VERIFIER_SESSION,
            "harness_id": "B",
            "harness_name": "claude",
            "role_resolution_source": "acceptance-fixture",
            "issued_at": acquired_at,
            "dispatch_run_id": VERIFIER_SESSION,
        }
        _write(
            self.root,
            f"harness-state/claude/session-envelopes/{VERIFIER_SESSION}.json",
            json.dumps(
                {
                    "status": "open",
                    "session_id": VERIFIER_SESSION,
                    "harness_id": "B",
                    "harness_name": "claude",
                    "worker_role_provenance": verifier_provenance,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
            + "\n",
        )
        packet: dict[str, Any] = {
            "schema_version": 3,
            "bridge_id": BRIDGE_ID,
            "created_at": acquired_at,
            "expires_at": expires_at,
            "latest_status": "GO",
            "proposal_file": f"bridge/{BRIDGE_ID}-001.md",
            "go_file": f"bridge/{BRIDGE_ID}-002.md",
            "target_path_globs": ["app.py"],
            "project_authorization": {
                "id": PAUTH_ID,
                "version": 1,
                "status": "active",
                "project_id": PROJECT_ID,
                "work_item_id": WORK_ITEM,
            },
            "implementation_start": {
                "schema_version": 1,
                "bridge_id": BRIDGE_ID,
                "session_id": AUTHOR_SESSION,
                "finalized_at": acquired_at,
                "target_path_globs": ["app.py"],
                "work_intent_claim": claim,
                "worker_role_provenance": worker_provenance,
                "project_authorization_decision": {
                    "allowed": True,
                    "authorization_id": PAUTH_ID,
                    "authorization_version": 1,
                    "normalized_operation": "implementation_start",
                },
            },
        }
        packet["packet_hash"] = self._packet_hash(packet)
        _write(
            self.root,
            f".gtkb-state/implementation-authorizations/by-bridge/{BRIDGE_ID}.json",
            json.dumps(packet, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        )

    def _write_verdict(
        self,
        *,
        status: str,
        fields: dict[str, str],
        verifier_session: str = VERIFIER_SESSION,
        verifier_role: str = "loyal-opposition",
    ) -> Path:
        self.bridge_version += 1
        lines = [
            status,
            f"author_session_context_id: {verifier_session}",
            *(f"{key}: {value}" for key, value in fields.items()),
            f"Author-Session: {AUTHOR_SESSION}",
            "Author-Role: prime-builder",
            f"Verifier-Session: {verifier_session}",
            f"Verifier-Role: {verifier_role}",
        ]
        relative = f"bridge/{BRIDGE_ID}-{self.bridge_version:03d}.md"
        _write(self.root, relative, "\n".join(lines) + "\n")
        return self.root / relative

    def new_service(
        self,
        *,
        worker_probe: Callable[[], int] | None = None,
        command_boundary: Any | None = None,
    ) -> GitLifecycleService:
        return GitLifecycleService.for_testing(
            self.root,
            clock=self.clock,
            sleep=self.clock.sleep,
            worker_probe=worker_probe or self.worker_probe,
            command_boundary=command_boundary,
        )

    def bind(self, *, scope: tuple[str, ...] = ("app.py",)) -> dict[str, Any]:
        return self.service.bind_work_item(
            work_item_id=WORK_ITEM,
            title=TITLE,
            project_branch=PROJECT_BRANCH,
            scope_paths=scope,
            required_checks=CHECKS,
        ).to_dict()

    def preserve(self, *, operation_id: str = "commit-wi-1001-acceptance", crash_hook=None) -> dict[str, Any]:
        return self.service.preserve_scoped_changes(
            work_item_id=WORK_ITEM,
            message="feat: scoped modernization change",
            operation_id=operation_id,
            ttl_seconds=20,
            wait_seconds=1,
            crash_hook=crash_hook,
        ).to_dict()

    def passing_evidence(self, source_commit: str, **changes: Any) -> PromotionEvidence:
        payload: dict[str, Any] = {
            "subject_commit": source_commit,
            "author_session": AUTHOR_SESSION,
            "verifier_session": VERIFIER_SESSION,
            "verified": True,
            "checks": {name: {"status": "PASS", "subject_commit": source_commit} for name in CHECKS},
            "author_role": "prime-builder",
            "verifier_role": "loyal-opposition",
        }
        payload.update(changes)
        author_session = str(payload["author_session"])
        verifier_session = str(payload["verifier_session"])
        subject_commit = str(payload["subject_commit"])
        verdict_status = "VERIFIED" if payload["verified"] else "NO-GO"
        if author_session != AUTHOR_SESSION:
            raise AssertionError("fixture author session must remain bound to the canonical start packet")
        self._write_verdict(
            status=verdict_status,
            fields={"Subject-Commit": subject_commit, "Work-Item": WORK_ITEM, "Branch": WORK_BRANCH},
            verifier_session=verifier_session,
            verifier_role=str(payload["verifier_role"]),
        )
        if payload["author_role"] != "prime-builder":
            raise OperationDenied("verification_role_invalid", "canonical author role is not prime-builder")
        return self.service.issue_work_item_promotion_evidence(
            work_item_id=WORK_ITEM,
            bridge_id=BRIDGE_ID,
            checks=dict(payload["checks"]),
        )

    def reach_preserved(self, *, operation_id: str = "commit-wi-1001-acceptance") -> str:
        self.bind()
        _write(self.root, "app.py", "VALUE = 'modernized'\n")
        return self.preserve(operation_id=operation_id)["commit_sha"]

    def branch_promotion_evidence(
        self,
        *,
        promotion_kind: str,
        source_branch: str,
        target_branch: str,
        receipt_ids: tuple[str, ...],
        subject_id: str | None = None,
        source_commit: str | None = None,
        target_commit: str | None = None,
    ) -> PromotionEvidence:
        subject = source_commit or _git(self.root, "rev-parse", source_branch).stdout.strip()
        target = target_commit or _git(self.root, "rev-parse", target_branch).stdout.strip()
        selected_subject = subject_id or (PROJECT_ID if promotion_kind == "project_to_develop" else "RC-PILOT-001")
        self._write_verdict(
            status="VERIFIED",
            fields={
                "Promotion-Kind": promotion_kind,
                "Subject": selected_subject,
                "Source-Branch": source_branch,
                "Target-Branch": target_branch,
                "Subject-Commit": subject,
                "Target-Commit": target,
            },
        )
        receipts = {
            receipt_id: {"status": "PASS", "subject_commit": subject, "target_commit": target}
            for receipt_id in receipt_ids
        }
        return self.service.issue_branch_promotion_evidence(
            bridge_id=BRIDGE_ID,
            promotion_kind=promotion_kind,
            subject_id=selected_subject,
            source_branch=source_branch,
            target_branch=target_branch,
            required_receipts=(
                ("verification",) if promotion_kind == "project_to_develop" else ("integration", "non-impairment")
            ),
            receipts=receipts,
        )


class OfflineGitHubBoundary:
    """Deterministic GitHub model that never opens a process or network connection."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.pull_requests: dict[tuple[str, str], dict[str, Any]] = {}
        self.merge_commits: dict[str, dict[str, Any]] = {}
        self.fail_step: str | None = None
        self.after_call: Callable[[tuple[str, ...]], None] | None = None
        self.crash_step: str | None = None
        self.check_conclusion = "SUCCESS"
        self.check_names: tuple[str, ...] | None = None
        self.merge_parent_override: tuple[str, str] | None = None

    @staticmethod
    def _step(argv: tuple[str, ...]) -> str:
        if argv[:2] == ("git", "push"):
            return "publish_source"
        if argv[:3] == ("gh", "pr", "list"):
            return "pr_list"
        if argv[:3] == ("gh", "pr", "create"):
            return "pr_create"
        if argv[:3] == ("gh", "pr", "view"):
            return "pr_view"
        if argv[:3] == ("gh", "pr", "merge"):
            return "pr_merge"
        if argv[:2] == ("gh", "api"):
            return "merge_commit_view"
        return "unknown"

    @staticmethod
    def _argument(argv: tuple[str, ...], name: str) -> str:
        return argv[argv.index(name) + 1]

    def run(self, argv: Any, *, cwd: Path) -> CommandResult:
        exact = tuple(str(item) for item in argv)
        self.calls.append(exact)
        step = self._step(exact)
        if step == "unknown":
            raise AssertionError(f"unexpected external command: {exact}")
        if self.fail_step == step:
            return CommandResult(exact, 1, stderr=f"simulated {step} failure")
        stdout = ""
        if step == "pr_list":
            key = (self._argument(exact, "--head"), self._argument(exact, "--base"))
            stdout = json.dumps([self.pull_requests[key]] if key in self.pull_requests else [])
        elif step == "pr_create":
            head = self._argument(exact, "--head")
            base = self._argument(exact, "--base")
            source = _git(cwd, "rev-parse", head).stdout.strip()
            target = _git(cwd, "rev-parse", base).stdout.strip()
            default_checks = ("verification",) if base == "develop" else ("integration", "non-impairment")
            check_names = self.check_names or default_checks
            url = f"https://github.com/example/gtkb/pull/{len(self.pull_requests) + 1}"
            self.pull_requests[(head, base)] = {
                "url": url,
                "state": "OPEN",
                "body": self._argument(exact, "--body"),
                "headRefName": head,
                "baseRefName": base,
                "headRefOid": source,
                "baseRefOid": target,
                "mergeCommit": None,
                "statusCheckRollup": [{"name": name, "conclusion": self.check_conclusion} for name in check_names],
            }
            stdout = url + "\n"
        elif step == "pr_view":
            url = exact[3]
            payload = next((item for item in self.pull_requests.values() if item["url"] == url), None)
            if payload is None:
                return CommandResult(exact, 1, stderr="pull request missing")
            stdout = json.dumps(payload)
        elif step == "pr_merge":
            url = exact[3]
            payload = next((item for item in self.pull_requests.values() if item["url"] == url), None)
            if payload is None:
                return CommandResult(exact, 1, stderr="pull request missing")
            payload["state"] = "MERGED"
            parents = self.merge_parent_override or (payload["baseRefOid"], payload["headRefOid"])
            merge_sha = hashlib.sha1(  # noqa: S324 - deterministic fake Git object identity
                f"{parents[1]}:{parents[0]}".encode("ascii")
            ).hexdigest()
            payload["mergeCommit"] = {"oid": merge_sha}
            self.merge_commits[merge_sha] = {
                "sha": merge_sha,
                "parents": [{"sha": parent} for parent in parents],
            }
            payload["baseRefOid"] = payload["mergeCommit"]["oid"]
        elif step == "merge_commit_view":
            merge_sha = exact[2].rsplit("/", 1)[-1]
            payload = self.merge_commits.get(merge_sha)
            if payload is None:
                return CommandResult(exact, 1, stderr="merge commit missing")
            stdout = json.dumps(payload)
        if self.after_call is not None:
            self.after_call(exact)
        if self.crash_step == step:
            self.crash_step = None
            raise SimulatedProcessExit()
        return CommandResult(exact, 0, stdout=stdout)


def _denial(call: Callable[[], object], expected_code: str) -> OperationDenied:
    try:
        call()
    except OperationDenied as exc:
        if exc.code != expected_code:
            raise AssertionError(f"expected denial {expected_code}, got {exc.to_dict()}") from exc
        return exc
    raise AssertionError(f"expected denial {expected_code}, operation passed")


def _cli_process(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(PACKAGE_SRC), env.get("PYTHONPATH", ""))))
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.git_lifecycle",
            *args,
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _cli(root: Path, *args: str) -> dict[str, Any]:
    result = _cli_process(root, "--json", *args)
    if result.returncode != 0:
        raise AssertionError(f"CLI {' '.join(args)} failed: {result.stdout}{result.stderr}")
    return json.loads(result.stdout)


def _inprocess_cli(root: Path, command_boundary: Any, *args: str) -> dict[str, Any]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with (
        patch("groundtruth_kb.git_lifecycle.__main__.Path.cwd", return_value=root),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        result = lifecycle_cli_main(
            ("--json", *args),
            command_boundary=command_boundary,
        )
    if result != 0:
        raise AssertionError(f"in-process CLI {' '.join(args)} failed: {stdout.getvalue()}{stderr.getvalue()}")
    return json.loads(stdout.getvalue())


def _reach_project_promotion_ready(fixture: Fixture) -> str:
    _git(fixture.root, "branch", "develop", "main")
    _git(fixture.root, "branch", "stage", "main")
    source = fixture.reach_preserved()
    _git(fixture.root, "checkout", PROJECT_BRANCH)
    fixture.service.promote_work_item(
        work_item_id=WORK_ITEM,
        evidence=fixture.passing_evidence(source),
        operation_id="promote-wi-1001-before-project",
        ttl_seconds=20,
        wait_seconds=1,
    )
    return _git(fixture.root, "rev-parse", PROJECT_BRANCH).stdout.strip()


def _assert_a1(root: Path) -> str:
    fixture = Fixture(root)
    fixture.state_dir.mkdir(parents=True)
    (fixture.state_dir / "git-lifecycle.lock").write_text(
        canonical_json(
            {
                "schema_version": 1,
                "pid": 2_000_000_000,
                "process_create_time": 1.0,
                "acquired_at_epoch": 1.0,
                "owner_token": "stale-owner",
            }
        )
        + "\n",
        encoding="ascii",
    )
    result = fixture.bind()
    registry = json.loads((fixture.state_dir / "branch-bindings.json").read_text(encoding="ascii"))
    record = registry["bindings"][WORK_ITEM]
    assert result["code"] == "binding_created"
    assert record["branch"] == WORK_BRANCH
    assert record["project_branch"] == PROJECT_BRANCH
    assert record["scope_paths"] == ["app.py"]
    assert record["required_checks"] == ["policy", "unit"]
    recovery = fixture.state_dir / "git-lifecycle-lock-recovery.jsonl"
    assert "stale-owner" in recovery.read_text(encoding="ascii")
    return (
        f"binding={record['binding_id']}; branch={record['branch']}; "
        f"generation={record['generation']}; stale_lock_recovered=true"
    )


def _assert_a2(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    _git(root, "checkout", PROJECT_BRANCH)
    _write(root, "app.py", "VALUE = 'wrong branch'\n")
    before_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    before_bytes = (root / "app.py").read_bytes()
    denial = _denial(lambda: fixture.preserve(), "wrong_branch")
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before_head
    assert (root / "app.py").read_bytes() == before_bytes
    assert not fixture.dispatcher_dir.exists()
    return canonical_json(denial.to_dict())


def _assert_a3(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    before = (fixture.state_dir / "branch-bindings.json").read_bytes()
    denial = _denial(lambda: fixture.bind(scope=("unrelated.txt",)), "binding_conflict")
    assert (fixture.state_dir / "branch-bindings.json").read_bytes() == before
    return canonical_json(denial.to_dict())


def _assert_a4(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    _write(root, "app.py", "VALUE = 'scoped'\n")
    _write(root, "unrelated.txt", "unrelated staged\n")
    _git(root, "add", "unrelated.txt")
    _write(root, "notes.tmp", "untracked bytes\n")
    _write(root, "scratch.log", "ignored bytes\n")
    staged_before = _git(root, "diff", "--cached", "--binary", "--", "unrelated.txt").stdout
    result = fixture.preserve()
    committed = _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", result["commit_sha"]).stdout.split()
    assert committed == ["app.py"]
    assert _git(root, "diff", "--cached", "--binary", "--", "unrelated.txt").stdout == staged_before
    assert (root / "notes.tmp").read_text(encoding="utf-8") == "untracked bytes\n"
    assert (root / "scratch.log").read_text(encoding="utf-8") == "ignored bytes\n"
    assert not (fixture.dispatcher_dir / "dispatch-drain.json").exists()
    return f"commit={result['commit_sha']}; committed_paths={committed}; unrelated_preserved=true"


def _assert_a5(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    before_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    denial = _denial(lambda: fixture.preserve(), "scope_has_no_changes")
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before_head
    assert not fixture.dispatcher_dir.exists()
    return canonical_json(denial.to_dict())


def _assert_a6(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    _write(root, "app.py", "VALUE = 'blocked'\n")
    marker = fixture.dispatcher_dir / "dispatch-drain.json"
    marker.parent.mkdir(parents=True)
    marker.write_text("{malformed", encoding="ascii")
    before_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    marker_denial = _denial(lambda: fixture.preserve(), "quiescence_malformed")
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before_head
    assert marker.read_text(encoding="ascii") == "{malformed"
    fixture.service.recover_quiescence(reason="replace malformed prior marker")
    runs_dir = fixture.dispatcher_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "broken.pid").write_text("not-a-pid\n", encoding="ascii")
    strict_service = GitLifecycleService(
        root,
        clock=fixture.clock,
        sleep=fixture.clock.sleep,
    )
    worker_denial = _denial(
        lambda: strict_service.preserve_scoped_changes(
            work_item_id=WORK_ITEM,
            message="feat: must remain blocked",
            operation_id="commit-wi-1001-malformed-worker",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "dispatcher_worker_state_malformed",
    )
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before_head
    return f"marker={marker_denial.code}; worker={worker_denial.code}; head_unchanged=true"


def _assert_a7(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    _write(root, "app.py", "VALUE = 'after recovery'\n")
    marker = fixture.dispatcher_dir / "dispatch-drain.json"
    marker.parent.mkdir(parents=True)
    marker.write_text(
        canonical_json(
            {
                "schema_version": 1,
                "owner": "gtkb-git-lifecycle",
                "operation_id": "old-operation",
                "active": True,
                "phase": "quiesced",
                "issued_at_epoch": fixture.clock() - 20,
                "expires_at_epoch": fixture.clock() - 10,
                "observed_workers": 0,
            }
        )
        + "\n",
        encoding="ascii",
    )
    _denial(lambda: fixture.preserve(), "quiescence_stale")
    recovery = fixture.service.recover_quiescence(reason="stale lease after interrupted prior operation")
    result = fixture.preserve(operation_id="commit-wi-1001-after-recovery")
    assert recovery["operation_id"] == "old-operation"
    assert result["code"] == "scoped_commit_preserved"
    assert not marker.exists()
    return f"recovered={recovery['operation_id']}; commit={result['commit_sha']}"


def _assert_a8(root: Path) -> str:
    fixture = Fixture(root, worker_probe=lambda: 1)
    fixture.bind()
    _write(root, "app.py", "VALUE = 'waited'\n")
    before_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    denial = _denial(
        lambda: fixture.service.preserve_scoped_changes(
            work_item_id=WORK_ITEM,
            message="feat: timeout",
            operation_id="commit-wi-1001-timeout",
            ttl_seconds=5,
            wait_seconds=0.1,
        ),
        "quiescence_timeout",
    )
    marker = json.loads((fixture.dispatcher_dir / "dispatch-drain.json").read_text(encoding="ascii"))
    assert marker["phase"] == "timeout" and marker["observed_workers"] == 1
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before_head
    fixture.service.recover_quiescence(reason="bounded drain timed out")
    recovered_service = fixture.new_service(worker_probe=lambda: 0)
    result = recovered_service.preserve_scoped_changes(
        work_item_id=WORK_ITEM,
        message="feat: resumed after timeout",
        operation_id="commit-wi-1001-timeout-retry",
        ttl_seconds=5,
        wait_seconds=0.1,
    )

    race_dir = root / ".gtkb-state" / "quiescence-race"
    barrier = Barrier(2)
    original_create = quiescence_module._create_marker_exclusive

    def synchronized_create(path: Path, payload: dict[str, Any]) -> bool:
        barrier.wait(timeout=5)
        return original_create(path, payload)

    def contend(operation_id: str) -> str:
        try:
            acquired = acquire_dispatcher_quiescence(
                race_dir,
                operation_id=operation_id,
                ttl_seconds=5,
                wait_seconds=0.1,
                clock=fixture.clock,
                sleep=fixture.clock.sleep,
                worker_probe=lambda: 0,
            )
        except OperationDenied as exc:
            return exc.code
        return f"acquired:{acquired['operation_id']}"

    with (
        patch.object(quiescence_module, "_create_marker_exclusive", synchronized_create),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        outcomes = sorted(executor.map(contend, ("race-operation-a", "race-operation-b")))
    assert sum(item.startswith("acquired:") for item in outcomes) == 1
    assert sum(item in {"quiescence_conflict", "quiescence_not_ready"} for item in outcomes) == 1

    inflight_dir = root / ".gtkb-state" / "inflight-race"
    inflight_dir.mkdir(parents=True)
    (inflight_dir / "dispatcher-runtime-inflight.lock").write_text(
        canonical_json(
            {
                "schema_version": 1,
                "token": "active-dispatch-cycle",
                "pid": 123,
                "acquired_at_epoch": fixture.clock(),
            }
        )
        + "\n",
        encoding="ascii",
    )
    assert active_dispatcher_workers(inflight_dir, now=fixture.clock()) == 1
    inflight_denial = _denial(
        lambda: acquire_dispatcher_quiescence(
            inflight_dir,
            operation_id="drain-vs-inflight",
            ttl_seconds=5,
            wait_seconds=0.1,
            clock=fixture.clock,
            sleep=fixture.clock.sleep,
        ),
        "quiescence_timeout",
    )
    recover_dispatcher_quiescence(
        inflight_dir,
        now=fixture.clock(),
        reason="bounded inflight race acceptance",
    )
    return (
        f"denial={denial.code}; recovered_commit={result.commit_sha}; exclusive_outcomes={outcomes}; "
        f"inflight={inflight_denial.code}"
    )


def _assert_a9(root: Path) -> str:
    fixture = Fixture(root)
    source = fixture.reach_preserved()
    _git(root, "checkout", PROJECT_BRANCH)
    before = _git(root, "rev-parse", "HEAD").stdout.strip()
    denial = _denial(
        lambda: fixture.passing_evidence(source, verified=False),
        "implementation_start_superseded",
    )
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before
    return canonical_json(denial.to_dict())


def _assert_a10(root: Path) -> str:
    fixture = Fixture(root)
    source = fixture.reach_preserved()
    _git(root, "checkout", PROJECT_BRANCH)
    before = _git(root, "rev-parse", "HEAD").stdout.strip()
    issuance_codes = [
        _denial(
            lambda: fixture.passing_evidence(source, verifier_session=AUTHOR_SESSION),
            "verification_not_independent",
        ).code,
        _denial(lambda: fixture.passing_evidence("0" * 40), "verification_subject_mismatch").code,
        _denial(
            lambda: fixture.passing_evidence(
                source,
                checks={"unit": {"status": "PASS", "subject_commit": source}},
            ),
            "required_check_missing",
        ).code,
        _denial(
            lambda: fixture.passing_evidence(source, verifier_role="prime-builder"),
            "verification_role_invalid",
        ).code,
    ]
    tampered_bundle = fixture.passing_evidence(source)
    (root / tampered_bundle.bundle_path).write_text("{}\n", encoding="ascii")
    arbitrary_path = root / "evidence" / "caller-authored.json"
    arbitrary_path.parent.mkdir(parents=True, exist_ok=True)
    arbitrary_path.write_text("{}\n", encoding="ascii")
    arbitrary = PromotionEvidence(
        bundle_path=arbitrary_path.relative_to(root).as_posix(),
        bundle_sha256=hashlib.sha256(arbitrary_path.read_bytes()).hexdigest().upper(),
    )
    codes = issuance_codes + [
        _denial(
            lambda: fixture.service.promote_work_item(work_item_id=WORK_ITEM, evidence=tampered_bundle),
            "evidence_bundle_hash_mismatch",
        ).code,
        _denial(
            lambda: fixture.service.promote_work_item(work_item_id=WORK_ITEM, evidence=arbitrary),
            "promotion_evidence_untrusted",
        ).code,
    ]
    audit_evidence = fixture.passing_evidence(source)
    audit_path = fixture.state_dir / "promotion-receipts" / "issuer-audit.jsonl"
    audit_lines = audit_path.read_text(encoding="ascii").splitlines()
    final_event = json.loads(audit_lines[-1])
    final_event["event_hash"] = "0" * 64
    audit_lines[-1] = canonical_json(final_event)
    audit_path.write_text("\n".join(audit_lines) + "\n", encoding="ascii", newline="\n")
    codes.append(
        _denial(
            lambda: fixture.service.promote_work_item(work_item_id=WORK_ITEM, evidence=audit_evidence),
            "promotion_issuer_audit_invalid",
        ).code
    )
    assert _git(root, "rev-parse", "HEAD").stdout.strip() == before
    return f"denials={','.join(codes)}; head_unchanged=true"


def _assert_a11(root: Path) -> str:
    fixture = Fixture(root)
    source = fixture.reach_preserved()
    _git(root, "checkout", PROJECT_BRANCH)
    result = fixture.service.promote_work_item(
        work_item_id=WORK_ITEM,
        evidence=fixture.passing_evidence(source),
        operation_id="promote-wi-1001-acceptance",
        ttl_seconds=20,
        wait_seconds=1,
    ).to_dict()
    parents = _git(root, "show", "-s", "--format=%P", result["commit_sha"]).stdout.strip().split()
    registry = json.loads((fixture.state_dir / "branch-bindings.json").read_text(encoding="ascii"))
    assert len(parents) == 2 and parents[1] == source
    assert registry["bindings"][WORK_ITEM]["lifecycle_state"] == "promoted"
    assert registry["bindings"][WORK_ITEM]["promoted_commit"] == result["commit_sha"]
    assert not (fixture.dispatcher_dir / "dispatch-drain.json").exists()
    return f"promotion={result['commit_sha']}; parents={','.join(parents)}"


def _crash(_: str) -> None:
    raise SimulatedProcessExit()


def _assert_a12(root: Path) -> str:
    fixture = Fixture(root)
    fixture.bind()
    _write(root, "app.py", "VALUE = 'survived crash'\n")
    operation_id = "commit-wi-1001-crash-recovery"
    before = _git(root, "rev-parse", "HEAD").stdout.strip()
    try:
        fixture.preserve(operation_id=operation_id, crash_hook=_crash)
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated process exit did not interrupt preservation")
    after = _git(root, "rev-parse", "HEAD").stdout.strip()
    assert after != before
    transaction = json.loads((fixture.state_dir / "transactions" / f"{operation_id}.json").read_text(encoding="ascii"))
    assert transaction["phase"] == "prepared"
    result = fixture.new_service().resume_operation(operation_id).to_dict()
    assert result["code"] == "preserve_recovered" and result["commit_sha"] == after
    assert not (fixture.dispatcher_dir / "dispatch-drain.json").exists()
    repeated = fixture.new_service().resume_operation(operation_id).to_dict()
    assert repeated["code"] == "operation_already_completed"

    late_fixture = Fixture(root / "late-state-recovery")
    late_fixture.bind()
    _write(late_fixture.root, "app.py", "VALUE = 'state applied before exit'\n")
    late_operation = "commit-wi-1001-late-state-recovery"

    def crash_after_audit(phase: str) -> None:
        if phase == "audit_appended":
            raise SimulatedProcessExit()

    late_fixture.service.state.fault_hook = crash_after_audit
    try:
        late_fixture.preserve(operation_id=late_operation)
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated late state exit did not interrupt preservation")
    late_commit = _git(late_fixture.root, "rev-parse", "HEAD").stdout.strip()
    late_result = late_fixture.new_service().resume_operation(late_operation).to_dict()
    assert late_result["code"] == "preserve_recovered" and late_result["commit_sha"] == late_commit
    assert late_result["details"]["state_transition_already_applied"] is True
    return f"recovered={after}; replay={repeated['code']}; late_state_recovered={late_commit}"


def _assert_a13(root: Path) -> str:
    fixture = Fixture(root)
    source = fixture.reach_preserved()
    _git(root, "checkout", PROJECT_BRANCH)
    operation_id = "promote-wi-1001-crash-recovery"
    before = _git(root, "rev-parse", "HEAD").stdout.strip()
    try:
        fixture.service.promote_work_item(
            work_item_id=WORK_ITEM,
            evidence=fixture.passing_evidence(source),
            operation_id=operation_id,
            ttl_seconds=20,
            wait_seconds=1,
            crash_hook=_crash,
        )
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated process exit did not interrupt promotion")
    merged = _git(root, "rev-parse", "HEAD").stdout.strip()
    assert merged != before
    result = fixture.new_service().resume_operation(operation_id).to_dict()
    assert result["code"] == "promote_recovered" and result["commit_sha"] == merged
    audit_lines = [
        json.loads(line)
        for line in (fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii").splitlines()
    ]
    previous = "0" * 64
    for event in audit_lines:
        assert event["previous_hash"] == previous
        expected = sha256_json({key: value for key, value in event.items() if key != "event_hash"})
        assert event["event_hash"] == expected
        previous = event["event_hash"]
    assert canonical_json(result) == canonical_json(json.loads(canonical_json(result)))
    audit_lines[0]["event_type"] = "tampered"
    (fixture.state_dir / "branch-binding-audit.jsonl").write_text(
        "\n".join(canonical_json(item) for item in audit_lines) + "\n",
        encoding="ascii",
        newline="\n",
    )
    _denial(
        lambda: fixture.service.state.append_audit({"event_type": "must-not-append"}),
        "audit_chain_malformed",
    )

    journal_fixture = Fixture(root / "journal-recovery")

    def crash_after_registry(phase: str) -> None:
        if phase == "registry_replaced":
            raise SimulatedProcessExit()

    journal_fixture.service.state.fault_hook = crash_after_registry
    try:
        journal_fixture.bind()
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated state-commit exit did not interrupt binding")
    assert (journal_fixture.state_dir / "state-commit-journal.json").is_file()
    recovery_service = journal_fixture.new_service()
    recovered_binding = recovery_service.bind_work_item(
        work_item_id=WORK_ITEM,
        title=TITLE,
        project_branch=PROJECT_BRANCH,
        scope_paths=("app.py",),
        required_checks=CHECKS,
    )
    assert recovered_binding.code == "binding_already_current"
    assert not (journal_fixture.state_dir / "state-commit-journal.json").exists()
    recovered_audit = (journal_fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii")
    assert recovered_audit.count("binding_created") == 1
    return (
        f"recovered={merged}; audit_events={len(audit_lines)}; deterministic_json=true; "
        "tamper_denied=true; journal_recovered=true"
    )


def _assert_a14(root: Path) -> str:
    fixture = Fixture(root)
    _git(root, "checkout", PROJECT_BRANCH)
    _git(root, "branch", "-D", WORK_BRANCH)
    dry_run = _cli(
        root,
        "--dry-run",
        "create",
        "--work-item-id",
        WORK_ITEM,
        "--title",
        TITLE,
        "--project-branch",
        PROJECT_BRANCH,
    )
    assert dry_run["status"] == "DRY-RUN" and not fixture.service.repo.branch_exists(WORK_BRANCH)
    created = _cli(
        root,
        "create",
        "--work-item-id",
        WORK_ITEM,
        "--title",
        TITLE,
        "--project-branch",
        PROJECT_BRANCH,
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    attached = _cli(
        root,
        "attach",
        "--work-item-id",
        WORK_ITEM,
        "--title",
        TITLE,
        "--project-branch",
        PROJECT_BRANCH,
        "--scope",
        "app.py",
        "--required-check",
        "unit",
        "--required-check",
        "policy",
    )
    assert _cli(root, "show", "--work-item-id", WORK_ITEM)["binding"]["branch"] == WORK_BRANCH
    assert _cli(root, "validate", "--work-item-id", WORK_ITEM)["code"] == "binding_valid"
    _write(root, "app.py", "VALUE = 'cli pilot'\n")
    preserved = _cli(
        root,
        "preserve",
        "--work-item-id",
        WORK_ITEM,
        "--message",
        "feat: CLI pilot",
        "--operation-id",
        "cli-preserve-pilot",
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    evidence = fixture.passing_evidence(preserved["commit_sha"])
    _git(root, "checkout", PROJECT_BRANCH)
    promoted = _cli(
        root,
        "promote",
        "--level",
        "work-item",
        "--work-item-id",
        WORK_ITEM,
        "--evidence-path",
        evidence.bundle_path,
        "--evidence-sha256",
        evidence.bundle_sha256,
        "--operation-id",
        "cli-promote-pilot",
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    closed = _cli(root, "close", "--work-item-id", WORK_ITEM)
    resumed = _cli(root, "resume", "--operation-id", "cli-promote-pilot")
    acquired = _cli(
        root,
        "drain",
        "acquire",
        "--operation-id",
        "cli-bounded-drain",
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    verified = _cli(root, "drain", "verify", "--operation-id", "cli-bounded-drain")
    released = _cli(root, "drain", "release", "--operation-id", "cli-bounded-drain")
    fixture.dispatcher_dir.mkdir(parents=True, exist_ok=True)
    (fixture.dispatcher_dir / "dispatch-drain.json").write_text("{malformed", encoding="ascii")
    recovered = _cli(root, "recover", "--reason", "replace malformed drain after interrupted command")
    assert created["code"] == "work_branch_created"
    assert attached["code"] == "binding_created"
    assert promoted["code"] == "work_item_promoted" and closed["code"] == "binding_closed"
    assert resumed["code"] == "operation_already_completed"
    assert acquired["phase"] == "quiesced" and verified["phase"] == "quiesced"
    assert released["status"] == "PASS" and recovered["action"] == "recover_quiescence"
    return "dry-run/create/attach/show/validate/preserve/promote/close/resume/recover/drain CLI pilot passed"


def _assert_a15(root: Path) -> str:
    fixture = Fixture(root)
    project_commit = _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    project_evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    project_result = _inprocess_cli(
        root,
        boundary,
        "promote",
        "--level",
        "project",
        "--project-id",
        "PROJECT-MODERNIZATION",
        "--project-branch",
        PROJECT_BRANCH,
        "--evidence-path",
        project_evidence.bundle_path,
        "--evidence-sha256",
        project_evidence.bundle_sha256,
        "--operation-id",
        "pr-project-to-develop-pilot",
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    _git(root, "checkout", "develop")
    _git(root, "merge", "--ff-only", PROJECT_BRANCH)
    stage_evidence = fixture.branch_promotion_evidence(
        promotion_kind="develop_to_stage",
        source_branch="develop",
        target_branch="stage",
        receipt_ids=("integration", "non-impairment"),
    )
    stage_result = _inprocess_cli(
        root,
        boundary,
        "promote",
        "--level",
        "stage",
        "--release-id",
        "RC-PILOT-001",
        "--evidence-path",
        stage_evidence.bundle_path,
        "--evidence-sha256",
        stage_evidence.bundle_sha256,
        "--operation-id",
        "pr-develop-to-stage-pilot",
        "--ttl-seconds",
        "20",
        "--wait-seconds",
        "1",
    )
    push_calls = [call for call in boundary.calls if call[:2] == ("git", "push")]
    merge_calls = [call for call in boundary.calls if call[:3] == ("gh", "pr", "merge")]
    assert project_result["code"] == "project_to_develop_completed"
    assert stage_result["code"] == "develop_to_stage_completed"
    assert project_result["details"]["source_commit"] == project_commit
    assert len(push_calls) == 1 and push_calls[0][-1] == f"{PROJECT_BRANCH}:{PROJECT_BRANCH}"
    assert len(merge_calls) == 2 and len(boundary.pull_requests) == 2
    return (
        f"project_pr={project_result['details']['pr_url']}; "
        f"stage_pr={stage_result['details']['pr_url']}; offline_cli=true"
    )


def _assert_a16(root: Path) -> str:
    direct = _denial(
        lambda: GitLifecycleService.validate_remote_push(PROJECT_BRANCH, "develop"),
        "direct_push_prohibited",
    )
    rewrite = _denial(
        lambda: GitLifecycleService.validate_remote_push(PROJECT_BRANCH, "project/another"),
        "remote_ref_rewrite_prohibited",
    )

    stale_fixture = Fixture(root / "stale")
    _reach_project_promotion_ready(stale_fixture)
    stale_boundary = OfflineGitHubBoundary()
    stale = _denial(
        lambda: stale_fixture.branch_promotion_evidence(
            promotion_kind="project_to_develop",
            source_branch=PROJECT_BRANCH,
            target_branch="develop",
            receipt_ids=("verification",),
            source_commit="0" * 40,
        ),
        "verification_subject_mismatch",
    )
    assert not stale_boundary.calls

    receipt_fixture = Fixture(root / "receipts")
    _git(receipt_fixture.root, "branch", "develop", "main")
    _git(receipt_fixture.root, "branch", "stage", "main")
    _git(receipt_fixture.root, "checkout", "develop")
    _write(receipt_fixture.root, "integration.txt", "integrated\n")
    _git(receipt_fixture.root, "add", "integration.txt")
    _git(receipt_fixture.root, "commit", "-m", "advance develop")
    receipt_boundary = OfflineGitHubBoundary()
    missing_receipt = _denial(
        lambda: receipt_fixture.branch_promotion_evidence(
            promotion_kind="develop_to_stage",
            subject_id="RC-MISSING-NONIMPAIRMENT",
            source_branch="develop",
            target_branch="stage",
            receipt_ids=("integration",),
        ),
        "promotion_receipt_missing",
    )
    assert not receipt_boundary.calls

    ancestry_fixture = Fixture(root / "ancestry")
    _reach_project_promotion_ready(ancestry_fixture)
    _git(ancestry_fixture.root, "checkout", "develop")
    _write(ancestry_fixture.root, "develop-only.txt", "diverged\n")
    _git(ancestry_fixture.root, "add", "develop-only.txt")
    _git(ancestry_fixture.root, "commit", "-m", "diverge develop")
    _git(ancestry_fixture.root, "checkout", PROJECT_BRANCH)
    ancestry = _denial(
        lambda: ancestry_fixture.new_service(command_boundary=OfflineGitHubBoundary()).promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=ancestry_fixture.branch_promotion_evidence(
                promotion_kind="project_to_develop",
                source_branch=PROJECT_BRANCH,
                target_branch="develop",
                receipt_ids=("verification",),
            ),
        ),
        "promotion_ancestry_invalid",
    )

    failed_fixture = Fixture(root / "pr-failure")
    _reach_project_promotion_ready(failed_fixture)
    failed_boundary = OfflineGitHubBoundary()
    failed_boundary.fail_step = "pr_create"
    failed_service = failed_fixture.new_service(command_boundary=failed_boundary)
    failed_evidence = failed_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    failed = _denial(
        lambda: failed_service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=failed_evidence,
            operation_id="pr-create-failure",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_command_failed",
    )
    assert not failed_boundary.pull_requests

    checks_fixture = Fixture(root / "pr-checks")
    _reach_project_promotion_ready(checks_fixture)
    checks_boundary = OfflineGitHubBoundary()
    checks_boundary.check_conclusion = "FAILURE"
    checks_service = checks_fixture.new_service(command_boundary=checks_boundary)
    checks_evidence = checks_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    failed_checks = _denial(
        lambda: checks_service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=checks_evidence,
            operation_id="pr-checks-failure",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_checks_failed",
    )
    assert not [call for call in checks_boundary.calls if call[:3] == ("gh", "pr", "merge")]

    skipped_fixture = Fixture(root / "pr-skipped-check")
    _reach_project_promotion_ready(skipped_fixture)
    skipped_boundary = OfflineGitHubBoundary()
    skipped_boundary.check_conclusion = "SKIPPED"
    skipped_evidence = skipped_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    skipped = _denial(
        lambda: skipped_fixture.new_service(command_boundary=skipped_boundary).promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=skipped_evidence,
            operation_id="pr-skipped-check",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_checks_failed",
    )
    assert not [call for call in skipped_boundary.calls if call[:3] == ("gh", "pr", "merge")]

    mismatch_fixture = Fixture(root / "pr-check-set-mismatch")
    _reach_project_promotion_ready(mismatch_fixture)
    mismatch_boundary = OfflineGitHubBoundary()
    mismatch_boundary.check_names = ("verification", "uncontracted-check")
    mismatch_evidence = mismatch_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    mismatch = _denial(
        lambda: mismatch_fixture.new_service(command_boundary=mismatch_boundary).promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=mismatch_evidence,
            operation_id="pr-check-set-mismatch",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_checks_mismatch",
    )
    assert not [call for call in mismatch_boundary.calls if call[:3] == ("gh", "pr", "merge")]
    return (
        f"direct={direct.code}; rewrite={rewrite.code}; stale={stale.code}; "
        f"receipt={missing_receipt.code}; ancestry={ancestry.code}; "
        f"pr={failed.code}; checks={failed_checks.code}; skipped={skipped.code}; exact_set={mismatch.code}"
    )


def _assert_a17(root: Path) -> str:
    fixture = Fixture(root)
    _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    service = fixture.new_service(command_boundary=boundary)
    evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )

    def lose_lease(argv: tuple[str, ...]) -> None:
        if argv[:2] == ("git", "push"):
            (fixture.dispatcher_dir / "dispatch-drain.json").unlink()

    boundary.after_call = lose_lease
    denial = _denial(
        lambda: service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=evidence,
            operation_id="pr-lease-loss",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "quiescence_lease_lost",
    )
    _denial(lambda: service.resume_operation("pr-lease-loss"), "explicit_recovery_required")
    recovery = service.recover_operation(operation_id="pr-lease-loss", reason="lease disappeared after source publish")
    boundary.after_call = None
    resumed = service.resume_operation("pr-lease-loss")
    assert recovery["prior_phase"] == "lease_lost_after_publish_source"
    assert resumed.code == "project_to_develop_completed"
    return f"denial={denial.code}; recovery={recovery['status']}; resumed={resumed.commit_sha}"


def _assert_a18(root: Path) -> str:
    fixture = Fixture(root)
    _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    boundary.crash_step = "pr_create"
    service = fixture.new_service(command_boundary=boundary)
    evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    try:
        service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=evidence,
            operation_id="pr-create-crash",
            ttl_seconds=20,
            wait_seconds=1,
        )
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated PR-create process loss did not occur")
    resumed = fixture.new_service(command_boundary=boundary).resume_operation("pr-create-crash")
    create_calls = [call for call in boundary.calls if call[:3] == ("gh", "pr", "create")]
    assert resumed.code == "project_to_develop_completed"
    assert len(create_calls) == 1 and len(boundary.pull_requests) == 1
    repeated = fixture.new_service(command_boundary=boundary).resume_operation("pr-create-crash")
    assert repeated.code == "operation_already_completed"
    return f"resumed={resumed.commit_sha}; pr_create_count=1; replay={repeated.code}; offline=true"


def _assert_a19(root: Path) -> str:
    fixture = Fixture(root)
    _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    service = fixture.new_service(command_boundary=boundary)
    evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    bundle_path = root / evidence.bundle_path

    def tamper_before_merge(argv: tuple[str, ...]) -> None:
        if argv[:3] == ("gh", "pr", "view"):
            bundle_path.write_text("{}\n", encoding="ascii")

    boundary.after_call = tamper_before_merge
    denial = _denial(
        lambda: service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=evidence,
            operation_id="pr-hosted-evidence-tamper",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "evidence_bundle_hash_mismatch",
    )
    merge_calls = [call for call in boundary.calls if call[:3] == ("gh", "pr", "merge")]
    assert not merge_calls

    parent_fixture = Fixture(root / "merged-parent-mismatch")
    _reach_project_promotion_ready(parent_fixture)
    parent_boundary = OfflineGitHubBoundary()
    parent_boundary.merge_parent_override = (
        "f" * 40,
        _git(parent_fixture.root, "rev-parse", PROJECT_BRANCH).stdout.strip(),
    )
    parent_evidence = parent_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    parent_denial = _denial(
        lambda: parent_fixture.new_service(command_boundary=parent_boundary).promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=parent_evidence,
            operation_id="pr-merged-parent-mismatch",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_merge_parent_mismatch",
    )
    parent_transaction = parent_fixture.service.state.load_transaction("pr-merged-parent-mismatch")
    completion_audit = (
        (parent_fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii")
        if (parent_fixture.state_dir / "branch-binding-audit.jsonl").exists()
        else ""
    )
    assert parent_transaction["phase"] == "failed_hosted_validation"
    assert "pull_request_promotion_completed" not in completion_audit
    assert len([call for call in parent_boundary.calls if call[:2] == ("gh", "api")]) == 1
    return (
        f"denial={denial.code}; merge_calls=0; immutable_until_merge=true; "
        f"merged_parent={parent_denial.code}; unrelated_merge_not_qualified=true"
    )


def _assert_a20(root: Path) -> str:
    fixture = Fixture(root)
    _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    service = fixture.new_service(command_boundary=boundary)
    evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )

    def exit_after_transaction_replace(phase: str) -> None:
        if phase == "transaction_replaced":
            raise SimulatedProcessExit()

    service.state.fault_hook = exit_after_transaction_replace
    try:
        service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=evidence,
            operation_id="pr-audit-crash",
            ttl_seconds=20,
            wait_seconds=1,
        )
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated transaction-before-audit process loss did not occur")
    journal_path = fixture.state_dir / "transaction-audit-journal.json"
    transaction_before = json.loads(
        (fixture.state_dir / "transactions" / "pr-audit-crash.json").read_text(encoding="ascii")
    )
    assert journal_path.is_file() and transaction_before["phase"] == "completed"
    assert transaction_before["completion_occurred_at"]
    pending = _denial(
        lambda: service.state.load_transaction("pr-audit-crash"),
        "transaction_journal_pending",
    )
    resumed = fixture.new_service(command_boundary=boundary).resume_operation("pr-audit-crash")
    audit = [
        json.loads(line)
        for line in (fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii").splitlines()
    ]
    matches = [item for item in audit if item.get("operation_id") == "pr-audit-crash"]
    assert resumed.code == "operation_already_completed" and len(matches) == 1
    assert matches[0]["occurred_at"] == transaction_before["completion_occurred_at"]
    assert not journal_path.exists()

    recovery_fixture = Fixture(root / "recovery-authorization-journal")
    _reach_project_promotion_ready(recovery_fixture)
    recovery_boundary = OfflineGitHubBoundary()
    recovery_boundary.fail_step = "pr_create"
    recovery_service = recovery_fixture.new_service(command_boundary=recovery_boundary)
    recovery_evidence = recovery_fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    _denial(
        lambda: recovery_service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=recovery_evidence,
            operation_id="pr-recovery-audit-crash",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_command_failed",
    )
    recovery_service.state.fault_hook = exit_after_transaction_replace
    try:
        recovery_service.recover_operation(
            operation_id="pr-recovery-audit-crash",
            reason="prove recovery authority is journal-bound",
        )
    except SimulatedProcessExit:
        pass
    else:
        raise AssertionError("simulated recovery-authorization audit loss did not occur")
    recovery_journal = recovery_fixture.state_dir / "transaction-audit-journal.json"
    assert recovery_journal.is_file()
    _denial(
        lambda: recovery_service.state.load_transaction("pr-recovery-audit-crash"),
        "transaction_journal_pending",
    )
    recovery_boundary.fail_step = None
    recovery_resumed = recovery_fixture.new_service(command_boundary=recovery_boundary).resume_operation(
        "pr-recovery-audit-crash"
    )
    recovery_audit = [
        json.loads(line)
        for line in (recovery_fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii").splitlines()
    ]
    recoveries = [item for item in recovery_audit if item.get("recovered_operation_id") == "pr-recovery-audit-crash"]
    assert recovery_resumed.code == "project_to_develop_completed" and len(recoveries) == 1
    assert not recovery_journal.exists()

    with recovery_fixture.service.state.lock():
        non_monotonic = _denial(
            lambda: recovery_fixture.service.state.append_audit(
                {"event_type": "out_of_order", "occurred_at": "2000-01-01T00:00:00Z"}
            ),
            "audit_timestamp_non_monotonic",
        )
    return (
        f"pending={pending.code}; resumed={resumed.code}; audit_count=1; "
        f"recovery={recovery_resumed.code}; recovery_audit_count=1; monotonic={non_monotonic.code}"
    )


def _assert_a21(root: Path) -> str:
    fixture = Fixture(root)
    _reach_project_promotion_ready(fixture)
    boundary = OfflineGitHubBoundary()
    boundary.fail_step = "pr_create"
    service = fixture.new_service(command_boundary=boundary)
    evidence = fixture.branch_promotion_evidence(
        promotion_kind="project_to_develop",
        source_branch=PROJECT_BRANCH,
        target_branch="develop",
        receipt_ids=("verification",),
    )
    _denial(
        lambda: service.promote_project_to_develop(
            project_id="PROJECT-MODERNIZATION",
            project_branch=PROJECT_BRANCH,
            evidence=evidence,
            operation_id="pr-repeated-failure",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "pull_request_command_failed",
    )
    first = service.recover_operation(operation_id="pr-repeated-failure", reason="retry first PR failure")
    _denial(lambda: service.resume_operation("pr-repeated-failure"), "pull_request_command_failed")
    _denial(lambda: service.resume_operation("pr-repeated-failure"), "explicit_recovery_required")
    second = service.recover_operation(operation_id="pr-repeated-failure", reason="retry second PR failure")
    boundary.fail_step = None
    resumed = service.resume_operation("pr-repeated-failure")
    audit = [
        json.loads(line)
        for line in (fixture.state_dir / "branch-binding-audit.jsonl").read_text(encoding="ascii").splitlines()
    ]
    recoveries = [item for item in audit if item.get("event_type") == "hosted_promotion_recovery_authorized"]
    assert first["status"] == second["status"] == "PASS"
    assert resumed.code == "project_to_develop_completed" and len(recoveries) == 2
    return f"recoveries={len(recoveries)}; resumed={resumed.commit_sha}; each_failure_requires_recovery=true"


def _assert_a22(root: Path) -> str:
    state_dir = root / ".gtkb-state" / "git-lifecycle"
    state_dir.mkdir(parents=True)
    lock_path = state_dir / "git-lifecycle.lock"
    crash = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import os,sys; from pathlib import Path; "
                "sys.path.insert(0,sys.argv[1]); "
                "from groundtruth_kb.git_lifecycle.state import LifecycleState; "
                "state=LifecycleState(Path(sys.argv[2])); "
                "context=state.lock(); context.__enter__(); os._exit(73)"
            ),
            str(PACKAGE_SRC),
            str(state_dir),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert crash.returncode == 73, crash.stdout + crash.stderr
    abandoned = json.loads(lock_path.read_text(encoding="ascii"))
    assert abandoned["pid"] != os.getpid() and abandoned["owner_token"]

    start = Barrier(2)
    denial_observed = Event()

    def contend(name: str) -> str:
        state = LifecycleState(state_dir)
        start.wait(timeout=5)
        try:
            with state.lock():
                if not denial_observed.wait(timeout=5):
                    raise AssertionError("the losing contender did not fail closed while the winner held the lock")
                assert lock_path.exists() and lock_path.stat().st_size > 0
                return f"acquired:{name}"
        except OperationDenied as exc:
            assert exc.code == "lifecycle_lock_held"
            denial_observed.set()
            return f"denied:{name}:{exc.code}"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = sorted(executor.map(contend, ("one", "two")))

    assert sum(item.startswith("acquired:") for item in outcomes) == 1
    assert sum(item.endswith(":lifecycle_lock_held") for item in outcomes) == 1
    assert lock_path.exists() and lock_path.read_bytes() == b""
    recovery_path = state_dir / "git-lifecycle-lock-recovery.jsonl"
    recoveries = [json.loads(line) for line in recovery_path.read_text(encoding="ascii").splitlines()]
    assert len(recoveries) == 1
    assert recoveries[0]["stale_owner_token"] == abandoned["owner_token"]
    assert recoveries[0]["stale_pid"] == abandoned["pid"]
    return f"outcomes={outcomes}; crash_exit=73; recovery_count=1; stable_rendezvous=true"


def _assert_a23(root: Path) -> str:
    missing = Fixture(root / "missing-start")
    missing.bind()
    _write(missing.root, "app.py", "VALUE = 'unauthorized'\n")
    before = _git(missing.root, "rev-parse", "HEAD").stdout.strip()
    (missing.root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{BRIDGE_ID}.json").unlink()
    missing_denial = _denial(lambda: missing.preserve(), "implementation_start_missing")
    assert _git(missing.root, "rev-parse", "HEAD").stdout.strip() == before

    expired = Fixture(root / "expired-claim")
    expired.bind()
    _write(expired.root, "app.py", "VALUE = 'expired'\n")
    connection = sqlite3.connect(expired.root / "groundtruth.db")
    connection.execute(
        "UPDATE work_intent_claims SET ttl_expires_at = ?, implementation_grace_expires_at = ?",
        ("2000-01-01T00:00:00Z", "2000-01-01T00:00:00Z"),
    )
    connection.commit()
    connection.close()
    expired_denial = _denial(lambda: expired.preserve(), "work_intent_claim_expired")

    expired_start = Fixture(root / "expired-start")
    expired_start.bind()
    _write(expired_start.root, "app.py", "VALUE = 'expired start'\n")
    packet_path = (
        expired_start.root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{BRIDGE_ID}.json"
    )
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["expires_at"] = "2000-01-01T00:00:00Z"
    packet["packet_hash"] = expired_start._packet_hash(packet)
    packet_path.write_text(json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")
    expired_start_denial = _denial(lambda: expired_start.preserve(), "implementation_start_expired")

    raced = Fixture(root / "claim-race")
    raced.bind()
    _write(raced.root, "app.py", "VALUE = 'claim changed during drain'\n")
    raced_before = _git(raced.root, "rev-parse", "HEAD").stdout.strip()
    changed = False

    def replace_claim_during_drain() -> int:
        nonlocal changed
        if not changed:
            changed = True
            connection = sqlite3.connect(raced.root / "groundtruth.db")
            connection.execute("UPDATE work_intent_claims SET session_id = ?", ("other-pb-session",))
            connection.commit()
            connection.close()
        return 0

    race_service = raced.new_service(worker_probe=replace_claim_during_drain)
    race_denial = _denial(
        lambda: race_service.preserve_scoped_changes(
            work_item_id=WORK_ITEM,
            message="feat: authority race must fail",
            operation_id="commit-authority-race",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "work_intent_claim_invalid",
    )
    assert _git(raced.root, "rev-parse", "HEAD").stdout.strip() == raced_before

    superseded_no_go = Fixture(root / "superseded-no-go")
    superseded_no_go.bind()
    _write(superseded_no_go.root, "app.py", "VALUE = 'superseded by no-go'\n")
    no_go_before = _git(superseded_no_go.root, "rev-parse", "HEAD").stdout.strip()
    superseded_no_go._write_verdict(status="NO-GO", fields={"Reason": "authority revoked before effect"})
    no_go_denial = _denial(
        lambda: superseded_no_go.preserve(operation_id="commit-after-no-go"),
        "implementation_start_superseded",
    )
    assert _git(superseded_no_go.root, "rev-parse", "HEAD").stdout.strip() == no_go_before

    superseded_revised = Fixture(root / "superseded-revised")
    superseded_revised.bind()
    _write(superseded_revised.root, "app.py", "VALUE = 'superseded by revision'\n")
    revised_before = _git(superseded_revised.root, "rev-parse", "HEAD").stdout.strip()
    superseded_revised._write_verdict(
        status="REVISED",
        fields={"Reason": "proposal changed after the bound GO"},
    )
    revised_denial = _denial(
        lambda: superseded_revised.preserve(operation_id="commit-after-revised"),
        "implementation_start_superseded",
    )
    assert _git(superseded_revised.root, "rev-parse", "HEAD").stdout.strip() == revised_before

    canonical_cli = Fixture(root / "canonical-cli")
    canonical_cli.bind()
    _write(canonical_cli.root, "app.py", "VALUE = 'must use real dispatcher state'\n")
    real_runs = canonical_cli.dispatcher_dir / "dispatch-runs"
    real_runs.mkdir(parents=True)
    (real_runs / "broken.pid").write_text("not-a-pid\n", encoding="ascii")
    false_repo = root / "false-repository"
    false_state = root / "false-lifecycle-state"
    false_dispatcher = root / "false-dispatcher-state"
    override_attempts = (
        ("--repo", str(false_repo)),
        ("--state-dir", str(false_state)),
        ("--dispatcher-state-dir", str(false_dispatcher)),
    )
    for override in override_attempts:
        result = _cli_process(
            canonical_cli.root,
            *override,
            "--json",
            "preserve",
            "--work-item-id",
            WORK_ITEM,
            "--message",
            "feat: false state must not bypass quiescence",
        )
        assert result.returncode == 2 and "error:" in result.stderr
    canonical_result = _cli_process(
        canonical_cli.root,
        "--json",
        "preserve",
        "--work-item-id",
        WORK_ITEM,
        "--message",
        "feat: canonical state remains fail closed",
    )
    assert canonical_result.returncode == 2
    assert json.loads(canonical_result.stderr)["code"] == "dispatcher_worker_state_malformed"
    assert not false_repo.exists() and not false_state.exists() and not false_dispatcher.exists()

    malformed_dir = root / "malformed-dispatch-read"
    malformed_dir.mkdir(parents=True)
    (malformed_dir / "dispatch-drain.json").write_text("{not-json", encoding="ascii")
    assert is_drain_marker_active(malformed_dir) is True
    return (
        f"missing={missing_denial.code}; expired_claim={expired_denial.code}; "
        f"expired_start={expired_start_denial.code}; race={race_denial.code}; "
        f"no_go={no_go_denial.code}; revised={revised_denial.code}; "
        "cli_overrides=rejected; canonical_dispatcher=fail_closed; "
        "unreadable_dispatch_marker=active; heads_unchanged=true"
    )


def _assert_a24(root: Path) -> str:
    preserve_fixture = Fixture(root / "preserve")
    preserve_fixture.bind()
    _write(preserve_fixture.root, "app.py", "VALUE = 'post-effect worker'\n")
    calls = 0

    def worker_appears_after_effect() -> int:
        nonlocal calls
        calls += 1
        return 1 if calls >= 4 else 0

    preserve_service = preserve_fixture.new_service(worker_probe=worker_appears_after_effect)
    preserve_denial = _denial(
        lambda: preserve_service.preserve_scoped_changes(
            work_item_id=WORK_ITEM,
            message="feat: post-effect revalidation",
            operation_id="commit-post-effect-worker",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "quiescence_lease_lost",
    )
    committed = _git(preserve_fixture.root, "rev-parse", "HEAD").stdout.strip()
    preserve_fixture.new_service(worker_probe=lambda: 0).recover_operation(
        operation_id="commit-post-effect-worker",
        reason="post-commit inflight worker cleared",
    )
    preserve_recovery_probes = 0

    def prove_fresh_preserve_quiescence() -> int:
        nonlocal preserve_recovery_probes
        preserve_recovery_probes += 1
        return 0

    recovered = preserve_fixture.new_service(worker_probe=prove_fresh_preserve_quiescence).resume_operation(
        "commit-post-effect-worker"
    )
    assert recovered.commit_sha == committed and recovered.code == "preserve_recovered"
    assert preserve_recovery_probes >= 3

    promote_fixture = Fixture(root / "promote")
    source = promote_fixture.reach_preserved()
    _git(promote_fixture.root, "checkout", PROJECT_BRANCH)
    evidence = promote_fixture.passing_evidence(source)
    merge_calls = 0

    def worker_appears_after_merge() -> int:
        nonlocal merge_calls
        merge_calls += 1
        return 1 if merge_calls >= 4 else 0

    promote_service = promote_fixture.new_service(worker_probe=worker_appears_after_merge)
    promote_denial = _denial(
        lambda: promote_service.promote_work_item(
            work_item_id=WORK_ITEM,
            evidence=evidence,
            operation_id="promote-post-effect-worker",
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "quiescence_lease_lost",
    )
    merged = _git(promote_fixture.root, "rev-parse", "HEAD").stdout.strip()
    promote_fixture.new_service(worker_probe=lambda: 0).recover_operation(
        operation_id="promote-post-effect-worker",
        reason="post-merge inflight worker cleared",
    )
    promote_recovery_probes = 0

    def prove_fresh_promote_quiescence() -> int:
        nonlocal promote_recovery_probes
        promote_recovery_probes += 1
        return 0

    promotion_recovered = promote_fixture.new_service(worker_probe=prove_fresh_promote_quiescence).resume_operation(
        "promote-post-effect-worker"
    )
    assert promotion_recovered.commit_sha == merged and promotion_recovered.code == "promote_recovered"
    assert promote_recovery_probes >= 3
    return (
        f"preserve={preserve_denial.code}/{recovered.code}; "
        f"promote={promote_denial.code}/{promotion_recovered.code}; post_effect_worker_denied=true; "
        f"fresh_recovery_probes={preserve_recovery_probes}/{promote_recovery_probes}"
    )


def _assert_a25(root: Path) -> str:
    claim_fixture = Fixture(root / "claim-revoked")
    claim_fixture.bind()
    _write(claim_fixture.root, "app.py", "VALUE = 'authority changes after commit'\n")
    original_commit = claim_fixture.service.repo.scoped_commit

    def commit_then_revoke(scope: tuple[str, ...], message: str) -> str:
        commit_sha = original_commit(scope, message)
        connection = sqlite3.connect(claim_fixture.root / "groundtruth.db")
        connection.execute(
            "UPDATE work_intent_claims SET session_id = ? WHERE thread_slug = ?",
            ("revoked-after-effect", BRIDGE_ID),
        )
        connection.commit()
        connection.close()
        return commit_sha

    claim_fixture.service.repo.scoped_commit = commit_then_revoke  # type: ignore[method-assign]
    operation_id = "commit-authority-revoked-after-effect"
    claim_denial = _denial(
        lambda: claim_fixture.preserve(operation_id=operation_id),
        "work_intent_claim_invalid",
    )
    transaction = claim_fixture.service.state.load_transaction(operation_id)
    binding = claim_fixture.service.show_binding(WORK_ITEM)
    assert transaction["phase"] == "guard_lost_after_commit"
    assert binding["lifecycle_state"] == "active" and binding["preserved_commit"] is None
    connection = sqlite3.connect(claim_fixture.root / "groundtruth.db")
    connection.execute(
        "UPDATE work_intent_claims SET session_id = ? WHERE thread_slug = ?",
        (AUTHOR_SESSION, BRIDGE_ID),
    )
    connection.commit()
    connection.close()
    claim_fixture.service.recover_operation(
        operation_id=operation_id,
        reason="canonical authority restored after post-effect denial",
    )
    resumed = claim_fixture.service.resume_operation(operation_id)
    assert resumed.code == "preserve_recovered"

    no_go_fixture = Fixture(root / "no-go-after-commit")
    no_go_fixture.bind()
    _write(no_go_fixture.root, "app.py", "VALUE = 'no-go after commit'\n")
    no_go_commit = no_go_fixture.service.repo.scoped_commit

    def commit_then_no_go(scope: tuple[str, ...], message: str) -> str:
        commit_sha = no_go_commit(scope, message)
        no_go_fixture._write_verdict(status="NO-GO", fields={"Reason": "revoked after Git effect"})
        return commit_sha

    no_go_fixture.service.repo.scoped_commit = commit_then_no_go  # type: ignore[method-assign]
    no_go_operation = "commit-no-go-after-effect"
    no_go_denial = _denial(
        lambda: no_go_fixture.preserve(operation_id=no_go_operation),
        "implementation_start_superseded",
    )
    no_go_transaction = no_go_fixture.service.state.load_transaction(no_go_operation)
    no_go_binding = no_go_fixture.service.show_binding(WORK_ITEM)
    assert no_go_transaction["phase"] == "guard_lost_after_commit"
    assert no_go_binding["lifecycle_state"] == "active" and no_go_binding["preserved_commit"] is None

    revised_fixture = Fixture(root / "revised-after-merge")
    source_commit = revised_fixture.reach_preserved()
    _git(revised_fixture.root, "checkout", PROJECT_BRANCH)
    evidence = revised_fixture.passing_evidence(source_commit)
    original_merge = revised_fixture.service.repo.merge_no_ff

    def merge_then_revise(source_branch: str, message: str) -> str:
        commit_sha = original_merge(source_branch, message)
        revised_fixture._write_verdict(
            status="REVISED",
            fields={"Reason": "proposal changed after merge effect"},
        )
        return commit_sha

    revised_fixture.service.repo.merge_no_ff = merge_then_revise  # type: ignore[method-assign]
    revised_operation = "promote-revised-after-effect"
    revised_denial = _denial(
        lambda: revised_fixture.service.promote_work_item(
            work_item_id=WORK_ITEM,
            evidence=evidence,
            operation_id=revised_operation,
            ttl_seconds=20,
            wait_seconds=1,
        ),
        "implementation_start_superseded",
    )
    revised_transaction = revised_fixture.service.state.load_transaction(revised_operation)
    revised_binding = revised_fixture.service.show_binding(WORK_ITEM)
    assert revised_transaction["phase"] == "guard_lost_after_commit"
    assert revised_binding["lifecycle_state"] == "preserved" and revised_binding["promoted_commit"] is None

    return (
        f"claim={claim_denial.code}/{resumed.code}; no_go={no_go_denial.code}; "
        f"revised={revised_denial.code}; phase=guard_lost_after_commit; "
        "state_advancement_blocked=true"
    )


def _assert_a26(root: Path) -> str:
    fixture = Fixture(root)
    source = fixture.reach_preserved()
    _git(root, "checkout", PROJECT_BRANCH)
    evidence = fixture.passing_evidence(source)
    session_path = root / "harness-state" / "claude" / "session-envelopes" / f"{VERIFIER_SESSION}.json"
    document = json.loads(session_path.read_text(encoding="utf-8"))
    document["worker_role_provenance"]["role"] = "prime-builder"
    session_path.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    denial = _denial(
        lambda: fixture.service.promote_work_item(work_item_id=WORK_ITEM, evidence=evidence),
        "verification_role_invalid",
    )
    assert fixture.service.show_binding(WORK_ITEM)["lifecycle_state"] == "preserved"
    return f"denial={denial.code}; canonical_session_tamper_blocked=true"


ASSERTIONS: tuple[tuple[str, str, Callable[[Path], str]], ...] = (
    ("GIT-LIFECYCLE-A1", "deterministic branch/work-item binding and ancestry", _assert_a1),
    ("GIT-LIFECYCLE-A2", "wrong-branch mutation denial with no Git or dispatcher effect", _assert_a2),
    ("GIT-LIFECYCLE-A3", "immutable binding conflict denial", _assert_a3),
    ("GIT-LIFECYCLE-A4", "exact scoped commit preserves unrelated work", _assert_a4),
    ("GIT-LIFECYCLE-A5", "empty attributable scope denies before quiescence", _assert_a5),
    ("GIT-LIFECYCLE-A6", "malformed dispatcher state fails closed", _assert_a6),
    ("GIT-LIFECYCLE-A7", "stale dispatcher lease requires explicit recovery", _assert_a7),
    ("GIT-LIFECYCLE-A8", "bounded quiescence timeout is recoverable", _assert_a8),
    ("GIT-LIFECYCLE-A9", "promotion requires verified evidence", _assert_a9),
    ("GIT-LIFECYCLE-A10", "promotion evidence is current, independent, and complete", _assert_a10),
    ("GIT-LIFECYCLE-A11", "passing gates produce one observable promotion merge", _assert_a11),
    ("GIT-LIFECYCLE-A12", "interrupted scoped commit resumes without duplicate Git effect", _assert_a12),
    ("GIT-LIFECYCLE-A13", "interrupted promotion and observable audit recover deterministically", _assert_a13),
    ("GIT-LIFECYCLE-A14", "production CLI executes the complete local work-item lifecycle", _assert_a14),
    ("GIT-LIFECYCLE-A15", "offline project/develop/stage pull-request pilot completes", _assert_a15),
    ("GIT-LIFECYCLE-A16", "direct push, stale evidence, wrong ancestry, and PR failure deny", _assert_a16),
    ("GIT-LIFECYCLE-A17", "lease loss fails closed and requires explicit recovery", _assert_a17),
    ("GIT-LIFECYCLE-A18", "PR-create interruption resumes without duplicate pull request", _assert_a18),
    ("GIT-LIFECYCLE-A19", "hosted evidence is revalidated immediately before merge", _assert_a19),
    ("GIT-LIFECYCLE-A20", "post-audit interruption reuses deterministic completion evidence", _assert_a20),
    ("GIT-LIFECYCLE-A21", "each repeated hosted failure requires a fresh recovery record", _assert_a21),
    ("GIT-LIFECYCLE-A22", "two stale-lock reclaimers cannot delete a fresh lock", _assert_a22),
    (
        "GIT-LIFECYCLE-A23",
        "canonical PAUTH, claim, start, dispatcher paths, and current bridge authority fail closed",
        _assert_a23,
    ),
    ("GIT-LIFECYCLE-A24", "preserve and promote revalidate zero inflight after each Git effect", _assert_a24),
    (
        "GIT-LIFECYCLE-A25",
        "post-effect claim or bridge supersession blocks state advancement and requires recovery",
        _assert_a25,
    ),
    ("GIT-LIFECYCLE-A26", "canonical verifier-session tampering blocks promotion", _assert_a26),
)


def run_acceptance() -> dict[str, Any]:
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="gtkb-modernization-git-") as temporary:
        base = Path(temporary)
        for assertion_id, description, assertion in ASSERTIONS:
            try:
                evidence = assertion(base / assertion_id.lower())
            except Exception as exc:  # noqa: BLE001 - report all acceptance failures in one deterministic result
                results.append(
                    {
                        "id": assertion_id,
                        "description": description,
                        "status": "FAIL",
                        "evidence": f"{type(exc).__name__}: {exc}",
                    }
                )
            else:
                results.append(
                    {
                        "id": assertion_id,
                        "description": description,
                        "status": "PASS",
                        "evidence": evidence,
                    }
                )
    return {
        "schema_version": 1,
        "capability": "CAP-GIT-LIFECYCLE",
        "status": "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL",
        "assertions": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the machine-readable acceptance report")
    args = parser.parse_args()
    report = run_acceptance()
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(f"Modernization Git lifecycle: {report['status']}")
        for item in report["assertions"]:
            print(f"- {item['id']}: {item['status']} - {item['evidence']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
