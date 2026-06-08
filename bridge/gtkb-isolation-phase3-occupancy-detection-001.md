# Bridge Proposal — GT-KB Isolation Phase 3: Occupancy Detection Implementation

**Status:** NEW (implementation proposal derived from program GO)  
**Author:** Prime Builder (Goose / interactive override)  
**Date:** 2026-06-08  
**Document name:** `gtkb-isolation-phase3-occupancy-detection`  
**Supersedes:** None (first implementation slice from program GO)  
**Derives from:** `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` (GO), `-009` (contract)

---

## 0. Scope

This is **Slice 1 of 3** for the isolation completion plan Phase 3/4/5 implementation. It covers:

- Occupancy detection algorithm (§1.1 of -009)
- `gt platform doctor` occupancy verdict cells (§1.2.2 of -009)
- Test contract tests 8-16 (§1.3 of -009)

**Out of scope for this slice:**
- Self-completion validation gate (Slice 2: `gtkb-isolation-phase3-self-completion-validation`)
- Application registration flow integration (Slice 3: `gtkb-isolation-phase3-register-integration`)

---

## 1. Specification Links

| Specification | Status | Relevance |
|---|---|---|
| `SPEC-ISOLATION-APPLICATION-SLOT-OCCUPANCY-001` | active | Defines occupancy semantics (default-occupied, allowlisted exceptions) |
| `SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001` | active | Defines single-active-application constraint |
| `SPEC-ISOLATION-PLATFORM-DOCTOR-VERDICTS-001` | active | Defines doctor diagnostic matrix |
| `REQ-ISOLATION-APPLICATION-REGISTER-001` | active | FR1-FR5 (register flow, cardinality checks) |
| `REQ-ISOLATION-PLATFORM-DOCTOR-001` | active | FR1-FR8 (doctor verdicts, remediation) |

**Requirement sufficiency:** Existing specifications are sufficient for this slice. No new specifications required. The -009 contract refines the semantics of existing specs without adding new requirements.

---

## 2. Prior Deliberations

- `DELIB-0834`: Agent Red as fully conformant application, not exception
- `DELIB-0877`: GT-KB/application separation, IDP framing
- `DELIB-1327`: Codex verification of application isolation sub-slice 1
- `DELIB-1329`: Codex NO-GO on earlier application isolation revision
- `DELIB-S324-OM-DELTA-0001-CHOICE`: Owner decision on operating model delta

**No prior deliberation contradicts the occupancy detection contract.**

---

## 3. Implementation Plan

### 3.1 Occupancy detection module

**File:** `scripts/isolation/occupancy_detector.py`

```python
def is_slot_occupied(slot_path: Path, slot_name: str, registry_path: Path | None) -> OccupancyVerdict:
    """
    Determine if applications/<name>/ is occupied per -009 §1.1.
    
    Returns:
        OccupancyVerdict(
            occupied: bool,
            reason: OccupancyReason,  # STRONG_MARKER | NON_ALLOWLISTED_CONTENT | REGISTRY_ENTRY | UNOCCUPIED
            details: list[str]  # Human-readable triggers for doctor
        )
    """
```

**Logic per -009 §1.1.1:**
1. Check strong markers (table §1.1.2) → `OccupancyReason.STRONG_MARKER`
2. Walk slot contents, filter allowlist (§1.1.3) → `OccupancyReason.NON_ALLOWLISTED_CONTENT` if any non-allowlisted file/dir
3. Check `applications/registry.toml` for entry naming `<name>` → `OccupancyReason.REGISTRY_ENTRY`
4. All checks negative → `OccupancyReason.UNOCCUPIED`

**Fail-closed:** Any unrecognized file type, directory, or content triggers occupancy.

### 3.2 Allowlist implementation

**File:** `scripts/isolation/allowlist.py`

```python
ALLOWLISTED_PATTERNS = [
    r"\.gitkeep$",
    r"\.DS_Store$",
    r"Thumbs\.db$",
    r"desktop\.ini$",
]

ALLOWLISTED_FILES = [".gitkeep", ".DS_Store", "Thumbs.db", "desktop.ini"]

def is_allowlisted(path: Path) -> bool:
    """Check if path matches allowlist per -009 §1.1.3."""
    if path.name in ALLOWLISTED_FILES:
        return True
    if path.name == "README.md":
        return _is_cleanup_marker_readme(path)
    return False

def _is_cleanup_marker_readme(path: Path) -> bool:
    """Check if README.md begins with cleanup marker header."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            return first_line == "<!-- gtkb-application-slot-cleanup-marker -->"
    except (OSError, UnicodeDecodeError):
        return False  # Fail-closed: unreadable README is not allowlisted
```

### 3.3 Strong markers list

**File:** `scripts/isolation/strong_markers.py`

