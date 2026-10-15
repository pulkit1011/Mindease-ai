# PROJECT REPORT

## Title Page
**MindEase AI: An AI-Powered Mental Wellness Assistant for Youth**
Submitted in partial fulfilment of the requirements for the degree of **[Bachelor of Technology in Computer Science and Engineering]**
By: **[Student name]** · Roll/Enrolment No.: **[number]**
Under the guidance of: **[Faculty supervisor name, designation]**
**[Department] · [University / Institution name] · [Academic year]**

## Certificate (TEMPLATE: to be completed and signed by the institution)
> This section is a template only. It must be issued, approved and signed by the supervisor and department. Nothing here has been approved.

This is to certify that the project entitled "MindEase AI" is a bonafide work carried out by **[student name]** under my supervision.
Supervisor signature: ______________ Date: ________  Head of Department signature: ______________ Date: ________

## Declaration (TEMPLATE: to be signed by the student)
I declare that this report is my own work, that sources are cited, and that no results or approvals have been fabricated.
Signature: ______________ Date: ________

## Acknowledgment (TEMPLATE)
I thank **[supervisor]**, **[department]**, and **[others]** for guidance and support. *(Edit to reflect real contributions.)*

## Abstract and Keywords
See `concept_notes.md` section 2 (copy the final abstract here). **Keywords:** mental wellness, SDG 3, chatbot, mood tracking, Streamlit, SQLite, responsible AI.

## Table of Contents
1 Introduction · 2 Literature/Background · 3 Existing vs Proposed System · 4 Requirements · 5 System Design · 6 Database Design · 7 Implementation · 8 Screenshots · 9 Testing · 10 Results and Discussion · 11 Limitations · 12 Future Enhancements · 13 Conclusion · 14 References

## 1. Introduction and Problem Definition
Youth often experience stress and anxiety with limited accessible support. The project builds an AI-assisted wellness web application for check-ins and general guidance, with safety, privacy and honesty as design priorities. Problem statement: "Lack of mental health support among youth results in stress and anxiety. This project aims to create an AI-powered chatbot for mental wellness check-ins and guidance." (Full text: `concept_notes.md` sections 3-9.)

## 2. Literature / Background Review
Add a short review after reading the sources in `references.md` (WHO adolescent mental health fact sheet and 2022 World Mental Health Report; UN SDG 3; Tele-MANAS; NIMHANS National Mental Health Survey 2015-16). **Write only what those sources actually say, with page/section and access date.** Also review responsible-AI guidance for health chatbots. *(This section is intentionally left for you to complete from real reading; no figures are fabricated here.)*

## 3. Existing versus Proposed System
| Existing | Proposed (this project) |
|---|---|
| Counselling cells, helplines, apps, general chatbots, journals (limits in `concept_notes.md` §11) | One local app with check-ins, charts, self-care, constrained AI chat, independent safety layer, honest fallback, editable support list, export/delete |

## 4. Requirements Analysis
Functional FR1-FR13 and non-functional requirements: `concept_notes.md` §13-14.

## 5. System Design and Architecture
Architecture and data-flow diagrams (Mermaid): `concept_notes.md` §16-17. Layering: Streamlit pages → services → SQLite / JSON / optional API.

## 6. Database Design
Tables `wellness_entries` and `activity_completions` with CHECK constraints, versioned migrations (`PRAGMA user_version`), hard deletion. Details: `concept_notes.md` §20 and `database.py`.

## 7. Implementation Details
Language Python (3.12 used for development). Files and roles are listed in `README.md`. Key points: parameterised SQL; validation collecting all errors; safety check before the model; AI client with timeout, one retry, error classification, secret redaction; offline fallback with label; analytics via pandas; Plotly charts imported lazily; CSV export with formula-injection protection; fictional demo data flagged by `is_demo`. About 1,900 lines of Python including tests.

## 8. Screenshots (PLACEHOLDERS: replace with real screenshots)
No screenshots were captured during the build because the Streamlit UI could not be launched in the offline build environment. Insert your own after running `streamlit run app.py`:
- Figure 1: Home page · Figure 2: Wellness check-in with reflection · Figure 3: AI chat showing fallback label · Figure 4: Safety response · Figure 5: Mood tracker charts (demo data flagged) · Figure 6: Self-care page · Figure 7: Dashboard · Figure 8: Help and support.

## 9. Testing
**Strategy:** unit tests for logic; fake clients for the AI service; temporary databases; page smoke execution; manual UI checklist (`README.md`).

**Environment actually used for the results below:** Python 3.12.3, no internet. `pytest`, `streamlit` and `plotly` were **not installable**, so:
- The tests (written in pytest style) were run with a small stand-in runner that supports `tmp_path`, `monkeypatch`, `pytest.raises` and `parametrize`.
- The Streamlit pages were executed against a hand-written stub of the Streamlit and Plotly APIs, with an empty database, with fictional demo data, and with all buttons forced to "clicked".

**Results observed (honest summary):**
| Test file | Cases | Result |
|---|---|---|
| test_database.py | 11 | all passed |
| test_wellness.py | 31 (incl. parametrised) | all passed |
| test_safety.py | 30 (incl. parametrised) | all passed |
| test_analytics.py | 6 | all passed |
| test_ai_service.py | 15 | all passed |
| **Total** | **93** | **93 passed, 0 failed (stand-in runner)** |

Page smoke runs: all 8 scripts (Home + 7 pages) ran without exceptions in all three scenarios.

**Not run:** the real `pytest` command; the real Streamlit server and browser rendering; real Plotly figure rendering; any live call to an AI API; any test with real users. **Action for you:** run `pytest -q` and `streamlit run app.py`, then paste your real output here and add screenshots.

## 10. Results and Discussion
Observed evidence is limited to the tests above: validation boundaries, CRUD, empty-data handling, CSV export, safety true/false positives on the defined phrase lists, AI error handling and absence of secret leakage in logs/replies for the tested cases. These show the code behaves as designed for those cases. They **do not** show clinical effectiveness, safety coverage of real-world language, usability, or user satisfaction. No user study was performed.

## 11. Limitations
Not clinically validated; keyword safety checks miss/over-trigger; English only; no authentication or encryption; local single-user database; unverified support contacts; no real-user evaluation; UI not exercised in a real browser during build; AI replies depend on an external model and can still be imperfect.

## 12. Future Enhancements
Authentication and encrypted per-user storage; privacy notice and consent; verified resource maintenance; regional languages; clinician-reviewed safety improvements; accessibility audit; ethics-approved pilot; optional opt-in chat history with deletion.

## 13. Conclusion
A working prototype of an honest, safety-aware youth wellness assistant was implemented and unit-tested in a limited environment. Its real-world value and safety remain to be evaluated with proper oversight.

## 14. References
See `references.md` (verify all links and add exact citations before submission).
