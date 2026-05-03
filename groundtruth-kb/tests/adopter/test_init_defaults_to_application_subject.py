# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 235: ``init defaults to application subject``.

Spec: a fresh ``gt project init`` produces an adopter whose Phase 7 durable
state defaults to ``current_subject=application`` (or omits the state file,
which Slice 1 check #3 treats as the same default).

Outside-in surfaces exercised:
- ``scaffold_project`` (via the ``clean_adopter`` fixture).
- ``run_isolation_checks(target, profile, *, product_root=...)`` from
  ``groundtruth_kb.project.doctor_isolation`` — the public preflight surface.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def test_clean_adopter_work_subject_check_defaults_to_application(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Slice 1 check #3 returns ``status="info"`` + the application-default message
    on a freshly-scaffolded adopter (no work-subject.json file is created at
    scaffold time per Slice 3's deliberate Phase 7 state policy).
    """
    adopter, product_root = clean_adopter
    checks = run_isolation_checks(adopter, "dual-agent", product_root=product_root)
    by_name = {c.name: c for c in checks}
    work_subject = by_name["isolation:work-subject"]
    assert work_subject.status == "info", (
        f"fresh adopter expected status=info; got {work_subject.status} with message={work_subject.message!r}"
    )
    assert "defaults to application" in work_subject.message, (
        f"expected default-to-application message; got {work_subject.message!r}"
    )


def test_clean_adopter_service_endpoint_is_placeholder(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Phase 9 §1 contract: scaffolded ``[service].endpoint`` is the placeholder
    ``configure-me://placeholder/v1`` (validated by Slice 3 TP1 + scaffolded
    by Slice 3 ``_emit_slice3_artifacts``). Verifying it from the clean-adopter
    surface keeps the user-facing contract under regression coverage.
    """
    adopter, _ = clean_adopter
    toml_path = adopter / "groundtruth.toml"
    with open(toml_path, "rb") as fp:
        data = tomllib.load(fp)
    assert data.get("service", {}).get("endpoint") == "configure-me://placeholder/v1"


def test_clean_adopter_service_endpoint_check_does_not_fail(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Slice 1 check #2 must not return ``status="fail"`` on a clean adopter.

    The placeholder endpoint matches the scoped-URL pattern (it has a
    scheme prefix), so check #2 returns ``pass``. Any future change that
    causes the scaffolded endpoint to look like a raw DB path must be
    caught here, not in production.
    """
    adopter, product_root = clean_adopter
    checks = run_isolation_checks(adopter, "dual-agent", product_root=product_root)
    by_name = {c.name: c for c in checks}
    service = by_name["isolation:service-endpoint"]
    assert service.status != "fail", (
        f"clean-adopter service endpoint must not fail check #2; "
        f"got status={service.status} message={service.message!r}"
    )
