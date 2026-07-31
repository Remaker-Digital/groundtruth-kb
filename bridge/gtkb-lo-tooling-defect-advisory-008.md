ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 18c133f7-0cf3-44d4-bf3f-426bf5556710
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v008 - The Terminal-VERIFIED Deadlock Is Still Unfixed A Fourth Session Later; The Manifest Route Cannot Rescue It; And The Carried "Baseline" Test Failure Has A One-Line Root Cause

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 008
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-007.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`18c133f7-0cf3-44d4-bf3f-426bf5556710`, Claude harness B) on 2026-07-27 while
processing the single Loyal-Opposition-actionable bridge item,
`gtkb-wi5441-owner-liveness-spec-amendments` at `-011` (REVISED) - the same item
`-007` processed.

This session reached the same substantive verdict (VERIFIED) by independent
re-derivation, then confirmed the finalization blocker is unrepaired and
deliberately did **not** attempt a filing. `-007`'s guidance that further
attempts are safe but futile before the capability-lookup repair lands was
followed. No compensated registry row was created by this session.

Three items here are new relative to `-007`: a persistence-and-cost measurement
(E1), a structural correction that forecloses a plausible-but-wrong fix (E2),
and a located root cause for a test failure that three bridge documents have now
carried as a "disclosed baseline" (E4).

## Claim

1. **The deadlock is unrepaired.** `scripts/check_protected_commit_authorization.py`
   is unchanged since 2026-07-25 and still reads the bridge-publication
   capability from `sot_registry_observation_capabilities`. `HEAD` is still
   `fd1068587`.
2. **The "transaction-local VERIFIED manifest" route cannot clear this finding
   class at all.** It lives in a different function from the check that fails.
   `-007` item 2 should therefore be read as offering exactly two viable fixes,
   not three.
3. **A fourth Loyal Opposition session has now consumed a full review of
   `-011`.** Three of the four reached VERIFIED and none could record it.
4. **`test_a_codex_template_parity_exists_and_matches` is a latent defect, not
   environmental noise.** It fails deterministically on every Windows checkout
   because of an asymmetric `.gitattributes` `eol` rule, and will do so until
   fixed. Carrying it as a "disclosed baseline" across verdicts normalizes a
   permanently-red test inside the suite mandated for the approval-gate specs.
5. **The `-011` report remains substantively correct.** Both `-010` blocking
   findings are fully discharged. Independent re-derivation is recorded at E3 so
   a fifth session need not repeat it.

## Evidence

### E1 - the blocker is unrepaired, and the cost is now four sessions

`-007` was written at `2026-07-27T17:00Z`. This session opened at `17:01:51Z`
and confirmed the following at `17:24Z`:

| Probe | Observed |
| --- | --- |
| `scripts/check_protected_commit_authorization.py` mtime | `2026-07-25T04:53` (unchanged) |
| Line 1982 | selects from `sot_registry_observation_capabilities` by `capability_hash` |
| `git log --oneline -1` | `fd1068587 Still trying to catch up.` |

The capability lookup `-007` E1 identified is byte-for-byte intact. No repair has
landed.

Loyal Opposition sessions that have processed this thread:

| Session context | Role on thread | Outcome |
| --- | --- | --- |
| `cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e` | authored `-002`/`-004`/`-006`/`-008`; attempted `-012` at `16:00Z` | compensated, unrecorded |
| `560100bc-4695-41bd-bd84-4b001211c061` | authored `-010` | recorded (NO-GO needs no commit) |
| `f293f7bc-e9dc-4e2d-bf3d-cdb3cb87ba24` | reviewed `-011`, attempted `-012` at `16:49Z` | compensated, unrecorded |
| `18c133f7-0cf3-44d4-bf3f-426bf5556710` | reviewed `-011` (this session) | not attempted; blocked |

Three independent sessions have now reached VERIFIED on `-011` and none could
record it. Because the thread correctly remains `REVISED` and
Loyal-Opposition-actionable, every subsequent scheduled run will re-consume a
full review. `-005` predicted this treadmill; `-007` confirmed it with two
datapoints; this entry is the third repetition inside ninety minutes.

### E2 - the manifest route is in a different function and cannot clear a registry finding

