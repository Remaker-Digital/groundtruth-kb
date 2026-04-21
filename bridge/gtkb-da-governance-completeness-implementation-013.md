# Implementation Bridge: DA Governance Completeness (REVISED-6, focused delta vs -011)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-18
**Target repo:** `groundtruth-kb`

**Revision basis:** addresses the single remaining blocker in Codex NO-GO
`bridge/gtkb-da-governance-completeness-implementation-012.md`:

- **High (only remaining blocker from `-012`)** — the `-011` upgrade-apply
  contract for `register-hook` appends missing registrations to the end
  of each event list, but the `-009` §5.11 registry-placement table
  (unchanged, still authoritative) requires `turn-marker.py` **before**
  `delib-search-gate.py`, `gov09-capture.py` **between** `delib-search-gate.py`
  and `intake-classifier.py`, and `owner-decision-capture.py` **before**
  `delib-search-tracker.py`. Append-only apply produces the wrong order on
  existing adopter projects whose scaffold-generated settings.json already
  contains `delib-search-gate.py`, `intake-classifier.py`, and
  `delib-search-tracker.py`. **Resolved in §B (rewritten) below.**

**Supersedes `-011`.** Preserves every piece of content accepted by `-008`,
`-010` non-blocking notes, and `-012` non-blocking notes:

- Phase 0 DELIB-0819 sequencing (`-009` §3) — unchanged.
- Transcript queue as pre-insert dry-run artifact (`-009` §5.6) — unchanged.
- Canonical `owner_conversation` source_ref grammar (`-009` §5.5.1) — unchanged.
- A3 HYBRID branch + A5 CI-result deterministic file (`-009` §5.9) — unchanged.
- Bypass DELIB stored without a `metadata` column; discriminators carried by
  `change_reason` + `title` + structured payload in `content` (`-009` §5.5.1)
  — unchanged.
- **Bypass `content` raw-JSON contract** (pinned in `-011` §5.5.1 / §C, accepted
  non-blocking in `-012`) — unchanged.
- 5 file records + 4 settings-hook-registration records (`-009` §5.11);
  registry placement table — unchanged.
- **§A lifecycle profile triples** for the 4 new `settings-hook-registration`
  records (pinned in `-011` §A, accepted non-blocking in `-012`) — unchanged.
- **Generalized doctor contract** (`-011` §B.3/§B.4, accepted non-blocking in
  `-012` with `_check_scanner_safe_writer_drift` wrapper retention for one
  release) — unchanged.
- 8 specs in MemBase (`-009` §5.1), test inventory shape (`-009` §6), post-impl
  report contract (`-009` §7, extended in `-011` §7 and further extended below),
  rollback (`-009` §8).

This bridge rewrites only:

- §B.1 — upgrade plan + apply contract (**append-only → structured merge**).
- §B.2 — upgrade test table (**replaces 9 append tests + 1 back-compat with
  11 structured-merge tests + 1 back-compat** covering the realistic
  existing-adopter fixtures Codex `-012` enumerated).
- §6 — test counts updated to reflect the §B.2 delta (net +3 vs `-011`).
- §7 item 9 — post-impl evidence upgraded to use a realistic existing-adopter
  fixture rather than empty/missing event-list fixtures.

All other §-numbered content from `-011` is preserved verbatim. §A (lifecycle
profiles) and §B.3/§B.4 (doctor) carry over without modification.

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this
implementation bridge. Per `.claude/rules/codex-review-gate.md`, no GT-KB
source, doc, hook, template, script, DB, or managed-artifact mutation may
begin until Codex GOs this `-013`.

---

## 1. Summary of Revisions vs `-011`

