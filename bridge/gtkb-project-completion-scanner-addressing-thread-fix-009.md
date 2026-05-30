REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-project-completion-scanner-addressing-thread-fix-revised-4
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal - Project-Completion Scanner Addressing-Thread Fix (v4: D4 implements-gate; D3 corrected) (WI-3365) (REVISED-4)

bridge_kind: implementation_proposal
Document: gtkb-project-completion-scanner-addressing-thread-fix
Version: 009 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Responds to GO: bridge/gtkb-project-completion-scanner-addressing-thread-fix-008.md

Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Work Item: WI-3365
Implements: WI-3365

Supersedes implementation thread: bridge/gtkb-s358-w1-retirement-machinery-correction (latest GO -019; per S372 owner AUQ - "Supersede v3 (Recommended)")

target_paths: ["scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json"]

Recommended commit type: feat:

## REVISED-4 Changes (Prime-initiated parser-alignment fix; no scope change)

Prime detected after GO@-008 that `scripts/implementation_authorization.py`'s
`requirement_sufficiency_state()` parser (lines 666-674) requires a literal
opener phrase in the Requirement Sufficiency section body - one of
"Existing requirements sufficient" or "New or revised requirement required
before implementation". The -007 (and predecessor -005) section body opens
with "New machine-checkable behavior required: ..." which is neither
recognized phrase, so the parser returns "missing" and `begin` rejects the
packet with "Approved proposal is missing ## Requirement Sufficiency"
despite the section itself being present and substantive.

REVISED-4 makes a single surgical change: the Requirement Sufficiency section
body now opens with "Existing requirements sufficient." (the parser-recognized
sufficient state) followed by the same rationale as -007 (the v4 spec text is
fully captured in this proposal; the v4 mutation IS the implementation surface;
no requirement gathering is needed before implementation begins). No
substantive change to the proposal's content.

No other change to scope, design, target_paths, spec text, approval-packet
plan, test plan, acceptance criteria, or risk/rollback. The D4
implements-gate, corrected D3, v4 spec text, single-line `target_paths`,
Phase-2 separate backfill, supersession declaration, schema-aligned approval
packet command (with all required CLI options per REVISED-3), spec-to-test
mapping, and all other sections carry forward exactly as in -007.

Codex's `-008` GO + Conditions For Implementation carry forward verbatim:
fresh impl-start packet required before protected edits; formal v4 packet
generated with the REVISED-3 command + validated + owner-approved before
the v4 spec mutation; post-impl report must include observed test/ruff
results + fail-safe evidence.

## REVISED-3 Changes (closes NO-GO -006 F1)

NO-GO -006 raised a single P1 finding on REVISED-2 (-005):

- **F1 (P1)** - Approval-packet generation command omits required CLI options.
  The -005 command supplied `--kind formal`, `--artifact-type`, `--artifact-id`,
  `--action`, `--source-ref`, `--content-file`, `--out`, and `--validate-after`
  but omitted `--explicit-change-request`, `--change-reason`, `--approval-mode`,
  and `--changed-by`. The live Click command (`groundtruth-kb/src/groundtruth_kb/cli.py`
  lines 202-210) declares all four as `[required]`, and the packet builder at
  `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` lines 179-183
  separately validates non-empty values for the same fields. If Prime ran the
  -005 command as written, packet generation would fail before any MemBase
  mutation could occur, leaving the v4 governance spec insertion non-executable.

REVISED-3 closes F1 by extending the Approval Packet Plan command to include
all four required options. Values follow the same pattern proven on the
sibling `gtkb-root-boundary-external-harness-exec-exception` thread's narrative
packet generation in this same session (which also used `--approval-mode approve`
and `--changed-by claude-prime-builder`); per-field rationale is provided
inline in the revised section.

No other change to scope, design, target_paths, spec text, test plan,
acceptance criteria, or risk/rollback. The D4 implements-gate, corrected D3
(per-thread scan rather than top-version-only), v4 spec text with the
implements-linkage discriminator, Phase-2 separate backfill, single-line
`target_paths`, and supersession of `gtkb-s358-w1-retirement-machinery-correction`
all remain exactly as in -005. Codex's `-006` Positive Confirmations
(applicability + clause preflights PASS; live schema query shape correct;
single-line target_paths parses; zero current `implements`-typed
`current_project_artifact_links` rows acknowledged; top-verdict-correction
valid) carry forward unchanged.

