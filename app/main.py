from fastapi import FastAPI, Request
from .core import database
from .api import trips, surveys, voting
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# This line tells SQLAlchemy to create all the tables based on your models
# It's good for development, but for production, a tool like Alembic is recommended
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ChaloVote")

# Include the routes from your trips API file
app.include_router(trips.router)
app.include_router(surveys.router)
app.include_router(voting.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/")
def read_root():
    return {"message": "Welcome to ChaloVote! 🌍"}