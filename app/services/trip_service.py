from sqlalchemy.orm import Session
from app import models, schemas
from app.services import notification_service
from app.models.trip import Trip




def create_trip(db: Session, trip: schemas.TripCreate):
    # Create the main Trip object
    db_trip = models.Trip(name=trip.name)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    participants = []
    # Now create the Participant objects and link them to the trip
    for participant_data in trip.participants:
        db_participant = models.Participant(
            contact_info=participant_data.contact_info,
            trip_id=db_trip.id
        )
        db.add(db_participant)
        participants.append(db_participant)
    db.commit()
    for p in participants:
        # In the future, this link will point to a unique survey page
        survey_link = f"http://yourapp.com/survey/{p.id}"
        message = (f"You've been invited to the trip '{db_trip.name}'! "
                   f"Please fill out your preferences here: {survey_link}")

        notification_service.send_notification(contact_info=p.contact_info, message=message)

    db.refresh(db_trip)
    return db_trip