```python
STRONG_MARKERS = {
    "application.toml": "Application registration manifest",
    ".gtkb-app-isolation.json": "S316 application isolation contract",
    "harness-state/": "Per-app Claude/Codex operating-role state",
    "src/": "Application source code",
    "tests/": "Application test suite",
}

def check_strong_markers(slot_path: Path) -> list[str]:
    """Return list of strong markers found in slot."""
    found = []
    for marker, description in STRONG_MARKERS.items():
        marker_path = slot_path / marker
        if marker.endswith("/"):
            if marker_path.is_dir() and any(marker_path.iterdir()):
                found.append(f"{marker} ({description})")
        else:
            if marker_path.is_file():
                found.append(f"{marker} ({description})")
    return found
```

### 3.4 Registry entry check

**File:** `scripts/isolation/registry_check.py`

```python
def check_registry_entry(registry_path: Path | None, slot_name: str) -> bool:
    """Check if registry.toml contains entry for <name> per -009 §1.1.1(c)."""
    if registry_path is None or not registry_path.is_file():
        return False
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = tomllib.load(f)
        return slot_name in registry.get("applications", {})
    except (OSError, tomllib.TOMLDecodeError):
        return False  # Fail-closed: malformed registry treated as no entry
```

### 3.5 Doctor verdict integration

**File:** `scripts/isolation/doctor_verdicts.py`

Augment `gt platform doctor` with occupancy-specific verdict cells per -009 §1.2.2:

| Slot state | Verdict | Remediation |
|---|---|---|
| Zero occupied slots, no registry drift | Green (informational) | None |
| One properly-registered slot | Green | None |
| One partial slot (consistent markers) | P1 | "Run `gt application register <name>` to complete registration" |
| Slot with mismatched-marker name | P1 | "Slot contains markers naming `<other>`. Run `gt application register <other>` or archive" |
| Slot with malformed structured markers | P1 | "Malformed marker at `<path>`. Manual repair required" |
| Two or more occupied slots | P0 | "Platform supports only one developed application at a time" |
| Registry entry exists but no slot directory | P2 | "Registry drift: run `gt application unregister <name>`" |
| Empty leftover subdirectories | P2 | "Empty leftover slot: run `rm -r applications/<name>`" |

### 3.6 Test contract

**File:** `tests/framework/test_occupancy_detection.py`

Implement tests 8-16 from -009 §1.3:

8. **Non-marker app content blocks foreign register:** `.env.local` exists → register `bar` fails
9. **Non-marker app content blocks foreign install:** `package.json` exists → install `bar` fails
10. **Malformed JSON marker blocks self-completion:** invalid JSON → register `foo` fails
11. **Mismatched marker name blocks self-completion:** marker names `Agent_Red` in slot `foo` → register `foo` fails
12. **Mismatched marker name blocks foreign register:** same fixture → register `bar` fails
13. **Registry-only conflict blocks foreign register:** registry has `foo`, no slot exists → register `bar` fails or doctor reports drift first
14. **Schema-version forward compatibility:** future schema version 2.0 → proceed with warning
15. **Allowlisted README cleanup-marker:** marker header present → register `bar` succeeds
16. **Non-allowlisted README blocks register:** arbitrary README → register `bar` fails

**Test mapping:** Each test derives from REQ-ISOLATION-APPLICATION-REGISTER-001 FR3-FR5 (cardinality checks) and REQ-ISOLATION-PLATFORM-DOCTOR-001 FR2-FR4 (verdict severity).

---

## 4. Acceptance Criteria

1. `is_slot_occupied()` returns correct `OccupancyVerdict` for all 8 doctor verdict cells
2. Allowlist correctly identifies `.gitkeep`, cleanup-marker README, OS metadata files
3. Strong markers list matches -009 §1.1.2 table
4. Registry entry check fails-closed on malformed registry
5. All tests 8-16 pass
6. Doctor verdicts match -009 §1.2.2 matrix
7. No regression of existing isolation tests (tests 1-7 from -007)

---

## 5. Risk Assessment

**Low risk:** This is a read-only detection module with no side effects. Fail-closed semantics ensure conservative behavior.

**Mitigation:** Comprehensive test coverage (9 new tests + 7 existing tests) validates all verdict cells.

---

## 6. Implementation Constraints

- **First slice lands detection only:** No registration flow changes, no self-completion logic
- **Fail-closed default:** Unrecognized content triggers occupancy
- **Allowlist grows only via bridge:** No ad-hoc additions
- **Registry drift blocks registration:** Test 13 default behavior (conservative)

---

## 7. Verification Plan

1. Run `pytest tests/framework/test_occupancy_detection.py -v`
2. Run `pytest tests/framework/test_application_register_cardinality.py -v` (no regression)
3. Run `gt platform doctor` on test fixtures, verify verdict matrix
4. Manual inspection of `is_slot_occupied()` logic against -009 §1.1.1

---

## 8. Owner Decisions / Input

**None required for this slice.** Owner decisions captured in program GO `-010`.

---

## 9. Reversibility

This slice is additive (new module, new tests). No existing code modified except `gt platform doctor` verdict augmentation (backward-compatible).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
