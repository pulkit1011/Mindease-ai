# Presentation Outline: MindEase AI (12 slides, about 10-12 minutes)

> **Actual vs proposed:** results marked *Actual* come from the automated tests and demo run; everything marked *Proposed* has not been done.

## Slide 1: Title and team
- MindEase AI: An AI-Powered Mental Wellness Assistant for Youth · SDG 3
- [Your name, roll no.] · [Supervisor] · [Institution, department, date]
**Notes:** Introduce yourself and the one-line idea: a private check-in and chat tool with safety built in.

## Slide 2: Problem statement
- Youth face stress and anxiety; support is not always reachable, affordable or comfortable to ask for.
- "Lack of mental health support among youth results in stress and anxiety."
**Notes:** Keep it factual. If you quote WHO figures, state the source and year after verifying them (see references).

## Slide 3: Motivation and SDG 3
- SDG 3: Good health and well-being; Target 3.4 mental health.
- Our contribution: early self-reflection and signposting, not treatment.
**Notes:** Be explicit that the app supports awareness and does not claim to improve health outcomes.

## Slide 4: Users and existing alternatives
- Users: college students and young adults.
- Alternatives: counselling cells, helplines, meditation apps, general chatbots, journals, each with limits (hours, cost, privacy, safety).
**Notes:** Position the app as a complement.

## Slide 5: Proposed solution and value proposition
- Check-ins · AI chat · mood trends · self-care · support page.
- UVP: "A calm, private place to check in with yourself, with honest limits and a clear path to real help."
**Notes:** Emphasise the three differentiators: safety layer, honest fallback labelling, privacy rules.

## Slide 6: Lean Canvas summary
- Problems · Segment · UVP · Solution · Channels · Revenue hypotheses · Costs · Metrics · Unfair advantage (honest: little yet).
- *Proposed:* nothing validated yet; pilot plan ready.
**Notes:** Say clearly the canvas is a hypothesis.

## Slide 7: Architecture and technology
- Diagram: Streamlit pages → services → SQLite; AI service → safety first → model or fallback.
- Stack: Python, Streamlit, SQLite, pandas, Plotly, optional Anthropic API, pytest.
**Notes:** Explain why each choice: free, simple, beginner-friendly.

## Slide 8: Features and demonstration workflow
- Demo order: Home → check-in → reflection → mood tracker (demo data, flagged) → self-care breathing → chat (ordinary message, fallback label) → chat (safety message) → dashboard → CSV export/delete.
**Notes:** Do the safety demo calmly; use a test phrase and explain it is a demonstration.

## Slide 9: Testing, safety and privacy
- *Actual:* 93 automated test cases passed (database, validation, analytics, safety, AI error handling); page smoke runs with a Streamlit stand-in.
- *Actual:* safety runs before the model and works offline; chat not stored; notes/moods never sent to AI.
- *Limits:* keyword safety check is not clinically validated; full UI run on real Streamlit should be shown live.
**Notes:** Report honestly which tests ran where.

## Slide 10: Expected impact and limitations
- *Proposed impact:* greater self-awareness and quicker routes to help, to be tested in a pilot.
- Limitations: not diagnostic; no accounts/encryption; no real-user evaluation; unverified support numbers marked as such.
**Notes:** Do not claim measured benefits.

## Slide 11: Future scope
- Authentication and encrypted storage; regional languages; clinician-reviewed safety; verified resource updates; pilot with ethics approval; accessibility audit.
**Notes:** Prioritise: safety review and privacy first.

## Slide 12: Conclusion and Q&A
- Working prototype demonstrating responsible AI design for youth wellness.
- Thank you · Questions?
**Notes:** Have `viva_questions.md` ready; be ready to open and explain `safety_service.py` and `ai_service.py`.
