"""Doctor coverage for application_scope/path alignment over the native specification and test pages.

Owner ruling D31 (2026-09-19): ``_check_application_scope_alignment`` reads ``GET /v1/specifications``
and ``GET /v1/tests`` (limit 1000, cursor ``after``) through the configured ``AuthorityClient`` and
never opens a local store. The pages are served from dicts by monkeypatching
``AuthorityClient.request`` (the ``test_doctor_native_harnesses.py`` pattern); a sentinel
``groundtruth.db`` keeps its bytes and ``sqlite3.connect`` is refused.

Written in c103 before the c102 shared fixtures (``platform_tests/groundtruth_kb/native_fixtures.py``)
reach this draft; the served-authority case of this check lives in
``platform_tests/groundtruth_kb/test_doctor_native_readers.py`` and skips until that rebase.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project.doctor import _check_application_scope_alignment

AUTHORITY_URL = "http://127.0.0.1:12345"
SENTINEL = b"Never opened by the application-scope check"


@pytest.fixture
def storeless_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A project whose sentinel ``groundtruth.db`` keeps its bytes and whose SQLite is refused."""
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(SENTINEL)

    def refuse(*args, **kwargs):
        pytest.fail("The application-scope check cannot open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    yield tmp_path
    assert sentinel.read_bytes() == SENTINEL


@pytest.fixture
def configured_authority(storeless_project: Path) -> Path:
    """The storeless project with ``authority_url`` configured; requests are served from dicts."""
    (storeless_project / "groundtruth.toml").write_text(
        f'[groundtruth]\nauthority_url="{AUTHORITY_URL}"\n', encoding="utf-8"
    )
    return storeless_project


def spec(spec_id: str, title: str, source_paths: list[str], application_scope: str | None = None) -> dict:
    return {"id": spec_id, "title": title, "source_paths": source_paths, "application_scope": application_scope}


def native_test(test_id: str, title: str, test_file: str, application_scope: str | None = None) -> dict:
    return {"id": test_id, "title": title, "test_file": test_file, "application_scope": application_scope}


def _pages(rows: list) -> list[list[dict]]:
    """One page from a flat list of records, or the given pages from a list of lists."""
    if rows and isinstance(rows[0], list):
        return [list(page) for page in rows]
    return [list(rows)]


def serve(
    monkeypatch: pytest.MonkeyPatch,
    *,
    specifications: list | None = None,
    tests: list | None = None,
    calls: list | None = None,
) -> None:
    """Serve the specification and test pages in order; a page that is not the last carries a cursor."""
    pages = {"/v1/specifications": _pages(specifications or []), "/v1/tests": _pages(tests or [])}

    def request(self, method, path, *, body=None, query=None):
        if calls is not None:
            calls.append((method, path, query))
        assert method == "GET" and body is None, "a doctor check only reads"
        if path not in pages:
            raise AuthorityClientError("invalid_path", f"Unexpected request {method} {path}")
        remaining = pages[path]
        assert remaining, f"no page left to serve for {path}"
        records = remaining.pop(0)
        return {"records": records, "next_after": records[-1]["id"] if remaining else None}

    monkeypatch.setattr(AuthorityClient, "request", request)


def test_application_scope_doctor_passes_aligned_rows(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    serve(
        monkeypatch,
        specifications=[
            spec(
                "SPEC-PLATFORM-ALIGNED", "Aligned platform spec", ["scripts/release_candidate_gate.py"], "gtkb_platform"
            ),
            spec("SPEC-UNSCOPED", "Unscoped platform spec", ["groundtruth-kb/src/groundtruth_kb/config.py"]),
        ],
        tests=[
            native_test(
                "TEST-PLATFORM-ALIGNED",
                "Aligned platform test",
                "platform_tests/scripts/test_platform.py",
                "gtkb_platform",
            ),
        ],
    )

    check = _check_application_scope_alignment(configured_authority)

    assert check.name == "Application scope alignment"
    assert check.status == "pass"
    assert check.required is True
    assert check.found is True
    assert check.message.startswith("Application-scope alignment OK")
    assert "(2 specifications, 1 tests)" in check.message


def test_application_scope_doctor_accepts_the_native_application_scope_vocabulary(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The authority stores ``application:<Name>`` (``native_authority.Scope``; live 2026-09-19: 633
    specifications and 8,169 tests carry ``application:Agent_Red``), so aligned application rows in that
    form must pass rather than fail the whole check on an unknown-vocabulary error."""
    serve(
        monkeypatch,
        specifications=[
            spec(
                "SPEC-APP-ALIGNED", "Aligned app spec", ["applications/Agent_Red/app/main.py"], "application:Agent_Red"
            ),
        ],
        tests=[
            native_test(
                "TEST-APP-ALIGNED",
                "Aligned app test",
                "applications/Agent_Red/tests/test_widget.py",
                "application:Agent_Red",
            ),
        ],
    )

    check = _check_application_scope_alignment(configured_authority)

    assert check.status == "pass", check.message
    assert check.message.startswith("Application-scope alignment OK")


def test_application_scope_doctor_fails_explicit_scope_path_mismatch(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    serve(
        monkeypatch,
        tests=[
            native_test(
                "TEST-MISSCOPED",
                "Mis-scoped platform test",
                "applications/Agent_Red/tests/test_widget.py",
                "gtkb_platform",
            ),
        ],
    )

    check = _check_application_scope_alignment(configured_authority)

    assert check.status == "fail"
    assert check.required is True
    assert check.found is True
    assert check.message.startswith("1 application-scope alignment violation(s): test TEST-MISSCOPED: ")
    assert "gtkb_platform path points at applications/Agent_Red/" in check.message


def test_application_scope_doctor_warns_on_ambiguous_unscoped_candidates(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    serve(
        monkeypatch,
        specifications=[spec("SPEC-AMBIGUOUS", "Agent Red generic evidence", ["tests/test_agent_red_widget.py"])],
    )

    check = _check_application_scope_alignment(configured_authority)

    assert check.status == "warning"
    assert check.required is False
    assert check.found is True
    assert check.message.startswith("1 ambiguous application-scope candidate(s): spec SPEC-AMBIGUOUS: ")
    assert "ambiguous application-scope candidate" in check.message


@pytest.mark.parametrize("config", ["[groundtruth]\ndb_path = 'groundtruth.db'\n", None], ids=["no-url", "no-toml"])
def test_not_configured_is_warning(
    storeless_project: Path, monkeypatch: pytest.MonkeyPatch, config: str | None
) -> None:
    if config is not None:
        (storeless_project / "groundtruth.toml").write_text(config, encoding="utf-8")

    def refuse(*args, **kwargs):
        pytest.fail("No authority may be contacted when none is configured")

    monkeypatch.setattr(AuthorityClient, "request", refuse)

    check = _check_application_scope_alignment(storeless_project)

    assert check.name == "Application scope alignment"
    assert check.status == "warning"
    assert check.required is True
    assert check.found is False
    assert "unverified" in check.message
    assert "no authority_url is configured" in check.message


@pytest.mark.parametrize("failure", ["unavailable", "malformed", "stuck_pagination"])
def test_unreachable_is_fail(configured_authority: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    def request(self, method, path, *, body=None, query=None):
        if failure == "unavailable":
            raise AuthorityClientError("authority_unavailable", "Service unavailable")
        if failure == "malformed":
            return {"records": [None], "next_after": None}
        return {"records": [spec("SPEC-A", "A", [], "gtkb_platform")], "next_after": "SPEC-A"}

    monkeypatch.setattr(AuthorityClient, "request", request)

    check = _check_application_scope_alignment(configured_authority)

    assert check.status == "fail"
    assert check.required is True
    assert check.found is False
    expected_code = "authority_unavailable" if failure == "unavailable" else "invalid_response"
    assert check.message.startswith(f"Application-scope alignment check failed: {expected_code}")


def test_pages_follow_next_after(configured_authority: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []
    serve(
        monkeypatch,
        specifications=[
            [spec("SPEC-APP-ALIGNED", "First page", ["scripts/first.py"], "gtkb_platform")],
            [spec("SPEC-PLATFORM-ZULU", "Second page", ["scripts/second.py"], "gtkb_platform")],
        ],
        tests=[
            native_test("TEST-PLATFORM-ALIGNED", "Aligned platform test", "platform_tests/scripts/test_platform.py")
        ],
        calls=calls,
    )

    check = _check_application_scope_alignment(configured_authority)

    assert check.status == "pass"
    assert "(2 specifications, 1 tests)" in check.message
    assert [(method, path) for method, path, _ in calls] == [
        ("GET", "/v1/specifications"),
        ("GET", "/v1/specifications"),
        ("GET", "/v1/tests"),
    ]
    assert [query["limit"] for _, _, query in calls] == [1000, 1000, 1000]
    assert [query["after"] for _, _, query in calls] == [None, "SPEC-APP-ALIGNED", None]
