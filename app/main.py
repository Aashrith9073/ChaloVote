from fastapi import FastAPI
from .core import database
from .api import trips

# This line tells SQLAlchemy to create all the tables based on your models
# It's good for development, but for production, a tool like Alembic is recommended
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ChaloVote")

# Include the routes from your trips API file
app.include_router(trips.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ChaloVote! 🌍"}