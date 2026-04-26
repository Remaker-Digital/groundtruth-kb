# Pending Owner Decisions

This file is owned by .claude/hooks/owner-decision-tracker.py.

---

## Pending

(none)

## Resolved

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

## History

(none)
