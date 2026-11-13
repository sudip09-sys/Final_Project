# Software Requirements Specification

## Purpose and stakeholders

Attendly records attendance for small, supervised class sessions. The administrator manages the roster and sessions. Participants may consent to face enrollment or use manual verification. A reviewer evaluates the source, test evidence and limitations. This version has one administrator credential and no participant login.

## Functional requirements and acceptance criteria

| ID | Requirement | Acceptance criterion |
|---|---|---|
| FR01 | Administrator authentication | Correct password creates a two-hour signed session; protected APIs reject unsigned requests. |
| FR02 | Student roster | Unique student ID, nonempty name and cohort; IDs permit letters, digits, underscore and hyphen. |
| FR03 | Optional face enrollment | A template is stored only with explicit consent and exactly one face in an accepted image. |
| FR04 | Session management | An administrator opens a titled cohort session and can permanently close check-ins for it. |
| FR05 | Recognition | An open session accepts one image, compares against consenting cohort members and rejects unknown or ambiguous candidates. |
| FR06 | Attendance uniqueness | A database constraint prevents more than one attendance row for a student/session pair. |
| FR07 | Manual fallback | A known cohort member can be marked by ID with a nonempty verification note. |
| FR08 | Register and CSV | Current cohort roster shows present or unmarked status; export includes name, ID, time, method and note. |
| FR09 | Withdrawal and deletion | Withdrawal removes the encrypted template and consent timestamp. Full student deletion cascades attendance. |
| FR10 | Audit and retention | Mutations add internal-reference audit events; a CLI command can purge templates older than a chosen consent age. |

## Nonfunctional requirements

| ID | Requirement | Implemented measure or evaluation target |
|---|---|---|
| NFR01 | Protect biometric templates | Fernet authenticated encryption; key supplied separately from database. Raw images never written by application code. |
| NFR02 | Protect web mutations | Same-origin forms, CSRF token, HttpOnly SameSite cookies, secure cookies on HTTPS and restrictive CSP. |
| NFR03 | Bound image processing | 4 MB file bound, 12 MP header limit, at most 960 pixels on long side, single image-processing lock. |
| NFR04 | Usability and accessibility | Labeled inputs, live status, native dialogs and selects, manual fallback, responsive 390px layout. |
| NFR05 | Performance | Target under 3 seconds per frame on a suitable CPU for a small roster; not an SLA. Measure in deployment. |
| NFR06 | Correctness | Parameterized ORM access, unique constraints, rollback on SQL errors, UTC persistence. |
| NFR07 | Deployment | Docker image, configurable port and secrets, persistent database, `/healthz` endpoint. |

## Interfaces and validation

Browser camera requires localhost or HTTPS and user permission. Uploads accept JPEG or PNG under 4 MB and up to 12 megapixels, with one face at least 70 pixels on each dimension after resizing. Forms use multipart requests. APIs return JSON messages and conventional 400, 401, 403, 409, 422, 429 and 503 responses. CSV download is UTF-8 with a BOM for spreadsheet compatibility.

## Assumptions and exclusions

A supervisor verifies identity before enrollment and watches check-in. Participants are consenting adults in the demonstration; adapting to minors or an institution needs a separate assessment and approval. Cohort names are exact strings. The roster is established before sessions. One app process/replica owns the in-memory lock and limiter. No liveness detection, role hierarchy, session roster snapshot, schema migration, automatic attendance penalty or automatic cleanup schedule is included.

## Traceability

FR01, FR02, FR04, FR06 through FR10 are covered by `tests/test_app.py`. FR03 and FR05 combine deterministic API tests with the real-model smoke result in `docs/evidence/model-smoke.json`. Camera hardware and MySQL/cloud execution remain separate deployment acceptance checks unless a verified record explicitly marks them passed.
