import platform
import signal
from utils.supabase_utils import supabase

# Vérifier si on tourne sur un Raspberry Pi
# Les Raspberry Pi utilisent généralement 'armv7l' ou 'aarch64'
if platform.machine() in ('armv7l', 'aarch64'):
    try:
        import MFRC522
    except ImportError:
        print("La bibliothèque MFRC522 n'est pas disponible.")
        MFRC522 = None
else:
    print("RFID non supporté sur cette plateforme.")
    MFRC522 = None


def uid_to_string(uid):
    """
    Convertit une liste d'entiers (UID) en une chaîne hexadécimale.
    """
    mystring = ""
    for i in uid:
        mystring = format(i, '02X') + mystring
    return mystring


def read_badge():
    """
    Lance la lecture d'un badge RFID en boucle et retourne l'UID (sous forme de chaîne hexadécimale)
    dès qu'un badge est détecté.
    Si la lecture RFID n'est pas supportée sur cette plateforme, retourne None.
    """
    if MFRC522 is None:
        print("Lecture RFID indisponible sur cette plateforme.")
        return None

    continue_reading = True

    def end_read(sig, frame):
        nonlocal continue_reading
        print("Ctrl+C capturé, arrêt de la lecture.")
        continue_reading = False

    # Intercepter Ctrl-C pour quitter proprement
    signal.signal(signal.SIGINT, end_read)

    MIFAREReader = MFRC522.MFRC522()
    print("Attente d'un badge RFID... (Appuyez sur Ctrl-C pour arrêter)")
    while continue_reading:
        # Scanner les cartes
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            # Une carte est détectée, on récupère son UID
            (status, uid) = MIFAREReader.MFRC522_SelectTagSN()
            if status == MIFAREReader.MI_OK:
                badge = uid_to_string(uid)
                print("Badge détecté:", badge)
                return badge
    return None


def get_staff_number_by_badge():
    """
    Lance la lecture d'un badge RFID, convertit l'UID en valeur numérique,
    et interroge Supabase (table staff_to_user) pour retrouver le staff_number correspondant.
    Retourne le staff_number si trouvé, sinon None.
    """
    badge = read_badge()
    if badge:
        try:
            # Convertir l'UID (en hexadécimal) en entier
            badge_numeric = int(badge, 16)
        except Exception as e:
            print("Erreur lors de la conversion du badge UID en nombre:", e)
            return None

        try:
            # Requête dans Supabase : rechercher dans la table staff_to_user un enregistrement dont tag_id correspond au badge numérique
            res = supabase.table("staff_to_user").select("staff_number").eq("tag_id", badge_numeric).execute()
            if res.data and len(res.data) > 0:
                staff_number = res.data[0]["staff_number"]
                print("Staff number trouvé:", staff_number)
                return staff_number
            else:
                print("Aucun staff trouvé pour le badge:", badge_numeric)
                return None
        except Exception as e:
            print("Erreur lors de la requête Supabase:", e)
            return None
    return None
