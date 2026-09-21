"""Close/wrap behavioral contract (SPEC-0266/0452/0512/0657 v2, SPEC-DA-MECHANICAL-ENFORCE v2,
SPEC-DA-HARVEST-INCLUSION v2, DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001 v2; TEST-11753, TEST-12147, TEST-12212).

The gtkb-session-wrap procedure is composed against a disposable PostgreSQL
authority served in its own process, with every agent step run as a separate
``gt`` CLI process: resolve the binding, read the assignment (wrap-scan reads
only), harvest through the supported version-checked writers with readback and a
visible stale refusal, author an ADVISORY with exact attribution, release the
held artifact claim, tear down exactly the own scratch directory, and hand over
to a fresh context that reconstructs the assignment from canonical state and
obtains its own claim. Nothing commits, pushes, archives or persists a prompt;
the immutable bindings and another context's claim survive; foreign scratch is
refused. No session-end hook exists in the baseline manifest; the teardown verb
is explicit and the guidance says so. Actual-host lifecycle behavior remains a
separate qualification.
"""

from __future__ import annotations

import hashlib
import json
import re
import socket
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from uuid import uuid4

import click
import pytest
from groundtruth_kb.cli import main as cli_root
from groundtruth_kb.postgres_kernel import TABLE_SPECS
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, history_count
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".harness-baseline-configuration"
# D15: the one skills source; the baseline directory holds rules and hooks only.
WRAP_SKILL = ROOT / ".agents/skills/gtkb-session-wrap"
FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)
EXCLUDED = ("scratchpad/", ".worktrees/", ".git/", "server.toml", "client.toml", "service.log")
PERSISTED_CONTINUATION = re.compile(r"prompt|handoff|archive|transcript|wrap", re.I)


def _tree(root: Path) -> dict[str, str]:
    files = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_file() and not relative.startswith(EXCLUDED):
            files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def _refs(repo: Path) -> tuple[str, str]:
    return _git(repo, "rev-parse", "HEAD").strip(), _git(repo, "for-each-ref")


def _claims(service, document: str) -> list[dict]:
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL(
                "SELECT attempt_id,claimant_session_context_id,fence,intended_status FROM {}.work_intent_claims "
                "WHERE attempt_id=%s ORDER BY fence"
            ).format(sql.Identifier(tx.schema)),
            (document,),
        )
        return [dict(row) for row in tx.cursor.fetchall()]


def _tables(service) -> set[str]:
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s", (tx.schema,))
        return {row["table_name"] for row in tx.cursor.fetchall()}


def _commands(group: click.Group, prefix: str = "gt") -> set[str]:
    names = set()
    for name in group.list_commands(click.Context(group)):
        command = group.get_command(click.Context(group), name)
        if isinstance(command, click.Group):
            names |= _commands(command, f"{prefix} {name}")
        else:
            names.add(f"{prefix} {name}")
    return names


