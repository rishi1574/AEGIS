import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CORS_ORIGINS = ["http://localhost:3000"]
