import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Should I Bunk?")
    API_V1_STR: str = "/api/v1"
    
    # Added a default string here so it doesn't crash if SECRET_KEY is missing locally
    SECRET_KEY: str = os.getenv("SECRET_KEY", "itssomethingyoushouldnotthinkaboutit")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_DETAILS: str = os.getenv("MONGO_DETAILS")
    
    # --- THE FIX ---
    # 1. Try "DATABASE_NAME" (Render standard)
    # 2. Try "MONGO_INITDB_DATABASE" (Your .env file)
    # 3. If both fail, use "should_i_bunk" (Hardcoded safety net)
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", os.getenv("MONGO_INITDB_DATABASE", "should_i_bunk"))

settings = Settings()