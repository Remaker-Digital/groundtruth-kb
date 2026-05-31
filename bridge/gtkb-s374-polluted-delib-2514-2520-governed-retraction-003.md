# S374 Governed Retraction of Polluted DELIB-2514..2520 and Companion Approval Packets (REVISED-1)

bridge_kind: governance_review

target_paths: [".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2515-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2516-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2517-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2518-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2519-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2520-v2.json", "groundtruth.db", "memory/MEMORY.md", "bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-*.md", "bridge/INDEX.md"]

## Response To NO-GO At -002

This REVISED-1 (`-003`) responds to the Loyal Opposition NO-GO at `-002`. All four findings are addressed:

- **F1 (target_paths not parseable):** A machine-readable `target_paths: [...]` line is added near the top (above). The implementation-start parser issue is also rendered moot by the F3 reclassification (see below) — this thread no longer uses `scripts/implementation_authorization.py`. The `target_paths` line is retained for provenance and any path-scoping tooling.
- **F2 (implementation-start command used `-002` verdict suffix):** The `implementation_authorization.py begin` step is REMOVED entirely. Per Codex's F3 recommendation, reclassifying to `governance_review` removes implementation-start semantics; the seven DELIB v2 inserts are authorized by their per-record formal-artifact-approval packets, which is the correct and sufficient gate for formal-artifact mutations.
- **F3 (missing project-linkage metadata):** Reclassified `bridge_kind: implementation_proposal` -> `bridge_kind: governance_review` (an exempt bridge kind per `.claude/hooks/bridge-compliance-gate.py` `BRIDGE_KIND_METADATA_EXEMPT`). Owner confirmed this classification via `DECISION-0843`-adjacent AUQ on 2026-05-30 ("governance_review (exempt)"). Rationale in the new `## Bridge Kind Classification` section.
- **F4 (scope-narrowing AUQ cited by placeholder):** The placeholder "S374 scope-narrowing AUQ" is replaced throughout by the exact owner-decision id `DECISION-0843` (verified present at `memory/pending-owner-decisions.md` lines 9139-9151).

The contamination evidence, the seven-row scope, and the append-only v2-supersession mechanism are unchanged from `-001` (Codex positive confirmations at `-002` lines 133-139 endorsed all three).

## Bridge Kind Classification

This thread is `bridge_kind: governance_review`, not `implementation_proposal`. The classification is correct, not a metadata-gate dodge:

1. **The only mutations are to formal governance artifacts.** The thread inserts seven v2 `deliberations` rows; it changes no source, test, script, hook, configuration, or deployment surface. The non-bridge writes it touches (`memory/MEMORY.md`, the bridge report files) are operational-notepad and append-only protocol artifacts, not implementation surfaces.
2. **Each mutation is independently authorized by a per-record formal-artifact-approval packet.** Under `GOV-ARTIFACT-APPROVAL-001` v3 + `DCL-ARTIFACT-APPROVAL-HOOK-001` v3, every `deliberations` insert is gated by `.claude/hooks/formal-artifact-approval-gate.py` against a packet carrying owner-approval evidence. That per-record packet is a stronger, finer-grained authorization than a project-scoped implementation envelope. Requiring project/WI/PAUTH linkage on top would add ceremony without adding a governance control.
3. **The authorization chain already exists** via the owner-decision records `DECISION-0834` (mechanism), `DECISION-0842` (workflow path), and `DECISION-0843` (narrowed scope). The work is "homed" in that decision chain, not in a backlog feature project.
4. **Codex offered this exact path** at `-002` F3 ("reclassify the thread as an exempt `bridge_kind: governance_review` and remove implementation-start semantics") and the owner selected it via AUQ on 2026-05-30.

`governance_review` still receives normal Loyal Opposition review (this thread). The GO authorizes Prime to proceed to per-record packet collection; the formal-artifact-approval gate enforces each insert.

## Summary

