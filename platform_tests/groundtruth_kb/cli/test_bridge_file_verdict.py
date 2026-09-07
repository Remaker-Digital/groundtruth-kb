# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for the deterministic verdict/advisory filing service (WI-5690)."""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge.verdict_filing import (
    ADVISORY_STATUSES,
    REFUSED_STATUSES,
    VERDICT_STATUSES,
    VerdictFilingError,
)

# TEST-11709 (deterministic verdict/advisory publication) and the adjacent
# bridge CLI/claim/taxonomy/preflight suites.
#
# The fixture directory is hermetic: the service imports the governed writer and
# claim registry by path, but for unit-level routing/fail-closed behavior we
# monkeypatch the writer façade to avoid touching the live MemBase and bridge
# chain. The adversarial consumer-facing contract (refusal and in-root
# enforcement) is exercised with the real service.

_GO_CONTENT_TEMPLATE = """GO
::init gtkb lo
::open test

bridge_kind: lo_verdict
Document: {document}
Version: {version:03d}
Responds to: bridge/{document}-001.md

# Verdict

GO
"""


class _FakePublished:
    def __init__(
        self,
        *,
        document_name: str,
        verdict: str,
        verdict_path: str,
        commit_sha: str | None,
        claim_released: bool,
    ) -> None:
        self.document_name = document_name
        self.verdict = verdict
        self.verdict_path = verdict_path
        self.commit_sha = commit_sha
        self.claim_released = claim_released


class _FakeWriter:
    PRIME_STATUSES = frozenset({"NEW", "REVISED", "NO-ACTION"})
    LO_ENVELOPE_BRIDGE_KINDS = frozenset({"lo_verdict", "loyal_opposition_review", "verification_verdict"})
    PROVIDER_VERDICT_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})

    def __init__(self, root: Path) -> None:
        self.root = root
        self.published: list[tuple[str, str]] = []

    def _thread_state(self, project_root: Path, document: str):
        bridge = project_root / "bridge"
        files = sorted(bridge.glob(f"{document}-*.md"))
        if not files:
            return None, 1, None, ""
        latest = files[-1]
        content = latest.read_text(encoding="utf-8")
        status = content.splitlines()[0].strip().upper()
        version = int(latest.name.rsplit("-", 1)[1].split(".")[0])
        return latest, version + 1, status, content

    def _bridge_kind(self, content: str) -> str:
        for line in content.splitlines():
            if line.strip().startswith("bridge_kind:"):
                return line.split(":", 1)[1].strip().strip("`")
        return ""

    def prepare_verdict_candidate(self, *, candidate_path, content, project_root) -> str:
        return content

    def publish_lo_verdict(self, document, verdict, content, root, **kwargs):
        self.published.append((document, verdict))
        return _FakePublished(
            document_name=document,
            verdict=verdict,
            verdict_path=f"bridge/{document}-002.md",
            commit_sha=None,
            claim_released=True,
        )

    def write_bridge_file(self, document, version, content, root, **kwargs):
        bridge = root / "bridge"
        bridge.mkdir(parents=True, exist_ok=True)
        target = bridge / f"{document}-{version:03d}.md"
        target.write_text(content, encoding="utf-8")
        return target


class _FakeClaimRegistry:
    def __init__(self) -> None:
        self.holders: dict[str, str] = {}

    def current_holder(self, slug, *, project_root=None):
        if slug not in self.holders:
            return None
        return {"session_id": self.holders[slug]}

    def acquire(self, slug, session_id, *, ttl_seconds=3600, project_root=None, claim_kind=None):
        current = self.holders.get(slug)
        if current is not None and current != session_id:
            return False
        self.holders[slug] = session_id
        return True


def _service_module(monkeypatch: pytest.MonkeyPatch, root: Path):
    import importlib

    module = importlib.import_module("groundtruth_kb.bridge.verdict_filing")
    fake_writer = _FakeWriter(root)
    fake_claims = _FakeClaimRegistry()
    monkeypatch.setattr(module, "_load_writer", lambda project_root: fake_writer)
    monkeypatch.setattr(module, "_load_claim_registry", lambda project_root: fake_claims)
    monkeypatch.setattr(
        module,
        "_candidate_evidence_hash",
        lambda *args, **kwargs: "sha256:fixture",
    )
    monkeypatch.setattr(
        module,
        "_metadata_from_envelope",
        lambda *args, **kwargs: {
            "author_identity": "loyal-opposition/goose/G",
            "author_harness_id": "G",
            "author_session_context_id": "fixture-session",
            "author_model": "fixture",
            "author_model_version": "fixture",
            "author_model_configuration": "fixture",
        },
    )
    return module, fake_writer, fake_claims


