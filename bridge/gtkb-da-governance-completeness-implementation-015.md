# Implementation Bridge: DA Governance Completeness (REVISED-7, focused delta vs -013)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-18
**Target repo:** `groundtruth-kb`

**Revision basis:** addresses the single remaining blocker in Codex NO-GO
`bridge/gtkb-da-governance-completeness-implementation-014.md`:

- **High (only remaining blocker from `-014`)** — `-013` §B.1's planner
  trigger compared only the **managed subsequence** (`existing_managed_markers !=
  target_managed_markers`) plus "upgrade-enforced marker missing / out-of-
  position among managed entries". That misses the case where all managed
  hooks are already present in the correct relative order but an adopter-owned
  **unmanaged** entry is interleaved inside the managed block. The bridge's
  own final-shape contract (managed block first, unmanaged block after)
  requires apply to mutate that file, but `-013`'s planner would report zero
  actions. **Resolved in §B.1 (rewritten) and §B.2 (two added cases) below.**

**Supersedes `-013`.** Preserves every piece of content accepted by `-008`,
`-010` non-blocking notes, `-012` non-blocking notes, and `-014` non-blocking
notes:

- `-014` non-blocking — append-only defect from `-012` resolved (accepted).
- `-014` non-blocking — unmanaged-preservation rule (managed-first,
  unmanaged-after) acceptable (accepted).
- `-014` non-blocking — bypass `content` raw-JSON contract, canonical bypass
  source refs, no-metadata audit contract, transcript pre-insert queue
  artifact, Phase 0 sequencing, A3/A4/A5 wrap behavior, lifecycle profile
  triples, generalized doctor contract (all accepted).
- All content accepted through `-013` §§1-11 other than §B.1 (planner trigger)
  and §B.2 (test table counts).

This bridge rewrites only:

- **§B.1** — upgrade plan + apply contract. Planner trigger is replaced with
  **target-event-list equality** (planner emits `merge-event-hooks` iff apply
  would change the file). A new `_compute_target_event_list` helper is
  extracted so planner and apply share one definition of the target list.
- **§B.2** — upgrade test table. Two new cases are added (case 12 =
  UserPromptSubmit interleaved-unmanaged, case 13 = PostToolUse interleaved-
  unmanaged) to cover the counterexample Codex `-014` enumerated.
- **§6** — test counts updated to reflect the §B.2 delta (net +2 vs `-013`).
- **§7 item 9** — post-impl evidence adds an **interleaved-unmanaged** fixture
  variant for UserPromptSubmit and for PostToolUse.

All other §-numbered content from `-013` is preserved verbatim. §A (lifecycle
profiles) and §B.3/§B.4 (doctor) carry over without modification.

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this
implementation bridge. Per `.claude/rules/codex-review-gate.md`, no GT-KB
source, doc, hook, template, script, DB, or managed-artifact mutation may
begin until Codex GOs this `-015`.

---

## 1. Summary of Revisions vs `-013`

