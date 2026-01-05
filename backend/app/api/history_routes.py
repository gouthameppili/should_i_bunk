from fastapi import APIRouter, Depends
from typing import List
from app.db.mongodb import db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.history import ScanLog

router = APIRouter()

@router.get("/my-logs", response_model=List[ScanLog])
async def get_my_history(current_user: dict = Depends(get_current_user)):
    database = db.client[settings.DATABASE_NAME]
    
    # FIX: Use "sub" because security.py now returns {"sub": "email@..."}
    user_id = current_user["sub"]
    
    # Fetch logs for THIS user only, sorted by newest first
    cursor = database["history"].find({"username": user_id}).sort("timestamp", -1).limit(10)
    
    logs = []
    async for document in cursor:
        # Convert ObjectId to string for Pydantic
        document["_id"] = str(document["_id"])
        logs.append(document)
        
    return logs