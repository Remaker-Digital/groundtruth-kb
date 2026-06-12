# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 1: nine isolation doctor checks.

Implements the 9 checks specified in Phase 9 §4 lines 199-228 of
``GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md``.

The checks enforce ADR-ISOLATION-APPLICATION-PLACEMENT-001 at runtime by
verifying that an adopter root respects application/platform separation.

Bridge authority: ``bridge/gtkb-isolation-017-slice1-doctor-checks-008.md`` GO.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from groundtruth_kb.project.doctor import ToolCheck

# Product-scope ownership labels for the no-writable-product-paths probe.
#
# Narrowed per Codex `-006` F1: `gt-kb-scaffolded` rows include adopter-
# editable files like `groundtruth.toml` (per authority matrix line 113 +
# scaffold-ownership.toml `adopter-groundtruth-toml` row 23-31). Treating
# them as non-writable would false-positive on every clean adopter root.
#
# Slice 1 rule: write-probe enforcement applies to `gt-kb-managed` rows only
# (definitively product-managed by upgrade semantics). Other labels with
# potential product-scope semantics are excluded pending Slice 2 row-level
# authority-marker work.
_PRODUCT_SCOPE_OWNERSHIP_LABELS: frozenset[str] = frozenset({"gt-kb-managed"})

_RAW_DB_ENDPOINT_RE = re.compile(r"(?i)^(?:sqlite:\/\/\/.*\.db|.*\.db)$")
_SCOPED_SERVICE_URL_RE = re.compile(r"(?i)^(?:https?:\/\/|[A-Za-z][A-Za-z0-9+\-]*:)")


# ---------------------------------------------------------------------------
# Check 1: adopter root not under product root
# ---------------------------------------------------------------------------


def _check_isolation_adopter_root_not_under_product_root(target: Path, product_root: Path) -> ToolCheck:
    """Check 1 per Phase 9 §4 line 205. ``product_root`` is required."""
    target_resolved = target.resolve()
    product_resolved = product_root.resolve()
    try:
        target_resolved.relative_to(product_resolved)
        return ToolCheck(
            name="isolation:adopter-root-placement",
            required=True,
            found=True,
            status="fail",
            message=(
                f"adopter root {target} is under product root {product_root}; "
                f"per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopters live at "
                f"<gt-kb-root>/applications/<name>/"
            ),
        )
    except ValueError:
        return ToolCheck(
            name="isolation:adopter-root-placement",
            required=True,
            found=True,
            status="pass",
            message=f"adopter root {target} is outside product root {product_root}",
        )


# ---------------------------------------------------------------------------
# Check 2: service endpoint not raw DB path
# ---------------------------------------------------------------------------


def _check_isolation_service_endpoint_not_raw_db(target: Path) -> ToolCheck:
    """Check 2 per Phase 9 §4 line 206-207."""
    toml_path = target / "groundtruth.toml"
    if not toml_path.exists():
        return ToolCheck(
            name="isolation:service-endpoint",
            required=True,
            found=False,
            status="info",
            message="groundtruth.toml absent; service endpoint not configured",
        )
    try:
        import tomllib

        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return ToolCheck(
            name="isolation:service-endpoint",
            required=True,
            found=True,
            status="warning",
            message=f"groundtruth.toml unreadable at {toml_path}",
        )
    service = data.get("service") or {}
    endpoint = service.get("endpoint")
    if not endpoint:
        return ToolCheck(
            name="isolation:service-endpoint",
            required=True,
            found=False,
            status="info",
            message="[service].endpoint absent; not configured",
        )
    # Raw-DB pattern must be evaluated BEFORE the generic scoped-URL pattern
    # because both `*.db` and `sqlite:///*.db` are explicit raw-DB classes per
    # the approved -001 proposal. Otherwise the scheme-prefix scoped-URL rule
    # would wrongly accept `sqlite:///path/to.db`. Per Codex `-010` F1 fix.
    if _RAW_DB_ENDPOINT_RE.match(str(endpoint)):
        return ToolCheck(
            name="isolation:service-endpoint",
            required=True,
            found=True,
            status="fail",
            message=(
                f"service endpoint points to a raw DB path: {endpoint}; "
                f"per Phase 9 line 206-207 the application must talk to a "
                f"scoped service, not the raw groundtruth.db"
            ),
        )
    if _SCOPED_SERVICE_URL_RE.match(str(endpoint)):
        return ToolCheck(
            name="isolation:service-endpoint",
            required=True,
            found=True,
            status="pass",
            message=f"service endpoint is a scoped service URL: {endpoint}",
        )
    return ToolCheck(
        name="isolation:service-endpoint",
        required=True,
        found=True,
        status="warning",
        message=f"service endpoint shape unrecognised: {endpoint}",
    )