| Origin | Finding | Where discharged in `-015` |
|--------|---------|----------------------------|
| `-014` sole finding (High) — planner compares only managed subsequence; misses unmanaged entries interleaved inside the managed block | Planner trigger must detect managed/unmanaged interleaving, not just managed-subsequence order | §B.1 — `_plan_settings_registration` rewritten to call new `_compute_target_event_list(event_entries, scaffold_registrations)` helper; trigger = `target_event_list != event_entries`; helper returns exactly what `_execute_merge_event_hooks` will write, so planner/apply agree by construction. |
| `-014` required action #1 — plan a merge when existing != apply-produced target, including interleaved unmanaged | Single-definition target; planner uses it for equality, apply uses it for rebuild | §B.1 — helper `_compute_target_event_list` shared between planner and apply; apply calls it and writes its first return value, planner calls it and compares to existing. |
| `-014` required action #2 — interleaved-unmanaged planning/apply/idempotence tests | Test table `-013` §B.2 had interleaved case only *combined* with missing-hook condition (case 4); Codex required the already-complete-but-interleaved case | §B.2 — **case 12** (UserPromptSubmit: all 4 target managed present in correct relative order, one adopter-owned entry interleaved) and **case 13** (PostToolUse: both target managed present in correct relative order, one adopter-owned entry interleaved). Both cases assert: plan emits 1 action; apply moves the custom entry after the managed block; a second plan emits zero actions. |
| `-014` required action #3 — post-impl evidence must include interleaved-unmanaged fixture | §7 item 9 in `-013` used missing-hook and preservation fixtures | §7 item 9 — adds a third fixture variant: UserPromptSubmit and PostToolUse each contain all target managed entries in correct relative order plus one interleaved unmanaged entry. Dry-run emits 2 actions (one per event); apply rebuilds both; second dry-run emits zero actions. |
| `-014` required action #4 — preserve all prior accepted content | Phase 0 sequencing, transcript queue, source_ref grammar, no-metadata audit contract, raw JSON bypass content, A3/A4/A5, lifecycle profile (§A), generalized doctor (§B.3/§B.4), unmanaged-preservation rule, apply structured-merge behavior | Preserved verbatim. Diff lives only in §B.1 planner trigger, §B.2 cases 12-13, §6 counts, §7 item 9. |

All previously accepted content is retained verbatim unless noted.

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

*(Unchanged from `-009` §2 — all 7 conditions still discharged in the same
locations. §A and §B.1 together still strengthen condition #4 with an
executable contract; `-015` further hardens §B.1 by making planner/apply
share a single definition of the target event list.)*

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

#### §B — Event-aware upgrade plan + apply + doctor contract

##### §B.1 Plan/apply contract — code-level changes (REWRITTEN for `-015`)

This sub-section **replaces** `-013` §B.1 in its entirety. §B.3 (doctor
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
must match). **Planner and apply share a single `_compute_target_event_list`
helper, so the planner emits `merge-event-hooks` iff apply would change the
file.**

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
`"append-gitignore"` for `-011`; for `-013`/`-015` the new member is
`"merge-event-hooks"` (and `"register-hook"` is **not** introduced, since
its semantics were the defect).

**New helper — `_entry_commands`.** *(Unchanged from `-013`.)*

```python
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

**New helper — `_compute_target_event_list` (NEW in `-015`).** Computes the
target event list that apply will write, given the existing entries and the
event's scaffold-superset registrations. This is the *single definition* of
"target list" shared by planner and apply. Returning the managed/unmanaged
counts alongside the list lets apply emit its status message without
recomputing.

```python
def _compute_target_event_list(
    existing_entries: list[object],
    scaffold_registrations: list[SettingsHookRegistration],
) -> tuple[list[object], int, int]:
    """Return ``(target_list, n_managed, n_preserved)``.

    target_list = registry-ordered managed block ++ unmanaged block in
    original relative order. Existing managed entries are reused by identity
    when their command marker matches; missing managed entries are
    synthesized in the canonical shape. Duplicate managed entries collapse
    to the first occurrence. Non-dict entries and entries whose commands do
    not match any scaffold-superset marker fall into the unmanaged block.
    """
    scaffold_filenames: list[str] = [r.hook_filename for r in scaffold_registrations]
    scaffold_markers: set[str] = {
        f"python .claude/hooks/{fn}" for fn in scaffold_filenames
    }

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
            # First occurrence wins; duplicates collapse to canonical slot.
            managed_existing_by_marker.setdefault(matched_marker, entry)

    new_managed_block: list[object] = []
    for filename in scaffold_filenames:
        marker = f"python .claude/hooks/{filename}"
        reused = managed_existing_by_marker.get(marker)
        if isinstance(reused, dict):
            new_managed_block.append(reused)
        else:
            new_managed_block.append(
                {"hooks": [{"type": "command", "command": marker}]}
            )

    target_list: list[object] = [*new_managed_block, *unmanaged]
    return target_list, len(new_managed_block), len(unmanaged)
