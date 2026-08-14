REVISED
::init gtkb lo
::open build

# WI-6216 Slice 1 — Close the High-Recurrence Gate Defects (D3 corrected)

bridge_kind: prime_proposal
Document: gtkb-wi6216-tool-and-gate-defect-corpus-slice-1
Version: 005
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a49752e4-5a9f-4290-bceb-910693b5271f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6216
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814

target_paths: [".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/destructive-gate.py", "scripts/implementation_authorization.py", ".harness-baseline-configuration/hooks/bridge-compliance-gate.py", ".harness-baseline-configuration/hooks/destructive-gate.py", ".goose/hooks/bridge-compliance-gate.py", ".goose/hooks/destructive-gate.py", ".goose/.projection-manifest.json", "platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py", "platform_tests/scripts/test_destructive_gate_target_resolution.py", "platform_tests/scripts/test_report_no_go_resume_tolerance.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation; it repairs three gate scripts,
projects the repaired hooks, and adds three regression-test modules.

Responds to: bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-004.md

---

## Why This Refile Exists (`-005`)

`-004` recorded **NO-GO on one mechanical ground only** and stated the substance
of `-003` was reviewed and accepted, with both `-002` Required-For-GO items
satisfied.

The block was provenance, not content: `-003` carried `author_identity: claude`,
a bare harness name with no role prefix. `bridge_lifecycle_resolver._author_role`
searches the identity string for a role token, so the bare form resolves `None`,
the operative version is classified legacy-shaped, and the typed publication
authorization refuses **any** verdict on the thread — including the GO the
reviewer had drafted.

Cause, stated plainly: the filing helper used for `-003` passed only model fields
in its author metadata and let the writer derive the identity, which produced the
bare form. The helper now passes `author_identity` and `author_harness_id`
explicitly, so this class cannot recur from that path.

**No content below this section changed from `-003`.** The D3 correction, the
scope, the verification plan and the specification links stand exactly as
reviewed.

## What Changed From `-001`

`-002` recorded **NO-GO on D3 only**, accepting D1 and D2 as proposed. This
revision changes D3 and nothing else. `target_paths`, D1, D2, scope items 4-5,
the specification links and the cross-harness disposition are unchanged.

`-002` offered two acceptable paths. This revision takes **path 2 — scope D3
explicitly as partial** — rather than path 1 (widen D3 to cover the index gate
and reconcile the two `Responds to:` contracts).

Reason: the widened repair changes lifecycle-resolver semantics that the
`gtkb-operation-taxonomy-baseline-path-rules` thread is concurrently changing
(it sits at `REVISED -009` awaiting review). Landing a second, independent
change to the same contract while that thread is open risks exactly the
interference the slice's own deferral list was drawn to avoid. Scoping D3 as
partial closes the annotation defect now, pins the residual gap with a test,
and leaves the contract reconciliation to a slice that can see the taxonomy
thread's outcome.

**`WI-6237` is NOT closed by this slice.** That is the substantive correction:
`-001` offered D3 as closing it.

## D3 — Corrected Mechanism Statement

`-001` Summary asserted the strict `Responds to:` parse was "empirically proven
**the sole blocker** on a live thread". That is **false**, and this revision
withdraws it.

Per `-002` F1, and per
`bridge/gtkb-operation-taxonomy-baseline-path-rules-006.md` F2 which superseded
the `-005` reading `-001` carried forward, `_report_no_go_resumption_authority`
in `scripts/implementation_authorization.py` imposes **three** independent
barriers, of which the regex is the last to execute:

1. **Index gate (executes first).** `report_status, report_file =
   entry.versions[1]`, then `if report_status not in {"NEW", "REVISED"}: return
   None`. Once a Prime `NO-ACTION` is filed, `versions[1]` holds that
   `NO-ACTION`, so the function returns `None` before any file is read or any
   regex is evaluated. The docstring states this is deliberate: it "rejects … a
   NO-GO that responds to an intervening NO-ACTION or other non-report
   artifact". Simulated against the real function over the live chain:
   `resumption = None`.
2. **Mutually unsatisfiable `Responds to:` contracts.**
   `scripts/bridge_lifecycle_resolver.py` line 438 requires version *N* to
   respond to version *N-1* exactly, while the resume path requires the latest
   `NO-GO` to respond to the *implementation report*. Those coincide only when
   the `NO-GO` immediately follows the report. Established by live publication
   attempt, rejected with `WRONG_RESPONDS_TO_LINK` — not by deduction.
3. **Strict annotation parse.** `re.search(r"(?im)^Responds\s+to\s*:\s*(\S+)\s*$", …)`
   rejects a trailing parenthetical annotation that the writer-side parser
   accepts.

On the live thread the annotation was **necessary but not sufficient**. D3
repairs barrier 3 only.

## Corrected Scope Item 3

3. **D3 repair (PARTIAL, by design)** in `_report_no_go_resumption_authority`:
   tolerate a trailing parenthetical annotation after the report path (match
   prefix, strip annotation), keeping every other check intact. This closes
   barrier 3 above.

   **Explicitly out of scope, and left open on `WI-6237`:** barrier 1 (the
   `versions[1]` index gate) and barrier 2 (the contract conflict between the
   lifecycle resolver's N→N-1 rule and the resume path's report-link rule). A
   chain carrying an intervening `NO-ACTION` remains unrecoverable after this
   slice. `WI-6237` stays open and its description is updated to name the two
   residual barriers so the remaining work is not rediscovered.

Scope items 1, 2, 4 and 5 are unchanged from `-001`.

## Corrected Verification Plan (D3 rows only)

| Defect | Test | Expected |
|---|---|---|
| D1 | `test_bridge_compliance_gate_pending_banner.py` | a fixture path claimed by an old parked NO-GO thread AND authorized by a live packet produces NO banner; without the packet, the banner names the most recently active matching thread; suffix collisions do not match |
| D2 | `test_destructive_gate_target_resolution.py` | single-file lock removal inside `.git/` passes; commit messages containing deletion verbs do not trigger; a genuine repo-root removal still blocks with the actual path named |
| D3 positive | `test_report_no_go_resume_tolerance.py` | in a chain where the `NO-GO` directly follows the implementation report, an annotated `Responds to:` line yields a resumption authority identical to the unannotated form |
| D3 **residual-gap pin** | `test_report_no_go_resume_tolerance.py` | in a chain carrying an intervening `NO-ACTION`, the annotated line still yields **no** authority — asserting the index gate is untouched and `WI-6237` remains open |
| D3 negative | `test_report_no_go_resume_tolerance.py` | proposal-level NO-GO still refuses resume |
| Regression floor | full `test_implementation_authorization.py` module + affected hook test modules, run in full rather than the new files alone | green; counts stated in the report, with any pre-existing failures shown identical at `HEAD` |

The residual-gap pin is the row that makes the partial scoping honest: without
it, the annotation fix would pass its acceptance test while the live failure
mode stayed silently unrecoverable — the false-confidence outcome `-002` F1
identified.

## D1 — Seventh Live Instance (evidence added, no scope change)

D1 was accepted as proposed. One further reproduction occurred after `-001` was
filed and is recorded here because it is a clean instance of the
root-anchored-matching sub-repair:

While editing `scripts/check_harness_parity.py` under a live GO'd packet for
`gtkb-wi6267-parity-projection-contract`, the banner fired with "Bridge
proposal for this module has NO-GO status. Review Codex findings at
`bridge/gtkb-adbr-t0-mechanism-repair`". That thread's latest version is a
2026-08-08 `NO-GO` whose `target_paths` are `config/agent-control/*`,
`.claude/rules/**`, `.claude/skills/*/helpers/**` and
`.claude/settings.json.rolegate-bak` — it does not reference
`scripts/check_harness_parity.py` at all. The banner fired on every edit in the
session despite a live packet authorizing the exact path.

This instance exercises three of the four D1 sub-repairs simultaneously:
live-packet suppression (a packet was held), parked-thread aging (the thread is
six days idle), and root-anchored matching (no declared path matches the edited
file). No scope change is requested; the fixture row for packet-suppression
already covers it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — D1/D3 repair the bridge protocol's own
  guidance and recovery surfaces.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — D3's stranded path is the lawful
  post-NO-GO revision route the resume authority exists to serve; barrier 1
  above is that DCL's semantics colliding with the resume contract.
- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2: hook repairs land in
  the baseline and project mechanically; the live `.claude` copy and the
  baseline copy change in lockstep in this slice (the `.claude` projector
  cutover is Phase D).
- `SPEC-1662` (GOV-18) — the new assertions are behavioral, not structural; the
  residual-gap pin is an assertion-quality requirement, not a nicety.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — the corrected D3 mechanism rests on
  re-read source and a live publication rejection, not on the superseded `-005`
  reading.

## Requirement Sufficiency

Existing requirements sufficient: each repair restores behavior the cited
specifications already require. No new requirement surface is created. The
partial scoping of D3 creates no requirement change either — it leaves an
already-tracked work item open rather than closing it prematurely.

## Owner Decisions / Input

- Owner standing directive (2026-08-13/14): capture and fix tool defects;
  WI-6216 is the owner-created carrier for exactly this corpus.
- Owner goal directive (this session): complete GET HEALTHY PHASE 2
  implemented, tested and committed.
- Owner decisions `DELIB-20260814-PHASE2-PAUTH-BRIDGE-MUTATION-CLASS` and
  `DELIB-20260814-PHASE2-PAUTH-BRIDGE-CLASS-NON-B` added the `bridge` mutation
  class to the Phase-2 execution authorizations, which is what permits this
  thread's report to be filed after implementation.
- No new owner decision is required for Slice 1. The choice between `-002`'s
  path 1 and path 2 is an implementation-sequencing judgement, made here and
  offered for review rather than escalated; deferred-item sequencing returns to
  the owner with the Slice 2 proposal.

## Prior Deliberations

- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-002.md` — the NO-GO
  this revision answers, including F1's correction of D3's mechanism.
- `bridge/gtkb-operation-taxonomy-baseline-path-rules-006.md` **F2** — the
  superseding diagnosis establishing barriers 1 and 2. Cited here in place of
  `-001`'s reliance on `-005`, per `-002`'s citation-currency finding.
- `bridge/gtkb-operation-taxonomy-baseline-path-rules-005.md` — the Prime
  `NO-ACTION` whose original "sole blocker" reading is superseded.
- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the 13-item inventory.
- `DELIB-20260814-PB-TOOL-TEST-FINDINGS-ADVISORY-BLOCKED` — carries D1's full
  mechanism and recommended remedy as finding 2.
- `WI-6237` / `TEST-11901` — D3's work item, which this slice deliberately
  leaves open.
- `bridge/gtkb-wi6267-parity-projection-contract-005.md` — records the seventh
  D1 instance described above.

## Cross-Harness Disposition

Unchanged from `-001`.

- **Claude Code (.claude/hooks/)**: repaired in place this slice (live
  enforcement surface); behavioral parity with the baseline copy is
  byte-lockstep by construction, verified by diff in the implementation report.
- **Goose (.goose/hooks/)**: behavioral parity via mechanical re-projection
  from the repaired baseline (engine `--check` 0-drift evidence in the report).
- **Codex (.codex/gtkb-hooks/), Cursor, Antigravity, API harnesses**: these
  surfaces do not carry the three affected gate scripts today. No behavioral
  change reaches them this slice; full parity arrives with their Phase D
  projector cutovers. Typed disposition: `deferred-to-projector-cutover`, no
  waiver required because no divergent behavior is introduced.

## Risk / Rollback

All three repairs narrow false-positive behavior; none loosens a true block:
D1 still banners genuinely-unauthorized edits, D2 still blocks real root-scoped
removals, D3 still refuses proposal-level NO-GO resumes and — by the residual-gap
pin — still refuses resumption across an intervening `NO-ACTION`.

The residual risk this revision accepts explicitly: a thread stranded behind
barriers 1 and 2 remains stranded until a later slice. That state is unchanged
from today, is now pinned by test rather than latent, and `WI-6237` stays open
to carry it.

Rollback is reverting the three scripts and re-projecting; the tests pin the
repaired behavior either way.

## Recommended Commit Type

`fix` — repairs to broken gate behavior with regression tests; no new
capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
