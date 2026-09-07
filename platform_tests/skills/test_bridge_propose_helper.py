# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Phase 2 of GTKB-DA-READ-SURFACE-CORRECTION.

Coverage matches the test plan in
``bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md``:

1. Glossary-source seeding (the F2 grounding) — deterministic seed extraction.
2. Helper unit test — known-DA-match topic.
3. Empty-section integration test — novel topic.
4. Override flag — opt-out preserves body.
5. S331-replay regression — seed-set membership.
6. Audit log — schema and contents.
7. Parity check — generate_codex_skill_adapters.py --update-registry --check.
8. Template parity — string-presence assertions on scaffold templates.

Tests 9 (Codex review check) is a manual integration test documented in the
implementation report rather than automated, since it requires LO harness
invocation.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py"
CODEX_HELPER_PATH = REPO_ROOT / ".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py"
TEMPLATE_HELPER_PATH = REPO_ROOT / "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py"
TEMPLATE_SKILL_PATH = REPO_ROOT / "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md"
GLOSSARY_PATH = REPO_ROOT / ".claude/rules/canonical-terminology.md"


def _load_helper_module():
    """Load the canonical helper module by file path.

    The helper lives at ``.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py``
    and is not on ``sys.path``. Loading by file path keeps the test independent
    of import-system configuration.
    """
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb/src"))
    spec = importlib.util.spec_from_file_location("bridge_propose_helper_under_test", HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def helper_module():
    return _load_helper_module()


@pytest.fixture(autouse=True)
def _central_writer_unit_boundary(helper_module, monkeypatch):
    monkeypatch.setenv("GTKB_AUTHOR_IDENTITY", "prime-builder/test")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "test-harness")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "fixture-model")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "fixture-version")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "unit-test")
    monkeypatch.setattr(
        helper_module._bridge_writer,
        "run_bridge_compliance_audit",
        lambda **_kwargs: {"decision": "pass"},
    )
    monkeypatch.setattr(
        helper_module,
        "_run_bridge_compliance_audit",
        lambda **_kwargs: {"decision": "pass"},
    )


def _valid_proposal_body() -> str:
    return "\n".join(
        [
            "NEW",
            "Document: passing-topic",
            "Project Authorization: PAUTH-TEST",
            "Project: PROJECT-TEST",
            "Work Item: WI-5409",
            "",
            "## Summary",
            "",
            "Clean bridge body.",
            "",
            "## Specification Links",
            "",
            "- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`",
            "",
            "## Prior Deliberations",
            "",
            "_No prior deliberations: unit test._",
            "",
        ]
    )


# --------------------------------------------------------------------------
# Test 1 — Glossary-source seeding (F2 grounding)
# --------------------------------------------------------------------------

ISOLATION_ANCHOR_IDS = {
    "DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT",
    "DELIB-0877",
    "DELIB-0879",
    "DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS",
}


def test_glossary_seed_ids_for_isolation_includes_anchor_delibs(helper_module):
    """The deterministic seed for topic 'isolation' must include the four
    lifecycle-independence anchor DELIB IDs.

    This is the F2 grounding: the S331 anti-regression no longer depends on
    the ranking behavior of ``KnowledgeDB.search_deliberations``.
    """
    glossary_content = GLOSSARY_PATH.read_text(encoding="utf-8")
    seeds = helper_module._glossary_seed_ids_for_topic("isolation", glossary_content)
    seed_set = set(seeds)
    missing = ISOLATION_ANCHOR_IDS - seed_set
    assert not missing, f"Missing anchor IDs from seed set: {missing}"


def test_glossary_seed_ids_unknown_topic_returns_empty(helper_module):
    """Topic slugs that don't match any glossary heading return an empty seed list."""
    glossary_content = GLOSSARY_PATH.read_text(encoding="utf-8")
    seeds = helper_module._glossary_seed_ids_for_topic(
        "this-slug-deliberately-matches-no-heading-xyz", glossary_content
    )
    assert seeds == []


def test_glossary_seed_ids_empty_glossary_returns_empty(helper_module):
    """Empty glossary content returns an empty seed list (no exception)."""
    seeds = helper_module._glossary_seed_ids_for_topic("isolation", "")
    assert seeds == []


