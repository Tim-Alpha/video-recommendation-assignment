from fastapi import FastAPI
from routes import router
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="EmpowerVerse Video Recommendation API",
    description="API for EmpowerVerse video recommendation and data collection",
    version="1.0.0"
)

# Lifespan handler for startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    required_env_vars = ["FLIC_TOKEN", "API_BASE_URL", "RESONANCE_ALGORITHM", "PAGE_SIZE"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    
    yield  # Application runs here

# Attach lifespan handler to app
app.lifespan = lifespan

# Include routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, reload=False)