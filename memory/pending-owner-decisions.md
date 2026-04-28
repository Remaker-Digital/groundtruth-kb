# Pending Owner Decisions

This file is owned by .claude/hooks/owner-decision-tracker.py.

---

## Pending

(none)

## Resolved

- id: DECISION-0059
  asked_at: 2026-04-28T18:53:28.329598Z
  question: "y remaining blocker awaiting your explicit approval."
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: 980b414bcaeb639e
  resolved_at: 2026-04-28T19:25:00Z
  resolved_in_session: S319
  answer: "Real question (not FP) — Prime Builder asked owner for explicit destructive-action approval to run `git rm --cached` per feedback_explicit_destructive_action_authorization.md, after destructive-gate hook blocked. Resolved organically: owner ran the cached-removal command themselves at PowerShell prompt, sidestepping the hook. Bridge 2 then committed (b95520c5). Same FP class as DECISION-0052 (S317): hook regex over-broad, catches non-destructive cached-only form. Tracked as follow-on in bridge/session-hygiene-gitignore-extensions-2026-04-28-003.md §8 — recommend hook refinement to recognize --cached/--staged as non-destructive flags."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T19:25:00Z (real question; resolved by owner action)"
- id: DECISION-0058
  asked_at: 2026-04-28T18:05:12.361592Z
  question: "Bridge 1 is filed, should I also begin drafting Bridge 2 (the hygiene gitignore extensions for items #5–#9 from the original drift triage) in parallel, or wait until Bridge 1 is VERIFIED before opening another thread?"
  detected_via: prose:should_i_or
  status: resolved
  question_hash: 50d3c43d8cab9623
  resolved_at: 2026-04-28T19:25:00Z
  resolved_in_session: S319
  answer: "Real question (not FP) — Prime Builder asked whether to draft Bridge 2 in parallel with Bridge 1. Owner answered: 'begin drafting Bridge 2'. Both bridges (role-contract-clarifications-2026-04-28 and session-hygiene-gitignore-extensions-2026-04-28) were drafted in parallel, filed at -001 NEW, GO'd by Codex at -002, implemented at commit a0a83c23 (Bridge 1) and b95520c5 (Bridge 2), with -003 post-impl reports filed awaiting Codex VERIFIED."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T19:25:00Z (real question; resolved by owner direction in subsequent turns)"
- id: DECISION-0057
  asked_at: 2026-04-28T18:05:12.361592Z
  question: "eed  **Q1**: Do you want me to proceed with the deliberation search + Bridge 1 drafting now, or pause to revisit any of the confirmed dispositions?  **Q2**: After Brid"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: a63384ecb64e1e1b
  resolved_at: 2026-04-28T19:25:00Z
  resolved_in_session: S319
  answer: "Real two-part question (not FP); capture truncated mid-sentence. Q1 (proceed with deliberation search + Bridge 1 drafting?) — owner answered 'Yes'. Q2 (begin drafting Bridge 2 in parallel after Bridge 1 filed?) — owner answered 'begin drafting Bridge 2'. Both bridges then drafted, GO'd, and implemented per the parallel autonomy directive. Companion to DECISION-0058 (which captured Q2 as its own entry due to detector firing twice on the same prompt block)."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T19:25:00Z (real question; resolved by owner direction; truncated capture reduces searchability but content recovered from session transcript)"



- id: DECISION-0056
  asked_at: 2026-04-28T17:28:29.110575Z
  question: "lose S318 cleanly.  Awaiting owner direction."
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: 057065de6e8d25fb
  resolved_at: 2026-04-28T17:32:00Z
  resolved_in_session: S318
  answer: "doc-paragraph false positive; recurring class (same as DECISION-0029..0055). Captured fragment is Prime Builder closing summary line offering session-wrap option. Owner directed wrap-up after this prompt, organically resolving without archival need. Class-elimination tracked in GTKB-COMMAND-SURFACE."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T17:32:00Z (recurring FP class; bulk-resolution pattern from DECISION-0048)"
- id: DECISION-0055
  asked_at: 2026-04-28T17:25:18.270792Z
  question: "terminally closed. Standing by for owner direction on next focus."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: e115121e2e2ab07d
  resolved_at: 2026-04-28T17:30:00Z
  resolved_in_session: S318
  answer: "doc-paragraph false positive; recurring class (same as DECISION-0029..0054). Captured fragment is from Prime Builder S318 closing line announcing generator-hardening triad terminal closure ('terminally closed. Standing by for owner direction on next focus.'). Per fresh-session input semantics, the closing acknowledgement is a stimulus-response convention, not an owner question. Class-elimination tracked in GTKB-COMMAND-SURFACE."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T17:30:00Z (recurring FP class; bulk-resolution pattern from DECISION-0048)"
