"""c123 (batch design WP5, G36): native targets under .agents/skills are accepted, every other .agents path refused.

GOV-HARNESS-NEUTRAL-BASELINE-001 v2 and ADR-RULE-PROJECTION-FLOW-INVERSION-001 v3 name .agents/skills the single
authored shared skills tree. The native bridge's path rule (``_paths`` in bridge/native.py, applied to proposal headers,
stored scope, effect paths and artifact snapshots) refuses every .agents path except a file under the root-level
.agents/skills folder. The commit checker states the same rule; the cases below follow its table
(platform_tests/scripts/test_check_commit_pathspec_safety.py). Until c123 only the refusals were tested.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge.native import _paths, parse_authored_message
from groundtruth_kb.postgres_kernel import PostgresKernelError
from psycopg import sql
from psycopg.types.json import Jsonb

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import native as native

ACCEPTED = [
    ".agents/skills/gtkb-verify/SKILL.md",
    ".agents/skills/gtkb-verify/helpers/x.py",
    ".agents/skills/new-skill/SKILL.md",
]
REFUSED = [
    ".agents/skills",
    ".agents/hooks/gate.py",
    ".agents/rules/topic.md",
    ".agents/AGENTS.md",
    ".agents/plugins/gtkb/hooks/hooks.json",
    "sub/.agents/skills/gtkb-verify/SKILL.md",
    ".AGENTS/hooks/gate.py",
    ".agents/skills/x/.claude/settings.json",
]
CONTEXT = {"session_context_id": "SENV-agents-skills-targets"}


@pytest.mark.parametrize("path", ACCEPTED)
def test_the_path_rule_accepts_a_file_under_the_shared_skills_tree(path: str) -> None:
    assert _paths([path], "target_paths") == [path]


@pytest.mark.parametrize("path", REFUSED)
def test_the_path_rule_refuses_every_other_agents_path(path: str) -> None:
    with pytest.raises(PostgresKernelError) as refused:
        _paths([path], "target_paths")

    assert refused.value.code == "invalid_bridge_header"


def test_a_proposal_naming_skill_paths_parses() -> None:
    content = authored(
        CONTEXT,
        "skills-proposal",
        1,
        "NEW",
        target_paths=json.dumps(ACCEPTED[:2]),
        test_artifact_targets=json.dumps([ACCEPTED[2]]),
    )

    parsed = parse_authored_message(content)

    assert parsed["status"] == "NEW"
    assert parsed["target_paths"] == ACCEPTED[:2]
    assert parsed["test_artifact_targets"] == [ACCEPTED[2]]


@pytest.mark.parametrize("field", ["target_paths", "test_artifact_targets"])
@pytest.mark.parametrize("path", REFUSED)
def test_a_proposal_naming_another_agents_path_is_refused(field: str, path: str) -> None:
    content = authored(CONTEXT, "skills-proposal", 1, "NEW", **{field: json.dumps([path])})

    with pytest.raises(PostgresKernelError) as refused:
        parse_authored_message(content)

    assert refused.value.code == "invalid_bridge_header"


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_a_tracked_skill_file_goes_through_the_whole_chain(bridge) -> None:
    _service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    skill = ACCEPTED[0]
    (root / skill).parent.mkdir(parents=True)
    (root / skill).write_text("# gtkb-verify\n", encoding="utf-8")
    for arguments in (["add", "--", skill], ["commit", "-qm", "Tracked skill preimage"]):
        subprocess.run(["git", "-C", str(root), *arguments], check=True, capture_output=True)
    document = "skill-chain"
    deliver(client, contexts, document, "pb1", 1, "NEW", target_paths=json.dumps([skill]))
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY")
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": "pb2", "fence": reserved.json()["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])
    assert (checkout / skill).read_text(encoding="utf-8") == "# gtkb-verify\n"
    (checkout / skill).write_text("# gtkb-verify\n\nRevised.\n", encoding="utf-8")

    def check(paths: list[str]):
        return client.post(
            "/v1/bridge/check-effects", json={"native_context_id": "pb2", "cwd": str(checkout), "paths": paths}
        )

    accepted = check([skill])
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["scope"] == "implementation"
    plugin = check([".agents/plugins/gtkb/hooks/hooks.json"])
    assert plugin.status_code == 422, plugin.text
    assert plugin.json()["error"]["code"] == "invalid_effect_path"

    expected = opened.json()["artifact_preimages"]
    published = client.post(f"/v1/bridge/{document}/publish-work", json={**fence, "expected_artifacts": expected})
    assert published.status_code == 200, published.text
    ready = {**fence, "content": authored(contexts["pb2"], document, 3, "READY")}
    delivered = client.post(f"/v1/bridge/{document}/deliver", json=ready)
    assert delivered.status_code == 200, delivered.text
    artifacts = client.get(f"/v1/bridge/{document}/artifacts")
    assert artifacts.status_code == 200, artifacts.text
    assert skill in json.dumps(artifacts.json())
    verified, _ = deliver(
        client, contexts, document, "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts.json())
    )
    assert verified.json()["project_ready_for_commit"] is True
    assert (work_root / skill).read_text(encoding="utf-8") == "# gtkb-verify\n\nRevised.\n"


@pytest.mark.integration
@pytest.mark.timeout(120)
@pytest.mark.parametrize("field", ["proposal_paths", "test_targets"])
def test_a_stored_agents_hooks_target_cannot_reuse_a_live_effect_claim(bridge, field: str) -> None:
    service, client, contexts, _ = bridge
    document = "stored-agents-hooks"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reservation = claim(client, document, "pb2", 2, "READY")
    assert reservation.status_code == 200, reservation.text
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET {}=%s WHERE id=%s").format(
                sql.Identifier(tx.schema), sql.Identifier(field)
            ),
            (Jsonb([".agents/hooks/x.py"]), document),
        )
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    body = {"native_context_id": "pb2", "fence": reservation.json()["fence"]}
    for operation in ["check", "worktree", "publish-work"]:
        request = {**body, "expected_artifacts": {}} if operation == "publish-work" else body
        response = client.post(f"/v1/bridge/{document}/{operation}", json=request)
        assert response.status_code == 422, (operation, response.text)
        assert response.json()["error"]["code"] == "scope_changed"
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
