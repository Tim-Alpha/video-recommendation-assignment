# File: app/main.py

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api.endpoints import feed, data

app = FastAPI(title="Video Recommendation Engine")

# Define the path to the frontend folder.
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

# When a user visits the root URL ("/"), send them the single index.html file.
@app.get("/", response_class=FileResponse)
async def serve_frontend():
    index_html_path = os.path.join(frontend_path, "index.html")
    if not os.path.exists(index_html_path):
        return {"error": "index.html not found!"}
    return FileResponse(index_html_path)

# This part includes your API endpoints.
app.include_router(feed.router, prefix="/feed", tags=["feed"])
app.include_router(data.router, prefix="", tags=["data"])


