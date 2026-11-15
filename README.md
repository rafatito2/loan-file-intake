# Loan File Intake from WhatsApp

Final Project for CEN 4010 (Principles of Software Engineering, FAU, Fall 2026).

A payroll-deduction lender in Panama receives loan application documents as WhatsApp photos over several days. Today a credit assistant forwards each photo by hand. This system receives the documents directly, files a document only when its cédula (national ID) number matches an open case, holds the rest for the assistant, checks the file against fixed rules, and drafts the follow-up message for the assistant to approve.

The AI model only extracts data and drafts text. Flags come from deterministic rules. No real message is sent and all example data is synthetic.

## Status

Design is complete (Solution Design Report, Assignment 2). The build follows the increments in Section 8 of that report.

| Increment | Builds | Status |
| --- | --- | --- |
| Early spike | Rules R-4, R-6, R-7, R-8, R-9 as plain functions | Done, 13 tests pass |
| 0 Base | Roles, cases, audit log, configuration, access check | Not started |
| 1 Intake | Webhook and simulator, registration, duplicates | Not started |
| 2 Extraction | Model gateway, extraction, validator | Not started |
| 3 Filing | Case resolver and held queue | Not started |
| 4 File checks | Rules R-5 to R-8 | Not started |
| 5 Follow-ups | Drafter, R-9, assistant workbench, send simulator | Not started |
| 6 Review and summary | Analyst review, gate, summary, versions | Not started |
| 7 Hardening | Ten synthetic cases, timing, restart test | Not started |

## Run the tests

Python 3.10 or later, no dependencies.

```bash
python3 -m unittest -v
```

## Layout

- `intake/rules.py`: the deterministic rules (filing by cédula, name comparison, salary conflicts, missing CSS months, follow-up draft check).
- `tests/test_rules.py`: 13 tests on the synthetic case L-0412.

Planned stack for the prototype: Python, FastAPI, SQLite.