| Origin | Finding | Where discharged in `-013` |
|--------|---------|----------------------------|
| `-012` only finding (High) — append-only apply violates `-009` §5.11 registry placement for UserPromptSubmit / PostToolUse | Apply must produce registry-ordered managed block on retrofit against realistic existing adopters | §B.1 — `_execute_register_hook` replaced by `_execute_merge_event_hooks` (structured merge per event); `_plan_settings_registration` emits one `merge-event-hooks` action per event when the event's existing managed subsequence does not match registry order (including any missing upgrade-enforced record); apply rebuilds the event's list as **[scaffold-superset managed entries in registry order] ++ [unmanaged entries in original relative order]**; mirrors `scaffold._write_settings_json()` for the managed block |
| `-012` required action #2 — specify unmanaged-entry placement rule | Explicit v1 rule for adopter-owned hook entries | §B.1 — **conservative v1 rule**: unmanaged entries are preserved and land **after** the managed block for that event, retaining their original relative order. Documented as explicit contract with rationale, edge cases, and follow-up pointer for v2 "insert-around-neighbors" behavior if adopters request it. |
| `-012` required action #3 — add realistic existing-adopter apply tests | Test table `-011` §B.2 used empty/missing-key fixtures; Codex required a fixture matching current scaffold reality | §B.2 — 11 new merge tests + 1 back-compat (was 9 append + 1 back-compat in `-011`); new cases include the three realistic fixtures Codex enumerated verbatim (existing UserPromptSubmit `[delib-search-gate, intake-classifier]`, existing PostToolUse `[delib-search-tracker]`, existing PreToolUse 6-entry tail), plus unmanaged-preservation and idempotence-through-merge |
| `-012` required action #4 — preserve all prior accepted content | Phase 0 sequencing, transcript queue, source_ref grammar, no-metadata audit contract, raw JSON bypass content, A3/A4/A5, lifecycle profile (§A), generalized doctor (§B.3/§B.4) | Preserved verbatim. See §1 bullet list above; diff lives only in §B.1 and §B.2. |
| `-012` non-blocking — bypass `content` raw JSON resolved | accepted | unchanged |
| `-012` non-blocking — lifecycle profile triples concrete | accepted | unchanged |
| `-012` non-blocking — generalized doctor contract concrete | accepted | unchanged |
| `-012` non-blocking — `_check_scanner_safe_writer_drift` wrapper retention for one release | accepted | unchanged |

All previously accepted content is retained verbatim unless noted.

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

*(Unchanged from `-009` §2 — all 7 conditions still discharged in the same
locations. §A and §B.1 together still strengthen condition #4 with an
executable contract; `-013` hardens §B.1 with registry-order-preserving
merge semantics.)*

---

## 3. Phase 0 — Owner Decision Gate (satisfied)

*(Unchanged from `-009` §3.)* DELIB-0819 already in place.

---

## 4. Hard Sequencing Gates

*(Unchanged from `-009` §4.)*

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording

*(Unchanged from `-009` §5.1.)*

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan

*(Unchanged from `-009` §5.2.)*

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

*(Unchanged from `-009` §5.3.)*

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill

*(Unchanged from `-009` §5.4.)*

### 5.5 Phase 5 — Preflight hook infrastructure (Q3 = env var + content marker)

#### 5.5.1 Q3 contract — bypass DELIB storage

*(Unchanged from `-011` §5.5.1, which pinned `content` as raw JSON with the
six-key document shape.)*

#### 5.5.2 `delib-preflight-gate.py` logic

*(Unchanged from `-009` §5.5.2.)*

#### 5.5.3 Tests (`tests/test_delib_preflight_gate.py`) — 23 total

*(Unchanged from `-011` §5.5.3.)*

### 5.6 Phase 6 — Transcript extractor (Q1 = HYBRID)

*(Unchanged from `-009` §5.6.)*

### 5.7 Phase 7 — Owner-decision capture hook + GOV-09 capture

*(Unchanged from `-009` §5.7.)*

### 5.8 Phase 8 — Backfill framework generalization

*(Unchanged from `-009` §5.8.)*

### 5.9 Phase 9 — Session wrap gate

*(Unchanged from `-009` §5.9 including A2 `change_reason` query shape.)*

### 5.10 Phase 10 — Dogfooding

*(Unchanged from `-009` §5.10.)*

### 5.11 Consolidated final hook / scaffold / managed-artifact surface

The **scaffold path**, **two-class registration requirement** (`hook` +
`settings-hook-registration`), the **5 file records** (with their profile
triples already concrete in `-009`), and the **registry placement** of the 4
new `settings-hook-registration` records relative to existing rows are all
unchanged from `-009` §5.11. The authoritative target rendered
`.claude/settings.json` hook ordering from `-009` §5.11 remains the
contract.

#### §A — Lifecycle profile values for the 4 new `settings-hook-registration` records

*(Unchanged from `-011` §A.)* All 4 new records carry
`initial_profiles = managed_profiles = doctor_required_profiles =
["dual-agent", "dual-agent-webapp"]`, with `target_settings_path =
".claude/settings.json"`, `ownership = "gt-kb-managed"`, `upgrade_policy =
"structured-merge"`, `adopter_divergence_policy = "warn"`. They are the
first `settings-hook-registration` rows that opt in to both upgrade
enforcement and doctor enforcement.

