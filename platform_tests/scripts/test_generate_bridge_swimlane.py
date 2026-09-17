"""Native bridge observations for the dashboard; no lifecycle authority."""

from __future__ import annotations

import copy
import json

import pytest
from groundtruth_kb import dashboard_swimlane as gbs
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

NOW = "2026-09-12T20:00:00+00:00"
HEAD = "2026-09-12T19:50:00+00:00"


def attempt(identity="example", status="NEW", *, disposition="active", claim=None):
    return {
        "id": identity,
        "work_item_id": "WI-1",
        "project_id": "PROJECT-1",
        "head_version": 1 if status else 0,
        "head_status": status,
        "disposition": disposition,
        "created_at": HEAD,
        "closed_at": None if disposition == "active" else NOW,
        "terminal_commit": "a" * 40 if disposition == "committed" else None,
        "head_created_at": HEAD if disposition == "active" and status else None,
        "next_artifact_claim": claim,
    }


def observation(rows=(), *, eligible=(), blocked=()):
    counts = {}
    mix = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
        if row["disposition"] == "active" and row["head_status"]:
            mix[row["head_status"]] = mix.get(row["head_status"], 0) + 1
    queues = {role: {"role": role, "eligible": [], "blocked": []} for role in ("pb", "lo")}
    for key, entries in (("eligible", eligible), ("blocked", blocked)):
        for identity, role in entries:
            queues[role][key].append({"id": identity, "payload": "PRIVATE-QUEUE-PAYLOAD"})
    return {
        "observed_at": NOW,
        "attempts": list(rows),
        "attempt_counts": counts,
        "active_status_mix": [{"status": key, "count": value} for key, value in sorted(mix.items())],
        "unfiled_attempt_count": sum(r["disposition"] == "active" and r["head_status"] is None for r in rows),
        "active_claim_count": sum(r["next_artifact_claim"] is not None for r in rows),
        "queues": queues,
    }


@pytest.fixture
def native_observation(monkeypatch, tmp_path):
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:8765"\n', encoding="utf-8"
    )
    current = {"report": observation(), "calls": []}

    def request(self, method, path, **kwargs):
        current["calls"].append((method, path, kwargs))
        assert (method, path, kwargs) == ("GET", "/v1/bridge/state-report", {})
        if isinstance(current["report"], Exception):
            raise current["report"]
        return copy.deepcopy(current["report"])

    monkeypatch.setattr(AuthorityClient, "request", request)
    return current


def test_generate_swimlane_empty_observation_is_distinct_from_unavailable(tmp_path, native_observation):
    result = gbs.generate_swimlane(tmp_path)
    assert result["status"] == "observed" and result["observed_at"] == NOW
    assert result["threads"] == [] and result["summary"]["thread_count"] == 0
    (tmp_path / "groundtruth.toml").unlink()
    missing = gbs.generate_swimlane(tmp_path)
    assert missing["status"] == "unavailable" and missing["summary"] is None
    assert missing["observed_at"] is None and len(native_observation["calls"]) == 1


def test_native_queue_and_disposition_determine_lanes_without_status_ownership(tmp_path, native_observation):
    rows = [
        attempt("advice", "ADVISORY"),
        attempt("reviewed", "VERIFIED"),
        attempt("recheck", "VERIFIED"),
        attempt("pb", "NOT-READY"),
        attempt("blocked", "READY"),
        attempt("closed", "VERIFIED", disposition="committed"),
        attempt("unfiled", None),
    ]
    native_observation["report"] = observation(
        rows, eligible=[("recheck", "lo"), ("pb", "pb")], blocked=[("blocked", "lo")]
    )
    result = gbs.generate_swimlane(tmp_path)
    by_id = {r["document"]: r for r in result["threads"]}
    assert by_id["advice"]["queue"] is None
    assert by_id["reviewed"]["disposition"] == "active" and by_id["reviewed"]["queue"] is None
    assert by_id["recheck"]["queue"] == {"role": "lo", "state": "eligible"}
    assert by_id["blocked"]["queue"] == {"role": "lo", "state": "blocked"}
    assert by_id["closed"]["disposition"] == "committed" and by_id["closed"]["terminal_commit"] == "a" * 40
    assert result["summary"] == {
        "thread_count": 7,
        "active_count": 6,
        "closed_count": 1,
        "eligible_pb_count": 1,
        "eligible_lo_count": 1,
        "blocked_count": 1,
        "active_claim_count": 0,
        "unfiled_count": 1,
    }
    assert not {
        "advisory_count",
        "no_go_count",
        "actionable_count_for_prime",
        "actionable_count_for_lo",
        "advisory_disposition_count",
        "failed_proposal_count",
    }.intersection(result["summary"])
    assert "PRIVATE-QUEUE-PAYLOAD" not in json.dumps(result)
    assert all("is_terminal" not in row and "awaiting_prime_dialogue" not in row for row in result["threads"])