# --------------------------------------------------------------------------
# Test 2 — Helper unit test (known-DA-match topic, semantic search disabled)
# --------------------------------------------------------------------------


def test_pre_populate_isolation_with_db_false(helper_module, tmp_path):
    """Full helper invocation with topic 'isolation' and ``db=False`` (explicit
    semantic-search disable).

    Glossary-source seeding alone produces the four anchor candidates;
    no auto-DB-open is attempted.
    """
    log_path = tmp_path / "audit.json"
    body = "## Summary\n\nTest body.\n\n## Specification Links\n\n- `GOV-FOO-001`\n\n## Prior Deliberations\n\n"
    new_body = helper_module.pre_populate_prior_deliberations(
        "isolation",
        body,
        db=False,  # explicit opt-out from semantic search
        glossary_path=GLOSSARY_PATH,
        log_path=log_path,
    )
    for anchor in ISOLATION_ANCHOR_IDS:
        assert f"`{anchor}`" in new_body, f"Anchor {anchor} missing from populated body"
    assert "<!-- Pre-populated by helper; review and prune. -->" in new_body
    assert log_path.exists()


# --------------------------------------------------------------------------
# Test 3 — Empty-section integration test (novel topic, F2 placeholder)
# --------------------------------------------------------------------------


def test_pre_populate_novel_topic_inserts_placeholder(helper_module, tmp_path):
    """A novel topic with no glossary match and no DB matches must insert the
    ``_No prior deliberations:_`` placeholder so the proposal does not fail
    the LO review-side check (Phase 2 Change 3).

    This is the F2 fix from `-006` NO-GO: the helper must not produce
    proposals that would NO-GO their own review-gate.
    """
    log_path = tmp_path / "audit.json"
    body = "## Summary\n\nNovel topic.\n"
    new_body = helper_module.pre_populate_prior_deliberations(
        "novel-topic-no-glossary-match-zzz",
        body,
        db=False,  # explicit opt-out so we only test the placeholder path
        glossary_path=GLOSSARY_PATH,
        log_path=log_path,
    )
    assert helper_module.NO_PRIOR_DELIBS_PLACEHOLDER in new_body, (
        "Novel topic should insert the empty-justification placeholder."
    )
    assert "## Prior Deliberations" in new_body


# --------------------------------------------------------------------------
# Test 4 — Override flag (opt-out)
# --------------------------------------------------------------------------