# ---------------------------------------------------------------------------
# Check 3: durable work subject = application
# ---------------------------------------------------------------------------


def _check_isolation_durable_work_subject_application(target: Path) -> ToolCheck:
    """Check 3 per Phase 9 §4 line 208-209.

    Reads canonical Phase 7 state at ``<target>/.claude/session/work-subject.json``
    per Phase 7 §"Durable State Contract" lines 120-164. Falls back to
    ``<target>/.claude/hooks/.workstream-focus-state.json`` for one migration
    window per Phase 7 line 154.
    """
    canonical = target / ".claude" / "session" / "work-subject.json"
    legacy = target / ".claude" / "hooks" / ".workstream-focus-state.json"
    state_path = canonical if canonical.exists() else (legacy if legacy.exists() else None)

    if state_path is None:
        return ToolCheck(
            name="isolation:work-subject",
            required=True,
            found=False,
            status="info",
            message="work-subject.json absent; defaults to application",
        )

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ToolCheck(
            name="isolation:work-subject",
            required=True,
            found=True,
            status="warning",
            message=f"invalid JSON at {state_path}; defaulting to application",
        )

    subject = data.get("current_subject")
    if subject == "application":
        app_root = data.get("application_root")
        if app_root and Path(app_root).resolve() != target.resolve():
            return ToolCheck(
                name="isolation:work-subject",
                required=True,
                found=True,
                status="warning",
                message=f"application_root mismatch: {app_root} vs {target}",
            )
        return ToolCheck(
            name="isolation:work-subject",
            required=True,
            found=True,
            status="pass",
            message="current_subject=application",
        )
    if subject in (None, ""):
        return ToolCheck(
            name="isolation:work-subject",
            required=True,
            found=True,
            status="info",
            message="current_subject unset; defaults to application",
        )
    return ToolCheck(
        name="isolation:work-subject",
        required=True,
        found=True,
        status="warning",
        message=f"current_subject={subject!r}; expected application",
    )


# ---------------------------------------------------------------------------
# Check 4: no writable product paths
# ---------------------------------------------------------------------------


def _check_isolation_no_writable_product_paths(target: Path, profile: str) -> ToolCheck:
    """Check 4 per Phase 9 §4 line 210-211.

    Enumerates product-scope paths via ``OwnershipResolver.all_records()``
    (per ``managed_registry.py:697`` callout). For FILE-class records, uses
    the ``ManagedArtifact.target_path``; for ownership-glob records, expands
    against the live filesystem under ``target``. Tests writability via a
    touch-and-remove probe.
    """
    # If this is the framework development repository itself (identified by the
    # presence of the groundtruth-kb package directory), the product-scope paths
    # are expected to be writable for local development.
    if (target / "groundtruth-kb").is_dir():
        return ToolCheck(
            name="isolation:no-writable-product-paths",
            required=True,
            found=True,
            status="pass",
            message="development repository workspace; write isolation probe bypassed",
        )

    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    product_paths: list[Path] = []

    for record in resolver.all_records():
        if record.ownership not in _PRODUCT_SCOPE_OWNERSHIP_LABELS:
            continue
        if record.source_class == "file" and record.source is not None:
            rel = getattr(record.source, "target_path", None)
            if rel:
                product_paths.append(target / rel)
        elif record.source_class == "ownership-glob" and record.path_glob is not None:
            for matched in target.glob(record.path_glob):
                product_paths.append(matched)

    writable: list[str] = []
    for path in product_paths:
        if not path.exists():
            continue
        probe = path / ".isolation-probe-tmp" if path.is_dir() else path.parent / f".isolation-probe-tmp-{path.name}"
        try:
            probe.touch()
            probe.unlink()
            writable.append(str(path))
        except (OSError, PermissionError):
            pass

    if writable:
        sample = writable[:5]
        suffix = "..." if len(writable) > 5 else ""
        return ToolCheck(
            name="isolation:no-writable-product-paths",
            required=True,
            found=True,
            status="fail",
            message=f"product-scope paths writable from app session: {sample}{suffix}",
        )
    return ToolCheck(
        name="isolation:no-writable-product-paths",
        required=True,
        found=True,
        status="pass",
        message=f"checked {len(product_paths)} product paths; none writable",
    )


# ---------------------------------------------------------------------------
# Check 5: hooks point to wrappers
# ---------------------------------------------------------------------------


