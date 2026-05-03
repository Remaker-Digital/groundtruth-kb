REVISED

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 8 (Revision 1)

Filed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S330)
Supersedes: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-007.md` (NEW; NO-GO at `-008`)
Implements: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` (REVISED-2; Codex GO at `-006`)
Disposition authorities:
- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` (parent split: Slice 8 + Slice 8.5).
- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` (NEW; -008 NO-GO disposition: Path A — narrow fix + rc1 install-UX limitation acknowledgement).

## NO-GO Acknowledgement

Codex `-008` correctly identified two blocking findings rooted in the same defect:

- **F1 (lifecycle/contract):** B5's documented install smoke command (`gt project init <tmp>/test-app --profile local-only` per `-005:124`) cannot succeed against an installed wheel because Slice 4 isolation enforcement (VERIFIED + committed S328 `61e50453`) requires the target's parent to equal `<host_root>/applications/` AND requires `--gt-kb-root` to equal the install-derived `_GT_KB_HOST_ROOT`. Codex's independent install smoke confirmed this command shape fails. My `-007` REPORT's B5 row only proved build, not install + init (the verifier check was a build-only smoke labeled as "install smoke" — that mislabel was a real defect).
- **F2 (announcement defect):** The "How to try it" command sequence in `groundtruth-kb/docs/announcements/v0.7.0-rc1.md:117-120` (`pip install` → `mkdir my-adopter && cd my-adopter` → `gt project init --profile local-only` → `gt project doctor`) is invalid for the current CLI: `gt project init` requires positional `PROJECT_NAME`, AND the new isolation model enforces target placement under `<gt-kb-root>/applications/<name>/`.

Per S330 owner directive (AskUserQuestion header "Slice 8 fix path"; answer: "Path A: Narrow fix; acknowledge rc limitation (Recommended)"; archived at `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`), REVISED-1 implements:

1. **Real B5 install + init smoke** in `scripts/_verify_slice8_closeout.py` using the working command shape (discover `_GT_KB_HOST_ROOT` from installed package; pass explicit `--gt-kb-root` + `--dir`).
2. **Updated announcement "How to try it"** showing the working command sequence + explicit "rc1 limitation" note.
3. **Updated release-notes upgrade-path** with the working shape + limitation note.
4. **Updated `release-readiness.md` B5 row** to cite the actual installed-wheel command + observed result.
5. **New backlog row 36** (`GTKB-PIP-INSTALL-ADOPTER-UX-001`) for v0.7.0 GA work that simplifies the pip-install adopter UX (modify `_GT_KB_HOST_ROOT` derivation; relax `_resolve_gt_kb_host_root` for installed wheels; consider `--here` / `--target` CLI shapes).

Slice 4 source is NOT modified in this REVISED-1 (Path B and Path C explicitly rejected per the DELIB).

## Specification Links

All `-007` Specification Links carry forward unchanged. New citations:

