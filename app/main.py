# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Import routers
from app.routes import videos, feed, data_collection

app = FastAPI(title="Video Recommendation Engine")

# Include API routers
app.include_router(videos.router, prefix="/api", tags=["videos"])
app.include_router(feed.router, prefix="/api", tags=["feed"])
app.include_router(data_collection.router, prefix="/api", tags=["data"])

# Serve static files (optional)
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

# Serve index.html at root
@app.get("/")
def root():
    index_path = os.path.join(".", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}
