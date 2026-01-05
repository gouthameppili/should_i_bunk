from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List

# --- 1. Timetable Structure (Keep this, it's good!) ---
class UserTimetable(BaseModel):
    monday: List[str] = []
    tuesday: List[str] = []
    wednesday: List[str] = []
    thursday: List[str] = []
    friday: List[str] = []
    saturday: List[str] = []

# --- 2. Signup Model (MUST match Frontend inputs) ---
# --- 2. Signup Model (MUST match Frontend inputs) ---
class UserCreate(BaseModel):
    full_name: str 
    
    # CHANGE HERE: Removed Field(alias="email")
    # Now it happily accepts "username" from your frontend!
    username: EmailStr 
    
    password: str
    roll_number: str
    branch: str 
    
    role: str = "student"
# --- 3. Database Model (What goes into MongoDB) ---
class UserInDB(UserCreate):
    hashed_password: str
    disabled: bool = False

# --- 4. Login Model ---
class UserLogin(BaseModel):
    username: EmailStr = Field(alias="email") # Accept 'email' but call it 'username' internally
    password: str

# --- 5. Response Model ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: Optional[str] = Field(alias="_id")
    full_name: str
    username: EmailStr
    roll_number: str
    branch: str
    role: str
    timetable: Optional[UserTimetable] = None