```

**Function replacement — `_plan_settings_registration`** (currently
`upgrade.py:191-270`). Replace the `PreToolUse`-only implementation with a
version that uses `_compute_target_event_list` for the trigger check.

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

    from groundtruth_kb.project.managed_registry import artifacts_for_scaffold

    # Partition scaffold-superset registrations by event in registry order.
    scaffold_by_event: dict[str, list[SettingsHookRegistration]] = {}
    for artifact in artifacts_for_scaffold(profile_name, class_="settings-hook-registration"):
        if isinstance(artifact, SettingsHookRegistration):
            scaffold_by_event.setdefault(artifact.event, []).append(artifact)

    # The outer-loop key set: every event that contains at least one
    # upgrade-enforced record for the active profile. A merge only fires
    # against events the registry claims ownership of.
    upgrade_enforced_by_event: dict[str, list[SettingsHookRegistration]] = {}
    for registration in _managed_settings_registrations(profile_name):
        upgrade_enforced_by_event.setdefault(registration.event, []).append(registration)

    actions: list[UpgradeAction] = []
    for event in upgrade_enforced_by_event.keys():
        raw_event_entries = hooks_dict.get(event)
        event_entries: list[object] = (
            raw_event_entries if isinstance(raw_event_entries, list) else []
        )

        scaffold_registrations = scaffold_by_event.get(event, [])
        target_event_list, _n_managed, _n_preserved = _compute_target_event_list(
            event_entries, scaffold_registrations
        )

        # Trigger: a merge is required iff the target list apply would
        # produce differs from the existing list. This captures every
        # mismatch shape — missing managed entries, wrong managed order,
        # interleaved unmanaged entries, non-list existing value, and
        # duplicate collapses — without a per-shape check.
        if target_event_list != event_entries:
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
```

**Function replacement — `_execute_register_hook` → `_execute_merge_event_hooks`**
(currently `upgrade.py:403-455`). Delete `_execute_register_hook` and add
the simplified executor that delegates the target computation to the shared
helper.

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

    raw_existing = hooks_dict.get(event)
    existing_entries: list[object] = raw_existing if isinstance(raw_existing, list) else []

    new_event_list, n_managed, n_preserved = _compute_target_event_list(
        existing_entries, scaffold_registrations
    )

    if new_event_list == existing_entries:
        return f"SKIPPED {action.file} — {event} already at registry order"

    hooks_dict[event] = new_event_list
    data["hooks"] = hooks_dict
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"MERGED {action.file} — {event} rebuilt ({n_managed} managed, {n_preserved} preserved)"
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
   **This rule applies uniformly whether the unmanaged entry originally
   appeared before, between, or after the managed entries on disk — the
   planner/apply pair does not attempt to preserve original position
   *relative to the managed block*, only original position *among
   unmanaged entries*.**
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

**Idempotence guarantee (strengthened in `-015`):** re-running upgrade
after a successful merge returns zero `merge-event-hooks` actions for each
already-merged event because `_compute_target_event_list(existing_entries,
scaffold_registrations)` is idempotent — feeding it its own output returns
byte-equal output, so the planner's `target_event_list != event_entries`
check is `False` on the second pass. (Tested directly in case 7 and in the
two new interleaved cases 12 and 13.)

**Planner/apply parity guarantee (new in `-015`).** Because both
`_plan_settings_registration` and `_execute_merge_event_hooks` route
through `_compute_target_event_list`, the planner emits an action iff apply
would change the file. There is no shape of existing `hooks[event]` list
for which dry-run can report zero actions while apply would still mutate
that event's list (nor vice versa).

**No change to:** `_managed_settings_registrations`, `plan_upgrade` control
flow, gitignore plan/apply, or managed-file copy plan/apply.

##### §B.2 Tests (`tests/test_upgrade.py`) — 13 new merge cases + 1 back-compat (net +2 vs `-013` §B.2)

Cases 1-11 and the back-compat row are unchanged from `-013` §B.2. Cases
**12** and **13** are new in `-015` to satisfy Codex `-014` required action
#2 (interleaved-unmanaged with all target managed already in correct
relative order, for UserPromptSubmit and for PostToolUse).

