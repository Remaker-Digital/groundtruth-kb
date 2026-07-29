"""Focused contract tests for the exact-thread bridge lifecycle resolver."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from scripts.bridge_lifecycle_resolver import (
    PENDING_CORRECTION_DIAGNOSTIC,
    BridgeLifecycleResolutionError,
    resolve_bridge_lifecycle,
)


def _role_for(status: str) -> str:
    if status in {"NEW", "REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}:
        return "prime-builder/codex"
    if status in {"GO", "NO-GO", "VERIFIED", "ADVISORY"}:
        return "loyal-opposition/codex"
    return "owner"


def _write_version(
    root: Path,
    bridge_id: str,
    version: int,
    status: str,
    *,
    author_identity: str | None = None,
    document: str | None = None,
    metadata_version: str | None = None,
    responds_to: str | None = None,
    include_responds: bool = True,
    include_author_identity: bool = True,
    raw_bytes: bytes | None = None,
) -> Path:
    path = root / "bridge" / f"{bridge_id}-{version:03d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if raw_bytes is not None:
        path.write_bytes(raw_bytes)
        return path
    if responds_to is None and version > 1:
        responds_to = f"bridge/{bridge_id}-{version - 1:03d}.md"
    version_value = metadata_version if metadata_version is not None else f"{version:03d}"
    lines = [status]
    if include_author_identity:
        lines.append(f"author_identity: {author_identity or _role_for(status)}")
    lines.append(f"Document: {document or bridge_id}")
    lines.append(f"Version: {version_value}")
    if include_responds and version > 1:
        lines.append(f"Responds to: {responds_to}")
    lines.extend(("", f"# Fixture {bridge_id} v{version}", ""))
    path.write_text("\n".join(lines), encoding="utf-8-sig")
    return path


def _write_malformed(
    root: Path,
    bridge_id: str,
    version: int,
    first_line: str = "GO - decorated verdict",
) -> Path:
    path = root / "bridge" / f"{bridge_id}-{version:03d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            (
                first_line,
                "author_identity: loyal-opposition/codex",
                f"Document: {bridge_id}",
                f"Version: {version:03d}",
                f"Responds to: bridge/{bridge_id}-{version - 1:03d}.md",
                "",
            )
        ),
        encoding="utf-8-sig",
    )
    return path


def _signature(result) -> bytes:
    return json.dumps(
        dataclasses.asdict(result),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _simple_go(root: Path, bridge_id: str = "fixture") -> None:
    _write_version(root, bridge_id, 1, "NEW")
    _write_version(root, bridge_id, 2, "GO")


def _corrected_go(root: Path, bridge_id: str) -> None:
    _write_version(root, bridge_id, 1, "NEW")
    _write_malformed(root, bridge_id, 2)
    _write_version(root, bridge_id, 3, "NO-ACTION")
    _write_version(root, bridge_id, 4, "GO")


def test_public_entrypoint_exposes_immutable_named_contract(tmp_path: Path) -> None:
    _simple_go(tmp_path)

    result = resolve_bridge_lifecycle(tmp_path, "fixture")

    assert result.bridge_id == "fixture"
    assert tuple(item.version for item in result.audit_versions) == (1, 2)
    assert tuple(item.status for item in result.audit_versions) == ("NEW", "GO")
    assert tuple(item.path for item in result.audit_versions) == (
        "bridge/fixture-001.md",
        "bridge/fixture-002.md",
    )
    assert result.latest_strict_state is result.audit_versions[1]
    assert result.review_artifact is None
    assert result.implementation_artifact is result.audit_versions[0]
    assert result.implementation_verdict is result.audit_versions[1]
    assert result.quarantined_paths == ()
    assert result.blocking_diagnostics == ()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.latest_strict_state.status = "NO-GO"
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.bridge_id = "changed"


def test_revised_proposal_go_uses_latest_prime_proposal(tmp_path: Path) -> None:
    slug = "revised-go"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "NO-GO")
    _write_version(tmp_path, slug, 3, "REVISED")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.implementation_artifact.version == 3
    assert result.implementation_verdict.version == 4


def test_post_go_report_verified_is_terminal(tmp_path: Path) -> None:
    slug = "verified-report"
    _simple_go(tmp_path, slug)
    _write_version(tmp_path, slug, 3, "NEW")
    _write_version(tmp_path, slug, 4, "VERIFIED")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.status == "VERIFIED"
    assert result.review_artifact is None
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None


def test_post_go_report_no_go_retains_resumable_implementation_pair(tmp_path: Path) -> None:
    slug = "report-no-go"
    _simple_go(tmp_path, slug)
    _write_version(tmp_path, slug, 3, "NEW")
    _write_version(tmp_path, slug, 4, "NO-GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.status == "NO-GO"
    assert result.implementation_artifact.version == 1
    assert result.implementation_verdict.version == 2


def test_post_go_report_awaiting_review_exposes_only_review_artifact(tmp_path: Path) -> None:
    slug = "report-awaiting"
    _simple_go(tmp_path, slug)
    _write_version(tmp_path, slug, 3, "NEW")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.review_artifact.version == 3
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None


def test_owner_deferred_post_go_report_can_be_followed_by_revised_proposal(tmp_path: Path) -> None:
    """A deferred report can hand off to a newly reviewed corrective proposal."""

    slug = "deferred-report-reproposal"
    _simple_go(tmp_path, slug)
    _write_version(tmp_path, slug, 3, "NEW")
    _write_version(tmp_path, slug, 4, "REVISED")

    awaiting_go = resolve_bridge_lifecycle(tmp_path, slug)

    assert awaiting_go.latest_strict_state.version == 4
    assert awaiting_go.review_artifact.version == 4
    assert awaiting_go.implementation_artifact is None
    assert awaiting_go.implementation_verdict is None

    _write_version(tmp_path, slug, 5, "GO")
    approved = resolve_bridge_lifecycle(tmp_path, slug)

    assert approved.implementation_artifact.version == 4
    assert approved.implementation_verdict.version == 5


def test_no_go_on_owner_deferred_corrective_proposal_does_not_resume_old_go(tmp_path: Path) -> None:
    """The old GO cannot authorize work after the new proposal receives NO-GO."""

    slug = "deferred-report-reproposal-no-go"
    _simple_go(tmp_path, slug)
    _write_version(tmp_path, slug, 3, "NEW")
    _write_version(tmp_path, slug, 4, "REVISED")
    _write_version(tmp_path, slug, 5, "NO-GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.status == "NO-GO"
    assert result.review_artifact is None
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None


def test_pending_correction_is_reviewable_non_authorizing_and_not_quarantined(
    tmp_path: Path,
) -> None:
    slug = "pending-correction"
    _write_version(tmp_path, slug, 1, "NEW")
    malformed = _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.audit_versions[1].status is None
    assert result.audit_versions[1].observed_status == "GO"
    assert result.audit_versions[1].classification == "malformed"
    assert result.latest_strict_state.version == 3
    assert result.review_artifact.version == 3
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None
    assert result.quarantined_paths == ()
    assert tuple(item.code for item in result.blocking_diagnostics) == (PENDING_CORRECTION_DIAGNOSTIC,)
    assert malformed.relative_to(tmp_path).as_posix() not in result.quarantined_paths


def test_complete_corrected_go_quarantines_only_malformed_file(tmp_path: Path) -> None:
    slug = "corrected-go"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.version == 4
    assert result.review_artifact is None
    assert result.implementation_artifact.version == 1
    assert result.implementation_verdict.version == 4
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)
    assert result.blocking_diagnostics == ()


def test_corrected_go_continues_into_pending_report(tmp_path: Path) -> None:
    slug = "corrected-report-pending"
    _corrected_go(tmp_path, slug)
    _write_version(tmp_path, slug, 5, "NEW")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert tuple(item.version for item in result.audit_versions) == (1, 2, 3, 4, 5)
    assert result.latest_strict_state.version == 5
    assert result.review_artifact.version == 5
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)


def test_public_foundation_shape_continues_to_report_no_go(tmp_path: Path) -> None:
    slug = "foundation-corrected-report"
    _corrected_go(tmp_path, slug)
    _write_version(tmp_path, slug, 5, "NEW")
    _write_version(tmp_path, slug, 6, "NO-GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert tuple(item.version for item in result.audit_versions) == (1, 2, 3, 4, 5, 6)
    assert result.latest_strict_state.version == 6
    assert result.latest_strict_state.status == "NO-GO"
    assert result.review_artifact is None
    assert result.implementation_artifact.version == 1
    assert result.implementation_verdict.version == 4
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)


def test_corrected_report_revision_switches_to_latest_implementation_pair(
    tmp_path: Path,
) -> None:
    slug = "corrected-report-revision"
    _corrected_go(tmp_path, slug)
    _write_version(tmp_path, slug, 5, "NEW")
    _write_version(tmp_path, slug, 6, "NO-GO")
    _write_version(tmp_path, slug, 7, "REVISED")
    _write_version(tmp_path, slug, 8, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.version == 8
    assert result.implementation_artifact.version == 7
    assert result.implementation_verdict.version == 8
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)


def test_corrected_chain_continues_to_terminal_verified(tmp_path: Path) -> None:
    slug = "corrected-terminal"
    _corrected_go(tmp_path, slug)
    _write_version(tmp_path, slug, 5, "NEW")
    _write_version(tmp_path, slug, 6, "NO-GO")
    _write_version(tmp_path, slug, 7, "REVISED")
    _write_version(tmp_path, slug, 8, "GO")
    _write_version(tmp_path, slug, 9, "NEW")
    _write_version(tmp_path, slug, 10, "VERIFIED")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert tuple(item.version for item in result.audit_versions) == tuple(range(1, 11))
    assert result.latest_strict_state.version == 10
    assert result.latest_strict_state.status == "VERIFIED"
    assert result.review_artifact is None
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)


def test_corrected_go_cannot_skip_report_to_verified(tmp_path: Path) -> None:
    slug = "corrected-go-direct-verified"
    _corrected_go(tmp_path, slug)
    _write_version(tmp_path, slug, 5, "VERIFIED")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "INVALID_BRIDGE_TRANSITION"


def test_version_after_corrected_verified_fails_terminal(tmp_path: Path) -> None:
    slug = "corrected-verified-terminal"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2, first_line="VERIFIED - decorated")
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "VERIFIED")
    _write_version(tmp_path, slug, 5, "REVISED")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "VERSION_AFTER_TERMINAL_STATUS"


def test_corrected_tail_does_not_accept_responds_to_go_alias(tmp_path: Path) -> None:
    slug = "corrected-responds-to-go"
    _corrected_go(tmp_path, slug)
    report = _write_version(tmp_path, slug, 5, "NEW")
    content = report.read_text(encoding="utf-8-sig")
    report.write_text(
        content.replace("Responds to:", "Responds to GO:"),
        encoding="utf-8-sig",
    )

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "WRONG_RESPONDS_TO_LINK"


def test_corrected_tail_does_not_accept_decorated_version_metadata(
    tmp_path: Path,
) -> None:
    slug = "corrected-decorated-version"
    _corrected_go(tmp_path, slug)
    _write_version(
        tmp_path,
        slug,
        5,
        "NEW",
        metadata_version="005 (NEW; implementation report)",
    )

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "WRONG_BRIDGE_VERSION_METADATA"


@pytest.mark.parametrize("corrected_status", ["NO-GO", "VERIFIED"])
def test_complete_non_go_correction_never_exposes_implementation_pair(
    tmp_path: Path,
    corrected_status: str,
) -> None:
    slug = f"corrected-{corrected_status.lower()}"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2, first_line=f"{corrected_status} - decorated")
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, corrected_status)

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.latest_strict_state.status == corrected_status
    assert result.implementation_artifact is None
    assert result.implementation_verdict is None
    assert result.quarantined_paths == (f"bridge/{slug}-002.md",)


@pytest.mark.parametrize(
    ("first_line", "expected_code"),
    [
        ("NEW - decorated", "MALFORMED_CORRECTION_WRONG_SHAPE"),
        ("REVISED-ish", "MALFORMED_CORRECTION_WRONG_SHAPE"),
        ("not a status", "MALFORMED_CORRECTION_WRONG_SHAPE"),
    ],
)
def test_prime_shaped_or_unknown_malformed_content_cannot_form_correction(
    tmp_path: Path,
    first_line: str,
    expected_code: str,
) -> None:
    slug = "wrong-malformed-shape"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2, first_line=first_line)
    _write_version(tmp_path, slug, 3, "NO-ACTION")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == expected_code


def test_unlinked_malformed_verdict_has_no_stale_fallback(tmp_path: Path) -> None:
    slug = "unlinked-malformed"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_INVALID_TAIL"


def test_multiple_malformed_exact_versions_fail_closed(tmp_path: Path) -> None:
    slug = "multiple-malformed"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)
    _write_malformed(tmp_path, slug, 3)

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MULTIPLE_MALFORMED_BRIDGE_VERSIONS"


def test_strict_utf8_sig_rejects_invalid_bytes(tmp_path: Path) -> None:
    slug = "invalid-utf8"
    _write_version(tmp_path, slug, 1, "NEW", raw_bytes=b"\xff\xfe\x00")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "BRIDGE_FILE_INVALID_UTF8"


@pytest.mark.parametrize("line_one", ["", " GO", "GO ", "GO - approved"])
def test_status_must_be_exact_physical_line_one(tmp_path: Path, line_one: str) -> None:
    slug = "strict-line-one"
    if line_one == "":
        content = f"\nGO\nauthor_identity: loyal-opposition/codex\nDocument: {slug}\nVersion: 001\n"
        path = tmp_path / "bridge" / f"{slug}-001.md"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8-sig")
    else:
        _write_malformed(tmp_path, slug, 1, first_line=line_one)

    with pytest.raises(BridgeLifecycleResolutionError):
        resolve_bridge_lifecycle(tmp_path, slug)


@pytest.mark.parametrize(
    ("versions", "code"),
    [
        ((2,), "NONCONTIGUOUS_BRIDGE_VERSIONS"),
        ((1, 3), "NONCONTIGUOUS_BRIDGE_VERSIONS"),
        ((0, 1), "NONCONTIGUOUS_BRIDGE_VERSIONS"),
    ],
)
def test_exact_versions_must_be_contiguous_from_one(
    tmp_path: Path,
    versions: tuple[int, ...],
    code: str,
) -> None:
    slug = "gapped"
    for version in versions:
        _write_version(tmp_path, slug, version, "NEW" if version in {0, 1} else "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ({"document": "other-thread"}, "WRONG_BRIDGE_DOCUMENT"),
        ({"metadata_version": "099"}, "WRONG_BRIDGE_VERSION_METADATA"),
        ({"responds_to": "bridge/other-thread-001.md"}, "WRONG_RESPONDS_TO_LINK"),
        ({"include_responds": False}, "WRONG_RESPONDS_TO_LINK"),
        ({"author_identity": "prime-builder/codex"}, "WRONG_STATUS_AUTHOR_ROLE"),
    ],
)
def test_wrong_document_version_link_or_verdict_role_fails_closed(
    tmp_path: Path,
    mutation: dict[str, object],
    code: str,
) -> None:
    slug = "metadata-failure"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "GO", **mutation)

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == code


def test_wrong_prime_author_role_fails_closed(tmp_path: Path) -> None:
    slug = "wrong-prime-role"
    _write_version(
        tmp_path,
        slug,
        1,
        "NEW",
        author_identity="loyal-opposition/codex",
    )

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "WRONG_STATUS_AUTHOR_ROLE"


def test_duplicate_metadata_fails_closed(tmp_path: Path) -> None:
    slug = "duplicate-metadata"
    path = _write_version(tmp_path, slug, 1, "NEW")
    path.write_text(
        path.read_text(encoding="utf-8-sig") + f"Document: {slug}\n",
        encoding="utf-8-sig",
    )

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "DUPLICATE_BRIDGE_METADATA"


def test_invalid_ordinary_transition_fails_closed(tmp_path: Path) -> None:
    slug = "bad-transition"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "GO")
    _write_version(tmp_path, slug, 3, "VERIFIED")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "INVALID_BRIDGE_TRANSITION"


def test_longer_valid_slug_prefix_sibling_is_observationally_irrelevant(
    tmp_path: Path,
) -> None:
    _simple_go(tmp_path, "topic")
    before = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))
    _simple_go(tmp_path, "topic-longer")

    after = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))

    assert after == before


def test_malformed_prefix_sibling_is_observationally_irrelevant(tmp_path: Path) -> None:
    _simple_go(tmp_path, "topic")
    before = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))
    sibling = tmp_path / "bridge" / "topic-malformed-001.md"
    sibling.write_bytes(b"\xff\xfe malformed sibling")

    after = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))

    assert after == before


def test_numeric_looking_prefix_sibling_is_observationally_irrelevant(
    tmp_path: Path,
) -> None:
    _simple_go(tmp_path, "topic")
    before = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))
    sibling = tmp_path / "bridge" / "topic-001-extra-001.md"
    sibling.write_text("not selected\n", encoding="utf-8")

    after = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))

    assert after == before


def test_prefix_sibling_creation_and_removal_preserve_byte_equivalent_result(
    tmp_path: Path,
) -> None:
    _simple_go(tmp_path, "topic")
    before = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))
    sibling = tmp_path / "bridge" / "topic-later-001.md"
    sibling.write_text("arbitrary sibling bytes\n", encoding="utf-8")
    during = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))
    sibling.unlink()
    after = _signature(resolve_bridge_lifecycle(tmp_path, "topic"))

    assert before == during == after


def test_legacy_no_suffix_file_has_no_authority(tmp_path: Path) -> None:
    slug = "legacy-only"
    path = tmp_path / "bridge" / f"{slug}.md"
    path.parent.mkdir(parents=True)
    path.write_text("NEW\n", encoding="utf-8")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "BRIDGE_THREAD_NOT_FOUND"


def test_legacy_no_suffix_file_is_ignored_beside_exact_chain(tmp_path: Path) -> None:
    slug = "legacy-shadow"
    _simple_go(tmp_path, slug)
    before = _signature(resolve_bridge_lifecycle(tmp_path, slug))
    (tmp_path / "bridge" / f"{slug}.md").write_bytes(b"\xff legacy authority")

    after = _signature(resolve_bridge_lifecycle(tmp_path, slug))

    assert after == before


# GOV-DOCUMENT-AUTHOR-PROVENANCE-001 grandfathering (WI-5670): a canonical-status
# version with structurally valid Document/Version/Responds-to but no
# author_identity header predates the provenance contract. Non-operative legacy
# versions must not block resolution; the operative proposal/GO pair must still
# be provenance-complete.


def test_legacy_non_operative_verdict_is_grandfathered(tmp_path: Path) -> None:
    """A non-operative legacy NO-GO (no author_identity) does not block an
    otherwise-strict thread from resolving to its strict operative pair."""

    slug = "legacy-grandfathered"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "NO-GO", include_author_identity=False)
    _write_version(tmp_path, slug, 3, "REVISED")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.implementation_artifact.version == 3
    assert result.implementation_verdict.version == 4
    assert result.audit_versions[1].classification == "legacy"


def test_roleless_identity_non_operative_verdict_is_grandfathered(tmp_path: Path) -> None:
    """A present but role-unreadable historical identity remains audit-only."""

    slug = "roleless-grandfathered"
    roleless_identity = "codex/A"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "NO-GO", author_identity=roleless_identity)
    _write_version(tmp_path, slug, 3, "REVISED")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    assert result.implementation_artifact.version == 3
    assert result.implementation_verdict.version == 4
    roleless = result.audit_versions[1]
    assert roleless.classification == "legacy"
    assert roleless.author_identity == roleless_identity
    assert roleless.author_role is None


def test_legacy_version_is_not_malformed(tmp_path: Path) -> None:
    """A legacy (missing author_identity) version is a distinct, non-malformed
    classification: the single-malformed correction path is unaffected."""

    slug = "legacy-not-malformed"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "NO-GO", include_author_identity=False)
    _write_version(tmp_path, slug, 3, "REVISED")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    legacy_version = result.audit_versions[1]
    assert legacy_version.is_legacy is True
    assert legacy_version.is_malformed is False
    assert legacy_version.is_strict is False
    assert legacy_version.status == "NO-GO"
    assert legacy_version.author_identity is None
    assert legacy_version.author_role is None


def test_present_roleless_identity_is_legacy_not_malformed(tmp_path: Path) -> None:
    slug = "roleless-not-malformed"
    roleless_identity = "claude/B"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "NO-GO", author_identity=roleless_identity)
    _write_version(tmp_path, slug, 3, "REVISED")
    _write_version(tmp_path, slug, 4, "GO")

    result = resolve_bridge_lifecycle(tmp_path, slug)

    roleless = result.audit_versions[1]
    assert roleless.is_legacy is True
    assert roleless.is_malformed is False
    assert roleless.is_strict is False
    assert roleless.author_identity == roleless_identity
    assert roleless.author_role is None


def test_roleless_terminal_verified_after_strict_report_fails_closed(tmp_path: Path) -> None:
    """A present-but-roleless terminal verdict is never grandfathered.

    The proposal, GO, and post-implementation report are strict.  A terminal
    VERIFIED carrying an identity whose role cannot be resolved must still
    pass the status-author-role check instead of becoming audit-only legacy.
    """

    slug = "roleless-terminal-verified"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "GO")
    _write_version(tmp_path, slug, 3, "NEW")
    _write_version(tmp_path, slug, 4, "VERIFIED", author_identity="codex/A")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "WRONG_STATUS_AUTHOR_ROLE"


def test_operative_go_missing_provenance_fails_closed(tmp_path: Path) -> None:
    """Implementation authority must never derive from a legacy GO, even though
    non-operative legacy versions are tolerated elsewhere in the same chain."""

    slug = "legacy-operative-go"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "GO", include_author_identity=False)

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "OPERATIVE_VERSION_MISSING_PROVENANCE"


def test_operative_go_roleless_identity_fails_closed(tmp_path: Path) -> None:
    slug = "roleless-operative-go"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_version(tmp_path, slug, 2, "GO", author_identity="codex/A")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "OPERATIVE_VERSION_MISSING_PROVENANCE"


def test_operative_proposal_missing_provenance_fails_closed(tmp_path: Path) -> None:
    """Implementation authority must never derive from a legacy proposal, even
    when the GO itself is strict."""

    slug = "legacy-operative-proposal"
    _write_version(tmp_path, slug, 1, "NEW", include_author_identity=False)
    _write_version(tmp_path, slug, 2, "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "OPERATIVE_VERSION_MISSING_PROVENANCE"


def test_operative_proposal_roleless_identity_fails_closed(tmp_path: Path) -> None:
    slug = "roleless-operative-proposal"
    _write_version(tmp_path, slug, 1, "NEW", author_identity="claude/B")
    _write_version(tmp_path, slug, 2, "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "OPERATIVE_VERSION_MISSING_PROVENANCE"


def test_corrected_go_operative_proposal_legacy_fails_closed_via_role_check(
    tmp_path: Path,
) -> None:
    """`_correction_resolution`'s direct implementation_artifact/verdict branch
    needs no separate OPERATIVE_VERSION_MISSING_PROVENANCE check: a legacy
    (author_role=None) Prime predecessor already fails the existing
    MALFORMED_CORRECTION_WRONG_PREDECESSOR role check before that branch is
    reached, so the fail-closed guarantee holds without redundant code."""

    slug = "corrected-legacy-proposal"
    _write_version(tmp_path, slug, 1, "NEW", include_author_identity=False)
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_WRONG_PREDECESSOR"


def test_corrected_go_operative_verdict_legacy_fails_closed_via_role_check(
    tmp_path: Path,
) -> None:
    """Symmetric to the predecessor case: a legacy (author_role=None) verdict
    standing in the corrected-tail GO/NO-GO/VERIFIED slot already fails the
    existing MALFORMED_CORRECTION_INVALID_VERDICT role check."""

    slug = "corrected-legacy-verdict"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "GO", include_author_identity=False)

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_INVALID_VERDICT"


def test_corrected_go_roleless_predecessor_fails_closed_via_role_check(tmp_path: Path) -> None:
    slug = "corrected-roleless-proposal"
    _write_version(tmp_path, slug, 1, "NEW", author_identity="codex/A")
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_WRONG_PREDECESSOR"


def test_corrected_go_roleless_no_action_fails_closed_via_role_check(tmp_path: Path) -> None:
    slug = "corrected-roleless-no-action"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION", author_identity="codex/A")
    _write_version(tmp_path, slug, 4, "GO")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_MISSING_NO_ACTION"


def test_corrected_go_roleless_verdict_fails_closed_via_role_check(tmp_path: Path) -> None:
    slug = "corrected-roleless-verdict"
    _write_version(tmp_path, slug, 1, "NEW")
    _write_malformed(tmp_path, slug, 2)
    _write_version(tmp_path, slug, 3, "NO-ACTION")
    _write_version(tmp_path, slug, 4, "GO", author_identity="claude/B")

    with pytest.raises(BridgeLifecycleResolutionError) as caught:
        resolve_bridge_lifecycle(tmp_path, slug)
    assert caught.value.code == "MALFORMED_CORRECTION_INVALID_VERDICT"
