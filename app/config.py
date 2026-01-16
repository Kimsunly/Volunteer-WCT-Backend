"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App Settings
    APP_NAME = "Volunteer Platform API"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Supabase Settings
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hyidxiytjwxknerdrpua.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5aWR4aXl0and4a25lcmRycHVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzUzNzg3MCwiZXhwIjoyMDgzMTEzODcwfQ.Fm1yVH9ZOJ-sGbegEbik8hZYYFnl9HJOBXpZo5GFuDk")
    
    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Allow overriding origins via environment variable
    _env_origins = os.getenv("ALLOWED_ORIGINS")
    if _env_origins:
        # Check if it's the wildcard "*"
        if _env_origins.strip() == "*":
            ALLOWED_ORIGINS = ["*"]
        else:
            try:
                import json
                parsed_origins = json.loads(_env_origins)
                if isinstance(parsed_origins, list):
                    ALLOWED_ORIGINS = parsed_origins
                else:
                    ALLOWED_ORIGINS = [str(parsed_origins)]
            except Exception:
                # Fallback: split by comma if not valid JSON
                ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()]
    
    # File Upload
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    # Storage buckets (override via env vars if your buckets are named differently)
    STORAGE_AVATAR_BUCKET = os.getenv("AVATAR_BUCKET", "avatars")
    STORAGE_OPPORTUNITY_BUCKET = os.getenv("OPPORTUNITY_BUCKET", "opportunity-images")
    STORAGE_CV_BUCKET = os.getenv("CV_BUCKET", "cvs")
    
    # Validation
    def validate(self):
        """Validate required settings"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required")
        return True

settings = Settings()