| # | Case | Asserts |
|---|------|---------|
| 1 | **Existing UserPromptSubmit = `[delib-search-gate.py, intake-classifier.py]`, all 4 hook files present** | Plan emits 1 `merge-event-hooks` action with `event="UserPromptSubmit"`; apply rebuilds `hooks["UserPromptSubmit"]` to the exact list `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py]`; apply return status is `MERGED ... UserPromptSubmit rebuilt (4 managed, 0 preserved)`; existing `hooks["PreToolUse"]` (if any) byte-unchanged. |
| 2 | **Existing PostToolUse = `[delib-search-tracker.py]`, all hook files present** | Plan emits 1 `merge-event-hooks` action with `event="PostToolUse"`; apply rebuilds `hooks["PostToolUse"]` to the exact list `[owner-decision-capture.py, delib-search-tracker.py]`; status message cites `2 managed, 0 preserved`. |
| 3 | **Existing PreToolUse = 6 existing scaffold-managed entries in current scaffold order** | Plan emits 1 `merge-event-hooks` action with `event="PreToolUse"`; apply rebuilds `hooks["PreToolUse"]` to exactly 7 entries in scaffold order with `delib-preflight-gate.py` as the 7th; none of the first 6 mutates (entries are reused by identity); status message cites `7 managed, 0 preserved`. |
| 4 | **Unmanaged preservation**: existing UserPromptSubmit = `[delib-search-gate.py, <adopter-authored custom-hook.py>, intake-classifier.py]` (managed incomplete *and* unmanaged interleaved) | After merge, `hooks["UserPromptSubmit"]` equals `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-hook.py entry byte-preserved>]`; status cites `4 managed, 1 preserved`. |
| 5 | **Missing event key** — `hooks` has no `PostToolUse` key, hook files present | Plan emits 1 `merge-event-hooks` action for PostToolUse; apply creates `hooks["PostToolUse"] = [owner-decision-capture.py, delib-search-tracker.py]`; other events untouched byte-for-byte. |
| 6 | **Empty event list** — `hooks["UserPromptSubmit"] = []` | Plan emits 1 action; apply rebuilds to full target order `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py]`; status cites `4 managed, 0 preserved`. |
| 7 | **Idempotence** — apply case 1 once, then re-plan | Re-plan returns zero `merge-event-hooks` actions for UserPromptSubmit; re-applying a forced synthesized action returns `SKIPPED ... UserPromptSubmit already at registry order` and does not mutate the file. |
| 8 | **Duplicate collapse** — existing UserPromptSubmit contains two `delib-search-gate.py` entries | Apply collapses to a single `delib-search-gate.py` at its registry-order slot; status message's `managed` count stays at 4 (duplicates do not inflate); file is mutated. |
| 9 | **Non-list `hooks[event]`** — `hooks["UserPromptSubmit"] = "not-a-list"` | Plan treats as empty existing; apply rebuilds `hooks["UserPromptSubmit"]` to full target order, replacing the non-list value with a well-formed list. |
| 10 | **Non-dict entry** — existing UserPromptSubmit = `[delib-search-gate.py-entry, "bad-entry-string"]` | Apply preserves `"bad-entry-string"` in the unmanaged block; final list = `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, "bad-entry-string"]`; status cites `4 managed, 1 preserved`. |
| 11 | **Non-dict root** — `settings.json` is a JSON array | `_execute_merge_event_hooks` returns `SKIPPED ... settings root is not a JSON object`; file is not mutated; no exception. |
| **12 (NEW in `-015`)** | **Interleaved-unmanaged, UserPromptSubmit, all managed present in correct relative order** — existing `hooks["UserPromptSubmit"] = [turn-marker.py, delib-search-gate.py, <adopter-authored custom-hook.py>, gov09-capture.py, intake-classifier.py]` (all 4 target managed hooks present in correct registry relative order, one unmanaged entry interleaved between `delib-search-gate.py` and `gov09-capture.py`) | Plan emits **exactly 1** `merge-event-hooks` action with `event="UserPromptSubmit"` (this is the Codex `-014` counterexample: the `-013` planner would have emitted zero here); apply rebuilds `hooks["UserPromptSubmit"]` to `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-hook.py entry byte-preserved by identity>]`; status cites `MERGED ... UserPromptSubmit rebuilt (4 managed, 1 preserved)`; a **second** plan on the resulting file emits **zero** `merge-event-hooks` actions (idempotence on the interleaved shape). |
| **13 (NEW in `-015`)** | **Interleaved-unmanaged, PostToolUse, all managed present in correct relative order** — existing `hooks["PostToolUse"] = [owner-decision-capture.py, <adopter-authored custom-post-hook.py>, delib-search-tracker.py]` (both target managed hooks present in correct registry relative order, one unmanaged entry interleaved between them) | Plan emits **exactly 1** `merge-event-hooks` action with `event="PostToolUse"`; apply rebuilds `hooks["PostToolUse"]` to `[owner-decision-capture.py, delib-search-tracker.py, <custom-post-hook.py entry byte-preserved by identity>]`; status cites `MERGED ... PostToolUse rebuilt (2 managed, 1 preserved)`; a **second** plan emits **zero** `merge-event-hooks` actions. This case covers Codex `-014` required-action #4 (the same shape must hold for PostToolUse, which this implementation supports symmetrically because the planner/apply pair is event-agnostic — both events route through `_compute_target_event_list` with only the scaffold registrations differing per event). |
| **+1** | **Back-compat assertion** — an `UpgradeAction` constructed without `event=` (the back-compat default `"PreToolUse"`) routes through `_execute_merge_event_hooks` without raising. Demonstrates the default-arg safety net even though the canonical planner never emits an `event`-less action. |