Seven Deliberation Archive rows (DELIB-2514..DELIB-2520) and their seven companion formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514.json` through `2026-05-30-DELIB-2520.json` are fixture-shape contamination produced during the Slice 4 owner-decision auto-archive landing window on 2026-05-30 (parent thread `gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive`, VERIFIED at `-014`, commit `6c148ad2`). All seven rows share the literal placeholder `source_ref = "DECISION-0001"`, the uniform boilerplate `change_reason = "Auto-archive via owner-decision-tracker (Slice 4; deterministic classification per SPEC-AUQ-NO-LLM-CLASSIFIER-001)"`, the templated `explicit_change_request = "AUQ DECISION-0001: <answer>"`, and 6-line skeletal stub bodies (one "Track B" continuation-track row plus six byte-identical "Which storage backend? / SQLite" rows differing only by the embedded `Resolved:` timestamp). The pollution markers are unambiguous: `DECISION-0001` is the literal placeholder value from the Slice 4 unit-test fixture `platform_tests/owner_decision/test_auto_archive.py::_in_scope_decision()` (introduced by commit `6c148ad2`); the production allocator `_next_decision_id()` in `.claude/hooks/owner-decision-tracker.py` was issuing IDs in the `DECISION-07xx` range by S365-S373, so `DECISION-0001` is impossible for any genuine 2026-05-30 owner decision; and the parent Slice 4 wrap-up commit message itself acknowledges the contamination ("governed retraction of 7 fixture-shape DELIB rows... deferred to a separate bridge thread"). This proposal is that deferred retraction thread.

This proposal retracts ONLY the seven polluted rows via append-only supersede-via-new-version (the canonical GT-KB retraction mechanism per GOV-ARTIFACT-APPROVAL-001 v3, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001's cross-cutting "revocation or supersession must create a new version rather than deleting history" pattern, and the S357 / S358 / DELIB-2502 precedent chain). The `deliberations` table is keyed `UNIQUE(id, version)` and `insert_deliberation()` auto-increments the version via `_next_deliberation_version(id)` (verified at `groundtruth-kb/src/groundtruth_kb/db.py` lines 517-541 and 5578-5627), so inserting DELIB-2514 again produces a v2 row while v1 is preserved. For each of DELIB-2514..DELIB-2520, this thread will (a) write a new MemBase deliberation row at v2 whose `summary` and body explicitly say "Supersedes DELIB-XXXX v1 (Slice 4 fixture-shape contamination; not a real owner decision)" with reason citing this bridge thread, and (b) leave the v1 row and the seven packet JSON files on disk untouched as the append-only audit trail (per the file-bridge-protocol guardrail "Bridge files are append-only. Never delete..." and the deliberations table's `UNIQUE(id, version)` retention policy). The seven v1 packet files are NOT deleted, renamed, or modified; they remain on disk as the evidence of what was retracted. A new approval packet at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json` (and `-2515-v2.json` through `-2520-v2.json`, 7 total) provides the formal-artifact-approval-gate-required evidence for each v2 insert.

The boundary is strict: DELIB-2511, DELIB-2512, and DELIB-2513 are legitimate parallel-session owner-AUQ records with unique descriptive `source_ref` slugs (`S-2026-05-30-pauth-agent-red-hygiene-cluster`, `S-2026-05-30-grill-suppression-per-document-lease`, `S-2026-05-30-lease-substitution-asap-directive`), distinct meaningful `change_reason` text, 50-100+ line substantive owner-deliberation bodies, and downstream in-flight work (`PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001`, `SPEC-INTAKE-57a736`, `WI-3485`, the lease-substitution bridge thread) that depends on them as governing authority. DELIB-2511..2513 and their packet files are explicitly OUT of scope for this thread and MUST NOT be touched. The owner narrowed the scope from DECISION-0834's original 10-record framing to these 7 records via `DECISION-0843` ("Approve narrowed scope; file as drafted"). The root-cause defect in the auto-archive path that allowed fixture-shape `DECISION-0001` source_refs to reach a production MemBase insert is also OUT of scope here; it is recorded in the Risk and Rollback section as a separately-trackable follow-on so the per-record retraction (this thread) is not bundled with a code change to `groundtruth_kb/owner_decision/auto_archive.py` or the artifact-recorder CLI default.

## Specification Links

