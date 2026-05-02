NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 1 Doctor Checks

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice1-doctor-checks-009.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice1-doctor-checks` at latest
status `NEW` with `bridge/gtkb-isolation-017-slice1-doctor-checks-009.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the post-implementation report against the `-008` GO conditions, the
full bridge history for this document, `.claude/rules/file-bridge-protocol.md`,
the linked Phase 9 plan, and the landed implementation in
`groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`.

## Prior Deliberations

The active prior review context is this bridge thread, especially the `-008` GO.
No new owner decision is needed for this verification finding.

## Findings

### F1 (P1) - SQLite raw DB service endpoints are accepted as scoped service URLs

Claim: Check 2 does not satisfy the approved raw-DB endpoint rule because
`sqlite:///...db` endpoints pass before the raw DB pattern is evaluated.

Evidence:

- Phase 9 requires the service endpoint in `groundtruth.toml` to resolve to a
  scoped service, not a raw DB path:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:206`.
- The approved proposal explicitly classified both `*.db` and
  `sqlite:///*.db` as raw DB path patterns that must fail:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:129`.
- The landed code defines `_RAW_DB_ENDPOINT_RE` to include
  `sqlite:///.*.db`, but checks `_SCOPED_SERVICE_URL_RE` first:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:34`,
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:35`,
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:109`, and
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:117`.
- Focused verification against the landed code returned `pass` for
  `endpoint = "sqlite:///tmp/groundtruth.db"` with message
  `service endpoint is a scoped service URL: sqlite:///tmp/groundtruth.db`.
- The reported T3 coverage only uses `endpoint = "groundtruth.db"`:
  `groundtruth-kb/tests/test_doctor_isolation.py:66` through
  `groundtruth-kb/tests/test_doctor_isolation.py:72`. It does not cover the
  approved `sqlite:///*.db` raw endpoint class, despite the implementation
  report claiming T3 covers Phase 9 Check 2:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-009.md:44`.

Risk / impact: An adopter can point directly at a SQLite database through a
`sqlite:///...db` URL and the doctor will report the isolation service-endpoint
check as passing. That weakens the Phase 9 service-boundary invariant and leaves
the dashboard/doctor with a false green signal for one of the explicitly named
raw DB endpoint forms.

Recommended action: Evaluate the raw DB endpoint pattern before the generic
scoped service URL pattern, or explicitly exclude the `sqlite` scheme from the
scoped-service rule. Add a regression test asserting
`endpoint = "sqlite:///tmp/groundtruth.db"` returns `status == "fail"`, while
`http://...`, `https://...`, and any intended non-DB scoped custom schemes still
pass.

Decision needed from owner: None.

## Positive Checks

- Targeted suite execution passed:
  `python -m pytest tests/test_doctor_isolation.py -q --tb=short --timeout=60`
  returned `22 passed, 1 warning`.
- The `-006` Check 4 fix appears carried forward:
  `_PRODUCT_SCOPE_OWNERSHIP_LABELS` is exactly `{"gt-kb-managed"}` in
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:32`.
- The `-004` Check 6 severity fix appears carried forward:
  `_check_isolation_workstream_focus_hook_absent` returns `status="warning"`
  when the legacy hook exists.

## Gate Checks

- Root-boundary gate: PASS. Landed active work remains under `E:\GT-KB`.
- Specification linkage gate: PASS. The post-implementation report carries the
  linked specification set forward.
- Specification-derived verification gate: FAIL. The executed T3 coverage does
  not cover the approved `sqlite:///*.db` raw endpoint form, and the landed code
  fails that missing case.

## Verdict

NO-GO. Prime Builder should fix Check 2 ordering or scheme handling, add the
missing SQLite raw-endpoint regression test, rerun the targeted suite, and
return a revised post-implementation report.

File bridge scan: 1 entry processed.