def test_explicit_close_wrap_harvests_releases_tears_down_and_hands_over_cleanly(bridge, tmp_path_factory):
    service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    inputs = tmp_path_factory.mktemp("wrap-inputs")
    own_context, other_context = "pb2", "lo3"
    own = root / "scratchpad" / contexts[own_context]["session_context_id"]
    foreign = root / "scratchpad" / contexts["lo1"]["session_context_id"]

    # Assigned work: NEW (pb1) -> GO (lo1) -> pb2 holds the READY claim and its registered checkout.
    document, other_document = "effect-doc", "other-doc"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, own_context, 2, "READY").json()
    fence = {"native_context_id": own_context, "fence": reserved["fence"]}
    checkout = Path(client.post(f"/v1/bridge/{document}/worktree", json=fence).json()["path"])
    # Another context's live claim on another attempt (its own advisory) must survive this context's wrap.
    assert claim(client, other_document, other_context, 0, "ADVISORY", work_item_id=None).status_code == 200
    other_claims = _claims(service, other_document)
    assert len(other_claims) == 1
    assert other_claims[0]["claimant_session_context_id"] == contexts[other_context]["session_context_id"]
    # Own scratch (through the scratch scope), a sibling's scratch and an unrelated file.
    scratch_check = client.post(
        "/v1/bridge/check-effects",
        json={"native_context_id": own_context, "cwd": str(root), "paths": [str(own / "notes.md")]},
    )
    assert scratch_check.status_code == 200 and scratch_check.json()["scope"] == "scratch"
    own.mkdir(parents=True)
    (own / "notes.md").write_text("disposable working notes", encoding="utf-8")
    (own / "drafts").mkdir()
    (own / "drafts" / "a.md").write_text("draft", encoding="utf-8")
    (foreign / "kept").mkdir(parents=True)
    (foreign / "kept" / "other.md").write_text("another context's work", encoding="utf-8")
    (root / "scratchpad" / "unrelated.txt").write_text("not a context directory", encoding="utf-8")
    # A large dirty registered checkout: wrap reads stay bounded and touch none of it.
    for index in range(400):
        (checkout / f"dirty-{index:03d}.txt").write_text(f"untracked {index}\n", encoding="utf-8")
    dirty_before = _git(checkout, "status", "--porcelain")
    assert dirty_before.count("\n") == 400

    bindings_before = {
        name: client.get("/v1/sessions/binding", params={"native_context_id": name}).json() for name in contexts
    }
    tables_before = _tables(service)
    tree_before = _tree(root)
    refs_before = _refs(root), _refs(checkout)
    history_before = history_count(service)

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    sentinel = inputs / "must-not-open.db"
    sentinel.write_bytes(b"SQLite is not a fallback authority for close or wrap.")
    client_config = inputs / "client.toml"
    client_config.write_text(
        f'[groundtruth]\nauthority_url="{url}"\ndb_path="{sentinel.as_posix()}"\nproject_root="{root.as_posix()}"\n',
        encoding="utf-8",
    )
    process, server_env = _serve_authority(root, port)
    # Ambient identity noise: a foreign context id, a role-bearing identity and a harness name. The CLI
    # resolves only the explicitly supplied native context; none of these becomes a fallback.
    client_env = {key: value for key, value in server_env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    client_env.pop("GT_AUTHORITY_URL", None)
    client_env.update(
        GT_PROJECT_ROOT=str(root),
        GT_DB_PATH=str(sentinel),
        PYTHONIOENCODING="utf-8",
        GTKB_NATIVE_CONTEXT_ID="lo1",
        GTKB_AUTHOR_SESSION_CONTEXT_ID=contexts["lo1"]["session_context_id"],
        GTKB_AUTHOR_IDENTITY="loyal-opposition/codex/B",
        GTKB_HARNESS_NAME="codex",
        GTKB_SESSION_ID="stale-marker",
    )

    def cli(*arguments: str, timeout: float = 30.0) -> subprocess.CompletedProcess:
        started = time.monotonic()
        completed = subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config), *arguments],
            cwd=str(inputs),
            env=client_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            creationflags=FLAGS,
        )
        assert time.monotonic() - started < timeout
        return completed

    def ok(*arguments: str):
        completed = cli(*arguments, "--json")
        assert completed.returncode == 0, (arguments, completed.stdout, completed.stderr)
        return json.loads(completed.stdout)

    def refused(*arguments: str, code: str) -> subprocess.CompletedProcess:
        completed = cli(*arguments, "--json")
        assert completed.returncode == 1, (arguments, completed.stdout, completed.stderr)
        assert code in completed.stderr and completed.stdout == ""
        return completed

    try:
        # 1. Resolve the immutable binding for exactly this context (no fallback to the ambient noise).
        binding = ok("session", "show", "--native-context-id", own_context)
        assert binding == bindings_before[own_context]
        assert binding["role"] == "prime-builder" and binding["subject"] == "gtkb"
        assert ok("session", "show", "--native-context-id", "lo1")["role"] == "loyal-opposition"
        refused("session", "show", "--native-context-id", "never-bound", code="no_session_binding")

        # 2. Wrap-scan: read the assignment, the exact dispatched action and Git state. Reads only.
        context = ok("context", "work-item", "WI-1")
        assert context["work_item"]["id"] == "WI-1" and context["project"]["id"] == "PROJECT-1"
        assert {record["id"] for record in context["specifications"]} >= {"SPEC-1"}
        shown = ok("bridge", "show", document, "--content")
        assert shown["attempt"]["head_version"] == 2 and shown["messages"][-1]["status"] == "GO"
        assert shown["messages"][-1]["author_session_context_id"] == contexts["lo1"]["session_context_id"]
        report = ok("bridge", "state-report")
        observed = {row["id"]: row for row in report["attempts"]}
        assert observed[document]["next_artifact_claim"]["intended_status"] == "READY"
        assert observed[other_document]["next_artifact_claim"]["intended_status"] == "ADVISORY"
        assert (
            cli(
                "bridge",
                "check",
                document,
                "--native-context-id",
                own_context,
                "--fence",
                str(reserved["fence"]),
                "--json",
            ).returncode
            == 0
        )
        # A write outside the own scratch (another context's scratch) is refused while the claim is live.
        refused(
            "bridge",
            "check-effects",
            "--native-context-id",
            own_context,
            "--cwd",
            str(root),
            "--path",
            str(foreign / "kept" / "other.md"),
            code="effect_outside_checkout",
        )
        assert _git(checkout, "status", "--porcelain") == dirty_before
        assert history_count(service) == history_before
        assert _tree(root) == tree_before
        assert own.is_dir() and (own / "notes.md").read_text(encoding="utf-8") == "disposable working notes"

        # 3. Harvest an enduring finding through the supported writer, with readback.
        finding = inputs / "finding.json"
        finding.write_text(
            json.dumps(
                {"title": "Wrap finding", "description": "Observed during the authorized work", "status": "active"}
            ),
            encoding="utf-8",
        )
        actor = binding["session_context_id"]
        written = ok(
            "spec",
            "record",
            "--id",
            "SPEC-WRAP-FINDING",
            "--fields-file",
            str(finding),
            "--expected-version",
            "0",
            "--actor",
            actor,
            "--change-reason",
            "Explicit wrap harvest",
        )
        assert written["version"] == 1 and written["changed_by"] == actor
        readback = ok("spec", "show", "SPEC-WRAP-FINDING")
        assert readback["version"] == 1 and readback["title"] == "Wrap finding"
        assert history_count(service) == history_before + 1
        # A stale-version write is a visible typed refusal, never a silent success or a partial write.
        refused(
            "spec",
            "record",
            "--id",
            "SPEC-WRAP-FINDING",
            "--fields-file",
            str(finding),
            "--expected-version",
            "0",
            "--actor",
            actor,
            "--change-reason",
            "Repeated harvest",
            code="cas_conflict",
        )
        malformed = inputs / "malformed.json"
        malformed.write_text("not json", encoding="utf-8")
        assert (
            cli(
                "spec",
                "record",
                "--id",
                "SPEC-WRAP-FINDING",
                "--fields-file",
                str(malformed),
                "--expected-version",
                "1",
                "--actor",
                actor,
                "--change-reason",
                "Malformed harvest",
                "--json",
            ).returncode
            == 1
        )
        assert ok("spec", "show", "SPEC-WRAP-FINDING")["version"] == 1
        assert history_count(service) == history_before + 1

        # 4. An ADVISORY authored by this context: exact attribution, no dispatch envelope; a message that names
        #    another context's binding as its author is refused and nothing is delivered.
        advisory = "wrap-advisory"
        advisory_claim = ok(
            "bridge",
            "claim",
            advisory,
            "--native-context-id",
            own_context,
            "--expected-version",
            "0",
            "--status",
            "ADVISORY",
            "--request-id",
            str(uuid4()),
        )
        content = authored(contexts[own_context], advisory, 1, "ADVISORY")
        content = content.replace("Project: PROJECT-1\r\n", "").replace("Work Item: WI-1\r\n", "")
        assert not content.startswith("::init") and "::open" not in content
        foreign_author = content.replace(
            contexts[own_context]["session_context_id"], contexts["lo1"]["session_context_id"]
        )
        (inputs / "foreign.md").write_text(foreign_author, encoding="utf-8", newline="")
        refused(
            "bridge",
            "deliver",
            advisory,
            "--native-context-id",
            own_context,
            "--fence",
            str(advisory_claim["fence"]),
            "--content-file",
            str(inputs / "foreign.md"),
            code="author_context_mismatch",
        )
        assert ok("bridge", "show", advisory, "--content")["messages"] == []
        (inputs / "advisory.md").write_text(content, encoding="utf-8", newline="")
        delivered = ok(
            "bridge",
            "deliver",
            advisory,
            "--native-context-id",
            own_context,
            "--fence",
            str(advisory_claim["fence"]),
            "--content-file",
            str(inputs / "advisory.md"),
        )
        assert delivered["status"] == "delivered"
        messages = ok("bridge", "show", advisory, "--content")["messages"]
        assert messages[-1]["content"] == content
        assert messages[-1]["author_session_context_id"] == contexts[own_context]["session_context_id"]

        # 5. Release the held artifact action and read it back; the released claim cannot be reused.
        released = ok(
            "bridge", "release", document, "--native-context-id", own_context, "--fence", str(reserved["fence"])
        )
        assert released == {"status": "released", "document": document, "fence": reserved["fence"]}
        refused(
            "bridge",
            "release",
            document,
            "--native-context-id",
            own_context,
            "--fence",
            str(reserved["fence"]),
            code="stale_artifact_fence",
        )
        assert _claims(service, document) == []
        assert ok("bridge", "show", document)["attempt"]["head_version"] == 2

        # 6. The own scratch is torn down exactly, through the explicit verb; no path can name a foreign one.
        teardown = ok("session", "scratch-teardown", "--native-context-id", own_context)
        assert teardown["status"] == "removed" and teardown["surviving"] == []
        assert {entry["path"] for entry in teardown["removed"]} == {"notes.md", "drafts/a.md", "drafts", "."}
        assert not own.exists()
        assert (foreign / "kept" / "other.md").read_text(encoding="utf-8") == "another context's work"
        assert (root / "scratchpad" / "unrelated.txt").is_file()
        assert ok("session", "scratch-teardown", "--native-context-id", own_context)["status"] == "absent"
        refused("session", "scratch-teardown", "--native-context-id", "never-bound", code="no_session_binding")
        assert (foreign / "kept" / "other.md").is_file()

        # 7. Nothing was committed, pushed, archived or persisted for continuation.
        assert (_refs(root), _refs(checkout)) == refs_before
        assert _git(checkout, "status", "--porcelain") == dirty_before
        assert _tree(root) == tree_before
        assert _tables(service) == tables_before
        assert not any(PERSISTED_CONTINUATION.search(name) for name in tables_before), tables_before
        assert history_count(service) == history_before + 1
        assert _claims(service, other_document) == other_claims
        for name in contexts:
            assert (
                client.get("/v1/sessions/binding", params={"native_context_id": name}).json() == bindings_before[name]
            )

        # 8. A fresh receiving context reconstructs the assignment from canonical reads and takes its own claim;
        #    it inherits neither the earlier context's binding, scratch nor claim, and starts with a clean scratch.
        successor = "pb-successor"
        bound = ok("session", "bind", "--native-context-id", successor, "--init-keyword", "::init gtkb pb")
        assert bound["status"] == "init_requested"
        successor_binding = bound["binding"]
        assert successor_binding["session_context_id"] != binding["session_context_id"]
        assert ok("session", "show", "--native-context-id", successor) == successor_binding
        assert ok("session", "show", "--native-context-id", own_context) == binding
        assert not (root / "scratchpad" / successor_binding["session_context_id"]).exists()
        assert ok("session", "scratch-teardown", "--native-context-id", successor)["status"] == "absent"
        rebuilt = ok("context", "work-item", "WI-1")
        assert rebuilt["work_item"]["id"] == "WI-1"
        assert ok("bridge", "show", document, "--content")["messages"][-1]["status"] == "GO"
        successor_claim = ok(
            "bridge",
            "claim",
            document,
            "--work-item-id",
            "WI-1",
            "--native-context-id",
            successor,
            "--expected-version",
            "2",
            "--status",
            "READY",
            "--request-id",
            str(uuid4()),
        )
        assert successor_claim["fence"] != reserved["fence"]
        assert [row["claimant_session_context_id"] for row in _claims(service, document)] == [
            successor_binding["session_context_id"]
        ]
        assert _claims(service, other_document) == other_claims
    finally:
        process.terminate()
        process.wait(timeout=30)


