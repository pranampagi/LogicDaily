import os
import sys

# Ensure backend directory is in sys.path to resolve imports uniformly
backend_path = os.path.abspath(os.path.dirname(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import questions, daily, cron, users, submissions
from database import Base, engine
import models

# Create database tables automatically on startup for development
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LogicDaily API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; we can restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Cache"],
)

# Register routers
app.include_router(questions.router)
app.include_router(daily.router)
app.include_router(cron.router)
app.include_router(users.router)
app.include_router(submissions.router)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "LogicDaily API"}