#### §B — Event-aware upgrade plan + apply + doctor contract (REWRITTEN for `-013`)

##### §B.1 Plan/apply contract — code-level changes (REWRITTEN)

This sub-section **replaces** `-011` §B.1 in its entirety. §B.3 (doctor
generalization) and §B.4 (doctor tests) from `-011` are preserved verbatim
and carried through unchanged.

**Conceptual model (single paragraph).** Upgrade apply for settings-hook
registrations is a *structured merge* per event, not an append. For each
event E that has any upgrade-enforced `settings-hook-registration` record,
the final `hooks[E]` list is rebuilt as two concatenated segments:
(1) the **managed block** — every scaffold-superset record for event E in
registry order, each rendered as `{"hooks": [{"type": "command", "command":
"python .claude/hooks/<filename>"}]}`, reusing the existing entry by
identity when the command marker is already present on disk; (2) the
**unmanaged block** — every pre-existing entry whose command does not match
any scaffold-superset managed filename for event E, preserved in original
relative order. This mirrors the byte-level output of
`scaffold._write_settings_json()` for the managed block (see
`scaffold.py:379-406` for the scaffold implementation that upgrade apply
must match).

**File: `src/groundtruth_kb/project/upgrade.py`**

**Type change.** Extend `UpgradeAction` with an optional `event` field
defaulting to `"PreToolUse"` for back-compat. Back-compat matters because
existing callers of `UpgradeAction(action="register-hook", …)` were a
transient intermediate state that `-011` introduced; the `-013` action
type `merge-event-hooks` replaces `register-hook` entirely, but the back-
compat default on `event` is still cheap insurance for any external harness
or test that constructs an `UpgradeAction` without explicitly naming the
field.

```python
@dataclass
class UpgradeAction:
    file: str
    action: Literal["update", "add", "skip", "merge-event-hooks", "append-gitignore"]
    reason: str
    payload: str | None = None
    event: str = "PreToolUse"
```

Note on the `Literal` extension: the existing `Literal["update", "add",
"skip"]` in `upgrade.py:22` already had to gain `"register-hook"` and
`"append-gitignore"` for `-011`; for `-013` the new member is
`"merge-event-hooks"` (and `"register-hook"` is **not** introduced, since
its semantics were the defect).

**Function replacement — `_plan_settings_registration`** (currently
`upgrade.py:191-270`). Replace the `PreToolUse`-only implementation with:

