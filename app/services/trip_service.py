from sqlalchemy.orm import Session
from app import models, schemas


def create_trip(db: Session, trip: schemas.TripCreate):
    # Create the main Trip object
    db_trip = models.Trip(name=trip.name)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    # Now create the Participant objects and link them to the trip
    for participant_data in trip.participants:
        db_participant = models.Participant(
            contact_info=participant_data.contact_info,
            trip_id=db_trip.id
        )
        db.add(db_participant)

    db.commit()
    db.refresh(db_trip)
    return db_trip