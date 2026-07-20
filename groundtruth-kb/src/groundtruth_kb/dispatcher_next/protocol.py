"""Deterministic, in-memory A2A task protocol for the Dispatcher Next spike.

The facade exercises the official A2A protobuf contract without importing the
live dispatcher, opening a network connection, or launching a harness.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from threading import RLock
from typing import Final, Literal, TypeAlias, cast

from a2a.types import Artifact, Message, Part, Role, Task, TaskState, TaskStatus
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import DecodeError
from google.protobuf.struct_pb2 import Value
from google.protobuf.timestamp_pb2 import Timestamp

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
TerminalOutcome: TypeAlias = Literal["completed", "failed", "canceled"]

_SUBMITTED: Final[int] = TaskState.TASK_STATE_SUBMITTED
_WORKING: Final[int] = TaskState.TASK_STATE_WORKING
_COMPLETED: Final[int] = TaskState.TASK_STATE_COMPLETED
_FAILED: Final[int] = TaskState.TASK_STATE_FAILED
_CANCELED: Final[int] = TaskState.TASK_STATE_CANCELED
_MAX_SAFE_JSON_INTEGER: Final[int] = (1 << 53) - 1
_TERMINAL_STATES: Final[frozenset[int]] = frozenset({_COMPLETED, _FAILED, _CANCELED})
_ALLOWED_TRANSITIONS: Final[dict[int, frozenset[int]]] = {
    _SUBMITTED: frozenset({_WORKING}),
    _WORKING: _TERMINAL_STATES,
}


class A2AProtocolError(ValueError):
    """Base exception for fail-closed protocol operations."""


class TaskAlreadyExistsError(A2AProtocolError):
    """Raised when a caller attempts to submit a duplicate task ID."""


class TaskNotFoundError(A2AProtocolError):
    """Raised when a caller references an unknown task ID."""


class InvalidTaskTransitionError(A2AProtocolError):
    """Raised when a task transition is invalid or repeats a terminal state."""


@dataclass(frozen=True)
class LifecycleEvidence:
    """One deterministic transition observation."""

    sequence: int
    from_state: str | None
    to_state: str
    message_id: str
    artifact_id: str | None
    task_sha256: str

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a compact JSON-friendly representation."""

        return {
            "sequence": self.sequence,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "message_id": self.message_id,
            "artifact_id": self.artifact_id,
            "task_sha256": self.task_sha256,
        }