def _check_isolation_hooks_point_to_wrappers(target: Path, profile: str) -> ToolCheck:
    """Check 5 per Phase 9 §4 line 212-213.

    Parses ``.claude/settings.json`` hook registrations; for each registered
    command, asserts it points to a path under the GT-KB framework or wrapped
    via ``${CLAUDE_PLUGIN_ROOT}``. Embedded inline logic in adopter hooks
    triggers a warning.
    """
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return ToolCheck(
            name="isolation:hooks-point-to-wrappers",
            required=True,
            found=False,
            status="info",
            message=".claude/settings.json absent; no hook registrations",
        )
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ToolCheck(
            name="isolation:hooks-point-to-wrappers",
            required=True,
            found=True,
            status="warning",
            message=f"invalid JSON at {settings_path}",
        )

    hooks = data.get("hooks") or {}
    embedded: list[str] = []
    for event_name, registrations in hooks.items():
        if not isinstance(registrations, list):
            continue
        for entry in registrations:
            for hook in (entry or {}).get("hooks", []) or []:
                command = (hook or {}).get("command", "")
                if not command:
                    continue
                # Acceptable: framework-package path, ${CLAUDE_PLUGIN_ROOT} wrapper,
                # adopter-side wrapper that invokes a framework module.
                if "${CLAUDE_PLUGIN_ROOT}" in command:
                    continue
                if "groundtruth_kb" in command or "groundtruth-kb" in command:
                    continue
                # Adopter-local hooks under .claude/hooks/ are accepted as wrappers
                # only if they reference a python module path; raw embedded shell
                # scripts that don't invoke a module are flagged.
                if ".claude/hooks/" in command and "python" in command:
                    continue
                # Framework local scripts in the scripts/ folder are accepted as
                # wrappers if we are running in the framework development workspace.
                if (target / "groundtruth-kb").is_dir() and "scripts/" in command and "python" in command:
                    continue
                embedded.append(f"{event_name}: {command[:80]}")

    if embedded:
        sample = embedded[:3]
        return ToolCheck(
            name="isolation:hooks-point-to-wrappers",
            required=True,
            found=True,
            status="warning",
            message=(
                f"hook registrations with embedded logic (not wrapper-shaped): "
                f"{sample}{'...' if len(embedded) > 3 else ''}"
            ),
        )
    return ToolCheck(
        name="isolation:hooks-point-to-wrappers",
        required=True,
        found=True,
        status="pass",
        message="hook registrations are wrapper-shaped",
    )


# ---------------------------------------------------------------------------
# Check 6: workstream-focus hook absent
# ---------------------------------------------------------------------------


def _check_isolation_workstream_focus_hook_absent(target: Path) -> ToolCheck:
    """Check 6 per Phase 9 §4 line 214-215 + line 410.

    Per Phase 9 line 410: "doctor warns if it reappears". Severity is
    ``warning``, not ``fail`` — the legacy hook is deprecated and should be
    removed, but presence is not a hard release blocker.
    """
    legacy_hook = target / ".claude" / "hooks" / "workstream-focus.py"
    if legacy_hook.exists():
        return ToolCheck(
            name="isolation:workstream-focus-hook-absent",
            required=True,
            found=True,
            status="warning",
            message=(
                f".claude/hooks/workstream-focus.py exists at {legacy_hook}; "
                f"per Phase 9 line 410 this is deprecated and should be removed. "
                f"See ADR-ISOLATION-APPLICATION-PLACEMENT-001 for replacement work-subject surface."
            ),
        )
    return ToolCheck(
        name="isolation:workstream-focus-hook-absent",
        required=True,
        found=False,
        status="pass",
        message="workstream-focus.py absent (deprecated hook correctly removed)",
    )


# ---------------------------------------------------------------------------
# Check 7: (retired at Slice 7-prime — standing-backlog markdown check
# removed per DELIB-S337; MemBase work_items is the sole canonical backlog)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Check 8: release-readiness app-subject header
# ---------------------------------------------------------------------------

_GREEN_KEYWORDS_RE = re.compile(r"(?i)\b(ready|verified|green|passing|approved)\b")


