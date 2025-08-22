"""
Application startup module to initialize all services.
"""

import logging
from app.database import create_tables
from app.services.chroma_service import ChromaService
# from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

# Global service instances
chroma_service = None
translation_service = None

def initialize_services():
    """Initialize all services during application startup."""
    global chroma_service, translation_service
    
    logger.info("🚀 Starting Astrochat services initialization...")
    
    try:
        # Step 1: Initialize database tables
        logger.info("🗄️ Initializing database tables...")
        create_tables()
        logger.info("✅ Database tables initialized successfully!")
        
        # Step 2: Initialize ChromaDB and load data
        logger.info("📊 Initializing ChromaDB and loading horoscope data...")
        chroma_service = ChromaService()
        
        # Check if data is already loaded
        try:
            collections = chroma_service.client.list_collections()
            if collections:
                logger.info("✅ ChromaDB already has data loaded")
            else:
                logger.info("📄 Loading horoscope data into ChromaDB...")
                success = chroma_service.load_horoscope_data("archive/horoscope_saved.csv")
                if success:
                    logger.info("✅ ChromaDB data loaded successfully!")
                else:
                    logger.error("❌ Failed to load ChromaDB data")
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization error: {e}")
        
        # Step 3: Translation service disabled
        # logger.info("🌐 Initializing translation service...")
        # translation_service = TranslationService()
        # 
        # if translation_service.is_initialized:
        #     logger.info("✅ Translation service initialized successfully!")
        # else:
        #     logger.warning("⚠️ Translation service initialization failed - will use English only")
        
        logger.info("🌐 Translation service disabled - using English only")
        translation_service = None
        
        logger.info("🎉 All services initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False

def get_chroma_service():
    """Get the global ChromaDB service instance."""
    return chroma_service

def get_translation_service():
    """Get the global translation service instance."""
    return translation_service
