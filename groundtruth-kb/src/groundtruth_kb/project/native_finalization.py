"""Project completion mirrors a real, complete, independently reviewed Git commit.

These operations neither invent a verdict nor retain bridge payloads as commit
evidence. The native service executes the verifying agent's normal Git commit.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Annotated, Any, Literal

from psycopg import sql
from pydantic import Field

from groundtruth_kb.bridge.native import NativeBridgeService, SessionRequest
from groundtruth_kb.native_authority import (
    Mutation,
    Text,
    _error,
    _related,
    _require_project_dependencies,
    _required,
    _write,
)
from groundtruth_kb.postgres_kernel import (
    PostgresKernelError,
    PostgresTransaction,
    canonical_json_bytes,
    parse_json_bytes,
)
from groundtruth_kb.project.native_commit import ProjectCommitError, commit_reviewed_project
from groundtruth_kb.session.worktree import (
    SessionWorktreeError,
    _registered_context_checkout,
    materialize_context_worktree,
)

GitObject = Annotated[str, Field(pattern=r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")]


class FinalizationRequest(SessionRequest):
    expected_version: int = Field(ge=1)


class CommitConfirmation(FinalizationRequest):
    commit_id: GitObject
    expected_parent: GitObject


class ProjectCommit(FinalizationRequest):
    message: Annotated[str, Field(min_length=1, max_length=262144)]


class CommitCheck(CommitConfirmation):
    index_tree: GitObject


class CommitFailure(FinalizationRequest):
    reason: Literal["commit_not_confirmed"]
    evidence: Text


class NativeProjectFinalization:
    def __init__(self, bridge: NativeBridgeService) -> None:
        self.bridge = bridge
        self.kernel = bridge.kernel
        self.root = bridge.project_root
        # A callback belongs only to the synchronous Git operation currently
        # holding this transaction. It stores no authority or recovery record.
        self._commit_callbacks: dict[str, Callable[[CommitCheck], dict[str, Any]]] = {}

    def _git(self, *arguments: str, root: Path | None = None) -> bytes:
        try:
            result = subprocess.run(
                ["git", "-C", str(root or self.root), *arguments],
                capture_output=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise PostgresKernelError("git_evidence_unavailable", "Git evidence could not be read") from error
        if result.returncode:
            _error(
                "git_evidence_unavailable",
                "Git command failed",
                evidence=result.stderr.decode("utf-8", errors="replace").strip(),
            )
        return result.stdout

    def _head(self, root: Path | None = None) -> str:
        head = self._git("rev-parse", "--verify", "HEAD", root=root).decode("ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", head):
            _error("git_evidence_unavailable", "The checkout has no valid current commit")
        return head

    def _project(
        self, tx: PostgresTransaction, project_id: str, request: FinalizationRequest, *, terminal: bool = False
    ) -> tuple[dict[str, Any], dict[str, Any], Path]:
        binding = self.bridge._binding(tx, request.native_context_id)
        if binding["role"] != "loyal-opposition":
            _error("independent_verifier_required", "Project finalization is performed by Loyal Opposition")
        project = _required(tx, "projects", project_id, lock=True)
        if project["kind"] != "project":
            _error("program_has_no_commit", "A program sequences projects and has no work-product commit")
        repository = self.bridge.repository_root(tx, project_id, binding=binding)
        if terminal and project["status"] == "verified":
            return binding, project, repository
        if project["version"] != request.expected_version:
            _error("cas_conflict", "Read the current project version before finalization")
        if project["status"] != "active":
            _error("project_not_active", "Only an active execution project can finalize")
        return binding, project, repository

    def _cohort(
        self, tx: PostgresTransaction, project: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, str] | None]]:
        _require_project_dependencies(tx, project["id"], lock=True)
        _require_project_dependencies(tx, project["id"], "closure", lock=True)
        members = _related(tx, "project_work_item_memberships", project_id=project["id"], status="active")
        if not members:
            _error("empty_project", "An empty project is not a completed work product")
        artifacts: dict[str, dict[str, str] | None]
        attempts, work_items, artifacts = [], [], {}
        for member in sorted(members, key=lambda item: item["work_item_id"]):
            work = _required(tx, "work_items", member["work_item_id"], lock=True)
            if work["resolution_status"] != "verified":
                _error(
                    "project_not_fully_verified",
                    "Every current project member must be VERIFIED",
                    work_item_id=work["id"],
                )
            tx.cursor.execute(
                sql.SQL(
                    "SELECT * FROM {}.bridge_attempts WHERE work_item_id=%s AND disposition='active' FOR UPDATE"
                ).format(sql.Identifier(tx.schema)),
                (work["id"],),
            )
            rows = tx.cursor.fetchall()
            if len(rows) != 1 or rows[0]["head_status"] != "VERIFIED" or not rows[0]["verified_artifacts"]:
                _error(
                    "review_state_missing",
                    "The member lacks canonical verification of exact artifacts",
                    work_item_id=work["id"],
                )
            attempt = dict(rows[0])
            # Hold current formal inputs until the effect is complete. The
            # project and work locks also exclude membership/scope mutations.
            for spec_id in sorted(attempt["spec_versions"]):
                _required(tx, "specifications", spec_id, lock=True)
            self.bridge._scope(tx, attempt)
            self.bridge._require_work_dependencies(tx, work["id"], attempt=attempt, lock=True, cross_project_only=True)
            for path, blob in attempt["verified_artifacts"].items():
                if path.casefold().split("/")[0] == "bridge":
                    _error("bridge_payload_in_cohort", "Bridge payloads cannot enter a project work-product commit")
                # This union enumerates the complete project scope. It is usable
                # as commit evidence only after every member's own review has
                # been compared with the current bytes below.
                artifacts[path] = blob
            attempts.append(attempt)
            work_items.append(work)
        tx.cursor.execute(
            sql.SQL(
                "SELECT 1 FROM {}.work_intent_claims c JOIN {}.bridge_attempts a ON a.id=c.attempt_id "
                "WHERE a.project_id=%s AND c.expires_at>clock_timestamp() LIMIT 1"
            ).format(sql.Identifier(tx.schema), sql.Identifier(tx.schema)),
            (project["id"],),
        )
        if tx.cursor.fetchone():
            _error("live_artifact_claim", "A project with a live artifact claim cannot finalize")
        return work_items, attempts, artifacts

    @staticmethod
    def _request_verification(
        tx: PostgresTransaction,
        attempts: Sequence[dict[str, Any]],
        code: str,
        evidence: dict[str, Any],
        *,
        paths: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        affected = []
        for attempt in attempts:
            if paths is not None and not set(paths).intersection(attempt["verified_artifacts"]):
                continue
            # Repeated requests describe the same pending action. Do not move
            # it behind newer work merely because status was checked again.
            try:
                prior = parse_json_bytes((attempt["finalization_failure"] or "").encode("utf-8"))
                requested_at = datetime.fromisoformat(prior["requested_at"])
                if requested_at.tzinfo is None:
                    raise ValueError("Naive request time")
            except (PostgresKernelError, TypeError, ValueError, KeyError):
                # An explicit new request establishes a time; queue reads never
                # fabricate an age for an older request lacking this fact.
                tx.cursor.execute("SELECT clock_timestamp() AS requested_at")
                requested_at = tx.cursor.fetchone()["requested_at"]
            failure = (
                canonical_json_bytes({"code": code, "evidence": evidence, "requested_at": requested_at.isoformat()})
                .decode("utf-8")
                .strip()
            )
            tx.cursor.execute(
                sql.SQL("UPDATE {}.bridge_attempts SET finalization_failure=%s WHERE id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (failure, attempt["id"]),
            )
            affected.append(attempt["work_item_id"])
        return {"status": "fresh_verification_required", "reason": code, "work_item_ids": affected}

    def _request_changed_reviews(
        self, tx: PostgresTransaction, attempts: Sequence[dict[str, Any]], actual: dict[str, dict[str, str] | None]
    ) -> dict[str, Any] | None:
        stale = [
            attempt
            for attempt in attempts
            if any(actual[path] != blob for path, blob in attempt["verified_artifacts"].items())
        ]
        if not stale:
            return None
        paths = sorted(
            {path for attempt in stale for path, blob in attempt["verified_artifacts"].items() if actual[path] != blob}
        )
        # A later work item can legitimately change an earlier item's artifact.
        # Preserve reviews already matching the final bytes, even on shared paths.
        return self._request_verification(tx, stale, "verified_bytes_changed", {"paths": paths})

    def prepare(self, project_id: str, request: FinalizationRequest) -> dict[str, Any]:
        with self.kernel.transaction(serializable=False) as tx:
            return self._prepare_locked(tx, project_id, request)

    def _prepare_locked(self, tx: PostgresTransaction, project_id: str, request: FinalizationRequest) -> dict[str, Any]:
        self.bridge.lock_worktrees(tx)
        binding, project, repository = self._project(tx, project_id, request, terminal=True)
        if project["status"] == "verified":
            links = _related(
                tx,
                "project_artifact_links",
                project_id=project_id,
                artifact_type="git_commit",
                relationship="activation",
                status="active",
            )
            if len(links) != 1:
                _error("terminal_commit_missing", "The terminal project must identify its one activation commit")
            commit_id = links[0]["artifact_ref"]
            self._git("cat-file", "-e", commit_id + "^{commit}", root=repository)
            return {"status": "already_confirmed", "project_id": project_id, "commit_id": commit_id}
        works, attempts, artifacts = self._cohort(tx, project)
        source = self.bridge.work_root(project_id, tx=tx)
        parent = self._head(root=repository)
        actual = self.bridge._snapshot(sorted(artifacts), root=source)
        changed_reviews = self._request_changed_reviews(tx, attempts, actual)
        if changed_reviews:
            return changed_reviews
        failures = [attempt["work_item_id"] for attempt in attempts if attempt["finalization_failure"]]
        if failures:
            return {"status": "fresh_verification_required", "work_item_ids": failures}
        existing = self._existing_commit(request, binding, works, artifacts, root=repository)
        if existing:
            return {
                "status": "ready_to_confirm",
                "project_id": project_id,
                "project_version": project["version"],
                **existing,
            }
        if self._head(source) != parent:
            # Carry unrelated work forward without resetting local reviewed bytes.
            self._git("merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", parent, root=source)
            changed_reviews = self._request_changed_reviews(
                tx, attempts, self.bridge._snapshot(sorted(artifacts), root=source)
            )
            if changed_reviews:
                return changed_reviews
        try:
            checkout = materialize_context_worktree(
                self.root,
                binding["session_context_id"],
                expected_head=parent,
                artifacts=artifacts,
                snapshot=self.bridge._snapshot,
                artifact_source=source,
                repository_root=repository,
            )
        except SessionWorktreeError as error:
            raise PostgresKernelError(error.code, str(error)) from error
        return {
            "status": "ready_to_commit",
            "project_id": project_id,
            "project_version": project["version"],
            "expected_parent": parent,
            "checkout": checkout,
            "hooks_path": str(repository / ".githooks"),
            "reviewed_artifacts": artifacts,
            "work_item_ids": [work["id"] for work in works],
            "required_citations": [f"({work['id']})" for work in works],
            "instruction": (
                "Create one normal Git commit of this complete reviewed cohort, excluding bridge payloads, "
                "then confirm its identity through the CLI."
            ),
        }

    def failure(self, project_id: str, request: CommitFailure) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            _, project, repository = self._project(tx, project_id, request)
            _, attempts, _ = self._cohort(tx, project)
            return self._request_verification(
                tx,
                attempts,
                request.reason,
                {"message": request.evidence, "observed_head": self._head(root=repository)},
            )

    def _tree(self, revision: str, *, root: Path) -> dict[str, dict[str, str] | str]:
        result: dict[str, dict[str, str] | str] = {}
        for item in self._git("ls-tree", "-rz", "--full-tree", revision, root=root).split(b"\0"):
            if not item:
                continue
            metadata, path = item.split(b"\t", 1)
            mode, kind, blob = metadata.split(b" ")
            name = path.decode("utf-8")
            if kind != b"blob" or mode not in {b"100644", b"100755"}:
                # Nonregular paths are not silently treated as reviewed files.
                result[name] = "unsupported"
            else:
                result[name] = {"mode": mode.decode("ascii"), "object_id": blob.decode("ascii")}
        return result

    def _verify_commit(
        self,
        request: CommitConfirmation,
        binding: dict[str, Any],
        works: Sequence[dict[str, Any]],
        artifacts: dict[str, dict[str, str] | None],
        *,
        root: Path,
        index_tree: str | None = None,
    ) -> None:
        integration_head = self._head(root=root)
        if integration_head not in {request.expected_parent, request.commit_id}:
            _error("integration_base_changed", "Read and review the current integration base before another commit")
        if index_tree is not None:
            try:
                checkout = _registered_context_checkout(self.root, binding["session_context_id"], repository_root=root)
            except SessionWorktreeError as error:
                raise PostgresKernelError(error.code, str(error)) from error
            if self._head(checkout) != request.expected_parent:
                _error("commit_not_current", "The registered context checkout is not at the expected commit")
        elif not self._git(
            "for-each-ref", "--contains=" + request.commit_id, "--format=%(refname)", "refs/heads", root=root
        ).strip():
            _error("commit_not_published", "The candidate must be a reachable repository branch fact")
        if index_tree is not None:
            if integration_head != request.expected_parent:
                _error("integration_base_changed", "The integration base changed before the reference update")
            candidate_tree = self._git("rev-parse", request.commit_id + "^{tree}", root=root).decode("ascii").strip()
            if candidate_tree != index_tree:
                _error("commit_index_changed", "A hook changed the index after Git formed the candidate commit")
        parent_line = (
            self._git("rev-list", "--parents", "-n", "1", request.commit_id, root=root).decode("ascii").strip().split()
        )
        if parent_line != [request.commit_id, request.expected_parent]:
            _error("unexpected_commit_parent", "A project commit has exactly the prepared parent")
        message = self._git("show", "-s", "--format=%B", request.commit_id, root=root).decode("utf-8")
        required = {f"({work['id']})" for work in works}
        cited = set(re.findall(r"\(WI-[A-Za-z0-9_-]+\)", message))
        if not required.issubset(cited):
            _error(
                "incomplete_commit_citations",
                "The commit must cite every project member",
                missing=sorted(required - cited),
            )
        after = self._tree(request.commit_id, root=root)
        changed = {
            path.decode("utf-8")
            for path in self._git(
                "diff-tree",
                "-r",
                "--no-renames",
                "--no-commit-id",
                "--name-only",
                "-z",
                request.expected_parent,
                request.commit_id,
                root=root,
            ).split(b"\0")
            if path
        }
        foreign = changed - artifacts.keys()
        if foreign:
            _error(
                "unreviewed_commit_paths",
                "The commit includes paths outside the complete reviewed cohort",
                paths=sorted(foreign),
            )
        mismatched = [path for path, blob in artifacts.items() if after.get(path) != blob]
        if mismatched:
            _error("unreviewed_commit_bytes", "The commit does not contain the exact reviewed bytes", paths=mismatched)
        if not changed:
            _error("empty_project_commit", "An empty commit is not the reviewed work product")

    def _existing_commit(
        self,
        request: FinalizationRequest,
        binding: dict[str, Any],
        works: Sequence[dict[str, Any]],
        artifacts: dict[str, dict[str, str] | None],
        *,
        root: Path,
    ) -> dict[str, str] | None:
        """Recover from repository references, never from another context's files."""
        candidates = set(
            self._git("for-each-ref", "--format=%(objectname)", "refs/heads/session/", root=root)
            .decode("ascii")
            .splitlines()
        ) | {self._head(root=root)}
        required = {f"({work['id']})" for work in works}
        found = []
        for commit_id in sorted(candidates):
            message = self._git("show", "-s", "--format=%B", commit_id, root=root).decode("utf-8")
            if not required.issubset(set(re.findall(r"\(WI-[A-Za-z0-9_-]+\)", message))):
                continue
            parents = self._git("rev-list", "--parents", "-n", "1", commit_id, root=root).decode("ascii").split()
            if len(parents) != 2:
                _error("existing_commit_needs_reconciliation", "A possible project commit has an unexpected parent")
            current = CommitConfirmation(
                native_context_id=request.native_context_id,
                expected_version=request.expected_version,
                expected_parent=parents[1],
                commit_id=commit_id,
            )
            try:
                self._verify_commit(current, binding, works, artifacts, root=root)
            except PostgresKernelError as error:
                _error(
                    "existing_commit_needs_reconciliation",
                    "Reconcile the existing Git fact before attempting another project commit",
                    commit_id=commit_id,
                    cause=error.to_json_dict(),
                )
            found.append({"commit_id": commit_id, "expected_parent": parents[1]})
        if len(found) > 1:
            _error(
                "ambiguous_project_commit",
                "Multiple reviewed Git candidates require reconciliation",
                commit_ids=[item["commit_id"] for item in found],
            )
        return found[0] if found else None

    def check_commit(self, project_id: str, request: CommitCheck) -> dict[str, Any]:
        callback = self._commit_callbacks.get(project_id)
        if callback is not None:
            return callback(request)
        with self.kernel.transaction(serializable=False) as tx:
            return self._check_commit_locked(tx, project_id, request)

    def _check_commit_locked(self, tx: PostgresTransaction, project_id: str, request: CommitCheck) -> dict[str, Any]:
        self.bridge.lock_worktrees(tx)
        binding, project, repository = self._project(tx, project_id, request)
        works, attempts, artifacts = self._cohort(tx, project)
        if any(attempt["finalization_failure"] for attempt in attempts):
            _error("fresh_verification_required", "Fresh verification must finish before committing")
        actual = self.bridge._snapshot(sorted(artifacts), root=self.bridge.work_root(project_id, tx=tx))
        changed_reviews = self._request_changed_reviews(tx, attempts, actual)
        if changed_reviews:
            return changed_reviews
        try:
            checkout = _registered_context_checkout(
                self.root, binding["session_context_id"], repository_root=repository
            )
            self._verify_commit(request, binding, works, artifacts, index_tree=request.index_tree, root=repository)
            local = self.bridge._snapshot(sorted(artifacts), root=checkout)
            if local != artifacts:
                _error("commit_checkout_changed", "The context files changed after preparation")
        except SessionWorktreeError as error:
            raise PostgresKernelError(error.code, str(error)) from error
        return {"status": "ready_to_update_reference", "commit_id": request.commit_id}

    def confirm(self, project_id: str, request: CommitConfirmation) -> dict[str, Any]:
        with self.kernel.transaction(serializable=False) as tx:
            return self._confirm_locked(tx, project_id, request)

    def _confirm_locked(self, tx: PostgresTransaction, project_id: str, request: CommitConfirmation) -> dict[str, Any]:
        self.bridge.lock_worktrees(tx)
        binding, project, repository = self._project(tx, project_id, request, terminal=True)
        links = _related(
            tx,
            "project_artifact_links",
            project_id=project_id,
            artifact_type="git_commit",
            relationship="activation",
            status="active",
        )
        if project["status"] == "verified":
            if len(links) == 1 and links[0]["artifact_ref"] == request.commit_id:
                self._git("cat-file", "-e", request.commit_id + "^{commit}", root=repository)
                return {"status": "already_confirmed", "project_id": project_id, "commit_id": request.commit_id}
            _error("terminal_commit_mismatch", "The terminal project names another Git commit")
        works, attempts, artifacts = self._cohort(tx, project)
        if any(attempt["finalization_failure"] for attempt in attempts):
            _error("fresh_verification_required", "Fresh independent verification must finish before confirmation")
        actual = self.bridge._snapshot(sorted(artifacts), root=self.bridge.work_root(project_id, tx=tx))
        changed_reviews = self._request_changed_reviews(tx, attempts, actual)
        if changed_reviews:
            return changed_reviews
        try:
            self._verify_commit(request, binding, works, artifacts, root=repository)
        except PostgresKernelError as error:
            return self._request_verification(tx, attempts, "commit_not_confirmed", error.to_json_dict())
        if links:
            _error("conflicting_commit_fact", "An active project already has a canonical activation commit link")
        try:
            # One candidate commit, one fast-forward, no synthetic merge
            # commit. Git refuses local overlap and retains unrelated work.
            if self._head(root=repository) != request.commit_id:
                self._git("symbolic-ref", "--quiet", "HEAD", root=repository)
                self._git(
                    "merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", request.commit_id, root=repository
                )
            if self._head(root=repository) != request.commit_id:
                _error("commit_not_current", "Git did not advance to the verified candidate")
        except PostgresKernelError as error:
            return self._request_verification(tx, attempts, "commit_not_confirmed", error.to_json_dict())
        reason = "Project completion confirmed from the complete independently reviewed Git commit"
        actor = binding["session_context_id"]
        _write(
            tx,
            "project_artifact_links",
            "PCL-" + hashlib.sha256(project_id.encode()).hexdigest()[:32],
            {
                "project_id": project_id,
                "artifact_type": "git_commit",
                "artifact_ref": request.commit_id,
                "relationship": "activation",
                "status": "active",
            },
            Mutation(expected_version=0, actor=actor, reason=reason),
        )
        _write(
            tx,
            "projects",
            project_id,
            {
                "status": "verified",
                "completed_at": self._git("show", "-s", "--format=%cI", request.commit_id, root=repository)
                .decode("ascii")
                .strip(),
            },
            Mutation(expected_version=project["version"], actor=actor, reason=reason),
        )
        for work, attempt in zip(works, attempts, strict=True):
            _write(
                tx,
                "work_items",
                work["id"],
                {"completion_evidence": "git:" + request.commit_id},
                Mutation(expected_version=work["version"], actor=actor, reason=reason),
            )
            tx.cursor.execute(
                sql.SQL("UPDATE {}.bridge_attempts SET disposition='committed',terminal_commit=%s WHERE id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (request.commit_id, attempt["id"]),
            )
            self.bridge._purge(tx, attempt["id"])
        return {
            "status": "confirmed",
            "project_id": project_id,
            "commit_id": request.commit_id,
            "work_item_ids": [work["id"] for work in works],
        }

    def commit(self, project_id: str, request: ProjectCommit, *, authority_url: str) -> dict[str, Any]:
        """Run the normal Git commit and confirmation under the current row locks."""
        with self.kernel.transaction(serializable=False) as tx:
            prepared = self._prepare_locked(tx, project_id, request)
            if prepared["status"] == "ready_to_confirm":
                return self._confirm_locked(
                    tx,
                    project_id,
                    CommitConfirmation(
                        native_context_id=request.native_context_id,
                        expected_version=request.expected_version,
                        expected_parent=prepared["expected_parent"],
                        commit_id=prepared["commit_id"],
                    ),
                )
            if prepared["status"] != "ready_to_commit":
                return prepared
            if any(citation not in request.message for citation in prepared["required_citations"]):
                _error("incomplete_commit_citations", "The authored message must cite every project work item")
            callback_lock = RLock()

            def check(current: CommitCheck) -> dict[str, Any]:
                with callback_lock:
                    if self._commit_callbacks.get(project_id) is not check:
                        _error("commit_not_in_progress", "Read current project state before checking a candidate")
                    if current.native_context_id != request.native_context_id:
                        _error("commit_context_mismatch", "Only this commit's bound context can check its candidate")
                    return self._check_commit_locked(tx, project_id, current)

            self._commit_callbacks[project_id] = check
            checkout = Path(prepared["checkout"]["path"])
            git_dir = Path(self._git("rev-parse", "--absolute-git-dir", root=checkout).decode("utf-8").strip())
            message_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=git_dir, prefix="gtkb-message-", suffix=".txt", delete=False
                ) as stream:
                    message_path = Path(stream.name)
                    stream.write(request.message.encode("utf-8"))
                commit_id = commit_reviewed_project(
                    prepared,
                    authority_url=authority_url,
                    project_id=project_id,
                    native_context_id=request.native_context_id,
                    message_file=message_path,
                )
            except (ProjectCommitError, OSError) as error:
                binding, project, repository = self._project(tx, project_id, request)
                works, attempts, artifacts = self._cohort(tx, project)
                existing = self._existing_commit(request, binding, works, artifacts, root=repository)
                if existing:
                    # Git may already have committed when later checkout/index
                    # housekeeping failed. Preserve that index and confirm once.
                    result = self._confirm_locked(
                        tx,
                        project_id,
                        CommitConfirmation(
                            native_context_id=request.native_context_id,
                            expected_version=request.expected_version,
                            expected_parent=existing["expected_parent"],
                            commit_id=existing["commit_id"],
                        ),
                    )
                    return {**result, "checkout_notice": str(error)}
                result = self._request_verification(tx, attempts, "commit_not_confirmed", {"message": str(error)})
                return {**result, "message": f"Project commit did not complete: {error}"}
            finally:
                # Serialize the final callback's exit with closing this local
                # operation, so a late request never uses an ended transaction.
                with callback_lock:
                    self._commit_callbacks.pop(project_id, None)
                if message_path is not None:
                    message_path.unlink(missing_ok=True)
            return self._confirm_locked(
                tx,
                project_id,
                CommitConfirmation(
                    native_context_id=request.native_context_id,
                    expected_version=request.expected_version,
                    expected_parent=prepared["expected_parent"],
                    commit_id=commit_id,
                ),
            )
