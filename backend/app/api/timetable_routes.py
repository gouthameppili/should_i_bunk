from fastapi import APIRouter, Depends, HTTPException
from app.db.mongodb import get_database
from app.core.security import get_current_user
from app.models.user import UserTimetable # ✅ NEW PATH

router = APIRouter()

@router.post("/", response_model=dict)
async def update_timetable(
    timetable: UserTimetable,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Saves or updates the student's weekly timetable.
    """
    user_email = current_user["email"]
    
    # Update the specific user's document with the new timetable
    result = await db["users"].update_one(
        {"email": user_email},
        {"$set": {"timetable": timetable.dict()}}
    )
    
    if result.modified_count == 0 and result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": "Timetable updated successfully! 📅"}

@router.get("/", response_model=UserTimetable)
async def get_timetable(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Retrieves the logged-in user's timetable.
    """
    user = await db["users"].find_one({"email": current_user["email"]})
    
    if not user or "timetable" not in user:
        # Return empty default if not set
        return UserTimetable()
        
    return user["timetable"]