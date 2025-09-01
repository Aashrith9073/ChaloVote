
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app import models, schemas
from app.services import voting_service

router = APIRouter(tags=["Voting"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/trip/{trip_id}/vote/{participant_id}", response_class=HTMLResponse)
def get_voting_page(request: Request, trip_id: int, participant_id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    return templates.TemplateResponse(
        "vote.html",
        {
            "request": request,
            "trip": trip,
            "recommendations": trip.recommendations
        }
    )

@router.post("/trip/{trip_id}/vote/{participant_id}")
async def submit_vote(request: Request, participant_id: int, db: Session = Depends(get_db)):
    form_data = await request.form()

    # Convert form data (e.g., {"rank_1": "2", "rank_2": "1"}) to a sorted list
    ranked_votes = sorted(form_data.items(), key=lambda item: int(item[1]))

    # Extract just the recommendation IDs in their ranked order
    ranked_ids = [int(key.split('_')[1]) for key, value in ranked_votes]

    # Check if this participant has already voted
    existing_vote = db.query(models.Vote).filter(models.Vote.participant_id == participant_id).first()
    if existing_vote:
        existing_vote.ranked_choices = ranked_ids
    else:
        new_vote = models.Vote(participant_id=participant_id, ranked_choices=ranked_ids)
        db.add(new_vote)

    db.commit()
    return {"message": "Vote submitted successfully!"}


@router.get("/trip/{trip_id}/results", response_model=schemas.Recommendation)
def get_trip_results(trip_id: int, db: Session = Depends(get_db)):
    """
    Tallies the votes for a trip and returns the winning destination.
    """
    winner = voting_service.tally_votes(trip_id=trip_id, db=db)

    if winner:
        # Finalize the trip by updating its status
        trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
        trip.status = "completed"
        db.commit()

    return winner