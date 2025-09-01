
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Participant Schemas ---
class ParticipantBase(BaseModel):
    contact_info: str

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    id: int
    trip_id: int

    class Config:
        from_attributes = True # Pydantic V2
        # orm_mode = True # Pydantic V1

class RecommendationBase(BaseModel):
    destination_name: str
    reason: str
    estimated_budget: str

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: int
    trip_id: int

    class Config:
        from_attributes = True

# --- Trip Schemas ---
class TripBase(BaseModel):
    name: str

class TripCreate(TripBase):
    # When creating a new trip, we expect a list of participants
    participants: List[ParticipantCreate]

class Trip(TripBase):
    id: int
    status: str
    # When we retrieve a trip, we want to see its participants
    participants: List[Participant] = []
    recommendations: List[Recommendation] = []
    winner: Optional[Recommendation] = None

    class Config:
        from_attributes = True # Pydantic V2
        # orm_mode = True # Pydantic V1

class SurveyResponseCreate(BaseModel):
    preferences: Dict[str, Any]

class VoteCreate(BaseModel):
    ranked_choices: List[int] # A list of recommendation IDs in order of preference
