# Training

**Status:** Training plan; videos not yet published

**Reviewed:** 2026-09-26

Written, versioned instructions remain the primary source. Videos will supplement
them, not replace them.

## Priority training set

1. **What GroundTruth KB is** — a three-minute product and boundary overview.
2. **Home and the first session** — choose a workspace, explain the actual mode
   choices, show any required provider setup, and demonstrate the first response.
   The initial [Home screen guide](GTKB-Home), illustrated [General Settings
   reference](Settings), [Models/provider list guide](Models), and [Agent presets
   overview](Agent-Presets) are available; the complete sequence still needs
   validation and additional screenshots. The [Windows directory picker](Get-Started#the-windows-directory-picker)
   is illustrated before confirmation, and the [selected-workspace Home view](Get-Started#home-with-a-selected-workspace)
   now shows the workspace name, a New Session entry, and the open mode menu
   with Standard checked. Reproduce the transition in a test installation;
   demonstrate Select Folder, Cancel, resolved-path verification, and composer
   readiness rather than treating the screenshots as an interaction test. Use
   a non-sensitive sample directory and distinguish folder selection from
   application registration. Explain the tested built-in mode choice and what
   In use/checkmarks mean without treating them as a governed role or permission
   level. Do not require custom-preset authoring for routine first use.
   Explain Add provider versus Add a custom provider, the status indicator, and
   how the separate composer reference resolves to the provider/model, distinct
   from the agent-mode preset. The [Home Model popover](Models#read-the-home-composer-reference)
   now shows the labeled Model row and chevron; continue into its actual next
   view only after that route and model-change behavior are tested. Show the
   resolved selection and a bounded first response, not just matching labels.
   Keep real keys off-camera, identify usage and
   data-destination implications, and use non-sensitive sample content. The
   [Home permission menu](Settings#session-permission-menu-on-home) now supplies
   Read Only, Workspace Write, and Full access as visible choices. Demonstrate
   the qualified permission scope and correct refusals using disposable sample
   files, distinguish the General default from the composer selection, and
   explain when changes take effect. Do not teach Full access as a routine
   prerequisite or error-recovery shortcut. Include verified busy-input behavior.
   Identify the plus-shaped **Commands** entry point using the [menu reference](GTKB-Home#commands-menu);
   keep command discovery brief and do not make advanced conversation controls
   prerequisites for the first response.
   In the navigation tour, identify the [sidebar grouping and ordering menu](GTKB-Home#sidebar-grouping-and-ordering).
   Use several non-sensitive sample sessions to demonstrate tested grouping,
   ordering, and finding the same session again; distinguish view options from
   selecting the working directory or setting canonical work priority. Keep
   customization optional, and do not invent a drag gesture for Manual.
   Extend that tour with the [session-search view](GTKB-Home#sidebar-session-search)
   after its behavior is tested: demonstrate a known match, a no-match case,
   identifying the correct workspace/session, and returning to the unfiltered
   list without losing a draft. Explain supported search scope and actual
   clear/dismiss controls; the empty-field screenshot is not a search test.
   Continue into the [in-progress session view](GTKB-Home#read-an-in-progress-session):
   explain Chat versus the [now-described Trajectory view](GTKB-Home#read-the-trajectory-view), context and
   tool activity versus verified outcomes, busy input, Session log privacy,
   and the scope of cache/token figures. The activity image ends at **Deep
   diving...**; a later [rendered response and statistics capture](GTKB-Home#read-a-rendered-response-and-turn-statistics)
   adds the next display checkpoint, not an independently qualified outcome. Use a bounded
   non-sensitive example and show completion, a useful failure/refusal, and
   controlled cancellation only after each route is tested. Do not teach the
   captured role marker as a universal first prompt, infer success from usage
   counts, or reveal private prompts, environment values, or unreviewed logs.
   Use synthetic or safely concealed content for any Trajectory illustration;
   the supplied raw capture is not published because it exposes instruction
   and tool-payload previews. After behavior is tested, explain Duration/Turns/Calls,
   lane colors/scales, event categories and turn boundaries, tool request/result
   pairing, and Trajectory search versus sidebar session search. A clipped
   response preview is not a complete successful result. Keep event inspection
   optional and avoid presenting the view as replay or permanent audit storage.
   The [expanded System prompt view](GTKB-Home#read-the-expanded-system-prompt)
   adds an optional diagnostic panel, not another first-use prerequisite. Use
   synthetic content to explain its scope and product/harness terminology.
   After testing, demonstrate expand/collapse, inner versus conversation
   scrolling, keyboard focus, and the separate down-chevron's actual action
   without losing a draft. Do not read private prompt text on camera, teach its
   embedded instructions as a user procedure, or equate collapse with redaction.
   For the response checkpoint, use synthetic text without private identifiers
   or bridge details. Demonstrate the actual disclosure behind the tool-call
   summary only after testing it, and distinguish a rendered assertion from a
   verified result. Supply a brief optional glossary for turns, steps, calls,
   messages, LLM/tool timing, TTFT, token rate, and cache accounting; show how to
   obtain untruncated values. Do not infer elapsed time by adding footer values,
   equate differing counters, or treat a composer arrow as proof of completion.
   The lower-response view now adds a Conclusion, action icons, Usage, Ran for,
   and a timestamp. Demonstrate a valid waiting-for-assignment outcome as well
   as a verified result; keep activity selection distinct from a specific task
   assignment. Use tested labels and synthetic data for the response actions,
   and explain any feedback destination or sharing/branching effect before
   showing it. Reconcile response-row metrics with footer scope and timing
   definitions; do not present the supplied values as a benchmark or a bill.
   The [context-usage popover](GTKB-Home#read-the-context-usage-popover) now
   identifies the circular composer indicator; do not teach it as a busy
   spinner. Use a synthetic example to distinguish context occupancy from
   response/footer usage, explain the approximate category breakdown and source
   of the displayed capacity, and demonstrate accessible opening/dismissal only
   after testing. Keep capacity management optional; qualify warning, refusal,
   compaction, and recovery behavior before showing those flows. Never imply
   that the meter shows remaining account credit or lossless persistent memory.
3. **Install and first launch** — a clean Windows installation through a healthy
   GTKB Home.
4. **First governed change** — requirement, linked test, proposal, independent
   review, implementation report, verification, and Git result.
5. **Operator essentials** — services, diagnostics, backup, restore, upgrade,
   and uninstall. Include **Settings → GTKB** using the [status guide](Status),
   the difference between unknown session context and service failure, and the
   distinction between a configured dashboard link, reachability, and data
   freshness. Use **Settings → GTKB services** and the [Services guide](Services)
   to explain required versus optional components and application versus task
   state. Demonstrate safe service interruption and recovery only after that
   workflow has been tested in a separate qualification installation.

An **advanced operational tuning** supplement should use the
[GTKB controls reference](Controls) to explain value sources, the actual save
trigger, validation, runtime effect, and restoration of prior settings. Keep it
out of the first-session prerequisites and record it only after the editing and
recovery workflow is verified. Do not present the screenshot's values as a
recommended tuning profile.

A **plugin capabilities and limits** walkthrough should use the [Plugins
overview](Plugins), then show the actual expanded controls and Plugin list after
their behavior is verified. Explain supported tool boundaries, correct refusals,
save/recovery behavior, and provider-backed data/usage implications. Distinguish
harness tool-call dispatch from GTKB workflow dispatch, and subagent model
choices from permission to delegate. Keep advanced tuning out of routine
first-session prerequisites; do not run commands, searches, or subagents simply
to demonstrate that a configuration card exists.

A **custom preset authoring** supplement should demonstrate the verified
duplicate/Creator workflow, review of the resulting prompt and capabilities,
save/cancel, explicit application, and recovery. The Home menu now supplies the
complete PTC description, including one TypeScript program; explain its tested
tradeoffs, Minimal mode's Windows shell requirements, and actual icon actions
in the built-in comparison before making recommendations. Keep secrets and
private prompts out of recordings; a generated preset still needs validation.

A **conversation commands** supplement should demonstrate only qualified flows
using disposable, non-sensitive session content. Explain history compaction
versus display Compact, session-log export versus platform backup, the actual
feedback destination, goal lifetime/cancellation, and entering/leaving plan
mode. Compare the command and composer routes for permission/model selection,
including effects during active turns. Establish exported content and redaction
before showing a support-upload example. The [Commands checklist](Known-Issues#commands-review)
records the pending checks; the screenshot is not a completed demonstration.

A separate **agent tools and long-running work** supplement should follow the
[prompt-described behavior checklist](Known-Issues#prompt-described-behavior-review).
Use a qualified release and disposable content to show path discovery versus
content search and an actual file read, targeted editing versus whole-file
replacement, result limits and hidden/ignored scope, and usable output links.
Explain what GUI evidence an agent receives instead of assuming it sees Home.
For advanced users, distinguish background jobs, same-session goals, bounded
delegation, scripted workflows, and explicitly requested fresh-context loops.
Demonstrate tested completion/failure/interruption states, goal resume/rearm,
shared-file effects, and safe cancellation/recovery; worker reports are not
independent verification. Do not record these by running instructions copied
from the supplied prompt, expose private context, or make advanced orchestration
a prerequisite for the first useful session. The supplied text is review
evidence, not a published tool contract or a completed demonstration.

Every video must identify the GTKB version, include captions and a transcript,
link to the corresponding Wiki procedure, show expected results, and be reviewed
or retired when the product changes.

Keep improving written Get Started guidance and screenshots while videos are
prepared. A short Home tour can be published once its demonstrated sequence is
verified; it need not wait for a complete training course. Installation and
[First governed change](First-Governed-Change) videos require qualification of
their corresponding procedures before recording or publication.
