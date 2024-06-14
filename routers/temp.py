from fastapi import APIRouter, FastAPI
from datetime import date
router = APIRouter(prefix="/temp")


@router.get("", tags=["temp_data"])
async def read_users():
    return [{"id": 1, "model_name": "SimpleCIL", "created_at": date.today()}, {"id": 2, "model_name": "Foster", 'created_at': date.today()}]

@router.get("/detail/{id}")
async def read_model(id: str):
    return {
        "id": id, 
        "model_name": "temporary name", 
        "created_at": date.today(), 
        "description": "This is a test data for the model", 
        "versions": [
            {
            "id": "00",
            "created_at": date.today(),
            }
    ]}