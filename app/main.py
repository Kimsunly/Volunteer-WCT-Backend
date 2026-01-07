"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, users
from app.routers import organizer, admin

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

origins = [
    "http://localhost:3000",   
    "http://127.0.0.1:3000",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary debugging middleware to log OPTIONS preflight requests
from fastapi import Request

@app.middleware("http")
async def log_options_request(request: Request, call_next):
    if request.method == "OPTIONS":
        try:
            headers = {k: v for k, v in request.headers.items()}
            print("DEBUG OPTIONS request:", request.url.path, headers)
        except Exception as e:
            print("DEBUG: failed to log OPTIONS headers", e)
    return await call_next(request)

# Mount static files (package-relative so imports work from anywhere)
from pathlib import Path
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    print(f"⚠️  Warning: 'static' directory not found at {static_path}")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizer.router)
app.include_router(admin.router)

# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": settings.APP_NAME,
        "version": settings.VERSION,
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "supabase_url": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else "Not configured"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    try:
        settings.validate()
        print(f"✓ {settings.APP_NAME} v{settings.VERSION} started successfully")
        print(f"✓ Supabase configured: {settings.SUPABASE_URL[:30]}...")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"✓ {settings.APP_NAME} shutting down")

