"""
Horoscope Generation Module
Handles AI horoscope generation using Gemini API with vector store integration
"""

import json
import re
from typing import List, Dict, Optional, Any
from datetime import date

import google.generativeai as genai
from .config import settings
from .models import PanchangData


class GeminiService:
    """Generates horoscopes using Gemini API with vector store integration"""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with error handling"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
            self.client = None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API with error handling and retry logic"""
        if not self.client:
            print("❌ Gemini client not initialized")
            return None
        
        try:
            print("🤖 Calling Gemini API...")
            response = self.client.generate_content(prompt)
            
            if not response or not response.text:
                print("❌ Empty response from Gemini")
                return None
            
            print("✅ Gemini API response received successfully")
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return None
    
    def generate_horoscope(
        self,
        user_name: str,
        zodiac: str,
        retrieved_horoscopes: List[Dict[str, Any]],
        panchang_data: Optional[PanchangData] = None
    ) -> str:
        """Generate horoscope using retrieved data and optional Panchang context"""
        try:
            print(f"🔍 Generating horoscope for {user_name} ({zodiac})")
            print(f"📊 Retrieved {len(retrieved_horoscopes)} horoscope entries from vector store")
            
            # Print vector results for debugging
            self._print_vector_results(retrieved_horoscopes)
            
            horoscope_text = self._format_retrieved_horoscopes_by_category(retrieved_horoscopes)
            
            # Build single unified prompt
            prompt = self._build_unified_prompt(user_name, zodiac, horoscope_text, panchang_data)
            
            print("📝 Generated prompt for LLM")
            
            response = self._call_gemini(prompt)
            if response:
                print("✨ Horoscope generated successfully")
                return response
            
            # Fallback if API fails
            print("⚠️ Using fallback horoscope due to API failure")
            return self._generate_fallback_horoscope(user_name, zodiac)
            
        except Exception as e:
            print(f"❌ Error generating horoscope: {e}")
            return self._generate_fallback_horoscope(user_name, zodiac)
    
    def generate_coherent_horoscope(
        self,
        user_name: str,
        zodiac: str,
        retrieved_horoscopes: List[Dict[str, Any]],
        panchang_data: Optional[PanchangData] = None
    ) -> str:
        """Generate coherent horoscope insight from multiple category recommendations"""
        print(f"\n🤖 DEBUG: Gemini service - Starting coherent horoscope generation")
        print(f"👤 DEBUG: User: {user_name}, Zodiac: {zodiac}")
        print(f"📊 DEBUG: Retrieved {len(retrieved_horoscopes)} horoscope entries from vector store")
        
        try:
            print(f"🔍 DEBUG: Generating coherent horoscope for {user_name} ({zodiac})")
            
            # Print vector results for debugging
            self._print_vector_results(retrieved_horoscopes)
            
            print(f"📝 DEBUG: Formatting horoscope text for LLM...")
            horoscope_text = self._format_retrieved_horoscopes_by_category(retrieved_horoscopes)
            print(f"📄 DEBUG: Formatted text length: {len(horoscope_text)} characters")
            
            # Build single unified prompt
            print(f"🔧 DEBUG: Building unified prompt...")
            prompt = self._build_unified_prompt(user_name, zodiac, horoscope_text, panchang_data)
            print(f"📝 DEBUG: Prompt length: {len(prompt)} characters")
            
            print("📝 DEBUG: Generated prompt for LLM")
            
            print(f"🤖 DEBUG: Calling Gemini API...")
            response = self._call_gemini(prompt)
            if response:
                print("✨ DEBUG: Coherent horoscope generated successfully")
                print(f"📝 DEBUG: Response length: {len(response)} characters")
                return response
            
            # Fallback if API fails
            print("⚠️ DEBUG: Using fallback insight due to API failure")
            return self._generate_fallback_insight(user_name, zodiac)
            
        except Exception as e:
            print(f"❌ DEBUG: Error generating coherent horoscope: {e}")
            return self._generate_fallback_insight(user_name, zodiac)
    
    def _print_vector_results(self, horoscopes: List[Dict[str, Any]]):
        """Print vector results for debugging"""
        print("\n" + "="*50)
        print("VECTOR STORE RESULTS:")
        print("="*50)
        
        for i, horoscope in enumerate(horoscopes, 1):
            metadata = horoscope.get('metadata', {})
            category = metadata.get('category', 'unknown')
            date_info = metadata.get('date', 'unknown')
            distance = horoscope.get('distance', 0)
            relevance_score = 1 - distance
            
            print(f"\n{i}. Category: {category}")
            print(f"   Date: {date_info}")
            print(f"   Relevance Score: {relevance_score:.3f}")
            print(f"   Content: {metadata.get('horoscope', 'No content')[:100]}...")
        
        print("="*50 + "\n")
    
    def _format_retrieved_horoscopes_by_category(self, horoscopes: List[Dict[str, Any]]) -> str:
        """Format retrieved horoscopes by category for coherent generation"""
        formatted_text = ""
        categories = {}
        
        # Group horoscopes by category
        for horoscope in horoscopes:
            metadata = horoscope.get('metadata', {})
            category = metadata.get('category', 'general')
            horoscope_text = metadata.get('horoscope', '')
            date_info = metadata.get('date', '')
            
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'text': horoscope_text,
                'date': date_info,
                'distance': horoscope.get('distance', 0)
            })
        
        # Format by category with better structure
        for category, entries in categories.items():
            formatted_text += f"\n=== {category.upper()} HOROSCOPES ===\n"
            for i, entry in enumerate(entries, 1):
                formatted_text += f"{i}. Date: {entry['date']} | Relevance Score: {1 - entry['distance']:.3f}\n"
                formatted_text += f"   Insight: {entry['text']}\n\n"
        
        # Add summary of what was found
        total_entries = sum(len(entries) for entries in categories.values())
        formatted_text += f"\nSUMMARY: Retrieved {total_entries} relevant horoscope entries across {len(categories)} categories."
        
        return formatted_text.strip()
    
    def _build_unified_prompt(
        self,
        user_name: str,
        zodiac: str,
        horoscope_text: str,
        panchang_data: Optional[PanchangData] = None
    ) -> str:
        """Build single unified prompt for horoscope generation"""
        
        # Base context
        context = f"""
