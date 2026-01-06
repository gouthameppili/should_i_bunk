from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.db.mongodb import db
from app.models.user import UserCreate


router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    # 1. Get the Database object correctly
    # We access the 'client' inside your wrapper, then pick the DB name from settings
    database = db.client[settings.DATABASE_NAME]

    # 2. Check if username exists
    existing_user = await database["users"].find_one({"username": user.username})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user.username} is already registered."
        )

    # 3. Hash Password
    hashed_password = get_password_hash(user.password)
    
    # 4. Create User Document
    user_doc = {
        "username": user.username,
        "full_name": user.full_name,
        "roll_number": user.roll_number,
        "branch": user.branch,
        "hashed_password": hashed_password,
        "role": user.role,
        "disabled": False
    }

    # 5. Insert into DB
    result = await database["users"].insert_one(user_doc)
    
    return {"message": "User created successfully", "id": str(result.inserted_id)}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Get the Database object correctly
    database = db.client[settings.DATABASE_NAME]

    # 2. Find User
    user = await database["users"].find_one({"username": form_data.username})
    
    # 3. Verify Password
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}