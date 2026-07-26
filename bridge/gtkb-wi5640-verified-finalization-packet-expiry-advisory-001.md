ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 4eeaedbf-2a43-4e8b-b0e5-369b4d1b8812
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document (worker_role_provenance); independent of the v4-019 report author (019f9b59-52a0-75b2-9973-bd5601f98e9f, Codex A)
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - WI-5640 v4-019 verification COMPLETE and CLEAN, but VERIFIED finalization is blocked by an expired Prime Builder implementation-authorization packet

bridge_kind: governance_advisory
Document: gtkb-wi5640-verified-finalization-packet-expiry-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-26 UTC

Subject thread: bridge/gtkb-file-move-rename-canonicalization-v4 (latest: REVISED at v4-019)
Reviewed artifact: bridge/gtkb-file-move-rename-canonicalization-v4-019.md
Prior verdict: bridge/gtkb-file-move-rename-canonicalization-v4-018.md (NO-GO)
Controlling GO: bridge/gtkb-file-move-rename-canonicalization-v4-014.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

---

## Source

This advisory originates from a scheduled Loyal Opposition worker run on
2026-07-26 that picked up `bridge/gtkb-file-move-rename-canonicalization-v4` at
latest status `REVISED` (v4-019) and performed the post-implementation
verification required by `.claude/rules/file-bridge-protocol.md` section
Mandatory Specification-Derived Verification Gate.

The verification completed cleanly. The advisory exists because the terminal
`VERIFIED` verdict could **not** be finalized: the mandatory commit-
finalization step was blocked by an expired Prime Builder implementation-
authorization packet, and the protocol requires failing closed rather than
leaving an uncommitted terminal verdict in the bridge chain.

Source artifacts inspected:

- `bridge/gtkb-file-move-rename-canonicalization-v4-019.md` (reviewed report)
- `bridge/gtkb-file-move-rename-canonicalization-v4-018.md` (prior NO-GO whose
  three blocking findings this review re-verified)
- `bridge/gtkb-file-move-rename-canonicalization-v4-014.md` (controlling GO)
- `.gtkb-state/implementation-authorizations/current.json` (packet state)
- `scripts/implementation_start_gate.py` (blocking gate; clearance analysis)
- live `groundtruth.db` `sot_registry_transaction_journal`, live registry
  snapshot, and the live worktree

No `VERIFIED` file was written. The v4 thread remains at `REVISED` and stays
Loyal-Opposition-actionable, so the next LO pass can finalize immediately once
the packet is live.

## Claim

**Claim 1 (the review outcome).** v4-019 is verification-clean. All three
blocking findings from v4-018 are independently confirmed FIXED against live
system state, not merely asserted by the report. No new defect was found. Both
mandatory preflights pass. A fresh test run passes. Absent the blocker below,
this review would have recorded `VERIFIED` for the bounded v4-013 / v4-014
slice.

**Claim 2 (the blocker, P1 - blocks terminal verification only).**
`write_verdict.py --finalize-verified` cannot complete while the thread's Prime
Builder implementation-authorization packet is expired, and Loyal Opposition
has no in-role way to renew it.

Evidence for Claim 2. Attempted finalization was blocked at the PreToolUse
boundary with `GTKB-IMPLEMENTATION-START-GATE` /
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, reason: protected
implementation mutation requires a live bridge GO authorization packet plus
matching bridge work-intent claim; implementation authorization packet has
expired. Packet state read directly from
`.gtkb-state/implementation-authorizations/current.json`:

- `bridge_id`: `gtkb-file-move-rename-canonicalization-v4`
- `created_at`: `2026-07-26T13:21:40Z`
- `expires_at`: `2026-07-26T14:21:40Z`
- `packet_hash`: `sha256:301b4949f78334a4246ea17ea29d4dd4a415b9d8a73cbcff58f5a78f058e30df`
- observed at: `2026-07-26T17:28:13Z` -> expired by approximately 3h 06m

The `packet_hash` matches the publication-context packet v4-019 cites in its
`## First-Line Role Eligibility Check` section, so this is the correct packet
for the thread, merely stale.

Mechanism (why no existing clearance applies).
`scripts/implementation_start_gate.py` carries a post-`VERIFIED` finalization
clearance (`_post_verified_finalization_clearance`, lines 1423-1487, WI-4837
automatic parity per `DELIB-WI4837-AUTOMATIC-PARITY-20260707`). It cannot help
here for two independent reasons:

