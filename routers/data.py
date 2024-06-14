from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from connect_s3 import client, check_folder, count_image
templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/data")

@router.get("")
async def data_main(request: Request):
    return templates.TemplateResponse(name="data_main.html", context={"request": request})
@router.get("/w3")
async def get_w3(request: Request, key = None):
    result = {"objects": [], "request": request}
    if key:
        result.update({"key": key})
        response = client.list_objects_v2(Bucket="pycil.com",Delimiter="/", Prefix=key.replace("_", "/"))
    else:
        result.update({"key": "root"})
        response = client.list_objects_v2(Bucket="pycil.com",Delimiter="/", Prefix="data/")
    sub_folder = response.get('CommonPrefixes')
    for x in response['Contents'][1:]:
        result['objects'].append({"item": x, "type": "file"})
    if sub_folder:
        for x in sub_folder:
            result["objects"].append({"item": x.get('Prefix'), "type": "folder", "key": x.get("Prefix").replace("/", "_")})
    return templates.TemplateResponse(name="data_tree_template.html", context=result)
@router.get("/w3/{key}")
async def get_w3_select(request: Request, key):
    cls_list = await check_folder(key.replace("_","/"))
    result = []
    for cls in cls_list:
        cls_name = cls.replace(key, "")
        result.append({"name": cls_name, "image": await count_image(cls)})
    if len(result) == 0:
        raise HTTPException(status_code=409, detail="A selected folder is not fitted in the format")
    return templates.TemplateResponse(name="selected_data.html", context={"key_id": key, "key": key.replace("_", "/"),"request": request, "class_number": len(cls_list), "detail": result})