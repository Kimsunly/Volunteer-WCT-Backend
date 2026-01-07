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
    
    # File Upload
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    # Storage buckets (override via AVATAR_BUCKET env var if your bucket is named differently, e.g. 'avatar')
    STORAGE_AVATAR_BUCKET = os.getenv("AVATAR_BUCKET", "avatars")
    
    # Validation
    def validate(self):
        """Validate required settings"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required")
        return True

settings = Settings()