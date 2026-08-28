import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    _cors = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS_ORIGINS = [origin.strip() for origin in _cors.split(",")]