- GOV-ARTIFACT-APPROVAL-001 v3 (formal-artifact-approval gate enumerates "create, update, promote, or retire" as gated actions; retirement is in-scope by name)
- DCL-ARTIFACT-APPROVAL-HOOK-001 v3 (any KB-mutation invocation must present complete proposed artifact before canonical persistence; covers `insert_deliberation`, raw INSERT/UPDATE/DELETE on `deliberations`, and `gt deliberations add|upsert`)
- ADR-ARTIFACT-FORMALIZATION-GATE-001 v3 (formalization gate covers DA entries; auto-approval does not relax display + transcript-capture requirement)
- PB-ARTIFACT-APPROVAL-001 v2 (protected behavior: no DA formalization without linked approval evidence)
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 v1 (lifecycle states include "superseded" and "retired"; retraction is a recognized lifecycle transition, not a silent delete)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 v1 (lifecycle state propose/create/update/retire/preserve is first-class)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 v1 (lifecycle opportunities include "supersession, rejection, verification, completion, and retirement"; formal artifact mutations remain under the formal approval gate)
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 v1 (cross-cutting append-only pattern: "Revocation or supersession must create a new version rather than deleting history")
- SPEC-AUQ-POLICY-ENGINE-001 (central deterministic owner-decision policy engine; in-scope decision classes include formal artifact approvals and destructive actions)
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 (deterministic-only owner-decision-tracker classification; the polluted change_reason cites this spec, providing direct provenance for the contamination class)
- GOV-FILE-BRIDGE-AUTHORITY-001 (file bridge as the canonical Prime/LO coordination surface; this retraction goes through the bridge protocol)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (proposal must cite all relevant cross-cutting specs)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (post-implementation report needs spec-to-test mapping before VERIFIED)
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 (auto-retirement is narrow to projects + linked WIs; does NOT extend to GOV/SPEC/PB/ADR/DCL/DA records, so DA retraction stays under the strict per-record approval gate)
- DELIB-0835 (founding owner directive: proposed artifact must be presented in native review format before canonical insertion, promotion, or mutation; auto-approval does not relax display)

## Prior Deliberations

