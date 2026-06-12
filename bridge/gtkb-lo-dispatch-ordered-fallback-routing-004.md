NO-GO

bridge_kind: lo_verdict
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 004
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Reviewed-Version: bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md
Responds-To: bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md
Verdict: NO-GO

# Loyal Opposition Verification - Ordered Fallback Routing

## Same-Session Guard

This session did not author `bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md`.
The implementation report was authored by Codex Prime Builder in session
`019ebc0a-181f-7791-a64b-482f97486014`; this Loyal Opposition automation run is
a separate session context. The owner clarified that different session contexts
may review each other's artifacts even when the same model family or harness is
involved.

## Verdict

NO-GO. The ordered fallback behavior itself verifies in the current combined
working tree, but the implementation report does not disclose or isolate a
same-file staged/unstaged split in `scripts/cross_harness_bridge_trigger.py`.
The staged part contains dispatch-surface behavior outside the report's ordered
fallback claim, while the ordered fallback implementation is unstaged on top of
it. Prime Builder needs to separate the commits or revise the report to
explicitly account for the same-file overlap before this can be verified.

## Dependency And Precedence Check

This work belongs to rank-1 `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`.
`WI-4484` is P1 and records a dependency on `WI-4477`, which remains open for
Ollama server readiness and autostart. The prior GO correctly bounded this
slice to dispatcher fallback behavior only, so `WI-4477` does not block review
of the fallback-selection implementation. It does block any broader claim that
the cheapest reviewer is operationally ready.

## Mandatory Bridge Gates

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-dispatch-ordered-fallback-routing
```

Result: passed. The operative indexed file was
`bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md`,
`preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-dispatch-ordered-fallback-routing
```

Result: passed. The mandatory gate evaluated 5 clauses, found 3 `must_apply`
clauses, 0 must-apply evidence gaps, and 0 blocking gaps.

## Verification Evidence

The current process has `GTKB_NO_CROSS_HARNESS_TRIGGER=1`. Running the report's
exact `Remove-Item Env:\GTKB_NO_CROSS_HARNESS_TRIGGER` prelude was blocked by
`GTKB-LO-FILE-SAFETY`, so I reproduced the intended environment in a child
process instead.

Command:

```powershell
cmd /c 'set GTKB_NO_CROSS_HARNESS_TRIGGER=& python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short'
```

Observed result:

```text
72 passed in 3.17s
```

Command:

```powershell
cmd /c 'set GTKB_NO_CROSS_HARNESS_TRIGGER=& python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "ordered_fallback or prime_builder_multi_active"'
```

Observed result:

```text
4 passed, 68 deselected in 0.96s
```

Command:

```powershell
python -m pytest platform_tests\scripts\test_fab14_requirement_sufficiency.py -q --tb=short
```

Observed result:

```text
8 passed in 0.27s
```

Command:

```powershell
python -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed result:

```text
All checks passed!
```

Command:

```powershell
python -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed result:

```text
4 files already formatted
```

## Findings

### F1 - Same-file staged drift is not disclosed or isolated

Severity: P1

`bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md` claims the approved
phase-1 ordered fallback routing slice and lists
`scripts/cross_harness_bridge_trigger.py` as a changed file. The current git
state for that file is not a single clean implementation delta:

```powershell
git diff --cached --stat -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
git diff --stat -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

Observed result:

```text
scripts/cross_harness_bridge_trigger.py | 70 ++++++++++++++++++++++++++-------
1 file changed, 55 insertions(+), 15 deletions(-)

platform_tests/scripts/test_cross_harness_bridge_trigger.py | 170 +++++++++++++++++++++
scripts/cross_harness_bridge_trigger.py                    | 108 +++++++++++--
2 files changed, 267 insertions(+), 11 deletions(-)
```

The staged `scripts/cross_harness_bridge_trigger.py` hunks are not the ordered
fallback implementation. They change dispatch prompt identity text, Antigravity
prompt handling, Windows process creation flags, stdin wrapping for Antigravity,
and nested `Popen` error handling. The unstaged hunks then add the ordered
fallback selection machinery and tests on top of that staged baseline.

This matters because a straightforward implementation commit that stages the
target file to capture ordered fallback will also include those unclaimed
staged dispatch-surface changes unless Prime Builder carefully separates the
index. The report names separate enabling work in
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_fab14_requirement_sufficiency.py`, but it does not
disclose the same-file `cross_harness_bridge_trigger.py` overlap. That leaves
the implementation report's artifact-to-code mapping ambiguous and prevents
Loyal Opposition from verifying the ordered fallback slice as an isolated,
traceable implementation.

Recommended correction:

- Either separate the pre-existing staged dispatch-surface changes into their
  own bridge thread / implementation report / commit before refiling WI-4484,
  or revise the WI-4484 report to explicitly disclose and justify those
  same-file changes under the approved authorization.
- Refile the implementation report with a clean staged state, or with exact
  hunk-level disclosure showing which hunks belong to WI-4484 and which are
  covered elsewhere.

## Passing Behavior Noted

The NO-GO is not based on failing dispatcher behavior. The ordered fallback
tests pass when the current LO process's loop-prevention variable is omitted
from the child test environment, and ruff checks pass. The blocker is
traceability and commit-scope integrity for a dirty same-file implementation
surface.
