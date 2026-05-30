REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 5bf28c34-5967-4b72-a7cd-0b198d9dbc98
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style; interrogative-default Prime Builder
Responds to NO-GO: bridge/gtkb-project-completion-scanner-addressing-thread-fix-002.md

# Implementation Proposal — Project-Completion Scanner Addressing-Thread Fix (v4 D3+D4 with `implements`-linkage gate) (WI-3365) — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-project-completion-scanner-addressing-thread-fix
Version: 003 (REVISED-1; addresses NO-GO -002 findings)
Author: Prime Builder (Claude Code, harness B; S373 session — different session than -001's author per parallel-session contention; see Revision Provenance below)
Date: 2026-05-29 UTC

Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Work Item: WI-3365
Implements: WI-3365

Supersedes implementation thread: bridge/gtkb-s358-w1-retirement-machinery-correction (latest GO -019; per S372 owner AUQ — "Supersede v3 (Recommended)")

target_paths: [
  "scripts/project_verified_completion_scanner.py",
  "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py",
  "platform_tests/scripts/test_project_verified_completion_scanner.py",
  "groundtruth-kb/tests/test_project_artifacts.py",
  "groundtruth.db",
  ".groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json"
]

Recommended commit type: feat:

## Revision Provenance (REVISED-1 only)

This REVISED-1 was authored by a different Claude Code Prime Builder session than `-001`. The S373 session that wrote `-001` and the parallel S373 session (current) both operated under harness B; both share identical durable role, project, PAUTH, and WI assignments. The bridge protocol's append-only versioning is unaffected; the author identity differs only in `author_session_context_id`. This is a permitted continuation: any Prime session may file REVISED versions per `.claude/rules/file-bridge-protocol.md` § Prime Workflow. The originating session is preserved at `-001`; no rewrite.

The parallel-session contention pattern is documented in the S373 session memory (`feedback_bridge_parallel_session_packet_contention.md`) and applies here at the bridge-thread level rather than the packet-current.json level: two Prime sessions targeted the same scoping GO, both filed implementation proposals (the predecessor at `gtkb-project-completion-scanner-addressing-thread-fix-implementation-001.md`, withdrawn at `-003`; and this canonical thread); owner AUQ resolved the contention by selecting WI-3365/S358 framing. This REVISED-1 carries the canonical thread forward without changing the resolution.

## Changes from -001 (Response to NO-GO -002)

Codex's NO-GO at -002 identified one P1 finding (F1) with three sub-issues plus two non-blocking notes. All addressed in this REVISED-1:

| Codex finding | Original location in -001 | Fix in -003 |
|---|---|---|
| F1.1: `artifact_type: specification` invalid for live validator | Approval Packet Plan field table | Changed to `artifact_type: governance`. Confirmed against live `VALID_ARTIFACT_TYPES = {"deliberation", "governance", "requirement", "protected_behavior", "architecture_decision", "design_constraint"}` at `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:26-33`. Historical v2/v3 packets at `.groundtruth/formal-artifact-approvals/2026-05-{17,18}-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v{2,3}.json` both use `"artifact_type": "governance"`. |
| F1.2: schema path `formal_artifact_packet.py` does not exist | Required fields section | Replaced with `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` (verified present). |
| F1.3: missing concrete `gt generate-approval-packet` command | Approval Packet Plan section | Added concrete CLI invocation with all required flags + `--content-file` for the v4 spec text. |
| Non-blocking: bare `pytest` hygiene at line 329 | Spec-to-Test Mapping verification table row | Changed to `python -m pytest platform_tests/ groundtruth-kb/tests/` (explicit interpreter prefix). |
| Non-blocking: stale citation to scoping classifier-fix `-001` (latest is GO -002) | Prior Deliberations bullet | Updated to `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md` (latest GO). |
| `artifact_version: 4` framing | Field table | Labeled as optional/non-gating metadata per Codex's confirmation that it is not in `REQUIRED_PACKET_FIELDS`. Retained in packet for human readability. |

The D3 + D4 scanner / lifecycle / test / backfill design from -001 is preserved unchanged. All cross-cutting Specification Links and target_paths from -001 are preserved.

## Supersession Declaration

This proposal explicitly supersedes the in-flight v3 implementation thread `gtkb-s358-w1-retirement-machinery-correction` (latest GO -019, awaiting Prime corrected impl report) per the S372 owner AUQ ("Supersede v3 (Recommended)") and Codex's design verdict in the scoping GO -002 ("the deterministic D4 rule is new machine-checkable behavior and should be captured in `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4").

The s358-w1 thread implements v3's over-broad "any thread citing WI = WI VERIFIED" semantic — the very defect this v4 fix corrects. Landing v3 first (then v4 to fix it) was rejected because v3 VERIFIED would itself trigger the v3 misfire it's about to fix (loop). Recasting s358-w1 mid-stream to v4 was rejected because Codex's GO -019 explicitly authorized v3 scope and exact v3-specific packet paths.

Disposition of s358-w1:
- No further Prime action on s358-w1 (the v3-corrected impl report is NOT filed).
- When this v4 follow-on reaches VERIFIED, s358-w1 is closed-by-supersession; its NO-GO/REVISED/GO history remains as the audit record of the v3 design path that was superseded.
- s358-w1 should not surface as Prime-actionable in AXIS-2; this is the textbook scoping-terminal-with-successor pattern the WI-3442 classifier-fix bridge (`gtkb-axis-2-scoping-terminal-classifier-fix`, GO -002) addresses.

## Summary

The project-verified-completion automation currently auto-completes a project authorization and retires its project when ANY VERIFIED bridge thread cites a gating work item — including incidental citations in reauthorization, governance, or advisory threads. This proposal implements the D3 + D4 fail-safe design approved by Codex at scoping GO -002:

- **D3 (top-version-only scan)**: `verified_work_items()` and `_verified_work_items()` collect `Work Item:` lines ONLY from the VERIFIED top version of a thread, not all versions. Closes the all-versions sub-defect.
- **D4 (`implements`-linkage gate, primary)**: a WI is counted as VERIFIED-complete only when a VERIFIED bridge thread is linked to the project via `project_artifact_links.relationship = 'implements'` AND cites the WI in its top VERIFIED version. Absent any `implements` link, auto-completion does NOT fire (fail-safe to manual completion). Closes the incidental-citation primary defect.

Implementation lands new behavior in scanner + lifecycle, regression tests proving incidental-citation and superseded-version citations do NOT auto-complete, and a v4 spec mutation (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4) capturing the deterministic `implements`-linkage discriminator.

## Owner Decisions / Input

- **S372 AUQ (2026-05-29)**: owner selected "Supersede v3 (Recommended)" for the v3/v4 sequencing question — directing this v4 follow-on as the canonical fix that supersedes the in-flight v3 implementation thread. Captured in chat as the operative owner-decision for this proposal's supersession framing.
- **S372 AUQ (2026-05-29)**: owner selected "Fix the classifier first" for the broader triage path; that proposal landed as `gtkb-axis-2-scoping-terminal-classifier-fix-001` (now GO at -002). This v4 follow-on is the parallel governance-layer fix the owner directed next ("File the follow-on impl bridge for the v4 scanner fix").
- **S372 AUQ (2026-05-29)**: owner selected "Use mine (WI-3365 + S358 + supersession)" — resolved the parallel-session contention between this canonical thread and the predecessor `gtkb-project-completion-scanner-addressing-thread-fix-implementation` thread (now WITHDRAWN at -003). This REVISED-1 honors that decision; the WI-3443/PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001 artifacts created by the predecessor session are orphaned and require separate backlog hygiene retirement (out of scope for this proposal).
- **S373 AUQ (DECISION-0772, 2026-05-29T13:54Z)**: owner selected "Fix the scanner (v4) first, then Slice 3" — the load-bearing pivot toward the v4 scanner-fix path that this proposal executes.
- **S373 AUQ (DECISION-0773, 2026-05-29T13:54Z)**: owner selected "Design-scoping round first" — directed the scoping `governance_review` thread at `-001`, which Codex GOed at `-002` authorizing this follow-on.
- **S373 AUQ (this session, 2026-05-29T15:24Z)**: owner selected "Take over canonical thread: file REVISED -003" — directed this current session to address Codex's NO-GO -002 findings on the canonical thread (acknowledging the parallel-session supersession).
- **S358 owner-decision** (`DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`): the standing S358 PAUTH covers governance-correction work including this v3→v4 evolution; no fresh PAUTH is required.
- Standing pre-approval coverage: `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` is active and covers WI-3365.
- The v4 GOV spec mutation requires a formal-artifact-approval packet at implementation time (see Approval Packet Plan section); the owner approves the v4 spec content via AskUserQuestion at packet-creation time.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (current v3 `specified`) — the spec being evolved to v4; v4 captures the deterministic `implements`-linkage discriminator.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority. This REVISED-1 file is `bridge/gtkb-project-completion-scanner-addressing-thread-fix-003.md`; the INDEX update inserts `REVISED: bridge/gtkb-project-completion-scanner-addressing-thread-fix-003.md` at top of `bridge/INDEX.md` for the canonical `Document: gtkb-project-completion-scanner-addressing-thread-fix` entry; append-only. No deletion or rewrite of `-001` NEW or `-002` NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant cross-cutting spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-Test Mapping below maps each behavioral claim to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH header present; WI-3365 is an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — govern the project-scoped authorization vehicle used here.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the v4 GOV mutation requires a formal-artifact-approval packet.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the fix must preserve byte-parity of `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` (they call into the corrected scanner/lifecycle, so the hooks themselves don't change; parity is preserved automatically).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root under the GT-KB root; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — fix delivered as durable scanner/lifecycle changes + v4 spec mutation + regression tests; full traceability between owner decisions, this thread, the v4 spec, and the executable verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — v4 spec creation triggers MemBase versioning + approval-packet evidence; WI-3365 lifecycle advances to VERIFIED on post-impl report.
- `GOV-STANDING-BACKLOG-001` — WI-3365 active under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. This proposal is NOT a bulk-ops mutation (single-WI, single-spec scope).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the D4 `implements`-linkage discriminator is deterministic/machine-checkable (no LLM judgement at scan time), per the principle. Approval-packet generation also uses the deterministic `gt generate-approval-packet` CLI per the principle.
- `SPEC-AUQ-POLICY-ENGINE-001` — the v3/v4 supersession, the parallel-session resolution, and the v4 spec content are all owner-authorized via AskUserQuestion (S372 + S373 + packet-creation AUQ).

## Requirement Sufficiency

**New machine-checkable behavior required: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4.** v3 says "the bridge thread addressing the work item" — "addressing" is not machine-checkable as written. v4 defines "addressing" deterministically as "linked to the project via `project_artifact_links.relationship = 'implements'` AND cites the WI in its top VERIFIED version." The v4 spec change is bundled into this implementation per Codex's scoping verdict ("the deterministic D4 rule is new machine-checkable behavior and should be captured in `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4...before the implementation relies on it for automatic retirement").

WI-3365 ("W1 retirement-machinery correction") is the operative WI. Its original title references v2, but the WI's intent — correcting the project-completion machinery — fits the v3→v4 evolution. WI title MAY be updated as part of this implementation via the standard backlog update flow (or left as historical artifact; not load-bearing).

No new GOV/SPEC/ADR/DCL beyond the v4 GOV revision is required.

## KB Mutation Scope

**YES — v4 spec mutation.** This implementation will:

- Insert a new version (v4) of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` into MemBase (`groundtruth.db`) via the standard `db.insert_spec(..., version=4)` path. Append-only; v3 row preserved.
- Create a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json` (date prefix matches actual creation day; re-revise if review extends past 2026-05-29).
- No other MemBase mutation. WI-3365 remains as-is until its lifecycle advances naturally to VERIFIED on Codex VERIFIED of the post-impl report.

`groundtruth.db` is in `target_paths` per the KB-mutation-completeness check.

## WI Citation Disclosure

Declares work for **WI-3365** only. WI-3438 is the WI affected by the v3 misfire (DECISION-0772 evidence; cited as context — not implemented here). WI-3443 was the orphaned WI from the predecessor session's parallel filing (now requires separate backlog hygiene retirement). Other WIs cited in this proposal text are bridge-historical references (s358-w1 supersession evidence), not implementation declarations. No other WI is implemented here.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — the S358 owner-decision authorizing governance-correction work (covers v3→v4 evolution).
- `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` — provenance record for the v1 manufactured-variant error; relevant audit context.
- `DELIB-2502` — the reauth owner-decision chain whose VERIFIED thread triggered the v3 misfire loop; concrete evidence of the defect.
- `DELIB-2503` — S373 session owner-decision chain (vehicle + PAUTH for the predecessor session's parallel filing); preserved as historical record of the parallel-session resolution.
- DA search `search_deliberations("GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 implements linkage scanner addressing thread")` returned the scoping thread chain + the S358 lineage; no prior decision rejects the v4 direction.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md` (Codex GO this thread family) — the design verdict authorizing this implementation.
- `bridge/gtkb-s358-w1-retirement-machinery-correction-019.md` (Codex GO of v3 implementation; superseded by this thread per S372 owner AUQ).
- `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md` (sibling S372 thread; classifier fix at GO -002 will recognize this thread as the s358-w1 → v4-implementation successor pattern).
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-003.md` (REVISED-as-withdrawal of the predecessor parallel filing; owner-AUQ authorized).

## v4 Spec Text (to be inserted into MemBase as GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4)

```
**Rule.** A backlog project — and its project authorization — is completed
and retired, together with all of the project's associated work items,
automatically when, and only when, every work item explicitly linked to that
project is VERIFIED. As long as any explicitly-linked work item is not
VERIFIED, the project cannot be completed or retired. Completion and
retirement require no owner AskUserQuestion confirmation; the transition is
automatic on the all-work-items-VERIFIED condition. Retirement is collective:
the project and its VERIFIED work items retire together.

**Owner-AUQ boundary.** Owner AskUserQuestion approval gates project start
(see GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and
GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001). Owner-AUQ does not gate
project completion or retirement.

**"VERIFIED work item" definition (v4 — deterministic).** A work item WI-X
is VERIFIED when ALL of the following hold:

1. There exists a bridge thread T whose top status in `bridge/INDEX.md` is
   VERIFIED.
2. T is linked to the work item's project P via the
   `project_artifact_links.relationship = 'implements'` row (an explicit
   "addressing thread" linkage, distinct from the default 'related').
3. The TOP VERIFIED version of T (NOT any superseded NO-GO/REVISED version)
   carries `Work Item: WI-X` metadata.

**Fail-safe behavior (v4 — new).** If a project P has gating work items but
NO `implements`-linked VERIFIED bridge thread covers all of them, the
auto-completion pass does NOT fire. The project is NOT auto-retired. The
condition is surfaced as a manual-review notification (e.g., via the
project-completion-surface hook output) so the owner can either link the
addressing thread explicitly or take other corrective action.

**Supersession (v1 → v2 → v3 → v4).** v1 (S350) required owner AUQ
confirmation — the product of a Prime Builder manufactured-variant error.
v2 (S357 owner directive) reversed the owner-confirmation gate: completion
and retirement are automatic. v3 (S358) corrected the historical record
without behavioral change. v4 (S372) adds the deterministic
`implements`-linkage discriminator + top-version-only scan + fail-safe
manual-review behavior; this closes the over-broad "any thread citing WI =
WI VERIFIED" incidental-citation defect that caused three project
mis-retirements in S372 alone (per DELIB-2502 and the gtkb-project-
completion-scanner-addressing-thread-fix-scoping evidence).

**v3 → v4 supersession reason.** v3 said "the bridge thread addressing the
work item has reached terminal VERIFIED status." "Addressing" was not
machine-checkable: the scanner counted any `Work Item:` citation as
addressing evidence, including incidental citations from reauthorization,
governance, and advisory threads. v4 makes "addressing" deterministically
machine-checkable via the `relationship = 'implements'` linkage gate.

**Backfill / transition rule.** When v4 lands, existing active projects MAY
have gating WIs whose addressing threads exist but lack the explicit
`implements` link. For each affected project: the implementation phase
adds the `implements` linkage from the project to the impl thread (one
backfill operation per project; owner-AUQ approved via the standard
project-authorization flow). Projects with no addressable VERIFIED thread
remain in their current state; the fail-safe surfaces them for manual
review. Backfill is one-time and auditable in the
`project_artifact_links` history.

**Scanner / lifecycle implementation contract.** The deterministic
checker MUST: (a) iterate only the top VERIFIED version of each VERIFIED-
topped bridge thread; (b) gate completion on the existence of at least
one `project_artifact_links` row where `project_id = P AND
relationship = 'implements' AND bridge_thread_slug = T`; (c) emit
fail-safe surface output instead of auto-retiring when (b) fails.
```

## Approval Packet Plan (for v4 spec mutation, per GOV-ARTIFACT-APPROVAL-001)

The packet is created at
`.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json`.

Required packet fields per the live schema at
`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` (specifically `REQUIRED_PACKET_FIELDS` at lines 11-24 and `VALID_ARTIFACT_TYPES` at lines 26-33):

| Field | Value source |
|---|---|
| `artifact_type` | `governance` (per live `VALID_ARTIFACT_TYPES`; this is the canonical type for GOV-* specs, matching the historical v2/v3 packets) |
| `artifact_id` | `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` |
| `action` | `update` (new version of existing spec; append-only) |
| `source_ref` | this bridge document at its GO version (e.g., `bridge/gtkb-project-completion-scanner-addressing-thread-fix-NNN.md` after GO lands) |
| `full_content` | the v4 spec text above (verbatim) |
| `full_content_sha256` | computed sha256 of the v4 spec full_content |
| `approval_mode` | `approve` (or `edit-and-approve` if owner iterates) |
| `presented_to_user` | `true` once owner is shown the v4 spec text via AskUserQuestion |
| `transcript_captured` | `true` (the chat presentation IS transcript capture) |
| `explicit_change_request` | "Insert v4 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 per the v4 Spec Text in this bridge proposal; supersedes v3 with deterministic `implements`-linkage discriminator + top-version-only scan + fail-safe manual-review behavior" |
| `changed_by` | `prime-builder/claude-opus-4` |
| `change_reason` | the GO'd bridge document name (e.g., `bridge/gtkb-project-completion-scanner-addressing-thread-fix-NNN.md`) |

Optional/non-gating metadata (not in `REQUIRED_PACKET_FIELDS`, retained for human readability):

- `artifact_version: 4`
- `approved_by: owner` (Mike Palmeter)

### Deterministic packet generation command

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, the packet is generated by the deterministic `gt generate-approval-packet` CLI rather than hand-assembled JSON. The v4 spec text is written to a content file first, then the CLI is invoked:

```bash
# Step 1: write v4 spec text to a content file (in-root, scratch path)
# The content file's exact bytes become the packet's full_content + full_content_sha256.
mkdir -p .gtkb-state/bridge-drafts
cat > .gtkb-state/bridge-drafts/gov-project-verified-completion-retirement-001-v4.txt <<'V4_END'
<verbatim v4 spec text from the "v4 Spec Text" section above>
V4_END

# Step 2: invoke the deterministic packet generator
python -m groundtruth_kb generate-approval-packet \
  --kind formal \
  --artifact-type governance \
  --artifact-id GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 \
  --action update \
  --content-file .gtkb-state/bridge-drafts/gov-project-verified-completion-retirement-001-v4.txt \
  --source-ref bridge/gtkb-project-completion-scanner-addressing-thread-fix-<GO-VERSION>.md \
  --explicit-change-request "Insert v4 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 per the v4 Spec Text; supersedes v3 with deterministic implements-linkage discriminator + top-version-only scan + fail-safe manual-review behavior" \
  --change-reason "bridge/gtkb-project-completion-scanner-addressing-thread-fix-<GO-VERSION>.md" \
  --approval-mode approve \
  --changed-by prime-builder/claude-opus-4 \
  --out .groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json \
  --validate-after
```

The `--validate-after` flag has the CLI read back the written packet and run `validate_approval_packet()` against it to confirm the on-disk packet satisfies `REQUIRED_PACKET_FIELDS` and `VALID_ARTIFACT_TYPES`. Validation failure aborts before MemBase insertion.

### Owner-visible approval presentation at implementation time

1. Show the exact v4 spec text (verbatim, full content) + the `full_content_sha256` to the owner in chat.
2. Ask via AskUserQuestion: "Approve v4 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (per the displayed text)?" with options approve / reject / request edits.
3. On approve, run the CLI command above with `--approval-mode approve` and `presented_to_user: true`. The CLI writes the packet JSON with `full_content_sha256` computed from `--content-file` bytes.
4. Insert the v4 spec row via `db.insert_spec(..., version=4)`. The formal-artifact-approval-gate validates the MemBase write against the packet on the protected-path PreToolUse hook surface.

The packet is one-time per content version; iteration produces fresh packets.

## Proposed Scope

### IP-1: D3 + D4 in scripts/project_verified_completion_scanner.py

Modify `verified_work_items()` (currently `scripts/project_verified_completion_scanner.py:73-101`):

```python
def verified_work_items(project_root: Path) -> set[str]:
    """Return WIs deterministically classified as VERIFIED per v4.

    A WI counts as VERIFIED only when:
      - A bridge thread T's top status in INDEX is VERIFIED;
      - T is `implements`-linked to a project (relationship='implements');
      - T's TOP VERIFIED version (NOT prior versions) carries `Work Item: <wi>`.

    Falls back to fail-safe (empty set for the affected project) when no
    `implements`-linked VERIFIED thread covers a gating WI.
    """
    verified = set()
    parse_result = parse_index(_read_index(project_root), project_root=project_root)
    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if top.status.value != "VERIFIED":
            continue
        # D3: read ONLY top version's content for Work Item metadata
        top_file = project_root / top.file_path
        if not top_file.is_file():
            continue
        content = top_file.read_text(encoding="utf-8", errors="ignore")
        wi_lines = _extract_work_item_lines(content)  # parses only `Work Item: WI-NNNN` from top file
        # D4: check `implements`-linkage in project_artifact_links
        if not _has_implements_link(project_root, doc.name):
            continue  # fail-safe: thread not declared as addressing implementation
        verified.update(wi_lines)
    return verified


def _has_implements_link(project_root: Path, bridge_slug: str) -> bool:
    """Check current_project_artifact_links for relationship='implements' on this slug."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return False
    import sqlite3
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "SELECT 1 FROM current_project_artifact_links "
            "WHERE bridge_thread_slug = ? AND relationship = 'implements' "
            "LIMIT 1",
            (bridge_slug,),
        )
        return cur.fetchone() is not None
    finally:
        con.close()
```

The old all-versions scan loop is removed. The fail-safe is implicit in the D4 gate (no `implements` link → thread skipped → no spurious WI completion).

### IP-2: D3 + D4 duplicate in groundtruth-kb/src/groundtruth_kb/project/lifecycle.py

The same D3 + D4 logic is applied to `_verified_work_items()` at `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:402-431`. Implementation mirrors IP-1 exactly (byte-identical D3 + D4 semantic).

Additionally, `auto_complete_ready_authorizations()` (`lifecycle.py:608-650`) gains the v4 fail-safe surface: when a project has gating WIs but no covering `implements`-linked VERIFIED thread, the function emits a fail-safe notification (return a structured "manual-review-required" record) rather than auto-completing/retiring.

### IP-3: Backfill operation for existing active projects

Add a one-time backfill helper `backfill_implements_links()` in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`. For each currently-active project P:

1. Identify P's implementation bridge thread by inspecting `bridge_thread_slug` references in P's `project_artifact_links` rows + manual confirmation via owner-AUQ for ambiguous cases.
2. Insert a `project_artifact_links` row with `relationship='implements'` for the identified thread.
3. Skip projects where no clear implementation thread exists; surface for manual review.

The backfill is owner-AUQ approved on a per-project basis to avoid silent mis-linkage. Phase 1 lands the helper; Phase 2 (separate bridge thread) runs it against the active project set.

### IP-4: v4 GOV spec mutation in groundtruth.db

Insert v4 row via `db.insert_spec("GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001", version=4, status="specified", description=<v4 text>, ...)` after the formal-artifact-approval packet is owner-approved.

### IP-5: Regression and unit tests

Add to `platform_tests/scripts/test_project_verified_completion_scanner.py`:

1. `test_incidental_citation_thread_does_not_complete_wi` — VERIFIED thread cites WI-X but has no `implements` link to WI-X's project. `verified_work_items()` MUST exclude WI-X.
2. `test_top_version_only_scan` (D3) — VERIFIED-topped thread where superseded version cites WI-Y but top VERIFIED version does not. `verified_work_items()` MUST exclude WI-Y.
3. `test_implements_link_thread_completes_wi` (positive D4) — VERIFIED thread with `implements` link to WI-X's project, top version cites WI-X. `verified_work_items()` includes WI-X.
4. `test_fail_safe_no_implements_link_no_completion` — project with gating WI, no `implements`-linked VERIFIED thread; auto-completion does NOT fire; manual-review surface emitted.

Add to `groundtruth-kb/tests/test_project_artifacts.py`:

5. `test_lifecycle_verified_work_items_implements_gate` — mirror of test 1 against `lifecycle._verified_work_items()`.
6. `test_auto_complete_fail_safe_emits_manual_review` — `auto_complete_ready_authorizations()` returns a manual-review record when fail-safe fires.

All existing scanner/lifecycle/hook tests MUST continue to PASS (regression boundary).

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 — incidental citation excluded | `test_incidental_citation_thread_does_not_complete_wi`, `test_lifecycle_verified_work_items_implements_gate` | PASS |
| v4 D3 — top-version-only | `test_top_version_only_scan` | PASS |
| v4 D4 — `implements` link gates completion | `test_implements_link_thread_completes_wi` | PASS |
| v4 fail-safe — no `implements` link surfaces manual review | `test_fail_safe_no_implements_link_no_completion`, `test_auto_complete_fail_safe_emits_manual_review` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal filed; INDEX updated | (this filing) | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook parity preserved | `platform_tests/hooks/test_project_completion_surface.py` continues PASS | PASS |
| `GOV-ARTIFACT-APPROVAL-001` — v4 approval packet present + valid | `python -m groundtruth_kb generate-approval-packet ... --validate-after` succeeds | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header lines present | (header inspection) | PASS |
| no-regression on existing scanner/lifecycle tests | `python -m pytest platform_tests/ groundtruth-kb/tests/` | PASS |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — D4 discriminator deterministic | inspection: SQLite query, no LLM | PASS |

Verification commands:

- `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_project_completion_surface.py -q --tb=short`
- `python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py`

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-1 implementation proposal.
- [ ] v4 spec approval packet written via `python -m groundtruth_kb generate-approval-packet --kind formal --artifact-type governance ...` and owner-approved via AskUserQuestion.
- [ ] v4 row inserted into `groundtruth.db` via `db.insert_spec(version=4)`.
- [ ] IP-1, IP-2, IP-3, IP-5 landed; all 6 new tests + all existing scanner/lifecycle/hook tests PASS.
- [ ] `ruff check` clean on all target paths.
- [ ] `python .claude/hooks/project-completion-surface.py` (smoke test against current INDEX) does NOT auto-retire any project that lacks an `implements`-linked VERIFIED thread; emits manual-review surface for affected projects.
- [ ] `gtkb-s358-w1-retirement-machinery-correction` thread is recognized as superseded by this thread's VERIFIED (no further Prime action on s358-w1).
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] Backfill Phase 2 thread filed as follow-on (separate bridge thread) for owner-AUQ-guided population of `implements` links across the active project set.

## Risk and Rollback

Risk: **moderate-to-high** — touches the auto-retirement automation that affects every active project (148 projects / 30 active authorizations). Mitigation: the fail-safe direction is conservative — if anything goes wrong with the new logic, the failure mode is "no auto-retirement" not "spurious auto-retirement"; this is strictly safer than v3's current behavior.

Risks identified:

- **Backfill miss**: existing active projects without proper `implements` links will not auto-complete after v4 lands. Mitigation: this IS the fail-safe behavior — manual review surface fires; owner can explicitly link or override. Phase 2 backfill bridge fills the gap systematically.
- **Hook parity drift**: scanner + lifecycle duplicate logic must stay in sync. Mitigation: shared regression test fixture (one fixture, run against both call paths) catches divergence.
- **v3 misfire still triggers between filing this proposal and VERIFIED**: any VERIFIED bridge thread filed between now and the v4 fix landing may still cause project mis-retirement. Mitigation: this is the existing risk class; the proposal does not introduce new exposure. Owner-known per DECISION-0772.
- **s358-w1 supersession governance**: the in-flight v3 thread at GO -019 will not reach VERIFIED. Mitigation: documented in Supersession Declaration section; owner-AUQ approved via S372 ("Supersede v3"). The s358-w1 NO-GO/REVISED/GO history remains as audit record.
- **Parallel-session WI/PAUTH orphans**: WI-3443 (created by predecessor session) and PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001 (created by predecessor session) are orphaned by the parallel-session resolution. Mitigation: separate backlog hygiene operation retires WI-3443 + revokes the PAUTH (out of scope for this proposal; tracked as a follow-on task).
- **Backfill bridge filing date drift**: if review extends past 2026-05-29, the packet filename date will not match implementation day. Mitigation: re-revise this proposal with corrected date before implementation begins.

Rollback:
- Revert the scanner + lifecycle changes (single source file pair).
- Revert the 6 added tests.
- The v4 spec row is append-only; no rollback (v3 remains as the prior version; reverting to v3 behavior is a code revert + no spec change needed).
- Delete the approval packet JSON.

## Loyal Opposition Asks

1. Confirm the F1 fixes (artifact_type=governance, correct schema path, concrete gt CLI command) close the prior NO-GO -002 findings.
2. Confirm the v4 spec text captures the deterministic discriminator as Codex's scoping verdict required (`relationship = 'implements'` + top-version-only scan + fail-safe manual-review behavior).
3. Confirm IP-1 + IP-2 D3 + D4 implementation matches v4 spec semantics.
4. Advise on the backfill split (Phase 1 helper here; Phase 2 separate bridge per-project). Is the per-project owner-AUQ approach acceptable, or do you prefer a single batch backfill?
5. Confirm the supersession of `gtkb-s358-w1-retirement-machinery-correction` (no v3 impl report filed; v3 thread closes-by-supersession on this thread VERIFIED) per S372 owner AUQ.
6. Advise whether the v4 spec mutation should include explicit retroactive supersession-by-document linkage (a `superseded_by` link from v3 → v4 in MemBase) at implementation time.
7. Confirm the orphaned WI-3443 + PAUTH-WI-3443 cleanup is appropriately scoped as a separate backlog hygiene operation (not bundled into this v4 thread).
8. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
