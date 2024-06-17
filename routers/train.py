from fastapi import APIRouter, Request, HTTPException
from datetime import date
from fastapi.templating import Jinja2Templates
from models.model import Model, get_all_model, get_model
from models.train import get_training_session, Train, get_train
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase import db
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/train")

@router.post("")
async def create_train(train: Train):
    train = train.create_to_firebase()
    response = await train.train()
    if response['model'] and response['train']:
        return JSONResponse(status_code=201, content=jsonable_encoder(response))
    else:
        return HTTPException(status_code=409, detail = "Conflict")
@router.delete("/{id}")
async def pause_train(id:str):
    doc_ref = db.collection('models').document(id) 
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return HTTPException(status_code=404, detail="The model cannot be found.")
    model_dict = snapshot.to_dict()
    if "current_train_session" not in model_dict.keys() or not model_dict["current_train_session"]:
        return HTTPException(status_code=404, detail="The model is currently not in any training session.")
    doc_ref.update({"status": "IDLE"})
    current_train = model_dict["current_train_session"]
    train_ref = db.collection("trains").document(current_train)
    train_snapshot = train_ref.get()
    if not train_snapshot.exists:
        return HTTPException(status_code=409, detail="The model is training a anonymous session. This could e a fault in the system.")
    time = train_ref.update({'status': "TERMINATED"})
    if not time:
        return HTTPException(status_code=500, detail="The training session cannot be deleted.")
    doc_ref.update({"current_train_session": None})
    model = Model()
    model.apply_dict_to_model(doc_ref.get().to_dict())
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "The model has successfully stopped.", "model": model.to_dict()}))
    