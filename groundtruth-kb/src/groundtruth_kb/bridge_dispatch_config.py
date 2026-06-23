"""Bridge dispatch configuration, status, and ranking helpers."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_rules import DispatchContext, DispatchRule

DISPATCH_CONFIG_RELATIVE_PATH = Path("config") / "dispatcher" / "rules.toml"
DISPATCH_STATE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-state.json"

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
DISPATCH_ROLES = (ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION)

DEFAULT_SELECTION_ORDER = ("quality", "cost", "availability", "reviewer_precedence", "harness_id")
GOVERNANCE_GRADE_LO_MIN_QUALITY = 80.0
RUNTIME_FAILURE_RESULTS = {
    "all_slugs_quarantined",
    "circuit_breaker_active",
    "dispatch_target_resolution_failed",
    "implementation_authorization_packet_failed",
    "launch_failed",
    "no_active_target_for_role",
    "no_ready_target_for_role",
    "provider_failure_backoff_active",
    "provider_failure",
    "retry_delay_enforced",
    "spawn_rate_limited",
    "target_unlaunchable",
    "work_intent_acquire_failed",
    "max_turn_exhaustion",
    "no_verdict_produced",
}
RUNTIME_FAILURE_CLASSES = {
    "guard_denial",
    "guard_denied_write",
    "max_turn_exhaustion",
    "missing_bridge_verdict",
    "no_verdict_produced",
    "process_terminated_abruptly",
    "provider_failure",
    "provider_failure_backoff_active",
    "provider_configuration_failure",
    "subprocess_execution_failed",
    "work_intent_acquire_failed",
}
RUNTIME_FAILURE_LAUNCH_REASONS = RUNTIME_FAILURE_RESULTS | {
    "previous_launch_failed",
    "subprocess_execution_failed",
}
# WI-4718/WI-4768: non-launch outcomes ('launch_failed') whose last_launch.reason
# indicates benign backpressure rather than a dispatcher failure. The trigger
# collapses all non-launch spawn results to last_result="launch_failed"; only the
# reason field distinguishes saturation from failure.
BENIGN_NONLAUNCH_LAUNCH_REASONS = frozenset({"concurrency_cap_reached", "per_role_concurrency_cap_reached"})


@dataclass(frozen=True)
class HarnessDispatchConfig:
    """Per-harness dispatch overlay from the dispatcher config."""

    harness_id: str
    can_receive_dispatch: bool | None = None
    can_fire_events: bool | None = None
    dispatch_cost: float | None = None
    dispatch_quality: float | None = None
    dispatch_availability: float | None = None
    max_items: int | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, harness_id: str, raw: dict[str, Any]) -> HarnessDispatchConfig:
        return cls(
            harness_id=harness_id,
            can_receive_dispatch=_optional_bool(raw.get("can_receive_dispatch")),
            can_fire_events=_optional_bool(raw.get("can_fire_events")),
            dispatch_cost=_optional_float(raw.get("dispatch_cost", raw.get("cost"))),
            dispatch_quality=_optional_float(raw.get("dispatch_quality", raw.get("quality"))),
            dispatch_availability=_optional_float(raw.get("dispatch_availability", raw.get("availability"))),
            max_items=_optional_int(raw.get("max_items")),
            tags=_string_tuple(raw.get("tags")),
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "harness_id": self.harness_id,
            "can_receive_dispatch": self.can_receive_dispatch,
            "can_fire_events": self.can_fire_events,
            "dispatch_cost": self.dispatch_cost,
            "dispatch_quality": self.dispatch_quality,
            "dispatch_availability": self.dispatch_availability,
            "max_items": self.max_items,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class BridgeDispatchConfig:
    """Parsed dispatcher configuration."""

    path: Path
    exists: bool
    schema_version: int
    selection_order: tuple[str, ...] = DEFAULT_SELECTION_ORDER
    harnesses: dict[str, HarnessDispatchConfig] = field(default_factory=dict)
    rules: tuple[DispatchRule, ...] = ()
    errors: tuple[str, ...] = ()

    def overlay_for(self, harness_id: str) -> HarnessDispatchConfig | None:
        return self.harnesses.get(harness_id)

    def matching_rules(self, context: DispatchContext) -> tuple[DispatchRule, ...]:
        matches = tuple(rule for rule in self.rules if rule.matches(context))
        if matches:
            return matches
        if context.status or context.session_subject or context.activity:
            return ()
        return tuple(rule for rule in self.rules if _role_only_match(rule, context.required_role))

    def selection_order_for(self, context: DispatchContext) -> tuple[str, ...]:
        for rule in self.matching_rules(context):
            if rule.prefer:
                return rule.prefer
        return self.selection_order

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "schema_version": self.schema_version,
            "selection_order": list(self.selection_order),
            "harnesses": {hid: cfg.to_json_dict() for hid, cfg in sorted(self.harnesses.items())},
            "rules": [rule.to_json_dict() for rule in self.rules],
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class BridgeDispatchStatus:
    """Current dispatch topology and health view."""

    config: BridgeDispatchConfig
    harnesses: tuple[dict[str, Any], ...]
    selected_by_role: dict[str, list[dict[str, Any]]]
    health_status: str
    health_findings: tuple[str, ...]
    consistency_findings: tuple[str, ...] = ()
    runtime_classifications: tuple[dict[str, Any], ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_json_dict(),
            "harnesses": list(self.harnesses),
            "selected_by_role": self.selected_by_role,
            "health_status": self.health_status,
            "health_findings": list(self.health_findings),
            "consistency_findings": list(self.consistency_findings),
            "runtime_classifications": list(self.runtime_classifications),
        }


def load_bridge_dispatch_config(project_root: Path) -> BridgeDispatchConfig:
    """Read ``config/dispatcher/rules.toml`` and return a tolerant config object."""
    path = project_root.resolve() / DISPATCH_CONFIG_RELATIVE_PATH
    if not path.exists():
        return BridgeDispatchConfig(path=path, exists=False, schema_version=1, errors=("dispatch config missing",))
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return BridgeDispatchConfig(path=path, exists=True, schema_version=1, errors=(str(exc),))
    if not isinstance(raw, dict):
        return BridgeDispatchConfig(path=path, exists=True, schema_version=1, errors=("top-level TOML is not a table",))

    harness_table = raw.get("harnesses", {})
    harnesses: dict[str, HarnessDispatchConfig] = {}
    if isinstance(harness_table, dict):
        for harness_id, row in harness_table.items():
            if isinstance(row, dict):
                harnesses[str(harness_id)] = HarnessDispatchConfig.from_mapping(str(harness_id), row)

    rules_raw = raw.get("rules", [])
    rules: list[DispatchRule] = []
    if isinstance(rules_raw, list):
        for row in rules_raw:
            if isinstance(row, dict):
                rules.append(DispatchRule.from_mapping(row))

    schema_version = _optional_int(raw.get("schema_version")) or 1
    selection_order = _string_tuple(raw.get("selection_order")) or DEFAULT_SELECTION_ORDER
    return BridgeDispatchConfig(
        path=path,
        exists=True,
        schema_version=schema_version,
        selection_order=selection_order,
        harnesses=harnesses,
        rules=tuple(rules),
    )


def apply_dispatch_config_to_record(
    record: dict[str, Any],
    config: BridgeDispatchConfig | None,
) -> dict[str, Any]:
    """Overlay dispatch config fields onto one projected harness record."""
    if config is None:
        return record
    harness_id = str(record.get("id") or "")
    overlay = config.overlay_for(harness_id)
    if overlay is None:
        return record
    updated = dict(record)
    if overlay.can_fire_events is not None:
        updated["can_fire_events"] = overlay.can_fire_events
        updated["event_driven_hooks"] = overlay.can_fire_events
    if overlay.can_receive_dispatch is not None:
        updated["can_receive_dispatch"] = overlay.can_receive_dispatch
    if overlay.dispatch_cost is not None:
        updated["dispatch_cost"] = overlay.dispatch_cost
    if overlay.dispatch_quality is not None:
        updated["dispatch_quality"] = overlay.dispatch_quality
    if overlay.dispatch_availability is not None:
        updated["dispatch_availability"] = overlay.dispatch_availability
    if overlay.max_items is not None:
        updated["dispatch_max_items"] = overlay.max_items
    if overlay.tags:
        updated["dispatch_tags"] = list(overlay.tags)
    return updated


def select_dispatch_candidates(
    records: list[dict[str, Any]],
    config: BridgeDispatchConfig,
    context: DispatchContext,
) -> list[dict[str, Any]]:
    """Return active, dispatchable records admitted by ``context``, ranked."""
    candidates: list[dict[str, Any]] = []
    order = config.selection_order_for(context)
    for raw in records:
        if not isinstance(raw, dict):
            continue
        record = apply_dispatch_config_to_record(dict(raw), config)
        if _record_status(record) != "active":
            continue
        roles = _record_roles(record)
        if context.required_role not in roles and not (
            context.required_role == ROLE_PRIME_BUILDER and "acting-prime-builder" in roles
        ):
            continue
        if record.get("can_receive_dispatch") is not True:
            continue
        if config.rules and not config.matching_rules(context):
            continue
        if not _passes_governance_grade_lo_quality_floor(record, context, order):
            continue
        candidates.append(record)
    return sorted(candidates, key=lambda record: _rank_key(record, order))


def collect_bridge_dispatch_status(project_root: Path) -> BridgeDispatchStatus:
    """Collect the current dispatch config and harness eligibility state."""
    root = project_root.resolve()
    config = load_bridge_dispatch_config(root)
    projection = _load_projection(root)
    raw_records = [record for record in projection.get("harnesses", []) if isinstance(record, dict)]
    records = tuple(apply_dispatch_config_to_record(dict(record), config) for record in raw_records)
    selected_by_role: dict[str, list[dict[str, Any]]] = {}
    findings: list[str] = []
    consistency_findings = _dispatch_config_consistency_findings(raw_records, config)

    if config.errors:
        findings.extend(f"config error: {error}" for error in config.errors)
    findings.extend(consistency_findings)

    active_event_sources = [
        record for record in records if _record_status(record) == "active" and record.get("can_fire_events") is True
    ]
    if not active_event_sources:
        findings.append("no active event-firing harness is available; scheduled wake fallback may be required")

    for role in DISPATCH_ROLES:
        context = DispatchContext(required_role=role)
        selected = select_dispatch_candidates(list(records), config, context)
        selected_by_role[role] = [_candidate_summary(record) for record in selected]
        role_holders = [
            record for record in records if _record_status(record) == "active" and role in _record_roles(record)
        ]
        if not role_holders:
            findings.append(f"no active harness holds role {role!r}")
        if not selected:
            findings.append(f"no active dispatchable harness is eligible for role {role!r}")

    runtime_findings, runtime_classifications = _runtime_dispatch_evaluation(root, selected_by_role)
    findings.extend(runtime_findings)

    health = (
        "FAIL"
        if any(
            "no active dispatchable" in finding
            or finding.startswith("config error")
            or finding.startswith("dispatch runtime failure")
            for finding in findings
        )
        else "PASS"
    )
    if health == "PASS" and findings:
        health = "WARN"
    return BridgeDispatchStatus(
        config=config,
        harnesses=tuple(_candidate_summary(record) for record in records),
        selected_by_role=selected_by_role,
        health_status=health,
        health_findings=tuple(findings),
        consistency_findings=tuple(consistency_findings),
        runtime_classifications=tuple(runtime_classifications),
    )


def format_bridge_dispatch_status(status: BridgeDispatchStatus) -> str:
    """Render a compact human-readable dispatch status report."""
    lines = [
        f"Bridge dispatch health: {status.health_status}",
        f"Config: {status.config.path}",
        "",
        "Harnesses:",
    ]
    for record in status.harnesses:
        roles = ", ".join(record.get("role", [])) or "(none)"
        lines.append(
            "- {id} {name}: roles=[{roles}], active={active}, dispatchable={dispatchable}, "
            "fires_events={fires}, cost={cost}, quality={quality}, availability={availability}".format(
                id=record.get("id"),
                name=record.get("harness_name"),
                roles=roles,
                active=record.get("status") == "active",
                dispatchable=record.get("can_receive_dispatch"),
                fires=record.get("can_fire_events"),
                cost=record.get("dispatch_cost"),
                quality=record.get("dispatch_quality"),
                availability=record.get("dispatch_availability"),
            )
        )
    lines.append("")
    lines.append("Selected candidates:")
    for role in DISPATCH_ROLES:
        ids = [str(row.get("id")) for row in status.selected_by_role.get(role, [])]
        lines.append(f"- {role}: {', '.join(ids) if ids else '(none)'}")
    if status.health_findings:
        lines.append("")
        lines.append("Findings:")
        lines.extend(f"- {finding}" for finding in status.health_findings)
    return "\n".join(lines)


def _load_projection(root: Path) -> dict[str, Any]:
    try:
        from groundtruth_kb.harness_projection import read_roles

        return read_roles(root)
    except Exception:  # intentional-catch: autogenerated check fix
        path = root / "harness-state" / "harness-registry.json"
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {"harnesses": []}
        except Exception:  # intentional-catch: autogenerated check fix
            return {"harnesses": []}


def _runtime_dispatch_findings(root: Path, selected_by_role: dict[str, list[dict[str, Any]]]) -> list[str]:
    findings, _classifications = _runtime_dispatch_evaluation(root, selected_by_role)
    return findings


def _runtime_dispatch_evaluation(
    root: Path,
    selected_by_role: dict[str, list[dict[str, Any]]],
) -> tuple[list[str], list[dict[str, Any]]]:
    state, errors = _load_dispatch_runtime_state(root)
    findings = list(errors)
    classifications: list[dict[str, Any]] = []
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return findings, classifications

    selected_keys: set[str] = set(DISPATCH_ROLES)
    for role, rows in selected_by_role.items():
        for row in rows:
            harness_id = str(row.get("id") or "").strip()
            if harness_id:
                selected_keys.add(f"{role}:{harness_id}")

    seen: set[str] = set()
    for recipient_key in sorted(selected_keys):
        row = recipients.get(recipient_key)
        if not isinstance(row, dict):
            continue
        classification = _runtime_classification_for_recipient(recipient_key, row)
        classifications.append(classification)
        for finding in classification["findings"]:
            if finding not in seen:
                findings.append(finding)
                seen.add(finding)
    return findings, classifications


def _load_dispatch_runtime_state(root: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    path = root / DISPATCH_STATE_RELATIVE_PATH
    if not path.exists():
        return {}, ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, (f"dispatch runtime warning: unable to read {DISPATCH_STATE_RELATIVE_PATH}: {exc}",)
    if not isinstance(payload, dict):
        return {}, (f"dispatch runtime warning: {DISPATCH_STATE_RELATIVE_PATH} is not a JSON object",)
    return payload, ()


def _runtime_findings_for_recipient(recipient_key: str, row: dict[str, Any]) -> list[str]:
    return list(_runtime_classification_for_recipient(recipient_key, row)["findings"])


def _runtime_classification_for_recipient(recipient_key: str, row: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    pending_count = _int_value(row.get("pending_count"), default=0)
    selected_count = _int_value(row.get("selected_count"), default=0)
    has_pending_work = pending_count > 0 or selected_count > 0
    failure_class = str(row.get("failure_class") or "").strip()
    last_result = str(row.get("last_result") or "").strip()
    last_launch = row.get("last_launch") if isinstance(row.get("last_launch"), dict) else {}
    launch_reason = str(last_launch.get("reason") or "").strip()
    launch_exit_failure = str(last_launch.get("exit_failure_reason") or "").strip()
    stale_failure_reason = _stale_failure_evidence_reason(recipient_key, row, last_launch)
    failure_evidence_present = any(
        (
            failure_class in RUNTIME_FAILURE_CLASSES,
            last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith("_dispatch_not_ready"),
            launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS,
            launch_exit_failure in RUNTIME_FAILURE_RESULTS | RUNTIME_FAILURE_CLASSES,
            row.get("circuit_breaker_tripped") is True,
        )
    )
    ignore_failure_fields = bool(stale_failure_reason and has_pending_work and failure_evidence_present)

    if ignore_failure_fields:
        findings.append(
            "dispatch runtime warning: "
            f"{recipient_key} stale failure evidence ignored ({stale_failure_reason}) "
            f"with pending_count={pending_count}"
        )

    if row.get("circuit_breaker_tripped") is True and has_pending_work and not ignore_failure_fields:
        findings.append(
            f"dispatch runtime failure: {recipient_key} circuit breaker is tripped with pending_count={pending_count}"
        )
    last_result_is_runtime_failure = last_result in RUNTIME_FAILURE_RESULTS or last_result.endswith(
        "_dispatch_not_ready"
    )
    # WI-4718: 'launch_failed' is the generic non-launch token written by the trigger
    # for ANY non-launch outcome; the specific cause is last_launch.reason. Defer to
    # it so benign backpressure is not misreported as a runtime failure. A genuine
    # launch reason (in RUNTIME_FAILURE_LAUNCH_REASONS, e.g. spawn_rate_limited) or
    # an absent reason still flags via the unchanged paths below.
    if last_result == "launch_failed" and launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS:
        last_result_is_runtime_failure = False
    if last_result_is_runtime_failure and has_pending_work and not ignore_failure_fields:
        findings.append(
            f"dispatch runtime failure: {recipient_key} last_result={last_result} with pending_count={pending_count}"
        )
    if last_result == "launch_failed" and launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS and has_pending_work:
        live = _int_value(last_launch.get("live_count", last_launch.get("per_role_live")), default=0)
        cap = _int_value(last_launch.get("cap", last_launch.get("per_role_cap")), default=0)
        findings.append(
            f"dispatch runtime warning: {recipient_key} saturated "
            f"(live_count={live}/cap={cap}, reason={launch_reason}) with pending_count={pending_count}"
        )
    if failure_class in RUNTIME_FAILURE_CLASSES and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} failure_class={failure_class} with pending_count={pending_count}"
        )
    if launch_reason in RUNTIME_FAILURE_LAUNCH_REASONS and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} last_launch.reason={launch_reason} with pending_count={pending_count}"
        )
    if (
        launch_exit_failure in RUNTIME_FAILURE_RESULTS | RUNTIME_FAILURE_CLASSES
        and has_pending_work
        and not ignore_failure_fields
    ):
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} last_launch.exit_failure_reason={launch_exit_failure} "
            f"with pending_count={pending_count}"
        )
    if launch_reason == "work_intent_acquire_failed" and has_pending_work and not ignore_failure_fields:
        findings.append(
            "dispatch runtime failure: "
            f"{recipient_key} work intent acquisition failed with pending_count={pending_count}"
        )
    fallback_skipped = row.get("fallback_skipped_candidates")
    if isinstance(fallback_skipped, list) and has_pending_work:
        for candidate in fallback_skipped:
            if not isinstance(candidate, dict):
                continue
            reason = str(candidate.get("reason") or "").strip()
            candidate_recipient = str(candidate.get("recipient") or candidate.get("harness_id") or "").strip()
            failure_label = str(candidate.get("failure_class") or "").strip()
            if reason in RUNTIME_FAILURE_RESULTS or reason.endswith("_dispatch_not_ready"):
                suffix = f", failure_class={failure_label}" if failure_label else ""
                findings.append(
                    "dispatch runtime failure: "
                    f"{recipient_key} skipped fallback {candidate_recipient} reason={reason}{suffix} "
                    f"with pending_count={pending_count}"
                )
    if last_result == "unchanged" and has_pending_work:
        findings.append(
            f"dispatch runtime warning: {recipient_key} last_result=unchanged with pending_count={pending_count}"
        )
    quarantined_threads = row.get("quarantined_threads")
    if isinstance(quarantined_threads, list) and quarantined_threads:
        slugs: list[str] = []
        for entry in quarantined_threads:
            if isinstance(entry, dict):
                slug = entry.get("slug")
                if isinstance(slug, str) and slug:
                    slugs.append(slug)
        unique_slugs = sorted(set(slugs))
        if unique_slugs:
            findings.append(
                f"dispatch runtime warning: {recipient_key} has "
                f"{len(unique_slugs)} bridge thread(s) quarantined for malformed status token: "
                f"{unique_slugs}"
            )
    severity = "PASS"
    if any(finding.startswith("dispatch runtime failure") for finding in findings):
        severity = "FAIL"
    elif findings:
        severity = "WARN"
    return {
        "recipient": recipient_key,
        "severity": severity,
        "pending_count": pending_count,
        "selected_count": selected_count,
        "last_result": last_result or None,
        "failure_class": failure_class or None,
        "last_launch_reason": launch_reason or None,
        "last_launch_exit_failure_reason": launch_exit_failure or None,
        "stale_failure_evidence": bool(stale_failure_reason),
        "stale_failure_reason": stale_failure_reason,
        "findings": tuple(findings),
    }


def _stale_failure_evidence_reason(
    recipient_key: str,
    row: dict[str, Any],
    last_launch: dict[str, Any],
) -> str | None:
    if ":" not in recipient_key:
        return None
    expected = recipient_key.strip()
    evidence_recipients = _recipient_evidence_values(row, last_launch)
    if not evidence_recipients or expected in evidence_recipients:
        return None
    return "recipient evidence points to " + ", ".join(sorted(evidence_recipients))


def _recipient_evidence_values(row: dict[str, Any], last_launch: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    _add_recipient_evidence(values, last_launch.get("recipient"))
    selected_candidate = last_launch.get("selected_candidate")
    if isinstance(selected_candidate, dict):
        _add_recipient_evidence(values, selected_candidate.get("recipient"))
    row_candidate = row.get("selected_candidate")
    if isinstance(row_candidate, dict):
        _add_recipient_evidence(values, row_candidate.get("recipient"))
    return values


def _add_recipient_evidence(values: set[str], value: Any) -> None:
    if isinstance(value, str) and value.strip():
        values.add(value.strip())


def _dispatch_config_consistency_findings(
    raw_records: list[dict[str, Any]],
    config: BridgeDispatchConfig,
) -> list[str]:
    findings: list[str] = []
    for raw in raw_records:
        harness_id = str(raw.get("id") or "").strip()
        if not harness_id:
            continue
        overlay = config.overlay_for(harness_id)
        if overlay is None:
            continue
        if overlay.can_receive_dispatch is not None:
            raw_receive = _optional_bool(raw.get("can_receive_dispatch"))
            if raw_receive is not None and raw_receive != overlay.can_receive_dispatch:
                findings.append(
                    "dispatch config drift warning: "
                    f"harness {harness_id} can_receive_dispatch "
                    f"rules.toml={overlay.can_receive_dispatch} harness-registry={raw_receive}"
                )
            if overlay.can_receive_dispatch is True and _record_status(raw) != "active":
                findings.append(
                    "dispatch config drift warning: "
                    f"harness {harness_id} can_receive_dispatch rules.toml=True "
                    f"but harness-registry status={_record_status(raw) or '(missing)'}"
                )
        if overlay.can_fire_events is not None:
            raw_fire = _optional_bool(raw.get("can_fire_events"))
            if raw_fire is not None and raw_fire != overlay.can_fire_events:
                findings.append(
                    "dispatch config drift warning: "
                    f"harness {harness_id} can_fire_events "
                    f"rules.toml={overlay.can_fire_events} harness-registry={raw_fire}"
                )
            raw_hooks = _optional_bool(raw.get("event_driven_hooks"))
            if raw_hooks is not None and raw_hooks != overlay.can_fire_events:
                findings.append(
                    "dispatch config drift warning: "
                    f"harness {harness_id} event_driven_hooks "
                    f"rules.toml={overlay.can_fire_events} harness-registry={raw_hooks}"
                )
    return findings


def _candidate_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "harness_name": record.get("harness_name"),
        "harness_type": record.get("harness_type"),
        "role": sorted(_record_roles(record)),
        "status": record.get("status"),
        "can_receive_dispatch": record.get("can_receive_dispatch"),
        "can_fire_events": record.get("can_fire_events"),
        "event_driven_hooks": record.get("event_driven_hooks"),
        "reviewer_precedence": record.get("reviewer_precedence"),
        "dispatch_cost": record.get("dispatch_cost"),
        "dispatch_quality": record.get("dispatch_quality"),
        "dispatch_availability": record.get("dispatch_availability"),
        "dispatch_max_items": record.get("dispatch_max_items"),
    }


def _rank_key(record: dict[str, Any], order: tuple[str, ...]) -> tuple[Any, ...]:
    values: list[Any] = []
    for sort_field in order:
        name = sort_field.strip().lower()
        if name in {"availability", "dispatch_availability"}:
            values.append(-_float_value(record.get("dispatch_availability"), default=50.0))
        elif name in {"cost", "dispatch_cost"}:
            values.append(_float_value(record.get("dispatch_cost"), default=50.0))
        elif name in {"quality", "dispatch_quality"}:
            values.append(-_float_value(record.get("dispatch_quality"), default=50.0))
        elif name == "reviewer_precedence":
            values.append(_int_value(record.get("reviewer_precedence"), default=1_000_000))
        elif name in {"harness_id", "id"}:
            values.append(str(record.get("id") or ""))
        else:
            values.append(str(record.get(name) or ""))
    values.append(str(record.get("id") or ""))
    return tuple(values)


def _passes_governance_grade_lo_quality_floor(
    record: dict[str, Any],
    context: DispatchContext,
    order: tuple[str, ...],
) -> bool:
    if context.required_role != ROLE_LOYAL_OPPOSITION:
        return True
    if not _selection_order_includes_quality(order):
        return True
    quality = _float_value(record.get("dispatch_quality"), default=50.0)
    return quality >= GOVERNANCE_GRADE_LO_MIN_QUALITY


def _selection_order_includes_quality(order: tuple[str, ...]) -> bool:
    return any(name.strip().lower() in {"quality", "dispatch_quality"} for name in order)


def _role_only_match(rule: DispatchRule, role: str) -> bool:
    lowered = role.strip().lower()
    return lowered in {r.lower() for r in rule.required_roles} and lowered not in {
        r.lower() for r in rule.blocked_roles
    }


def _record_status(record: dict[str, Any]) -> str:
    return str(record.get("status") or "").strip().lower()


def _record_roles(record: dict[str, Any]) -> set[str]:
    role = record.get("role")
    if isinstance(role, str):
        return {role.strip().lower()} if role.strip() else set()
    if isinstance(role, (list, tuple, set, frozenset)):
        return {str(item).strip().lower() for item in role if str(item).strip()}
    return set()


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _float_value(value: Any, *, default: float) -> float:
    parsed = _optional_float(value)
    return default if parsed is None else parsed


def _int_value(value: Any, *, default: int) -> int:
    parsed = _optional_int(value)
    return default if parsed is None else parsed


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())
