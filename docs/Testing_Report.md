# Testing Report

**Build date:** 13 November 2026  
**Environment:** Python 3.12, Flask 3.1.3, SQLAlchemy 2.1.8, dlib 20.0.1, face_recognition 1.3.0, OpenCV 5.0.0.93.  
**Local database:** SQLite. MySQL is configured but not executed in this validation environment.

## Executed API suite

`python -m pytest tests -q` completed with **11 passed**. The JUnit record is `evidence/api-tests.xml`. Tests substitute deterministic face descriptors to isolate application rules. One deprecation warning comes from face_recognition_models using pkg_resources; setuptools is constrained below version 81 for compatibility.

| Area | Executed check | Result |
|---|---|---|
| Authentication | Protected API/page redirect, login and logout | Pass |
| CSRF | Mutation without token rejected | Pass |
| Throttling | Eleventh login attempt in a minute rejected | Pass |
| Manual attendance | Verified ID and note create attendance | Pass |
| Duplicates | Repeat check-in leaves one record | Pass |
| Closed sessions | Both shared mark paths validate session state | Pass |
| Cohort membership | Wrong cohort and unknown ID rejected | Pass |
| Enrollment consent | Face upload without consent rejected | Pass |
| Encryption | Stored template is an encrypted Fernet token | Pass |
| Withdrawal | Template removal blocks future recognition and retains attendance | Pass |
| Unique IDs and delete | Duplicate student conflict; attendance deletion cascades | Pass |
| Export | Present and unmarked rows; formula-like names escaped | Pass |
| Retention CLI | Template older than configured consent age cleared | Pass |
| Matching logic | Unknown, empty roster and ambiguous candidates rejected | Pass |
| HTTP protection | CSP and no-store headers returned | Pass |

## Separate real-model smoke test

The real dlib model processed a public Grace Hopper fixture and a public Obama fixture, without mocked inference. A second image reduced the enrollment fixture's brightness to 85 percent. The changed image matched at distance **0.11787**, below the configured 0.48 threshold. The other person's image was rejected. Blank, corrupt and two-face inputs were rejected. Enrollment through the real API followed by recognition produced an attendance record. One descriptor extraction took **0.568 seconds**, a single measurement on this runtime.

Actual results appear in `evidence/model-smoke.json`. To reproduce, supply two appropriately licensed public test images: `python tests/model_smoke.py /path/face.jpg /path/other-person.jpg`. The file paths are local test inputs, not application enrollment records. No portrait or descriptor is distributed with this source package.

## Browser and hardware evaluation

The complete browser workflow passed. Actual results are recorded separately in `evidence/browser-tests.json`, with zero captured JavaScript console errors. The workflow covers sign-in, real face enrollment, session creation, image check-in, duplicate handling, CSV download, manual attendance, consent withdrawal, session close and mobile layout. A passing browser recording does not verify physical camera capture. Camera hardware, target participants and camera permission behavior must be checked on the actual demonstration computer.

## Unverified acceptance checks

MySQL runtime execution, Docker build on the deployment host, public HTTPS, database survival across a cloud restart, and physical webcam capture need deployment acceptance evidence. Recognition accuracy, false acceptance/rejection rates, demographic performance and replay-attack resistance have not been evaluated. The current project has no liveness detector.

## Suggested future protocol

Use independent enrollment and test sessions from consenting target participants. Record genuine and impostor scores across light, pose, glasses and other expected conditions. Evaluate multiple thresholds and the runner-up margin. Report false acceptance and false rejection rates with sample sizes, along with latency under expected concurrency. Do not tune and evaluate on the same captures.
