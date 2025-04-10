from nicegui import ui, app
from utils.camera_utils import  video_stream
from interface import setup_interface


@app.get('/video_stream')
async def video_stream_route():
    
    return video_stream()


# Lancer l'application
ui.run(storage_secret="secret", title="Storebot", show=False)
