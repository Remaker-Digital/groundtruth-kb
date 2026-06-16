"""TAFE live implementation-flow pilot (WI-4495, re-cast).

This module is the **live, enforcing, parity-checking** layer over the generic
Typed Artifact-Flow Engine (TAFE) runtime. Given a single designated real bridge
thread slug, it:

1. reads the thread's canonical latest status from injected ``bridge/INDEX.md``
   text (read-only; the caller supplies the text, this module never opens a
   file);
2. gets-or-creates a TAFE ``flow_instance`` for the thread under the canonical
   ``implementation`` flow definition;
3. drives the flow's ``stage_instances`` toward the stage that corresponds to
   the thread's current bridge status, ENFORCING the definition's declared
   constraints — legal ``stage_sequence`` transition order,
   ``required_roles_by_stage``, and ``never_self_review_stages`` (checked against
   the real thread's per-version authors, injected as ``actors``);
4. computes a **semantic parity verdict** between the canonical bridge status and
   the TAFE projection; and
5. records an append-only ``flow_event`` carrying the verdict + findings.

The pilot runs in **parallel/shadow**: it performs **no write to
``bridge/INDEX.md``** and never changes its authority. ``bridge/INDEX.md``
remains canonical per ``GOV-FILE-BRIDGE-AUTHORITY-001``; when the TAFE projection
diverges from the canonical status, the divergence is recorded as a finding and
**the canonical index wins** — TAFE never overrides it.

Purity boundary: this module performs no file I/O, no subprocess, and never
references the canonical bridge-index path literal. It mutates only TAFE runtime
rows through the public service API and reads only the ``index_text`` the caller
injects. The human-readable preview string is produced by the WI-4507 renderer
(``render_tafe_bridge_index_preview``), which is itself pure.

Specification links: ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (live,
enforcing, parallel-run half), ``SPEC-TAFE-R1`` (ordered, role-gated stage
routing), ``SPEC-TAFE-R7`` (MemBase canonical; public-API-only access),
``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical INDEX preserved; divergence favors
canonical).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from groundtruth_kb.tafe_index_preview import render_tafe_bridge_index_preview
from groundtruth_kb.tafe_index_sync import parse_bridge_index
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

#: The canonical flow definition this pilot drives (``flow_type``/``id`` both
#: ``implementation`` per ``CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS``).
IMPLEMENTATION_FLOW_DEFINITION_ID = "implementation"

#: Sentinel logical status for a post-implementation ``NEW`` report (a fresh
#: ``NEW`` version filed *after* a ``GO`` already appeared in the version chain).
#: It maps to ``verify`` rather than ``propose``.
POST_IMPL_NEW = "POST_IMPL_NEW"

#: Fixed map from a bridge thread's (logical) latest status to the implementation
#: flow stage that status corresponds to. ``NEW`` is disambiguated upstream into
#: either ``NEW`` (initial proposal -> ``propose``) or ``POST_IMPL_NEW``
#: (post-impl report -> ``verify``) by :func:`expected_stage_for_thread`.
BRIDGE_STATUS_TO_STAGE: dict[str, str] = {
    "NEW": "propose",
    "REVISED": "propose",
    "NO-GO": "review",
    "GO": "implement",
    POST_IMPL_NEW: "verify",
    "VERIFIED": "complete",
}

__all__ = [
    "IMPLEMENTATION_FLOW_DEFINITION_ID",
    "POST_IMPL_NEW",
    "BRIDGE_STATUS_TO_STAGE",
    "ThreadStatus",
    "EnforcementResult",
    "LivePilotResult",
    "parse_index_thread_status",
    "expected_stage_for_thread",
    "is_legal_transition",
    "evaluate_enforcement",
    "run_live_pilot",
]


@dataclass(frozen=True)
class ThreadStatus:
    """The canonical status of one bridge thread, parsed read-only from INDEX.

    ``version_statuses`` is the thread block's full status chain, latest-first
    (``version_statuses[0]`` is the latest). ``has_prior_go`` is ``True`` when a
    ``GO`` appears *below* the latest entry — the signal that a latest ``NEW`` is
    a post-implementation report rather than a fresh proposal.
    """

    slug: str
    latest_status: str
    latest_version: int
    version_statuses: tuple[str, ...]

    @property
    def has_prior_go(self) -> bool:
        return any(status == "GO" for status in self.version_statuses[1:])


@dataclass(frozen=True)
class EnforcementResult:
    """The outcome of driving TAFE toward an expected stage under enforcement.

    ``reachable_stage`` is the furthest stage TAFE could legally reach; it equals
    ``expected_stage`` exactly when no enforcement constraint blocked the drive.
    """

    expected_stage: str | None
    reachable_stage: str | None
    parity_ok: bool
    divergences: tuple[str, ...] = field(default_factory=tuple)
    never_self_review_violations: tuple[str, ...] = field(default_factory=tuple)
    role_violations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LivePilotResult:
    """Immutable result of one live-pilot run on a designated bridge thread."""

    slug: str
    latest_status: str
    expected_stage: str | None
    actual_stage: str | None
    parity_ok: bool
    divergences: tuple[str, ...]
    never_self_review_violations: tuple[str, ...]
    role_violations: tuple[str, ...]
    flow_instance_id: str
    flow_event_id: str
    preview_text: str


def parse_index_thread_status(index_text: str, slug: str) -> ThreadStatus | None:
    """Parse the latest canonical status of ``slug`` from ``index_text``.

    Read-only: ``index_text`` is the verbatim contents of ``bridge/INDEX.md``
    supplied by the caller. Returns ``None`` when the slug has no
    ``Document:`` block or the block carries no canonical version line.
    """

    parsed = parse_bridge_index(index_text)
    for block in parsed.blocks:
        if block.name != slug:
            continue
        if not block.version_lines:
            return None
        statuses = tuple(line.status for line in block.version_lines)
        latest = block.version_lines[0]
        return ThreadStatus(
            slug=slug,
            latest_status=latest.status,
            latest_version=latest.version,
            version_statuses=statuses,
        )
    return None


def expected_stage_for_thread(thread_status: ThreadStatus) -> str | None:
    """Map a thread's canonical latest status to its expected TAFE stage.

    Applies the post-implementation ``NEW`` disambiguation: a latest ``NEW`` with
    a ``GO`` already in the version chain is a verification report and maps to
    ``verify``; an initial ``NEW`` maps to ``propose``. Returns ``None`` for
    statuses outside the implementation flow (e.g. ``WITHDRAWN``, ``DEFERRED``,
    ``ADVISORY``).
    """

    logical = thread_status.latest_status
    if logical == "NEW" and thread_status.has_prior_go:
        logical = POST_IMPL_NEW
    return BRIDGE_STATUS_TO_STAGE.get(logical)


def is_legal_transition(
    from_stage: str | None,
    to_stage: str,
    *,
    stage_sequence: Sequence[str],
) -> bool:
    """Return ``True`` when advancing ``from_stage`` -> ``to_stage`` is legal.

    A legal transition either enters the first stage from ``None`` (flow start)
    or advances to the immediately-following stage in ``stage_sequence``. Skips,
    backward moves, and unknown stages are illegal.
    """

    sequence = list(stage_sequence)
    if to_stage not in sequence:
        return False
    to_index = sequence.index(to_stage)
    if from_stage is None:
        return to_index == 0
    if from_stage not in sequence:
        return False
    return to_index == sequence.index(from_stage) + 1


def evaluate_enforcement(
    *,
    stage_sequence: Sequence[str],
    required_roles_by_stage: Mapping[str, str],
    never_self_review_stages: Sequence[str],
    expected_stage: str | None,
    actors: Mapping[str, str],
    actor_roles: Mapping[str, str] | None = None,
) -> EnforcementResult:
    """Drive a flow toward ``expected_stage`` enforcing the definition's rules.

    Walks the ``stage_sequence`` from the first stage toward ``expected_stage``,
    one legal transition at a time. At each stage it enforces, in order:

    * **required role** — when an actor is known for the stage and ``actor_roles``
      supplies that actor's role, the role must equal
      ``required_roles_by_stage[stage]``;
    * **never-self-review** — for a stage in ``never_self_review_stages``, its
      actor must differ from the actor of the immediately-preceding stage (the
      artifact being reviewed/verified).

    The drive stops at the first blocked stage. ``parity_ok`` is ``True`` only
    when the reachable stage equals ``expected_stage``. A pure function: no I/O,
    no mutation.
    """

    sequence = list(stage_sequence)
    never_self_review = set(never_self_review_stages)
    divergences: list[str] = []
    role_violations: list[str] = []
    never_self_review_violations: list[str] = []

    if expected_stage is None:
        return EnforcementResult(
            expected_stage=None,
            reachable_stage=None,
            parity_ok=False,
            divergences=("bridge status maps to no implementation-flow stage",),
        )
    if expected_stage not in sequence:
        return EnforcementResult(
            expected_stage=expected_stage,
            reachable_stage=None,
            parity_ok=False,
            divergences=(f"expected stage {expected_stage!r} is not in the implementation sequence",),
        )

    expected_index = sequence.index(expected_stage)
    reachable: str | None = None

    for index in range(expected_index + 1):
        stage = sequence[index]
        # Transition legality is guaranteed by sequential iteration, but assert it
        # so an accidental refactor that reorders the walk is caught.
        if not is_legal_transition(reachable, stage, stage_sequence=sequence):
            divergences.append(f"illegal transition {reachable!r} -> {stage!r}")
            break

        actor = actors.get(stage)
        required_role = required_roles_by_stage.get(stage)

        if (
            actor_roles is not None
            and actor is not None
            and actor in actor_roles
            and required_role is not None
            and actor_roles[actor] != required_role
        ):
            role_violations.append(
                f"stage {stage!r} requires role {required_role!r} but actor {actor!r} holds {actor_roles[actor]!r}"
            )
            break

        if stage in never_self_review and index > 0:
            prev_stage = sequence[index - 1]
            prev_actor = actors.get(prev_stage)
            if actor is not None and prev_actor is not None and actor == prev_actor:
                never_self_review_violations.append(
                    f"never-self-review violation at stage {stage!r}: actor {actor!r} also performed {prev_stage!r}"
                )
                break

        reachable = stage

    parity_ok = reachable == expected_stage
    if not parity_ok and not divergences:
        divergences.append(f"expected stage {expected_stage!r}, TAFE enforcement reached {reachable!r}")

    return EnforcementResult(
        expected_stage=expected_stage,
        reachable_stage=reachable,
        parity_ok=parity_ok,
        divergences=tuple(divergences),
        never_self_review_violations=tuple(never_self_review_violations),
        role_violations=tuple(role_violations),
    )


def _ensure_implementation_definition(service: TypedArtifactFlowService, *, changed_by: str) -> dict[str, Any]:
    """Return the seeded ``implementation`` flow definition, seeding if absent."""

    definition = service.get_flow_definition(IMPLEMENTATION_FLOW_DEFINITION_ID)
    if definition is None:
        service.seed_reviewed_task_flow_definitions(
            changed_by=changed_by,
            change_reason="seed canonical reviewed-task flow definitions for the live implementation-flow pilot",
        )
        definition = service.get_flow_definition(IMPLEMENTATION_FLOW_DEFINITION_ID)
    if definition is None:  # pragma: no cover - defensive; seed is idempotent
        raise RuntimeError("implementation flow definition could not be seeded")
    return definition


def _get_or_create_flow_instance(
    service: TypedArtifactFlowService,
    *,
    slug: str,
    changed_by: str,
) -> dict[str, Any]:
    """Find the pilot flow instance for ``slug`` or create a fresh one."""

    flow_instance_id = f"FLOWINST-PILOT-{slug}"
    existing = service.get_flow_instance(flow_instance_id)
    if existing is not None:
        return existing
    return service.create_flow_instance(
        id=flow_instance_id,
        flow_definition_id=IMPLEMENTATION_FLOW_DEFINITION_ID,
        subject_type="bridge-thread",
        subject_id=slug,
        status="in_progress",
        metadata={"pilot": True, "parallel_shadow": True},
        changed_by=changed_by,
        change_reason=f"live implementation-flow pilot for bridge thread {slug}",
    )


def _drive_stage_instances(
    service: TypedArtifactFlowService,
    *,
    flow_instance_id: str,
    stage_sequence: Sequence[str],
    required_roles_by_stage: Mapping[str, str],
    never_self_review_stages: Sequence[str],
    reachable_stage: str | None,
    changed_by: str,
) -> None:
    """Create any missing stage instances up to ``reachable_stage`` (idempotent).

    Stage instances carry deterministic IDs so repeated pilot runs do not append
    redundant versions for stages that already exist.
    """

    if reachable_stage is None:
        return
    sequence = list(stage_sequence)
    never_self_review = set(never_self_review_stages)
    reachable_index = sequence.index(reachable_stage)
    existing_ids = {row["id"] for row in service.list_stage_instances(flow_instance_id=flow_instance_id)}
    for index in range(reachable_index + 1):
        stage_id = sequence[index]
        stage_instance_id = f"{flow_instance_id}-stage-{index}-{stage_id}"
        if stage_instance_id in existing_ids:
            continue
        service.create_stage_instance(
            id=stage_instance_id,
            flow_instance_id=flow_instance_id,
            stage_id=stage_id,
            stage_index=index,
            required_role=required_roles_by_stage[stage_id],
            status="completed" if index < reachable_index else "active",
            metadata={"never_self_review": stage_id in never_self_review},
            changed_by=changed_by,
            change_reason=f"pilot drive: stage {stage_id} for {flow_instance_id}",
        )


def run_live_pilot(
    slug: str,
    *,
    service: TypedArtifactFlowService,
    index_text: str,
    now: str | datetime,
    actors: Mapping[str, str] | None = None,
    actor_roles: Mapping[str, str] | None = None,
    changed_by: str = "prime-builder/tafe-live-pilot",
) -> LivePilotResult:
    """Run the live implementation-flow pilot on one designated bridge thread.

    Reads the thread's canonical latest status from ``index_text`` (read-only),
    drives a parallel/shadow TAFE implementation flow under enforcement, computes
    the semantic parity verdict, records a ``flow_event`` carrying the verdict +
    findings, and returns the structured result. Performs no write to
    ``bridge/INDEX.md`` and changes none of its authority; divergence is recorded
    and the canonical index wins.
    """

    actors = dict(actors or {})

    thread_status = parse_index_thread_status(index_text, slug)
    if thread_status is None:
        raise ValueError(f"bridge thread {slug!r} not found in the supplied index text")

    definition = _ensure_implementation_definition(service, changed_by=changed_by)
    stage_sequence = list(definition["stage_sequence_parsed"])
    required_roles_by_stage = dict(definition["required_roles_by_stage_parsed"])
    never_self_review_stages = list(definition["never_self_review_stages_parsed"])

    expected_stage = expected_stage_for_thread(thread_status)
    enforcement = evaluate_enforcement(
        stage_sequence=stage_sequence,
        required_roles_by_stage=required_roles_by_stage,
        never_self_review_stages=never_self_review_stages,
        expected_stage=expected_stage,
        actors=actors,
        actor_roles=actor_roles,
    )

    flow_instance = _get_or_create_flow_instance(service, slug=slug, changed_by=changed_by)
    flow_instance_id = flow_instance["id"]

    _drive_stage_instances(
        service,
        flow_instance_id=flow_instance_id,
        stage_sequence=stage_sequence,
        required_roles_by_stage=required_roles_by_stage,
        never_self_review_stages=never_self_review_stages,
        reachable_stage=enforcement.reachable_stage,
        changed_by=changed_by,
    )

    # Build the non-authoritative preview from current TAFE state via the pure
    # WI-4507 renderer. The pilot flow appears alongside any other TAFE flows.
    preview = render_tafe_bridge_index_preview(
        service.list_flow_instances(),
        service.list_stage_instances(),
        now=now,
    )

    event_payload = {
        "slug": slug,
        "latest_status": thread_status.latest_status,
        "latest_version": thread_status.latest_version,
        "expected_stage": enforcement.expected_stage,
        "actual_stage": enforcement.reachable_stage,
        "parity_ok": enforcement.parity_ok,
        "divergences": list(enforcement.divergences),
        "never_self_review_violations": list(enforcement.never_self_review_violations),
        "role_violations": list(enforcement.role_violations),
        "canonical_wins": True,
    }
    # Deterministic event ID keyed on (slug, latest_version): one parity verdict
    # per canonical thread version. Get-or-create keeps the whole pilot run
    # idempotent on rerun (mirroring the flow-instance and stage-instance
    # get-or-create above); a same-version rerun reuses the recorded verdict
    # instead of colliding on the UNIQUE(flow_events.id) constraint. A genuine
    # status advance bumps latest_version, yielding a fresh append-only event.
    event_id = f"FLOWEVENT-PILOT-{slug}-v{thread_status.latest_version}"
    flow_event = service.get_flow_event(event_id)
    if flow_event is None:
        flow_event = service.record_flow_event(
            id=event_id,
            flow_instance_id=flow_instance_id,
            event_type="live_pilot_parity_verdict",
            stage_instance_id=None,
            event_payload=event_payload,
            changed_by=changed_by,
            change_reason=(
                f"live pilot parity verdict for {slug}: {'MATCH' if enforcement.parity_ok else 'DIVERGENCE'}"
            ),
        )

    return LivePilotResult(
        slug=slug,
        latest_status=thread_status.latest_status,
        expected_stage=enforcement.expected_stage,
        actual_stage=enforcement.reachable_stage,
        parity_ok=enforcement.parity_ok,
        divergences=enforcement.divergences,
        never_self_review_violations=enforcement.never_self_review_violations,
        role_violations=enforcement.role_violations,
        flow_instance_id=flow_instance_id,
        flow_event_id=flow_event["id"],
        preview_text=preview.text,
    )