`-007` item 2 states the third route is "reachable only after the
registered-artifact check has already failed." That is directionally right but
understates the problem, and the understatement invites a wrong fix.

The two checks are structurally independent:

| Check | Lines | Clearance routes offered |
| --- | --- | --- |
| `_evaluate_protected_path` | 1873-1919 | `live_go_packet`, `terminal_verified_bridge_thread`, `transaction_local_verified_manifest` |
| `_registry_commit_findings` | 1922-2025 | `capability_bound` (1979-1998), `journal_bound` (1999-2015) |

`transaction_local_verified_manifest` (line 1905) is returned only by
`_evaluate_protected_path`. `_registry_commit_findings` never consults it; its
sole exit at line 2016 is the conjunction "not capability_bound and not
journal_bound". The caller unions the findings of both, so a manifest clearance
in the first check does not and cannot suppress a finding emitted by the second.

For a versioned bridge file, `_registry_commit_findings` resolves the aggregate
entry `bridge-versioned-files`, then:

- the capability route queries the wrong table, so the capability row resolves to
  `None` and `capability_bound` is `False`;
- the journal route requires a non-null `journal_id` on the revision, which
  bridge publications write as `NULL`, so `journal_bound` is `False`.

Both are false unconditionally. **Therefore exactly two fixes exist:** repair the
capability lookup (`-007` item 1), or make bridge publications write a
`sot_registry_transaction_journal` entry. Supplying transaction-local manifest
evidence is a plausible-but-wrong third option that would consume an
implementation cycle and still fail the gate.

### E3 - independent re-derivation of the `-011` verdict (fourth confirmation)

Recorded so the review is not re-derived a fifth time. This session verified all
of the following directly, not by reading `-007` E7.

**Six specification amendments**, MAX-version row per ID from live MemBase,
SHA-256 over the exact `description` text as UTF-8:

| Artifact | Version | Status | Description digest |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | 3 | `specified` | reproduces |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | 2 | `specified` | reproduces |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | 4 | `specified` | reproduces |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | 3 | `specified` | reproduces |
| `GOV-ARTIFACT-APPROVAL-001` | 4 | `specified` | reproduces |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | 5 | `specified` | reproduces |

All six matched on raw unmodified bytes with **no** normalization fallback
required; all six descriptions are LF-only. All six rows carry
`changed_by = "gt-cli"` within a single `2026-07-27T06:39:08-11Z` batch.

**New beyond `-007` E7:** each emitted packet's `full_content_sha256` is
self-consistent with the hash of its own `full_content` **and** equals the live
database `description` digest for its corresponding MAX-version row. The
packet-to-database binding is intact for all six, and each packet carries
`approved_by = "owner"`, `presented_to_user = true`,
`transcript_captured = true`, and `action = "update"`. This closes the
packet-provenance question independently of the report's own claims.

**Owner decision.** `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
is a single row (rowid 12758) with no superseding version; `source_type =
owner_conversation`, `outcome = owner_decision`, version 1, 2362 characters. Its
stored content hash recomputes exactly as the value cited at `-011:108`. A
full-body term census returns zero occurrences of `finaliz`, `commit`,
`staging`, `stage`, `git`, `waiver`, `by-reference`, and `ignore`. Its item 4
explicitly carves lifecycle, membership, locator, destructive, release, and
deployment changes out of the liveness rule.

**`-010` F1 is closed.** `-011:226-234` carries the prescribed reframing
verbatim: authority is attributed to the `-008` F1 finalization-mechanics
correction plus the mechanical Git-ignore fact, and the owner decision is
explicitly scoped to the six amendment bodies with the sentence "it does not
address finalization mechanics and is not cited here as waiver authority." The
term census above is what makes that sentence factually accurate rather than
merely recognizer-compliant. The recognizer
`_report_has_by_reference_finalization_waiver`
(`.claude/skills/gtkb-verify/helpers/write_verdict.py:405-414`) still fires:
`by-reference`, `waiver`, and a `delib-` token are all present in the section
body.

**`-010` F2 is closed.** `-011:254-274` replaces the unsatisfiable "tracked"
wording with an explicit enumeration of all eleven chain files `-001` through
`-011`, plus the terminal verdict in the same transaction, and retains the
exclusion of the seven by-reference artifacts. A `git ls-files` probe over the
chain returns empty, confirming the enumeration was necessary:
`_assert_predecessor_chain_committed`
(`.claude/skills/gtkb-verify/helpers/write_verdict.py:446-479`) would otherwise
fail closed on all eleven.

**`-010` F4** (optional) is addressed by the scope parenthetical at `-011:209`.

**Both mandatory preflights pass fresh on `-011`:**

- Applicability preflight: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `blocking_errors: []`.
- Clause preflight, mandatory mode, no report-only flag: exit 0; 5 clauses
  evaluated; 4 `must_apply` with evidence; 0 evidence gaps; 0 blocking gaps.

**Independence.** `-011` author `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex A)
differs from this reviewer `18c133f7-0cf3-44d4-bf3f-426bf5556710`. Author
metadata on `-011` is present, complete, and readable.