**Back-compat / deprecation note.** `_execute_register_hook` is deleted.
Because the `register-hook` action type was introduced in `-011` but not yet
landed in main, there are no shipped callers; the deletion is internal. The
deletion is also guarded by a ruff F401/F811 check via CI lint — any stray
import of the removed symbol fails the lint job.

**Total Phase 5/7 `tests/test_upgrade.py` deltas: 13 new + 1 back-compat =
14 new (was 12 new in `-013`; net +2 new vs `-013`; net +10 vs `-009`).**

##### §B.3 Doctor contract — generalized composite check

*(Unchanged from `-011` §B.3. Carried verbatim. Codex `-012` accepted the
generalized doctor contract as a non-blocking note; `-014` did not raise
new findings against it; no change is required.)*

##### §B.4 Doctor tests (`tests/test_doctor.py`) — 5 new cases + 1 back-compat

*(Unchanged from `-011` §B.4.)*

#### Scaffold tests — unchanged from -009

`-009` §5.11 added 3 registry-order test cases asserting the rendered
`.claude/settings.json` per-event order matches the target. Those 3 cases
are unchanged. The §B.1 changes apply to upgrade-time retrofit ordering,
which is covered by §B.2 cases 1/2/3/4/8/10/12/13. Parity between scaffold
output and upgrade output is asserted indirectly by cases 1/2/3/12/13 (both
paths must produce the same managed-block byte-sequence).

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7 (revised below).

---

## 6. Test Inventory Summary (REVISED counts)

| Phase | Test file | New tests in `-015` | Δ vs `-013` |
|-------|-----------|---------------------|-------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 | — |
| 3 | `tests/test_source_ref_validation.py` | ~13 | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | — |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 23 | — |
| 5+7 | `tests/test_scaffold_settings.py` | +3 registry-order cases | — |
| 5+7 | `tests/test_upgrade.py` | **14** (13 structured-merge + 1 back-compat) | **+2** |
| 5+7 | `tests/test_doctor.py` | 6 (5 generalized-check + 1 back-compat) | — |
| 6 | `tests/test_transcript_extract.py` | 13 | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 | — |
| **Total** | | **~120 new** (was ~118 in `-013`) | **+2** |

All new tests ASCII-only. All new modules mypy --strict clean, ruff check +
format clean. Baseline 1161 stays green. Expected post-bridge suite size:
~1281.

---

## 7. Post-Impl Report Contract (REVISED to add interleaved-unmanaged evidence)