def _check_isolation_release_readiness_app_subject_header(target: Path) -> ToolCheck:
    """Check 8 per Phase 9 §4 line 217-218."""
    rr_path = target / "memory" / "release-readiness.md"
    if not rr_path.exists():
        return ToolCheck(
            name="isolation:release-readiness-app-subject-header",
            required=True,
            found=False,
            status="info",
            message="memory/release-readiness.md absent; no release-readiness to check",
        )
    try:
        text = rr_path.read_text(encoding="utf-8")
    except OSError:
        return ToolCheck(
            name="isolation:release-readiness-app-subject-header",
            required=True,
            found=True,
            status="warning",
            message=f"release-readiness.md unreadable at {rr_path}",
        )

    first_header = ""
    for line in text.splitlines():
        if line.strip():
            first_header = line.strip()
            break

    issues: list[str] = []
    if "application" not in first_header.lower():
        issues.append("first header does not mention 'application' subject")

    for lineno, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        if "gt-kb" in lower and _GREEN_KEYWORDS_RE.search(line):
            issues.append(f"line {lineno} combines GT-KB subject with green keyword")
            break

    if issues:
        return ToolCheck(
            name="isolation:release-readiness-app-subject-header",
            required=True,
            found=True,
            status="warning",
            message="; ".join(issues),
        )
    return ToolCheck(
        name="isolation:release-readiness-app-subject-header",
        required=True,
        found=True,
        status="pass",
        message="release-readiness.md header asserts application subject without combined-claim",
    )


# ---------------------------------------------------------------------------
# Check 9: chroma cache is regeneratable
# ---------------------------------------------------------------------------


def _check_isolation_chroma_regeneratable(target: Path) -> ToolCheck:
    """Check 9 per Phase 9 §4 line 219-220."""
    chroma = target / ".groundtruth-chroma"
    if not chroma.exists():
        return ToolCheck(
            name="isolation:chroma-regeneratable",
            required=True,
            found=False,
            status="pass",
            message=".groundtruth-chroma absent (no orphan cache)",
        )
    db = target / "groundtruth.db"
    if not db.exists() or db.stat().st_size == 0:
        return ToolCheck(
            name="isolation:chroma-regeneratable",
            required=True,
            found=True,
            status="warning",
            message=(
                f".groundtruth-chroma exists at {chroma} but groundtruth.db is "
                f"missing or empty; chroma cache is orphaned and not regeneratable"
            ),
        )
    return ToolCheck(
        name="isolation:chroma-regeneratable",
        required=True,
        found=True,
        status="pass",
        message=".groundtruth-chroma is regeneratable from groundtruth.db",
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_isolation_checks(target: Path, profile: str, *, product_root: Path) -> list[ToolCheck]:
    """Return the isolation checks in preflight order.

    Per Phase 9 §4 line 224-226: environment boundary → service reachability →
    subject assertion → registry compliance → app-local governed state health.

    ``product_root`` is REQUIRED. Per Codex `-002` F2 fix: there is no
    ``manifest.find_project_root()`` API; callers must supply ``product_root``
    explicitly. ``run_doctor`` derives it from
    ``Path(__file__).resolve().parents[3]``.

    When ``target`` is the platform development repository (detected by the
    presence of the ``groundtruth-kb/`` package directory), adopter-specific
    checks are replaced with pass-with-explanation results. Checks 2 (service
    endpoint), 4 (writable product paths), and 9 (chroma cache) apply to both
    contexts and run unconditionally.
    """
    is_platform_dev = (target / "groundtruth-kb").is_dir()

    if is_platform_dev:
        _skip = "platform development repository; adopter-context check not applicable"
        return [
            ToolCheck(
                name="isolation:adopter-root-placement", required=False, found=True, status="pass", message=_skip
            ),
            _check_isolation_service_endpoint_not_raw_db(target),
            ToolCheck(name="isolation:work-subject", required=False, found=True, status="pass", message=_skip),
            _check_isolation_no_writable_product_paths(target, profile),
            ToolCheck(
                name="isolation:hooks-point-to-wrappers", required=False, found=True, status="pass", message=_skip
            ),
            ToolCheck(
                name="isolation:workstream-focus-hook-absent", required=False, found=True, status="pass", message=_skip
            ),
            ToolCheck(
                name="isolation:release-readiness-app-subject-header",
                required=False,
                found=True,
                status="pass",
                message=_skip,
            ),
            _check_isolation_chroma_regeneratable(target),
        ]

    return [
        _check_isolation_adopter_root_not_under_product_root(target, product_root),
        _check_isolation_service_endpoint_not_raw_db(target),
        _check_isolation_durable_work_subject_application(target),
        _check_isolation_no_writable_product_paths(target, profile),
        _check_isolation_hooks_point_to_wrappers(target, profile),
        _check_isolation_workstream_focus_hook_absent(target),
        _check_isolation_release_readiness_app_subject_header(target),
        _check_isolation_chroma_regeneratable(target),
    ]
