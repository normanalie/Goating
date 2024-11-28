from nicegui import ui
import time

def setup_interface(ui, columns, rows, update_states):
    with ui.column().style("width: 100%; height: 100vh; justify-content: center; align-items: center; max-height: 480px; overflow: hidden;"):
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