def test_propose_bridge_pre_populate_opt_out_preserves_body(helper_module, tmp_path, monkeypatch):
    """pre_populate_prior_deliberations=False on propose_bridge must skip the
    Phase 0 pre-population step entirely.

    Verified by: invoking propose_bridge with the flag False and a body that
    does NOT contain a Specification Links section. The validator (template
    only) would normally catch that; the canonical helper has no validator,
    so the test asserts via patched body inspection: the bridge file's
    content matches the input body modulo the credential scan.
    """
    monkeypatch.setenv("GTKB_SESSION_ID", "test-session-id")
    monkeypatch.setattr(helper_module, "_run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text("# Bridge Index\n\n<!-- comment -->\n\n", encoding="utf-8")

    body = (
        "NEW\n\n# Test Proposal\n\n"
        "## Summary\n\nNo pre-population.\n\n"
        "## Specification Links\n\n- `GOV-FOO-001`\n\n"
        "## Prior Deliberations\n\n_No prior deliberations: opt-out test._\n"
    )

    out = helper_module.propose_bridge(
        "isolation",  # would normally seed
        body,
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    written = out.read_text(encoding="utf-8")
    # The four anchor IDs must NOT be present (pre-population was skipped).
    for anchor in ISOLATION_ANCHOR_IDS:
        assert f"`{anchor}`" not in written, (
            f"Opt-out failed: anchor {anchor} was seeded despite pre_populate_prior_deliberations=False"
        )
    # The opt-out justification line should still be present.
    assert "_No prior deliberations: opt-out test._" in written


def test_propose_bridge_compliance_denial_precedes_claim_and_write(helper_module, tmp_path, monkeypatch):
    """Compliance denial must create no file and acquire no work intent."""
    bridge_dir = tmp_path / "bridge"
    bridge_file = bridge_dir / "denied-topic-001.md"
    events: list[str] = []

    def deny(**_kwargs):
        events.append("audit")
        assert _kwargs["content"].startswith("NEW\n::init gtkb pb\n::open build\n")
        raise helper_module.BridgeComplianceError("project/work-item mismatch")

    def fail_acquire(*_args, **_kwargs):  # pragma: no cover - assertion helper
        raise AssertionError("work-intent acquisition must not run after compliance denial")

    monkeypatch.setenv("GTKB_SESSION_ID", "session-denied")
    monkeypatch.setattr(helper_module, "_run_bridge_compliance_audit", deny)
    monkeypatch.setattr(helper_module, "_acquire_bridge_work_intent", fail_acquire)

    with pytest.raises(helper_module.BridgeComplianceError, match="project/work-item mismatch"):
        helper_module.propose_bridge(
            "denied-topic",
            _valid_proposal_body(),
            bridge_dir=bridge_dir,
            pre_populate_prior_deliberations=False,
        )

    assert events == ["audit"]
    assert not bridge_file.exists()
    assert not bridge_dir.exists()


def test_propose_bridge_compliance_pass_keeps_single_claim_write_release(helper_module, tmp_path, monkeypatch):
    """A passing proposal still writes once after one claim lifecycle."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    events: list[str] = []
    registry = object()

    def pass_audit(**_kwargs):
        events.append("audit")
        assert _kwargs["content"].startswith("NEW\n::init gtkb pb\n::open build\n")
        return {"decision": "pass"}

    def acquire(thread_slug, session_id, *, project_root):
        assert events == ["audit"]
        assert thread_slug == "passing-topic"
        assert session_id == "session-pass"
        assert project_root == tmp_path.resolve()
        events.append("acquire")
        return registry

    def release(project_root, thread_slug, session_id, *, claim_registry=None):
        assert claim_registry is registry
        assert thread_slug == "passing-topic"
        assert session_id == "session-pass"
        assert project_root == tmp_path.resolve()
        events.append("release")

    monkeypatch.setenv("GTKB_SESSION_ID", "session-pass")
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", "session-pass")
    monkeypatch.setattr(helper_module, "_run_bridge_compliance_audit", pass_audit)
    monkeypatch.setattr(helper_module, "resolve_work_intent_session_id", lambda: "session-pass")
    monkeypatch.setattr(helper_module, "_acquire_bridge_work_intent", acquire)
    monkeypatch.setattr(helper_module._bridge_writer, "_release_claim", release)

    out = helper_module.propose_bridge(
        "passing-topic",
        _valid_proposal_body(),
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    assert events == ["audit", "acquire", "release"]
    assert out == bridge_dir / "passing-topic-001.md"
    assert out.read_text(encoding="utf-8").startswith("NEW\n::init gtkb pb\n::open build\n")


# --------------------------------------------------------------------------
# Test 5 — S331-replay regression (seed-set membership)
# --------------------------------------------------------------------------


def test_s331_replay_regression(helper_module):
    """The S331 wrong-frame failure (agent evaluating 'isolation' without
    consulting the DA's four anchor deliberations) is structurally prevented
    by glossary-source seeding.

    With this helper enabled, authoring a proposal on the topic 'isolation'
    deterministically surfaces the four anchor DELIB IDs from the Phase 1
    glossary entry's Source: block — regardless of semantic-search ranking.
    """
    glossary_content = GLOSSARY_PATH.read_text(encoding="utf-8")
    seeds = helper_module._glossary_seed_ids_for_topic("isolation", glossary_content)
    seed_set = set(seeds)
    # Every anchor record must be in the seed set. This is the structural
    # anti-regression for the S331 failure case.
    for anchor in ISOLATION_ANCHOR_IDS:
        assert anchor in seed_set, (
            f"S331 anti-regression FAILED: {anchor} not in seeds for 'isolation'. Found seeds: {seeds}"
        )


# --------------------------------------------------------------------------
# Test 6 — Audit log
# --------------------------------------------------------------------------


def test_audit_log_schema(helper_module, tmp_path):
    """The audit log file is written with the expected schema."""
    log_path = tmp_path / "audit-log.json"
    body = "## Summary\n\nx\n\n## Specification Links\n\n- `GOV-FOO-001`\n\n## Prior Deliberations\n\n"
    helper_module.pre_populate_prior_deliberations(
        "isolation",
        body,
        db=False,
        glossary_path=GLOSSARY_PATH,
        log_path=log_path,
    )
    assert log_path.exists()
    log_data = json.loads(log_path.read_text(encoding="utf-8"))
    expected_keys = {
        "timestamp",
        "topic_slug",
        "query",
        "glossary_path",
        "glossary_seed_ids",
        "search_result_ids",
        "semantic_search_attempted",
        "limit",
        "threshold",
        "candidate_count",
    }
    missing_keys = expected_keys - set(log_data)
    assert not missing_keys, f"Audit log missing keys: {missing_keys}"
    assert log_data["topic_slug"] == "isolation"
    assert log_data["candidate_count"] >= 4  # at least the four anchors
    assert log_data["semantic_search_attempted"] is False  # db=False explicit


# --------------------------------------------------------------------------
# Tests 7-9 — Explicit semantic-search opt-in behavior (F1 of -006 fix)
# --------------------------------------------------------------------------


class _FakeKnowledgeDB:
    """Minimal fake DB exposing ``search_deliberations`` for the F1 tests."""

    def __init__(self, results: list[dict]):
        self._results = results
        self.calls: list[tuple[str, int]] = []

    def search_deliberations(self, query: str, *, limit: int = 5):
        self.calls.append((query, limit))
        return self._results


def test_explicit_db_instance_invokes_semantic_search(helper_module, tmp_path):
    """An explicit DB instance opts into semantic search and calls
    ``search_deliberations``."""
    fake_results = [
        {"id": "DELIB-FAKE-100", "source_type": "owner_conversation", "title": "Fake match A"},
        {"id": "DELIB-FAKE-101", "source_type": "owner_conversation", "title": "Fake match B"},
    ]
    fake_db = _FakeKnowledgeDB(fake_results)

    body = "## Summary\n\nx\n\n## Specification Links\n\n- `GOV-FOO-001`\n\n## Prior Deliberations\n\n"
    new_body = helper_module.pre_populate_prior_deliberations(
        "isolation",
        body,
        db=fake_db,  # explicit DB to verify the semantic-search call path
        glossary_path=GLOSSARY_PATH,
        log_path=tmp_path / "log.json",
    )
    # The fake DB's search_deliberations was called once.
    assert len(fake_db.calls) == 1, f"Expected 1 search call, got {len(fake_db.calls)}"
    assert fake_db.calls[0][0] == "isolation"  # query is the topic with hyphens replaced
    # Both fake results appear in the populated body.
    assert "DELIB-FAKE-100" in new_body
    assert "DELIB-FAKE-101" in new_body
    # And the four glossary-seed anchors are present too.
    for anchor in ISOLATION_ANCHOR_IDS:
        assert f"`{anchor}`" in new_body


def test_search_only_candidates_inserted_when_no_glossary_heading(helper_module, tmp_path):
    """When the topic has no glossary heading, search candidates are still
    inserted (search-only path)."""
    fake_results = [
        {"id": "DELIB-FAKE-200", "source_type": "owner_conversation", "title": "Search-only A"},
    ]
    fake_db = _FakeKnowledgeDB(fake_results)
    body = "## Summary\n\nx\n\n## Specification Links\n\n- `GOV-FOO-001`\n\n## Prior Deliberations\n\n"
    new_body = helper_module.pre_populate_prior_deliberations(
        "no-glossary-heading-for-this-topic-zzz",
        body,
        db=fake_db,
        glossary_path=GLOSSARY_PATH,
        log_path=tmp_path / "log.json",
    )
    assert "DELIB-FAKE-200" in new_body, "Search-only candidate missing from body"


def test_seeds_and_search_combined_and_deduplicated(helper_module, tmp_path):
    """Seeds and search results are combined; duplicates are removed
    (search results that are already in the seed set don't appear twice)."""
    # Fake DB returns one of the known anchor IDs (would dedupe) and one new ID.
    fake_results = [
        {
            "id": "DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT",
            "source_type": "owner_conversation",
            "title": "Dup of seed",
        },
        {"id": "DELIB-FAKE-300", "source_type": "owner_conversation", "title": "Search-only new"},
    ]
    fake_db = _FakeKnowledgeDB(fake_results)
    body = "## Summary\n\nx\n\n## Specification Links\n\n- `GOV-FOO-001`\n\n## Prior Deliberations\n\n"
    new_body = helper_module.pre_populate_prior_deliberations(
        "isolation",
        body,
        db=fake_db,
        glossary_path=GLOSSARY_PATH,
        log_path=tmp_path / "log.json",
    )
    # The duplicate ID appears only once (from the glossary seed).
    occurrences = new_body.count("`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`")
    assert occurrences == 1, f"Duplicate seed/search ID should appear once; got {occurrences}"
    # The new search-only ID is present.
    assert "DELIB-FAKE-300" in new_body


# --------------------------------------------------------------------------
# Test 7 — Adapter-generation parity check
# --------------------------------------------------------------------------


def test_codex_skill_adapter_parity_check():
    """The Codex bridge-propose helper projection must match the canonical helper."""
    assert CODEX_HELPER_PATH.read_bytes() == HELPER_PATH.read_bytes()


# --------------------------------------------------------------------------
# Test 8 — Template parity (scaffold templates contain the new function/section)
# --------------------------------------------------------------------------


def test_template_helper_contains_new_function():
    """Scaffold template helper must contain the new pre_populate function."""
    content = TEMPLATE_HELPER_PATH.read_text(encoding="utf-8")
    assert "def pre_populate_prior_deliberations(" in content
    assert "_glossary_seed_ids_for_topic" in content
    assert "DEFAULT_GLOSSARY_PATH" in content


def test_template_skill_md_contains_pre_population_section():
    """Scaffold template SKILL.md must document the pre-population behavior."""
    content = TEMPLATE_SKILL_PATH.read_text(encoding="utf-8")
    assert "Prior Deliberations pre-population" in content or (
        "Phase 0a" in content and "pre-population" in content.lower()
    )
    assert "glossary-source seeding" in content.lower() or "Glossary-source seeding" in content
    assert "default-on" not in content
    assert "automatically and queries" not in content
    assert "``db=False`` to disable semantic search entirely" not in content
    assert "``db=None`` skips" in content
    assert "``db=True``" in content
    assert "explicit DB instance" in content


# --------------------------------------------------------------------------
# WI-4565: semantic search is opt-in (db=None/False skip; db=True opts in) and
# the default-store open is timeout-bounded so opt-in can never hang.
# --------------------------------------------------------------------------


def _prior_deliberations_module():
    from groundtruth_kb.bridge import prior_deliberations as pd

    return pd


def test_wi4565_db_none_default_skips_open_and_search():
    """db=None (default) must NOT open the default DB nor run semantic search."""
    pd = _prior_deliberations_module()
    orig = pd._try_open_default_db

    def boom():
        raise AssertionError("_try_open_default_db must not be called when db=None")

    pd._try_open_default_db = boom
    try:
        body = "## Prior Deliberations\n\n_placeholder._\n"
        out = pd.pre_populate_prior_deliberations("wi4565-opt-in-topic", body, db=None, log_path=False)
    finally:
        pd._try_open_default_db = orig
    assert "## Prior Deliberations" in out


def test_wi4565_db_false_still_disables_search():
    """db=False keeps disabling semantic search (unchanged explicit-disable contract)."""
    pd = _prior_deliberations_module()
    orig = pd._try_open_default_db

    def boom():
        raise AssertionError("_try_open_default_db must not be called when db=False")

    pd._try_open_default_db = boom
    try:
        body = "## Prior Deliberations\n\n_placeholder._\n"
        out = pd.pre_populate_prior_deliberations("wi4565-opt-in-topic", body, db=False, log_path=False)
    finally:
        pd._try_open_default_db = orig
    assert "## Prior Deliberations" in out


def test_wi4565_db_true_opts_in_to_default_store_search():
    """db=True opts in to the bounded default-store semantic search."""
    pd = _prior_deliberations_module()

    class _Fake:
        def __init__(self):
            self.calls = 0

        def search_deliberations(self, query, *, limit=5):
            self.calls += 1
            return [{"id": "DELIB-WI4565-FAKE", "title": "Fake", "score": 0.9}]

    fake = _Fake()
    orig = pd._try_open_default_db
    pd._try_open_default_db = lambda: fake
    try:
        body = "## Prior Deliberations\n\n_placeholder._\n"
        out = pd.pre_populate_prior_deliberations("wi4565-opt-in-topic", body, db=True, log_path=False)
    finally:
        pd._try_open_default_db = orig
    assert fake.calls == 1
    assert "DELIB-WI4565-FAKE" in out


def test_wi4565_open_db_bounded_by_timeout(monkeypatch):
    """_try_open_default_db is timeout-bounded; a hanging construction degrades to None."""
    import time

    import groundtruth_kb.db as dbmod

    pd = _prior_deliberations_module()
    monkeypatch.setattr(pd, "_OPEN_DB_TIMEOUT_SECONDS", 0.2)

    def slow_ctor(_path):
        time.sleep(3.0)
        return object()

    monkeypatch.setattr(dbmod, "KnowledgeDB", slow_ctor)
    assert pd._try_open_default_db() is None


def test_wi4565_db_param_docstring_matches_skip_behavior(helper_module):
    """write_bridge.py propose_bridge db-param docstring states the None-skips
    contract that the WI-4565 code fix now honors. (The db=True opt-in doc
    enhancement + .codex adapter regen are deferred to WI-4716 to avoid an
    out-of-scope generated-adapter rewrite.)"""
    doc = helper_module.propose_bridge.__doc__ or ""
    assert "skips semantic search" in doc


# --------------------------------------------------------------------------
# WI-5767 C3 — direct helper usage contract (CLI surface)
# --------------------------------------------------------------------------


def _run_helper_cli(*argv: str) -> tuple[int, str, str]:
    """Run the helper module as a script and return (rc, stdout, stderr)."""
    import subprocess

    r = subprocess.run(
        [sys.executable, str(HELPER_PATH), *argv],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return r.returncode, r.stdout, r.stderr


def test_wi5767_helper_cli_help_exits_zero_stdout():
    """--help writes usage to stdout and exits 0."""
    rc, stdout, stderr = _run_helper_cli("--help")
    assert rc == 0
    assert stdout.strip(), "usage must be written to stdout"
    assert "propose_bridge(" in stdout
    assert "BridgeFileAlreadyExistsError" in stdout
    assert stderr.strip() == ""


def test_wi5767_helper_cli_bare_invocation_exits_two_stderr():
    """Bare/direct invocation writes usage to stderr and exits 2."""
    rc, stdout, stderr = _run_helper_cli()
    assert rc == 2
    assert stdout.strip() == ""
    assert stderr.strip(), "usage must be written to stderr"


def test_wi5767_helper_import_is_silent(helper_module):
    """Importing the module must not print to stdout (import silence)."""
    import contextlib
    import io as _io

    buf = _io.StringIO()
    with contextlib.redirect_stdout(buf):
        _load_helper_module()
    assert buf.getvalue().strip() == ""


def test_wi5767_helper_codex_parity():
    """The generated Codex helper copy is byte-identical to the canonical Claude helper."""
    a = HELPER_PATH.read_bytes()
    b = CODEX_HELPER_PATH.read_bytes()
    assert a == b, "Codex helper copy must match the canonical Claude helper bytes"


# --- WI-6538: the propose helper must not reorder an authored head ---


def test_propose_helper_does_not_reorder_complete_authored_head() -> None:
    """The helper head-normalization binding preserves a complete authored head.

    The helper calls normalize_bridge_envelope_head before compose/write. With the
    WI-6538 writer contract in force that call is a no-op for a complete head, so an
    authored non-canonical order reaches disk unchanged. Asserted through the helper
    own binding rather than the writer module, so the test fails if the helper is
    ever repointed at a rewriting implementation.
    """
    import importlib.util
    import sys
    from pathlib import Path as _Path

    newline = chr(10)
    repo_root = _Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    helper_path = repo_root / "scripts" / "skill-helpers" / "gtkb-bridge-propose" / "write_bridge.py"
    spec = importlib.util.spec_from_file_location("wi6538_write_bridge", helper_path)
    assert spec is not None and spec.loader is not None
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

    authored = newline.join(["::init gtkb lo", "::open build", "NEW", "", "Document: gtkb-x", "body", ""])
    assert helper.normalize_bridge_envelope_head(authored) == authored
