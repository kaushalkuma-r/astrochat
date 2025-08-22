#!/usr/bin/env python3
"""
Test script to verify the astrochat setup.
"""

import sys
import os
from datetime import date

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.config import settings
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config module import failed: {e}")
        return False
    
    try:
        from app.utils import calculate_zodiac
        print("✅ Utils module imported successfully")
    except Exception as e:
        print(f"❌ Utils module import failed: {e}")
        return False
    
    try:
        from app.database import create_tables
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    try:
        from app.chroma_service import ChromaService
        print("✅ ChromaDB service imported successfully")
    except Exception as e:
        print(f"❌ ChromaDB service import failed: {e}")
        return False
    
    try:
        from app.gemini_service import GeminiService
        print("✅ Gemini service imported successfully")
    except Exception as e:
        print(f"❌ Gemini service import failed: {e}")
        return False
    
    try:
        from app.panchang_service import PanchangService
        print("✅ Panchang service imported successfully")
    except Exception as e:
        print(f"❌ Panchang service import failed: {e}")
        return False
    
    return True

def test_zodiac_calculation():
    """Test zodiac calculation functionality."""
    print("\nTesting zodiac calculation...")
    
    from app.utils import calculate_zodiac
    
    test_cases = [
        (date(1995, 8, 15), "leo"),
        (date(1990, 1, 1), "capricorn"),
        (date(1985, 6, 21), "gemini"),
        (date(2000, 12, 25), "capricorn"),
    ]
    
    for birth_date, expected_zodiac in test_cases:
        calculated_zodiac = calculate_zodiac(birth_date)
        if calculated_zodiac == expected_zodiac:
            print(f"✅ {birth_date} → {calculated_zodiac}")
        else:
            print(f"❌ {birth_date} → {calculated_zodiac} (expected {expected_zodiac})")
            return False
    
    return True

def test_chroma_service():
    """Test ChromaDB service initialization."""
    print("\nTesting ChromaDB service...")
    
    try:
        from app.services.chroma_service import ChromaService
        chroma_service = ChromaService()
        info = chroma_service.get_collection_info()
        print(f"✅ ChromaDB service initialized: {info}")
        return True
    except Exception as e:
        print(f"❌ ChromaDB service test failed: {e}")
        return False

def test_panchang_service():
    """Test Panchang service functionality."""
    print("\nTesting Panchang service...")
    
    try:
        from app.services.panchang_service import PanchangService
        panchang_service = PanchangService()
        
        # Test mock data generation
        test_date = date(2025, 1, 21)
        panchang_data = panchang_service._get_mock_panchang_data(test_date)
        
        print(f"✅ Panchang service test successful:")
        print(f"   Date: {test_date}")
        print(f"   Nakshatra: {panchang_data.nakshatra}")
        print(f"   Tithi: {panchang_data.tithi}")
        print(f"   Yoga: {panchang_data.yoga}")
        print(f"   Weekday: {panchang_data.weekday}")
        
        return True
    except Exception as e:
        print(f"❌ Panchang service test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🌌 Astrochat Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_zodiac_calculation,
        test_chroma_service,
        test_panchang_service,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test failed: {test.__name__}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your astrochat setup is ready.")
        print("\nNext steps:")
        print("1. Set up your .env file with database and API credentials")
        print("2. Run: python main.py")
        print("3. Load data: curl -X POST http://localhost:8000/load-data")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
