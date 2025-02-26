from nicegui import ui, app
import time
from utils.camera_utils import load_face_from_supabase, capture_frame, add_new_face, verify_face, frame_to_data_uri
from utils.supabase_utils import login as supabase_login, check_login, supabase as supabase_client, get_orders, get_order_items
import base64
import asyncio 

DISABLE_LOGIN = True  # WARNING NOT TO BE USED IN PRODUCTION

def is_user_connected():
    if (not check_login()) or (not 'user' in app.storage.user.keys()) or (app.storage.user['user'] == None):
        if DISABLE_LOGIN:
            app.storage.user['user'] = {"id": "developper", "email": "developper@test.com"}
            return True
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

    # Bloc central contenant les 3 boutons en colonne
    with ui.column().style("width: 100%; justify-content: center; align-items: center; margin-top: 60px;"):
        ui.label("Connecté en tant que " + app.storage.user['user']['email']).style("font-size: 14px; margin-bottom: 10px;")
        ui.button("Mes commandes", on_click=lambda: ui.navigate.to('/orders')).style(
            "margin-bottom: 10px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
        )
        ui.button("Nouvelle commande", on_click=lambda: ui.navigate.to('/new_order')).style(
            "margin-bottom: 10px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
        )
        ui.button("Déconnexion", color=None, on_click=logout).style(
            "width: 200px; padding: 10px;"
        )

    # Attente de la connexion du client
    await ui.context.client.connected()
    # Modale utilisateur
    with ui.dialog() as user_modal, ui.card():
        with ui.row().style("align-items: center; margin-bottom: 10px;"):
            ui.icon("person").style("font-size: 24px; color: #007acc;")
            ui.label("Utilisateur").style("font-size: 20px; font-weight: bold; color: #007acc; margin-left: 5px;")
        user = app.storage.user['user']  # L'existence de la clé est vérifiée lors du chargement de la page
        ui.label(f'ID: {user["id"]}').style("font-size: 14px; color: #007acc; margin-left: 5px;")
        ui.label(f'Email: {user["email"]}').style("font-size: 14px; color: #007acc; margin-left: 5px;")
        ui.button("Déconnexion", on_click=logout).style(
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
    user, err = supabase_login(staff_number, password)
    if user:
        app.storage.user['user'] = {
            "id": user.id,
            "email": user.email,
        }
        ui.navigate.to('/face_verification')
    elif err:
        app.storage.user['user'] = None
        ui.notify(err, color="red")
    else:
        app.storage.user['user'] = None 
        ui.notify("Erreur inconnue", color="red")

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
    
    # Première étape : flèche au centre et capture de la première image
    arrow = ui.icon("arrow_upward").style(
        "position: fixed; top: 10px; left: 50%; transform: translateX(-50%); font-size: 48px; color: #007acc; z-index: 1000;"
    )
    await asyncio.sleep(0.5)
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
    # Afficher un loader
    ui.spinner(size='lg').style(
        "position: fixed; top: 10px; left: 50%; transform: translateX(-50%); font-size: 48px; color: #007acc; z-index: 1000;"
    )
    await asyncio.sleep(0.5)


    if frames:
        print(f"[INTERFACE] Face registration: captured {len(frames)} frames for user {user_id}")
        success = await add_new_face(supabase_client, user_id, frames)
        if success:
            ui.navigate.to('/face_verification')
        else:
            print(f"[INTERFACE] Face registration: failed to add face for user {user_id}")
            ui.notify("Impossible d'enregistrer le visage dans la DB. Veuillez réessayer.", color="red")
            ui.timer(2, lambda: ui.navigate.to('/login'), once=True)
    else:
        print(f"[INTERFACE] Face registration: no frames captured for user {user_id}")
        ui.notify("Impossible de capturer une image", color="red")

@ui.page('/help')
def help_page():
    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center; overflow: hidden;"):
        with ui.row().style("align-items: center; margin-bottom: 10px;"):
            ui.icon("precision_manufacturing").style("font-size: 28px; color: #007acc;")
            ui.label("STOREBOT").style("font-size: 28px; font-weight: bold; color: #007acc; margin-left: 5px;")
        ui.label("Aide").style("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        ui.markdown(
            """
            Storebot vous permet de commander du matériel electronique et de gérer vos emprunts et retours.
            """
        ).style("text-align: center; margin-bottom: 20px;")
        with ui.row().style("margin-top: 20px; justify-content: center; gap: 10px;"):
            ui.button("Créer un compte", on_click=lambda: ui.navigate.to('/signup')).style(
                "width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )
            ui.button("Mot de passe oublié", on_click=lambda: ui.navigate.to('/signup')).style(
                "width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )
        ui.button("Accueil", color=None, on_click=lambda: ui.navigate.to('/login')).style(
            "width: 200px; padding: 10px;"
        )


@ui.page('/signup')
def signup_page():
    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center;"):
        ui.label("Créer un compte").style("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        # Première ligne : numéro de compte et badge côte à côte
        with ui.row().style("justify-content: center; gap: 10px; margin-bottom: 10px;"):
            staff_number = ui.input(
                label="N° de compte UVSQ", 
                placeholder="Votre numéro de compte sur votre carte UVSQ"
            ).props("clearable").style("width: 300px")
            tag_id = ui.input(
                label="Scannez votre badge UVSQ"
            ).props("disable").style("width: 300px")
        # Deuxième ligne : email et mot de passe côte à côte
        with ui.row().style("justify-content: center; gap: 10px; margin-bottom: 10px;"):
            email = ui.input(
                label="Email", 
                placeholder="Entrez votre email"
            ).props("clearable").style("width: 300px")
            password = ui.input(
                label="Mot de passe", 
                placeholder="Entrez votre mot de passe", 
                password=True
            ).props("clearable").style("width: 300px")
        # Boutons d'action
        with ui.row().style("margin-top: 20px; justify-content: center; gap: 10px;"):
            ui.button("Créer un compte", on_click=lambda: check_and_signup(
                staff_number.value, email.value, password.value, tag_id.value
            )).style(
                "font-size: 14px; width: 200px; padding: 10px; background-color: #007acc; color: white;"
            )
            ui.button("Retour", on_click=lambda: ui.navigate.to('/login')).style(
                "font-size: 14px; width: 200px; padding: 10px;"
            )

def check_and_signup(staff_number, email, password, tag_id):
    from utils.supabase_utils import signup as supabase_signup
    user = supabase_signup(staff_number, email, password, tag_id if tag_id != "" else None)
    if user:
        app.storage.user['user'] = {"id": user.id, "email": user.email}
        logout()
    else:
        ui.notify("Erreur lors de la création du compte", color="red")


@ui.page('/orders')
async def orders_page():
    if not is_user_connected():
        ui.navigate.to('/login')
        return

    user = app.storage.user['user']
    user_id = user["id"]

    # Récupérer les commandes de l'utilisateur en déléguant la requête à un thread
    orders_data = await asyncio.to_thread(get_orders, user_id)

    with ui.column().style("padding: 20px;"):
        ui.label("Mes commandes").style("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        if orders_data:
            for order in orders_data:
                order_id = order["id"]
                order_name = order["name"]
                created_at = order["created_at"]
                with ui.card().classes("q-pa-md q-mb-md"):
                    ui.label(f"Commande : {order_name}").style("font-size: 16px;")
                    ui.label(f"Date : {created_at}").style("font-size: 14px; color: gray;")
                    # Bouton pour afficher les détails de la commande
                    ui.button("Détails", on_click=lambda order_id=order_id: ui.navigate.to(f'/order/{order_id}')).style("margin-top: 10px;")
        else:
            ui.label("Aucune commande trouvée.").style("font-size: 16px;")
        
        ui.button("Retour", on_click=lambda: ui.navigate.to('/')).style("margin-top: 20px;")


@ui.page('/order/{order_id}')
async def order_detail_page(order_id: str):
    if not is_user_connected():
        ui.navigate.to('/login')
        return

    # Récupérer les items de la commande via la fonction dans supabase_utils
    order_items = await asyncio.to_thread(get_order_items, order_id)

    with ui.column().style("padding: 20px;"):
        ui.label(f"Détails de la commande {order_id}")\
          .style("font-size: 24px; font-weight: bold; margin-bottom: 20px;")

        if order_items:
            # Préparation des données pour le tableau
            rows = [
                {
                    "denom": item.get('boxes', {}).get('material_types', {}).get('name', "N/A"),
                    "image": item.get('boxes', {}).get('material_types', {}).get('image', ""),
                    "quantity": item['quantity'],
                    "action": item['action'],
                    "loan": item.get('loan_item_id', "")
                }
                for item in order_items
            ]
            table = ui.table(
                columns=[
                    {"name": "image", "label": "Image", "field": "image"},
                    {"name": "denom", "label": "Dénomination", "field": "denom"},
                    {"name": "quantity", "label": "Quantité", "field": "quantity"},
                    {"name": "action", "label": "Action", "field": "action"},
                    {"name": "loan", "label": "Emprunt initial", "field": "loan"},
                ],
                rows=rows
            ).style("width: 100%;")

            # Slot personnalisé pour afficher l'image
            table.add_slot('body-cell-image', """
                <q-td :props="props">
                    <img :src="props.row.image" style="width: 50px; height: auto;" alt="Image de l'item" />
                </q-td>
            """)
        else:
            ui.label("Aucun item trouvé pour cette commande.").style("font-size: 16px;")
        
        ui.button("Retour", on_click=lambda: ui.navigate.to('/orders')).style("margin-top: 20px;")
