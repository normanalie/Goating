from nicegui import ui, app
from fastapi import Response
from utils.supabase_utils import check_supabase
from utils.camera_utils import check_camera, video_stream, capture_frame
from utils.arm_utils import check_serial_connection
from interface import setup_interface
import time

import cv2

# Colonnes et lignes de la table
columns = [
    {'name': 'service', 'label': 'Service', 'field': 'service', 'align': 'left'},
    {'name': 'state', 'label': 'Etat', 'field': 'state', 'align': 'center'},
]

rows = [
    {'service': 'Supabase', 'state': "checking"},
    {'service': 'Camera', 'state': "checking"},
    {'service': 'Serial Pico', 'state': "checking"},
    {'service': 'ROS', 'state': "error"},
]

# Fonction de mise à jour des états
# def update_states():
#     rows[0]['state'] = "connecte" if check_supabase() else "error"
#     rows[1]['state'] = "connecte" if check_camera() else "error"
#     rows[2]['state'] = "connecte" if check_serial_connection() else "error"

# Configurer l'interface utilisateur
# setup_interface(ui, columns, rows, update_states)


# Initialiser les états au lancement
#update_states()

@app.get('/video_stream')
async def video_stream_route():
    
    return video_stream()


# Lancer l'application
ui.run(storage_secret="secret")
