"""Read the existing application catalog and validate hosted slot boundaries."""

import os
import re
import subprocess
import tomllib
from pathlib import Path


class ApplicationRegistryError(ValueError):
    """The configured catalog or application slot cannot be interpreted safely."""


def application_slot_path(project_root: Path, app_name: str) -> Path:
    """Resolve one named immediate child without treating package location as host."""
    if not isinstance(app_name, str) or re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", app_name) is None:
        raise ApplicationRegistryError("application name must be one hosted slot identifier")
    host = Path(project_root).resolve()
    applications = host / "applications"
    slot = applications / app_name
    try:
        if applications.resolve() != applications or slot.resolve() != slot:
            raise ApplicationRegistryError("application slot must not be redirected from the selected host")
        if applications.exists() and not applications.is_dir():
            raise ApplicationRegistryError("the selected host's applications path is not a directory")
        if slot.exists() and not slot.is_dir():
            raise ApplicationRegistryError(f"application slot {app_name} is not a directory")
    except (OSError, RuntimeError) as exc:
        raise ApplicationRegistryError("application slot boundary cannot be resolved") from exc
    return slot


def load_application_catalog(project_root: Path) -> dict[str, dict[str, str]]:
    """Read current catalog entries; malformed data never means an empty catalog."""
    host = Path(project_root).resolve()
    applications = host / "applications"
    path = applications / "registry.toml"
    try:
        if applications.resolve() != applications or path.resolve() != path:
            raise ApplicationRegistryError("application catalog must remain directly under the selected host")
        if not path.exists():
            return {}
        if not path.is_file():
            raise ApplicationRegistryError("applications/registry.toml is not a file")
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        raise ApplicationRegistryError(f"application catalog cannot be read: {exc}") from exc
    entries = payload.get("applications")
    if not isinstance(entries, dict):
        raise ApplicationRegistryError("application catalog requires an applications table")
    seen: set[str] = set()
    for name, entry in entries.items():
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name) is None:
            raise ApplicationRegistryError("application catalog contains an invalid slot identifier")
        if name.casefold() in seen:
            raise ApplicationRegistryError("application catalog contains duplicate application names")
        seen.add(name.casefold())
        if not isinstance(entry, dict) or entry.get("slot") != name:
            raise ApplicationRegistryError(f"application catalog entry {name} must identify its same-named hosted slot")
    return entries


def has_registry_entry(project_root: Path, app_name: str) -> bool:
    """Observe registration; this grants no claim, ownership or mutation right."""
    application_slot_path(project_root, app_name)
    return app_name in load_application_catalog(project_root)


def register_application(project_root: Path, app_name: str) -> dict[str, object]:
    """Register one hosted name and marker without creating governance or Git state.

    Reuse the platform declaration writer's existing OS mutex and controls.
    Registration does not initialize a repository, commit files or qualify it.
    """
    import tomlkit

    from groundtruth_kb.project.registry_control_plane import (
        _atomic_replace,
        _declaration_lock_path,
        _registry_controls,
        _RegistryFileLock,
    )

    from .validation import validate_self_completion_preflight

    host = Path(project_root).resolve(strict=True)
    app_root = application_slot_path(host, app_name)
    catalog_path = host / "applications/registry.toml"
    marker_path = app_root / "application.toml"
    controls = _registry_controls(host)
    with _RegistryFileLock(_declaration_lock_path(host, controls), controls=controls):
        entries = load_application_catalog(host)
        for existing in entries:
            if existing.casefold() == app_name.casefold() and existing != app_name:
                raise ApplicationRegistryError(f"Application name differs in case from registered {existing}")
        validate_self_completion_preflight(host, app_name)
        before = catalog_path.read_bytes() if catalog_path.exists() else None
        after = before
        if app_name not in entries:
            document = tomlkit.parse(before.decode("utf-8")) if before is not None else tomlkit.document()
            if "applications" not in document:
                document.add("applications", tomlkit.table())
            applications = document["applications"]
            if not isinstance(applications, (tomlkit.items.Table, tomlkit.items.InlineTable)):
                raise ApplicationRegistryError("Application catalog requires an applications table")
            entry = tomlkit.inline_table()
            entry["slot"] = app_name
            applications[app_name] = entry
            after = tomlkit.dumps(document).encode("utf-8")
            parsed = tomllib.loads(after.decode("utf-8"))["applications"]
            if parsed.get(app_name) != {"slot": app_name} or any(
                parsed.get(name) != value for name, value in entries.items()
            ):
                raise ApplicationRegistryError("Application catalog postimage does not preserve existing entries")
        created_marker = False
        created_app = not app_root.exists()
        created_applications = not app_root.parent.exists()
        published = False
        marker = f'[application]\nname = "{app_name}"\n'.encode()
        created_paths = []
        try:
            app_root.mkdir(parents=True, exist_ok=True)
            if not marker_path.exists():
                # An existing marker is never overwritten, even on a repeated
                # registration. Exclusive creation also detects outside edits.
                with marker_path.open("xb") as handle:
                    created_marker = True
                    handle.write(marker)
                    handle.flush()
                    os.fsync(handle.fileno())
                created_paths.append(marker_path.relative_to(host).as_posix())
            validate_self_completion_preflight(host, app_name)
            observed = catalog_path.read_bytes() if catalog_path.exists() else None
            if observed != before:
                raise ApplicationRegistryError(
                    "Application catalog changed; inspect the current entries before retrying"
                )
            if after != before:
                assert after is not None
                _atomic_replace(catalog_path, after)
                published = True
                created_paths.append(catalog_path.relative_to(host).as_posix())
            if load_application_catalog(host).get(app_name, {}).get("slot") != app_name:
                raise ApplicationRegistryError("Application registration readback differs from the requested entry")
            validate_self_completion_preflight(host, app_name)
        except Exception:
            # A pre-publication failure removes only this operation's complete,
            # still-identical new marker and empty directories. Never remove
            # existing content or a marker that changed outside this writer.
            # Replacement can succeed before a subsequent durability check
            # raises. Remove the marker only when the original catalog is
            # positively observed; otherwise retain it for inspection/retry.
            try:
                catalog_unchanged = (
                    catalog_path.resolve() == catalog_path
                    and (catalog_path.read_bytes() if catalog_path.exists() else None) == before
                )
            except (OSError, RuntimeError):
                catalog_unchanged = False
            if not published and catalog_unchanged:
                if (
                    created_marker
                    and marker_path.resolve() == marker_path
                    and marker_path.is_file()
                    and marker_path.read_bytes() == marker
                ):
                    marker_path.unlink()
                if created_app and app_root.resolve() == app_root and app_root.is_dir() and not any(app_root.iterdir()):
                    app_root.rmdir()
                if (
                    created_applications
                    and app_root.parent.resolve() == app_root.parent
                    and app_root.parent.is_dir()
                    and not any(app_root.parent.iterdir())
                ):
                    app_root.parent.rmdir()
            raise
        return {
            "status": "registered" if created_paths else "already_registered",
            "application": app_name,
            "repository_ref": "application:" + app_name,
            "application_root": str(app_root),
            "changed_paths": created_paths,
        }