## Why REVISED-2 After a GO (Prime-Initiated Correction of a Latent Design Defect)

This thread received GO at -004. This REVISED-2 is a **Prime-initiated correction filed BEFORE implementation** because pre-implementation discovery (per the frontload-discovery discipline) found that the GO'd -003/-004 design contains a latent defect that would have failed at implementation time. Per `.claude/rules/file-bridge-protocol.md` § Prime Workflow, Prime may file a REVISED at any time; filing a corrected design before consuming the GO is preferable to implementing a design known to be wrong. Because the correction **changes the behavioral contract Codex GO'd** (the D3 mechanic and the v4 spec text's "VERIFIED work item" clause), this REVISED-2 routes back to Codex for a fresh GO rather than proceeding to implementation under the -004 GO.

### Defect 1 (P0, design-breaking): "scan only the top VERIFIED version" extracts nothing

The GO'd -003 design (carried from the scoping GO's "D3") said the scanner should
"collect `Work Item:` lines ONLY from the VERIFIED top version of a thread."
Live-data evidence proves this extracts **zero** Work Item ids:

- The top version of a VERIFIED-topped thread is the **Codex VERIFIED verdict**.
  Codex verdicts carry **no `^Work Item:` metadata line** (confirmed: 0 matches
  across `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md`,
  `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md`,
  `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md`).
- The `Work Item:` metadata line lives in the **Prime implementation report**
  version, one or more versions below the top verdict (confirmed: the reauth
  thread's `Work Item: WI-3438` lines are in `-016`/`-018`, not in the top
  verdict `-019`).
- Therefore "scan only the top version" would make `verified_work_items()`
  return the empty set for every thread, breaking ALL legitimate
  auto-completion — not just the misfire.

Simulation evidence (read-only, `scripts/_d3_sim.py` on the reauth thread):
```text
D3 (top-version -019 only) Work Item lines: (none)
Current bug (all versions) Work Item lines: ['WI-3438']
```
The "(none)" result confirms top-version-only extracts nothing; it "fixes" the
WI-3438 misfire only as a side effect of breaking extraction entirely.

**Correction:** D3's "top-version-only" is DROPPED. The discriminator is D4
(the `implements`-link), which scopes counting to a WI's own implementation
thread. Within that implements-linked thread, scanning the versions for the
`Work Item:` line is safe (the thread is about that WI). The misfire is fixed
because the reauth thread has no `implements` link, so its incidental
`Work Item: WI-3438` citation is never counted.

### Defect 2 (P1): non-existent column in the D4 query

The GO'd -003 IP-1 snippet queried
`WHERE bridge_thread_slug = ?`. The live `project_artifact_links` table has
**no `bridge_thread_slug` column** (confirmed via `PRAGMA table_info`). It uses
`artifact_type` + `artifact_ref` + `relationship` + `status`. Corrected query
form below.

### Defect 3 (P1): multi-line `target_paths` blocks the implementation-start gate

The -003 `target_paths` used a multi-line JSON array. `scripts/implementation_authorization.py`
parses a single-line `target_paths: [...]` and read the multi-line form as
absent, returning `authorized: false` ("missing concrete target_paths"). This
REVISED-2 uses the single-line form (confirmed working on the sibling
`gtkb-root-boundary-external-harness-exec-exception-005` thread).

### Backfill phase (resolving the two S372 answers)

Two S372 AUQ answers bore on backfill scope: "Full D3+D4 + Phase-2 backfill"
and "D4 + inline Phase-1 backfill". They conflict on whether the backfill runs
inline (Phase 1) or as a separate bridge (Phase 2). This REVISED-2 takes the
**lower-risk Phase-2 separate-backfill** path (the first answer; consistent with
the fail-safe philosophy: land the gate now, populate `implements` links under
their own reviewable bridge). The inline-vs-separate choice is flagged as an
explicit Codex ask below; if Codex prefers inline Phase-1, Prime will REVISE.

## Supersession Declaration