USER CONTEXT:
- Name: {user_name}
- Zodiac Sign: {zodiac}
"""
        
        # Add Panchang context if available
        if panchang_data:
            context += f"- Current Panchang: Nakshatra: {panchang_data.nakshatra}, Tithi: {panchang_data.tithi}, Yoga: {panchang_data.yoga}\n"
        
        prompt = f"""You are an expert astrologer and horoscope writer with deep knowledge of Vedic astrology and Western zodiac systems. You specialize in creating personalized, insightful horoscopes that combine traditional astrological wisdom with modern psychological insights.

{context}

VECTOR QUERY RESULTS (from ChromaDB semantic search):
Below are the most relevant horoscope entries retrieved from our database, organized by category. These represent the best matches based on zodiac sign, date, and astrological context:

{horoscope_text}

INSTRUCTIONS FOR USING VECTOR RESULTS:
1. **Analyze Patterns**: Look for recurring themes, emotions, and guidance across different categories
2. **Synthesize Insights**: Combine the most relevant elements from general, love, career, health, and money categories
3. **Maintain Authenticity**: Use the essence of the retrieved horoscopes while making them personal to {user_name}
4. **Balance Categories**: Ensure the final insight touches on multiple life areas naturally
5. **Incorporate Panchang**: Subtly weave in the nakshatra, tithi, and yoga influences (if available)

TASK:
Generate a **coherent daily horoscope insight** that:
1. Addresses {user_name} by name and zodiac sign
2. Synthesizes the best elements from the vector query results
3. Incorporates Panchang elements naturally and subtly (if available in the given prompt else do not mention it)
4. Provides specific, actionable guidance for the day
5. Maintains a warm, encouraging, and positive tone
6. Is concise (50-80 words) but meaningful
7. Feels personal and relevant to {user_name}'s {zodiac} nature

STYLE GUIDELINES:
- Use present tense and direct address
- Include specific actionable advice
- Balance optimism with realism
- Make it feel like a personal message from the stars
- Avoid generic statements - make it specific to the retrieved insights

Return only the insight text, no additional formatting or explanations."""

        return prompt
    
    def _generate_fallback_horoscope(self, user_name: str, zodiac: str) -> str:
        """Generate fallback horoscope when API fails"""
        return f"Dear {user_name}, as a {zodiac}, your natural charisma and determination will guide you through today's challenges. Trust your instincts and embrace opportunities that come your way. Stay positive and focused on your goals."
    
    def _generate_fallback_insight(self, user_name: str, zodiac: str) -> str:
        """Generate fallback insight when API fails"""
        return f"Your {zodiac} energy brings warmth and creativity to everything you do today, {user_name}. Trust your intuition and let your natural leadership shine through."
