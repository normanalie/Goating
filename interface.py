from nicegui import ui, app
import time
from utils.camera_utils import load_face_from_supabase, capture_frame, add_new_face, verify_face, frame_to_data_uri
from utils.supabase_utils import login as supabase_login, check_login, supabase as supabase_client
import base64
import asyncio 

def is_user_connected():
    if (not check_login()) or (not 'user' in app.storage.user.keys()) or (app.storage.user['user'] == None):
        return False
    return True

@ui.page('/')
async def home_page():
    if not is_user_connected():
        print('[INTERFACE] User not logged in')
        ui.navigate.to('/login')
        return 

    with ui.row().style("width: 100%; display: flex; align-items: center;"):
        ui.button(icon="arrow_back_ios_new", on_click=lambda: ui.navigate.to('/')).style(
            "visibility: hidden; height: 28px; width: 28px; background-color: #007acc; color: white; margin-right: auto;"
        )
        with ui.row().style("margin: 0 auto; display: flex; align-items: center; justify-content: center;"):
            ui.icon("precision_manufacturing").style("font-size: 24px; color: #007acc;")
            ui.label("STOREBOT").style("font-size: 20px; font-weight: bold; color: #007acc; margin-left: 5px;")
        
        # Bouton "user" ouvre la modale
        ui.button("", icon="person", on_click=lambda: user_modal.open()).style(
            "height: 20px; width: 20px; background-color: #007acc; color: white; margin-left: auto;"
        )


    # When clients are connected
    await ui.context.client.connected()
    with ui.dialog() as user_modal, ui.card():
        with ui.row().style("align-items: center; margin-bottom: 10px;"):
            ui.icon("person").style("font-size: 24px; color: #007acc;")
            ui.label("Utilisateur").style("font-size: 20px; font-weight: bold; color: #007acc; margin-left: 5px;")
        user = app.storage.user['user']  # Existence of the key is checked at the loading of the page
        ui.label(f'ID: {user["id"]}').style("font-size: 14px; color: #007acc; margin-left: 5px;")
        ui.label(f'Email: {user["email"]}').style("font-size: 14px; color: #007acc; margin-left: 5px;")
        ui.button("Deconnexion", on_click=logout).style(
                "font-size: 14px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )

def logout():
    print('[INTERFACE] User logged out')
    app.storage.user['user'] = None
    ui.navigate.to('/login')


@ui.page('/setup')
def setup_interface(ui, columns, rows, update_states):
    with ui.column().style("width: 100%; margin-top: 20px; justify-content: center; align-items: center; max-height: 480px; overflow: hidden;"):
        # Affichage du nom du système avec l'icône
        with ui.row().style("align-items: center; margin-bottom: 10px;"):
            ui.icon("precision_manufacturing").style("font-size: 28px; color: #007acc;")
            ui.label("STOREBOT").style("font-size: 28px; font-weight: bold; color: #007acc; margin-left: 5px;")

        # Tableau des états de connexion
        with ui.table(columns=columns, rows=rows).style("width: 200px") as table:
            table.add_slot('body-cell-state', """
                <q-td :props="props">
                    <q-icon name="fiber_manual_record" size="16px" color="green" v-if="props.value == 'connecte'"/>
                    <q-icon name="fiber_manual_record" size="16px" color="yellow" v-else-if="props.value == 'checking'"/>
                    <q-icon name="fiber_manual_record" size="16px" color="red" v-else/>
                </q-td> 
            """)

        # Boutons côte à côte
        with ui.row().style("margin-top: 20px; justify-content: center; gap: 10px;"):
            ui.button('Rafraîchir', on_click=update_states).style(
                "font-size: 14px; width: 200px; padding: 10px;"
            )
            ui.button("Vision", on_click=lambda: ui.navigate.to('/video')).style(
                "font-size: 14px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )

        # Footer en bas de page
        ui.label("Made with <3 by GOATing team").style("font-size: 12px; color: #888888; margin-top: 10px;")

@ui.page('/video')
def video_page():
    # Conteneur principal
    with ui.row().style("width: 100%; display: flex; align-items: center;"):
        ui.button(icon="arrow_back_ios_new", on_click=lambda: ui.navigate.to('/')).style(
            "height: 28px; width: 28px; background-color: #007acc; color: white; margin-right: auto;"
        )
        with ui.row().style("margin: 0 auto; display: flex; align-items: center; justify-content: center;"):
            ui.icon("precision_manufacturing").style("font-size: 24px; color: #007acc;")
            ui.label("STOREBOT").style("font-size: 20px; font-weight: bold; color: #007acc; margin-left: 5px;")
        
        # Bouton "settings" ouvre la modale
        ui.button("", icon="settings", on_click=lambda: settings_modal.open()).style(
            "height: 28px; width: 28px; background-color: #007acc; color: white; margin-left: auto;"
        )
    
    # Modale pour ajouter un nom
    with ui.dialog() as settings_modal, ui.card():
        ui.label("Ajouter un nom").style("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        name_input = ui.input(label="Nom", placeholder="Entrez un nom").style("width: 300px; margin-bottom: 10px;")
        with ui.row().style("justify-content: flex-end; gap: 10px;"):
            ui.button("Annuler", on_click=lambda: settings_modal.close()).style(
                "background-color: gray; color: white;"
            )
            ui.button("Ajouter", on_click=lambda: (add_face(name_input), settings_modal.close())).style(
                "background-color: #007acc; color: white;"
            )

    # Affichage du flux vidéo
    with ui.row().style("justify-content: center; width: 100%;"):
        ui.html('<iframe src="/video_stream" style="width: 640px; height: 360px;"></iframe>').style(
            "margin-bottom: 5px;"
        )

        

def add_face(name_input):
    """
    Capture et ajoute un visage à partir du flux vidéo.
    """
    name = name_input.value
    if not name:
        ui.notify("Veuillez entrer un nom avant d'ajouter", color="red")
        return

    from utils.camera_utils import capture_and_add
    success = capture_and_add(name)
    if success:
        ui.notify(f"Visage ajouté pour {name}", color="green")
    else:
        ui.notify("Aucun visage détecté, veuillez réessayer", color="red")


@ui.page('/login')
def login_page():
    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center;"):
        with ui.row().style("align-items: center; margin-bottom: 10px;"):
            ui.icon("precision_manufacturing").style("font-size: 28px; color: #007acc;")
            ui.label("STOREBOT").style("font-size: 28px; font-weight: bold; color: #007acc; margin-left: 5px;")
        staff_number = ui.input(label="N° de compte", placeholder="Entrez votre n° étudiant").props("clearable").style("margin-bottom: 10px; width: 410px")
        password = ui.input(label="Mot de passe", placeholder="Entrez votre mot de passe", password=True).props("clearable").style("margin-bottom: 10px; width: 410px")
        with ui.row().style("margin-top: 20px; justify-content: center; gap: 10px;"):
            ui.button('Aide', color=None, on_click=lambda: ui.navigate.to('/help')).style(
                "font-size: 14px; width: 200px; padding: 10px;"
            )
            # Au lieu d'aller directement à '/', on va vers la page de vérification du visage
            ui.button("Connexion", on_click=lambda: check_and_verify(staff_number.value, password.value)).style(
                "font-size: 14px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )
        ui.label("Made with <3 by GOATing team").style("font-size: 12px; color: #888888; margin-top: 10px;")

def check_and_verify(staff_number, password):
    user = supabase_login(staff_number, password)
    if user:
        app.storage.user['user'] = {
            "id": user.id,
            "email": user.email,
        }
        ui.navigate.to('/face_verification')
    else:
        app.storage.user['user'] = None
        ui.notify("Email ou mot de passe incorrect", color="red")

@ui.page('/face_verification')
async def face_verification_page():
    if not is_user_connected:
        ui.navigate.to('/login')
        return
    
    user = app.storage.user['user']
    # Ajout de la flèche bleue en haut, au centre de la page
    with ui.row().style("position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000;"):
        ui.icon("arrow_upward").style("font-size: 48px; color: #007acc;")
    
    # Charger les encodages enregistrés pour cet utilisateur
    stored_encodings = load_face_from_supabase(supabase_client, user["id"])

    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center;"):
        ui.label("Un petit instant, nous vérifions votre identité...").style("font-size: 18px; margin-bottom: 20px;")
    await ui.context.client.connected()
    if stored_encodings["encoding"] == []:
        ui.navigate.to('/face_registration')
    verify_and_login(user["id"])

def verify_and_login(user_id):
    # La fonction verify_face doit capturer une frame et comparer avec les encodings stockés
    valid, message = verify_face(supabase_client, user_id)
    if valid:
        ui.notify("Visage reconnu, connexion validée !", color="green")
        ui.timer(1, lambda: ui.navigate.to('/'), once=True)
    else:
        ui.notify(message, color="red")
        ui.timer(2, lambda: ui.navigate.to('/login'), once=True)

@ui.page('/face_registration')
def face_registration_page():
    if not is_user_connected():
        ui.navigate.to('/login')
        return
    
    user = app.storage.user['user']
    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center;"):
        ui.label("Nous devons enregistrer votre visage. Cliquer sur le bouton pour commencer").style("font-size: 18px; margin-bottom: 20px;")
        ui.button("Démarrer", on_click=lambda: register_face(user["id"])).style(
            "font-size: 14px; width: 250px; padding: 10px; background-color: #007acc; color: white;"
        )

import asyncio

async def register_face(user_id):
    # Capture quelques frames pour obtenir un bon encoding
    frames = []
    # Créer la flèche en haut au centre
    arrow = ui.icon("arrow_upward").style(
        "position: fixed; top: 10px; left: 50%; transform: translateX(-50%); font-size: 48px; color: #007acc; z-index: 1000;"
    )

    # Première étape : flèche au centre et capture de la première image
    await asyncio.sleep(1)  # attendre 1 seconde
    frame1 = capture_frame()
    if frame1 is not None:
        frames.append(frame1)

    # Deuxième étape : déplacer la flèche en haut à droite et capturer une image
    arrow.style("position: fixed; top: 10px; right: 10px; left: unset; transform: none;")
    await asyncio.sleep(1)
    frame2 = capture_frame()
    if frame2 is not None:
        frames.append(frame2)

    # Troisième étape : déplacer la flèche en haut à gauche et capturer une image
    arrow.style("position: fixed; top: 10px; left: 10px; right: unset; transform: none;")
    await asyncio.sleep(1)
    frame3 = capture_frame()
    if frame3 is not None:
        frames.append(frame3)

    # Supprimer la flèche après la capture
    arrow.style("display: none;")
    arrow.delete()

    if frames:
        print(f"[INTERFACE] Face registration: captured {len(frames)} frames for user {user_id}")
        # Utilisation d'asyncio.to_thread pour ne pas bloquer l'event loop si add_new_face est synchrone
        success = await add_new_face(supabase_client, user_id, frames)
        if success:
            ui.notify("Visage enregistré, vous pouvez maintenant vérifier votre visage.", color="green")
            ui.timer(2, lambda: ui.navigate.to('/face_verification'), once=True)
        else:
            print(f"[INTERFACE] Face registration: failed to add face for user {user_id}")
            ui.notify("Impossible d'enregistrer le visage dans la DB. Veuillez réessayer.", color="red")
            ui.timer(2, lambda: ui.navigate.to('/login'), once=True)
    else:
        print(f"[INTERFACE] Face registration: no frames captured for user {user_id}")
        ui.notify("Impossible de capturer une image", color="red")
