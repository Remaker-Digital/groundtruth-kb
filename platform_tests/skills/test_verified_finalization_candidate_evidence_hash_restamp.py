"""WI-5826: the VERIFIED finalizer re-stamps ``candidate_evidence_hash`` over final bytes.

The field is self-referential: the bridge-compliance gate recomputes it over the
fully normalized candidate bytes it is about to audit. ``finalize_verified_commit``
mutates the body after the reviewer stamps the field (Prior-Deliberations seeding
and the Commit Finalization Evidence append), and the writer normalizes it twice
more immediately before the audit. These tests lock in TEST-11782's expected
outcome: after finalization, recomputing the hash over the final on-disk verdict
bytes equals the stamped value.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

CLAUDE_HELPER = REPO_ROOT / ".claude" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py"
CODEX_HELPER = REPO_ROOT / ".codex" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py"
LIVE_GATE = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"

SLUG = "restamp-fixture"
_THIS_TEST = "platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py"


def _load_module(name: str, path: Path) -> ModuleType:
    src_root = str(REPO_ROOT / "groundtruth-kb" / "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def helper() -> ModuleType:
    return _load_module("write_verdict_restamp", CLAUDE_HELPER)


@pytest.fixture(scope="module")
def gate() -> ModuleType:
    return _load_module("bridge_gate_restamp", LIVE_GATE)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _implementation_report_body() -> str:
    return """NEW
author_identity: prime-builder/test
author_harness_id: P
author_session_context_id: 11111111-1111-4111-8111-111111111111
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: implementation_report
Document: restamp-fixture
Version: 003

