from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from app.core.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Status can be: 'planning', 'voting', 'completed'
    status = Column(String, default="planning")

    winner_recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    recommendations = relationship("Recommendation", foreign_keys="[Recommendation.trip_id]", back_populates="trip")


    winner = relationship("Recommendation", foreign_keys=[winner_recommendation_id])
    participants = relationship("Participant", back_populates="trip")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    # You can store phone numbers or emails here for notifications
    contact_info = Column(String, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    start_location = Column(String, nullable=True)

    # This links a Participant back to its Trip
    trip = relationship("Trip", back_populates="participants")
    survey_response = relationship("SurveyResponse", uselist=False, back_populates="participant")
    __table_args__ = (UniqueConstraint('contact_info', 'trip_id', name='_contact_trip_uc'),)


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"))

    # We use JSON to store flexible survey data
    preferences = Column(JSON)

    participant = relationship("Participant", back_populates="survey_response")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    destination_name = Column(String)
    reason = Column(String)
    estimated_budget = Column(String)
    details = Column(JSON, nullable=True)  # <-- ADD THIS LINE

    trip = relationship("Trip", back_populates="recommendations", foreign_keys=[trip_id])

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"))
    # Storing ranked list of recommendation IDs, e.g., [3, 1, 2]
    ranked_choices = Column(JSON)
    __table_args__ = (UniqueConstraint('participant_id', name='_participant_vote_uc'),)