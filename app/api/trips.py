from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.services import trip_service
from app.services import ai_service
from app import schemas
from fastapi.responses import HTMLResponse

from fastapi import Form
from typing import List

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/trips",  # All routes in this file will start with /trips
    tags=["Trips"]    # This groups them nicely in the docs
)

@router.post("/", response_model=schemas.Trip)
def create_new_trip(
        name: str = Form(...),
        participants: List[str] = Form(...),
        db: Session = Depends(get_db)
):
    """
    Create a new trip and add its participants from form data.
    """
    # Manually create the Pydantic schemas from the form data
    participant_schemas = [schemas.ParticipantCreate(contact_info=p) for p in participants if p]
    trip_data = schemas.TripCreate(name=name, participants=participant_schemas)

    # The trip_service function doesn't need to change
    return trip_service.create_trip(db=db, trip=trip_data)

@router.post("/{trip_id}/generate-recommendations", response_model=List[schemas.Recommendation])
def generate_trip_recommendations(trip_id: int, db: Session = Depends(get_db)):
    """
    Triggers the AI to generate travel recommendations for a specific trip.
    """
    recommendations = ai_service.generate_recommendations(trip_id=trip_id, db=db)
    return recommendations


@router.get("/add-participant-input", response_class=HTMLResponse)
def add_participant_input(request: Request):
    return templates.TemplateResponse("participant_input.html", {"request": request})