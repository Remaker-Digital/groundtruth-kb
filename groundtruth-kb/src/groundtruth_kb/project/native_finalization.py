"""Project completion mirrors a real, complete, independently reviewed Git commit.

These operations neither invent a verdict nor retain bridge payloads as commit
evidence. The verifying agent performs the normal Git commit after preparation.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
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
from groundtruth_kb.postgres_kernel import PostgresKernelError, canonical_json_bytes
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


class CommitFailure(FinalizationRequest):
    reason: Literal["commit_not_confirmed"]
    evidence: Text


class NativeProjectFinalization:
    def __init__(self, bridge: NativeBridgeService) -> None:
        self.bridge = bridge
        self.kernel = bridge.kernel
        self.root = bridge.project_root

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

    def _project(self, tx, project_id, request, *, terminal=False):
        binding = self.bridge._binding(tx, request.native_context_id)
        if binding["role"] != "loyal-opposition" or binding["subject"] != "gtkb":
            _error("independent_verifier_required", "Project finalization is performed by Loyal Opposition")
        project = _required(tx, "projects", project_id, lock=True)
        if project["kind"] != "project":
            _error("program_has_no_commit", "A program sequences projects and has no work-product commit")
        if terminal and project["status"] == "verified":
            return binding, project
        if project["version"] != request.expected_version:
            _error("cas_conflict", "Read the current project version before finalization")
        if project["status"] != "active":
            _error("project_not_active", "Only an active execution project can finalize")
        return binding, project

    def _cohort(self, tx, project):
        _require_project_dependencies(tx, project["id"], lock=True)
        _require_project_dependencies(tx, project["id"], "closure", lock=True)
        members = _related(tx, "project_work_item_memberships", project_id=project["id"], status="active")
        if not members:
            _error("empty_project", "An empty project is not a completed work product")
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
    def _request_verification(tx, attempts, code, evidence, *, paths=None):
        affected = []
        for attempt in attempts:
            if paths is not None and not set(paths).intersection(attempt["verified_artifacts"]):
                continue
            failure = canonical_json_bytes({"code": code, "evidence": evidence}).decode("utf-8").strip()
            tx.cursor.execute(
                sql.SQL("UPDATE {}.bridge_attempts SET finalization_failure=%s WHERE id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (failure, attempt["id"]),
            )
            affected.append(attempt["work_item_id"])
        return {"status": "fresh_verification_required", "reason": code, "work_item_ids": affected}

    def _request_changed_reviews(self, tx, attempts, actual):
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
            self.bridge.lock_worktrees(tx)
            binding, project = self._project(tx, project_id, request)
            works, attempts, artifacts = self._cohort(tx, project)
            source = self.bridge.work_root(project_id)
            parent = self._head()
            if self._head(source) != parent:
                # Ordinary fast-forward carries unrelated project work forward
                # and refuses overlapping local edits. Never reset the cohort.
                self._git("merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", parent, root=source)
            actual = self.bridge._snapshot(sorted(artifacts), root=source)
            changed_reviews = self._request_changed_reviews(tx, attempts, actual)
            if changed_reviews:
                return changed_reviews
            failures = [attempt["work_item_id"] for attempt in attempts if attempt["finalization_failure"]]
            if failures:
                return {"status": "fresh_verification_required", "work_item_ids": failures}
            try:
                checkout = materialize_context_worktree(
                    self.root,
                    binding["session_context_id"],
                    expected_head=parent,
                    artifacts=artifacts,
                    snapshot=self.bridge._snapshot,
                    artifact_source=source,
                )
            except SessionWorktreeError as error:
                raise PostgresKernelError(error.code, str(error)) from error
            return {
                "status": "ready_to_commit",
                "project_id": project_id,
                "project_version": project["version"],
                "expected_parent": parent,
                "checkout": checkout,
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
            _, project = self._project(tx, project_id, request)
            _, attempts, _ = self._cohort(tx, project)
            return self._request_verification(
                tx, attempts, request.reason, {"message": request.evidence, "observed_head": self._head()}
            )

    def _tree(self, revision: str) -> dict[str, str]:
        result = {}
        for item in self._git("ls-tree", "-rz", "--full-tree", revision).split(b"\0"):
            if not item:
                continue
            metadata, path = item.split(b"\t", 1)
            mode, kind, blob = metadata.split(b" ")
            name = path.decode("utf-8")
            if kind != b"blob" or mode not in {b"100644", b"100755"}:
                # Nonregular paths are not silently treated as reviewed files.
                result[name] = "unsupported"
            else:
                result[name] = blob.decode("ascii")
        return result

    def _verify_commit(self, request, binding, works, artifacts):
        integration_head = self._head()
        if integration_head not in {request.expected_parent, request.commit_id}:
            _error("integration_base_changed", "Read and review the current integration base before another commit")
        if integration_head != request.commit_id:
            try:
                checkout = _registered_context_checkout(self.root, binding["session_context_id"])
            except SessionWorktreeError as error:
                raise PostgresKernelError(error.code, str(error)) from error
            if self._head(checkout) != request.commit_id:
                _error("commit_not_current", "Confirm the candidate at the head of this context's own checkout")
        parent_line = self._git("rev-list", "--parents", "-n", "1", request.commit_id).decode("ascii").strip().split()
        if parent_line != [request.commit_id, request.expected_parent]:
            _error("unexpected_commit_parent", "A project commit has exactly the prepared parent")
        message = self._git("show", "-s", "--format=%B", request.commit_id).decode("utf-8")
        required = {f"({work['id']})" for work in works}
        cited = set(re.findall(r"\(WI-[A-Za-z0-9_-]+\)", message))
        if not required.issubset(cited):
            _error(
                "incomplete_commit_citations",
                "The commit must cite every project member",
                missing=sorted(required - cited),
            )
        after = self._tree(request.commit_id)
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

    def confirm(self, project_id: str, request: CommitConfirmation) -> dict[str, Any]:
        with self.kernel.transaction(serializable=False) as tx:
            self.bridge.lock_worktrees(tx)
            binding, project = self._project(tx, project_id, request, terminal=True)
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
                    self._git("cat-file", "-e", request.commit_id + "^{commit}")
                    return {"status": "already_confirmed", "project_id": project_id, "commit_id": request.commit_id}
                _error("terminal_commit_mismatch", "The terminal project names another Git commit")
            works, attempts, artifacts = self._cohort(tx, project)
            if any(attempt["finalization_failure"] for attempt in attempts):
                _error("fresh_verification_required", "Fresh independent verification must finish before confirmation")
            actual = self.bridge._snapshot(sorted(artifacts), root=self.bridge.work_root(project_id))
            changed_reviews = self._request_changed_reviews(tx, attempts, actual)
            if changed_reviews:
                return changed_reviews
            try:
                self._verify_commit(request, binding, works, artifacts)
            except PostgresKernelError as error:
                return self._request_verification(tx, attempts, "commit_not_confirmed", error.to_json_dict())
            if links:
                _error("conflicting_commit_fact", "An active project already has a canonical activation commit link")
            try:
                # One candidate commit, one fast-forward, no synthetic merge
                # commit. Git refuses local overlap and retains unrelated work.
                if self._head() != request.commit_id:
                    self._git("symbolic-ref", "--quiet", "HEAD")
                    self._git("merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", request.commit_id)
                if self._head() != request.commit_id:
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
                    "completed_at": self._git("show", "-s", "--format=%cI", request.commit_id).decode("ascii").strip(),
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
                    sql.SQL(
                        "UPDATE {}.bridge_attempts SET disposition='committed',terminal_commit=%s WHERE id=%s"
                    ).format(sql.Identifier(tx.schema)),
                    (request.commit_id, attempt["id"]),
                )
                self.bridge._purge(tx, attempt["id"])
            return {
                "status": "confirmed",
                "project_id": project_id,
                "commit_id": request.commit_id,
                "work_item_ids": [work["id"] for work in works],
            }
