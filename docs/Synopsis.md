# Smart Attendance System Using Face Recognition

**Project:** Attendly  
**Author:** Sudip Sah  
**Institution:** Gachon University  
**Version:** Academic prototype 1.0, 13 November 2026

## Problem

Calling names and maintaining paper registers interrupts class and makes later consolidation difficult. A digital register can reduce repeated data entry, but face recognition also introduces incorrect matches and sensitive biometric data. The project therefore combines supervised recognition with administrator review and manual attendance.

## Aim and objectives

Build an application that enrolls consenting participants, opens class sessions, identifies one face at a time within the selected cohort, prevents duplicate attendance, and exports a readable register. Demonstrate computer vision, database constraints, secure web requests, and testable application design.

## Proposed system

A browser captures or uploads a frame. Flask validates the request and session. OpenCV decodes the image and converts BGR to RGB. The face_recognition library detects a face and produces a pretrained dlib 128D descriptor. The application compares that descriptor to decrypted templates for the selected cohort. A sufficiently close and unambiguous match records attendance once per student and session.

## Scope and expected output

One administrator, one small workspace, several cohorts and sessions, camera or upload input, manual check-in, session closing, CSV export, encrypted templates and consent withdrawal. Local SQLite makes setup quick; a MySQL configuration and Docker deployment are included. The supplied source, report, UML, presentation and tutorials support demonstration and viva preparation.

## Evaluation and limitations

Automated API checks and a separate real-model smoke test verify working paths and rejection behavior. These tests do not estimate population recognition accuracy. Liveness detection, automatic absence decisions, large-scale recognition and institutional rollout are outside the implemented scope. Cloud publication requires verified account access and runtime checks.
