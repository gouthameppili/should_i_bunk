from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ScanLog(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str
    filename: str
    overall_attendance: float
    prediction: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True