from datetime import date, datetime
from typing import Optional


def calculate_zodiac(birth_date: date) -> str:
    """Calculate zodiac sign based on birth date."""
    month = birth_date.month
    day = birth_date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "gemini"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    else:
        return "pisces"


def format_date_for_query(query_date: date) -> str:
    """Format date for ChromaDB query (YYYYMMDD format)."""
    return query_date.strftime("%Y%m%d")


def get_weekday_name(query_date: date) -> str:
    """Get weekday name for the given date."""
    weekdays = [
        "monday", "tuesday", "wednesday", "thursday", 
        "friday", "saturday", "sunday"
    ]
    return weekdays[query_date.weekday()]
