from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os


load_dotenv()
FLIC_TOKEN = os.getenv("FLIC_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

app = FastAPI(
    title="Socialverse Feed API",
    version="1.0",
    description="API for personalized and category-specific video recommendations using a hybrid recommendation model"
)
@app.get("/health")
def health_check():
    return {"status": "alive"}
from app.routes.feed import router as feed_router
app.include_router(feed_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