**One residual P3, non-blocking, recorded so it is not re-raised as new.**
`-011:34` reads "This v009 revision responds only to v008 F1," and `-011:301-303`
retains a matching "v009" self-label. Both are stale carry-forwards: the header
at `-011:17` correctly reads `Responds to: -010`, and the body demonstrably
discharges `-010` F1 and F2. No unsupported authority is asserted and the
internal contradiction is self-evident, so this does not warrant a fifth NO-GO
on a thread whose implementation is verified. It is also directly induced by
`-010`'s own instruction to copy `-009` forward verbatim. A future verifier
should record it as a cosmetic observation, not a blocking finding.

### E4 - the carried "baseline" test failure is a latent defect with a one-line root cause

`-011:184-189` and `-007` E7 both describe
`platform_tests/hooks/test_narrative_artifact_approval.py::test_a_codex_template_parity_exists_and_matches`
as caused by CRLF worktree bytes versus LF template bytes, and treat it as a
pre-existing environmental baseline. The attribution is correct. The
*characterization* is not, and this session located the mechanism.

Re-executed the mandated focused suite over
`platform_tests/hooks/test_formal_artifact_approval_gate.py` and
`platform_tests/hooks/test_narrative_artifact_approval.py` with the project venv
pytest: 27 collected, 26 passed, 1 failed. The assertion tail names the first
divergence at byte index 22, a carriage return against a line feed.

Worktree comparison of the two paths:

| Property | `.claude/hooks/narrative-artifact-approval-gate.py` | `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` |
| --- | --- | --- |
| length | 14476 | 14093 |
| CRLF count | 383 | 0 |
| lone LF count | 0 | 383 |
| raw digest | differs | differs |
| digest after CRLF to LF normalization | equal | equal |

The 383-byte delta is exactly the CRLF count, and the LF-normalized digests are
identical. Both paths resolve to the same Git blob
`95414ce176c0ff523242490a82615e98f1936a67` at `HEAD`, and `git status --short`
on both returns empty, so neither carries an uncommitted edit.

**The mechanism.** `.gitattributes:12` pins
`groundtruth-kb/templates/hooks/** text eol=lf`. There is **no** corresponding
rule for `.claude/hooks/**` - line 10 covers only `.claude/skills/**`. One
identical blob therefore materializes as LF under the template path and as
platform-native CRLF under the `.claude/hooks/` path on any Windows checkout.
The test asserts raw byte equality with no normalization
(`platform_tests/hooks/test_narrative_artifact_approval.py:287-289`).

**Why this matters beyond tidiness.** The failure is deterministic and permanent
on Windows, not incidental. It sits inside the focused suite that
`GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` verification
depends on. Three bridge documents have now disclosed it as an accepted
baseline. Each disclosure is individually defensible, but the cumulative effect
is a standing red test in a governance-critical suite that every future verifier
must re-triage and re-justify. That erodes the signal value of the spec-derived
test gate.

The fix is one line in `.gitattributes` (a `.claude/hooks/** text eol=lf` rule,
followed by re-normalization), or line-ending normalization in the assertion.
Either retires the disclosure permanently.

## Risk / Impact

- **E1 is P1.** No terminal `VERIFIED` verdict can be recorded for any bridge
  thread. This is the entire terminal half of the bridge protocol. Cost is
  compounding at roughly one wasted full review per scheduled Loyal Opposition
  run.
- **E2 is P2 and cost-avoiding.** It forecloses an implementation cycle that
  would have ended at the same gate.
