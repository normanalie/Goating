import sqlite3
import cv2
import time
import face_recognition
from fastapi.responses import StreamingResponse
import numpy as np
import json
import base64

# Charger le classificateur Haar pour la détection des visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def save_faces_to_supabase(supabase_client, user_id, encodings):
    """
    Enregistre plusieurs encodages d'un même visage dans la table "faces".
    Chaque encodage est inséré dans une ligne distincte.
    Les encodages sont stockés sous forme de liste (format JSON) dans une colonne de type jsonb.
    """
    for encoding in encodings:
        # Convertir le tableau numpy en liste Python (sérialisable en JSON)
        encoding_json = np.array(encoding).tolist()
        data = {
            "user_id": user_id,
            "encoding": encoding_json
        }
        try:
            res = supabase_client.table("faces").insert(data).execute()
            print('[CAMERA] Insertion réussie de l\'encoding pour user_id:', user_id)
        except Exception as e:
            print('[CAMERA] Erreur lors de l\'insertion de l\'encoding pour user_id', user_id, ":", e)


def load_face_from_supabase(supabase_client, user_id):
    """
    Charge tous les encodages de la table "faces" pour un user donné,
    convertit chaque encoding (liste de floats) en tableau numpy et retourne un dictionnaire:
      { "name": user_id, "encoding": [array1, array2, ...] }
    """
    try:
        res = supabase_client.table("faces").select("encoding").eq("user_id", user_id).execute()
        encodings = []
        for row in res.data:
            # Chaque row contient une liste stockée dans la colonne "encoding"
            encoding_list = row["encoding"]
            arr = np.array(encoding_list, dtype=np.float64)
            encodings.append(arr)
        return {"name": user_id, "encoding": encodings}
    except Exception as e:
        print('[CAMERA] Load face encodings from Supabase error:', e)
        return None


def check_camera():
    """Vérifie si la caméra est accessible."""
    print("[CAMERA] Checking...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
        return True
    else:
        return False


def detect_faces_with_name(frame: np.ndarray, stored_data) -> np.ndarray:
    """
    Détecte les visages dans l'image et dessine une boîte si le visage correspond aux encodages stockés.
    stored_data est un dictionnaire {"name": user_id, "encoding": [array1, array2, ...]}.
    """
    stored_encodings = stored_data["encoding"]
    # Réduction de la résolution pour optimiser la détection
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Localisation et encodage des visages dans la frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        # On compare chaque encoding détecté avec tous les encodages stockés
        matches = face_recognition.compare_faces(stored_encodings, face_encoding, tolerance=0.5)
        name = "No Name"
        if True in matches:
            name = stored_data["name"]
        top, right, bottom, left = int(top * 2), int(right * 2), int(bottom * 2), int(left * 2)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame


def video_stream(known_faces):
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
            frame_with_faces = detect_faces_with_name(frame, known_faces)

            # Encode l'image en JPEG
            _, buffer = cv2.imencode('.jpg', frame_with_faces)
            frame_bytes = buffer.tobytes()

            # Envoie le contenu sous forme de flux multipart
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


def add_new_face(supabase_client, user_id, frames):
    """
    Ajoute un nouveau visage à la liste des visages connus et le stocke dans la base de données.
    """
    encodings = []
    for frame in frames:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if face_encodings:
            encodings.append(face_encodings[0])

    return save_faces_to_supabase(supabase_client, user_id, encodings)


def capture_frame():
    cap = cv2.VideoCapture(0)
    time.sleep(1)  # Attendre l'initialisation de la caméra pour éviter une image noire.
    ret, frame = cap.read()
    cap.release()
    return frame 


def verify_face(supabase_client, user_id, tolerance=0.5):
    """
    Capture une frame et compare les encodages détectés avec ceux stockés pour l'utilisateur.
    Retourne (True, message) si le visage est reconnu, sinon (False, message).
    """
    stored_data = load_face_from_supabase(supabase_client, user_id)
    if not stored_data or not stored_data["encoding"]:
        print('[CAMERA] Aucun visage enregistré pour cet utilisateur')
        return False, "Aucun visage enregistré pour cet utilisateur."
    
    frame = capture_frame()
    if frame is None:
        print('[CAMERA] Impossible de capturer une image')
        return False, "Impossible de capturer l'image."
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    if not face_encodings:
        print('[CAMERA] Aucun visage détecté')
        return False, "Aucun visage détecté, veuillez réessayer."
    
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(stored_data["encoding"], encoding, tolerance=tolerance)
        if True in matches:
            return True, "Visage reconnu."
    return False, "Visage non reconnu, veuillez réessayer."


def frame_to_data_uri(frame):
    # Encode la frame en JPEG
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return None
    # Convertit en base64
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    # Retourne une URI pour l'image
    return f"data:image/jpeg;base64,{jpg_as_text}"
