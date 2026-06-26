#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""WI-4848 slice 1: read-only shadow-decision parity harness.

The dispatcher cutover (WI-4848) requires the flip to live spawn to be gated on
*shadow-decision parity evidence*: proof that the daemon's shadow dispatch
decision matches what the live ``cross_harness_bridge_trigger`` would actually
dispatch for the same bridge state. This module produces that evidence.

It is strictly read-only: it loads the trigger and daemon modules, computes both
decisions for a given bridge state, and reports per-role whether they match
field-for-field (recipient harness, selected documents, signature). It never
calls the trigger's spawn path, never writes dispatch state, and never re-enables
dispatchability -- running it leaves the quiesced posture unchanged.

Scope (slice 1): isolate the *selection* divergence. The daemon's
``compute_shadow_decisions`` feeds the full ``items`` list to
``_target_selected_signature`` per target, while the trigger's ``run_trigger``
loop shrinks ``remaining_items`` after each target (cross_harness_bridge_trigger
~L4252-L4292). Identical for single-target roles; a real divergence class for
multi-target roles. Both sides are resolved against the same state dir here so
the comparison isolates that one variable; the live trigger's distinct
``--state-dir`` and its readiness/provider-backoff runtime gates are documented
known differences addressed by the cutover slice, not by this harness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_OPS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _OPS_DIR.parent
_REPO_ROOT = _SCRIPTS_DIR.parent

for _p in (_SCRIPTS_DIR, _REPO_ROOT / "groundtruth-kb" / "src"):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

DEFAULT_MAX_ITEMS = 2
_TRIGGER_STATE_SUBDIR = (".gtkb-state", "cross-harness-trigger")


def _load_module(mod_name: str, path: Path):
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def _load_trigger():
    return _load_module("_cross_harness_trigger_for_parity", _SCRIPTS_DIR / "cross_harness_bridge_trigger.py")


def _load_daemon():
    return _load_module("_gtkb_dispatcher_daemon_for_parity", _SCRIPTS_DIR / "gtkb_dispatcher_daemon.py")


def _doc_names(items: list[Any]) -> list[str]:
    return [str(getattr(item, "document_name", "") or "") for item in items]


def _decision(role: str, target: Any, signature: str, selected: list[Any]) -> dict[str, Any]:
    return {
        "role": role,
        "recipient": getattr(target, "dispatch_state_key", None),
        "harness_id": getattr(target, "harness_id", None),
        "signature": signature,
        "selected": _doc_names(selected),
    }


def trigger_canonical_decisions(project_root: Path, *, max_items: int = DEFAULT_MAX_ITEMS) -> list[dict[str, Any]]:
    """Replicate the trigger's run_trigger dispatch-selection (with remaining_items shrink), no spawn."""
    trigger = _load_trigger()
    index_text = trigger._read_bridge_state_live(project_root)
    actionable_prime, actionable_codex = trigger._compute_actionable(index_text, project_root)
    state_dir = project_root.joinpath(*_TRIGGER_STATE_SUBDIR)
    decisions: list[dict[str, Any]] = []
    for role_label, items in (
        ("prime-builder", actionable_prime),
        ("loyal-opposition", actionable_codex),
    ):
        try:
            targets = trigger._resolve_dispatch_targets(role_label, project_root, state_dir, items=items)
        except ValueError:
            continue
        if not targets:
            continue
        remaining = list(items)
        for target in targets:
            selected, signature = trigger._target_selected_signature(target, remaining, max_items)
            decisions.append(_decision(role_label, target, signature, selected))
            if not selected:
                break
            remaining = trigger._without_selected_dispatch_items(remaining, selected)
            if not any(getattr(item, "dispatchable", True) for item in remaining):
                break
    return decisions


def daemon_shadow_decisions(project_root: Path, *, max_items: int = DEFAULT_MAX_ITEMS) -> list[dict[str, Any]]:
    """Normalize the daemon's compute_shadow_decisions to actual dispatch decisions (recipient + docs)."""
    daemon = _load_daemon()
    out: list[dict[str, Any]] = []
    for record in daemon.compute_shadow_decisions(project_root, max_items=max_items):
        if record.get("recipient") and "would_dispatch" in record:
            out.append(
                {
                    "role": record.get("role"),
                    "recipient": record.get("recipient"),
                    "harness_id": record.get("harness_id"),
                    "signature": record.get("signature"),
                    "selected": list(record.get("would_dispatch") or []),
                }
            )
    return out


@dataclass(frozen=True)
class ParityReport:
    """Per-role comparison of the daemon's shadow decision vs the trigger's canonical selection."""

    overall_match: bool
    roles_compared: tuple[str, ...]
    per_role: dict[str, dict[str, Any]]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "overall_match": self.overall_match,
            "roles_compared": list(self.roles_compared),
            "per_role": self.per_role,
        }


def _normalize(decisions: list[dict[str, Any]]) -> list[tuple[Any, Any, tuple[str, ...]]]:
    return [(d.get("recipient"), d.get("signature"), tuple(d.get("selected") or [])) for d in decisions]


def compare_decisions(
    trigger_decisions: list[dict[str, Any]],
    daemon_decisions: list[dict[str, Any]],
) -> ParityReport:
    """Pure: compare two decision lists per role, returning a per-role parity report."""
    roles = sorted({str(d.get("role")) for d in trigger_decisions} | {str(d.get("role")) for d in daemon_decisions})
    per_role: dict[str, dict[str, Any]] = {}
    overall = True
    for role in roles:
        t = [d for d in trigger_decisions if str(d.get("role")) == role]
        d = [d for d in daemon_decisions if str(d.get("role")) == role]
        tn, dn = _normalize(t), _normalize(d)
        match = tn == dn
        divergences: list[dict[str, Any]] = []
        if not match:
            for i in range(max(len(tn), len(dn))):
                tv = tn[i] if i < len(tn) else None
                dv = dn[i] if i < len(dn) else None
                if tv != dv:
                    divergences.append({"index": i, "trigger": tv, "daemon": dv})
        per_role[role] = {"match": match, "trigger": t, "daemon": d, "divergences": divergences}
        overall = overall and match
    return ParityReport(overall_match=overall, roles_compared=tuple(roles), per_role=per_role)


def compute_parity(project_root: Path, *, max_items: int = DEFAULT_MAX_ITEMS) -> ParityReport:
    """Read-only: compute the daemon-shadow vs trigger-canonical parity for the current bridge state."""
    return compare_decisions(
        trigger_canonical_decisions(project_root, max_items=max_items),
        daemon_shadow_decisions(project_root, max_items=max_items),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only shadow-decision parity harness (WI-4848 slice 1).")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    args = parser.parse_args(argv)
    root = (args.project_root or _REPO_ROOT).resolve()
    report = compute_parity(root, max_items=args.max_items)
    print(json.dumps(report.to_json_dict(), indent=2, sort_keys=True, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
