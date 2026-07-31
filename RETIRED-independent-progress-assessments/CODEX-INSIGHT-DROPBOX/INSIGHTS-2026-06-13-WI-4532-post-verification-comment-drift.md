# WI-4532 Post-Verification Comment Drift Advisory

Date: 2026-06-13
Role: Loyal Opposition (Codex, harness A)
WIs: WI-4532
Specs: PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
Bridge thread: gtkb-impl-auth-packet-liveness-coupling

## Summary

Codex found no live Loyal Opposition-actionable bridge entries. During bridge-function verification, the `gtkb-impl-auth-packet-liveness-coupling` thread advanced concurrently from an unindexed implementation report to latest `VERIFIED` at `bridge/gtkb-impl-auth-packet-liveness-coupling-006.md`.

Codex did not duplicate that verdict. I did run the implementation report's targeted verification commands independently: 78 pytest tests passed, `ruff check` passed, and `ruff format --check` passed for the two WI-4532 target files.

The implementation behavior appears correct. The residual defect is documentary/maintenance drift: the new source comment and the live backlog row still describe the withdrawn `_validate_packet` orphan-check design, while the accepted revised design uses the gate-level `work_intent_claim_block_reason` check plus TTL shrink.

## Finding 1 - Source comment names the withdrawn guard as active

Severity: P2 - misleading control-location evidence in an authorization module.

Observation:
- `scripts/implementation_authorization.py:33` says: "The orphan check in _validate_packet is the primary liveness guard".
- The accepted revised proposal says the broad `_validate_packet` orphan check was withdrawn because it broke verified WI-4443/WI-4452 contracts, and that the existing gate-level `work_intent_claim_block_reason` check is the liveness coupling (`bridge/gtkb-impl-auth-packet-liveness-coupling-003.md:95`, `:101`, `:150`).
- The implementation report repeats that `_validate_packet` is untouched and the proof is gate-level (`bridge/gtkb-impl-auth-packet-liveness-coupling-005.md:30`, `:53`).
- `rg` over `scripts/implementation_authorization.py` shows `_validate_packet` at line 1090 and the live claim guard at `work_intent_claim_block_reason` plus the `gate_decision` call site at lines 1372 and 1439.

Deficiency rationale:
The code comment maps future maintainers to the wrong control point. In an implementation-start authorization path, that is more than cosmetic: the next repair could incorrectly add the rejected `_validate_packet` coupling back, or remove the actual gate-level claim check while believing `_validate_packet` still protects orphan packets.

Recommended action:
Before committing the WI-4532 implementation, Prime should update the comment near `DEFAULT_EXPIRY_MINUTES` to say that `work_intent_claim_block_reason` at the gate is the primary liveness guard and the 120-minute TTL is the fallback ceiling. After that comment-only correction, rerun:

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

Option rationale:
Correcting the comment is lower risk than changing authorization logic. The tests already prove the accepted behavior, so the repair should preserve source behavior and fix the misleading control map.

## Finding 2 - WI-4532 backlog text still describes the superseded design

Severity: P3 - backlog disposition drift.

Observation:
`python -m groundtruth_kb.cli backlog show WI-4532 --json` still reports `resolution_status: open`, `stage: backlogged`, and a description saying the fix is: "`_validate_packet` rejects an orphaned packet whose bridge has no live current_holder", plus the TTL shrink.

Deficiency rationale:
The live bridge thread is latest `VERIFIED`, and the accepted revised scope explicitly rejected the `_validate_packet` orphan check. Leaving the row open/backlogged with the withdrawn mechanism creates duplicate-effort risk: Prime may later re-implement the rejected design or treat WI-4532 as unfinished for the wrong reason.

Recommended action:
After the implementation commit is finalized, Prime should perform governed backlog disposition for WI-4532. If resolving it, the completion evidence should cite the terminal bridge thread and the actual implemented mechanism: `DEFAULT_EXPIRY_MINUTES = 120` plus gate-level `work_intent_claim_block_reason` proof. If keeping it open, restate the remaining scope without the withdrawn `_validate_packet` design.

Option rationale:
Backlog mutation is governed and should stay with Prime/owner-approved disposition. A Loyal Opposition advisory is sufficient here because the code behavior passed verification and the defect is in authoritative work-item wording.

## Verification Performed By Codex

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
-> 78 passed in 2.46s

python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
-> All checks passed!

python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
-> 2 files already formatted
```

The concurrent Antigravity `VERIFIED` verdict says its test rows were "verified via code review / skipped execution per owner instructions"; Codex's run supplies independent executed evidence, but does not replace the terminal bridge verdict.

## Prime Builder Context

Objective: remove residual documentary drift from WI-4532 before treating the implementation as cleanly closed.

Preconditions: keep the accepted revised implementation behavior unchanged.

Evidence paths:
- `scripts/implementation_authorization.py:33`
- `bridge/gtkb-impl-auth-packet-liveness-coupling-003.md:101`
- `bridge/gtkb-impl-auth-packet-liveness-coupling-005.md:30`
- `bridge/gtkb-impl-auth-packet-liveness-coupling-006.md:85`

File touchpoints:
- `scripts/implementation_authorization.py` for the comment correction.
- MemBase `work_items` row `WI-4532` only through the governed backlog disposition path.

Implementation sequence:
1. Correct the comment near `DEFAULT_EXPIRY_MINUTES`.
2. Rerun the three targeted verification commands above.
3. Commit the WI-4532 implementation with the corrected comment.
4. Separately disposition WI-4532 in MemBase, citing the terminal bridge evidence.

Rollback notes: comment correction is a single-hunk source revert; no schema or state rollback is involved.

Open decisions: none for Codex. Backlog disposition requires the normal governed Prime path.

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
