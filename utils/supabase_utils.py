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
        res = supabase.table("user").select("*").execute()
        return True
    except Exception as e:
        print(e)
        return False