- id: DECISION-0054
  asked_at: 2026-04-28T16:55:18.101343Z
  question: "ded + VERIFIED).  **Standing by for Codex bridge cycle on `-003`, or for owner direction on the still-pendin"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 2de54dd422861a55
  resolved_at: 2026-04-28T17:00:00Z
  resolved_in_session: S318
  answer: "doc-paragraph false positive; recursive class (same as DECISION-0029..0053). Captured fragment is from Prime Builder S318 closing line ('Standing by for Codex bridge cycle on -003'). Per fresh-session input semantics, the closing acknowledgement is a stimulus-response convention, not an owner question. Class-elimination tracked in GTKB-COMMAND-SURFACE."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T17:00:00Z (recurring FP class; bulk-resolution pattern from DECISION-0048)"
- id: DECISION-0053
  asked_at: 2026-04-28T15:45:34.683808Z
  question: "-report.md)  ---  **Standing by for direction.** Per fresh-sessio"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 913e5a16493d895f
  resolved_at: 2026-04-28T15:50:00Z
  resolved_in_session: S318
  answer: "doc-paragraph false positive; recursive class (same as DECISION-0029..0050). Captured fragment is from Prime Builder S318 startup-disclosure closing line ('Standing by for direction.'). Per fresh-session input semantics, the closing acknowledgement is a stimulus-response convention, not an owner question. The 'standing_by_for' detector continues to fire on Prime Builder closing lines; class-elimination tracked in GTKB-COMMAND-SURFACE."
  notes: "Edited-by-prime-via-standing-pre-approval 2026-04-28T15:50:00Z (recurring FP class; bulk-resolution pattern from DECISION-0048)"
- id: DECISION-0014
  asked_at: 2026-04-26T05:54:24.554619Z
  question: "RESPONSE -001 NO-GO awaiting owner input on governance quest"
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: faddb88dab6f806c
  resolved_at: 2026-04-26T06:00:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; recursive class (same as DECISION-0009/0011/0012/0013). Captured fragment is from Prime Builder bridge-state table prose ('INCIDENT-RESPONSE -001 NO-GO awaiting owner input on governance question'). The 'awaiting_input' detector continues to fire on Prime Builder bridge-state descriptions. Owner directed one-by-one question presentation, organically converting the bridge-state into AskUserQuestion flow. Yet more motivating evidence for GTKB-COMMAND-SURFACE class-elimination."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T06:00:00Z (owner directed one-by-one question presentation)"
- id: DECISION-0013
  asked_at: 2026-04-26T02:38:08.123026Z
  question: "dge state captured; standing by for direction on which thread to"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 8567a2ace1d79bf3
  resolved_at: 2026-04-26T02:42:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; recursive class. Same class as DECISION-0009/0011/0012. The 'standing_by_for' detector continues to fire on Prime Builder closing acknowledgements. Owner directed return to GT-KB isolation work, organically consuming the offered standby. Yet more motivating evidence for GTKB-COMMAND-SURFACE class-elimination."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T02:42:00Z (owner asked about isolation-plan implementation proposals)"
- id: DECISION-0012
  asked_at: 2026-04-26T02:28:41.727244Z
  question: "separate artifacts  Standing by for direction. The bridge state ("
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 0b94f19641ed6eab
  resolved_at: 2026-04-26T02:35:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; recursive class. Captured fragment is from a Prime Builder closing offering response options ('as a single bridge proposal at scoping level, or as two separate artifacts. Standing by for direction.'). Owner answered organically with 'formulate it as an implementation proposal for a multi-phase project' — consuming the offered options without needing decision archival. Same class as DECISION-0009/0011; further motivating evidence for GTKB-COMMAND-SURFACE class-eliminating approach."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T02:35:00Z (owner directed multi-phase proposal drafting)"
- id: DECISION-0011
  asked_at: 2026-04-26T00:15:57.816184Z
  question: "e parallel threads. Standing by for direction on which to advance"
  detected_via: prose:awaiting_input
  status: resolved
  resolved_at: 2026-04-26T00:20:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; recursive class. Captured fragment is from a Prime Builder statement-form closing line ('Standing by for direction on which to advance first when you next prompt'), explicitly written to be statement-form rather than question-form for FP avoidance. The detector still fired because the literal substring 'direction' appeared. This is now motivating evidence for the GTKB-COMMAND-SURFACE program — heuristic prose detectors over unbounded natural language cannot be tightened to closure."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T00:20:00Z (owner directed architectural-plan drafting; bulk resolution of cascade)"
- id: DECISION-0010
  asked_at: 2026-04-25T23:59:00.434125Z
  question: "er, not a blocker.  Want me to also revise the Slice 1 NO-GO findings now, or focus this turn entirely on the command-surface design question?"
  detected_via: prose:offering_or_choice
  status: resolved
  resolved_at: 2026-04-26T00:20:00Z
  resolved_in_session: S310
  answer: "Real question (not FP), asked by Prime Builder. Resolved organically by the owner's subsequent prompts: focus is the architectural-plan / command-surface design question; WRAPUP Slice 1 NO-GO revision is deferred until the architecture lands (since it may reframe what Slice 1 contains). NOT a Phase 7 FP-guard candidate — this category is 'real questions whose answers came in subsequent turns'; the future ::question command would mark them as non-archival."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T00:20:00Z"
