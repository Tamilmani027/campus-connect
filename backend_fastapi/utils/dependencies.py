from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from backend_fastapi.database import get_db
from backend_fastapi.utils.jwt_handler import verify_token
from backend_fastapi.models.student import Student


def require_admin(authorization: str = Header(None)):
    """Validate admin JWT from Authorization header and return its payload."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth header")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return payload


def get_current_student(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Return the authenticated student instance using the bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Student authentication required")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    payload = verify_token(token)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Student privileges required")
    student = db.query(Student).filter(Student.id == payload.get("sid")).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    return student