def _seed_thread(root: Path, document: str, status: str = "NEW") -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / f"{document}-001.md").write_text(
        f"{status}\n\nbridge_kind: prime_proposal\nDocument: {document}\nVersion: 001\n",
        encoding="utf-8",
    )


def test_rejects_verified_with_finalization_guidance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="example",
            status="VERIFIED",
            content="VERIFIED\n\nbridge_kind: lo_verdict\n",
        )
    assert "finalize-verified" in str(exc_info.value)


def test_rejects_no_action_with_prime_path_guidance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="example",
            status="NO-ACTION",
            content="NO-ACTION\n\nbridge_kind: implementation_report\n",
        )
    assert "file-no-action" in str(exc_info.value)


def test_go_publishes_through_writer_with_response_and_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_writer, fake_claims = _service_module(monkeypatch, tmp_path)
    _seed_thread(tmp_path, "example")
    fake_claims.holders["example"] = "fixture-session"
    content = _GO_CONTENT_TEMPLATE.format(document="example", version=2)
    result = module.publish_verdict(
        tmp_path,
        document="example",
        status="GO",
        content=content,
        session_id="fixture-session",
    )
    assert result.status == "GO"
    assert result.version == 2
    assert result.path == "bridge/example-002.md"
    assert result.responded_to == "bridge/example-001.md"
    assert result.capability_consumed is True
    assert result.claim_released is True
    assert fake_writer.published == [("example", "GO")]


def test_advisory_publishes_with_governance_advisory_kind(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_writer, fake_claims = _service_module(monkeypatch, tmp_path)
    _seed_thread(tmp_path, "advexample", status="NEW")
    content = (
        "ADVISORY\n::init gtkb lo\n::open deliberation\n\n"
        "bridge_kind: governance_advisory\n"
        "Document: advexample\n"
        "Responds to: bridge/advexample-001.md\n"
    )
    result = module.publish_verdict(
        tmp_path,
        document="advexample",
        status="ADVISORY",
        content=content,
        session_id="fixture-session",
    )
    assert result.status == "ADVISORY"
    assert result.version == 2
    result_path = tmp_path / "bridge" / "advexample-002.md"
    assert result_path.is_file()
    text = result_path.read_text(encoding="utf-8")
    assert "bridge_kind: governance_advisory" in text


def test_invalid_status_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="example",
            status="BOGUS",
            content="BOGUS\n",
        )
    assert "verdict status must be one of" in str(exc_info.value)


def test_version_mismatch_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    _seed_thread(tmp_path, "example")
    content = _GO_CONTENT_TEMPLATE.format(document="example", version=5)  # wrong next version
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="example",
            status="GO",
            content=content,
            session_id="fixture-session",
        )
    assert "Version must be" in str(exc_info.value)


def test_missing_responds_to_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    _seed_thread(tmp_path, "example")
    content = _GO_CONTENT_TEMPLATE.format(document="example", version=2).replace(
        "Responds to: bridge/example-001.md", "Responds to: bridge/other-001.md"
    )
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="example",
            status="GO",
            content=content,
            session_id="fixture-session",
        )
    assert "respond to current latest entry" in str(exc_info.value)


def test_advisory_requires_lo_provenance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module, _, _ = _service_module(monkeypatch, tmp_path)
    _seed_thread(tmp_path, "advexample")
    content = (
        "ADVISORY\n::init gtkb pb\n\n"
        "bridge_kind: governance_advisory\n"
        "Document: advexample\n"
        "Responds to: bridge/advexample-001.md\n"
    )
    with pytest.raises(VerdictFilingError) as exc_info:
        module.publish_verdict(
            tmp_path,
            document="advexample",
            status="ADVISORY",
            content=content,
            session_id="fixture-session",
        )
    assert "loyal-opposition" in str(exc_info.value)


def test_status_routing_constants() -> None:
    assert "GO" in VERDICT_STATUSES
    assert "NO-GO" in VERDICT_STATUSES
    assert "ADVISORY" in ADVISORY_STATUSES
    assert {"VERIFIED", "NO-ACTION"} <= REFUSED_STATUSES
