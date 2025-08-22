#!/usr/bin/env python3
"""
Test script for translation functionality
"""

import requests
import json

def test_translation():
    """Test the translation functionality."""
    
    # Test data
    test_request = {
        "name": "Priya",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Mumbai, India",
        "language": "hi"  # Hindi
    }
    
    print("🧪 Testing Translation Functionality")
    print("=" * 50)
    
    # Test 1: Get supported languages
    print("\n1. Testing supported languages endpoint...")
    try:
        response = requests.get("http://localhost:8000/languages")
        if response.status_code == 200:
            languages = response.json()
            print("✅ Supported languages retrieved successfully")
            print(f"📋 Available languages: {list(languages['supported_languages'].keys())}")
        else:
            print(f"❌ Failed to get languages: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting languages: {e}")
    
    # Test 2: Get horoscope in English
    print("\n2. Testing horoscope in English...")
    try:
        english_request = test_request.copy()
        english_request["language"] = "en"
        
        response = requests.post(
            "http://localhost:8000/horoscope",
            json=english_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ English horoscope generated successfully")
            print(f"📝 Insight: {result['insight'][:100]}...")
            print(f"🌐 Language: {result['language']}")
        else:
            print(f"❌ Failed to get English horoscope: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting English horoscope: {e}")
    
    # Test 3: Get horoscope in Hindi
    print("\n3. Testing horoscope in Hindi...")
    try:
        response = requests.post(
            "http://localhost:8000/horoscope",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hindi horoscope generated successfully")
            print(f"📝 Insight: {result['insight'][:100]}...")
            print(f"🌐 Language: {result['language']}")
        else:
            print(f"❌ Failed to get Hindi horoscope: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting Hindi horoscope: {e}")
    
    # Test 4: Get horoscope in Bengali
    print("\n4. Testing horoscope in Bengali...")
    try:
        bengali_request = test_request.copy()
        bengali_request["language"] = "bn"
        
        response = requests.post(
            "http://localhost:8000/horoscope",
            json=bengali_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bengali horoscope generated successfully")
            print(f"📝 Insight: {result['insight'][:100]}...")
            print(f"🌐 Language: {result['language']}")
        else:
            print(f"❌ Failed to get Bengali horoscope: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting Bengali horoscope: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Translation testing completed!")

if __name__ == "__main__":
    test_translation()
