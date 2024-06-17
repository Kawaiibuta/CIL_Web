from fastapi import APIRouter, Request, HTTPException
from datetime import date
from fastapi.templating import Jinja2Templates
from models.model import Model, get_all_model, get_model
from models.train import get_training_session, Train
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase import db
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/model")

async def getAllMethod():
    return [{"id": 1, "name": "SimpleCIL", "description": "This is the most simple method for training a CIL model, but the accuracy is not that much to applause"}, {"id": 2, "name": "FOSTER", "description": "The power of architecture model laid inside. The performance is much terrific and please to see."}]
@router.get("")
async def model_main(request: Request, search=None):
    result = await get_all_model()
    if search:
        result = filter( lambda x: x.name.find(search) != -1, result)
    result = [x.minimized_dict() for x in result]
    return templates.TemplateResponse(name="model_main.html", context={"models": result, "request": request})
@router.get("/create")
async def model_add(request: Request, id=None):
    if id:
        model = await get_model(id)
        if model:
            result = {"model": model.to_dict(), "request": request}
            return templates.TemplateResponse(name="model_template.html", context=result)
        return HTTPException(status_code=404, detail = "The model cannot be found")
    result = {"methods": await getAllMethod(), "request": request}
    return templates.TemplateResponse(name="model_template.html", context=result)
@router.get("/detail/{id}")
async def model_detail(request: Request, id: str):
    model = await get_model(id)
    if model:
        data = model.to_dict()
        train_sessions = await get_training_session(id)
        data.update({"trains": train_sessions})
        return templates.TemplateResponse(name='model_detail.html', context={"request": request, **data})
    else:
        raise HTTPException(404, detail="The model cannot be found in the database.")

@router.post("")
async def post_model(model: Model):
    response = await model.create_in_firebase()
    if response['data']:
        return JSONResponse(status_code=200, content=jsonable_encoder(response))
    else:
        return HTTPException(409, detail="A error ocurred in the system. Please try again later while we are fixing the issue.")
@router.delete("/{id}")
async def delete_model(id: str):
    doc_ref = db.collection("models").document(id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return HTTPException(status_code=404, detail="The model cannot be found in database.")
    doc_ref.update({"status": "DISABLED"})
    return JSONResponse(content={"message": "The model has been disabled an cannot be used except being reset by admin."}, status_code=200)