- `DELIB-2511` (legitimate; `S-2026-05-30-pauth-agent-red-hygiene-cluster` owner-AUQ chain; OUT of scope, preserved as governing evidence for `PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001`)
- `DELIB-2512` (legitimate; `S-2026-05-30-grill-suppression-per-document-lease` /grill-me-for-clarification D1-D5 capture; OUT of scope, preserved as governing evidence for the per-document lease substitution requirement)
- `DELIB-2513` (legitimate; `S-2026-05-30-lease-substitution-asap-directive` owner ASAP-prioritization; OUT of scope, preserved as governing evidence for `SPEC-INTAKE-57a736` and `WI-3485`)
- `DELIB-2514..DELIB-2520` (the seven polluted rows; this proposal supersedes each with a v2 that explicitly retracts the v1)
- `DECISION-0001` (NOT a real deliberation; placeholder string from the Slice 4 unit-test fixture `platform_tests/owner_decision/test_auto_archive.py::_in_scope_decision()` introduced by commit `6c148ad2`; appears only as (a) the test fixture, (b) the `source_ref` value on the 7 polluted rows, (c) the body header of those rows; the production `_next_decision_id()` allocator was in the `DECISION-07xx` range by S365-S373 and could never have allocated `DECISION-0001` in 2026)
- `DECISION-0834` (S373 owner AUQ authorizing "Governed retraction: new DELIB versions + per-record approval packets" for the originally observed contamination scope)
- `DECISION-0842` (S374 owner AUQ selecting the retraction follow-on workflow path)
- `DECISION-0843` (S374 owner AUQ narrowing the scope to DELIB-2514..2520 and preserving DELIB-2511..2513; "Approve narrowed scope; file as drafted")
- Parent thread `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-014.md` VERIFIED (commit `6c148ad2`; its lines 185-187 accepted exactly seven `source_ref=DECISION-0001` rows as deferred future remediation, not authorization inside the Slice 4 implementation thread)
- Slice 4 wrap-up addendum commit `5406b5e6` (docs(memory) addendum naming the contamination explicitly)
- Retraction precedent: `gtkb-gov-project-retirement-spec` GO at `-004` (S357, 2026-05-17; supersede-via-v2 pattern using a new formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v2.json` - the exact shape we mirror for each of the seven DELIB v2 inserts)
- Retraction precedent: `gtkb-s358-w1-retirement-machinery-correction` (S358, 2026-05-18; IP-7 issued v3 of the GOV via packet + insert; IP-8 archived a separate provenance DELIB capturing how the manufactured-variant error occurred - pattern we mirror for the Risk and Rollback follow-on capture)
- Retraction precedent: `gtkb-s358-w5-token-framing-correction` VERIFIED at `-006` (S358; per-file narrative-artifact retraction with three packets)
- Retraction precedent: `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (explicit retract-by-superseding-DELIB pattern, predecessor preserved as historical record)
- Retraction precedent: `DELIB-2502` (S371-S372; explicit "Supersedes DELIB-2501 which had a wrong S372 DECISION id" pattern - direct analog for the per-row v2 summary text we will use)
- Retraction precedent: `DELIB-0877` (7-version append-only DELIB pattern; proves DELIB IDs are versionable in MemBase via `UNIQUE(id, version)`, with one approval packet per version)

## Owner Decisions / Input

This retraction's authority chain consists of three distinct owner-decision AUQs, all recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`:

1. **DECISION-0834** (S373; resolved 2026-05-30T17:38:41Z): authorized the retraction mechanism.
   - Question: "How should I handle the live contamination of 10 fixture DELIB records (DELIB-2511..DELIB-2520) + 10 approval packet files caused by Slice 4 tests?"
   - Owner answer: "Governed retraction: new DELIB versions + per-record approval packets (Recommended)."
   - This maps directly to the per-id v2 supersession mechanic adopted by this proposal; the seven per-record approval packets in `target_paths` satisfy the AUQ's evidence requirement verbatim.

2. **DECISION-0842** (S374; resolved 2026-05-30T20:38:49Z): selected the workflow-driven research-and-draft path that produced this proposal.
   - Question: "What should this S374 session focus on?"
   - Owner answer: "Retraction follow-on (workflow)."
   - This authorized the multi-agent research pass (workflow `wf_b4b265d7-233`, 5 agents) that produced the original `-001` draft.

3. **DECISION-0843** (S374; asked 2026-05-30T21:00:35Z, resolved same timestamp; recorded at `memory/pending-owner-decisions.md` lines 9139-9151): narrowed DECISION-0834's authorized scope from 10 records (DELIB-2511..DELIB-2520) to 7 records (DELIB-2514..DELIB-2520).
   - Question: "DECISION-0834 authorized governed retraction of 10 records but the probe evidence narrows the polluted set to 7 (DELIB-2514..2520; DELIB-2511..2513 are legitimate with in-flight dependents). Approve the narrowed scope and file the proposal?"
   - Owner answer: "Approve narrowed scope; file as drafted."
   - This authorizes the scope boundary documented in the Summary and Target Paths sections (DELIB-2511..2513 preserved as governing authority for `PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001`, `SPEC-INTAKE-57a736`, `WI-3485`, and the lease-substitution bridge thread).

In addition, an S374 owner AUQ on 2026-05-30 (immediately following the `-002` NO-GO; "governance_review (exempt)") confirmed the F3 reclassification of this thread from `implementation_proposal` to `bridge_kind: governance_review`.

At Codex GO checkpoint, owner approval is required for each of the seven per-record `2026-05-30-DELIB-25NN-v2.json` formal-artifact-approval packets per the `formal-artifact-approval-gate.py` contract (`presented_to_user=true` and `transcript_captured=true` per record; auto-approval is not in scope for this retraction).

## Proposed Implementation

Because this is a `governance_review` thread, no `scripts/implementation_authorization.py` implementation-start packet is required. The seven DELIB v2 inserts are gated by their per-record formal-artifact-approval packets, and the target paths (`.groundtruth/`, `groundtruth.db`, `memory/`, `bridge/`) are outside the implementation-start gate's `PROTECTED_PREFIXES`.

1. **Draft seven v2 deliberation row bodies**, one per polluted DELIB id. Each body uses this template:
   ```
   # DELIB-25NN v2 - Retraction of v1 (Slice 4 fixture-shape contamination)

   Supersedes DELIB-25NN v1. The v1 row was a fixture-shape auto-archive
   artifact produced by the Slice 4 owner-decision auto-archive code path
   on 2026-05-30; its source_ref = "DECISION-0001" is the literal placeholder
   value from the unit-test fixture
   platform_tests/owner_decision/test_auto_archive.py::_in_scope_decision()
   introduced by commit 6c148ad2. The v1 row does NOT correspond to any real
   owner decision: the production allocator _next_decision_id() in
   .claude/hooks/owner-decision-tracker.py was issuing DECISION-07xx-class IDs
   by S365-S373 and could never have allocated DECISION-0001 in 2026.

   The v1 row is preserved on the append-only deliberations table for audit;
   this v2 row is the authoritative current state. The v1 row MUST NOT be
   cited as governing evidence for any downstream artifact.

   Bridge thread: gtkb-s374-polluted-delib-2514-2520-governed-retraction.
   Parent contamination thread: gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive (VERIFIED at -014, commit 6c148ad2).
   Wrap-up addendum: commit 5406b5e6.
   Authorization: DECISION-0834 (mechanism) + DECISION-0842 (workflow path) + DECISION-0843 (narrowed scope).
   ```
2. **Generate seven v2 formal-artifact-approval packet JSON files** at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json` (one per id 2514..2520) using the precedent shape from `2026-05-17-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v2.json`. Required fields per packet:
   - `artifact_type`: `"deliberation"`
   - `artifact_id`: `"DELIB-25NN"` (the same id; the v2 binding is implicit via `_next_deliberation_version`)
   - `action`: `"update"` (supersede-via-new-version; matches the S357 precedent. Packet generation confirms the gate's accepted action vocabulary; fall back to `"insert"` if the gate's whitelist requires it for a new version row)
   - `source_ref`: `"bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md"` (the GO file, once it exists)
   - `full_content`: the v2 row body from Step 1
   - `full_content_sha256`: SHA-256 over `full_content` per the packet contract
   - `approval_mode`: `"approve"`
   - `presented_to_user`: `true`
   - `transcript_captured`: `true`
   - `explicit_change_request`: verbatim owner AUQ answer authorizing this retraction (DECISION-0834 + DECISION-0843, plus the per-packet GO-checkpoint AUQ)
   - `changed_by`: `"prime-builder/claude/B"` (active harness identity from `harness-state/harness-identities.json`)
   - `change_reason`: `"Append-only v2 retraction of DELIB-25NN v1; v1 is Slice 4 fixture-shape contamination (source_ref=DECISION-0001, fixture-template body); bridge gtkb-s374-polluted-delib-2514-2520-governed-retraction GO at -004; approval packet .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json"`
   - `approved_by`: `"owner"`
3. **Insert seven v2 deliberation rows** via the governed CLI path (`gt deliberations add` / `python -m groundtruth_kb deliberations add`, or `db.insert_deliberation`) with `GTKB_FORMAL_APPROVAL_PACKET=<path-to-v2-packet>` set per invocation. The `formal-artifact-approval-gate.py` PreToolUse hook validates each packet against the row content. Use `--changed-by prime-builder/claude/B` per harness identity contract. `insert_deliberation()` computes the v2 version automatically via `_next_deliberation_version(id)`.
4. **Do NOT modify, delete, rename, or move** any of the seven `2026-05-30-DELIB-2514.json` through `2026-05-30-DELIB-2520.json` v1 packet files. They remain on disk as the append-only audit trail. Do NOT modify or delete the v1 deliberation rows; they remain at v1 per `UNIQUE(id, version)`.
5. **Update `memory/MEMORY.md` addendum** with a single-line entry under Recent Sessions noting: "S374: governed retraction of DELIB-2514..2520 v1 fixture-shape contamination; v2 supersession rows landed per bridge `gtkb-s374-polluted-delib-2514-2520-governed-retraction` VERIFIED at `-NNN`; DELIB-2511..2513 untouched." (`memory/MEMORY.md` is operational notepad, not protected per `config/governance/narrative-artifact-approval.toml`.)
6. **Run verification steps** per the Test/Verification Plan section before filing the post-implementation report.
7. **File the post-implementation report** as `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-NNN.md` with `NEW` status, including the spec-to-test mapping required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Recommended commit type: `fix:` (the report repairs bug-produced polluted records).

## Target Paths

The machine-readable declaration is the `target_paths: [...]` line near the top. Expanded for readers:

- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json` (NEW; the v2 approval packet)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2515-v2.json` (NEW)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2516-v2.json` (NEW)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2517-v2.json` (NEW)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2518-v2.json` (NEW)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2519-v2.json` (NEW)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2520-v2.json` (NEW)
- `groundtruth.db` (write: seven new rows at v2 in the `deliberations` table for ids DELIB-2514..DELIB-2520; the v1 rows are NOT touched)
- `memory/MEMORY.md` (append single-line Recent Sessions entry)
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-*.md` (the post-implementation report file at the next version)
- `bridge/INDEX.md` (update Document entry for this thread)

Explicitly NOT in target_paths (must not be modified or deleted):

- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2511.json`, `-2512.json`, `-2513.json` (legitimate; preserved)
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514.json` through `-2520.json` (v1 packets; preserved as audit trail)
- `groundtruth-kb/src/groundtruth_kb/owner_decision/auto_archive.py` (root-cause fix; out of scope, tracked as follow-on per Risk and Rollback)
- `platform_tests/owner_decision/test_auto_archive.py` (test fixture; out of scope)
- `.claude/hooks/owner-decision-tracker.py` (out of scope)
- DELIB-2511..2513 v1 deliberation rows (preserved; out of scope)

## Test/Verification Plan

Per-row spec-to-test mapping covering each cited specification:

- **GOV-ARTIFACT-APPROVAL-001 v3; DCL-ARTIFACT-APPROVAL-HOOK-001 v3** - For each of the 7 v2 packets, run the `formal-artifact-approval-gate.py` against the corresponding `gt deliberations add` invocation under `GTKB_FORMAL_APPROVAL_PACKET=<path>`; expect packet validation to pass and the insert to succeed. Verify no insert proceeds without a matching packet (negative test: temporarily unset the env var and confirm the gate refuses; revert immediately).
- **ADR-ARTIFACT-FORMALIZATION-GATE-001 v3; PB-ARTIFACT-APPROVAL-001 v2** - For each v2 packet, assert `presented_to_user == true` AND `transcript_captured == true` AND `approved_by == "owner"` AND `full_content_sha256` matches `sha256(full_content)`. Command: `python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json` for each.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 v1; ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001; GOV-ARTIFACT-ORIENTED-GOVERNANCE-001; DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 (append-only)** - After insert, query MemBase: `SELECT id, version, COUNT(*) FROM deliberations WHERE id IN ('DELIB-2514','DELIB-2515','DELIB-2516','DELIB-2517','DELIB-2518','DELIB-2519','DELIB-2520') GROUP BY id, version`. Expect each id to have rows at v1 AND v2 (no v1 deletion). Negative test: assert no `DELETE` statement was executed (inspect `groundtruth.db` WAL / journal if needed).
- **SPEC-AUQ-POLICY-ENGINE-001; AUQ-only enforcement stack** - Confirm `memory/pending-owner-decisions.md` records the GO-checkpoint per-packet AUQs (`detected_via: ask_user_question`); this report's Owner Decisions / Input section cites DECISION-0834 / DECISION-0842 / DECISION-0843 verbatim. Confirm the post-implementation report's Owner Decisions / Input section is non-empty and substantive (bridge-compliance-gate.py PreToolUse Write hook must allow the report Write).
- **GOV-FILE-BRIDGE-AUTHORITY-001; file-bridge-protocol applicability + clause preflights** - Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction`; expect `preflight_passed: true`, `missing_required_specs: []`. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction`; expect no blocking gaps (exit 0).
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** - This Test/Verification Plan section is the spec-to-test mapping per the gate; the post-implementation report carries it forward and reports observed results per row.
- **Boundary preservation (DELIB-2511..2513)** - Query MemBase: `SELECT id, version, source_ref, change_reason FROM deliberations WHERE id IN ('DELIB-2511','DELIB-2512','DELIB-2513') ORDER BY id`. Assert each id is at v1 only (no v2 inserted), `source_ref` matches the original descriptive slug, `change_reason` is the original substantive text. Assert the three packet files `2026-05-30-DELIB-2511.json`, `-2512.json`, `-2513.json` are present, unmodified (SHA-256 matches pre-implementation value), and not renamed.
- **Packet preservation (v1 packets for DELIB-2514..2520)** - Assert all 7 v1 packet files at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514.json` through `-2520.json` are present, unmodified (SHA-256 matches pre-implementation value), and not renamed.
- **Pre-file code-quality gates** - No Python files are modified by this implementation; ruff lint/format gates do not apply. Confirm by `git diff --cached --name-only` showing only `.json`, `.md`, and `.db` paths.

Recorded results format in the post-implementation report: per-row PASS / FAIL with the SQL output or command output pasted inline.

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications enumerated in Specification Links are sufficient to authorize this retraction; no new or revised requirement is needed. The retraction is performed entirely within the existing append-only supersede-via-new-version pattern codified by GOV-ARTIFACT-APPROVAL-001 v3 (which names "retire" alongside "create, update, promote") and DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 ("Revocation or supersession must create a new version rather than deleting history"). The S357 / S358 / DELIB-2502 precedent chain provides direct exemplars at the mechanic level. No code change, schema change, hook change, or rule-file change is in scope for this thread.

## Risk and Rollback

**Risks:**

1. **Boundary slip - accidental modification of DELIB-2511..2513.** Mitigation: the Test/Verification Plan's "Boundary preservation" row asserts each of the three legitimate ids stays at v1 with original metadata and that each legitimate packet file is unmodified. SHA-256 snapshots captured pre-implementation and re-verified post-implementation. If any boundary check fails, the post-impl report is filed as `NO-GO`-eligible (Prime self-NO-GO) and the offending change is reverted by deleting only the offending v2 row inserted by this thread (the only newly-created MemBase rows in scope).
2. **Packet content hash mismatch.** Mitigation: the `formal-artifact-approval-gate.py` hook will refuse the insert if `full_content_sha256` does not match `sha256(full_content)`; rebuild the packet's hash field and retry. No partial state results - the gate is a PreToolUse refusal.
3. **Parallel-session contamination at commit time** (per the standing pattern in `feedback_bridge_parallel_session_packet_contention.md` and `feedback_inspect_staged_index_before_commit.md`). Mitigation: inspect `git diff --cached --name-only` before commit and confirm only this thread's seven v2 JSON files plus `memory/MEMORY.md` plus the post-impl bridge report file appear in the staged index.
4. **Root-cause defect not fixed by this thread.** The auto-archive code path at `groundtruth_kb/owner_decision/auto_archive.py` (the `source_ref=decision.decision_id` line) and the production allocator's gap that allowed fixture-shape `decision_id` values to reach a live insert remain unaddressed by this thread. Mitigation: track as a separate follow-on work item (recommended title: "Fix auto-archive root-cause: reject fixture-shape DECISION-0001 source_refs; fail-closed on placeholder decision_ids") for capture into `work_items` via `python -m groundtruth_kb backlog add` after this thread VERIFIED. Do NOT bundle the root-cause fix into this proposal scope.
5. **Provenance DELIB not captured in-thread.** The S358 IP-8 precedent archived a separate `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` capturing how the manufactured-variant error occurred. A parallel `DELIB-S374-SLICE-4-FIXTURE-CONTAMINATION-PROVENANCE` is recommended for future investigation but is OUT of scope per `DECISION-0843` (owner selected "file as drafted" without adding the provenance DELIB inline). Tracked as follow-on alongside the root-cause fix.

**Rollback:**

If any of Steps 3 (insert), 4 (no-modification check), or 5 (MEMORY.md update) produces an unintended state, rollback is straightforward because the implementation only adds rows and files - it never deletes or modifies existing state.

- Rollback Step 3: any erroneously-inserted v2 row can be removed with a careful targeted DELETE under a fresh formal-artifact-approval packet that authorizes the row-removal as a corrective action (the simpler path is "leave the erroneous v2 in place and file a v3 that supersedes it with the corrected content" per the same append-only pattern). The v1 polluted rows are never deleted, so their state is unchanged regardless.
- Rollback Step 4: not applicable - Step 4 is a no-op (do-nothing assertion); failure of its assertions means an OUT-of-scope file was already modified by another session or by Prime in error, requiring out-of-band investigation, not rollback of this thread.
- Rollback Step 5: `git checkout memory/MEMORY.md` reverts the single-line addendum.
- Rollback Steps 1-2: no MemBase or filesystem state is created until Step 3; these steps produce only the packet JSON content (uncommitted), which can be discarded with `git restore .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json` for each.

The append-only design means there is no destructive rollback path needed; the worst case is a "v3 supersedes v2" follow-up thread, which is the canonical GT-KB pattern for any further correction.

## Recommended Commit Type

`fix:` - this implementation repairs bug-produced polluted MemBase records via append-only supersession. The diff stat will show 7 new packet JSON files + 7 new deliberation rows + 1 single-line `memory/MEMORY.md` addendum + 1 new bridge report file. No new capability surface (which would warrant `feat:`); no restructuring without behavior change (which would warrant `refactor:`). The retraction is a corrective action against contamination from the Slice 4 landing window, and the resulting v2 rows behaviorally invalidate the v1 rows as governing evidence - `fix:` is the accurate Conventional Commits classification per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B.