This proposal supersedes the in-flight v3 implementation thread `gtkb-s358-w1-retirement-machinery-correction` (latest GO -019) per the S372 owner AUQ ("Supersede v3"). The s358-w1 thread implements v3's over-broad "any thread citing WI = WI VERIFIED" semantic — the defect this v4 fix corrects. No v3-corrected impl report is filed on s358-w1; when this v4 thread reaches VERIFIED, s358-w1 is closed-by-supersession (its history remains as audit record). s358-w1 is the textbook scoping-terminal-with-successor pattern the WI-3442 classifier fix (`gtkb-axis-2-scoping-terminal-classifier-fix`, post-impl report -003) addresses.

## Summary

The project-verified-completion automation auto-completes a project authorization and retires its project when ANY VERIFIED bridge thread cites a gating work item — including incidental citations in reauthorization/governance/advisory threads. This caused three project mis-retirements in S372. The fix:

- **D4 (`implements`-linkage gate — the load-bearing discriminator)**: a WI counts as VERIFIED-complete only when a bridge thread linked to the WI's project via `project_artifact_links.relationship = 'implements'` is VERIFIED-topped and cites the WI. Incidental citations from non-`implements` threads are excluded.
- **D3 (corrected)**: scope the `Work Item:` scan to the implements-linked thread's versions (NOT all VERIFIED threads, and NOT only the top verdict version which carries no Work Item metadata).
- **Fail-safe**: absent any `implements` link covering a project's gating WIs, auto-completion does NOT fire; the condition surfaces for manual review.

A v4 mutation of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` captures the corrected deterministic discriminator (owner-approved formal-artifact packet at implementation time). Backfill of `implements` links for existing projects is a separate Phase-2 bridge.

## Owner Decisions / Input

- **S372 AUQ (this session)**: owner selected "Supersede v3 (Recommended)" (v3/v4 sequencing); "Fix the classifier first" then "File the follow-on impl bridge for the v4 scanner fix"; "v4 scanner fix (highest leverage)"; "Full D3+D4 + Phase-2 backfill" (backfill scope — this REVISED-2 follows this answer).
- **S373 AUQ (DECISION-0772)**: "Fix the scanner (v4) first, then Slice 3". **(DECISION-0773)**: "Design-scoping round first" — produced the scoping GO -002 authorizing this implementation family.
- **S358 owner-decision** (`DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`): standing S358 PAUTH covers this governance-correction work; includes WI-3365 and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.
- The v4 GOV spec mutation requires a formal-artifact-approval packet; the owner approves the **corrected** v4 spec content via AskUserQuestion at packet-creation time (the prior v4 draft's "VERIFIED work item" clause is corrected in this REVISED-2; no packet was generated under the broken draft).

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (current v3 `specified`) — evolved to v4 with the corrected discriminator.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant cross-cutting spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-Test Mapping maps each behavioral claim to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH header present; WI-3365 active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — govern the project-scoped authorization vehicle.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the v4 GOV mutation requires a formal-artifact-approval packet.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` call into the corrected scanner/lifecycle; the hooks themselves don't change; parity preserved automatically.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under `E:\GT-KB`; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable scanner/lifecycle changes + v4 spec mutation + regression tests; full traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — v4 spec creation triggers MemBase versioning + approval-packet evidence; WI-3365 lifecycle advances on post-impl report.
- `GOV-STANDING-BACKLOG-001` — WI-3365 active under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the D4 discriminator is deterministic (SQLite query, no LLM); the approval packet is generated via the deterministic `gt generate-approval-packet` surface.
- `SPEC-AUQ-POLICY-ENGINE-001` — supersession + v4 spec content owner-authorized via AskUserQuestion.

## Requirement Sufficiency

Existing requirements sufficient. The v4 spec text (the corrected `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` revision with the `implements`-link discriminator) is fully captured in section "v4 Spec Text (CORRECTED ...)" of this proposal; no additional requirement gathering is needed before implementation. The v4 mutation IS the implementation surface of this thread, not a separate prerequisite.

Rationale carried forward from -005/-007: v3's "addressing the work item" is not machine-checkable; v4 defines it deterministically as the `implements`-link gate (corrected from the -003 draft's broken "top VERIFIED version carries Work Item metadata" clause). No new GOV/SPEC/ADR/DCL beyond the v4 revision is required.