Post-implementation report filed to this thread as the next version (NEW).
Contents — items 1-12 from `-009` §7 are unchanged except for items 9 and
12 which are extended.

1-8. *(Unchanged from `-009` §7.)*

9. **Rendered scaffold-settings evidence** (unchanged from `-009`) **PLUS
   event-aware upgrade plan/apply evidence (revised per `-015` §B.1):**

   **Fixture variant A — realistic existing-adopter missing-hook fixture (from `-013`, unchanged):**
   - Output of `gt project upgrade --dry-run` against a realistic existing-
     adopter fixture whose `.claude/settings.json` already contains:
     - `hooks["UserPromptSubmit"] = [delib-search-gate.py, intake-classifier.py]`
     - `hooks["PostToolUse"] = [delib-search-tracker.py]`
     - `hooks["PreToolUse"] = [<6 existing scaffold-managed entries in current order>]`
   - Must show exactly 3 `merge-event-hooks` actions (one per event).
   - Output of `gt project upgrade --apply` against the same fixture — must
     show 3 `MERGED ... ({event} rebuilt)` lines with the correct `{n}
     managed, {m} preserved` counts.
   - Resulting `.claude/settings.json` rendered `hooks` block must match
     the `-009` §5.11 target exactly.
   - Output of `gt project upgrade --dry-run` immediately after — must show
     zero `merge-event-hooks` actions (idempotence proof on the realistic
     fixture, not only on empty/missing-key fixtures).

   **Fixture variant B — unmanaged-preservation fixture (from `-013`, unchanged):**
   - A second variant fixture with one adopter-authored entry
     `<custom-hook.py>` in `hooks["UserPromptSubmit"]` between
     `delib-search-gate.py` and `intake-classifier.py` (managed incomplete —
     `turn-marker.py` and `gov09-capture.py` missing). Apply output must show
     `4 managed, 1 preserved`; resulting list must be
     `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-hook.py entry>]`;
     dry-run after apply must show zero actions.

   **Fixture variant C — interleaved-unmanaged with all target managed
   already present (NEW in `-015`, required by Codex `-014` action #3):**
   - A third fixture whose `.claude/settings.json` already contains, for
     both UserPromptSubmit and PostToolUse, *all target managed hooks in
     correct registry relative order* plus one adopter-owned entry
     interleaved inside the managed block:
     - `hooks["UserPromptSubmit"] = [turn-marker.py, delib-search-gate.py, <custom-ups.py>, gov09-capture.py, intake-classifier.py]`
     - `hooks["PostToolUse"] = [owner-decision-capture.py, <custom-post.py>, delib-search-tracker.py]`
     - `hooks["PreToolUse"] = [<7 existing scaffold-managed entries in current scaffold order, including delib-preflight-gate.py>]` (so PreToolUse is already fully merged and contributes zero actions, isolating the interleaved-unmanaged effect).
   - `gt project upgrade --dry-run` must emit **exactly 2**
     `merge-event-hooks` actions (UserPromptSubmit + PostToolUse; PreToolUse
     contributes zero).
   - `gt project upgrade --apply` must show 2 `MERGED` lines with
     `UserPromptSubmit rebuilt (4 managed, 1 preserved)` and
     `PostToolUse rebuilt (2 managed, 1 preserved)`.
   - Resulting `hooks["UserPromptSubmit"]` must be
     `[turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py, <custom-ups.py entry byte-preserved by identity>]`.
   - Resulting `hooks["PostToolUse"]` must be
     `[owner-decision-capture.py, delib-search-tracker.py, <custom-post.py entry byte-preserved by identity>]`.
   - Resulting `hooks["PreToolUse"]` must be byte-unchanged from the input
     (no PreToolUse action emitted).
   - Output of `gt project upgrade --dry-run` immediately after must emit
     **zero** `merge-event-hooks` actions across all three events
     (idempotence on the interleaved-unmanaged shape).

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

*(Unchanged from `-009` §8 and `-013` §8.)* All §A and §B changes reversible
via `git revert` on `groundtruth-kb` main. The optional `event` field on
`UpgradeAction` defaults to `"PreToolUse"` so any caller (including
historical test harnesses) continues to construct valid actions under
revert. `_execute_merge_event_hooks` is the sole new dispatch path; the
dispatch table's `register-hook` branch (from `-011`) is simultaneously
deleted — no intermediate state where both exist. The new
`_compute_target_event_list` helper is a pure function with no side effects
and is trivially reverted alongside its two call sites.

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
which `-013`/`-015` §B.1 operationalizes with registry-order semantics, an
explicit unmanaged-preservation rule, and **(new in `-015`)** a planner
trigger that matches apply's output by construction.

REVISED-7 `-015` differs from `-013` only in:
- §B.1 (planner trigger replaced with target-event-list equality via new
  shared `_compute_target_event_list` helper; no change to apply's
  observable behavior, only to the planner's trigger coverage and to the
  single-definition-of-target invariant).
- §B.2 (2 new structured-merge test cases — case 12 UserPromptSubmit
  interleaved, case 13 PostToolUse interleaved — per Codex `-014` required
  action #2 and #4).
- §6 (test counts: +2 upgrade net vs `-013`).
- §7 item 9 (adds fixture variant C = interleaved-unmanaged for both
  UserPromptSubmit and PostToolUse, per Codex `-014` required action #3).

All other content preserved verbatim from `-013` (including §A, §B.3,
§B.4, §5.5.1 raw-JSON bypass content, Phase 0 sequencing, transcript queue,
apply structured-merge behavior, unmanaged-preservation rule text, etc.).

---

## 10. Required Next Steps After Codex GO on This REVISED-7 Bridge

Same as `-009` §10 with one strengthening preserved from `-011`/`-013`:
Phase 7's "owner-decision capture + GOV-09 capture + upgrade/doctor
enforcement extension" expands to:

3. After Phase 1, in parallel:
   - Phase 7 — owner-decision capture + GOV-09 capture + **§B.1
     upgrade structured-merge (`upgrade.py` edits: new
     `_execute_merge_event_hooks`, updated `_plan_settings_registration`,
     new `_entry_commands` helper, **new `_compute_target_event_list`
     helper shared by planner and apply (`-015`)**, `UpgradeAction.action`
     Literal extension, `UpgradeAction.event` field)** + **§B.3 doctor
     generalization (`doctor.py` edits, unchanged from `-011`)** + §A
     profile-axis additions in `templates/managed-artifacts.toml` for the
     4 new settings-hook-registration records.

All other phasing and exit-gates unchanged from `-009` §10.

---

## 11. Open Questions for Codex

Zero open questions. The one narrow preference question from `-011` §11
(doctor wrapper retention horizon) remains unchanged and defaulted to
"keep the wrapper for one release" — Codex `-012` non-blocking accepted
that default; Codex `-014` did not raise any new open questions; so it is
no longer open.

All `-014` findings are discharged:
- **Planner missing interleaved unmanaged entries** (Finding #1 / required
  action #1) — §B.1 replaces the managed-subsequence trigger with a
  target-event-list equality trigger via shared
  `_compute_target_event_list`; by construction, planner emits an action
  iff apply would change the file.
- **Interleaved-unmanaged planning/apply/idempotence tests** (required
  action #2) — §B.2 case 12 covers UserPromptSubmit; idempotence covered
  by the "second plan emits zero actions" assertion.
- **Post-impl evidence includes interleaved-unmanaged fixture** (required
  action #3) — §7 item 9 adds fixture variant C for both UserPromptSubmit
  and PostToolUse.
- **PostToolUse symmetry** (required action #4) — §B.2 case 13 covers
  PostToolUse interleaved-unmanaged; the planner/apply pair is event-
  agnostic (both route through `_compute_target_event_list`), so the
  contract holds uniformly for any event registered in
  `upgrade_enforced_by_event`.
- **Preservation of all prior accepted content** — §A unchanged, §B.3/§B.4
  unchanged, §5.5.1 raw-JSON contract unchanged, Phase 0 sequencing
  unchanged, unmanaged-preservation rule text unchanged, apply observable
  behavior unchanged.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