def validate_application_scope(project_root: Path | None, scope: str | None) -> None:
    """Validate a record's classification; this grants no repository effects.

    Null is explicitly unresolved. Application names come from the current
    catalog, never a platform enumeration or a guessed path association.
    """
    if scope is None or scope == "gtkb_platform":
        return
    if not isinstance(scope, str) or re.fullmatch(r"application:[A-Za-z][A-Za-z0-9_-]*", scope) is None:
        raise ApplicationRegistryError("application_scope must be gtkb_platform or application:<catalog name>")
    if project_root is None:
        raise ApplicationRegistryError("application scope validation requires the configured platform host")
    name = scope.removeprefix("application:")
    application_slot_path(project_root, name)
    if name not in load_application_catalog(project_root):
        raise ApplicationRegistryError("application_scope must identify an exact current application catalog entry")


def resolve_project_repository(project_root: Path, repository_ref: str) -> Path:
    """Resolve an explicit current project fact against this host's catalog.

    This read grants no claim or commit permission. Callers re-read the project
    and resolve again at the effect boundary; no absolute path is persisted.
    """
    from .validation import check_slot_markers

    host = Path(project_root).absolute()
    if host.resolve() != host:
        raise ApplicationRegistryError("the platform host must not be redirected")
    if repository_ref == "platform":
        root = host
    else:
        if not isinstance(repository_ref, str) or not repository_ref.startswith("application:"):
            raise ApplicationRegistryError("repository_ref must be platform or application:<catalog name>")
        name = repository_ref.removeprefix("application:")
        root = application_slot_path(host, name)
        if name not in load_application_catalog(host):
            raise ApplicationRegistryError("repository_ref must identify an exact current application catalog entry")
        markers = check_slot_markers(host, name)
        if not markers["app_toml_present"] or not markers["consistent"]:
            raise ApplicationRegistryError("the application repository requires matching current application markers")
        if not (root / ".git").is_dir():
            raise ApplicationRegistryError("the application slot requires its own independent Git repository")
    try:
        if not root.is_dir() or (root / ".git").resolve() != root / ".git":
            raise ApplicationRegistryError("the selected repository root or Git directory is unavailable or redirected")
        result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "rev-parse",
                "--show-toplevel",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            cwd=root,
            env={key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")},
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        lines = result.stdout.splitlines()
        if result.returncode or len(lines) != 2 or Path(lines[0]).resolve() != root:
            raise ApplicationRegistryError("the selected path is not its exact Git checkout root")
        if repository_ref != "platform" and Path(lines[1]).resolve() != root / ".git":
            raise ApplicationRegistryError("the application must have its own independent Git common directory")
    except (OSError, UnicodeError, RuntimeError, subprocess.TimeoutExpired) as exc:
        raise ApplicationRegistryError("the selected repository identity could not be observed") from exc
    return root
