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
            "*, boxes(material_type_id, row, col, stack_level, stock, status, material_types(name, image, characteristics))"
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

