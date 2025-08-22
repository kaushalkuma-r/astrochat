#!/usr/bin/env python3
"""
Test script to investigate ChromaDB structure and data
"""

import chromadb
import pandas as pd
from datetime import date
from app.config import settings
from app.utils import format_date_for_query, get_weekday_name

def test_chromadb_structure():
    """Test ChromaDB structure and data"""
    print("🔍 Testing ChromaDB Structure")
    print("="*50)
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    collection_name = "horoscopes"
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"✅ Collection '{collection_name}' found")
        
        # Get collection info
        count = collection.count()
        print(f"📊 Total documents: {count}")
        
        if count == 0:
            print("❌ No documents found in collection")
            return
        
        # Get a sample of documents
        print("\n📋 Sample Documents:")
        print("-" * 30)
        
        # Get first 5 documents
        results = collection.get(limit=5)
        
        for i, (doc_id, metadata, document) in enumerate(zip(results['ids'], results['metadatas'], results['documents'])):
            print(f"\nDocument {i+1}:")
            print(f"  ID: {doc_id}")
            print(f"  Metadata: {metadata}")
            print(f"  Document: {document}")
            print(f"  Full Horoscope: {metadata.get('horoscope', 'No content')}")
        
        # Test different query approaches
        print("\n🔍 Testing Query Approaches:")
        print("-" * 30)
        
        # Test 1: Simple query without where clause
        print("\n1. Simple query without where clause:")
        try:
            results = collection.query(
                query_texts=["leo zodiac horoscope"],
                n_results=3
            )
            print(f"   Results: {len(results['ids'][0])} found")
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0], results['metadatas'][0])):
                print(f"\nResult {i+1}:")
                print(f"  ID: {doc_id}")
                print(f"  Sign: {metadata['sign']}")
                print(f"  Category: {metadata['category']}")
                print(f"  Date: {metadata['date']}")
                print(f"  Full Horoscope: {metadata['horoscope']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Query with single where condition
        print("\n2. Query with single where condition (sign only):")
        try:
            results = collection.query(
                query_texts=["leo zodiac horoscope"],
                n_results=3,
                where={"sign": "leo"}
            )
            print(f"   Results: {len(results['ids'][0])} found")
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0], results['metadatas'][0])):
                print(f"   - {doc_id}: {metadata.get('sign', 'N/A')} | {metadata.get('category', 'N/A')} | {metadata.get('date', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Query with date condition
        print("\n3. Query with date condition:")
        try:
            formatted_date = format_date_for_query(date.today())
            results = collection.query(
                query_texts=["leo zodiac horoscope"],
                n_results=3,
                where={"date": formatted_date}
            )
            print(f"   Results: {len(results['ids'][0])} found")
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0], results['metadatas'][0])):
                print(f"   - {doc_id}: {metadata.get('sign', 'N/A')} | {metadata.get('category', 'N/A')} | {metadata.get('date', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Check what dates are available
        print("\n4. Available dates in database:")
        try:
            # Get all documents to see available dates
            all_results = collection.get()
            dates = set()
            for metadata in all_results['metadatas']:
                dates.add(metadata.get('date', 'N/A'))
            
            print(f"   Available dates: {sorted(list(dates))[:10]}...")  # Show first 10
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Check what categories are available
        print("\n5. Available categories in database:")
        try:
            all_results = collection.get()
            categories = set()
            for metadata in all_results['metadatas']:
                categories.add(metadata.get('category', 'N/A'))
            
            print(f"   Available categories: {sorted(list(categories))}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Check what signs are available
        print("\n6. Available signs in database:")
        try:
            all_results = collection.get()
            signs = set()
            for metadata in all_results['metadatas']:
                signs.add(metadata.get('sign', 'N/A'))
            
            print(f"   Available signs: {sorted(list(signs))}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error accessing collection: {e}")

def test_csv_data():
    """Test the CSV data structure"""
    print("\n📄 Testing CSV Data Structure")
    print("="*50)
    
    try:
        df = pd.read_csv("archive/horoscope_saved.csv")
        print(f"✅ CSV loaded: {len(df)} rows")
        
        print(f"\nColumns: {list(df.columns)}")
        print(f"Sample data:")
        print(df.head(3))
        
        print(f"\nUnique signs: {df['sign'].unique()}")
        print(f"Unique categories: {df['category'].unique()}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

if __name__ == "__main__":
    test_csv_data()
    test_chromadb_structure()
