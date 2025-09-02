from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.services import trip_service
from app.services import ai_service
from app import schemas, models
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
        request: Request,  # Add the request object
        name: str = Form(...),
        participants: List[str] = Form(...),
        db: Session = Depends(get_db)
):
    """
    Create a new trip and return an HTML confirmation.
    """
    participant_schemas = [schemas.ParticipantCreate(contact_info=p) for p in participants if p]
    trip_data = schemas.TripCreate(name=name, participants=participant_schemas)

    # Create the trip in the database
    created_trip = trip_service.create_trip(db=db, trip=trip_data)

    # Return the HTML template as the response
    return templates.TemplateResponse(
        "trip_created_success.html",
        {"request": request, "trip": created_trip}
    )
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


@router.get("/{trip_id}", response_class=HTMLResponse)
def get_trip_status_page(request: Request, trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()

    votes = db.query(models.Vote).join(models.Participant).filter(models.Participant.trip_id == trip_id).all()
    vote_count = len(votes)
    # Create a set of IDs for easy lookup in the template
    voted_participant_ids = {vote.participant_id for vote in votes}

    return templates.TemplateResponse(
        "trip_status.html",
        {
            "request": request,
            "trip": trip,
            "vote_count": vote_count,
            "voted_participant_ids": voted_participant_ids  # Pass the new list to the template
        }
    )