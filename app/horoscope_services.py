from datetime import date, datetime, time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database import User
from app.models import PanchangData, HoroscopeResponse, HoroscopeDirectRequest, HoroscopeDirectResponse
from app.utils import calculate_zodiac
from app.services.panchang_service import PanchangService
from app.services.chroma_service import ChromaService
from app.services.gemini_service import GeminiService
from app.services.cache_service import CacheService
from app.services.translation_service import TranslationService


class HoroscopeService:
    """Main service orchestrating the horoscope generation workflow."""
    
    def __init__(self):
        self.panchang_service = PanchangService()
        self.chroma_service = None  # Will be set during startup
        self.gemini_service = GeminiService()
        self.cache_service = CacheService()
        self.translation_service = None  # Will be set during startup
    
    async def generate_horoscope(
        self,
        db: Session,
        user_id: int,
        query_date: Optional[date] = None
    ) -> HoroscopeResponse:
        """
        Main workflow for generating personalized horoscope.
        
        Args:
            db: Database session
            user_id: User ID
            query_date: Date for horoscope (defaults to today)
        """
        # Set default date to today if not provided
        if query_date is None:
            query_date = date.today()
        
        # Step 1: Get user information
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Step 2: Check Panchang API availability and fetch data
        panchang_used = False
        panchang_data = None
        
        if self.panchang_service.is_available():
            panchang_data = await self.panchang_service.get_panchang_data(query_date)
            panchang_used = panchang_data is not None
        
        # Step 3: Query ChromaDB for relevant horoscopes
        panchang_dict = None
        if panchang_data:
            panchang_dict = {
                'nakshatra': panchang_data.nakshatra,
                'tithi': panchang_data.tithi,
                'yoga': panchang_data.yoga,
                'weekday': panchang_data.weekday
            }
        
        retrieved_horoscopes = self.chroma_service.query_horoscopes(
            zodiac=user.zodiac,
            query_date=query_date,
            panchang_data=panchang_dict,
            n_results=5
        )
        
        # Step 4: Generate personalized horoscope using Gemini
        horoscope_message = self.gemini_service.generate_horoscope(
            user_name=user.name,
            zodiac=user.zodiac,
            retrieved_horoscopes=retrieved_horoscopes,
            panchang_data=panchang_data
        )
        
        # Step 5: Return response
        return HoroscopeResponse(
            name=user.name,
            zodiac=user.zodiac,
            date=query_date.strftime("%Y-%m-%d"),
            panchang_used=panchang_used,
            panchang_data=panchang_data,
            message=horoscope_message
        )
    
    async def generate_horoscope_direct(
        self,
        request: HoroscopeDirectRequest,
        query_date: Optional[date] = None
    ) -> HoroscopeDirectResponse:
        """
        Generate horoscope directly from user details using vector store recommendations.
        
        Args:
            request: User details
            query_date: Date for horoscope (defaults to today)
        """
        print(f"\n🔍 DEBUG: Starting horoscope generation for {request.name}")
        print(f"📅 DEBUG: Birth date: {request.birth_date}, Birth time: {request.birth_time}, Birth place: {request.birth_place}")
        
        # Set default date to today if not provided
        if query_date is None:
            query_date = date.today()
        print(f"📅 DEBUG: Query date: {query_date}")
        
        # Step 1: Check cache first
        birth_date_str = request.birth_date.strftime("%Y-%m-%d")
        birth_time_str = request.birth_time or ""
        birth_place_str = request.birth_place or ""
        
        print(f"🔍 DEBUG: Checking cache for user: {request.name}")
        print(f"🔑 DEBUG: Cache key components - Date: {birth_date_str}, Time: {birth_time_str}, Place: {birth_place_str}")
        
        cached_response = self.cache_service.get_cached_response(
            user_name=request.name,
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            birth_place=birth_place_str
        )
        
        if cached_response:
            print(f"🎯 DEBUG: Cache HIT - Returning cached response for {request.name}")
            print(f"📋 DEBUG: Cached response: {cached_response}")
            return HoroscopeDirectResponse(
                zodiac=cached_response["zodiac"],
                insight=cached_response["insight"],
                language=cached_response["language"]
            )
        
        print(f"❌ DEBUG: Cache MISS - Generating new horoscope for {request.name}")
        
        # Step 2: Calculate zodiac from birth date
        zodiac = calculate_zodiac(request.birth_date)
        print(f"♈ DEBUG: Calculated zodiac: {zodiac}")
        
        # Step 3: Check Panchang API availability and fetch data
        print(f"🔮 DEBUG: Checking Panchang service availability...")
        panchang_used = False
        panchang_data = None
        
        if self.panchang_service.is_available():
            print(f"✅ DEBUG: Panchang service available, fetching data...")
            panchang_data = await self.panchang_service.get_panchang_data(query_date)
            panchang_used = panchang_data is not None
            if panchang_data:
                print(f"📊 DEBUG: Panchang data: Nakshatra={panchang_data.nakshatra}, Tithi={panchang_data.tithi}, Yoga={panchang_data.yoga}")
            else:
                print(f"⚠️ DEBUG: Panchang data fetch failed")
        else:
            print(f"❌ DEBUG: Panchang service not available")
        
        # Step 4: Query ChromaDB for top 2 horoscopes from each category
        panchang_dict = None
        if panchang_data:
            panchang_dict = {
                'nakshatra': panchang_data.nakshatra,
                'tithi': panchang_data.tithi,
                'yoga': panchang_data.yoga,
                'weekday': panchang_data.weekday
            }
            print(f"📋 DEBUG: Panchang dict prepared: {panchang_dict}")
        
        # Check if ChromaDB service is available
        if not self.chroma_service:
            print("❌ DEBUG: ChromaDB service not available")
            raise Exception("ChromaDB service not initialized")
        
        # Get top 2 from each category (general, love, career, health, etc.)
        categories = ["general", "love", "career", "health", "money"]
        all_horoscopes = []
        
        print(f"🔍 DEBUG: Querying ChromaDB for {len(categories)} categories...")
        for category in categories:
            print(f"📂 DEBUG: Querying category: {category}")
            category_horoscopes = self.chroma_service.query_horoscopes_by_category(
                zodiac=zodiac,
                category=category,
                query_date=query_date,
                panchang_data=panchang_dict,
                n_results=2
            )
            print(f"📊 DEBUG: Found {len(category_horoscopes)} horoscopes for {category}")
            all_horoscopes.extend(category_horoscopes)
        
        print(f"📈 DEBUG: Total horoscopes retrieved: {len(all_horoscopes)}")
        
        # Step 5: Generate coherent response using Gemini
        print(f"🤖 DEBUG: Calling Gemini service for coherent horoscope generation...")
        insight = self.gemini_service.generate_coherent_horoscope(
            user_name=request.name,
            zodiac=zodiac,
            retrieved_horoscopes=all_horoscopes,
            panchang_data=panchang_data
        )
        print(f"✨ DEBUG: Gemini response generated successfully")
        print(f"📝 DEBUG: Generated insight length: {len(insight)} characters")
        
        # Step 6: Create response
        response = HoroscopeDirectResponse(
            zodiac=zodiac.capitalize(),
            insight=insight,
            language="en"
        )
        print(f"📤 DEBUG: Response object created: {response}")
        
        # Step 6.5: Translation enabled - translate if requested
        target_language = request.language.lower() if request.language else "en"
        if target_language != "en" and self.translation_service:
            print(f"🌐 DEBUG: Translating horoscope to {target_language}...")
            response_dict = {
                "zodiac": response.zodiac,
                "insight": response.insight,
                "language": response.language
            }
            
            translated_response = self.translation_service.translate_horoscope_response(
                response_dict, target_language
            )
            
            if translated_response:
                response = HoroscopeDirectResponse(
                    zodiac=translated_response["zodiac"],
                    insight=translated_response["insight"],
                    language=translated_response["language"]
                )
                print(f"✅ DEBUG: Horoscope translated to {target_language}")
            else:
                print(f"⚠️ DEBUG: Translation failed, keeping original English response")
        elif target_language != "en" and not self.translation_service:
            print(f"⚠️ DEBUG: Translation service not available, keeping original English response")
        else:
            # Keep English response
            response.language = "en"
            print(f"🌐 DEBUG: Returning English response")
        
        # Step 7: Cache the response
        print(f"💾 DEBUG: Caching response for future requests...")
        cache_success = self.cache_service.cache_response(
            user_name=request.name,
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            birth_place=birth_place_str,
            response={
                "zodiac": response.zodiac,
                "insight": response.insight,
                "language": response.language
            }
        )
        print(f"💾 DEBUG: Cache operation {'successful' if cache_success else 'failed'}")
        
        print(f"✅ DEBUG: Horoscope generation completed for {request.name}")
        return response
    
    def load_horoscope_data(self, csv_path: str = "archive/horoscope_saved.csv"):
        """Load horoscope data into ChromaDB."""
        if self.chroma_service:
            return self.chroma_service.load_horoscope_data(csv_path)
        else:
            print("❌ ChromaDB service not available")
            return False
    
    def get_chroma_info(self) -> Dict[str, Any]:
        """Get ChromaDB collection information."""
        if self.chroma_service:
            return self.chroma_service.get_collection_info()
        else:
            return {"error": "ChromaDB service not available"}


class UserService:
    """Service for user management operations."""
    
    @staticmethod
    def create_user(
        db: Session,
        name: str,
        birth_date: date,
        birth_time: Optional[time] = None,
        birth_place: Optional[str] = None
    ) -> User:
        """Create a new user."""
        zodiac = calculate_zodiac(birth_date)
        
        user = User(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            zodiac=zodiac
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users."""
        return db.query(User).all()
