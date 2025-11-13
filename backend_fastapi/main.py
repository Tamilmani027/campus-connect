from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, companies, experiences, admin, students, content
import logging

# Import models to ensure they are registered
from . import models  # ensures models are imported

app = FastAPI(title="Placement Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
	"""Create database tables on startup (use Alembic for production)"""
	try:
		Base.metadata.create_all(bind=engine)
		logger.info("Database tables created successfully")
	except Exception as e:
		logger.error(f"Failed to create database tables: {e}")
		logger.warning("Application will continue, but database operations may fail")

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(experiences.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(content.router)

@app.get("/")
def read_root():
	return {"msg": "Placement Portal API — FastAPI backend running"}
