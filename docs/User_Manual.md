# Attendly User Manual

## Installation and sign in

Install Python 3.12 plus a C++ compiler and CMake, create a virtual environment, and install `requirements.txt`. Run `python scripts/setup.py` and create a password of at least 12 characters. Then run `python scripts/run.py` and open http://127.0.0.1:5000. The README contains Windows and Docker alternatives. Keep the generated `.env` private and backed up securely.

## Add participants

Select Add student, enter a name, student ID and cohort. A face image is optional. Without one, the record supports manual attendance only. To enroll a face, obtain explicit participant consent, choose a clear single-face JPEG/PNG, check the consent box and save. To use a camera frame, start the camera on Overview before opening the enrollment dialog, then choose Use current camera frame. Enrollment does not train a new neural network; it stores an encrypted descriptor from the pretrained model.

## Start and run a class

Open Class sessions, enter a title and the same cohort string as the roster, and choose Open session. Return to Overview and select the session. Start camera only when the participant is ready. Choose Capture and check in, or choose an image file and Check image. A green message confirms a recorded attendance. A duplicate message means the earlier entry remains. The system never silently marks an unknown face.

## Manual attendance and export

Choose Manual check-in, enter the student's existing ID and a verification reason, and record attendance. The selected session must still be open and match the participant's cohort. Export CSV downloads the selected session's current cohort roster, including Unmarked rows. Unmarked means no recorded check-in; it does not establish an absence. Close sessions in the Class sessions screen when check-in ends.

## Withdrawal and deletion

In Students, Remove face erases the encrypted template and consent timestamp while preserving attendance. Delete student permanently removes the participant and their linked attendance. Read the confirmation carefully. Backups may still contain old data until backup retention expires. Administrators can run the retention CLI after loading environment variables; the application does not schedule it automatically.

## Troubleshooting

| Symptom | Action |
|---|---|
| Camera unavailable | Use HTTPS or localhost, check site camera permission, or upload an image. |
| Expected one face | Use one clearly visible face and move closer. |
| No confident match | Improve light and framing. Use a manual ID check instead of repeatedly raising the threshold. |
| Similar face already enrolled | Review the existing student roster and verify identity. |
| Different cohort | Use the student's matching cohort session. |
| Security token expired | Reload the page and sign in again if requested. |
| Secrets required | Run setup once, then start through `scripts/run.py`. |
| Cannot read enrolled templates | Restore the original EMBEDDING_KEY. Do not replace it and expect old templates to work. |
| Build fails on dlib | Use Python 3.12 with CMake and a C++ compiler, WSL2, or the included Dockerfile. |

Keep the station supervised. A photograph or replay may pass because this version does not implement liveness detection.
