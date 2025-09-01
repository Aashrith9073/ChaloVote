from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services import trip_service
from app.services import ai_service
from app import schemas

router = APIRouter(
    prefix="/trips",  # All routes in this file will start with /trips
    tags=["Trips"]    # This groups them nicely in the docs
)

@router.post("/", response_model=schemas.Trip)
def create_new_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    """
    Create a new trip and add its participants.
    """
    return trip_service.create_trip(db=db, trip=trip)

@router.post("/{trip_id}/generate-recommendations", response_model=List[schemas.Recommendation])
def generate_trip_recommendations(trip_id: int, db: Session = Depends(get_db)):
    """
    Triggers the AI to generate travel recommendations for a specific trip.
    """
    recommendations = ai_service.generate_recommendations(trip_id=trip_id, db=db)
    return recommendations