# Implementation report
"""


def _init_repo(tmp_path: Path) -> Path:
    """A fixture repo whose bridge chain can carry a green VERIFIED finalization."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.autocrlf", "false")
    _write(repo / "groundtruth.toml", "# test project root marker\n")
    _write(repo / "config" / "governance" / "spec-applicability.toml", "rules = []\n")
    _write(
        repo / "bridge" / f"{SLUG}-001.md",
        "NEW\n::init gtkb pb\n::open build\n\nbridge_kind: prime_proposal\n"
        f"Document: {SLUG}\nVersion: 001\n"
        'target_paths: ["scripts/feature.py"]\n',
    )
    _write(repo / "bridge" / f"{SLUG}-002.md", f"GO\n\nDocument: {SLUG}\nVersion: 002\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    _git(
        repo,
        "add",
        "--",
        "groundtruth.toml",
        "config/governance/spec-applicability.toml",
        f"bridge/{SLUG}-001.md",
        f"bridge/{SLUG}-002.md",
        "scripts/feature.py",
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(repo / "bridge" / f"{SLUG}-003.md", _implementation_report_body())
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


def _packet_hash(repo: Path) -> str:
    """Rebuild the packet exactly as the gate subprocess rebuilds it."""
    from scripts import bridge_applicability_preflight as preflight

    packet = preflight.build_packet(
        bridge_id=SLUG,
        bridge_dir=repo / "bridge",
        config_path=repo / "config" / "governance" / "spec-applicability.toml",
        db_path=repo / "groundtruth.db",
        content_file=repo / "bridge" / f"{SLUG}-003.md",
    )
    return str(packet["packet_hash"])


def _verdict_body(
    repo: Path,
    *,
    hash_value: str,
    hash_field_count: int = 1,
    include_preflight_section: bool = True,
    extra_sections: str = "",
) -> str:
    hash_lines = "".join(f"- candidate_evidence_hash: `{hash_value}`\n" for _ in range(hash_field_count))
    preflight_section = ""
    if include_preflight_section:
        preflight_section = (
            "\n## Applicability Preflight\n\n"
            f"- packet_hash: `{_packet_hash(repo)}`\n"
            f"- bridge_document_name: `{SLUG}`\n"
            f"- content_file: `bridge/{SLUG}-003.md`\n"
            f"- operative_file: `bridge/{SLUG}-003.md`\n"
            "- preflight_passed: `true`\n"
            "- missing_required_specs: []\n"
            "- missing_advisory_specs: []\n"
            f"{hash_lines}"
        )
    elif hash_field_count:
        preflight_section = f"\n## Evidence\n\n{hash_lines}"

    return f"""VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: 22222222-2222-4222-8222-222222222222
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: lo_verdict
Document: {SLUG}
Version: 004
Responds to: bridge/{SLUG}-003.md
Recommended commit type: fix

## Prior Deliberations

_No prior deliberations: candidate evidence hash restamp fixture._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest {_THIS_TEST}` | yes | PASS |

## Positive Confirmations

- Restamp fixture only.

## Commands Executed

- `pytest {_THIS_TEST} -q`
{preflight_section}{extra_sections}
"""


def _finalize(helper: ModuleType, repo: Path, body: str):
    return helper.finalize_verified_commit(
        SLUG,
        body,
        include_paths=["scripts/feature.py", f"bridge/{SLUG}-003.md"],
        commit_message="fix: restamp fixture finalization",
        project_root=repo,
        pre_populate=False,
        db=False,
        log_path=False,
    )


def _hash_field_values(gate: ModuleType, text: str) -> list[str]:
    """Actual ``candidate_evidence_hash:`` field values.

    Matching on the field regex rather than the bare substring matters: this
    module's own filename contains ``candidate_evidence_hash`` and appears inside
    the fixture body's evidence sections.
    """
    return [match.group("value") for match in gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.finditer(text)]


def _assert_final_bytes_are_hash_consistent(gate: ModuleType, repo: Path) -> str:
    """TEST-11782: recomputation over the final on-disk bytes equals the stamped value."""
    verdict_rel = f"bridge/{SLUG}-004.md"
    verdict_path = repo / "bridge" / f"{SLUG}-004.md"
    assert verdict_path.is_file(), "finalization must have written the terminal verdict"
    content = verdict_path.read_text(encoding="utf-8")

    matches = list(gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.finditer(content))
    assert len(matches) == 1, f"expected exactly one stamped field, found {len(matches)}"
    stamped = matches[0].group("value")

    expected = gate._candidate_evidence_hash(verdict_rel, content, repo)
    assert expected is not None
    assert stamped == expected, "stamped candidate_evidence_hash must match the final normalized bytes"
    assert stamped != gate.CANDIDATE_EVIDENCE_HASH_SENTINEL
    return stamped


def test_final_verdict_bytes_match_stamped_candidate_evidence_hash(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """TEST-11782 end to end through the real finalizer and the real writer normalization."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)

    _finalize(helper, repo, body)

    _assert_final_bytes_are_hash_consistent(gate, repo)


def test_finalization_succeeds_where_stale_stamp_previously_denied(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """The pre-mutation stamp is the exact input the gate denied before this fix."""
    repo = _init_repo(tmp_path)
    stale = "sha256:" + ("0" * 64)
    body = _verdict_body(repo, hash_value=stale)

    _finalize(helper, repo, body)

    stamped = _assert_final_bytes_are_hash_consistent(gate, repo)
    assert stamped != stale, "the stale authored value must have been replaced"


def test_evidence_append_path_is_hash_consistent(helper: ModuleType, gate: ModuleType, tmp_path: Path) -> None:
    """The Commit Finalization Evidence append lands inside the stamped bytes."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)
    assert "## Commit Finalization Evidence" not in body

    _finalize(helper, repo, body)

    content = (repo / "bridge" / f"{SLUG}-004.md").read_text(encoding="utf-8")
    assert "## Commit Finalization Evidence" in content, "the append must have fired for this body"
    _assert_final_bytes_are_hash_consistent(gate, repo)


def test_prior_deliberations_seeding_path_is_hash_consistent(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """Seeded content is inside the stamped bytes; the recomputation still matches."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)
    seeded_marker = "\n_Seeded prior deliberation fixture line._\n"

    def _seed(_slug, incoming_body, **_kwargs):
        return incoming_body + seeded_marker

    original = helper.seed_prior_deliberations
    helper.seed_prior_deliberations = _seed
    try:
        _finalize(helper, repo, body)
    finally:
        helper.seed_prior_deliberations = original

    content = (repo / "bridge" / f"{SLUG}-004.md").read_text(encoding="utf-8")
    assert seeded_marker.strip() in content, "seeded content must be present in the final verdict"
    _assert_final_bytes_are_hash_consistent(gate, repo)


def test_writer_normalization_is_idempotent_for_finalizer_bodies(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """The pre-applied normalization and the writer's re-application must agree."""
    from scripts.gtkb_bridge_writer import ensure_author_metadata, normalize_bridge_envelope_head

    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)

    once = normalize_bridge_envelope_head(ensure_author_metadata(body, project_root=repo, explicit=None))
    twice = normalize_bridge_envelope_head(ensure_author_metadata(once, project_root=repo, explicit=None))

    assert once == twice, "writer pre-audit normalization must be idempotent for finalizer-shaped bodies"


def test_restamp_returns_body_whose_recomputation_is_a_fixpoint(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """Unit-level: the returned body is already stable under the gate's recomputation."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)
    verdict_rel = f"bridge/{SLUG}-004.md"

    stamped = helper._restamp_candidate_evidence_hash(body, verdict_rel_path=verdict_rel, project_root=repo)
    again = helper._restamp_candidate_evidence_hash(stamped, verdict_rel_path=verdict_rel, project_root=repo)

    assert stamped == again, "re-stamping an already-stamped body must be a no-op"
    embedded = gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.search(stamped).group("value")
    assert embedded == gate._candidate_evidence_hash(verdict_rel, stamped, repo)


def test_missing_candidate_evidence_hash_field_fails_closed(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """A preflight section with no hash field would be denied by the gate; fail closed first."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value="", hash_field_count=0)
    assert not _hash_field_values(gate, body)

    with pytest.raises(helper.VerifiedFinalizationError, match="candidate_evidence_hash"):
        _finalize(helper, repo, body)

    assert not (repo / "bridge" / f"{SLUG}-004.md").exists(), "no terminal artifact may survive a failure"
    assert "restamp fixture finalization" not in _git(repo, "log", "--oneline", check=False).stdout


def test_body_without_preflight_section_needs_no_stamp(helper: ModuleType, gate: ModuleType, tmp_path: Path) -> None:
    """The gate only checks the hash when a preflight section exists; mirror that exactly."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value="", hash_field_count=0, include_preflight_section=False)

    result = helper._restamp_candidate_evidence_hash(body, verdict_rel_path=f"bridge/{SLUG}-004.md", project_root=repo)

    assert not _hash_field_values(gate, result)


def test_duplicate_candidate_evidence_hash_field_fails_closed(
    helper: ModuleType, gate: ModuleType, tmp_path: Path
) -> None:
    """The gate's substitution requires exactly one match and returns None otherwise."""
    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL, hash_field_count=2)

    with pytest.raises(helper.VerifiedFinalizationError, match="candidate_evidence_hash"):
        _finalize(helper, repo, body)

    assert not (repo / "bridge" / f"{SLUG}-004.md").exists()
    assert "restamp fixture finalization" not in _git(repo, "log", "--oneline", check=False).stdout


def test_gate_module_unavailable_fails_closed(
    helper: ModuleType, gate: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No terminal VERIFIED verdict may be finalized without the hash definition."""
    import scripts.gtkb_bridge_writer as writer

    repo = _init_repo(tmp_path)
    body = _verdict_body(repo, hash_value=gate.CANDIDATE_EVIDENCE_HASH_SENTINEL)
    monkeypatch.setattr(
        writer,
        "_bridge_compliance_gate_path",
        lambda _root: tmp_path / "absent" / "bridge-compliance-gate.py",
    )

    with pytest.raises(helper.VerifiedFinalizationError, match="Bridge-compliance gate could not be loaded"):
        _finalize(helper, repo, body)

    assert not (repo / "bridge" / f"{SLUG}-004.md").exists()
    assert "restamp fixture finalization" not in _git(repo, "log", "--oneline", check=False).stdout


def test_codex_adapter_projection_matches_canonical_helper() -> None:
    """Both bridge submission paths must carry the fix (DCL-CROSS-HARNESS-ENFORCEMENT-001)."""
    assert CODEX_HELPER.read_bytes() == CLAUDE_HELPER.read_bytes()


def test_restamp_is_wired_into_finalization() -> None:
    """The re-stamp must run after every body mutation and before the write."""
    source = CLAUDE_HELPER.read_text(encoding="utf-8")
    restamp_at = source.index("body_to_write = _restamp_candidate_evidence_hash(")
    append_at = source.index("body_to_write = _append_commit_finalization_evidence(")
    write_at = source.index("publication_path = write_bridge_file(")
    assert append_at < restamp_at < write_at
