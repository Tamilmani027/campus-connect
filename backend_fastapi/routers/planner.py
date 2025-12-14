from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from ..database import get_db
from ..models import planner as models
from ..schemas import planner as schemas
from ..models.student import Student
from ..utils.dependencies import get_current_student, require_admin

router = APIRouter(
    prefix="/planner",
    tags=["planner"],
    responses={404: {"description": "Not found"}},
)

# --- Student Routes ---

@router.get("/plans", response_model=List[schemas.StudyPlanOut])
def list_available_plans(db: Session = Depends(get_db)):
    # Return all plans with their tasks
    return db.query(models.StudyPlan).all()

@router.get("/my-subscription", response_model=schemas.SubscriptionOut) 
# Fix: The return type annotation might fail if I reference it wrong, let's skip complex annotation for now or fix imports
# Actually, let's use the schema properly.
def get_my_subscription(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    sub = db.query(models.StudentSubscription).filter(
        models.StudentSubscription.student_id == current_student.id,
        models.StudentSubscription.is_active == True
    ).first()
    
    if not sub:
        return None
        
    # Manually attach plan because Pydantic needs it and we might not have lazy load set up perfectly
    plan = db.query(models.StudyPlan).filter(models.StudyPlan.id == sub.plan_id).first()
    
    # Parse completed tasks
    completed_ids = json.loads(sub.completed_tasks) if sub.completed_tasks else []
    
    # Construct response manually or map it
    return {
        "id": sub.id,
        "student_id": sub.student_id,
        "plan_id": sub.plan_id,
        "start_date": sub.start_date,
        "current_day": sub.current_day,
        "is_active": sub.is_active,
        "plan": plan,
        "completed_tasks_list": completed_ids
    }

@router.post("/plans/{plan_id}/subscribe")
def subscribe_to_plan(
    plan_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Check if already subscribed
    existing = db.query(models.StudentSubscription).filter(
        models.StudentSubscription.student_id == current_student.id,
        models.StudentSubscription.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="You already have an active study plan.")
        
    plan = db.query(models.StudyPlan).filter(models.StudyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    new_sub = models.StudentSubscription(
        student_id=current_student.id,
        plan_id=plan_id
    )
    db.add(new_sub)
    db.commit()
    return {"status": "subscribed", "plan_title": plan.title}

@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    sub = db.query(models.StudentSubscription).filter(
        models.StudentSubscription.student_id == current_student.id,
        models.StudentSubscription.is_active == True
    ).first()
    
    if not sub:
        raise HTTPException(status_code=400, detail="No active subscription")
        
    completed = json.loads(sub.completed_tasks) if sub.completed_tasks else []
    
    if task_id not in completed:
        completed.append(task_id)
        sub.completed_tasks = json.dumps(completed)
        db.commit()
        
    return {"status": "success", "completed_count": len(completed)}

# --- Admin Routes (Seeding) ---

@router.post("/seed", dependencies=[Depends(require_admin)])
def seed_plan(db: Session = Depends(get_db)):
    # Create a sample plan if none exists
    if db.query(models.StudyPlan).count() > 0:
        return {"msg": "Plans already exist"}
        
    plan = models.StudyPlan(
        title="30 Days of DSA",
        description="A comprehensive guide to master Data Structures and Algorithms in one month.",
        duration_days=30
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    tasks = [
        models.DailyTask(plan_id=plan.id, day_number=1, title="Arrays Basics", description="Learn about Arrays, memory layout.", reference_link="https://www.geeksforgeeks.org/array-data-structure/"),
        models.DailyTask(plan_id=plan.id, day_number=1, title="Solve Two Sum", description="Try the Two Sum problem.", reference_link="/practice/question/1"),
        models.DailyTask(plan_id=plan.id, day_number=2, title="String Manipulation", description="Learn about Strings and common operations."),
        models.DailyTask(plan_id=plan.id, day_number=3, title="Linked Lists", description="Singly and Doubly Linked Lists."),
    ]
    db.add_all(tasks)
    db.commit()
    
    return {"msg": "Seeded '30 Days of DSA' plan"}