def test_wrap_guidance_cites_available_commands_and_discloses_the_missing_session_end_hook() -> None:
    """The authored procedure names only commands the CLI has; no session-end hook is declared or claimed."""
    available = _commands(cli_root)
    for relative in ("SKILL.md", "references/audit-checklist.md", "references/handoff-template.md"):
        text = (WRAP_SKILL / relative).read_text(encoding="utf-8")
        cited = {
            "gt " + " ".join(match.split()[1:3]).strip("`.,;:")
            for match in re.findall(r"`gt [a-z-]+(?: [a-z-]+)?", text)
        }
        for command in cited:
            if command in {"gt context", "gt bridge", "gt session"}:
                continue
            assert command in available, (relative, command)
    skill = (WRAP_SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "gt session scratch-teardown --native-context-id" in skill
    assert "No session-end hook runs the" in skill
    assert "never implicitly stage, commit, push, publish" in skill
    manifest = tomllib.loads((BASELINE / "hooks/manifest.toml").read_text(encoding="utf-8"))
    events = {hook["event"] for hook in manifest["hook"]}
    assert events == {"pre_tool_use"}, events
    assert not any(event in {"session_end", "stop", "turn_end", "session_stop"} for event in events)
    rule = (BASELINE / "rules/session-bootstrap.md").read_text(encoding="utf-8")
    assert "gt session scratch-teardown" in rule and "No session-end hook performs the" in rule


def test_no_persisted_continuation_route_exists_in_the_cli_or_the_schema(native) -> None:
    """Persisted prompt, handoff and archive consumers are absent: the CLI has no such verb; the schema no table."""
    service, _client, _schema, _service_name = native
    tables = _tables(service)
    assert set(TABLE_SPECS) <= tables
    assert not any(PERSISTED_CONTINUATION.search(name) for name in tables | set(TABLE_SPECS)), tables
    commands = _commands(cli_root)
    assert {"gt session bind", "gt session show", "gt session scratch-teardown"} <= commands
    assert not any(
        any(token in command for token in ("handoff", "prompt", "archive", "wrap")) for command in commands
    ), commands
