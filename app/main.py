from fastapi import FastAPI, Query, HTTPException
from app.recommender import recommend_for_user

app = FastAPI(title="Socialverse Recommender")

@app.get("/feed")
def feed(
    username: str = Query(..., min_length=1, description="Username is required"),
    project_code: str = Query(None, description="Optional category")
):
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    recs = recommend_for_user(username, project_code)
    return {"username": username, "recommendations": recs}