- id: DECISION-0009
  asked_at: 2026-04-25T23:49:08.054986Z
  question: "t demonstrated)\" / \"Awaiting your direction\"). I'll resolve it"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: eadba8052c13b38d
  resolved_at: 2026-04-26T00:20:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; recursive class. Fragment captured is from Prime Builder's ACKNOWLEDGEMENT of the DECISION-0008 resolution (i.e., the resolution-text of a prior FP became input to the same detector, generating the next FP). This is the canonical example of why the heuristic class cannot be tightened to closure: each FP entry's prose generates the next. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 + cited as motivating evidence for the GTKB-COMMAND-SURFACE program."
  notes: "Edited-by-prime-via-owner-direction 2026-04-26T00:20:00Z (bulk resolution of cascade)"
- id: DECISION-0008
  asked_at: 2026-04-25T23:42:57.713172Z
  question: "demonstrated)  ---  Awaiting your direction. Per the fresh-sess"
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: ba15636fe8652b1d
  resolved_at: 2026-04-25T23:55:00Z
  resolved_in_session: S310
  answer: "doc-paragraph false positive; same class as DECISION-0001/0002/0005. The fragments came from a session-startup ORIENT block table cell (\"61k tokens — read by section/limit, not in full (just demonstrated)\") followed by the standard fresh-session closing line (\"Awaiting your direction. Per the fresh-session input semantics...\"). Both are documentation prose, not owner questions. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 (FP-guard tightening) as further live test evidence — table-cell + standard-closing-phrase context are guard candidates."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T23:55:00Z (owner directed continuation to Slice 1 implementation; not a context-switch block)"
