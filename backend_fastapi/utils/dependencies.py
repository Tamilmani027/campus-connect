from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
try:
    from ..database import get_db
    from .jwt_handler import verify_token
    from ..models.student import Student
except Exception:
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

def get_current_user_id_and_role(authorization: str = Header(None)):
    """
    Return (user_id, role) tuple.
    Role can be 'student' or 'admin'.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    token = authorization.split(" ")[1] if " " in authorization else authorization
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    role = payload.get("role")
    if role == "student":
        return payload.get("sid"), "student"
    elif role == "admin":
        # Admin payload might use 'id' or 'aid' or 'sub' - verify jwt_handler. Usually it's id.
        # Assuming admin payload has 'id' or 'sub' as user id. 
        # But wait, require_admin checks role='admin'.
        # Let's assume standard payload.
        return payload.get("id", payload.get("sub", 0)), "admin"
    
    raise HTTPException(status_code=403, detail="Unknown role")

def get_current_admin_or_student(authorization: str = Header(None)):
    return get_current_user_id_and_role(authorization)