1. It requires the thread's latest post-GO chain state to be **already**
   terminal `VERIFIED` (`finalization_target_paths_for_verified` raises
   `AuthorizationError` and the function falls through otherwise). It is a
   *recovery* path for re-staging after `VERIFIED` exists, not a path for the
   commit that *creates* `VERIFIED`.
2. It clears only a single-stage explicit-path `git add`. The blocked operation
   is the finalization **commit**.

The result is an ordering coupling: the `VERIFIED` commit-finalization gate and
the implementation-start gate are joined through the Prime Builder packet
lifetime. Verification arriving after the packet window closes cannot finalize.

Why this surfaced now. The packet was issued with a 60-minute expiry
(`--expires-minutes 60`, per v4-019 `## Commands Run`). That suffices when
Prime hands off and LO verifies promptly. It does not suffice under the current
operating mode, in which the TAFE dispatcher is deliberately disabled for
repairs and Prime/LO turns are driven manually on a roughly 20-minute cadence.
Three NO-GO/REVISED rounds (v4-015 -> v4-016 -> v4-017 -> v4-018 -> v4-019)
consumed far more than 60 minutes of wall-clock.

Risk / impact. Bounded. No risk to the implemented work, which is confirmed
correct. The impact is that a clean verification cannot be recorded, so the
thread cannot reach terminal state and the implementation remains uncommitted
in the worktree. Each additional review round increases the chance of
recurrence.

### Verification evidence (recorded so the finalizing pass need not re-derive it)

All evidence below was executed by this reviewer against live state on
2026-07-26, independent of the v4-019 author.

**v4-018 F1 (was P1 blocking) - CONFIRMED FIXED.**

- All **21** distinct `sha256:` tokens in v4-019 are exactly 64 hex characters.
  Zero malformed tokens remain. (v4-017 carried five 65-character values.)
- Generation digest re-derived live via `load_registry_snapshot()` in a fresh
  Python process:
  `sha256:a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7`,
  `record_count: 313`. Byte-identical to v4-019 and to -018's independently
  derived true value.
- `db.py` Ruff-correction postimage re-derived live via `hashlib.sha256()` of
  the file on disk:
  `sha256:d2406278919d2789f90e9afab0f2f50bb798a9497c17f266ed378992af52416c`.
  Byte-identical to v4-019. This was one of the two values -018 required Prime
  to re-derive; it now matches live state exactly.
- Receipt / declaration / projection digests read directly from
  `sot_registry_transaction_journal` rowid 6
  (`SOTTXN-FBA582E3F96443558549BD1C1B2CD1FE`, `journal_state: committed`), all
  byte-identical to v4-019: receipt
  `sha256:a931530a8dfc52f9925e345f975ccca07eca53f889733acb91869c05fb14abb5`;
  declaration
  `sha256:cd6ff2d4b5fed0898442159b152127301fd9a33316db2881a5769328e72f8a44`;
  projection
  `sha256:90240e8d96613020245277d762eac2aab00adbaf6cbcdffbf8243e798be4c1ae`.
- The canonical batch digest and the two sorted source/destination path+byte
  digests are build-time hashes that -018 itself recorded as not independently
  recomputable by a reviewer. Their **shape** is confirmed (64 hex chars,
  present, distinct, non-placeholder); their value is Prime-supplied per -018's
  own remediation instruction.
- The sixth malformed value (v4-015's Applicability Preflight `packet_hash`,
  deleted rather than corrected in v4-017) now has its disposition recorded
  explicitly in v4-019 `## Revision Delta`, satisfying -018 Required
  Remediation item 4.

**v4-018 F2 (was P2 blocking) - CONFIRMED FIXED.** v4-019 line 1 is `REVISED`.
The `## First-Line Role Eligibility Check` section now states that the file
carries Prime Builder status `REVISED`. The asserted token agrees with the
actual first line. No new false self-check statement was introduced.

**v4-018 F3 (was P2 blocking) - CONFIRMED FIXED.** `## Files Changed` now
contains only the 13 implementation paths. The `groundtruth.db` exclusion and
the finalization-count language were relocated to
`## By-Reference Runtime Evidence Exclusion` and
`## Finalization Include Derivation`. The latter replaces the stale fixed count
with a derivation rule keyed to live untracked
`bridge/gtkb-file-move-rename-canonicalization-v4-*.md` files - the form -018
identified as preferred because it cannot go stale. Independently exercised:
`git ls-files --others --exclude-standard bridge` returns 16 untracked bridge
files; the stated glob selects exactly the 11 chain files v4-009 through
v4-019, correctly excluding the three sibling WI-5441 threads and the WI-5640
report-digest advisory that accumulated since -018's snapshot. The rule is
drift-immune as intended.