- id: DECISION-0001
  asked_at: 2026-04-25T17:34:16.235676Z
  question: "ose anti-patterns (\"want me to X or Y?\") and logs them. **"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: 816b3bc292f9eb72
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; the assistant was DESCRIBING the prose-anti-pattern detector in a session-end report, not asking an owner decision. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 (FP-guard tightening: quotation-aware + code-fence-aware) as live test evidence."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0002
  asked_at: 2026-04-25T18:05:52.219310Z
  question: "The detector saw `\"want me to X or Y?\"` as a literal stri"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: 4d507bca99868817
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; same class as DECISION-0001. The assistant was citing a backtick-quoted example of the regex pattern. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 as live test evidence; quotation/code-fence-aware guard will suppress this case."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0005
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "e | not yet filed — awaiting your direction |  ## Next move opt"
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: 3dbf274b10e088de
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; the assistant was rendering a markdown table cell describing the GTKB-STARTUP-ENHANCEMENTS row 9 status (\"awaiting your direction\"). Table-cell prose triggered the awaiting_input regex. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 — table-cell context is another guard candidate alongside quotation/code-fence."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0003
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "How aggressive should the rule-file consolidation be in Phase P4?"
  options:
    - "Full consolidation (Recommended)"
    - "Soft consolidation"
    - "Index-only"
  detected_via: ask_user_question
  status: resolved
  question_hash: 421a8dd70dc726b2
  resolved_at: 2026-04-25T18:22:47.070797Z
  answer: "User has answered your questions: \"How aggressive should the rule-file consolidation be in Phase P4?\"=\"Full consolidation (Recommended)\", \"Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?\"=\"P1 quick wins first (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0004
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?"
  options:
    - "P1 quick wins first (Recommended)"
    - "P3 six-primer registry first"
    - "P6 action tray first"
  detected_via: ask_user_question
  status: resolved
  question_hash: f7d7193d324160b8
  resolved_at: 2026-04-25T18:22:47.070797Z
  answer: "User has answered your questions: \"How aggressive should the rule-file consolidation be in Phase P4?\"=\"Full consolidation (Recommended)\", \"Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?\"=\"P1 quick wins first (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0006
  asked_at: 2026-04-25T23:37:21.713306Z
  question: "Should the scanner suite run automatically on Stop (within budget) or only on owner-triggered /wrap?"
  options:
    - "On-demand /wrap only (Recommended)"
    - "Hybrid: cheap scanners on Stop, expensive ones on /wrap"
    - "All on Stop (push timeout)"
  detected_via: ask_user_question
  status: resolved
  question_hash: 7f4836dcb60104ab
  resolved_at: 2026-04-25T23:37:21.713306Z
  answer: "User has answered your questions: \"Should the scanner suite run automatically on Stop (within budget) or only on owner-triggered /wrap?\"=\"On-demand /wrap only (Recommended)\", \"Where should the GTKB-WRAPUP-ENHANCEMENTS work item live relative to the existing GTKB-STARTUP-ENHANCEMENTS?\"=\"Separate item, coordinated phases (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0007
  asked_at: 2026-04-25T23:37:21.713306Z
  question: "Where should the GTKB-WRAPUP-ENHANCEMENTS work item live relative to the existing GTKB-STARTUP-ENHANCEMENTS?"
  options:
    - "Separate item, coordinated phases (Recommended)"
    - "Merge into GTKB-STARTUP-ENHANCEMENTS as P9-P13"
    - "File as upstream-routed in groundtruth-kb"
  detected_via: ask_user_question
  status: resolved
  question_hash: 74bc648053632a90
  resolved_at: 2026-04-25T23:37:21.713306Z
  answer: "User has answered your questions: \"Should the scanner suite run automatically on Stop (within budget) or only on owner-triggered /wrap?\"=\"On-demand /wrap only (Recommended)\", \"Where should the GTKB-WRAPUP-ENHANCEMENTS work item live relative to the existing GTKB-STARTUP-ENHANCEMENTS?\"=\"Separate item, coordinated phases (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0015
  asked_at: 2026-04-26T06:24:19.672743Z
  question: "How should fast-path mitigation actions (rollback, scale-up, traffic shift, feature flag toggle) interact with the bridge protocol during a SEV-1 at 2 AM? Codex flagged the original 'bypasses bridge review' framing as a material governance change. Three coherent models exist:"
  options:
    - "Pre-reviewed registry + post-execution review (Recommended)"
    - "Explicit bypass via GOV/ADR"
    - "No fast-path; bridge protocol always"
  detected_via: ask_user_question
  status: resolved
  question_hash: ff2802c2b7023b7b
  resolved_at: 2026-04-26T06:24:19.672743Z
  answer: "User has answered your questions: \"How should fast-path mitigation actions (rollback, scale-up, traffic shift, feature flag toggle) interact with the bridge protocol during a SEV-1 at 2 AM? Codex flagged the original 'bypasses bridge review' framing as a material governance change. Three coherent models exist:\"=\"Pre-reviewed registry + post-execution review (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0016
  asked_at: 2026-04-26T06:24:19.672743Z
  question: "Where should the GTKB-INCIDENT-RESPONSE framework artifacts ship? This shapes who else benefits and how the documents are scoped. The framework is the SRE/ITIL 8-phase model SPEC, the ADR, severity schema, fast-path mitigation registry, postmortem skill, etc."
  options:
    - "Mixed: framework upstream, documents Agent Red-local (Recommended)"
    - "All upstream to groundtruth-kb"
    - "All Agent Red-local"
  detected_via: ask_user_question
  status: resolved
  question_hash: 19e09ff2ea324ad9
  resolved_at: 2026-04-26T06:24:19.672743Z
  answer: "User has answered your questions: \"Where should the GTKB-INCIDENT-RESPONSE framework artifacts ship? This shapes who else benefits and how the documents are scoped. The framework is the SRE/ITIL 8-phase model SPEC, the ADR, severity schema, fast-path mitigation registry, postmortem skill, etc.\"=\"All upstream to groundtruth-kb\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0017
  asked_at: 2026-04-26T06:24:19.672743Z
  question: "What should Phase IR-1 contain? The original proposal had six deliverables (framework SPEC, ADR, CTO 1-page, LinkedIn article concept, backlog placeholders, DELIB). Codex's [P2] finding flagged that Agent Red ALREADY has incident infrastructure (cosmos schema, incidents repository, public status API, tests, GTKB-DORA-001 dashboard incidents) — these need to be mapped to the new framework before the framework lands, otherwise parallel concepts diverge."
  options:
    - "IR-0 inventory first, then IR-1 framework (Recommended)"
    - "Single combined Phase IR-1 (inventory + framework + docs)"
    - "IR-1 framework + IR-2 inventory (defer)"
  detected_via: ask_user_question
  status: resolved
  question_hash: 9dd9c76f44c738fc
  resolved_at: 2026-04-26T06:24:19.672743Z
  answer: "User has answered your questions: \"What should Phase IR-1 contain? The original proposal had six deliverables (framework SPEC, ADR, CTO 1-page, LinkedIn article concept, backlog placeholders, DELIB). Codex's [P2] finding flagged that Agent Red ALREADY has incident infrastructure (cosmos schema, incidents repository, public status API, tests, GTKB-DORA-001 dashboard incidents) — these need to be mapped to the new framework before the framework lands, otherwise parallel concepts diverge.\"=\"IR-0 inventory first, then IR-1 framework (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0018
  asked_at: 2026-04-26T06:24:19.672743Z
  question: "Which capabilities ship in Phase IR-2 to make the framework demonstrable end-to-end? The original proposed five: IR-CS-1 severity classification spec, IR-CS-2 ::incident <id> command, IR-CS-3 postmortem auto-draft skill, IR-CS-4 fast-path mitigation registry (now pre-reviewed per the earlier governance answer), IR-CS-5 status-page draft generator (::incident-update)."
  options:
    - "All five as proposed (Recommended)"
    - "Trim to three: severity + ::incident + postmortem"
    - "Expand: add ::mitigate-rollback as IR-CS-6"
  detected_via: ask_user_question
  status: resolved
  question_hash: 4e101e69cb070a89
  resolved_at: 2026-04-26T06:24:19.672743Z
  answer: "User has answered your questions: \"Which capabilities ship in Phase IR-2 to make the framework demonstrable end-to-end? The original proposed five: IR-CS-1 severity classification spec, IR-CS-2 ::incident <id> command, IR-CS-3 postmortem auto-draft skill, IR-CS-4 fast-path mitigation registry (now pre-reviewed per the earlier governance answer), IR-CS-5 status-page draft generator (::incident-update).\"=\"All five as proposed (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0019
  asked_at: 2026-04-26T06:24:19.672743Z
  question: "How should incident-response commands integrate with the command-surface architecture? The relevant commands are ::incident, ::mitigate-*, ::postmortem, ::incident-update, ::incident-close."
  options:
    - "Single registry under GTKB-COMMAND-SURFACE (Recommended)"
    - "Parallel incident-specific dispatcher"
    - "Hybrid: shared registry + dedicated incident-aware hook layer"
  detected_via: ask_user_question
  status: resolved
  question_hash: 978ce5ed30429c1a
  resolved_at: 2026-04-26T06:24:19.672743Z
  answer: "User has answered your questions: \"How should incident-response commands integrate with the command-surface architecture? The relevant commands are ::incident, ::mitigate-*, ::postmortem, ::incident-update, ::incident-close.\"=\"Single registry under GTKB-COMMAND-SURFACE (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0020
  asked_at: 2026-04-26T17:41:04.744095Z
  question: "Which recovery path should I execute?"
  options:
    - "Option A: .recover from live (Recommended)"
    - "Option B: Restore April 11 backup + replay"
    - "Option C: Investigate further before deciding"
  detected_via: ask_user_question
  status: resolved
  question_hash: c2cce3ef927f4d44
  resolved_at: 2026-04-26T17:41:04.744095Z
  answer: "User has answered your questions: \"Which recovery path should I execute?\"=\"Option A: .recover from live (Recommended)\", \"How should I handle the OneDrive sync issue (root cause)?\"=\"Stop sync of GT-KB folder now (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0021
  asked_at: 2026-04-26T17:41:04.744095Z
  question: "How should I handle the OneDrive sync issue (root cause)?"
  options:
    - "Stop sync of GT-KB folder now (Recommended)"
    - "Move GT-KB out of OneDrive entirely"
    - "Defer — I'll handle OneDrive separately"
  detected_via: ask_user_question
  status: resolved
  question_hash: 0060cf7647e54adb
  resolved_at: 2026-04-26T17:41:04.744095Z
  answer: "User has answered your questions: \"Which recovery path should I execute?\"=\"Option A: .recover from live (Recommended)\", \"How should I handle the OneDrive sync issue (root cause)?\"=\"Stop sync of GT-KB folder now (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0022
  asked_at: 2026-04-26T17:41:04.744095Z
  question: "How should I handle the atomic-replace step (final commit of recovery)?"
  options:
    - "Pause Drive in system tray, then I'll swap (Recommended)"
    - "I'll kill GoogleDriveFS.exe processes briefly, then swap"
    - "Swap now without pausing Drive (risky)"
    - "Hold — let me inspect recovered.db first"
  detected_via: ask_user_question
  status: resolved
  question_hash: 46ee8950bb4ee82d
  resolved_at: 2026-04-26T17:41:04.744095Z
  answer: "User has answered your questions: \"How should I handle the atomic-replace step (final commit of recovery)?\"=\"Pause Drive in system tray, then I'll swap (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0023
  asked_at: 2026-04-26T18:00:22.154791Z
  question: "Which permanent Google Drive exclusion strategy do you want?"
  options:
    - "Add .driveignore for SQLite triple (Recommended)"
    - "Drive UI per-file exclusion"
    - "Move groundtruth.db outside GT-KB folder"
    - "Build snapshot+upload daemon"
  detected_via: ask_user_question
  status: resolved
  question_hash: 89feaa37246ba2cd
  resolved_at: 2026-04-26T18:00:22.154791Z
  answer: "User has answered your questions: \"Which permanent Google Drive exclusion strategy do you want?\"=\"Add .driveignore for SQLite triple (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0024
  asked_at: 2026-04-26T18:14:03.420521Z
  question: "DORA-001b -007 §7.1 — Confirm the 3-source authority split shape?"
  options:
    - "A primary, C reconcile, B deferred (Recommended)"
    - "A + C only, drop B-deferred plan"
    - "Flat single-source A only"
    - "Different shape — explain"
  detected_via: ask_user_question
  status: resolved
  question_hash: 10b1d3f81dbc0e28
  resolved_at: 2026-04-26T18:14:03.420521Z
  answer: "User has answered your questions: \"DORA-001b -007 §7.1 — Confirm the 3-source authority split shape?\"=\"A primary, C reconcile, B deferred (Recommended)\", \"DORA-001b -007 §7.2 — Where does Source B (GH Actions out-of-band detection) live?\"=\"GTKB-DORA-001c (Recommended)\", \"DORA-001b -007 §7.3 — Track 1 GOV-17 acknowledgement (modifies scripts/deploy_pipeline.py)?\"=\"Acknowledged — Track 1 may modify deploy_pipeline.py\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0025
  asked_at: 2026-04-26T18:14:03.420521Z
  question: "DORA-001b -007 §7.2 — Where does Source B (GH Actions out-of-band detection) live?"
  options:
    - "GTKB-DORA-001c (Recommended)"
    - "Defer indefinitely (no work item)"
    - "Different work item home"
  detected_via: ask_user_question
  status: resolved
  question_hash: 06b50753fe9a0c91
  resolved_at: 2026-04-26T18:14:03.420521Z
  answer: "User has answered your questions: \"DORA-001b -007 §7.1 — Confirm the 3-source authority split shape?\"=\"A primary, C reconcile, B deferred (Recommended)\", \"DORA-001b -007 §7.2 — Where does Source B (GH Actions out-of-band detection) live?\"=\"GTKB-DORA-001c (Recommended)\", \"DORA-001b -007 §7.3 — Track 1 GOV-17 acknowledgement (modifies scripts/deploy_pipeline.py)?\"=\"Acknowledged — Track 1 may modify deploy_pipeline.py\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0026
  asked_at: 2026-04-26T18:14:03.420521Z
  question: "DORA-001b -007 §7.3 — Track 1 GOV-17 acknowledgement (modifies scripts/deploy_pipeline.py)?"
  options:
    - "Acknowledged — Track 1 may modify deploy_pipeline.py"
    - "Hold — want to see Track 1 impl proposal first"
    - "NO — find approach that doesn't modify deploy_pipeline.py"
  detected_via: ask_user_question
  status: resolved
  question_hash: ecd2f21d2b408b15
  resolved_at: 2026-04-26T18:14:03.420521Z
  answer: "User has answered your questions: \"DORA-001b -007 §7.1 — Confirm the 3-source authority split shape?\"=\"A primary, C reconcile, B deferred (Recommended)\", \"DORA-001b -007 §7.2 — Where does Source B (GH Actions out-of-band detection) live?\"=\"GTKB-DORA-001c (Recommended)\", \"DORA-001b -007 §7.3 — Track 1 GOV-17 acknowledgement (modifies scripts/deploy_pipeline.py)?\"=\"Acknowledged — Track 1 may modify deploy_pipeline.py\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0027
  asked_at: 2026-04-26T18:14:03.420521Z
  question: "ISOLATION-016 §3.3 — Where should rehearsal sub-scripts write their preview outputs?"
  options:
    - "Separate sandbox dir, never becomes target child root (Recommended)"
    - "Target child root, becomes part of eventual real root"
    - "Different approach — explain"
  detected_via: ask_user_question
  status: resolved
  question_hash: 07e4e32555595105
  resolved_at: 2026-04-26T18:14:03.420521Z
  answer: "User has answered your questions: \"ISOLATION-016 §3.3 — Where should rehearsal sub-scripts write their preview outputs?\"=\"Separate sandbox dir, never becomes target child root (Recommended)\", \"ISOLATION-016 §3.5 — Git strategy for the target child root?\"=\"Clone with history filter (Agent Red commits only)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0028
  asked_at: 2026-04-26T18:14:03.420521Z
  question: "ISOLATION-016 §3.5 — Git strategy for the target child root?"
  options:
    - "Fresh repo (no history)"
    - "Clone with history filter (Agent Red commits only)"
    - "Clean worktree (shares history, separate working tree)"
    - "Different approach — explain"
  detected_via: ask_user_question
  status: resolved
  question_hash: a9c8b642ee3aac45
  resolved_at: 2026-04-26T18:14:03.420521Z
  answer: "User has answered your questions: \"ISOLATION-016 §3.3 — Where should rehearsal sub-scripts write their preview outputs?\"=\"Separate sandbox dir, never becomes target child root (Recommended)\", \"ISOLATION-016 §3.5 — Git strategy for the target child root?\"=\"Clone with history filter (Agent Red commits only)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0041
  asked_at: 2026-04-27T14:47:52.141335Z
  question: "Approve Phase 2 hibernation execution against subscription 4dce2122 / Agent-Red RG?"
  options:
    - "Execute 2.1 + 2.2 (Recommended)"
    - "Execute 2.1 only"
    - "Cancel hibernation"
  detected_via: ask_user_question
  status: resolved
  question_hash: 82b8b2f0d5fbf02d
  resolved_at: 2026-04-27T14:47:52.141335Z
  answer: "User has answered your questions: \"Approve Phase 2 hibernation execution against subscription 4dce2122 / Agent-Red RG?\"=\"Execute 2.1 + 2.2 (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0046
  asked_at: 2026-04-28T02:51:12.397457Z
  question: "Which priority should lead this session? (Top-3 surfaced from work_list, bridge state, and uncommitted-tree triage; per session-self-initialization principle DELIB-0840.)"
  options:
    - "Commit untracked feedback/* + triage drift (Recommended)"
    - "Resume isolation chain: file row 18 GH-CROSS-REPO impl"
    - "Bulk-resolve the 12 pending-decision FPs"
    - "Different direction — I will specify"
  detected_via: ask_user_question
  status: resolved
  question_hash: 638b7beb5770a96c
  resolved_at: 2026-04-28T02:51:12.397457Z
  answer: "User has answered your questions: \"Which priority should lead this session? (Top-3 surfaced from work_list, bridge state, and uncommitted-tree triage; per session-self-initialization principle DELIB-0840.)\"=\"Commit untracked feedback/* + triage drift (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0048
  asked_at: 2026-04-28T02:57:56.927026Z
  question: "How would you like to handle the 17 pending owner decisions while we wait for Codex review on the working-tree-triage bridge proposal?"
  options:
    - "Bulk-clear FPs + I confirm DECISION-0044 (Recommended)"
    - "Trigger Codex bridge review now"
    - "Leave the queue; pick a different task"
    - "Resolve DECISION-0044 only; leave FPs for batch cleanup later"
  detected_via: ask_user_question
  status: resolved
  question_hash: dc5b4ed393bf6705
  resolved_at: 2026-04-28T02:57:56.927026Z
  answer: "User has answered your questions: \"How would you like to handle the 17 pending owner decisions while we wait for Codex review on the working-tree-triage bridge proposal?\"=\"Bulk-clear FPs + I confirm DECISION-0044 (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0049
  asked_at: 2026-04-28T02:57:56.927026Z
  question: "Confirm the DECISION-0044 resolution. The S316 implementation chose option (a) empty/minimal placeholders, structurally enforced by Codex GO condition 2 (no GT-KB platform content imported). Does that match your intent?"
  options:
    - "Confirm (a) — record as resolved (Recommended)"
    - "Reverse to (b) — import filtered GT-KB starter selection"
    - "Hybrid — keep (a) for now, plan a curated starter for later"
    - "Different framing entirely — I will explain"
  detected_via: ask_user_question
  status: resolved
  question_hash: 0d626e7983e08d1b
  resolved_at: 2026-04-28T02:57:56.927026Z
  answer: "User has answered your questions: \"Confirm the DECISION-0044 resolution. The S316 implementation chose option (a) empty/minimal placeholders, structurally enforced by Codex GO condition 2 (no GT-KB platform content imported). Does that match your intent?\"=\"Confirm (a) — record as resolved (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0044
  asked_at: 2026-04-27T23:52:20.367859Z
  question: "de/` and `.codex/`, should I (a) start with empty/minimal directories and let you populate the agent/skill/plugin selections, or (b) propose a starter selection drawn from the GT-KB-level configs filtered to app-relevant items?  I'll wait on these"
  detected_via: prose:should_i_or
  status: resolved
  question_hash: 2eb91454e4a8c959
  resolved_at: 2026-04-28T02:58:26.706391Z
  answer: "option (a) chosen during S316 sub-slice 1 per Codex GO condition 2 (minimization principle); starter selection (b) structurally rejected by DCL-APP-ROOT-MINIMIZATION-001."
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0029
  asked_at: 2026-04-26T19:35:00.271540Z
  question: "s green throughout. Standing by for owner decision on poller v1 scope"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 61e91be58bdc2678
  resolved_at: 2026-04-28T02:58:42.574199Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0030
  asked_at: 2026-04-27T00:28:51.000753Z
  question: "ap if you'd prefer. Standing by for direction. `─────────────────"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: b10806190aa5e6a3
  resolved_at: 2026-04-28T02:58:42.574216Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0031
  asked_at: 2026-04-27T01:11:44.187119Z
  question: "total in S311) ```  Standing by for Codex VERIFIED on Slice 3 -005, or for your direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 3bde1f936473aca8
  resolved_at: 2026-04-28T02:58:42.574219Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0032
  asked_at: 2026-04-27T01:21:52.614673Z
  question: "re ready. Otherwise standing by for next direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: a9209bc27fd2a2ae
  resolved_at: 2026-04-28T02:58:42.574221Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0033
  asked_at: 2026-04-27T01:24:31.046057Z
  question: "ant to address it.  Standing by for `/kb-session-wrap S311` or other direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 675e6ee971a3ef76
  resolved_at: 2026-04-28T02:58:42.574223Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0034
  asked_at: 2026-04-27T01:28:40.561671Z
  question: "5 (handoff) remain. Want me to skip the harvest and continue, or construct the approval packet?"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: 8a238611d3a8e62b
  resolved_at: 2026-04-28T02:58:42.574224Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0035
  asked_at: 2026-04-27T01:40:52.091559Z
  question: "tart stimulus only. Awaiting your direction (focus choice from"
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: 58662ebc32207825
  resolved_at: 2026-04-28T02:58:42.574226Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0036
  asked_at: 2026-04-27T03:49:12.435752Z
  question: "──────────────`  ## Standing By for Insertion Approval  Per `.claude/rules"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 302c6541b50390f2
  resolved_at: 2026-04-28T02:58:42.574227Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0037
  asked_at: 2026-04-27T04:29:22.544912Z
  question: "──────────────`  ## Standing By for Approval  **Approve insertio"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 98750599ecd09cd6
  resolved_at: 2026-04-28T02:58:42.574229Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0038
  asked_at: 2026-04-27T06:42:35.876853Z
  question: "e resuming Wave 2.  Standing by for direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: c1d89c2c4e056ced
  resolved_at: 2026-04-28T02:58:42.574231Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0039
  asked_at: 2026-04-27T06:51:22.853708Z
  question: "d like to surface.  Standing by for direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 3c287c647e426cbe
  resolved_at: 2026-04-28T02:58:42.574233Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0040
  asked_at: 2026-04-27T08:37:18.827636Z
  question: "─────────────────`  Standing by for direction."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 20c3584dccf20edd
  resolved_at: 2026-04-28T02:58:42.574234Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0042
  asked_at: 2026-04-27T15:24:04.713902Z
  question: "prised me before  **Standing by for whatever's next** — another bridge scan when you have direction, or a different pri"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 907710153e53864f
  resolved_at: 2026-04-28T02:58:42.574236Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0043
  asked_at: 2026-04-27T18:29:58.141516Z
  question: "no implementation.  Standing by for direction or session wrap."
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 4373a198ddd92d82
  resolved_at: 2026-04-28T02:58:42.574237Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0045
  asked_at: 2026-04-28T02:15:37.359759Z
  question: "store integrity  **Standing by for your direction.** The deletion-saf"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: eb3eba454aa1d1de
  resolved_at: 2026-04-28T02:58:42.574239Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0047
  asked_at: 2026-04-28T02:51:12.397457Z
  question: "age fragments like \"standing by for direction\" — and previously-resolved DECISION-0008/0009/0011/0013 showed each FP's resolution-text became input to the next FP. Thi"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 50a6bf31ae4f8f32
  resolved_at: 2026-04-28T02:58:42.574240Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0050
  asked_at: 2026-04-28T02:57:56.927026Z
  question: "e FP class to you (\"standing by for direction\" was a quoted examp"
  detected_via: prose:standing_by_for
  status: resolved
  question_hash: 392e3762d1d0dcfe
  resolved_at: 2026-04-28T02:58:42.574242Z
  answer: "owner cleared without specific answer"
  notes: "auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable"
- id: DECISION-0051
  asked_at: 2026-04-28T04:26:26.098049Z
  question: "Per `feedback_explicit_destructive_action_authorization.md`, I need explicit authorization before deleting the nested `E:\\GT-KB\\GT-KB\\` directory (created by my verification commands due to a path-handling bug in `session_self_initialization.py`). The directory contains 4 auto-regenerable dashboard output files (~176K total): `GT-KB/docs/gtkb-dashboard/dashboard-data.json`, `GT-KB/docs/gtkb-dashboard/session-startup-report.md`, `GT-KB/docs/gtkb-dashboard/session-wrapup-report.md`, `GT-KB/memory/gtkb-dashboard-history.json`. The same 4 files exist correctly at `E:\\GT-KB\\docs/...` and `E:\\GT-KB\\memory/...` (Commit 6 of S317 tracked them). Codex requires this directory be removed before VERIFIED. How should I proceed?"
  options:
    - "APPROVE: delete `E:\\GT-KB\\GT-KB\\` recursively (Recommended)"
    - "Add `GT-KB/` to .gitignore (no deletion)"
    - "I will delete it myself; you file REVISED-1 after"
    - "Different approach — I will specify"
  detected_via: ask_user_question
  status: resolved
  question_hash: 3bf126423c32aec1
  resolved_at: 2026-04-28T04:26:26.098049Z
  answer: "User has answered your questions: \"Per `feedback_explicit_destructive_action_authorization.md`, I need explicit authorization before deleting the nested `E:\\GT-KB\\GT-KB\\` directory (created by my verification commands due to a path-handling bug in `session_self_initialization.py`). The directory contains 4 auto-regenerable dashboard output files (~176K total): `GT-KB/docs/gtkb-dashboard/dashboard-data.json`, `GT-KB/docs/gtkb-dashboard/session-startup-report.md`, `GT-KB/docs/gtkb-dashboard/session-wrapup-report.md`, `GT-KB/memory/gtkb-dashboard-history.json`. The same 4 files exist correctly at `E:\\GT-KB\\docs/...` and `E:\\GT-KB\\memory/...` (Commit 6 of S317 tracked them). Codex requires this directory be removed before VERIFIED. How should I proceed?\"=\"APPROVE: delete `E:\\GT-KB\\GT-KB\\` recursively (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0052
  asked_at: 2026-04-28T14:41:26.074384Z
  question: "Per Codex GO -002 condition 2 (telemetry-churn-policy thread), I need to run `git rm --cached` to remove 2 files from git tracking while preserving them on disk. The destructive-gate hook is blocking the bash form. The exact operation: `git rm --cached docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json` — removes from git index only, files stay on disk for runtime regen. Both files are auto-regen telemetry; no data loss. How should I proceed?"
  options:
    - "APPROVE: run `git rm --cached` on the 2 named files (Recommended)"
    - "I will run it myself; you proceed after I confirm"
    - "Different approach — use Python equivalent"
    - "Defer this thread; revise to a different approach"
  detected_via: ask_user_question
  status: resolved
  question_hash: 3baf195b98556af4
  resolved_at: 2026-04-28T14:41:26.074384Z
  answer: "User has answered your questions: \"Per Codex GO -002 condition 2 (telemetry-churn-policy thread), I need to run `git rm --cached` to remove 2 files from git tracking while preserving them on disk. The destructive-gate hook is blocking the bash form. The exact operation: `git rm --cached docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json` — removes from git index only, files stay on disk for runtime regen. Both files are auto-regen telemetry; no data loss. How should I proceed?\"=\"APPROVE: run `git rm --cached` on the 2 named files (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""

## History

(none)