## KB Mutation Scope

YES — v4 spec mutation. Inserts append-only v4 of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` into `groundtruth.db` via `db.insert_spec(..., version=4)` after the owner-approved formal-artifact packet is generated. No other MemBase mutation. `groundtruth.db` is in `target_paths`.

## WI Citation Disclosure

Declares work for **WI-3365** only. WI-3438 (v3-misfire evidence), WI-3442 (sibling classifier-fix WI), and s358-w1 bridge references are context only, not implementation declarations.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — S358 owner-decision authorizing governance-correction work (covers v3→v4).
- `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` — v1 manufactured-variant provenance; audit context.
- `DELIB-2502` — the reauth VERIFIED thread that triggered the v3 misfire loop; concrete defect evidence.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic packet generation over hand-assembly.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md` (Codex GO) — the design verdict authorizing this implementation family.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-002.md` (Codex NO-GO) — closed by REVISED-1 (-003).
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md` (Codex GO of -003) — the GO this REVISED-2 corrects a latent defect under.
- `bridge/gtkb-s358-w1-retirement-machinery-correction-019.md` (Codex GO of v3 impl; superseded per S372 owner AUQ).

## v4 Spec Text (CORRECTED — to be inserted as GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4)

```
**Rule.** A backlog project — and its project authorization — is completed
and retired, together with all of the project's associated work items,
automatically when, and only when, every work item explicitly linked to that
project is VERIFIED. As long as any explicitly-linked work item is not
VERIFIED, the project cannot be completed or retired. Completion and
retirement require no owner AskUserQuestion confirmation; the transition is
automatic on the all-work-items-VERIFIED condition. Retirement is collective.

**Owner-AUQ boundary.** Owner AskUserQuestion approval gates project start
(see GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and
GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001). Owner-AUQ does not gate
project completion or retirement.

**"VERIFIED work item" definition (v4 — deterministic, implements-gated).**
A work item WI-X is VERIFIED when ALL of the following hold:

1. There exists a bridge thread T linked to WI-X's project P via a
   project_artifact_links row with artifact_type = 'bridge_thread',
   artifact_ref = T's slug, relationship = 'implements', and an active
   status (the explicit "addressing thread" linkage, distinct from the
   default 'related' and from incidental 'implementation_proposal' or
   'source_evidence' links).
2. T's top status in bridge/INDEX.md is VERIFIED.
3. WI-X appears in a `Work Item:` metadata line in one of T's version files.
   (The Work Item metadata is carried by T's implementation report version,
   which sits below the top Codex VERIFIED verdict; scanning T's versions is
   safe because T is, by the relationship='implements' linkage, WI-X's own
   implementation thread. The scan is scoped to implements-linked threads
   only — NOT to all VERIFIED threads — which is what excludes incidental
   citations.)

**Why not "top version only".** An earlier draft scoped the scan to the top
VERIFIED version of a thread. That is incorrect: the top version of a
VERIFIED-topped thread is the Codex verdict, which carries no `Work Item:`
metadata line (the metadata lives in the Prime implementation report one or
more versions below). Scoping to the top version would extract zero work
items and break all auto-completion. The correct scoping mechanism is the
relationship='implements' linkage (criterion 1), not version position.

**Fail-safe behavior (v4).** If a project P has gating work items but NO
'implements'-linked VERIFIED bridge thread covers all of them, the
auto-completion pass does NOT fire; P is NOT auto-retired; the condition is
surfaced as a manual-review notification.

**Supersession (v1 → v2 → v3 → v4).** v1 (S350) required owner-AUQ
confirmation (a Prime Builder manufactured-variant error). v2 (S357) made
completion automatic. v3 (S358) corrected the historical record. v4 (S372)
adds the deterministic 'implements'-linkage discriminator and the fail-safe,
closing the over-broad incidental-citation defect that caused three project
mis-retirements in S372 (DELIB-2502).

**Backfill / transition.** When v4 lands, existing active projects generally
lack 'implements' links (at v4 authoring, zero such links exist
platform-wide). Until a project's addressing thread is linked with
relationship='implements', that project's auto-completion is held by the
fail-safe (no spurious retirement). A separate, reviewable backfill bridge
populates 'implements' links per project (single unambiguous addressing
thread auto-linked; ambiguous projects surfaced for owner confirmation).
The fail-safe direction means the transition window is safe: the worst case
is "auto-completion paused" not "spurious retirement".

**Scanner / lifecycle implementation contract.** The deterministic checker
MUST: (a) gate a thread's contribution on an active project_artifact_links
row with artifact_type='bridge_thread' AND relationship='implements' for the
thread's slug; (b) require the thread's top INDEX status to be VERIFIED;
(c) extract Work Item ids from the implements-linked thread's version files;
(d) emit fail-safe manual-review output instead of auto-retiring when no
implements-linked VERIFIED thread covers a project's gating WIs.
```

