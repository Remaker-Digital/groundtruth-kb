"""TEST-12653: corrected GO lineage retains exact proposal scope."""

from pathlib import Path

import pytest
from groundtruth_kb.test_artifact_update import (
    TestArtifactUpdateError as LineageError,
)
from groundtruth_kb.test_artifact_update import (
    TestArtifactUpdateRequest as UpdateRequest,
)
from groundtruth_kb.test_artifact_update import (
    _resolve_bridge_lineage,
)

SLUG = "corrected-go-fixture"


def request():
    return UpdateRequest(
        test_id="TEST-FIXTURE",
        expected_version=1,
        idempotency_key="fixture",
        project_id="PROJECT-FIXTURE",
        work_item_id="WI-FIXTURE",
        bridge_slug=SLUG,
        actor_session_context_id="fixture",
        changed_by="fixture",
        change_reason="fixture",
    )


def write(root: Path, version: int, status: str, predecessor=None, **overrides):
    metadata = {
        "Document": SLUG,
        "Version": f"{version:03}",
        "Project": "PROJECT-FIXTURE",
        "Work Item": "WI-FIXTURE",
        "bridge_kind": "implementation_proposal" if status in {"NEW", "REVISED"} else "lo_verdict",
    }
    if predecessor is not None:
        metadata["Responds to"] = f"bridge/{SLUG}-{predecessor:03}.md"
    if status in {"NEW", "REVISED"}:
        metadata["test_artifact_targets"] = '["TEST-FIXTURE"]'
    metadata.update(overrides)
    path = root / "bridge" / f"{SLUG}-{version:03}.md"
    path.parent.mkdir(exist_ok=True)
    role = "pb" if status == "GO" else "lo"
    path.write_text(
        f"{status}\n::init gtkb {role}\n::open build\n\n" + "\n".join(f"{k}: {v}" for k, v in metadata.items()) + "\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize("corrections", [0, 1, 2])
def test_corrected_go_resolves_original_proposal(tmp_path, corrections):
    write(tmp_path, 1, "NEW")
    write(tmp_path, 2, "GO", 1)
    for index in range(corrections):
        rejection = 3 + index * 2
        write(tmp_path, rejection, "VERDICT-REJECTED", rejection - 1)
        write(tmp_path, rejection + 1, "GO", rejection)
    result = _resolve_bridge_lineage(tmp_path, request())
    assert result["proposal_file"] == f"bridge/{SLUG}-001.md"
    assert result["test_artifact_targets"] == ["TEST-FIXTURE"]
    assert result["go_file"] == f"bridge/{SLUG}-{2 + corrections * 2:03}.md"


def test_corrected_go_resolves_latest_revised_proposal(tmp_path):
    write(tmp_path, 1, "NEW", test_artifact_targets='["TEST-OLD"]')
    write(tmp_path, 2, "NO-GO", 1)
    write(tmp_path, 3, "REVISED", 2)
    write(tmp_path, 4, "GO", 3)
    write(tmp_path, 5, "VERDICT-REJECTED", 4)
    write(tmp_path, 6, "GO", 5)
    result = _resolve_bridge_lineage(tmp_path, request())
    assert result["proposal_file"] == f"bridge/{SLUG}-003.md"


@pytest.mark.parametrize(
    "field,value",
    [
        ("Project", "PROJECT-OTHER"),
        ("Work Item", "WI-OTHER"),
        ("Document", "another-thread"),
        ("Version", "999"),
        ("test_artifact_targets", '["TEST-OTHER"]'),
    ],
)
def test_direct_proposal_identity_and_scope_are_enforced(tmp_path, field, value):
    write(tmp_path, 1, "NEW", **{field: value})
    write(tmp_path, 2, "GO", 1)
    with pytest.raises(LineageError):
        _resolve_bridge_lineage(tmp_path, request())


@pytest.mark.parametrize("mode", ["missing", "cycle", "cross_thread", "outside", "no_proposal", "mismatched_hop"])
def test_invalid_correction_path_is_refused(tmp_path, mode):
    write(tmp_path, 1, "NEW")
    write(tmp_path, 2, "GO", 1)
    write(tmp_path, 3, "VERDICT-REJECTED", 2)
    write(tmp_path, 4, "GO", 3)
    if mode == "missing":
        (tmp_path / "bridge" / f"{SLUG}-002.md").unlink()
    elif mode == "cycle":
        write(tmp_path, 3, "VERDICT-REJECTED", 4)
    elif mode == "cross_thread":
        write(tmp_path, 3, "VERDICT-REJECTED", 2, **{"Document": "other"})
    elif mode == "outside":
        write(tmp_path, 3, "VERDICT-REJECTED", 2, **{"Responds to": "../outside.md"})
    elif mode == "no_proposal":
        write(tmp_path, 1, "ADVISORY")
    else:
        write(tmp_path, 2, "GO", 1, **{"Work Item": "WI-OTHER"})
    with pytest.raises(LineageError):
        _resolve_bridge_lineage(tmp_path, request())


def test_same_thread_metadata_cannot_hide_foreign_filename(tmp_path):
    source = write(tmp_path, 1, "NEW")
    foreign = tmp_path / "bridge" / "another-thread-001.md"
    foreign.write_bytes(source.read_bytes())
    write(tmp_path, 2, "GO", 1, **{"Responds to": "bridge/another-thread-001.md"})
    with pytest.raises(LineageError):
        _resolve_bridge_lineage(tmp_path, request())
