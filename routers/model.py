from fastapi import APIRouter, Request, HTTPException
from datetime import date
from fastapi.templating import Jinja2Templates
from models.model import Model, get_all_model, get_model
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
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
async def model_add(request: Request):
    result = {"methods": await getAllMethod(), "request": request}

    return templates.TemplateResponse(name="model_template.html", context=result)
@router.get("/detail/{id}")
async def model_detail(request: Request, id: int):
    json = {
        "id": id, 
        "model_name": "temporary name", 
        "created_at": date.today(), 
        "description": "This is a test data for the model", 
        "versions": [
            {
            "id": "00",
            "created_at": date.today(),
            "description": "This is a version's test description. Nothing is in here."
            }
    ]}
    json.update({"request": request})
    return templates.TemplateResponse(name='model_detail.html', context=json)

@router.get("/{id}")
async def model(request: Request, id:int):
    model = await get_model(id)
    if model:
        return templates.TemplateResponse( name='model_card.html', context = {"id": id, "request": request})
    else:
        raise HTTPException(status_code=404, detail="The required model cannot be found in the database.")

@router.post("")
async def post_model(model: Model):
    return JSONResponse(status_code=200, content=jsonable_encoder(await model.create_in_firebase()))