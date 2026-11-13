# Research Foundation and References

## Base research paper

Florian Schroff, Dmitry Kalenichenko and James Philbin. **FaceNet: A Unified Embedding for Face Recognition and Clustering.** CVPR 2015, pages 815–823. DOI: 10.1109/CVPR.2015.7298682.

- Author manuscript and metadata: https://arxiv.org/abs/1503.03832
- Open-access publisher copy: https://openaccess.thecvf.com/content_cvpr_2015/papers/Schroff_FaceNet_A_Unified_2015_CVPR_paper.pdf
- The original PDF is included unchanged as `Base_Research_Paper_FaceNet_CVPR2015.pdf`. Copyright and publication rights remain with the original holders.

FaceNet explains how an embedding space can support recognition with distances and describes triplet-based training. It motivates the project's use of descriptors and a distance threshold. **Attendly does not implement or train FaceNet.** It calls the face_recognition library, which wraps dlib's pretrained metric-learning ResNet. Do not attribute FaceNet's published benchmark numbers to this application.

## Implementation sources

1. Adam Geitgey, face_recognition repository and usage examples: https://github.com/ageitgey/face_recognition
2. dlib official face recognition example and metric-learning architecture: https://dlib.net/dnn_face_recognition_ex.cpp.html
3. OpenCV color conversion documentation: https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html
4. Flask security guidance: https://flask.palletsprojects.com/en/stable/web-security/
5. SQLAlchemy constraints: https://docs.sqlalchemy.org/en/20/core/constraints.html
6. cryptography Fernet documentation: https://cryptography.io/en/latest/fernet/

## Evidence and responsible claims

The dlib and FaceNet publications report benchmark results under their own protocols. Neither gives a measured accuracy for this classroom workflow. A proper evaluation needs independent consenting participants and tests across enrollment conditions, unknown people, light, pose and relevant subgroups. The project's default threshold and margin are engineering settings awaiting that validation.

Functional smoke testing used the Grace Hopper sample image distributed with Matplotlib and an Obama example image from the face_recognition repository. These are public test fixtures, not enrolled students or evidence of participant consent for deployment. Tests ran locally with temporary data. The original portraits and biometric vectors are excluded from the project package. The tutorial labels the fixture as Demo Participant.
