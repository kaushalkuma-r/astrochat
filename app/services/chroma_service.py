import chromadb
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import date
from app.config import settings
from app.utils import format_date_for_query, get_weekday_name


class ChromaService:
    """Service to handle ChromaDB operations for horoscope retrieval."""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection_name = "horoscopes"
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get the horoscope collection."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Using existing collection: {self.collection_name}")
        except:
            print(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def load_horoscope_data(self, csv_path: str = "archive/horoscope_saved.csv"):
        """Load horoscope data from CSV into ChromaDB."""
        try:
            # Read CSV data
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} horoscope entries from CSV")
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in df.iterrows():
                # Create unique ID
                doc_id = f"{row['sign']}_{row['date']}_{idx}"
                
                # Prepare document text
                doc_text = f"Zodiac: {row['sign']}, Category: {row['category']}, Date: {row['date']}, Horoscope: {row['horoscope']}"
                
                documents.append(doc_text)
                metadatas.append({
                    "sign": row['sign'],
                    "category": row['category'],
                    "date": row['date'],
                    "horoscope": row['horoscope']
                })
                ids.append(doc_id)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Successfully loaded {len(documents)} documents into ChromaDB")
            
        except Exception as e:
            print(f"Error loading horoscope data: {e}")
            raise
    
    def query_horoscopes(
        self, 
        zodiac: str, 
        query_date: date, 
        panchang_data: Optional[Dict[str, str]] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query horoscopes using deterministic filtering and semantic search.
        
        Args:
            zodiac: User's zodiac sign
            query_date: Date for horoscope
            panchang_data: Optional Panchang data for enhanced querying
            n_results: Number of results to return
        """
        try:
            # Format date for query
            formatted_date = format_date_for_query(query_date)
            weekday = get_weekday_name(query_date)
            
            # Build query text
            if panchang_data:
                # Enhanced query with Panchang data
                query_text = f"zodiac {zodiac} date {formatted_date} {weekday} {panchang_data.get('nakshatra', '')} {panchang_data.get('tithi', '')} {panchang_data.get('yoga', '')}"
            else:
                # Basic query
                query_text = f"zodiac {zodiac} date {formatted_date} {weekday}"
            
            # Perform semantic search with single where condition
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"sign": zodiac}
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying horoscopes: {e}")
            return []
    
    def query_horoscopes_by_category(
        self, 
        zodiac: str, 
        category: str,
        query_date: date, 
        panchang_data: Optional[Dict[str, str]] = None,
        n_results: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Query horoscopes by specific category.
        
        Args:
            zodiac: User's zodiac sign
            category: Horoscope category (general, love, career, etc.)
            query_date: Date for horoscope
            panchang_data: Optional Panchang data for enhanced querying
            n_results: Number of results to return (default 2)
        """
        print(f"🔍 DEBUG: ChromaDB query - Zodiac: {zodiac}, Category: {category}, Date: {query_date}, Results: {n_results}")
        
        try:
            # Format date for query
            formatted_date = format_date_for_query(query_date)
            weekday = get_weekday_name(query_date)
            print(f"📅 DEBUG: Formatted date: {formatted_date}, Weekday: {weekday}")
            
            # Build query text
            if panchang_data:
                # Enhanced query with Panchang data
                query_text = f"zodiac {zodiac} category {category} date {formatted_date} {weekday} {panchang_data.get('nakshatra', '')} {panchang_data.get('tithi', '')} {panchang_data.get('yoga', '')}"
                print(f"🔮 DEBUG: Enhanced query with Panchang: {query_text}")
            else:
                # Basic query
                query_text = f"zodiac {zodiac} category {category} date {formatted_date} {weekday}"
                print(f"🔍 DEBUG: Basic query: {query_text}")
            
            print(f"🔍 DEBUG: Executing ChromaDB query with where condition: {{'sign': '{zodiac}'}}")
            
            # Perform semantic search with single where condition
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"sign": zodiac}
            )
            
            print(f"📊 DEBUG: ChromaDB returned {len(results['ids'][0])} results for {category}")
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
                print(f"📋 DEBUG: Result {i+1} - ID: {result['id']}, Distance: {result['distance']:.4f}")
            
            print(f"✅ DEBUG: ChromaDB query successful for {category}, returning {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ DEBUG: ChromaDB query error for {category}: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "active"
            }
        except Exception as e:
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "status": f"error: {e}"
            }
