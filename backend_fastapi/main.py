from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import database and routers with a fallback so the module works both when
# imported as a package and when executed in environments that don't set
# the package context (e.g. some hosting platforms invoking the module).
try:
	from .database import engine, Base
	from .routers import auth, companies, experiences, admin, students, content, analytics, drives, questions, discussion, planner, bookmarks
	# Import models to ensure they are registered
	from . import models  # ensures models are imported
except Exception:
	from backend_fastapi.database import engine, Base
	from backend_fastapi.routers import auth, companies, experiences, admin, students, content, analytics, drives, questions, discussion, planner, bookmarks
	# Import models to ensure they are registered
	import backend_fastapi.models as models

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
app.include_router(analytics.router)
app.include_router(drives.router)
app.include_router(questions.router)
app.include_router(discussion.router)
app.include_router(planner.router)
app.include_router(bookmarks.router)

@app.get("/")
def read_root():
	return {"msg": "Placement Portal API — FastAPI backend running"}


@app.get("/health")
def health_check():
	return {"status": "ok"}
