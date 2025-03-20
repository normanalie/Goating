import sqlite3
import cv2
import time
import face_recognition
from fastapi.responses import StreamingResponse
import numpy as np
import json
import base64
import asyncio
import platform

# Fonction de détection du Raspberry Pi
def is_raspberry_pi():
    try:
        with open('/proc/device-tree/model', 'r') as model_file:
            model = model_file.read().lower()
            return 'raspberry pi' in model
    except Exception:
        return False

# Flag indiquant si l'on est sur un Raspberry Pi
IS_PI = is_raspberry_pi()

if IS_PI:
    try:
        from picamera2 import Picamera2
    except ImportError as e:
        raise ImportError("Le module picamera2 est requis sur Raspberry Pi. Installez-le avec 'pip install picamera2'") from e

# Charger le classificateur Haar pour la détection des visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- Fonction utilitaire pour obtenir une instance de Picamera2 ---
def get_picamera2_instance(video=True):
    """
    Crée et configure une nouvelle instance de Picamera2.
    Si video est True, on utilise une configuration pour la vidéo,
    sinon pour la capture still.
    """
    picam2 = Picamera2()
    if video:
        config = picam2.create_video_configuration(main={"size": (640, 480)})
    else:
        config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    return picam2

# --- Fonctions liées à Supabase (inchangées) ---
async def save_faces_to_supabase(supabase_client, user_id, encodings):
    async def insert_encoding(encoding):
        encoding_json = np.array(encoding).tolist()
        data = {
            "user_id": user_id,
            "encoding": encoding_json
        }
        try:
            await asyncio.to_thread(supabase_client.table("faces").insert(data).execute)
            print('[CAMERA] Insertion réussie de l\'encoding pour user_id:', user_id)
            return True
        except Exception as e:
            print('[CAMERA] Erreur lors de l\'insertion de l\'encoding pour user_id', user_id, ":", e)
            return False

    results = await asyncio.gather(*(insert_encoding(encoding) for encoding in encodings))
    return all(results)

def load_face_from_supabase(supabase_client, user_id):
    try:
        res = supabase_client.table("faces").select("encoding").eq("user_id", user_id).execute()
        encodings = []
        for row in res.data:
            encoding_list = row["encoding"]
            arr = np.array(encoding_list, dtype=np.float64)
            encodings.append(arr)
        return {"name": user_id, "encoding": encodings}
    except Exception as e:
        print('[CAMERA] Load face encodings from Supabase error:', e)
        return None

# --- Fonctions de gestion de la caméra ---
def check_camera():
    """Vérifie si la caméra est accessible en fonction de la plateforme."""
    print("[CAMERA] Checking...")
    if IS_PI:
        try:
            picam2 = get_picamera2_instance(video=True)
            picam2.start()
            picam2.stop()
            picam2.close()
            return True
        except Exception as e:
            print("[CAMERA] Erreur d'accès à la caméra sur Raspberry Pi:", e)
            return False
    else:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            return True
        else:
            return False

def detect_faces_with_name(frame: np.ndarray, stored_data) -> np.ndarray:
    """
    Détecte les visages dans l'image et dessine une boîte si le visage correspond aux encodages stockés.
    """
    stored_encodings = stored_data["encoding"]
    # Réduction de la résolution pour optimiser la détection
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(stored_encodings, face_encoding, tolerance=0.5)
        name = "No Name"
        if True in matches:
            name = stored_data["name"]
        top, right, bottom, left = int(top * 2), int(right * 2), int(bottom * 2), int(left * 2)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def video_stream(known_faces=None):
    """
    Génère un flux vidéo continu avec détection des visages.
    Pour Raspberry Pi, on utilise picamera2 ; sinon, cv2.VideoCapture.
    """
    if IS_PI:
        # Instanciation locale de la caméra pour la vidéo
        picam2 = get_picamera2_instance(video=True)
        picam2.start()
        time.sleep(0.1)  # Stabilisation de la caméra

        def generate_frames():
            try:
                while True:
                    frame = picam2.capture_array()
                    # Conversion de RGB (picamera2) vers BGR (OpenCV)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    if known_faces:
                        frame = detect_faces_with_name(frame, known_faces)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print("Erreur lors de la génération des frames :", e)
            finally:
                # Toujours arrêter et fermer la caméra
                picam2.stop()
                picam2.close()
        return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')
    else:
        # Utilisation de cv2.VideoCapture pour un ordinateur
        cap = cv2.VideoCapture(0)
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
                if known_faces:
                    frame = detect_faces_with_name(frame, known_faces)
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

async def add_new_face(supabase_client, user_id, frames):
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
    print(f"[CAMERA] Detected face in {len(encodings)} frame(s) for user {user_id}")
    success = await save_faces_to_supabase(supabase_client, user_id, encodings)
    return success

def capture_frame():
    """
    Capture une frame unique en utilisant la méthode adaptée à la plateforme.
    """
    if IS_PI:
        picam2 = get_picamera2_instance(video=False)
        try:
            picam2.start()
            time.sleep(0.5)  # Temps de warm-up
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        finally:
            picam2.stop()
            picam2.close()
    else:
        cap = cv2.VideoCapture(0)
        time.sleep(0.5)
        ret, frame = cap.read()
        cap.release()
        return frame
def verify_face(supabase_client, user_id, tolerance=0.5):
    """
    Capture une frame et compare les encodages détectés avec ceux stockés pour l'utilisateur.
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
    """
    Convertit une frame en URI de données pour l'image.
    """
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return None
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{jpg_as_text}"
