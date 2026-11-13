# Viva Preparation

## A short project explanation

Attendly is a supervised attendance web application. An administrator enrolls a consenting participant, opens a cohort session and sends a camera frame to a Python server. OpenCV decodes it, face_recognition produces a dlib descriptor, and the application compares it against that cohort's encrypted templates. A close and unambiguous match creates one attendance entry. Manual verification is available throughout.

## Questions and answers

1. **Is face detection the same as recognition?** No. Detection locates faces in an image. Recognition compares a detected face's descriptor to enrolled descriptors.
2. **Why convert BGR to RGB?** OpenCV decodes into BGR, while the recognition model expects RGB. Reversing that order can change descriptors and matches.
3. **What is stored for a face?** A 128-element numeric descriptor encrypted as a Fernet token. The app discards the uploaded image after processing.
4. **Does enrollment train the model?** No. It runs an existing pretrained network to obtain a descriptor. There is no application training dataset or custom training claim.
5. **How is similarity measured?** Euclidean distance: square the differences between 128 components, sum them and take the square root. Lower distance means a closer embedding.
6. **Why threshold 0.48?** It is a deliberately strict prototype setting. It requires validation on consenting target users. It is not a universally correct threshold.
7. **What is the ambiguity margin?** The second-nearest distance must exceed the nearest by at least 0.06. A small gap indicates uncertainty and leads to a rejection.
8. **Is distance a probability?** No. A distance of 0.2 does not mean 80% confidence. The app does not display invented confidence percentages.
9. **What prevents duplicates?** A pre-check gives a helpful message and a unique database constraint on person_id and session_id handles concurrent insert attempts.
10. **Why SQLAlchemy?** It parameterizes database operations and lets the same model use SQLite locally and MySQL through PyMySQL. Database constraints remain the final integrity guard.
11. **How are images validated?** The server checks encoded size and image header dimensions before decoding, limits formats, resizes, and requires one sufficiently large face.
12. **How do you protect the web application?** Administrator password hash, signed short-lived session, CSRF token on mutation, restrictive same-origin CSP, secure cookies on HTTPS and bounded processing.
13. **Does encryption make biometrics anonymous?** No. Descriptors remain sensitive and can be decrypted by the server holding the key. Access control and retention still matter.
14. **Can a photo fool it?** Yes. This prototype lacks liveness detection. It requires supervision and must not be presented as a spoof-resistant identity system.
15. **What did your tests show?** API tests check business rules with deterministic vectors. A separate real-model smoke test verifies a positive altered-image match and rejection of another fixture, blank input and two faces. It does not establish overall accuracy.
16. **Why no automatic absence or grading?** A missing or rejected match does not prove absence. A human should verify records before any consequential decision.
17. **How does the system scale?** Matching is linear in enrolled cohort size and the state endpoint loads the workspace. One process controls image work. Larger deployments need pagination, shared limiting, worker queues and measured search optimizations.
18. **How would you evaluate it properly?** Collect consented enrollment and independent test sessions, separate genuine/impostor pairs, vary light and pose, report false acceptance/rejection across thresholds and subgroups, and test replay attacks separately.
19. **What happens when consent is withdrawn?** The app removes the face template and consent time, keeps attendance, and supports manual checks. Backup lifecycle needs separate handling.
20. **What would you improve next?** Validate on the intended population, add evaluated liveness, session roster snapshots, secure account roles and migration/backup procedures before a real pilot.

## Code walkthrough order

Start with `create_app` and configuration, then Person/ClassSession/Attendance/Audit. Explain enrollment and encryption. Walk through `encode_image`, `nearest`, `/api/recognize` and the shared `mark` function. Show the unique constraint, manual fallback, export escaping and withdrawal. Finish by running the tests and naming the remaining hardware/deployment checks.

## Demonstration checklist

Sign in, enroll a consenting fixture, open a session, record a match, show duplicate prevention, reject an unknown image, mark another participant manually, export CSV, withdraw a template and close the session. Use demonstration data rather than real student records in a public presentation.
