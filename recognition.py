"""CPU face embeddings. No images persist after this function returns."""
import cv2
import face_recognition
import numpy as np


def encode_image(raw):
    if not raw or len(raw) > 4 * 1024 * 1024:
        raise ValueError('Choose a JPEG or PNG under 4 MB.')
    # Read the header before OpenCV allocates the full decoded array.
    from PIL import Image
    from io import BytesIO
    try:
        with Image.open(BytesIO(raw)) as img:
            if img.format not in {'JPEG', 'PNG'} or img.width * img.height > 12_000_000:
                raise ValueError('Use a JPEG or PNG up to 12 megapixels.')
            img.verify()
    except (OSError, SyntaxError) as exc:
        raise ValueError('The image could not be decoded.') from exc
    bgr = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError('The image could not be decoded.')
    scale = min(1, 960 / max(bgr.shape[:2]))
    if scale < 1:
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb, model='hog')
    if len(faces) != 1:
        raise ValueError(f'Expected exactly one face. Found {len(faces)}. Use a clear, front-facing image.')
    top, right, bottom, left = faces[0]
    if min(bottom - top, right - left) < 70:
        raise ValueError('Move closer. The face must be at least 70 pixels wide and high.')
    return face_recognition.face_encodings(rgb, faces, num_jitters=1)[0].tolist()


def nearest(probe, candidates, threshold=0.48, margin=0.06):
    """candidates = [(person_id, embedding)]. Reject ambiguous best matches."""
    if not candidates:
        return None, None
    distances = np.linalg.norm(np.asarray([v for _, v in candidates]) - probe, axis=1)
    order = np.argsort(distances)
    best = int(order[0])
    distance = float(distances[best])
    ambiguous = len(order) > 1 and float(distances[order[1]]) - distance < margin
    if distance > threshold or ambiguous:
        return None, distance
    return candidates[best][0], distance