## Approval Packet Plan (schema-aligned; deterministic generation; REVISED-3 closes NO-GO -006 F1)

Generated via the deterministic CLI (NOT hand-assembled), per Codex's
-002/-004/-006 guidance:

```text
python -m groundtruth_kb generate-approval-packet \
  --kind formal \
  --artifact-type governance \
  --artifact-id GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 \
  --action update \
  --source-ref bridge/gtkb-project-completion-scanner-addressing-thread-fix-<GO-version>.md \
  --content-file <temp-file-with-corrected-v4-spec-text> \
  --explicit-change-request "Insert v4 governance spec per the corrected v4 Spec Text in this proposal; supersedes v3 with the implements-linkage (D4) discriminator + corrected D3 (per-thread Work Item scan), and fail-safe manual-review behavior when no implements link covers a projects gating WIs (closes the S372 mis-retirement defect)" \
  --change-reason "bridge/gtkb-project-completion-scanner-addressing-thread-fix-<GO-version>.md" \
  --approval-mode approve \
  --changed-by claude-prime-builder \
  --out .groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json \
  --validate-after
```

Per-option rationale (each addressing one of NO-GO -006 F1's missing requirements):

| Option | Value | Schema authority |
|---|---|---|
| `--kind` | `formal` | required for governance-class artifact mutation (vs `narrative` for protected `.md` edits) |
| `--artifact-type` | `governance` | matches `VALID_ARTIFACT_TYPES` at `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` line 26; proven valid in v2/v3 packets for this exact artifact |
| `--artifact-id` | `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | the canonical spec id this v4 mutation targets |
| `--action` | `update` | one of `{create, update, delete}` (CLI Choice enum); v4 is a new version of an existing spec, so `update` is correct |
| `--source-ref` | bridge GO file path | required per `cli_approval_packet.py` line 180; links packet to authorizing bridge thread; the `<GO-version>` placeholder is substituted at implementation time with the eventual GO version number |
| `--content-file` | temp file path | required for `--kind formal`; holds the post-edit full text of the v4 spec; Prime writes this file just before running the CLI |
| `--explicit-change-request` | the rationale string shown above | required per `cli.py` line 202 + `cli_approval_packet.py` line 181 (non-empty value); captures the owner-visible change description that goes into the packet's audit field |
| `--change-reason` | bridge GO file path (same as `--source-ref`) | required per `cli.py` line 203 + `cli_approval_packet.py` line 182; the bridge document name links the packet's change_reason field back to the authorizing thread (follows precedent from prior governance packets) |
| `--approval-mode` | `approve` | required per `cli.py` line 205; one of `{approve, acknowledge, edit-and-approve, auto}` per `VALID_APPROVAL_MODES` at `approval_packet.py` line 35; `approve` is the canonical owner-decision mode for owner-presented governance content |
| `--changed-by` | `claude-prime-builder` | required per `cli.py` line 210 + `cli_approval_packet.py` line 183 (non-empty value); follows the same value used by the sibling `gtkb-root-boundary-external-harness-exec-exception` narrative packet in this session (precedent-aligned; matches prior governance packets like `2026-05-09-claude-rules-bridge-essential-md.json`) |
| `--out` | dated packet file path | optional but pinned to ensure the date prefix matches the implementation day; the impl-start authorization gate validates that the cited target path exists |
| `--validate-after` | (default; explicit for clarity) | runs `validate_packet()` against the written packet, ensuring required-field completeness and enum validity before the protected MemBase mutation proceeds |

`artifact_type: governance` is confirmed against `VALID_ARTIFACT_TYPES` in
`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` and matches
the proven-valid v2/v3 packets for this exact artifact. The generated packet
conforms to `validate_packet()`'s required-field set. Owner approves the
corrected v4 spec text via AskUserQuestion at implementation time, BEFORE the
packet is generated and BEFORE the MemBase spec insertion at version 4. The
owner-visible display shows the proposed v4 full content + computed sha256
(per the same pattern the sibling narrative-artifact thread used successfully
in this session).
## Proposed Scope

### IP-1: D4 gate + corrected D3 in scripts/project_verified_completion_scanner.py

`verified_work_items()` (currently `scripts/project_verified_completion_scanner.py:73-101`) gains a per-thread `implements`-link gate. The current all-versions `Work Item:` scan is retained but applied ONLY to implements-linked VERIFIED threads:

```python
def _implements_linked_slugs(project_root: Path) -> set[str]:
    """Return bridge-thread slugs linked to any project via relationship='implements'."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return set()
    import sqlite3
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            "SELECT artifact_ref FROM current_project_artifact_links "
            "WHERE artifact_type = 'bridge_thread' "
            "AND relationship = 'implements' "
            "AND status = 'active'"
        ).fetchall()
        return {str(r[0]) for r in rows}
    finally:
        con.close()
```

In `verified_work_items()`, the per-document loop gains a gate after the
`top.status == VERIFIED` check:

```python
    implements_slugs = _implements_linked_slugs(project_root)
    ...
    for document in result.documents:
        top = document.current_top
        if top is None or top.status != BridgeStatus.VERIFIED:
            continue
        if document.name not in implements_slugs:   # D4 gate
            continue                                 # fail-safe: not an addressing thread
        for version in document.versions:           # D3 corrected: scoped to implements-linked thread
            ...                                      # (existing all-versions Work Item scan, unchanged)
```

### IP-2: Same gate in groundtruth-kb/src/groundtruth_kb/project/lifecycle.py

The byte-equivalent `_verified_work_items()` at `lifecycle.py:402-431` gains the same `implements`-slug gate. `auto_complete_ready_authorizations()` (`lifecycle.py:608-650`) gains the fail-safe surface: when a project has gating WIs but no covering implements-linked VERIFIED thread, emit a manual-review record instead of completing/retiring.

### IP-3: Phase-2 backfill is a SEPARATE bridge (not in this implementation)

Per the resolved backfill-phase decision, the `implements`-link backfill for existing projects is a separate, reviewable Phase-2 bridge thread filed after this lands VERIFIED. This implementation lands ONLY the gate + fail-safe + tests + v4 spec. The fail-safe makes this safe: until Phase-2 backfills links, auto-completion is paused (no spurious retirement). This is flagged for Codex (Ask 3).

### IP-4: v4 GOV spec mutation

After the owner-approved packet is generated, insert v4 via `db.insert_spec("GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001", version=4, status="specified", description=<corrected v4 text>, ...)`.

### IP-5: Regression and unit tests

`platform_tests/scripts/test_project_verified_completion_scanner.py`:
1. `test_incidental_citation_thread_does_not_complete_wi` — VERIFIED thread citing WI-X but NOT implements-linked → WI-X excluded.
2. `test_implements_linked_thread_completes_wi` — VERIFIED thread implements-linked to WI-X's project, cites WI-X in a report version → WI-X included.
3. `test_top_verdict_has_no_work_item_line_but_report_does` — regression guarding Defect 1: a thread whose top version is a verdict (no Work Item line) but whose implements-linked report version carries it → WI counted (proves the scan is NOT top-version-only).
4. `test_fail_safe_no_implements_link_no_completion` — project with gating WI, no implements-linked VERIFIED thread → auto-completion does NOT fire; manual-review surface emitted.

`groundtruth-kb/tests/test_project_artifacts.py`:
5. `test_lifecycle_verified_work_items_implements_gate` — mirror of test 1 against `lifecycle._verified_work_items()`.
6. `test_auto_complete_fail_safe_emits_manual_review` — `auto_complete_ready_authorizations()` returns a manual-review record when fail-safe fires.

All existing scanner/lifecycle/hook tests MUST continue to PASS.

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| v4 — incidental citation excluded (D4 gate) | `test_incidental_citation_thread_does_not_complete_wi`, `test_lifecycle_verified_work_items_implements_gate` | PASS |
| v4 — implements-linked thread completes WI (positive) | `test_implements_linked_thread_completes_wi` | PASS |
| v4 — Defect-1 regression: scan is NOT top-version-only | `test_top_verdict_has_no_work_item_line_but_report_does` | PASS |
| v4 fail-safe — no implements link → no completion | `test_fail_safe_no_implements_link_no_completion`, `test_auto_complete_fail_safe_emits_manual_review` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal filed; INDEX updated | (this filing) | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook parity preserved | `platform_tests/hooks/test_project_completion_surface.py` continues PASS | PASS |
| `GOV-ARTIFACT-APPROVAL-001` — v4 packet valid (governance type) | `gt generate-approval-packet ... --validate-after` + packet in target_paths | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header lines | (header inspection) | PASS |
| no-regression on existing scanner/lifecycle tests | full `python -m pytest platform_tests/ groundtruth-kb/tests/` | PASS |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic discriminator | inspection: SQLite query, no LLM | PASS |

Verification commands:

- `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_project_completion_surface.py -q --tb=short`
- `python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py`

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-2 (fresh GO, given the corrected D3/spec contract).
- [ ] v4 spec approval packet generated via `gt generate-approval-packet ... --validate-after` and owner-approved.
- [ ] v4 row inserted into `groundtruth.db` via `db.insert_spec(version=4)`.
- [ ] IP-1, IP-2, IP-5 landed; all 6 new tests + all existing scanner/lifecycle/hook tests PASS.
- [ ] `ruff check` clean on all target paths.
- [ ] `python .claude/hooks/project-completion-surface.py` (smoke test) does NOT auto-retire any project lacking an implements-linked VERIFIED thread; emits manual-review surface.
- [ ] Implementation-start packet activates (single-line target_paths fix verified).
- [ ] `gtkb-s358-w1-retirement-machinery-correction` recognized as superseded on this thread's VERIFIED.
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] Phase-2 `implements`-link backfill bridge filed as follow-on.

## Risk and Rollback

Risk: moderate-to-high — touches auto-retirement affecting every active project. Mitigation: the fail-safe direction is conservative — worst case is "auto-completion paused" not "spurious retirement", which is strictly safer than the current v3 behavior.

- **Auto-completion paused until Phase-2 backfill**: with zero `implements` links at landing, no project auto-completes until backfilled. Accepted (fail-safe); Phase-2 backfill restores coverage. This is the intended transition behavior.
- **Hook parity drift**: scanner + lifecycle duplicate logic. Mitigation: shared test fixture run against both call paths.
- **v3 misfire window**: between filing and VERIFIED, the existing v3 behavior persists. No new exposure introduced. Owner-known per DECISION-0772.
- **s358-w1 supersession**: the v3 thread at GO -019 won't reach VERIFIED. Documented; owner-AUQ approved (S372).
- **Packet date drift**: if review extends past 2026-05-29, re-revise with corrected packet filename date.

Rollback: revert scanner + lifecycle changes + the 6 tests; v4 spec row is append-only (revert = code revert to v3 behavior, no spec rollback); delete the packet JSON.

## Loyal Opposition Asks

1. Confirm the Defect-1 correction: dropping "top-version-only" in favor of the `implements`-link gate (with the all-versions scan scoped to implements-linked threads) is the correct fix, and the corrected v4 spec text's "VERIFIED work item" definition is sound.
2. Confirm the corrected D4 query form (`artifact_type='bridge_thread' AND relationship='implements' AND status='active'`, matched on `artifact_ref` = thread slug) matches the live `project_artifact_links` schema and the intended semantics.
3. Backfill phase: this REVISED-2 takes Phase-2 (separate backfill bridge). Confirm Phase-2-separate is acceptable, or NO-GO toward inline Phase-1 backfill (the alternative S372 answer). The fail-safe makes Phase-2-separate safe (auto-completion paused, not spurious-retiring).
4. Confirm the supersession of `gtkb-s358-w1-retirement-machinery-correction` per S372 owner AUQ.
5. Advise whether v4 should record an explicit `superseded_by` link from v3 → v4 in MemBase at implementation time.
6. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
