import cv2
import face_recognition
from fastapi.responses import StreamingResponse
import numpy as np

# Charger le classificateur Haar pour la détection des visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

known_faces = []

def check_camera():
    """Vérifie si la caméra est accessible."""
    print("[CAMERA] Checking...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
        return True
    else:
        return False

def detect_faces_with_names(frame: np.ndarray) -> np.ndarray:
    """
    Détecte les visages dans une image et dessine des boîtes autour.
    """
    # Réduction de la résolution pour optimiser la détection
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Localisation et encodage des visages
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        # Recherche dans les visages connus
        matches = face_recognition.compare_faces([f["encoding"] for f in known_faces], face_encoding, tolerance=0.5)
        name = "No Name"

        if True in matches:
            match_index = matches.index(True)
            name = known_faces[match_index]["name"]

        # Mise à l'échelle des coordonnées pour la résolution d'origine
        top, right, bottom, left = int(top * 2), int(right * 2), int(bottom * 2), int(left * 2)

        # Dessiner les boîtes autour des visages
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def video_stream():
    """
    Génère un flux vidéo continu avec détection des visages.
    """
    cap = cv2.VideoCapture(0)

    # Configurer la résolution et le framerate
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        raise RuntimeError("Impossible d'accéder à la caméra")

    def generate_frames():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Optimisation de la détection des visages
            frame_with_faces = detect_faces_with_names(frame)

            # Encode l'image en JPEG
            _, buffer = cv2.imencode('.jpg', frame_with_faces)
            frame_bytes = buffer.tobytes()

            # Envoie le contenu sous forme de flux multipart
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

def add_new_face(name, frame):
    """
    Ajoute un nouveau visage à la liste des visages connus.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if face_encodings and len(face_encodings) == 1:
        known_faces.append({"name": name, "encoding": face_encodings[0]})
        return True
    return False

def capture_and_add(name):
    """
    Capture une image à partir de la caméra et ajoute un visage connu.
    """
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret and add_new_face(name, frame):
        return True
    return False