def test_claim_is_only_the_next_artifact_slot(tmp_path, native_observation):
    claim = {
        "next_version": 2,
        "intended_status": "GO",
        "expires_at": "2026-09-12T20:10:00+00:00",
        "claimant": "PRIVATE-CLAIMANT",
    }
    native_observation["report"] = observation([attempt(claim=claim)])
    result = gbs.generate_swimlane(tmp_path)
    assert result["summary"]["active_claim_count"] == 1
    assert result["threads"][0]["queue"] is None
    assert result["threads"][0]["next_artifact_claim"] == {k: v for k, v in claim.items() if k != "claimant"}
    assert "PRIVATE-CLAIMANT" not in json.dumps(result)


def test_swimlane_uses_database_head_time_and_keeps_purged_time_unknown(tmp_path, native_observation):
    poison = tmp_path / "bridge/obsolete-099.md"
    poison.parent.mkdir()
    poison.write_text("VERIFIED\n")
    native_observation["report"] = observation([attempt(), attempt("withdrawn", "WITHDRAWN", disposition="withdrawn")])
    result = gbs.generate_swimlane(tmp_path)
    by_id = {r["document"]: r for r in result["threads"]}
    assert by_id["example"]["age_in_state_minutes"] == 10
    assert by_id["withdrawn"]["age_in_state_minutes"] is None and by_id["withdrawn"]["head_created_at"] is None
    poison.write_text("NEW\n")
    assert gbs.generate_swimlane(tmp_path) == result
    assert all("latest_filename" not in r and "version_count" not in r for r in result["threads"])


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r.pop("observed_at"),
        lambda r: r.update(observed_at="2026-09-12T20:00:00"),
        lambda r: r.update(active_claim_count=True),
        lambda r: r.update(unfiled_attempt_count=1),
        lambda r: r["attempts"].append(copy.deepcopy(r["attempts"][0])),
        lambda r: r["attempts"][0].update(head_version=True),
        lambda r: r["attempts"][0].update(head_created_at="malformed"),
        lambda r: r["attempts"][0].update(disposition="unknown"),
        lambda r: r["attempt_counts"].update(active=2),
        lambda r: r["queues"]["lo"]["eligible"].append({"id": "missing"}),
        lambda r: r["queues"]["lo"].update(role="pb"),
        lambda r: r["queues"]["pb"]["eligible"].append({"id": "example"}),
        lambda r: r["queues"]["lo"]["eligible"].extend([{"id": "example"}, {"id": "example"}]),
    ],
)
def test_malformed_native_observations_are_unavailable_not_complete_zero(tmp_path, native_observation, change):
    report = observation([attempt()])
    change(report)
    native_observation["report"] = report
    result = gbs.generate_swimlane(tmp_path)
    assert result["status"] == "unavailable" and result["summary"] is None
    assert result["threads"] == [] and result["code"] == "invalid_native_bridge_observation"


def test_unavailable_read_replaces_prior_observation_without_retaining_error_details(tmp_path, native_observation):
    native_observation["report"] = observation([attempt()])
    out = tmp_path / "out.json"
    assert gbs.write_swimlane(tmp_path, out)["status"] == "observed"
    native_observation["report"] = AuthorityClientError("authority_unavailable", "PRIVATE-SERVICE-DETAIL")
    result = gbs.write_swimlane(tmp_path, out)
    assert json.loads(out.read_text()) == result
    assert result["status"] == "unavailable" and result["summary"] is None
    assert "PRIVATE-SERVICE-DETAIL" not in out.read_text()
    native_observation["report"] = AuthorityClientError("invalid_response", "PRIVATE-SERVICE-DETAIL")
    malformed = gbs.write_swimlane(tmp_path, out)
    assert malformed["code"] == "invalid_native_bridge_observation" and malformed["summary"] is None
    assert "PRIVATE-SERVICE-DETAIL" not in out.read_text()


def test_write_swimlane_atomic(tmp_path, native_observation, monkeypatch):
    out = tmp_path / "out.json"
    gbs.write_swimlane(tmp_path, out)
    before = out.read_bytes()

    def boom(*args):
        raise OSError("simulated atomic write failure")

    monkeypatch.setattr(gbs.os, "replace", boom)
    with pytest.raises(OSError):
        gbs.write_swimlane(tmp_path, out)
    assert out.read_bytes() == before


def test_installed_refresh_publishes_unavailable_bridge_observation(tmp_path, monkeypatch):
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    selected = tmp_path / "chosen.toml"
    selected.write_text("[groundtruth]\n", encoding="utf-8")
    result = CliRunner().invoke(main, ["--config", str(selected), "dashboard", "refresh", "--json"])
    assert result.exit_code == 0, result.output
    # A completed refresh is distinct from unavailable native observations.
    assert json.loads(result.output)["status"] == "completed"
    observed = json.loads((tmp_path / ".groundtruth/dashboard/bridge-swimlane.json").read_text())
    assert observed["status"] == "unavailable" and observed["summary"] is None
    assert observed["code"] == "native_authority_not_configured"
    assert observed["threads"] == []
