from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, time, datetime


class UserCreate(BaseModel):
    name: str = Field(..., description="User's full name")
    birth_date: date = Field(..., description="User's birth date")
    birth_time: Optional[time] = Field(None, description="User's birth time")
    birth_place: Optional[str] = Field(None, description="User's birth place")


class UserResponse(BaseModel):
    id: int
    name: str
    birth_date: date
    birth_time: Optional[time]
    birth_place: Optional[str]
    zodiac: str
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HoroscopeRequest(BaseModel):
    user_id: int = Field(..., description="User ID to get horoscope for")
    date: Optional[date] = None


class HoroscopeDirectRequest(BaseModel):
    name: str = Field(..., description="User's full name")
    birth_date: date = Field(..., description="User's birth date")
    birth_time: Optional[str] = Field(None, description="User's birth time (HH:MM format)")
    birth_place: Optional[str] = Field(None, description="User's birth place")
    language: Optional[str] = Field("en", description="Target language for horoscope (e.g., 'en', 'hi', 'bn', 'ta')")


class HoroscopeDirectResponse(BaseModel):
    zodiac: str
    insight: str
    language: str = "en"


class PanchangData(BaseModel):
    nakshatra: Optional[str] = None
    tithi: Optional[str] = None
    yoga: Optional[str] = None
    weekday: Optional[str] = None


class HoroscopeResponse(BaseModel):
    name: str
    zodiac: str
    date: str
    panchang_used: bool
    panchang_data: Optional[PanchangData] = None
    message: str
