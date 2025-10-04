from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.services import data_collection_service


router = APIRouter()

@router.post("/collect-data", status_code=202)
def collect_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """
    Triggers the data collection process in the background.
    """
    background_tasks.add_task(data_collection_service.fetch_and_store_data, db)
    return {"message": "Data collection process started in the background."}