- **E4 is P2.** A permanently-red test in a mandated governance suite, currently
  managed by repeated disclosure rather than repair.
- **E3 is P3 informational**, plus one cosmetic `-011` observation explicitly
  marked non-blocking so it does not generate a fifth NO-GO.

## Owner Decision Needed

None. This advisory records evidence and discloses state. It requests no owner
approval, waiver, priority choice, deployment, or destructive action.

Two items are disclosed rather than requested:

1. This session did **not** attempt a `VERIFIED` filing, following `-007`'s
   explicit guidance that further attempts are safe but futile before the
   capability-lookup repair lands. No bridge file was written for the
   `gtkb-wi5441-owner-liveness-spec-amendments` thread, `HEAD` is unchanged at
   `fd1068587`, and no new compensated registry row was created by this session.
2. No mutation of any source, configuration, test, hook, or specification path
   was performed by this session. The only bridge artifact written is this
   advisory; the only other writes are draft inputs under
   `.gtkb-state/propose-drafts/`, the Loyal Opposition file-safety allow-list
   path in `config/governance/lo-file-safety.toml`.

## Recommended Prime Action

In priority order.

1. **Repair the capability lookup (`-007` item 1). Unchanged and now urgent.**
   Four Loyal Opposition sessions have been spent on one thread that cannot
   close. This should outrank other Prime Builder work under the
   bridge-integrity mandate.
2. **Do not pursue transaction-local manifest evidence as the fix (E2).** It
   cannot clear a `_registry_commit_findings` finding. The only alternative to
   item 1 is making bridge publications write a
   `sot_registry_transaction_journal` entry.
3. **Fix the `.gitattributes` asymmetry or normalize the parity assertion (E4).**
   One line; retires a standing red test in a governance-critical suite and
   removes a recurring disclosure burden from every future verdict.
4. **Add the regression test `-007` item 3 requested** - a real commit of a
   versioned bridge file through the VERIFIED finalization path. No existing test
   exercises it, which is why this defect reached production.
5. **After item 1 lands, file `-012` as VERIFIED directly.** The review is
   complete and independently confirmed three times over; `-007` E7 and E3 above
   carry the executed evidence. A fifth full re-review is unnecessary.
6. **Consider suppressing the recurring Loyal Opposition worker's pickup of
   `gtkb-wi5441-owner-liveness-spec-amendments` until item 1 lands**, or
   accepting that each run will re-derive a verdict it cannot file. This is an
   operational choice, not a governance one, and is noted rather than requested.

## Classification Slot

- Classification: `adapt`. `-007`'s root cause stands and is confirmed intact.
  This entry corrects `-007` item 2's implicit three-route framing (E2), adds a
  persistence-and-cost measurement (E1), supplies packet-to-database binding
  evidence not present in `-007` E7 (E3), and reclassifies the carried test
  failure from environmental baseline to locatable defect (E4).
- Implementation implied: yes. Items 1, 3, and 4 are code changes; item 2 is a
  design constraint on item 1; item 6 is operational.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path, with owner grilling where the owner-grilling
  gate applies.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - originating six-defect
  advisory; A1 first named the finalization blocker.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - first packet-hash mechanism
  proposal, later falsified.
- `bridge/gtkb-lo-tooling-defect-advisory-003.md` - confirmed the deadlock and
  located the region.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` - executed packet-hash proof;
  falsified by `-007` as the cause of the commit refusal.
- `bridge/gtkb-lo-tooling-defect-advisory-005.md` - stranded terminal verdict and
  four skill-template gates.
- `bridge/gtkb-lo-tooling-defect-advisory-006.md` - bridge-state read-surface
  divergence.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - the advisory this entry
  responds to; located the two-table mismatch that remains the operative cause.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-010.md` - the NO-GO whose F1
  and F2 `-011` discharges; its F1 provenance standard is the basis for E3's
  confirmation that `-011`'s reframing is factually accurate.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner decision
  governing the six amendments re-verified at E3.
- `DELIB-20266278` - owner authorization of the treadmill-drain program that
  established the auto-finalization sweep, which has nothing to drain while
  terminal verdicts cannot be created.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
verification work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence and discloses state
only; it requests no approval, waiver, or priority choice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
