"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, users
from app.routers import organizer, admin_comprehensive, opportunity_with_images
from app.routers import categories, blogs, community, comments, donations, contact, applications

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    redirect_slashes=False  # Prevent 307 redirects for missing trailing slashes
)

# CORS middleware
# Note: allow_credentials=True is incompatible with allow_origins=["*"]
# We handle this by setting allow_credentials based on the origins list
allow_all = "*" in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from pathlib import Path
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizer.router)
app.include_router(admin_comprehensive.router)  # Use comprehensive admin router
app.include_router(opportunity_with_images.router)
app.include_router(categories.router)
app.include_router(blogs.router)
app.include_router(community.router)
app.include_router(comments.router)
app.include_router(donations.router)
app.include_router(contact.router)
app.include_router(applications.router)

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

