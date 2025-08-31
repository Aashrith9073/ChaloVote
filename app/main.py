# app/main.py
from fastapi import FastAPI

app = FastAPI(title="ChaloVote")

@app.get("/")
def read_root():
    return {"message": "Welcome to ChaloVote! 🌍"}