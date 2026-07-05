# Loyal Opposition Report: Orphaned Kill-Switch Test (ImportError during collection)

## 1. Observation

During platform test execution, pytest fails collection with the following error:
```
platform_tests\scripts\test_doctor_kill_switch_staleness.py:24: in <module>
    from groundtruth_kb.project.doctor import (
E   ImportError: cannot import name '_KILL_SWITCH_ENV_VAR' from 'groundtruth_kb.project.doctor' (E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py)
```

Investigation reveals that:
1. `_check_kill_switch_staleness` and associated constants (such as `_KILL_SWITCH_ENV_VAR`) were added to [doctor.py](file:///e:/GT-KB/groundtruth-kb/src/groundtruth_kb/project/doctor.py) in commit `0116c93f` (`fix(doctor): warn on stale dispatch kill-switch (WI-4804)`) alongside [test_doctor_kill_switch_staleness.py](file:///e:/GT-KB/platform_tests/scripts/test_doctor_kill_switch_staleness.py).
2. Commit `d2da67de` (`fix(dispatcher): purge retired cross-harness trigger`) purged the retired cross-harness trigger family, removing the `_check_kill_switch_staleness` check and its constants from [doctor.py](file:///e:/GT-KB/groundtruth-kb/src/groundtruth_kb/project/doctor.py).
3. The test file [test_doctor_kill_switch_staleness.py](file:///e:/GT-KB/platform_tests/scripts/test_doctor_kill_switch_staleness.py) was not deleted, resulting in an orphaned test that fails to collect.

## 2. Deficiency Rationale

Orphaned test files that attempt to import deleted functions or constants break the test collection process. Since `pytest` automatically scans all files matching `test_*.py`, this import failure halts test execution or outputs errors during the collection phase, violating test suite integrity and blocking CI/CD validation gates (`GOV-RELEASE-READINESS-GOVERNED-TESTING-001`).

## 3. Proposed Solution/Enhancement

Delete the obsolete and orphaned test file:
- [platform_tests/scripts/test_doctor_kill_switch_staleness.py](file:///e:/GT-KB/platform_tests/scripts/test_doctor_kill_switch_staleness.py)

This is a clean-up task consistent with the rollback/purge plan described in the WI-4804 implementation report (`gtkb-wi4804-kill-switch-staleness-visibility-003.md`), which lists removing the test file as part of the purge process.

## 4. Option Rationale

Deleting the test file is the only correct action. The feature it tests (`_check_kill_switch_staleness` for the retired `GTKB_NO_CROSS_HARNESS_TRIGGER`) has been intentionally purged and is no longer part of GroundTruth-KB's dispatcher architecture. Re-introducing the dummy check simply to satisfy the test is rejected as it would create dead code.

---

## Prime Builder Implementation Context

### Objective and Intended Outcome
- Purge the orphaned test file to restore green `pytest` collection and run status.

### Preconditions and Constraints
- Prime Builder must execute this under an active bridge and work intent claim once authorized.

### Exact Evidence Paths and Line References
- [test_doctor_kill_switch_staleness.py](file:///e:/GT-KB/platform_tests/scripts/test_doctor_kill_switch_staleness.py#L24-L29):
  ```python
  from groundtruth_kb.project.doctor import (
      _KILL_SWITCH_ENV_VAR,
      _KILL_SWITCH_FIRST_SEEN_REL,
      _KILL_SWITCH_STALE_SECONDS,
      _check_kill_switch_staleness,
  )
  ```

### Expected File Touchpoints
- Delete: `platform_tests/scripts/test_doctor_kill_switch_staleness.py`

### Ordered Implementation Sequence
1. Git-remove/delete the file: `git rm platform_tests/scripts/test_doctor_kill_switch_staleness.py`
2. Run pytest suite to confirm collection and test runs succeed.

### Verification/Test Steps
- Run `python -m pytest platform_tests/scripts/` and confirm clean collection.

### Rollback or Containment Notes
- Revert the deletion commit if the test is ever needed, but since the feature is purged, rollback is highly unlikely.

### Open Decisions Required from Owner
- None. This is a straightforward hygiene and build-health correction.

---
Skills applied: loyal-opposition-report, structural-hygiene-review