```python
def _plan_settings_registration(target: Path, profile_name: str) -> list[UpgradeAction]:
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return []

    try:
        data: object = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            UpgradeAction(
                file=".claude/settings.json",
                action="skip",
                reason="Malformed JSON — manual repair required",
            )
        ]
    except OSError:
        return []

    if not isinstance(data, dict):
        hooks_dict: dict[str, object] = {}
    else:
        raw_hooks = data.get("hooks", {})
        hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}

    # Partition registrations by event in registry order. Superset = scaffold-
    # managed (initial_profiles); subset = upgrade-enforced (managed_profiles).
    from groundtruth_kb.project.managed_registry import artifacts_for_scaffold

    scaffold_by_event: dict[str, list[SettingsHookRegistration]] = {}
    for artifact in artifacts_for_scaffold(profile_name, class_="settings-hook-registration"):
        if isinstance(artifact, SettingsHookRegistration):
            scaffold_by_event.setdefault(artifact.event, []).append(artifact)

    upgrade_enforced_by_event: dict[str, list[SettingsHookRegistration]] = {}
    for registration in _managed_settings_registrations(profile_name):
        upgrade_enforced_by_event.setdefault(registration.event, []).append(registration)

    actions: list[UpgradeAction] = []
    for event, upgrade_enforced_list in upgrade_enforced_by_event.items():
        raw_event_entries = hooks_dict.get(event)
        event_entries: list[object] = (
            raw_event_entries if isinstance(raw_event_entries, list) else []
        )

        scaffold_filenames: list[str] = [r.hook_filename for r in scaffold_by_event.get(event, [])]
        scaffold_marker_set: set[str] = {
            f"python .claude/hooks/{fn}" for fn in scaffold_filenames
        }

        # Existing managed subsequence (entries whose command marker matches
        # any scaffold-superset filename for this event), preserved in the
        # order they appear on disk.
        existing_managed_markers: list[str] = []
        for entry in event_entries:
            for cmd in _entry_commands(entry):
                for marker in scaffold_marker_set:
                    if marker in cmd:
                        existing_managed_markers.append(marker)
                        break

        # Target managed order = scaffold-superset registry order.
        target_managed_markers: list[str] = [
            f"python .claude/hooks/{fn}" for fn in scaffold_filenames
        ]

        # Trigger: a merge is required iff any upgrade-enforced record's
        # marker is absent from the existing managed subsequence, OR the
        # existing managed subsequence does not equal the target order
        # (which includes the case where scaffold-only records moved) AND
        # at least one upgrade-enforced record is implicated in the mismatch.
        upgrade_enforced_markers: set[str] = {
            f"python .claude/hooks/{r.hook_filename}" for r in upgrade_enforced_list
        }
        missing_upgrade_enforced: set[str] = upgrade_enforced_markers - set(existing_managed_markers)
        order_mismatch: bool = existing_managed_markers != target_managed_markers

        implicated: bool = bool(missing_upgrade_enforced)
        if not implicated and order_mismatch:
            # Check whether any upgrade-enforced marker is out-of-position
            # relative to its registry-order neighbors among the existing
            # managed subsequence.
            for m in upgrade_enforced_markers & set(existing_managed_markers):
                target_idx = target_managed_markers.index(m)
                existing_idx = existing_managed_markers.index(m)
                if target_idx != existing_idx:
                    implicated = True
                    break

        if missing_upgrade_enforced or (order_mismatch and implicated):
            actions.append(
                UpgradeAction(
                    file=".claude/settings.json",
                    action="merge-event-hooks",
                    reason=f"Merge {event} hooks to registry order",
                    payload=event,
                    event=event,
                )
            )

    return actions


def _entry_commands(entry: object) -> list[str]:
    """Extract every `command` string reachable from a hooks event entry."""
    if not isinstance(entry, dict):
        return []
    entry_hooks = entry.get("hooks", [])
    if not isinstance(entry_hooks, list):
        return []
    out: list[str] = []
    for h in entry_hooks:
        if isinstance(h, dict):
            cmd = h.get("command", "")
            if isinstance(cmd, str):
                out.append(cmd)
    return out
```

**Function replacement — `_execute_register_hook` → `_execute_merge_event_hooks`**
(currently `upgrade.py:403-455`). Delete `_execute_register_hook` and add:

```python
def _execute_merge_event_hooks(target: Path, action: UpgradeAction) -> str:
    """Rebuild ``hooks[action.event]`` as registry-ordered managed block ++
    original-order unmanaged block. Idempotent; returns a SKIPPED status
    when the resulting list is byte-equal to the existing list."""
    from groundtruth_kb.project.managed_registry import artifacts_for_scaffold
    from groundtruth_kb.project.manifest import read_manifest

    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return f"SKIPPED {action.file} — settings.json not found"

    try:
        data: object = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return f"SKIPPED {action.file} — malformed JSON"
    except OSError as exc:
        return f"SKIPPED {action.file} — unreadable ({exc})"

    if not isinstance(data, dict):
        return f"SKIPPED {action.file} — settings root is not a JSON object"

    raw_hooks = data.get("hooks")
    if not isinstance(raw_hooks, dict):
        data["hooks"] = {}
    hooks_dict = data["hooks"]

    event = action.event
    manifest = read_manifest(target / "groundtruth.toml")
    profile_name = manifest.profile if manifest else "dual-agent"

    scaffold_registrations: list[SettingsHookRegistration] = [
        a for a in artifacts_for_scaffold(profile_name, class_="settings-hook-registration")
        if isinstance(a, SettingsHookRegistration) and a.event == event
    ]
    scaffold_filenames: list[str] = [r.hook_filename for r in scaffold_registrations]
    scaffold_markers: set[str] = {f"python .claude/hooks/{fn}" for fn in scaffold_filenames}

    raw_existing = hooks_dict.get(event)
    existing_entries: list[object] = raw_existing if isinstance(raw_existing, list) else []

    # Partition existing entries: reusable managed entries (by first-marker-
    # match) keyed by marker; unmanaged entries preserved in original order.
    managed_existing_by_marker: dict[str, object] = {}
    unmanaged: list[object] = []
    for entry in existing_entries:
        matched_marker: str | None = None
        for cmd in _entry_commands(entry):
            for marker in scaffold_markers:
                if marker in cmd:
                    matched_marker = marker
                    break
            if matched_marker is not None:
                break
        if matched_marker is None:
            unmanaged.append(entry)
        else:
            # First occurrence wins if the adopter duplicated a managed entry;
            # duplicates collapse to the registry-order canonical position.
            managed_existing_by_marker.setdefault(matched_marker, entry)

    # Rebuild managed block in registry order, reusing existing entries when
    # present and synthesizing new entries otherwise.
    new_managed_block: list[dict[str, object]] = []
    for filename in scaffold_filenames:
        marker = f"python .claude/hooks/{filename}"
        reused = managed_existing_by_marker.get(marker)
        if isinstance(reused, dict):
            new_managed_block.append(reused)
        else:
            new_managed_block.append(
                {"hooks": [{"type": "command", "command": marker}]}
            )

    new_event_list: list[object] = [*new_managed_block, *unmanaged]

    if new_event_list == existing_entries:
        return f"SKIPPED {action.file} — {event} already at registry order"

    hooks_dict[event] = new_event_list
    data["hooks"] = hooks_dict
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"MERGED {action.file} — {event} rebuilt ({len(new_managed_block)} managed, {len(unmanaged)} preserved)"
```

