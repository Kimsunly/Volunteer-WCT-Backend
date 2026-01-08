"""
Configuration settings for the application
"""
import os
from pathlib import Path

# Get the base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

# Manually read and parse .env file
def load_env_file(filepath):
    """Manually load environment variables from .env file"""
    env_vars = {}
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig strips BOM automatically
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    env_vars[key] = value
    return env_vars

# Load environment variables
env_vars = load_env_file(dotenv_path)

class Settings:
    # App Settings
    APP_NAME = "Volunteer Platform API"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Supabase Settings - Use env_vars directly first, fallback to os.getenv
    SUPABASE_URL = env_vars.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = env_vars.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    
    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # File Upload
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    STORAGE_AVATAR_BUCKET = os.getenv("AVATAR_BUCKET", "avatars")
    
    # Validation
    def validate(self):
        """Validate required settings"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required in .env file")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required in .env file")
        return True

settings = Settings()
settings.validate()