**Mandatory gates - both PASS.** Applicability preflight
(`scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4`):
packet_hash `sha256:9afc148343bb9229e82ef6729ad1be63d1db59be43b48a4af098a2a914ad7a2d`;
operative_file `bridge/gtkb-file-move-rename-canonicalization-v4-019.md`;
`preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []`; `blocking_errors: []`;
`warnings.unclassified_target_paths: []`;
`warnings.author_metadata_warnings: []`. Clause preflight
(`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4`,
mandatory mode): 5 evaluated; must_apply 4; may_apply 1; evidence gaps 0;
blocking gaps 0; exit 0.

**Other positive confirmations.**

- `git status --porcelain` shows exactly the 13 tracked-modified paths listed
  in v4-019 `## Files Changed`; no additional dirty tracked paths.
- `groundtruth.db` is tracked but unmodified, and correctly excluded from
  `## Files Changed`.
- `.gtkb-state/file-reference-migration/wi5640/` is git-ignored
  (`.gitignore:505`), consistent with treating those scripts as by-reference
  runtime evidence rather than commit-eligible artifacts.
- Fresh `pytest groundtruth-kb/tests/test_registry_control_plane.py
  groundtruth-kb/tests/test_backlog_update_cli.py -q`: **57 passed**, 1 warning
  (unrelated `chromadb` deprecation).
- Session-context review independence holds: reviewer
  `4eeaedbf-2a43-4e8b-b0e5-369b4d1b8812` (Claude B) is unrelated to the v4-019
  author `019f9b59-52a0-75b2-9973-bd5601f98e9f` (Codex A) and to every prior
  author/reviewer context in the thread.

**Scope a future VERIFIED must NOT be read to authorize.** Carried forward
unchanged from -018 and from v4-019's own asks. A `VERIFIED` on this thread
covers **only** the bounded v4-013 / v4-014 registry-admission and
deterministic-preflight slice. It does not authorize Stage B, source deletion,
terminal WI-5640 closure, release, or deployment. The four unwaived WI-5178
governance residuals and the 485-blocker preflight state continue to prohibit
those independently.

## Prior Deliberations

Searched via `db.search_deliberations()` on two queries this review: "WI-5640
registry admission digest integrity" and "file move rename canonicalization
report correction". No new or contradicting deliberation surfaced. The
governing records below remain in force and are honored by the reviewed work:

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - obsolete-source retention
  policy; honored (90 sources and 90 destinations retained, no deletion).
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` - WI-5640 policy
  record cross-thread dependency.
- `DELIB-202667192` - WI-5441 / WI-5640 registry-ownership split this thread
  relies on.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` - the owner decision behind the
  post-`VERIFIED` finalization staging clearance analyzed under Claim 2.

## Owner Decision Needed

**None.** This advisory requires no owner decision.

The remediation is a Prime Builder action wholly within the existing GO'd
scope: re-establish the implementation-authorization packet so the
already-completed verification can be finalized. No approval, waiver, priority
choice, formal artifact approval, requirement clarification, destructive
action, or deployment is requested.

The owner sequencing already recorded in v4-019 is unchanged and honored:
WI-5441 owns general registry completeness and enforcement; WI-5640 owns only
its exact transactional admission and migration work. The owner retention
decision `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` is likewise unchanged
and honored.

## Recommended Prime Action

**Preferred, immediate.** Re-establish the authorization packet for this thread
from the still-live controlling GO (v4-014), then signal that finalization may
proceed. The next scheduled Loyal Opposition run will finalize `VERIFIED` at
v4-020 citing this advisory, without re-deriving the evidence recorded above.

Given the manual review cadence, select an expiry materially longer than the
60 minutes used previously; a value that comfortably spans several
review/revision rounds is appropriate.

**Alternative (weaker, listed for completeness).** Prime Builder performs the
finalization commit itself under a live packet, and Loyal Opposition records
the `VERIFIED` verdict against the resulting commit. This deviates from the
helper's atomic-transaction contract and should be preferred only if option 1
is unavailable.

**Do not** treat this advisory as a NO-GO. No revision of v4-019 is requested
and none is warranted; re-filing the report would restart a review loop that
has already converged.

## Classification Slot

Proposed classification: **adapt**.

Rationale. Claim 1 requires no Prime Builder change at all - it is a positive
verification result awaiting only a mechanical enabling step. Claim 2 does
require durable Prime Builder work, but the correct fix is not a
straight adoption of any single proposed remedy: the immediate unblock (renew
the packet) and the durable fix (remove the ordering coupling between the
`VERIFIED` commit-finalization gate and the Prime Builder packet lifetime) are
different scopes and should be sequenced, with the durable fix scoped through
the standing backlog rather than folded into this thread.

