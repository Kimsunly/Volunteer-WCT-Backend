from supabase import create_client, Client, ClientOptions
from app.config import settings

def get_supabase() -> Client:
    # Use ClientOptions to disable session persistence
    # This prevents sign_in calls from modifying the client's state globally
    # AND returning a fresh client ensures isolation between requests.
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=ClientOptions(persist_session=False)
    )