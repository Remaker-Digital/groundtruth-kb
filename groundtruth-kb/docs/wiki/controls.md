# GTKB controls

**Status:** Illustrated operational-controls reference; editing and runtime effects unverified

**Audience:** Advanced operators

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings → GTKB controls**. The pane is headed
**GTKB configuration** and presents operational tuning fields. It is distinct
from [General Settings](Settings), the [GTKB status pane](Status), and the
Start/Stop controls in [GTKB services](Services).

Use this page to understand the visible fields, not as a tuning prescription.
No change to these values is established as a prerequisite for getting started.
Leave an existing configuration unchanged unless a diagnosed need and a tested
change/recovery procedure justify adjusting it.

## Read the operational-controls panel

![GTKB controls selected in Settings, showing GTKB configuration with eight operational controls, numeric values, seconds or ratio units, allowed ranges, and descriptions for Git probes and registry lock acquisition and retry behavior.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-controls.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. These are the values and ranges shown in that
capture, not confirmed factory defaults, recommended settings, or independently
checked effective runtime values. No value was changed, no button was exercised,
and no configuration file was opened during this review.

The columns are **Control**, **Value**, and **Allowed**; units appear beside the
value fields. Eight controls are visible. This is not evidence that the complete
product has only eight operational controls.

| Control | Value shown | Allowed range shown | Visible purpose |
| --- | --- | --- | --- |
| `inventory.git_probe_seconds` | 30 seconds | 0.001–3600 seconds | Maximum duration of the optional local Git revision probe within one inventory operation. |
| `registry.git_probe_seconds` | 10 seconds | 0.001–3600 seconds | Subprocess timeout for Git checkout identity lookup; the helper describes it as socket-independent. |
| `registry.lock.acquire_seconds` | 300 seconds | 0.001–3600 seconds | Maximum acquisition wait after locating the checkout mutex. |
| `registry.lock.backoff_factor` | 2 ratio | 1–16 ratio | Multiplier applied to the previous retry backoff. |
| `registry.lock.initial_backoff_seconds` | 0.05 seconds | 0.001–3600 seconds | Initial basis for acquisition retry backoff. |
| `registry.lock.jitter_max_ratio` | 1 ratio | 0.001–1 ratio | Upper fractional multiplier for jitter. |
| `registry.lock.jitter_min_ratio` | 0.5 ratio | 0.001–1 ratio | Lower fractional multiplier for jitter. |
| `registry.lock.max_backoff_seconds` | 1 second | 0.001–3600 seconds | Maximum acquisition retry backoff before jitter and remaining-budget clipping. |

These descriptions refer to individual probes and checkout-lock acquisition or
retry behavior. Do not read a probe timeout as the duration of the entire
operation, or an acquisition timeout as a lock-holding duration, bridge-claim
lease, or work-item ownership period. The screenshot does not establish the
complete retry algorithm or a recommended performance profile.

## Configuration path and value source

The subtitle displays **Operational controls** followed by
`E:\GT-KB\config\governance\operational-controls.toml`. This is the example
installation's displayed path, not an instruction to rename your root or edit
that file. The screenshot alone does not establish whether it stores control
definitions, defaults, overrides, or the values currently used by a running
component.

The dialog also has **Open configuration file**, **Refresh**, and a close
control. The file opened by the dialog-level button has not been verified; do
not assume it is the path in the subtitle. Do not manually edit generated
harness configuration or publish configuration files in a support request.

The reference still needs a release-verified explanation of value precedence,
scope, and source: default versus override versus effective value, which
component consumes each value, and when a change takes effect.

## Saving, validation, and recovery

No Save, Apply, Cancel, or Reset button is visible in this capture. That does not
prove autosave or the absence of recovery elsewhere. In particular, do not
assume that leaving a field, pressing Enter, closing the dialog, or selecting
Refresh applies or discards an edit. Their behavior must be tested first.

Before publishing an editing walkthrough, verify in a separate qualification
installation:

1. **Commit and feedback:** establish the save trigger and show pending,
   successful, and failed writes without a false success indication.
2. **Validation:** check numeric types, units, decimal precision, empty and
   non-numeric input, exact boundaries, and values outside the allowed range.
   An on-screen range is not proof of enforcement.
3. **Related values:** verify the intended relationships between minimum and
   maximum jitter and between initial and maximum backoff. Two individually
   in-range values are not proof of a valid combined configuration.
4. **Persistence and effect:** distinguish what the pane displays after refresh
   or reopening from what a subsequent operation or running component actually
   uses. State whether a restart is needed; do not require one by assumption.
5. **Recovery and competing edits:** prove the supported way to restore the
   previous configuration, handle a failed write, and avoid silently losing an
   edit made from another open settings view or supported configuration route.

Do not probe invalid values on an active installation just to test the fields.
If the supported save or recovery procedure is unclear, stop before changing a
value and use [Support](Support) with the control name, intended outcome,
version, and redacted error—not the whole configuration file.

## Documentation and usability follow-up

The [operational controls review checklist](Known-Issues#operational-controls-review)
tracks the remaining checks. Keep an advanced tuning walkthrough separate from
[Get started](Get-Started): a first-time user should not need to understand
mutexes, backoff, or jitter to launch Home and complete a first session. Preserve
the exact technical keys for operators while adding plain-language task and
impact guidance where needed.
