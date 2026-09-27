# GTKB status

**Status:** Illustrated status reference; live checks and controls not exercised

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings**, then select **GTKB**. This is the
status pane, distinct from the separately labeled **GTKB services** and
**GTKB controls** sections.

## Read the status pane

![GTKB status in Settings: Overall UNKNOWN; authority, project, bridge, registry, formal, and dashboard show PASS; session shows UNKNOWN with no native context id supplied; the dashboard row says not contacted.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-status.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. Its exact
build/version is not visible. All results, counts, paths, and times below are
examples from this capture, not a current report about your installation. The
review did not contact the displayed local endpoints or exercise the controls.

The header shows **Overall UNKNOWN**. Six rows show **PASS** and the session row
shows **UNKNOWN**. Read each row's explanation; the screenshot does not establish
the complete overall-status aggregation rule.

| Row | Displayed result and detail | Interpretation boundary |
| --- | --- | --- |
| **authority** | **PASS**; ready at `http://127.0.0.1:8765` | The pane reports authority readiness at the displayed address. This captured result is not an independent current endpoint check or full installation qualification. |
| **project** | **PASS**; `E:\GT-KB`, 1 registered application | This identifies the example root and an application-registration count. It is not a count of canonical projects or evidence of project authorization. Use your own installed configuration; do not rename a root to match this image. |
| **bridge** | **PASS**; `active_claim_count 0`, `active_status_mix 1`, `attempts 1`, `unfiled_attempt_count 0` | These are displayed coordination summaries, not proof that work is complete or available to claim. The abbreviated status-mix value does not identify the underlying statuses or work items. |
| **registry** | **PASS**; 371 declarations, 296 active | These are example declaration counts, not required installation targets or an agent count. |
| **formal** | **PASS**; no ambiguities, source issues, or validation issues reported | This is the pane's reported check result. It does not establish complete product correctness or independent release qualification. |
| **session** | **UNKNOWN**; no native context id supplied, with nothing inferred from the environment | Session-specific information was not established in this result. Do not read it as a proven authority-service outage or invent a context identifier to make the row green. |
| **dashboard** | **PASS**; a local dashboard URL on port 3000, explicitly marked **not contacted** | This row does not establish dashboard reachability. A configured or displayed URL is not an observed successful connection. |

## Overall UNKNOWN and session context

An unknown result needs its stated reason, not an automatic reinstall or service
restart. In this capture, the session explanation explicitly identifies a
missing native context identifier while the authority row reports ready.

If you are inspecting host status without a session context, the session row
does not by itself establish a host failure. If you need session-specific
diagnostics, use the installed release's supported session workflow and check
the actual context supplied. Do not guess an identity, reuse another session's
identity, or infer a governed role from this screen. See
[Core concepts](Core-Concepts) and [Troubleshooting](Troubleshooting).

The documentation still needs a tested definition of the overall aggregation
rule and the next action for each possible row result.

## Refresh times and dashboard links

The capture contains two different timestamps on 2026-09-26:

- the overall status header shows **6:09:13 PM**;
- the **GTKB dashboard** card says **Last refreshed 1:44:39 PM**.

No timezone is shown. The different times should not be treated as one shared
freshness result. The screenshot alone does not establish an acceptable age,
automatic refresh interval, or failure threshold.

The pane exposes **Refresh**, **Open dashboard**, **Overview page**, and
**License notices**. The refresh effect and link destinations have not been
exercised in this documentation pass. In particular:

- after requesting a refresh, check which timestamp and results actually
  changed; do not assume an older dashboard was regenerated;
- use the displayed dashboard route for the selected installation, then verify
  the destination actually responds and displays the intended data;
- distinguish successfully opening a dashboard from proving its underlying
  data is current; and
- do not treat **Open dashboard** and **Overview page** as interchangeable
  without checking their destinations.

## What to check next

Use [Verify installation](Verify-Installation) for service and canonical-read
checks, [Services](Services) for supported operator procedures, and
[Release health](Release-Health) for the distinction between runtime diagnostics
and release evidence. Do not start or stop a service solely because a captured
status was unknown.

The [status review checklist](Known-Issues#status-pane-review) records the remaining
documentation and usability work, including the dashboard's ambiguous PASS
label, session-context guidance, freshness semantics, and readable metric names.