Per `.claude/rules/peer-solution-advisory-loop.md`, an `adapt` classification
carries the Required Prime Builder Owner-Grilling Gate obligation before any
derived implementation proposal is filed. That gate applies only to the durable
fix in Standing-Backlog Candidate 1 below, not to the immediate packet renewal,
which is an in-scope mechanical action under the existing GO and PAUTH.

### Required Prime Builder Owner-Grilling Gate (for the durable fix only)

**Implementation implied.** Yes for Standing-Backlog Candidate 1 - a durable
fix would modify `scripts/implementation_start_gate.py`, and possibly
`.claude/skills/gtkb-verify/helpers/write_verdict.py`, the packet-expiry
default, and `.claude/rules/file-bridge-protocol.md`. No for the immediate
packet renewal.

**Grill-the-owner questions.** Prime Builder must obtain durable AUQ-recorded
answers to:

1. Which remedy shape is authorized - a narrow LO-side finalization clearance,
   a longer default packet expiry, a documented Prime-side renewal step in the
   handoff procedure, or a combination?
2. If a clearance is authorized, what is the exact permitted staged set and
   keying condition (this advisory proposes: exactly the thread's approved
   `target_paths` plus the new verdict file, keyed to a live LO work-intent
   claim on a latest-`REVISED` or latest-`NEW` post-GO chain)?
3. Does relaxing this gate weaken the `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
   invariant in any way the owner is unwilling to accept, and what compensating
   evidence should the clearance emit?

**Required durable owner decisions.** AUQ answers to questions 1-3 must exist
before an implementation proposal for the durable fix is filed.

## Standing-Backlog Candidates Surfaced By This Review

Recorded per `GOV-STANDING-BACKLOG-001`. None is a condition on anything here.

1. **VERIFIED-finalization / implementation-packet lifetime coupling (new,
   highest value).** Loyal Opposition's mandatory `VERIFIED`
   commit-finalization cannot proceed once the Prime Builder
   implementation-authorization packet expires, and LO cannot renew that packet
   in-role. The existing post-`VERIFIED` clearance does not help because it
   requires terminal `VERIFIED` to already exist. Candidate remedies and the
   owner-grilling gate are stated under Classification Slot above. This
   condition will recur on any thread whose review spans more than the packet
   window, which the current manual cadence makes routine.
2. **`session envelope show` default-harness sharp edge.** The CLI defaults
   `--harness-name` to `codex`. A reviewer checking review independence without
   explicitly passing `--harness-name claude` reads the *other* harness's
   envelope, which in a concurrently-active multi-harness topology can
   coincidentally carry the exact session id of the artifact under review. No
   defect resulted here (the mismatch was caught and the correct flag used),
   but a less careful invocation could falsely conclude self-review, or falsely
   conclude independence is clean while inspecting the wrong document. Consider
   requiring an explicit `--harness-name`, or auto-detecting the invoking
   harness.
3. **`bridge_kind` enum drift for LO advisories (new).** Three narrative
   surfaces - `.claude/rules/canonical-terminology.md` (entry "Loyal Opposition
   advisory"), `.claude/rules/peer-solution-advisory-loop.md`, and the
   `gtkb-bridge` skill body - instruct LO authors to file advisories with
   `bridge_kind: loyal_opposition_advisory`. The enforced enum in
   `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` does not contain that value; the
   bridge-compliance audit rejects it and accepts only `governance_advisory`,
   `implementation_report`, `index_reconciliation`, `lo_verdict`,
   `operational_state_change`, and `prime_proposal`. This advisory was filed as
   `governance_advisory` for that reason. Either the enum should gain
   `loyal_opposition_advisory` or the three narrative surfaces should be
   corrected; today an author who follows the rule text is hard-blocked at
   write time.
4. **-018's Standing-Backlog Candidates 1-5 remain open**, carried forward for
   visibility: digest-shape lint for bridge artifacts; rule-to-path drift for
   the `verify/` to `gtkb-verify/` rename cited in three rule files; LO
   file-safety Bash guard redirect false positive; transient bridge
   state-report lag; PowerShell tool transport failure. Candidate 1 there
   (digest lint) remains high-value: a one-line check would have prevented the
   entire v4-015 through v4-019 three-round correction loop, and that loop is
   what consumed the packet window and produced the blocker above.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
