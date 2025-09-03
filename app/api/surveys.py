
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import models, schemas

router = APIRouter(tags=["Surveys"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/survey/{participant_id}", response_class=HTMLResponse)
def get_survey_form(request: Request, participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    return templates.TemplateResponse(
        "survey.html",
        {
            "request": request,
            "trip_name": participant.trip.name,
            "contact_info": participant.contact_info,
            "participant_id": participant.id
        }
    )

@router.post("/surveys/{participant_id}")
def submit_survey(participant_id: int,location: str = Form(), budget: str = Form(), interests: str = Form(), db: Session = Depends(get_db)):
    # In a real app, you'd have more robust validation
    preferences = {
        "budget": budget,
        "interests": [interest.strip() for interest in interests.split(',')]
    }
    participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if participant:
        participant.start_location = location

    survey_response = models.SurveyResponse(
        participant_id=participant_id,
        preferences=preferences
    )
    db.add(survey_response)
    db.commit()
    return {"message": "Thank you for submitting your preferences!"}