@dataclass(frozen=True)
class LifecycleResult:
    """JSON-friendly snapshot of a task and its transition evidence."""

    schema_version: int
    task_id: str
    context_id: str
    state: str
    terminal: bool
    artifact: JsonValue
    diagnostic: str | None
    evidence: tuple[LifecycleEvidence, ...]

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a representation suitable for JSON encoding and assertions."""

        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "context_id": self.context_id,
            "state": self.state,
            "terminal": self.terminal,
            "artifact": self.artifact,
            "diagnostic": self.diagnostic,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass
class _TaskRecord:
    task: Task
    evidence: list[LifecycleEvidence]


def serialize_task(task: Task) -> bytes:
    """Serialize an A2A task deterministically with protobuf."""

    if not isinstance(task, Task):
        raise TypeError("task must be an a2a.types.Task")
    return task.SerializeToString(deterministic=True)


def parse_task(payload: bytes) -> Task:
    """Parse serialized protobuf bytes into an independent A2A task."""

    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    task = Task()
    try:
        task.ParseFromString(payload)
    except DecodeError as exc:
        raise A2AProtocolError("payload is not a valid serialized A2A task") from exc
    if not task.id or not task.context_id:
        raise A2AProtocolError("serialized A2A task must include id and context_id")
    try:
        _state_name(task.status.state)
    except ValueError as exc:
        raise A2AProtocolError("serialized A2A task has an unsupported state") from exc
    return task


def round_trip_task(task: Task) -> Task:
    """Serialize and parse a task to prove protobuf wire compatibility."""

    return parse_task(serialize_task(task))


def task_to_dict(task: Task) -> dict[str, JsonValue]:
    """Convert an A2A task to a protobuf-aware JSON-friendly dictionary."""

    if not isinstance(task, Task):
        raise TypeError("task must be an a2a.types.Task")
    converted = MessageToDict(task, preserving_proto_field_name=True)
    return cast(dict[str, JsonValue], converted)


class A2AProtocolFacade:
    """Strict in-memory state machine over A2A protobuf task types."""

    def __init__(self) -> None:
        self._records: dict[str, _TaskRecord] = {}
        self._lock = RLock()

    def submit(
        self,
        task_id: str,
        context_id: str,
        request: str | Mapping[str, object],
    ) -> Task:
        """Create a task in ``submitted`` with one deterministic user message."""

        normalized_task_id = _identifier("task_id", task_id)
        normalized_context_id = _identifier("context_id", context_id)
        request_part = _request_part(request)
        with self._lock:
            if normalized_task_id in self._records:
                raise TaskAlreadyExistsError(f"task {normalized_task_id!r} already exists")

            message = Message(
                message_id=_message_id(normalized_task_id, 0, "submitted"),
                context_id=normalized_context_id,
                task_id=normalized_task_id,
                role=Role.ROLE_USER,
                parts=[request_part],
            )
            task = Task(
                id=normalized_task_id,
                context_id=normalized_context_id,
                status=_status(_SUBMITTED, message, sequence=0),
                history=[message],
            )
            record = _TaskRecord(task=task, evidence=[])
            self._append_evidence(
                record,
                sequence=0,
                from_state=None,
                to_state=_SUBMITTED,
                message_id=message.message_id,
                artifact_id=None,
            )
            self._records[normalized_task_id] = record
            return round_trip_task(task)

    def start(self, task_id: str) -> Task:
        """Move a submitted task to ``working``."""

        return self._transition_with_message(
            task_id,
            target_state=_WORKING,
            text="working",
        )

    def complete(
        self,
        task_id: str,
        result: Mapping[str, object],
        *,
        artifact_name: str = "result",
    ) -> Task:
        """Complete a working task with exactly one structured A2A artifact."""

        normalized_name = _identifier("artifact_name", artifact_name)
        structured_result = _normalize_json(result)
        if not isinstance(structured_result, dict):
            raise A2AProtocolError("completion result must be a JSON object")

        with self._lock:
            record = self._record(task_id)
            self._require_transition(record, _COMPLETED)
            sequence = len(record.evidence)
            message = _agent_message(record.task, sequence, "completed", "completed")
            artifact = Artifact(
                artifact_id=f"{record.task.id}:artifact:{sequence}",
                name=normalized_name,
                description="Structured Dispatcher Next task result",
                parts=[Part(data=_protobuf_value(structured_result))],
            )
            record.task.artifacts.append(artifact)
            self._apply_status(record, _COMPLETED, message, sequence)
            self._append_evidence(
                record,
                sequence=sequence,
                from_state=_WORKING,
                to_state=_COMPLETED,
                message_id=message.message_id,
                artifact_id=artifact.artifact_id,
            )
            return round_trip_task(record.task)

    def fail(self, task_id: str, diagnostic: str) -> Task:
        """Fail a working task with a diagnostic agent message."""

        return self._transition_with_message(
            task_id,
            target_state=_FAILED,
            text=_non_empty("diagnostic", diagnostic),
        )

    def cancel(self, task_id: str, reason: str) -> Task:
        """Explicitly cancel a working task with an agent-authored reason."""

        return self._transition_with_message(
            task_id,
            target_state=_CANCELED,
            text=_non_empty("reason", reason),
        )

    def task(self, task_id: str) -> Task:
        """Return an independent protobuf copy of the current task."""

        with self._lock:
            return round_trip_task(self._record(task_id).task)

    def evidence(self, task_id: str) -> tuple[LifecycleEvidence, ...]:
        """Return immutable transition evidence for a task."""

        with self._lock:
            return tuple(self._record(task_id).evidence)

    def result(self, task_id: str) -> LifecycleResult:
        """Return a compact task result without exposing mutable protobuf state."""

        with self._lock:
            record = self._record(task_id)
            task = record.task
            state = task.status.state
            artifact: JsonValue = None
            if state == _COMPLETED:
                if len(task.artifacts) != 1 or len(task.artifacts[0].parts) != 1:
                    raise A2AProtocolError("completed task must contain exactly one structured artifact")
                part = task.artifacts[0].parts[0]
                if part.WhichOneof("content") != "data":
                    raise A2AProtocolError("completed task artifact must contain structured data")
                artifact = cast(JsonValue, MessageToDict(part.data))

            diagnostic = None
            if state in {_FAILED, _CANCELED}:
                diagnostic = _message_text(task.status.message)

            return LifecycleResult(
                schema_version=1,
                task_id=task.id,
                context_id=task.context_id,
                state=_state_name(state),
                terminal=state in _TERMINAL_STATES,
                artifact=artifact,
                diagnostic=diagnostic,
                evidence=tuple(record.evidence),
            )

    def _transition_with_message(self, task_id: str, *, target_state: int, text: str) -> Task:
        with self._lock:
            record = self._record(task_id)
            previous_state = record.task.status.state
            self._require_transition(record, target_state)
            sequence = len(record.evidence)
            state_name = _state_name(target_state)
            message = _agent_message(record.task, sequence, state_name, text)
            self._apply_status(record, target_state, message, sequence)
            self._append_evidence(
                record,
                sequence=sequence,
                from_state=previous_state,
                to_state=target_state,
                message_id=message.message_id,
                artifact_id=None,
            )
            return round_trip_task(record.task)

    def _record(self, task_id: str) -> _TaskRecord:
        normalized_task_id = _identifier("task_id", task_id)
        try:
            return self._records[normalized_task_id]
        except KeyError as exc:
            raise TaskNotFoundError(f"task {normalized_task_id!r} does not exist") from exc

    @staticmethod
    def _require_transition(record: _TaskRecord, target_state: int) -> None:
        current_state = record.task.status.state
        if current_state in _TERMINAL_STATES:
            raise InvalidTaskTransitionError(
                f"task {record.task.id!r} is already terminal in {_state_name(current_state)!r}"
            )
        allowed = _ALLOWED_TRANSITIONS.get(current_state, frozenset())
        if target_state not in allowed:
            raise InvalidTaskTransitionError(
                f"task {record.task.id!r} cannot transition "
                f"from {_state_name(current_state)!r} to {_state_name(target_state)!r}"
            )

    @staticmethod
    def _apply_status(
        record: _TaskRecord,
        target_state: int,
        message: Message,
        sequence: int,
    ) -> None:
        record.task.status.CopyFrom(_status(target_state, message, sequence))
        record.task.history.append(message)

    @staticmethod
    def _append_evidence(
        record: _TaskRecord,
        *,
        sequence: int,
        from_state: int | None,
        to_state: int,
        message_id: str,
        artifact_id: str | None,
    ) -> None:
        record.evidence.append(
            LifecycleEvidence(
                sequence=sequence,
                from_state=None if from_state is None else _state_name(from_state),
                to_state=_state_name(to_state),
                message_id=message_id,
                artifact_id=artifact_id,
                task_sha256=hashlib.sha256(serialize_task(record.task)).hexdigest(),
            )
        )


def run_lifecycle(
    *,
    task_id: str,
    context_id: str,
    request: str | Mapping[str, object],
    outcome: TerminalOutcome,
    result: Mapping[str, object] | None = None,
    detail: str | None = None,
) -> LifecycleResult:
    """Exercise one complete deterministic lifecycle for focused tests."""

    facade = A2AProtocolFacade()
    facade.submit(task_id, context_id, request)
    facade.start(task_id)
    if outcome == "completed":
        if result is None:
            raise A2AProtocolError("completed outcome requires result")
        facade.complete(task_id, result)
    elif outcome == "failed":
        if detail is None:
            raise A2AProtocolError("failed outcome requires detail")
        facade.fail(task_id, detail)
    elif outcome == "canceled":
        if detail is None:
            raise A2AProtocolError("canceled outcome requires detail")
        facade.cancel(task_id, detail)
    else:
        raise A2AProtocolError(f"unsupported terminal outcome: {outcome!r}")
    return facade.result(task_id)


def _request_part(request: str | Mapping[str, object]) -> Part:
    if isinstance(request, str):
        return Part(text=_non_empty("request", request))
    normalized = _normalize_json(request)
    if not isinstance(normalized, dict):
        raise A2AProtocolError("structured request must be a JSON object")
    return Part(data=_protobuf_value(normalized))


def _agent_message(task: Task, sequence: int, state_name: str, text: str) -> Message:
    return Message(
        message_id=_message_id(task.id, sequence, state_name),
        context_id=task.context_id,
        task_id=task.id,
        role=Role.ROLE_AGENT,
        parts=[Part(text=text)],
    )


def _status(state: int, message: Message, sequence: int) -> TaskStatus:
    return TaskStatus(
        state=state,
        message=message,
        timestamp=Timestamp(seconds=sequence),
    )


def _protobuf_value(value: JsonValue) -> Value:
    protobuf_value = Value()
    ParseDict(value, protobuf_value)
    return protobuf_value


def _normalize_json(value: object) -> JsonValue:
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_JSON_INTEGER:
            raise A2AProtocolError(
                "JSON integers must be within protobuf Value's exact IEEE-754 "
                f"safe-integer range [-{_MAX_SAFE_JSON_INTEGER}, {_MAX_SAFE_JSON_INTEGER}]"
            )
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise A2AProtocolError("JSON values must not contain NaN or infinity")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, JsonValue] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise A2AProtocolError("JSON object keys must be strings")
            normalized[key] = _normalize_json(value[key])
        return normalized
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_json(item) for item in value]
    raise A2AProtocolError(f"value of type {type(value).__name__!r} is not JSON-friendly")


def _message_text(message: Message) -> str:
    if message.role != Role.ROLE_AGENT:
        raise A2AProtocolError("terminal diagnostic must be agent-authored")
    if len(message.parts) != 1 or message.parts[0].WhichOneof("content") != "text":
        raise A2AProtocolError("terminal diagnostic must contain exactly one text part")
    return _non_empty("terminal diagnostic", message.parts[0].text)


def _identifier(name: str, value: str) -> str:
    normalized = _non_empty(name, value)
    if normalized != value:
        raise A2AProtocolError(f"{name} must not have leading or trailing whitespace")
    return normalized


def _non_empty(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise A2AProtocolError(f"{name} must not be empty")
    return value


def _message_id(task_id: str, sequence: int, state_name: str) -> str:
    return f"{task_id}:message:{sequence}:{state_name}"


def _state_name(state: int) -> str:
    name = TaskState.Name(state)
    if state not in {_SUBMITTED, _WORKING, *_TERMINAL_STATES}:
        raise ValueError(f"unsupported task state: {name}")
    return name.removeprefix("TASK_STATE_").lower()


__all__ = [
    "A2AProtocolError",
    "A2AProtocolFacade",
    "InvalidTaskTransitionError",
    "JsonValue",
    "LifecycleEvidence",
    "LifecycleResult",
    "TaskAlreadyExistsError",
    "TaskNotFoundError",
    "TerminalOutcome",
    "parse_task",
    "round_trip_task",
    "run_lifecycle",
    "serialize_task",
    "task_to_dict",
]
