"""Subprocess acceptance for the public modernization production workflow."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from groundtruth_kb.modernization.workflow import ModernizationWorkflowError, _resolve_workflow_actor
from groundtruth_kb.session import envelope as session_envelope

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
PB_SESSION = "019f5ca0-6be7-73a1-b6c4-8fd3af65a101"
LO_SESSION = "019f5ca1-7288-78c2-9a51-2b0d0a6a5102"


def _run(
    workspace: Path,
    command: str,
    *,
    session_id: str,
    extra: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(PACKAGE_SRC), str(REPO_ROOT), env.get("PYTHONPATH", "")]).rstrip(
        os.pathsep
    )
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.modernization",
            command,
            "--workspace",
            str(workspace),
            "--platform-root",
            str(REPO_ROOT),
            "--session-id",
            session_id,
            *extra,
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _prime(workspace: Path, command: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return _run(
        workspace,
        command,
        session_id=PB_SESSION,
        extra=tuple(extra),
    )


def _lo(
    workspace: Path,
    command: str,
    *extra: str,
    session_id: str = LO_SESSION,
) -> subprocess.CompletedProcess[str]:
    return _run(
        workspace,
        command,
        session_id=session_id,
        extra=tuple(extra),
    )


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"workflow emitted non-JSON output: {result.stdout!r}\n{result.stderr}") from exc
    assert isinstance(payload, dict)
    return payload


def _successful_payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    payload = _payload(result)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    return payload


def _git(workspace: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _issue_runtime_sessions(workspace: Path, *, issue_sessions: bool = True) -> None:
    state = workspace / "harness-state"
    state.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "harness-state" / "harness-identities.json", state / "harness-identities.json")
    shutil.copy2(REPO_ROOT / "harness-state" / "harness-registry.json", state / "harness-registry.json")
    if not issue_sessions:
        return
    for harness_name, role, session_id in (
        ("codex", "prime-builder", PB_SESSION),
        ("antigravity", "loyal-opposition", LO_SESSION),
    ):
        session_envelope.open_session(
            workspace,
            harness_name=harness_name,
            role=role,
            session_id=session_id,
            worker_role_source="dispatcher_composition",
            dispatch_run_id=f"acceptance-{session_id}",
        )


def _new_workspace(
    *,
    issue_sessions: bool = True,
) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp_root = REPO_ROOT / ".gtkb-state" / "modernization-e2e-acceptance"
    temp_root.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.TemporaryDirectory(prefix="run-", dir=temp_root)
    workspace = Path(temporary.name) / "modernization-rehearsal"
    _issue_runtime_sessions(workspace, issue_sessions=issue_sessions)
    return temporary, workspace


def _prepare_and_go(workspace: Path) -> tuple[dict[str, object], Path]:
    prepared = _successful_payload(_prime(workspace, "prime-prepare"))
    assert prepared["status"] == "awaiting_go_review"
    request = workspace / str(prepared["proposal_review_request"])
    reviewed = _successful_payload(_lo(workspace, "lo-review", "--request", str(request)))
    assert reviewed["status"] == "go_reviewed"
    return prepared, workspace / str(reviewed["go_review_receipt"])


def _execute_to_verification_request(workspace: Path, go_receipt: Path) -> dict[str, object]:
    result = _successful_payload(_prime(workspace, "rehearse", "--go-receipt", str(go_receipt)))
    assert result["status"] == "awaiting_independent_verification"
    return result


@pytest.mark.timeout(120)
def test_public_workflow_uses_external_reviews_and_resumes_exactly_once() -> None:
    temporary, workspace = _new_workspace()
    with temporary:
        authority_documents = {
            session_id: session_envelope.worker_session_envelope_path(workspace, harness_name, session_id).read_bytes()
            for harness_name, session_id in (("codex", PB_SESSION), ("antigravity", LO_SESSION))
        }
        prepared, go_receipt = _prepare_and_go(workspace)

        interrupted = _prime(
            workspace,
            "rehearse",
            "--go-receipt",
            str(go_receipt),
            "--interrupt-after",
            "authorized-mutation",
        )
        interrupted_payload = _payload(interrupted)
        assert interrupted.returncode == 75, interrupted.stderr
        assert interrupted_payload["status"] == "interrupted"
        assert interrupted_payload["interruption_boundary"] == "authorized-mutation-before-checkpoint"
        assert interrupted_payload["mutation_written"] is True
        denial = interrupted_payload["missing_authority"]
        assert isinstance(denial, dict)
        assert denial["authorization_denied"] is True
        assert denial["start_gate_denied"] is True

        target = workspace / "scripts" / "e2e_sample.py"
        assert target.read_text(encoding="utf-8") == "RESULT = 'verified'\n"
        interrupted_mtime = target.stat().st_mtime_ns

        awaiting = _execute_to_verification_request(workspace, go_receipt)
        assert awaiting["attempt_count"] == 2
        assert awaiting["mutation_effect_count"] == 1
        assert awaiting["mutation_reused_existing"] is True
        assert target.stat().st_mtime_ns == interrupted_mtime
        request = workspace / str(awaiting["verification_review_request"])

        verified = _successful_payload(_lo(workspace, "lo-verify", "--request", str(request)))
        assert verified["status"] == "independently_verified"
        verification_receipt = workspace / str(verified["verification_review_receipt"])

        completed = _successful_payload(
            _prime(
                workspace,
                "rehearse",
                "--go-receipt",
                str(go_receipt),
                "--verification-receipt",
                str(verification_receipt),
            )
        )
        assert completed["status"] == "completed"
        assert completed["author_session"] == PB_SESSION
        assert completed["verifier_session"] == LO_SESSION
        assert completed["author_session"] != completed["verifier_session"]
        assert completed["verdict_path"] == "bridge/modernization-e2e-004.md"
        assert completed["recovery_status"] == "completed"
        assert all(completed["selection"].values())
        assert completed["start_authority"]["project_authorization_id"] == "PAUTH-E2E-001"
        assert completed["candidate_assessment"]["manifest_valid"] is True
        assert completed["candidate_assessment"]["workflow_acceptance_test_id"] == "AT-END-TO-END-WORKFLOW"
        assert completed["candidate_assessment"]["production_deployment_separate"] is True
        assert prepared["session"]["session_id"] == PB_SESSION

        target_commits = _git(workspace, "log", "--format=%H", "--", "scripts/e2e_sample.py").splitlines()
        assert target_commits == [completed["implementation_commit"]]
        assert (
            _git(
                workspace,
                "merge-base",
                "--is-ancestor",
                str(completed["implementation_commit"]),
                str(completed["verification_commit"]),
            )
            == ""
        )
        completed_mtime = target.stat().st_mtime_ns
        completed_event_count = completed["event_count"]

        replayed = _successful_payload(
            _prime(
                workspace,
                "rehearse",
                "--go-receipt",
                str(go_receipt),
                "--verification-receipt",
                str(verification_receipt),
            )
        )
        assert replayed["status"] == "completed_existing"
        assert replayed["replayed_completed_result"] is True
        assert replayed["implementation_commit"] == completed["implementation_commit"]
        assert replayed["event_count"] == completed_event_count
        assert target.stat().st_mtime_ns == completed_mtime
        for harness_name, session_id in (("codex", PB_SESSION), ("antigravity", LO_SESSION)):
            assert (
                session_envelope.worker_session_envelope_path(workspace, harness_name, session_id).read_bytes()
                == authority_documents[session_id]
            )


def test_public_workflow_rejects_missing_runtime_envelope() -> None:
    temporary, workspace = _new_workspace(issue_sessions=False)
    with temporary:
        result = _prime(workspace, "prime-prepare")
        payload = _payload(result)
        assert result.returncode == 1
        assert payload["status"] == "error"
        assert "pre-existing runtime-issued session envelope" in str(payload["error"])
        assert not (workspace / ".git").exists()


def test_public_workflow_rejects_forged_harness_identity() -> None:
    temporary, workspace = _new_workspace()
    with temporary:
        path = session_envelope.worker_session_envelope_path(workspace, "codex", PB_SESSION)
        forged = json.loads(path.read_text(encoding="utf-8"))
        forged["harness_id"] = "C"
        forged["worker_role_provenance"]["harness_id"] = "C"
        path.write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = _prime(workspace, "prime-prepare")
        payload = _payload(result)
        assert result.returncode == 1
        assert payload["status"] == "error"
        assert "workspace harness identity authority" in str(payload["error"])
        assert not (workspace / ".git").exists()


def test_public_workflow_rejects_tampered_session_envelope() -> None:
    temporary, workspace = _new_workspace()
    with temporary:
        path = session_envelope.worker_session_envelope_path(workspace, "codex", PB_SESSION)
        tampered = json.loads(path.read_text(encoding="utf-8"))
        tampered["role"] = "loyal-opposition"
        tampered["role_resolved"] = "loyal-opposition"
        path.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = _prime(workspace, "prime-prepare")
        payload = _payload(result)
        assert result.returncode == 1
        assert payload["status"] == "error"
        assert "conflicts with its authoritative provenance" in str(payload["error"])
        assert not (workspace / ".git").exists()


def test_interactive_transcript_role_overrides_registry_default() -> None:
    temporary, workspace = _new_workspace(issue_sessions=False)
    with temporary:
        session_envelope.open_session(
            workspace,
            harness_name="codex",
            role="loyal-opposition",
            session_id=LO_SESSION,
            worker_role_source="interactive_transcript_explicit",
        )

        actor = _resolve_workflow_actor(
            workspace,
            REPO_ROOT,
            session_id=LO_SESSION,
            required_role="loyal-opposition",
        )

        assert actor.harness_id == "A"
        assert actor.role == "loyal-opposition"
        assert actor.role_resolution_source == "interactive_transcript_explicit"


def test_registry_fallback_role_cannot_override_registry_default() -> None:
    temporary, workspace = _new_workspace(issue_sessions=False)
    with temporary:
        session_envelope.open_session(
            workspace,
            harness_name="codex",
            role="loyal-opposition",
            session_id=LO_SESSION,
            worker_role_source="session_resolver_fallback",
        )

        try:
            _resolve_workflow_actor(
                workspace,
                REPO_ROOT,
                session_id=LO_SESSION,
                required_role="loyal-opposition",
            )
        except ModernizationWorkflowError as exc:
            assert "role is not active" in str(exc)
        else:
            raise AssertionError("registry fallback must not mint a role absent from durable authority")


def test_go_review_rejects_same_session_and_tampered_proposal() -> None:
    temporary, workspace = _new_workspace()
    with temporary:
        prepared = _successful_payload(_prime(workspace, "prime-prepare"))
        request = workspace / str(prepared["proposal_review_request"])

        same_session = _lo(workspace, "lo-review", "--request", str(request), session_id=PB_SESSION)
        same_session_payload = _payload(same_session)
        assert same_session.returncode == 1
        assert same_session_payload["status"] == "error"
        assert "session" in str(same_session_payload["error"]).lower()
        assert not (workspace / "bridge" / "modernization-e2e-002.md").exists()

        proposal = workspace / str(prepared["proposal"]["proposal"])
        original = proposal.read_bytes()
        proposal.write_bytes(original + b"\nUNREVIEWED CHANGE\n")
        tampered = _lo(workspace, "lo-review", "--request", str(request))
        tampered_payload = _payload(tampered)
        assert tampered.returncode == 1
        assert tampered_payload["status"] == "error"
        assert "exact proposal bytes" in str(tampered_payload["error"])
        assert not (workspace / "bridge" / "modernization-e2e-002.md").exists()


def test_finalization_rejects_tampered_report_and_verification_receipt() -> None:
    temporary, workspace = _new_workspace()
    with temporary:
        _, go_receipt = _prepare_and_go(workspace)
        original_go_receipt = go_receipt.read_bytes()
        go_payload = json.loads(original_go_receipt)
        go_payload["proposal_sha256"] = "0" * 64
        go_receipt.write_text(json.dumps(go_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rejected_go = _prime(workspace, "rehearse", "--go-receipt", str(go_receipt))
        rejected_go_payload = _payload(rejected_go)
        assert rejected_go.returncode == 1
        assert "receipt digest" in str(rejected_go_payload["error"])
        assert not (workspace / "scripts" / "e2e_sample.py").exists()
        go_receipt.write_bytes(original_go_receipt)

        awaiting = _execute_to_verification_request(workspace, go_receipt)
        request = workspace / str(awaiting["verification_review_request"])
        request_payload = json.loads(request.read_text(encoding="utf-8"))
        report = workspace / str(request_payload["report_path"])
        original_report = report.read_bytes()
        report.write_bytes(original_report + b"\nUNREVIEWED CHANGE\n")

        rejected_report = _lo(workspace, "lo-verify", "--request", str(request))
        rejected_report_payload = _payload(rejected_report)
        assert rejected_report.returncode == 1
        assert "implementation report digest" in str(rejected_report_payload["error"])
        assert not (workspace / "bridge" / "modernization-e2e-004.md").exists()
        report.write_bytes(original_report)

        verified = _successful_payload(_lo(workspace, "lo-verify", "--request", str(request)))
        verification_receipt = workspace / str(verified["verification_review_receipt"])
        original_receipt = verification_receipt.read_bytes()
        receipt_payload = json.loads(original_receipt)
        receipt_payload["implementation_commit"] = "0" * 40
        verification_receipt.write_text(json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        rejected_receipt = _prime(
            workspace,
            "rehearse",
            "--go-receipt",
            str(go_receipt),
            "--verification-receipt",
            str(verification_receipt),
        )
        rejected_receipt_payload = _payload(rejected_receipt)
        assert rejected_receipt.returncode == 1
        assert "receipt digest" in str(rejected_receipt_payload["error"])
        assert not (workspace / ".gtkb-state" / "modernization-workflow" / "result.json").exists()

        verification_receipt.write_bytes(original_receipt)
        completed = _successful_payload(
            _prime(
                workspace,
                "rehearse",
                "--go-receipt",
                str(go_receipt),
                "--verification-receipt",
                str(verification_receipt),
            )
        )
        assert completed["status"] == "completed"
