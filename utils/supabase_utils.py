from supabase import create_client, Client as SupabaseClient
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("Init Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_supabase():
    print("[SUPABASE] Checking...")
    try:
        res = supabase.table("ping").select("*").execute()
        return True
    except Exception as e:
        print(e)
        return False
    
def login(staff_number, password):
    try:
        res = supabase.rpc("get_email_for_staff_num", {"staff_num": staff_number}).execute()
        email = res.data
        res = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if res.user and res.session:
            print('[SUPABASE] Login success as ', res.user)
            return res.user, None
        return None, "Invalid staff number or password"
    except Exception as e:
        print('[SUPABASE] Login error: ',e)
        return None, e
    
def check_login():
    try:
        res = supabase.auth.get_user()
        if res.user:
            return res.user
    except Exception as e:
        print('[SUPABASE] Check login error: ',e)
    return False

def signup(staff_number, email, password, tag_id=None):
    try:
        # Création du compte dans Supabase Auth
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if res.user:
            # Insertion dans la table staff_to_user
            data = {
                "staff_number": staff_number,
                "user_id": res.user.id,
                "tag_id": tag_id
            }
            supabase.table("staff_to_user").insert(data).execute()
            print('[SUPABASE] Signup success as', res.user)
            return res.user
        return None
    except Exception as e:
        print('[SUPABASE] Signup error:', e)
        return None

def get_orders(user_id):
    try:
        res = supabase.table("orders").select("*").eq("user_id", user_id).execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("[SUPABASE] Error fetching orders:", e)
        return []


def get_order_items(order_id):
    try:
        # Effectue une requête en joignant la table boxes et, via celle-ci, material_types pour récupérer le nom de l'objet
        res = supabase.table("order_items").select(
            "*, item_id(id, name, image, characteristics)"
        ).eq("order_id", order_id).execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("[SUPABASE] Error fetching order items:", e)
        return []


def get_all_items():
    try:
        res = supabase.table("boxes").select("*, material_types(name, image)").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("[SUPABASE] Error fetching items:", e)
        return []
    
def get_box(item_id):
    try:
        res = supabase.table("boxes").select("*").eq("material_type_id", item_id).execute()
        return res.data[0] if res.data is not None else {}
    except Exception as e:
        print("[SUPABASE] Error fetching box:", e)
        return {}

def toggle_order_item(order_item_id):
    try:
        # Récupérer l'order_item avec les informations de la boîte (row et col)
        res = supabase.table("order_items").select("*, item_id(row, col, material_types(type))").eq("id", order_item_id).execute()
        if not res.data or len(res.data) == 0:
            return None
        item = res.data[0]
        current_status = item.get("status", "pending")
        # Déterminer le nouveau statut :
        # Si l'item n'est pas encore récupéré, on passe à "retrieved"
        # Sinon, si déjà récupéré et que l'item est durable (type != 'consommable'), on passe à "returned"
        joined = item.get("item_id", {})
        mat_type = joined.get("material_types", {}) or {}
        item_type = mat_type.get("type", "consommable")
        if current_status != "retrieved":
            new_status = "retrieved"
        else:
            # Seul le matériel durable peut être redéposé
            new_status = "returned" if item_type != "consommable" else current_status

        # Mise à jour de l'order_item dans Supabase
        update_res = supabase.table("order_items").update({"status": new_status}).eq("id", order_item_id).execute()
        # Récupérer la position de la boîte
        row = joined.get("row", "?")
        col = joined.get("col", "?")
        position = f"Ligne {row} / Colonne {col}"
        return {"status": new_status, "position": position, "type": item_type}
    except Exception as e:
        print("[SUPABASE] Error toggling order item:", e)
        return None


