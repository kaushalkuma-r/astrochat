import logging
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.services.chroma_service import ChromaService
from app.database import get_db
from app.models import UserCreate, UserResponse, HoroscopeRequest, HoroscopeResponse, HoroscopeDirectRequest, HoroscopeDirectResponse
from app.horoscope_services import UserService, HoroscopeService
from app.startup import initialize_services, get_chroma_service, get_translation_service

# Setup logger
logger = logging.getLogger("astrochat.api")

# Create FastAPI app
app = FastAPI(
    title="Astrochat API",
    description="A personalized horoscope API system with ChromaDB, PostgreSQL, and Google Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (will be set during startup)
horoscope_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup."""
    global horoscope_service
    
    logger.info("🚀 Starting Astrochat API initialization...")
    
    # Initialize all services
    success = initialize_services()
    
    if success:
        # Initialize horoscope service with global instances
        
        # from app.services.translation_service import TranslationService
        
        # Create horoscope service with global instances
        horoscope_service = HoroscopeService()
        horoscope_service.chroma_service = get_chroma_service()
        horoscope_service.translation_service = get_translation_service()
        
        logger.info("✅ Astrochat API initialization completed successfully!")
    else:
        logger.error("❌ Astrochat API initialization failed!")
        # Still create horoscope service but it may not have all features
        horoscope_service = HoroscopeService()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Astrochat API! 🌌",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "horoscopes": "/horoscopes",
            "horoscope": "/horoscope",
            "languages": "/languages",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    chroma_status = "active" if get_chroma_service() else "inactive"
    translation_status = "active" if get_translation_service() and get_translation_service().is_initialized else "inactive"
    
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "chromadb": chroma_status,
            "gemini": "configured",
            "translation": translation_status
        }
    }


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation."""
    try:
        translation_service = get_translation_service()
        if translation_service:
            languages = translation_service.get_supported_languages()
            return {
                "supported_languages": languages,
                "description": "Language codes for horoscope translation",
                "note": "Use these codes in the 'language' field when requesting horoscopes"
            }
        else:
            # Fallback if translation service is not available
            return {
                "supported_languages": {"en": "eng_Latn"},
                "description": "Translation service not available - only English supported",
                "note": "Translation service is not initialized"
            }
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


# User Management Endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        logger.info(f"Creating new user: {user_data.name}")
        user = UserService.create_user(
            db=db,
            name=user_data.name,
            birth_date=user_data.birth_date,
            birth_time=user_data.birth_time,
            birth_place=user_data.birth_place
        )
        logger.info(f"User created successfully with ID: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users."""
    users = UserService.get_all_users(db)
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Horoscope Endpoints
@app.post("/horoscopes", response_model=HoroscopeResponse)
async def generate_horoscope(
    request: HoroscopeRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized horoscope for a user."""
    try:
        logger.info(f"Generating horoscope for user ID: {request.user_id}, date: {request.date}")
        horoscope = await horoscope_service.generate_horoscope(
            db=db,
            user_id=request.user_id,
            query_date=request.date
        )
        logger.info(f"Horoscope generated successfully for user: {horoscope.name}")
        return horoscope
    except ValueError as e:
        logger.error(f"User not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating horoscope: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating horoscope: {str(e)}")


@app.get("/horoscopes/{user_id}")
async def get_horoscope_for_user(
    user_id: int,
    date: date = None,
    db: Session = Depends(get_db)
):
    """Generate horoscope for a user (GET endpoint for convenience)."""
    try:
        horoscope = await horoscope_service.generate_horoscope(
            db=db,
            user_id=user_id,
            query_date=date
        )
        return horoscope
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating horoscope: {str(e)}")


@app.post("/horoscope", response_model=HoroscopeDirectResponse)
async def generate_horoscope_direct(request: HoroscopeDirectRequest):
    """Generate horoscope directly from user details using vector store recommendations."""
    print(f"\n🚀 DEBUG: API endpoint called - /horoscope")
    print(f"👤 DEBUG: Request received for user: {request.name}")
    print(f"📅 DEBUG: Request details - Birth date: {request.birth_date}, Time: {request.birth_time}, Place: {request.birth_place}")
    
    try:
        logger.info(f"Generating direct horoscope for: {request.name}")
        print(f"🔍 DEBUG: Calling horoscope service...")
        
        horoscope = await horoscope_service.generate_horoscope_direct(request)
        
        print(f"✅ DEBUG: Horoscope service completed successfully")
        print(f"📤 DEBUG: Returning response: {horoscope}")
        
        logger.info(f"Direct horoscope generated successfully for: {request.name}")
        return horoscope
    except Exception as e:
        print(f"❌ DEBUG: Error in API endpoint: {e}")
        logger.error(f"Error generating direct horoscope: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating horoscope: {str(e)}")


# Data Management Endpoints
@app.post("/load-data")
async def load_horoscope_data(background_tasks: BackgroundTasks):
    """Load horoscope data into ChromaDB (runs in background)."""
    try:
        background_tasks.add_task(horoscope_service.load_horoscope_data)
        return {
            "message": "Horoscope data loading started in background",
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@app.get("/chroma-info")
async def get_chroma_info():
    """Get ChromaDB collection information."""
    try:
        info = horoscope_service.get_chroma_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ChromaDB info: {str(e)}")


@app.get("/cache-stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = horoscope_service.cache_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached horoscope responses."""
    try:
        success = horoscope_service.cache_service.clear_all_cache()
        if success:
            return {"message": "Cache cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@app.delete("/cache/invalidate")
async def invalidate_user_cache(request: HoroscopeDirectRequest):
    """Invalidate cached response for a specific user."""
    try:
        birth_date_str = request.birth_date.strftime("%Y-%m-%d")
        birth_time_str = request.birth_time or ""
        birth_place_str = request.birth_place or ""
        
        success = horoscope_service.cache_service.invalidate_cache(
            user_name=request.name,
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            birth_place=birth_place_str
        )
        
        if success:
            return {"message": f"Cache invalidated for user: {request.name}"}
        else:
            return {"message": "No cache found for user or cache disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating cache: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}