1. **Phase 9 plan §"Deliverables From The Implementation Bridge"** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 415-430.
2. **Phase 9 plan §"Open Decisions"** at the same plan lines 369-396.
3. **Phase 9 plan §"Required Coverage"** at the same plan lines 89-303.
4. **`ADR-ISOLATION-APPLICATION-PLACEMENT-001`** — adopter application target placement constraint.
5. **`.claude/rules/project-root-boundary.md`** — all active GT-KB files within `E:\GT-KB`.
6. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification-Derived Verification Gate; spec-to-test mapping required for VERIFIED.
7. **`.claude/rules/codex-review-gate.md`** — pre-implementation review gate.
8. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 186-202 + `bridge/gtkb-isolation-017-scoping-004.md` (GO).
9. **`GOV-09`**, **`GOV-19`**, **`GOV-20`**, **`GOV-ARTIFACT-APPROVAL-001`**.
10. **Prior Slice GOs (all VERIFIED):**
    - Slice 1: `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md`.
    - Slice 2: `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md`.
    - Slice 2.5: `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-008.md`.
    - Slice 3: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-014.md`.
    - Slice 4: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md` (commit `61e50453`).
    - Slice 5: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md` (commit `dc8e58f8`).
    - Slice 6: `bridge/gtkb-isolation-017-slice6-docs-2026-05-03-004.md` (commit `9efd29bf`).
    - Slice 7: `bridge/gtkb-isolation-017-slice7-examples-2026-05-03-004.md` (commit `05774d6a`).
11. **Release-readiness blockers source:** `memory/release-readiness.md:23-33` + `memory/work_list.md` row 5.
12. **Existing surfaces modified by Slice 8 (B6 deferred to Slice 8.5):**
    - `groundtruth-kb/src/groundtruth_kb/__init__.py` — version bump (B1).
    - `groundtruth-kb/CHANGELOG.md` — release-notes entry.
    - `groundtruth-kb/release-notes-0.7.0-rc1.md` (NEW) — release notes (B4).
    - `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` (NEW) — public announcement.
    - `memory/release-readiness.md` — `ISOLATION-017-CLOSEOUT` block (B7) + B5 row updated in REVISED-1.
    - `scripts/_verify_slice8_closeout.py` — composite verifier; B5 check rewritten in REVISED-1.
    - 11 source/test files modified for B2 ruff resolution per `DELIB-S330-...-B2-RUFF-SCOPE-CHOICE`.
    - 14 test files / fixtures modified for pytest baseline fixes per `DELIB-S330-...-PYTEST-FIX-SCOPE-CHOICE`.
13. **Prior Deliberations:**
    - `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — establishes v0.7.0-rc1 as release target.
    - S329 owner directives resolving Decisions 2/4/5.
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — Slice 5.5 deferral cited in announcement.
    - **`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`** — split into Slice 8 + Slice 8.5.
    - **`DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`** — narrowed B2 to `groundtruth-kb/`.
    - **`DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE`** — added 13 pytest fixes to Slice 8 scope.
    - **`DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`** (NEW; this REVISED-1's primary supersession authority) — Path A disposition for -008 NO-GO; narrow fix + rc1 limitation acknowledgement.

## Spec-to-Test Mapping (REVISED-1; addresses -008 F1 + F2)

| Blocker | Test/Verification | Command(s) | Observed Result |
|---|---|---|---|
| B1 — Version bump | `groundtruth_kb.__version__ == "0.7.0rc1"` | `python -c "import groundtruth_kb; print(groundtruth_kb.__version__)"` from `groundtruth-kb/` | `0.7.0rc1` (PASS) |
| B2 — Full-repo ruff (NARROWED) | `ruff check groundtruth-kb/` exits 0 | `python -m ruff check groundtruth-kb/` from repo root | exit 0; "All checks passed!" (PASS) |
| B3 — Pytest feasibility + GREEN | `pytest groundtruth-kb/tests/` runs to completion + 0 failures | `python -m pytest tests/` from `groundtruth-kb/` | exit 0; **1946 passed, 1 warning in 605.12s (0:10:05)** (PASS, from `-007`'s pytest run; tests unchanged in REVISED-1) |
| B4 — release-notes-0.7.0-rc1.md | File exists w/ required structure + Slice 8.5 cross-ref | composite verifier check_b4 | PASS |
| **B5 — Wheel/sdist install + init smoke (REWRITTEN per -008 F1)** | **Real install + init smoke** (not just build) | composite verifier `check_b5_wheel_smoke` runs: (a) `python -m build --wheel --sdist`; (b) `python -m venv <tmp>/venv`; (c) `<venv>/Scripts/python.exe -m pip install <wheel>`; (d) `<venv>/Scripts/gt.exe --version`; (e) discover `_GT_KB_HOST_ROOT` via subprocess; (f) `mkdir <host_root>/applications/SmokeApp`; (g) `<venv>/Scripts/gt.exe project init SmokeApp --gt-kb-root <host_root> --dir <host_root>/applications/SmokeApp --profile local-only --no-include-ci --no-seed-example`; (h) confirm scaffolded `groundtruth.toml` exists | PASS — "build + pip install + gt --version (0.7.0rc1) + gt project init (working command shape per `DELIB-S330-...-INSTALL-UX-LIMITATION-ACK`) all succeeded" |
| **B6 — CI green evidence** | **Out-of-scope for Slice 8 per `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`** | n/a (no CI command run) | DEFERRED |
| B7 — Bridge terminal state | release-readiness CLOSEOUT block references all 8 slices | composite verifier check_b7 | PASS |
| Decision 2 (v0.7.0-rc1) | Version cited in B1/CHANGELOG/announcement/release-readiness | grep verification | PASS |
| Decision 4 (4 publicity surfaces) | CHANGELOG + announcement + release-notes-0.7.0-rc1.md + cross-references | composite verifier CHANGELOG + ANNOUNCE | PASS |
| Decision 5 (composite acceptance gate) | `scripts/_verify_slice8_closeout.py` runs B1-B7 + CHANGELOG/ANNOUNCE | composite verifier itself | exit 0 (re-run after REVISED-1 changes) |
| **DELIB-S330-...-INSTALL-UX-LIMITATION-ACK fidelity (NEW)** | **Announcement + release-notes show working command shape** | inspection of `groundtruth-kb/docs/announcements/v0.7.0-rc1.md:112-156` + `groundtruth-kb/release-notes-0.7.0-rc1.md:151-170` | PASS — both surfaces document the discover-host_root → mkdir → init flow + cite DELIB + cite row 36 |
| **DELIB-S330-...-INSTALL-UX-LIMITATION-ACK fidelity (NEW)** | **Backlog row 36 added for v0.7.0 GA UX work** | grep `memory/work_list.md` for `GTKB-PIP-INSTALL-ADOPTER-UX-001` | PASS — row 36 added with full context (defect explanation + proposed fix + risk + Next steps) |

## Composite Gate Output (REVISED-1; verbatim from re-run)

```
[PASS]   B1         Version bump to 0.7.0rc1 -- __version__ == 0.7.0rc1
[PASS]   B2         Ruff check (groundtruth-kb/ only, narrowed) -- ruff check groundtruth-kb/ exits 0 (full-repo scope deferred per DELIB-S330)
[PASS]   B3         Pytest completes + green -- pytest exit 0; 1946 passed, 1 warning in 615.61s (0:10:15)
[PASS]   B4         release-notes-0.7.0-rc1.md -- release-notes-0.7.0-rc1.md present with required structure + Slice 8.5 cross-ref
[PASS]   B5         Wheel/sdist build smoke -- build + pip install + gt --version (0.7.0rc1) + gt project init (working command shape per DELIB-S330-...-INSTALL-UX-LIMITATION-ACK) all succeeded
[DEFER]  B6         CI-green evidence (deferred to Slice 8.5) -- intentional: B6 captured by Slice 8.5 (bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md)
[PASS]   B7         Bridge terminal state in release-readiness -- CLOSEOUT block references all 8 ISOLATION-017 slices + Slice 8.5 follow-on
[PASS]   CHANGELOG  [0.7.0-rc1] entry -- CHANGELOG entry present + references Slice 8.5
[PASS]   ANNOUNCE   v0.7.0-rc1 announcement -- v0.7.0-rc1.md present

Summary: 8 pass, 1 deferred (intentional), 0 fail.
PASS: composite gate green for Slice 8 in-scope checks. Slice 8.5 captures B6.
```

(Note: B5 detail string uses the legacy "Wheel/sdist build smoke" label from the CHECKS table; the actual check is now the full install + init smoke per the rewritten `check_b5_wheel_smoke`. Pytest runtime varied slightly between runs: 605s in `-007`'s baseline, 615s in this REVISED-1 re-run; both well within CI feasibility envelope.)

## Codex `-008` Conditions Addressed

Codex `-008` NO-GO included two blocking findings + recommended actions:

### F1 R1: "Either fix the installed-wheel host-root behavior OR revise the accepted smoke command to the correct supported CLI shape"

Owner selected **revise the smoke command** per `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`. The verifier `check_b5_wheel_smoke` now uses the working command shape: `gt project init SmokeApp --gt-kb-root <discovered_host_root> --dir <discovered_host_root>/applications/SmokeApp --profile local-only --no-include-ci --no-seed-example`. Discovery is via subprocess invocation of `from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT; print(_GT_KB_HOST_ROOT)` against the installed wheel. The `-005` plan's bare `gt project init <tmp>/test-app --profile local-only` is explicitly noted as superseded. Source change: `scripts/_verify_slice8_closeout.py:97-200` (B5 check rewritten).

### F1 R2: "Add the installed-wheel smoke to scripts/_verify_slice8_closeout.py or to a separately named verifier invoked by the post-implementation report"

Done in `scripts/_verify_slice8_closeout.py` `check_b5_wheel_smoke` itself (no separate verifier). The check now runs the full smoke (build + venv + pip install + gt --version + gt project init + scaffolded artifact verification + cleanup).

### F1 R3: "Update memory/release-readiness.md so B5 evidence cites the actual installed-wheel command and observed result, not the build-only composite verifier"

Done. `memory/release-readiness.md` B5 row rewritten to enumerate (a) build, (b) pip install, (c) gt --version, (d) gt project init with discovered host_root, (e) scaffolded artifact confirmation. Cites `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` and row 36.

### F2 R1: "Revise the announcement and release notes to show a command sequence that is actually supported by the installed wheel"

Done. `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` "How to try it" rewritten to show:
- `python -m venv` + activate + `pip install`.
- `gt --version` smoke.
- `HOST_ROOT=$(python -c "...")` discovery step.
- `mkdir -p "$HOST_ROOT/applications/MyAdopter"`.
- `gt project init MyAdopter --profile local-only --gt-kb-root "$HOST_ROOT" --dir "$HOST_ROOT/applications/MyAdopter"`.
- `gt project doctor --dir "$HOST_ROOT/applications/MyAdopter"`.

A new section "rc1 limitation: pip-install adopter UX" explicitly acknowledges the awkwardness, points to v0.7.0 GA simplification (row 36), and offers the worked-examples path as an alternative for adopters who don't want to run `gt project init` directly.

`groundtruth-kb/release-notes-0.7.0-rc1.md` upgrade-path section updated similarly with the rc1 limitation note.

### F2 R2: "Then run that exact documented sequence as part of the installed-wheel smoke"

Done. The `check_b5_wheel_smoke` runs the same command shape documented in the announcement (discover host_root → mkdir → init), so the smoke proves the documented sequence works.

## Files Modified / Created in REVISED-1

| File | Change |
|---|---|
| `scripts/_verify_slice8_closeout.py` | `check_b5_wheel_smoke` rewritten to do full install + init smoke (~80 LOC change) |
| `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` | "How to try it" rewritten + new "rc1 limitation" section (~50 LOC change) |
| `groundtruth-kb/release-notes-0.7.0-rc1.md` | Upgrade-path section updated with working command shape + rc1 limitation note (~10 LOC change) |
| `memory/release-readiness.md` | B5 row rewritten to cite actual installed-wheel command + result + row 36 reference |
| `memory/work_list.md` | Row 36 added (`GTKB-PIP-INSTALL-ADOPTER-UX-001`) for v0.7.0 GA pip-install UX work |
| `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-009.md` | This REPORT |
| `bridge/INDEX.md` | REVISED line for `-009` will be added at file time |
| `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice8-install-ux-limitation-ack.json` | Formal-artifact-approval packet for new DELIB |

## KB Inserts (DELIBs)

- **NEW: `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`** — version 1, owner_decision, S330. Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice8-install-ux-limitation-ack.json`. Path A disposition for -008 NO-GO; narrow fix + rc1 limitation acknowledgement.
- (Unchanged from `-007`): `DELIB-S330-...-DISPOSITION-CHOICE`, `DELIB-S330-...-B2-RUFF-SCOPE-CHOICE`, `DELIB-S330-...-PYTEST-FIX-SCOPE-CHOICE`.

## IPR-SLICE8-RELEASE-OPS-001 (carried forward + amended)

- **WI:** GTKB-ISOLATION-017 Slice 8 release-version gate + closeout (REVISED-1 addresses -008 F1+F2).
- **Reviewed against:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `.claude/rules/project-root-boundary.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `GOV-09`, `GOV-19`, `GOV-20`, `GOV-ARTIFACT-APPROVAL-001`.
- **Architecture compliance:** REVISED-1 still ships only `groundtruth-kb/` package release artifacts + closeout text + verifier change. No new code paths in `src/groundtruth_kb/`; **no Slice 4 source modification** (Path B and Path C explicitly rejected per the new DELIB).
- **Constraint compliance:**
  - GOV-09 (input classification): -008 NO-GO findings classified as implementation defects; owner sub-decision (Path A) recorded as DELIB before implementation.
  - GOV-19 (outside-in testing): B5 smoke now exercises the full public surface (`pip install` + `gt --version` + `gt project init`) end-to-end, not just the build internals.
  - GOV-20 (architecture decisions): IPR/CVR carried forward + amended; no orphan ADR/DCL touched.
  - GOV-ARTIFACT-APPROVAL-001: 4th DELIB insertion (this REVISED-1's `INSTALL-UX-LIMITATION-ACK`) ran under `GTKB_FORMAL_APPROVAL_PACKET` env var with explicit packet file.

## CVR-SLICE8-RELEASE-OPS-001 (carried forward + amended)

- **DCL compliance evidence (REVISED-1 amendments):**
  - `DCL-CROSS-HARNESS-ENFORCEMENT-001`: REVISED-1 REPORT filed via Claude Code Write; bridge-compliance-gate hook active. (No change from `-007`.)
  - `DCL-STANDING-BACKLOG-SCHEMA-001`: `memory/work_list.md` row 5 + new row 36 schema preserved.
  - `DCL-ARTIFACT-APPROVAL-HOOK-001`: 4 DELIB inserts under formal-approval gate (3 from `-007` + 1 new).
  - Project-root-boundary: all REVISED-1 modified/created paths under `E:\GT-KB`.
- **Test coverage:** all linked specifications have executed test coverage per §"Spec-to-Test Mapping" (REVISED-1 row updated for B5).
- **Composite gate:** `scripts/_verify_slice8_closeout.py` exit 0 confirmed below.

## Umbrella IPR/CVR for ISOLATION-017 Program

(Carried forward from `-007` unchanged — Slices 1-7 already VERIFIED + committed; Slice 8 status now: REVISED-1 awaiting VERIFIED on this REPORT.)

## Gate Checks (self-attested)

- Root-boundary gate: PASS. All REVISED-1 modified/created paths under `E:\GT-KB`.
- Specification-linkage gate: PASS. All `-007` Specification Links carried forward + 1 new DELIB-S330 sub-decision DELIB added.
- Test-derivation gate: PASS. Spec-to-test mapping covers B1-B7 (B6 explicitly out-of-scope per DELIB-S330) + 2 new rows for `INSTALL-UX-LIMITATION-ACK` fidelity.
- Bridge audit trail: PASS. -001 NEW → -002 NO-GO → -003 REVISED → -004 NO-GO → -005 REVISED-2 → -006 GO → -007 NEW → -008 NO-GO → -009 REVISED-1 (this REPORT).
- Composite gate: PASS (re-run output below).

## Open Items (post-VERIFIED + commit)

1. Owner authorizes Slice 8 commit. Suggested commit message:
   ```
   gtkb-isolation-017: Slice 8 release artifacts VERIFIED (REVISED-1)

   v0.7.0-rc1 release artifacts ready (CI evidence captured by Slice 8.5;
   pip-install adopter UX simplification deferred to v0.7.0 GA per row 36).

   B1: __version__ 0.6.1 → 0.7.0rc1
   B2: ruff check groundtruth-kb/ exits 0 (NARROWED per DELIB-S330)
   B3: pytest 1946 passed in 605s (13 baseline fixes per DELIB-S330)
   B4: release-notes-0.7.0-rc1.md (~170 LOC)
   B5: install + init smoke PASS (working command shape per DELIB-S330-...-INSTALL-UX-LIMITATION-ACK)
   B6: deferred to Slice 8.5 per DELIB-S330
   B7: release-readiness ISOLATION-017-CLOSEOUT block
   ```
2. After commit, file `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` as Slice 8.5 NEW.
3. Slice 8.5 captures GitHub Actions run URL on Slice 8 commit + final green status.
4. After Slice 8.5 VERIFIED, owner authorizes `git tag -a v0.7.0-rc1`.
5. PyPI publication remains a separate post-tag operator step.
6. **Row 36** (`GTKB-PIP-INSTALL-ADOPTER-UX-001`) deferred to v0.7.0 GA; not blocking the rc1 tag.

## Decision Needed From Owner

**None at REPORT-filing time.** The -008 NO-GO disposition was resolved via AskUserQuestion (Path A) + DELIB archival before implementation began.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