**Dispatch table update** in `execute_upgrade` (currently `upgrade.py:357-365`):
replace the `register-hook` branch with:

```python
if action.action == "merge-event-hooks":
    results.append(_execute_merge_event_hooks(target, action))
    continue
```

**Unmanaged-preservation rule (conservative v1 — explicit contract).**

1. An existing entry in `hooks[event]` is classified as *managed* iff any of
   its `command` strings contains `python .claude/hooks/<filename>` for some
   scaffold-superset `settings-hook-registration` record whose event matches
   the target event and whose `initial_profiles` includes the active
   manifest profile.
2. All other entries are *unmanaged*. These include adopter-authored hooks,
   entries that reference hooks that were once managed but have since been
   removed from the registry, and any malformed / non-dict entries
   (malformed entries are preserved verbatim; the merge does not attempt to
   repair non-dict entries).
3. After merge, unmanaged entries are placed **after** the managed block in
   their original relative order. The managed block is registry-ordered.
4. Rationale for "managed-first, unmanaged-after": (a) deterministic and
   idempotent — a second merge over the same file returns SKIPPED; (b)
   matches scaffold output byte-for-byte for the managed portion, satisfying
   the registry-parity contract; (c) never loses adopter data; (d) does not
   require the algorithm to know about "neighbor" relationships between
   managed and unmanaged entries. Alternative v2 rules ("insert-around-
   neighbors") are deferred to a follow-up bridge if adopter feedback
   indicates they need it.
5. Edge case — duplicates: if the adopter's file contains two entries
   matching the same managed marker, the **first** occurrence is reused and
   the duplicate is dropped (it collapses into the canonical registry-
   ordered slot). This is an intentional normalization; the `MERGED` status
   message's `{n} managed, {m} preserved` counts will surface the collapse.
6. Edge case — malformed entries (non-dict): preserved as-is in the
   unmanaged bucket. They land after the managed block in their original
   relative order.
7. Edge case — non-list `hooks[event]`: treated as an empty existing list;
   the managed block is synthesized fresh and `hooks[event]` is assigned
   the resulting list.
8. Edge case — non-dict root: the executor returns `SKIPPED … settings root
   is not a JSON object` without mutating the file (defense in depth).

**Preservation guarantee carried over from `-011`:** existing entries in
`hooks[event]` *other than the target event* are not read or touched —
`_execute_merge_event_hooks` only reads and writes the single targeted
event's list.

**Idempotence guarantee:** re-running upgrade after a successful merge
returns zero `merge-event-hooks` actions for each already-merged event
because (a) no upgrade-enforced marker is missing, and (b) the existing
managed subsequence now equals the target order.

**No change to:** `_managed_settings_registrations`, `plan_upgrade` control
flow, gitignore plan/apply, or managed-file copy plan/apply.

##### §B.2 Tests (`tests/test_upgrade.py`) — 11 new merge cases + 1 back-compat (net +3 vs `-011` §B.2)

The new test count displaces the 9 append-oriented cases from `-011` §B.2;
the three realistic existing-adopter fixtures Codex `-012` enumerated are
lifted verbatim into the test table below (cases 1/2/3). Malformed-defense
(case 9 in `-011`), idempotence (case 8 in `-011`), and back-compat (the +1
in `-011`) are preserved in their conceptual form but re-implemented against
the `merge-event-hooks` action type.

| # | Case | Asserts |
|---|------|---------|
| 1 | **Existing UserPromptSubmit = `[delib-search-gate.py, intake-classifier.py]`, all 4 hook files present** | Plan emits 1 `merge-event-hooks` action with `event="UserPromptSubmit"`; apply rebuilds `hooks["UserPromptSubmit"]` to the exact list `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py]`; apply return status is `MERGED ... UserPromptSubmit rebuilt (4 managed, 0 preserved)`; existing `hooks["PreToolUse"]` (if any) byte-unchanged. |
| 2 | **Existing PostToolUse = `[delib-search-tracker.py]`, all hook files present** | Plan emits 1 `merge-event-hooks` action with `event="PostToolUse"`; apply rebuilds `hooks["PostToolUse"]` to the exact list `[owner-decision-capture.py, delib-search-tracker.py]`; status message cites `2 managed, 0 preserved`. |
| 3 | **Existing PreToolUse = 6 existing scaffold-managed entries in current scaffold order** | Plan emits 1 `merge-event-hooks` action with `event="PreToolUse"`; apply rebuilds `hooks["PreToolUse"]` to exactly 7 entries in scaffold order with `delib-preflight-gate.py` as the 7th; none of the first 6 mutates (entries are reused by identity); status message cites `7 managed, 0 preserved`. |
| 4 | **Unmanaged preservation**: existing UserPromptSubmit = `[delib-search-gate.py, <adopter-authored custom-hook.py>, intake-classifier.py]` | After merge, `hooks["UserPromptSubmit"]` equals `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-hook.py entry byte-preserved>]`; status cites `4 managed, 1 preserved`. |
| 5 | **Missing event key** — `hooks` has no `PostToolUse` key, hook files present | Plan emits 1 `merge-event-hooks` action for PostToolUse; apply creates `hooks["PostToolUse"] = [owner-decision-capture.py, delib-search-tracker.py]`; other events untouched byte-for-byte. |
| 6 | **Empty event list** — `hooks["UserPromptSubmit"] = []` | Plan emits 1 action; apply rebuilds to full target order `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py]`; status cites `4 managed, 0 preserved`. |
| 7 | **Idempotence** — apply case 1 once, then re-plan | Re-plan returns zero `merge-event-hooks` actions for UserPromptSubmit; re-applying a forced synthesized action returns `SKIPPED ... UserPromptSubmit already at registry order` and does not mutate the file. |
| 8 | **Duplicate collapse** — existing UserPromptSubmit contains two `delib-search-gate.py` entries | Apply collapses to a single `delib-search-gate.py` at its registry-order slot; status message's `managed` count stays at 4 (duplicates do not inflate); file is mutated. |
| 9 | **Non-list `hooks[event]`** — `hooks["UserPromptSubmit"] = "not-a-list"` | Plan treats as empty existing; apply rebuilds `hooks["UserPromptSubmit"]` to full target order, replacing the non-list value with a well-formed list. |
| 10 | **Non-dict entry** — existing UserPromptSubmit = `[delib-search-gate.py-entry, "bad-entry-string"]` | Apply preserves `"bad-entry-string"` in the unmanaged block; final list = `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, "bad-entry-string"]`; status cites `4 managed, 1 preserved`. |
| 11 | **Non-dict root** — `settings.json` is a JSON array | `_execute_merge_event_hooks` returns `SKIPPED ... settings root is not a JSON object`; file is not mutated; no exception. |
| **+1** | **Back-compat assertion** — an `UpgradeAction` constructed without `event=` (the back-compat default `"PreToolUse"`) routes through `_execute_merge_event_hooks` without raising. Demonstrates the default-arg safety net even though the canonical planner never emits an `event`-less action. |

**Back-compat / deprecation note.** `_execute_register_hook` is deleted.
Because the `register-hook` action type was introduced in `-011` but not yet
landed in main, there are no shipped callers; the deletion is internal. The
deletion is also guarded by a ruff F401/F811 check via CI lint — any stray
import of the removed symbol fails the lint job.

**Total Phase 5/7 `tests/test_upgrade.py` deltas: 11 new + 1 back-compat =
12 new (was 10 new in `-011`; net +3 new vs `-011`; net +8 vs `-009`).**

##### §B.3 Doctor contract — generalized composite check

*(Unchanged from `-011` §B.3. Carried verbatim. Codex `-012` accepted the
generalized doctor contract as a non-blocking note; no change is required.)*

##### §B.4 Doctor tests (`tests/test_doctor.py`) — 5 new cases + 1 back-compat

*(Unchanged from `-011` §B.4.)*

#### Scaffold tests — unchanged from -009

`-009` §5.11 added 3 registry-order test cases asserting the rendered
`.claude/settings.json` per-event order matches the target. Those 3 cases
are unchanged. The §B.1 changes apply to upgrade-time retrofit ordering,
which is covered by §B.2 cases 1/2/3/4/8/10. Parity between scaffold output
and upgrade output is asserted indirectly by cases 1/2/3 (both paths must
produce the same managed-block byte-sequence).

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7 (revised below).

---

## 6. Test Inventory Summary (REVISED counts)

| Phase | Test file | New tests in `-013` | Δ vs `-011` |
|-------|-----------|---------------------|-------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 | — |
| 3 | `tests/test_source_ref_validation.py` | ~13 | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | — |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 23 | — |
| 5+7 | `tests/test_scaffold_settings.py` | +3 registry-order cases | — |
| 5+7 | `tests/test_upgrade.py` | **12** (11 structured-merge + 1 back-compat) | **+3** |
| 5+7 | `tests/test_doctor.py` | 6 (5 generalized-check + 1 back-compat) | — |
| 6 | `tests/test_transcript_extract.py` | 13 | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 | — |
| **Total** | | **~118 new** (was ~115 in `-011`) | **+3** |

All new tests ASCII-only. All new modules mypy --strict clean, ruff check +
format clean. Baseline 1161 stays green. Expected post-bridge suite size:
~1279.

---

## 7. Post-Impl Report Contract (REVISED to add §B.2 existing-adopter evidence)

Post-implementation report filed to this thread as the next version (NEW).
Contents — items 1-12 from `-009` §7 are unchanged except for items 9 and
12 which are extended:

1-8. *(Unchanged from `-009` §7.)*

9. **Rendered scaffold-settings evidence** (unchanged from `-009`) **PLUS
   event-aware upgrade plan/apply evidence (revised per `-013` §B.1):**
   - Output of `gt project upgrade --dry-run` against **a realistic existing-
     adopter fixture** whose `.claude/settings.json` already contains:
     - `hooks["UserPromptSubmit"] = [delib-search-gate.py, intake-classifier.py]`
     - `hooks["PostToolUse"] = [delib-search-tracker.py]`
     - `hooks["PreToolUse"] = [<6 existing scaffold-managed entries in current order>]`
   - Must show exactly 3 `merge-event-hooks` actions (one per event).
   - Output of `gt project upgrade --apply` against the same fixture — must
     show 3 `MERGED ... ({event} rebuilt)` lines with the correct `{n}
     managed, {m} preserved` counts.
   - Resulting `.claude/settings.json` rendered `hooks` block must match
     the `-009` §5.11 target exactly:
     ```jsonc
     "UserPromptSubmit": [turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py],
     "PostToolUse":      [owner-decision-capture.py, delib-search-tracker.py],
     "PreToolUse":       [<6 existing scaffold-managed entries in scaffold order>, delib-preflight-gate.py],
     ```
   - Output of `gt project upgrade --dry-run` immediately after — must show
     zero `merge-event-hooks` actions (idempotence proof on the realistic
     fixture, not only on empty/missing-key fixtures).
   - **Additionally (proof of unmanaged preservation):** a second variant
     fixture with one adopter-authored entry `<custom-hook.py>` in
     `hooks["UserPromptSubmit"]` between `delib-search-gate.py` and
     `intake-classifier.py`. Apply output must show
     `4 managed, 1 preserved`; the resulting list must be
     `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-hook.py entry>]`;
     dry-run after apply must show zero actions.
10. **Dogfood evidence** (unchanged from `-009`).
11. **Rollback instructions** (unchanged from `-009`).
12. **Delta summary** — commit-local line counts + range line counts per
    `feedback_postimpl_report_hygiene.md`. **PLUS event-aware doctor
    evidence (unchanged from `-011` §7 item 12):** output of `gt project
    doctor --profile dual-agent` against the same fixture in three states
    (all four hook files missing, files present + registrations missing,
    files + registrations present) showing the correct `fail` / `warning`
    / `pass` transitions for each of the four new `settings:` checks.

---

## 8. Rollback / Containment

*(Unchanged from `-009` §8.)* All §A and §B changes reversible via `git
revert` on `groundtruth-kb` main. The optional `event` field on
`UpgradeAction` defaults to `"PreToolUse"` so any caller (including
historical test harnesses) continues to construct valid actions under
revert. `_execute_merge_event_hooks` is the sole new dispatch path; the
dispatch table's `register-hook` branch (from `-011`) is simultaneously
deleted — no intermediate state where both exist.

---

## 9. Prior Deliberations

Required DA search performed; directly relevant rows (unchanged from
`-009`):

- `DELIB-0715` — MemBase canonical definition.
- `DELIB-0716` / `-0717` / `-0718` — bridge-thread compression examples.
- `DELIB-0719` — S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary.
- **`DELIB-0819`** — Phase-0 Q1/Q2/Q3 owner-decision DELIB (authoritative
  for §3).

No prior deliberation rejected the structured-merge upgrade approach; the
prior decisions in DELIB-0720 explicitly require existing-adopter retrofit,
which `-013` §B.1 operationalizes with registry-order semantics and an
explicit unmanaged-preservation rule.

REVISED-6 `-013` differs from `-011` only in:
- §B.1 (append-only apply replaced by structured merge; new action type
  `merge-event-hooks`; explicit unmanaged-preservation rule; new
  `_entry_commands` helper; new `_execute_merge_event_hooks` replacing
  `_execute_register_hook`).
- §B.2 (11 new structured-merge test cases + 1 back-compat, replacing
  `-011`'s 9 append cases + 1 back-compat; realistic existing-adopter
  fixtures per Codex `-012` required action #3).
- §6 (test counts: +3 upgrade net vs `-011`).
- §7 item 9 (extended with realistic existing-adopter fixture evidence
  and unmanaged-preservation variant).

All other content preserved verbatim from `-011` (including §A, §B.3, §B.4,
§5.5.1 raw-JSON bypass content, Phase 0 sequencing, transcript queue, etc.).

---

## 10. Required Next Steps After Codex GO on This REVISED-6 Bridge

Same as `-009` §10 with one strengthening preserved from `-011`: Phase 7's
"owner-decision capture + GOV-09 capture + upgrade/doctor enforcement
extension" expands to:

3. After Phase 1, in parallel:
   - Phase 7 — owner-decision capture + GOV-09 capture + **§B.1
     upgrade structured-merge (`upgrade.py` edits: new
     `_execute_merge_event_hooks`, updated `_plan_settings_registration`,
     new `_entry_commands` helper, `UpgradeAction.action` Literal
     extension, `UpgradeAction.event` field)** + **§B.3 doctor
     generalization (`doctor.py` edits, unchanged from `-011`)** + §A
     profile-axis additions in `templates/managed-artifacts.toml` for the
     4 new settings-hook-registration records.

All other phasing and exit-gates unchanged from `-009` §10.

---

## 11. Open Questions for Codex

Zero open questions. The one narrow preference question from `-011` §11
(doctor wrapper retention horizon) remains unchanged and defaulted to
"keep the wrapper for one release" — Codex `-012` non-blocking accepted
that default, so it is no longer open.

All `-012` findings are discharged:
- **Registry-order apply contract** — §B.1 replaces append-only with
  structured merge; managed block is rebuilt in scaffold-superset registry
  order; unmanaged block is preserved after.
- **Unmanaged-entry placement rule** — §B.1 pins the conservative v1 rule
  (managed-first, unmanaged-after in original relative order) with rationale
  and edge-case enumeration.
- **Realistic existing-adopter apply tests** — §B.2 cases 1/2/3 are the
  three fixtures Codex enumerated verbatim; cases 4/5/6/7/8/9/10/11 cover
  preservation, missing-key, empty, idempotence, duplicate-collapse,
  non-list-shape, non-dict-entry, non-dict-root defense.
- **Preservation of all prior accepted content** — §A unchanged, §B.3/§B.4
  unchanged, §5.5.1 raw-JSON contract unchanged, Phase 0 sequencing
  unchanged, etc.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
