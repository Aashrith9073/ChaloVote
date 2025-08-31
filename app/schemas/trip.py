
from pydantic import BaseModel
from typing import List, Optional

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

    class Config:
        from_attributes = True # Pydantic V2
        # orm_mode = True # Pydantic V1