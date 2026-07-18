"""Canonical registry, transaction, and hash-chained audit storage."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.git_lifecycle.models import OperationDenied


def canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def sha256_json(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("ascii")).hexdigest().upper()


class LifecycleState:
    """File-backed Git lifecycle state rooted below ``.gtkb-state``."""

    def __init__(self, state_dir: Path, *, fault_hook: Callable[[str], None] | None = None) -> None:
        self.state_dir = state_dir.resolve()
        self.registry_path = self.state_dir / "branch-bindings.json"
        self.audit_path = self.state_dir / "branch-binding-audit.jsonl"
        self.transactions_dir = self.state_dir / "transactions"
        self.lock_path = self.state_dir / "git-lifecycle.lock"
        self.journal_path = self.state_dir / "state-commit-journal.json"
        self.transaction_journal_path = self.state_dir / "transaction-audit-journal.json"
        self.lock_recovery_path = self.state_dir / "git-lifecycle-lock-recovery.jsonl"
        self.fault_hook = fault_hook

    @staticmethod
    def _process_create_time(pid: int) -> float | None:
        try:
            import psutil  # noqa: PLC0415
        except ImportError:
            return None
        try:
            return float(psutil.Process(pid).create_time())
        except (psutil.Error, OSError, ValueError):
            return None

    def _new_lock_record(self) -> dict[str, Any]:
        pid = os.getpid()
        create_time = self._process_create_time(pid)
        if create_time is None:
            raise OperationDenied(
                "lifecycle_lock_provenance_unavailable",
                "cannot establish process provenance for the lifecycle lock",
            )
        return {
            "schema_version": 1,
            "pid": pid,
            "process_create_time": create_time,
            "acquired_at_epoch": time.time(),
            "owner_token": uuid.uuid4().hex,
        }

    def _read_lock_record(self) -> dict[str, Any]:
        record = self._read_object(self.lock_path)
        return self._validate_lock_record(record)

    @staticmethod
    def _validate_lock_record(record: dict[str, Any]) -> dict[str, Any]:
        if (
            record.get("schema_version") != 1
            or not isinstance(record.get("pid"), int)
            or isinstance(record.get("pid"), bool)
            or record["pid"] <= 0
            or not isinstance(record.get("process_create_time"), (int, float))
            or isinstance(record.get("process_create_time"), bool)
            or not isinstance(record.get("owner_token"), str)
            or not record["owner_token"]
        ):
            raise OperationDenied("lifecycle_lock_malformed", "lifecycle lock ownership is malformed")
        return record

    def _read_lock_record_from_descriptor(self, descriptor: int) -> dict[str, Any]:
        os.lseek(descriptor, 0, os.SEEK_SET)
        remaining = os.fstat(descriptor).st_size
        payload = bytearray()
        try:
            while remaining:
                chunk = os.read(descriptor, remaining)
                if not chunk:
                    break
                payload.extend(chunk)
                remaining -= len(chunk)
            record = json.loads(payload.decode("ascii"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OperationDenied(
                "lifecycle_state_malformed",
                "lifecycle state is unreadable or malformed",
                path=str(self.lock_path),
            ) from exc
        if not isinstance(record, dict):
            raise OperationDenied("lifecycle_lock_malformed", "lifecycle lock ownership is malformed")
        return self._validate_lock_record(record)

    def _record_stale_lock_recovery(self, record: dict[str, Any]) -> None:
        event = {
            "action": "recover_stale_lifecycle_lock",
            "recovered_at_epoch": time.time(),
            "stale_owner_token": record["owner_token"],
            "stale_pid": record["pid"],
            "stale_process_create_time": record["process_create_time"],
        }
        self.lock_recovery_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_recovery_path.open("a", encoding="ascii", newline="\n") as handle:
            handle.write(canonical_json(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    @staticmethod
    def _try_acquire_os_lock(descriptor: int) -> bool:
        """Acquire the stable rendezvous file without deleting or replacing it."""
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == "nt":
            import msvcrt  # noqa: PLC0415

            try:
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                if exc.errno in {errno.EACCES, errno.EAGAIN}:
                    return False
                raise
            return True

        import fcntl  # noqa: PLC0415

        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN}:
                return False
            raise
        return True

    @staticmethod
    def _release_os_lock(descriptor: int) -> None:
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == "nt":
            import msvcrt  # noqa: PLC0415

            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            return

        import fcntl  # noqa: PLC0415

        fcntl.flock(descriptor, fcntl.LOCK_UN)

    @staticmethod
    def _write_lock_record(descriptor: int, record: dict[str, Any] | None) -> None:
        payload = b"" if record is None else (canonical_json(record) + "\n").encode("ascii")
        os.lseek(descriptor, 0, os.SEEK_SET)
        os.ftruncate(descriptor, 0)
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written == 0:
                raise OSError("failed to write lifecycle lock ownership metadata")
            offset += written
        os.fsync(descriptor)

    def _current_lock_owner(self) -> dict[str, Any] | None:
        try:
            return self._read_lock_record()
        except (FileNotFoundError, OperationDenied):
            return None

    @contextmanager
    def lock(self) -> Iterator[None]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        record = self._new_lock_record()
        descriptor = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        acquired = False
        try:
            acquired = self._try_acquire_os_lock(descriptor)
            if not acquired:
                existing = self._current_lock_owner()
                details: dict[str, Any] = {"lock_path": str(self.lock_path)}
                if existing is not None:
                    details["owner_pid"] = existing["pid"]
                raise OperationDenied(
                    "lifecycle_lock_held",
                    "another lifecycle writer holds the repository lock",
                    **details,
                )

            if os.fstat(descriptor).st_size:
                existing = self._read_lock_record_from_descriptor(descriptor)
                self._record_stale_lock_recovery(existing)
            self._write_lock_record(descriptor, record)
            self._recover_state_journal()
            self._recover_transaction_journal()
            yield
        finally:
            try:
                if acquired:
                    try:
                        self._write_lock_record(descriptor, None)
                    finally:
                        self._release_os_lock(descriptor)
            finally:
                os.close(descriptor)

    @staticmethod
    def _read_object(path: Path, *, missing: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            if missing is not None:
                return missing
            raise
        except (OSError, json.JSONDecodeError) as exc:
            raise OperationDenied(
                "lifecycle_state_malformed",
                "lifecycle state is unreadable or malformed",
                path=str(path),
            ) from exc
        if not isinstance(payload, dict):
            raise OperationDenied("lifecycle_state_malformed", "lifecycle state root must be an object", path=str(path))
        return payload

    @staticmethod
    def _write_object(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        temporary.write_text(canonical_json(payload) + "\n", encoding="ascii", newline="\n")
        os.replace(temporary, path)

    def load_registry(self) -> dict[str, Any]:
        registry = self._read_object(
            self.registry_path,
            missing={"schema_version": 1, "generation": 0, "bindings": {}},
        )
        if registry.get("schema_version") != 1 or not isinstance(registry.get("generation"), int):
            raise OperationDenied("registry_schema_invalid", "branch binding registry schema is invalid")
        if not isinstance(registry.get("bindings"), dict):
            raise OperationDenied("registry_schema_invalid", "branch binding registry bindings must be an object")
        for work_item_id, record in registry["bindings"].items():
            if not isinstance(work_item_id, str) or not isinstance(record, dict):
                raise OperationDenied("registry_schema_invalid", "branch binding registry record is invalid")
            expected_hash = sha256_json({key: value for key, value in record.items() if key != "record_hash"})
            if record.get("work_item_id") != work_item_id or record.get("record_hash") != expected_hash:
                raise OperationDenied("binding_hash_mismatch", "branch binding registry record hash is not current")
        return registry

    def save_registry(self, registry: dict[str, Any]) -> None:
        self._write_object(self.registry_path, registry)

    def _audit_records(self) -> list[dict[str, Any]]:
        if not self.audit_path.exists():
            return []
        previous_hash = "0" * 64
        previous_timestamp: datetime | None = None
        records: list[dict[str, Any]] = []
        try:
            lines = [line for line in self.audit_path.read_text(encoding="ascii").splitlines() if line]
            for line in lines:
                record = json.loads(line)
                if not isinstance(record, dict) or record.get("previous_hash") != previous_hash:
                    raise ValueError("invalid previous link")
                recorded_hash = record.get("event_hash")
                expected_hash = sha256_json({key: value for key, value in record.items() if key != "event_hash"})
                if recorded_hash != expected_hash:
                    raise ValueError("invalid event hash")
                timestamp = self._audit_timestamp(record.get("occurred_at"))
                if timestamp is not None and previous_timestamp is not None and timestamp < previous_timestamp:
                    raise ValueError("non-monotonic audit timestamp")
                if timestamp is not None:
                    previous_timestamp = timestamp
                previous_hash = recorded_hash
                records.append(record)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise OperationDenied("audit_chain_malformed", "branch binding audit chain is malformed") from exc
        return records

    @staticmethod
    def _audit_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value.endswith("Z"):
            raise ValueError("invalid audit timestamp")
        timestamp = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
        if timestamp.tzinfo is None:
            raise ValueError("invalid audit timestamp")
        return timestamp

    def _append_audit_record(self, record: dict[str, Any]) -> None:
        records = self._audit_records()
        if records and records[-1].get("event_hash") == record.get("event_hash"):
            return
        previous_hash = records[-1]["event_hash"] if records else "0" * 64
        if record.get("previous_hash") != previous_hash:
            raise OperationDenied("audit_chain_conflict", "journal audit event does not extend the current chain")
        expected_hash = sha256_json({key: value for key, value in record.items() if key != "event_hash"})
        if record.get("event_hash") != expected_hash:
            raise OperationDenied("audit_chain_malformed", "journal audit event hash is invalid")
        try:
            current_timestamp = self._audit_timestamp(record.get("occurred_at"))
            previous_timestamp = self._audit_timestamp(records[-1].get("occurred_at")) if records else None
        except ValueError as exc:
            raise OperationDenied("audit_timestamp_invalid", "audit event timestamp is invalid") from exc
        if current_timestamp is not None and previous_timestamp is not None and current_timestamp < previous_timestamp:
            raise OperationDenied("audit_timestamp_non_monotonic", "audit event timestamp precedes the audit head")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="ascii", newline="\n") as handle:
            handle.write(canonical_json(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _fault(self, phase: str) -> None:
        if self.fault_hook is not None:
            self.fault_hook(phase)

    def commit_registry_and_audit(
        self,
        registry: dict[str, Any],
        event: dict[str, Any],
        *,
        operation_id: str,
    ) -> dict[str, Any]:
        """Commit registry and audit through one recoverable write-ahead journal."""
        previous_registry = self.load_registry()
        records = self._audit_records()
        previous_hash = records[-1]["event_hash"] if records else "0" * 64
        audit_record = {**event, "previous_hash": previous_hash}
        audit_record["event_hash"] = sha256_json(audit_record)
        journal: dict[str, Any] = {
            "schema_version": 1,
            "operation_id": operation_id,
            "previous_registry_sha256": sha256_json(previous_registry),
            "registry": registry,
            "audit_record": audit_record,
        }
        journal["journal_hash"] = sha256_json(journal)
        self._write_object(self.journal_path, journal)
        self._fault("journal_prepared")
        self.save_registry(registry)
        self._fault("registry_replaced")
        self._append_audit_record(audit_record)
        self._fault("audit_appended")
        self.journal_path.unlink()
        return audit_record

    def _recover_state_journal(self) -> None:
        if not self.journal_path.exists():
            return
        journal = self._read_object(self.journal_path)
        expected_hash = sha256_json({key: value for key, value in journal.items() if key != "journal_hash"})
        if journal.get("schema_version") != 1 or journal.get("journal_hash") != expected_hash:
            raise OperationDenied("state_journal_malformed", "lifecycle state journal is malformed")
        registry = journal.get("registry")
        audit_record = journal.get("audit_record")
        if not isinstance(registry, dict) or not isinstance(audit_record, dict):
            raise OperationDenied("state_journal_malformed", "lifecycle state journal payload is malformed")
        current = self.load_registry()
        current_hash = sha256_json(current)
        target_hash = sha256_json(registry)
        if current_hash not in {journal.get("previous_registry_sha256"), target_hash}:
            raise OperationDenied("state_journal_conflict", "lifecycle state advanced beyond the pending journal")
        if current_hash != target_hash:
            self.save_registry(registry)
        self._append_audit_record(audit_record)
        self.journal_path.unlink()

    @staticmethod
    def _hashed_transaction(payload: dict[str, Any]) -> dict[str, Any]:
        transaction = {key: value for key, value in payload.items() if key != "transaction_hash"}
        transaction["transaction_hash"] = sha256_json(transaction)
        return transaction

    def _load_transaction_unchecked(self, operation_id: str) -> dict[str, Any]:
        transaction = self._read_object(self.transactions_dir / f"{operation_id}.json")
        expected_hash = sha256_json({key: value for key, value in transaction.items() if key != "transaction_hash"})
        if transaction.get("transaction_hash") != expected_hash:
            raise OperationDenied("transaction_hash_mismatch", "lifecycle transaction hash is not current")
        return transaction

    def commit_transaction_and_audit(
        self,
        operation_id: str,
        transaction: dict[str, Any],
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Commit authority-bearing transaction state and its audit record atomically."""
        if self.transaction_journal_path.exists():
            raise OperationDenied(
                "transaction_journal_pending",
                "pending transaction audit journal must be recovered under the lifecycle lock",
            )
        previous_transaction = self._load_transaction_unchecked(operation_id)
        target_transaction = self._hashed_transaction(transaction)
        records = self._audit_records()
        previous_hash = records[-1]["event_hash"] if records else "0" * 64
        audit_record = {**event, "previous_hash": previous_hash}
        audit_record["event_hash"] = sha256_json(audit_record)
        journal: dict[str, Any] = {
            "schema_version": 1,
            "operation_id": operation_id,
            "previous_transaction_sha256": sha256_json(previous_transaction),
            "transaction": target_transaction,
            "audit_record": audit_record,
        }
        journal["journal_hash"] = sha256_json(journal)
        self._write_object(self.transaction_journal_path, journal)
        self._fault("transaction_journal_prepared")
        self.save_transaction(operation_id, target_transaction)
        self._fault("transaction_replaced")
        self._append_audit_record(audit_record)
        self._fault("audit_appended")
        self.transaction_journal_path.unlink()
        return target_transaction

    def _recover_transaction_journal(self) -> None:
        if not self.transaction_journal_path.exists():
            return
        journal = self._read_object(self.transaction_journal_path)
        expected_hash = sha256_json({key: value for key, value in journal.items() if key != "journal_hash"})
        if journal.get("schema_version") != 1 or journal.get("journal_hash") != expected_hash:
            raise OperationDenied("transaction_journal_malformed", "transaction audit journal is malformed")
        operation_id = journal.get("operation_id")
        transaction = journal.get("transaction")
        audit_record = journal.get("audit_record")
        if not isinstance(operation_id, str) or not isinstance(transaction, dict) or not isinstance(audit_record, dict):
            raise OperationDenied("transaction_journal_malformed", "transaction audit journal payload is malformed")
        target_transaction = self._hashed_transaction(transaction)
        if target_transaction != transaction:
            raise OperationDenied("transaction_journal_malformed", "journal transaction hash is invalid")
        current = self._load_transaction_unchecked(operation_id)
        current_hash = sha256_json(current)
        target_hash = sha256_json(target_transaction)
        if current_hash not in {journal.get("previous_transaction_sha256"), target_hash}:
            raise OperationDenied("transaction_journal_conflict", "transaction advanced beyond the pending journal")
        if current_hash != target_hash:
            self.save_transaction(operation_id, target_transaction)
        self._append_audit_record(audit_record)
        self.transaction_journal_path.unlink()

    def load_transaction(self, operation_id: str) -> dict[str, Any]:
        if self.transaction_journal_path.exists():
            raise OperationDenied(
                "transaction_journal_pending",
                "pending transaction audit journal must be recovered under the lifecycle lock",
            )
        return self._load_transaction_unchecked(operation_id)

    def save_transaction(self, operation_id: str, payload: dict[str, Any]) -> None:
        transaction = self._hashed_transaction(payload)
        self._write_object(self.transactions_dir / f"{operation_id}.json", transaction)

    def append_audit(self, event: dict[str, Any]) -> dict[str, Any]:
        records = self._audit_records()
        previous_hash = records[-1]["event_hash"] if records else "0" * 64
        record = {**event, "previous_hash": previous_hash}
        record["event_hash"] = sha256_json(record)
        self._append_audit_record(record)
        return record

    def append_audit_once(self, event: dict[str, Any]) -> dict[str, Any]:
        """Append an operation event once so recovery cannot duplicate evidence."""
        operation_id = event.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id:
            raise OperationDenied("audit_operation_id_missing", "idempotent audit append requires an operation id")
        records = self._audit_records()
        matches = [record for record in records if record.get("operation_id") == operation_id]
        if len(matches) > 1:
            raise OperationDenied("audit_operation_duplicate", "audit contains duplicate operation records")
        if matches:
            expected = {key: value for key, value in event.items() if key not in {"previous_hash", "event_hash"}}
            actual = {key: value for key, value in matches[0].items() if key not in {"previous_hash", "event_hash"}}
            if actual != expected:
                raise OperationDenied(
                    "audit_operation_conflict", "operation audit evidence conflicts with recovery input"
                )
            return matches[0]
        return self.append_audit(event)
