
import json
from datetime import date
from pydantic import ValidationError
from app.models.opportunity import OpportunityResponse

def test_validation():
    # Example data from a real Supabase response
    # (Based on the columns we found earlier)
    data = {
        "id": 1,
        "organizer_id": 2,
        "title": "Test Title",
        "title_en": "Test Title EN",
        "category_label": "Education",
        "location_label": "Phnom Penh",
        "description": "Test Description",
        "is_private": True,
        "access_key": "ABCDEFGHIJKL",
        "date_range": "2024-03-15",
        "time_range": "09:00 AM - 05:00 PM", # Mismatch with 'time' object if it was used, but it's 'str' now
        "capacity": 50,
        "transport": "Bus",
        "housing": "None",
        "meals": "Lunch",
        "organization": "Test Org",
        "skills": ["skill1", "skill2"],
        "tasks": ["task1", "task2"],
        "impact_description": "Test Impact",
        "status": "active",
        "visibility": "private",
        "created_at": "2026-01-16T12:13:00.000Z"
    }
    
    try:
        opp = OpportunityResponse(**data)
        print("Validation SUCCESSFUL!")
        print(opp.model_dump_json(indent=2))
    except ValidationError as e:
        print(f"Validation FAILED: {e}")

if __name__ == "__main__":
    test_validation()
